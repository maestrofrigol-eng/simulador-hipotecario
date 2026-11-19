"""Motor de amortización a 240 periodos, calendario Actual/360 y cálculo de TIR/CAT (Bloque D)."""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, localcontext
from typing import Optional

from .catalog_repository import CONSTANTS
from .models import (
    AmortizationRow,
    AmortizationTotals,
    CommissionType,
    CreditProgram,
    DECIMAL_PREC,
    LoanSizingResult,
    MAX_PERIODS,
    PrepayMode,
    PricingResult,
    ProductScheme,
    SimulationInput,
)

ZERO = Decimal("0")
ONE = Decimal("1")
THOUSAND = Decimal("1000")
INSURANCE_MIN_BALANCE = Decimal("0.01")
IRR_TOLERANCE = Decimal("1e-12")
IRR_MAX_ITERATIONS = 100


def _add_months(year: int, month: int, delta_months: int) -> tuple[int, int]:
    """Suma ``delta_months`` meses a (year, month) sin librerías externas."""
    total = (year * 12 + (month - 1)) + delta_months
    return total // 12, (total % 12) + 1


def build_period_date(quote_date: date, period: int) -> tuple[date, int]:
    """Calcula la fecha de corte (Tabla!BD{r}) y los días calendario del mes (BE{r})."""
    cut_day = 3 if 3 <= quote_date.day <= 16 else 17
    add_month = 1 if quote_date.day > cut_day else 0
    first_year, first_month = _add_months(quote_date.year, quote_date.month, add_month)

    if period == 1:
        period_date = date(first_year, first_month, cut_day)
    else:
        yr, mo = _add_months(first_year, first_month, period - 1)
        period_date = date(yr, mo, 1)

    days_in_month = calendar.monthrange(period_date.year, period_date.month)[1]
    return period_date, days_in_month


def rate_for_period(
    period: int,
    sim_input: SimulationInput,
    pricing: PricingResult,
) -> Decimal:
    """Evolución mensual de la tasa anual (Tabla!AJ para Valora, AL:AO para Pagos Oportunos)."""
    if sim_input.scheme == ProductScheme.VALORA:
        if period <= 36:
            return pricing.initial_rate
        drops = (period - 25) // 12
        candidate = pricing.initial_rate - (CONSTANTS.valora_annual_rate_drop * Decimal(drops))
        return max(candidate, pricing.floor_rate)

    # Pagos Oportunos
    if period > sim_input.term.months:
        return ZERO
    drops = min(4, (period - 1) // 12)
    return pricing.initial_rate - (pricing.po_rate_drop_per_year * Decimal(drops))


def solve_irr_newton_raphson(
    cash_flows: list[Decimal],
    initial_guess: Decimal = ZERO,
    tolerance: Decimal = IRR_TOLERANCE,
    max_iterations: int = IRR_MAX_ITERATIONS,
) -> Decimal:
    """Resuelve la TIR mensual por Newton-Raphson (tolerancia 1e-12, prec=34).

    Retorna ``Decimal("0")`` si los flujos no presentan cambio de signo o no convergen.
    """
    if not cash_flows or cash_flows[0] >= ZERO:
        return ZERO
    if not any(cf > ZERO for cf in cash_flows[1:]):
        return ZERO

    with localcontext() as ctx:
        ctx.prec = DECIMAL_PREC
        rate = initial_guess

        for _ in range(max_iterations):
            one_plus_r = ONE + rate
            if one_plus_r <= ZERO:
                rate = Decimal("0.005")
                one_plus_r = ONE + rate

            npv = ZERO
            d_npv = ZERO
            discount = ONE
            for t, cf in enumerate(cash_flows):
                if t == 0:
                    npv += cf
                else:
                    discount *= one_plus_r
                    if cf != ZERO:
                        term_val = cf / discount
                        npv += term_val
                        d_npv -= (Decimal(t) * term_val) / one_plus_r

            if d_npv == ZERO:
                break

            step = npv / d_npv
            next_rate = rate - step
            if abs(next_rate - rate) <= tolerance:
                return next_rate
            rate = next_rate

        return rate


def annualize_cat(monthly_irr: Decimal) -> Decimal:
    """Convierte la TIR mensual a CAT anualizado sin IVA: (1 + irr)^12 - 1."""
    if monthly_irr == ZERO:
        return ZERO
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PREC
        return ((ONE + monthly_irr) ** 12) - ONE


def _calc_bimonthly_infonavit(
    period: int,
    program: CreditProgram,
    infonavit_salary: Decimal,
    initial_balance: Decimal,
    principal: Decimal,
    prev_even_support: Decimal,
) -> Decimal:
    """Calcula la aportación patronal bimestral de Apoyo Infonavit (Tabla!N15:N254)."""
    if not program.is_apoyo_infonavit or period % 2 != 0:
        return ZERO

    if period == 2:
        if initial_balance <= ZERO:
            return ZERO
        raw = infonavit_salary * CONSTANTS.employer_infonavit_rate * Decimal("2")
        if raw > CONSTANTS.bimonthly_cap_amount:
            return CONSTANTS.bimonthly_cap_amount
        return raw

    # Periodos pares >= 4
    if initial_balance - principal <= ZERO:
        return ZERO
    growth = CONSTANTS.employer_annual_increase if (period % 12 == 2) else ZERO
    return prev_even_support * (ONE + growth)


def run_amortization(
    sim_input: SimulationInput,
    pricing: PricingResult,
    sizing: LoanSizingResult,
) -> tuple[tuple[AmortizationRow, ...], AmortizationTotals]:
    """Ejecuta la corrida base contractual (AT:BB) y la corrida principal (A:Y) a 240 periodos."""
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PREC

        initial_balance = sizing.initial_balance
        damage_base = (
            sim_input.destructible_value
            if (sim_input.destructible_value is not None and sim_input.destructible_value > ZERO)
            else sizing.housing_value
        )
        external_ins = sim_input.insurance_option.is_external

        # --- 1. Corrida base contractual (AT:BB) sin prepagos ni Apoyo Infonavit ---
        base_at: list[Decimal] = [ZERO] * MAX_PERIODS
        base_au: list[Decimal] = [ZERO] * MAX_PERIODS
        base_bb: list[Decimal] = [ZERO] * MAX_PERIODS
        aq_factors: list[Decimal] = [ZERO] * MAX_PERIODS
        period_dates: list[Optional[date]] = [None] * MAX_PERIODS
        period_days: list[int] = [0] * MAX_PERIODS

        prev_ax = ZERO
        prev_au = ZERO

        for idx in range(MAX_PERIODS):
            p = idx + 1
            at = initial_balance if p == 1 else (ZERO if prev_ax <= ZERO else prev_ax)
            base_at[idx] = at

            if at > ZERO:
                p_date, days = build_period_date(sim_input.quote_date, p)
                period_dates[idx] = p_date
                period_days[idx] = days
            else:
                p_date, days = None, 0

            ay = rate_for_period(p, sim_input, pricing)
            av = (
                ZERO
                if (at <= ZERO or days == 0)
                else (ay / CONSTANTS.interest_day_count_base) * Decimal(days) * at
            )

            ba = (
                pricing.annual_payment_increase
                if (p >= 13 and (p - 1) % 12 == 0 and at > ZERO)
                else ZERO
            )

            if p == 1:
                au = (at / THOUSAND) * pricing.ppm
            elif at <= ZERO:
                au = ZERO
            elif (at + av - prev_au) < ZERO:
                au = at + av
            else:
                au = prev_au * (ONE + ba)

            aw = au - av
            ax = at - aw

            if external_ins or at <= INSURANCE_MIN_BALANCE:
                az = ZERO
            else:
                az = (at * CONSTANTS.life_insurance_rate) + (
                    damage_base * CONSTANTS.damage_insurance_rate
                )

            bb = av + aw + az

            base_au[idx] = au
            base_bb[idx] = bb
            aq_factors[idx] = (au / at) if at > ZERO else ZERO

            prev_ax = ax
            prev_au = au

        # CAT Oficial (I40 / B11) calculado siempre sobre la corrida base AT:BB
        cf0 = (sizing.opening_commission + sizing.appraisal_cost) - initial_balance
        official_cash_flows = [cf0] + base_bb
        official_irr = solve_irr_newton_raphson(official_cash_flows)
        official_cat = annualize_cat(official_irr)

        # --- 2. Corrida principal (A:Y) con prepagos, penalizaciones y Apoyo Infonavit ---
        rows: list[AmortizationRow] = []
        real_cash_flows: list[Decimal] = [cf0]

        prev_r = ZERO
        prev_d = ZERO
        prev_j = ZERO
        prev_even_n = ZERO
        initial_bimonthly_support = ZERO

        total_d = ZERO
        total_f = ZERO
        total_h = ZERO
        total_j = ZERO
        total_l = ZERO
        total_n = ZERO
        total_t = ZERO
        total_v = ZERO
        total_y = ZERO

        payoff_period = 0

        for idx in range(MAX_PERIODS):
            p = idx + 1
            b_bal = initial_balance if p == 1 else (ZERO if prev_r <= ZERO else prev_r)

            if period_dates[idx] is not None:
                p_date = period_dates[idx]
                days = period_days[idx]
            elif b_bal > ZERO:
                p_date, days = build_period_date(sim_input.quote_date, p)
            else:
                p_date, days = None, 0

            p_rate = rate_for_period(p, sim_input, pricing)
            f_int = (
                ZERO
                if (b_bal <= ZERO or days == 0)
                else (p_rate / CONSTANTS.interest_day_count_base) * Decimal(days) * b_bal
            )

            inc_aa = (
                pricing.annual_payment_increase
                if (p >= 13 and (p - 1) % 12 == 0)
                else ZERO
            )

            if p == 1:
                d_pay = (b_bal / THOUSAND) * pricing.ppm
            elif b_bal <= ZERO:
                d_pay = ZERO
            elif (b_bal + f_int - prev_d) <= ZERO:
                d_pay = b_bal + f_int
            elif (
                sim_input.program in (CreditProgram.APOYO_INFONAVIT, CreditProgram.CICB_COFINAVIT)
                and prev_j == ZERO
            ):
                d_pay = prev_d * (ONE + inc_aa)
            elif sim_input.prepay_mode == PrepayMode.DISMINUCION_PAGO:
                d_pay = b_bal * aq_factors[idx]
            else:
                d_pay = prev_d * (ONE + inc_aa)

            h_prin = d_pay - f_int
            j_prep = sim_input.prepayments[idx] if b_bal > ZERO else ZERO

            if sim_input.commission_type == CommissionType.CONTRATACION_CREDITO:
                l_pen = ZERO
            else:
                l_pen = j_prep * pricing.prepay_commission_rate * CONSTANTS.vat_factor

            n_sup = _calc_bimonthly_infonavit(
                period=p,
                program=sim_input.program,
                infonavit_salary=sim_input.infonavit_salary,
                initial_balance=b_bal,
                principal=h_prin,
                prev_even_support=prev_even_n,
            )
            if p == 2:
                initial_bimonthly_support = n_sup
            if p % 2 == 0:
                prev_even_n = n_sup

            # Paridad literal W-03: la penalización por prepago L se SUMA al saldo final R
            # (R = B - H - J + L - N) y NO se suma al pago mensual Y.
            r_end = b_bal - h_prin - j_prep + l_pen - n_sup

            t_life = ZERO if (external_ins or b_bal <= ZERO) else (b_bal * CONSTANTS.life_insurance_rate)
            v_dmg = ZERO if (external_ins or b_bal <= ZERO) else (damage_base * CONSTANTS.damage_insurance_rate)
            y_total = ZERO if b_bal <= ZERO else (d_pay + j_prep + t_life + v_dmg)

            # W-05: detectar liquidación real verificando saldo inicial > 0 y saldo final <= 0
            # (evita falso positivo en periodo 1 cuando el crédito es $0).
            if payoff_period == 0 and b_bal > ZERO and r_end <= ZERO:
                payoff_period = p

            rows.append(
                AmortizationRow(
                    period=p,
                    cut_date=p_date,
                    days_in_month=days,
                    initial_balance=b_bal,
                    scheduled_payment=d_pay,
                    interest=f_int,
                    principal=h_prin,
                    prepayment=j_prep,
                    prepayment_penalty=l_pen,
                    infonavit_support=n_sup,
                    annual_rate=p_rate,
                    final_balance=r_end,
                    life_insurance=t_life,
                    damage_insurance=v_dmg,
                    total_monthly_payment=y_total,
                )
            )

            # W-07: sumar exclusivamente los periodos 1..240 (Y15:Y254).
            total_d += d_pay
            total_f += f_int
            total_h += h_prin
            total_j += j_prep
            total_l += l_pen
            total_n += n_sup
            total_t += t_life
            total_v += v_dmg
            total_y += y_total

            real_cash_flows.append(y_total)

            prev_r = r_end
            prev_d = d_pay
            prev_j = j_prep

        real_irr = solve_irr_newton_raphson(real_cash_flows)
        real_cat = annualize_cat(real_irr)

        totals = AmortizationTotals(
            total_scheduled_payment=total_d,
            total_interest=total_f,
            total_principal=total_h,
            total_prepayments=total_j,
            total_penalties=total_l,
            total_infonavit_support=total_n,
            total_life_insurance=total_t,
            total_damage_insurance=total_v,
            total_amount_to_pay=total_y,
            official_cat=official_cat,
            real_cat=real_cat,
            first_monthly_payment=rows[0].total_monthly_payment if rows else ZERO,
            payoff_period=payoff_period,
            payoff_years=payoff_period // 12,
            payoff_months=payoff_period % 12,
            initial_bimonthly_support=initial_bimonthly_support,
        )
        return tuple(rows), totals
