"""Dimensionamiento de crédito, gastos de originación e inversión (Bloques B y C)."""

from __future__ import annotations

from decimal import Decimal, localcontext

from .catalog_repository import CONSTANTS, CatalogRepository, DEFAULT_CATALOG
from .models import (
    CalcMode,
    Campaign,
    CommissionType,
    CreditProgram,
    DECIMAL_PREC,
    LoanSizingResult,
    PricingResult,
    ProductScheme,
    SimulationInput,
    ValidationAlert,
)

ZERO = Decimal("0")
ONE = Decimal("1")
THOUSAND = Decimal("1000")


def _calc_cofinavit_bank_loan(
    housing_value: Decimal,
    d37: Decimal,
    d44: Decimal,
    d35: Decimal,
    d42: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    """Regla Cofinavit (Simulador!AE4:AE20). Devuelve (max_bank_loan, infonavit_total, ssv_total)."""
    ae11 = d37 + d44
    ae12 = d35 + d42
    if housing_value <= ZERO:
        return ZERO, ae11, ae12
    ae16 = (ae11 + ae12) / housing_value
    ae17 = Decimal("0.95")
    ae19 = max(ZERO, ae17 + ae16 - ONE)
    ae20 = ae17 * housing_value - ae19 * housing_value
    return ae20, ae11, ae12


def _calc_cicb_bank_loan(
    housing_value: Decimal,
    d35: Decimal,
    d38: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Regla CI+CB Cofinavit (Simulador!AE24:AE28).

    Devuelve (max_bank_loan, infonavit_total, ssv_total, total_granted_ae26).
    """
    ae24 = housing_value * Decimal("0.90")
    ae25 = d35 + d38
    ae26 = ae24 if housing_value > (ae24 + ae25) else (housing_value - ae25)
    ae27 = min(CONSTANTS.cicb_max_infonavit_loan, ae26 * CONSTANTS.cicb_infonavit_share)
    ae28 = ae26 - ae27
    return ae28, ae27, ae25, ae26


def calculate_loan_sizing(
    sim_input: SimulationInput,
    pricing: PricingResult,
    catalog: CatalogRepository = DEFAULT_CATALOG,
) -> tuple[LoanSizingResult, tuple[ValidationAlert, ...]]:
    """Calcula crédito máximo (I24), gastos financiados (I28), gastos O26:O33 e inversión."""
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PREC

        prog_spec = catalog.get_program(sim_input.program)
        d21 = sim_input.base_value
        ltv = pricing.ltv
        pti = pricing.pti
        ppm = pricing.ppm

        if sim_input.calc_mode == CalcMode.POR_VALOR_INMUEBLE:
            housing_value = d21
            base_max_loan = d21 * ltv
        elif sim_input.calc_mode == CalcMode.POR_IMPORTE_CREDITO:
            base_max_loan = d21
            housing_value = d21 / ltv if ltv > ZERO else ZERO
        else:  # POR_INGRESOS (Y41=2)
            max_monthly_payment = d21 * pti
            base_max_loan = (
                max_monthly_payment / (ppm / THOUSAND) if ppm > ZERO else ZERO
            )
            housing_value = base_max_loan / ltv if ltv > ZERO else ZERO

        infonavit_loan_total = ZERO
        ssv_total = ZERO
        cicb_total_granted = ZERO

        if sim_input.program == CreditProgram.COFINAVIT:
            max_loan, infonavit_loan_total, ssv_total = _calc_cofinavit_bank_loan(
                housing_value=housing_value,
                d37=sim_input.infonavit_credit_titular,
                d44=sim_input.infonavit_credit_spouse,
                d35=sim_input.ssv_titular,
                d42=sim_input.ssv_spouse_cofinavit,
            )
        elif sim_input.program == CreditProgram.CICB_COFINAVIT:
            max_loan, infonavit_loan_total, ssv_total, cicb_total_granted = _calc_cicb_bank_loan(
                housing_value=housing_value,
                d35=sim_input.ssv_titular,
                d38=sim_input.ssv_spouse_cicb,
            )
        else:
            max_loan = base_max_loan

        # Tope LTI (AC86): solo si Y41=2, Valora, IR>3
        if (
            sim_input.calc_mode == CalcMode.POR_INGRESOS
            and sim_input.scheme == ProductScheme.VALORA
            and sim_input.risk_index > 3
        ):
            max_loan = d21 * CONSTANTS.lti_multiplier_ir_gt_3_valora

        requested_loan = (
            sim_input.requested_loan if sim_input.requested_loan is not None else max_loan
        )

        # Gastos notariales financiados en Pasivo Hipotecario (Simulador!I28)
        financed_expenses = ZERO
        if sim_input.program.is_pasivo and sim_input.finance_notary_fees:
            if (
                sim_input.calc_mode == CalcMode.POR_VALOR_INMUEBLE
                and housing_value * ltv == requested_loan
            ):
                financed_expenses = ZERO
            elif (
                sim_input.calc_mode == CalcMode.POR_VALOR_INMUEBLE
                and requested_loan * (ONE + CONSTANTS.pasivo_financed_cap_rate) > max_loan
            ):
                financed_expenses = max_loan - requested_loan
            else:
                financed_expenses = requested_loan * CONSTANTS.pasivo_financed_cap_rate

        initial_balance = (
            requested_loan + financed_expenses if financed_expenses > ZERO else requested_loan
        )

        # Porcentaje de financiamiento (Simulador!M20)
        if housing_value == ZERO:
            financing_pct = ZERO
        elif sim_input.program == CreditProgram.CICB_COFINAVIT:
            financing_pct = cicb_total_granted / housing_value
        else:
            financing_pct = initial_balance / housing_value

        # Bloque C: Gastos de originación (O26:O33)
        is_cofin = sim_input.program.is_cofinavit_family
        info_orig = (
            infonavit_loan_total * CONSTANTS.infonavit_origination_rate if is_cofin else ZERO
        )

        # W-09: defaults explícitos 3% Impuestos y Derechos (AE65) y 2% Honorarios Notariales (AE66).
        tax_rate = (
            sim_input.manual_tax_rate
            if sim_input.manual_tax_rate is not None
            else CONSTANTS.default_tax_rate
        )
        notary_rate = (
            sim_input.manual_notary_rate
            if sim_input.manual_notary_rate is not None
            else CONSTANTS.default_notary_rate
        )

        if is_cofin and sim_input.exact_infonavit_expenses > ZERO:
            taxes_and_rights = sim_input.exact_infonavit_expenses - info_orig
        else:
            taxes_and_rights = housing_value * tax_rate

        notary_fees = housing_value * notary_rate

        appraisal_exempt = (
            pricing.effective_campaign == Campaign.WEALTH_MANAGEMENT
            or sim_input.program.is_pasivo
        )
        if appraisal_exempt:
            appraisal_cost = ZERO
            requires_appraisal_quote = False
        else:
            # W-04 manejado dentro de lookup_appraisal_cost (retorna 0 si housing_value <= 0).
            appraisal_cost = catalog.lookup_appraisal_cost(housing_value)
            requires_appraisal_quote = housing_value > CONSTANTS.appraisal_quote_threshold

        # En campañas 2, 3 y 4 o comisión por pago anticipado (T41=2), la apertura es $0.
        if (
            pricing.effective_campaign
            in (Campaign.WEALTH_MANAGEMENT, Campaign.HIPOTECA_GREEN, Campaign.VINCULACION)
            or sim_input.commission_type == CommissionType.PAGO_ANTICIPADO
        ):
            opening_commission = ZERO
        else:
            opening_commission = requested_loan * pricing.opening_commission_rate

        # Paridad literal W-10: en Pasivo Hipotecario se permite valor negativo en O33
        # cuando los gastos financiados (I28) exceden la suma de gastos reales O26:O31.
        # Si en el futuro se desea acotar, reemplazar por max(ZERO, ...).
        net_origination_expenses = (
            info_orig
            + taxes_and_rights
            + notary_fees
            + appraisal_cost
            + opening_commission
            - financed_expenses
        )

        total_resources = (
            requested_loan + ssv_total + infonavit_loan_total if is_cofin else requested_loan
        )
        down_payment = ZERO if sim_input.program.is_pasivo else (housing_value - total_resources)
        client_investment = (
            net_origination_expenses
            if sim_input.program == CreditProgram.LIQUIDEZ_VIVIENDA
            else down_payment + net_origination_expenses
        )

        min_required_income = prog_spec.min_income
        if requested_loan > ZERO and pti > ZERO:
            computed_income = (requested_loan / THOUSAND) * ppm / pti
            if computed_income > min_required_income:
                min_required_income = computed_income

        alerts: list[ValidationAlert] = []
        if d21 <= ZERO:
            alerts.append(
                ValidationAlert(
                    code="BASE_VALUE_ZERO",
                    severity="info",
                    message="Ingresa un valor base mayor a cero para calcular la cotización.",
                )
            )
        else:
            if (
                sim_input.calc_mode == CalcMode.POR_VALOR_INMUEBLE
                and prog_spec.min_property_value > ZERO
                and d21 < prog_spec.min_property_value
            ):
                alerts.append(
                    ValidationAlert(
                        code="MIN_PROPERTY_VALUE",
                        severity="warning",
                        message=(
                            f"El valor del inmueble (${d21:,.2f}) es menor al mínimo "
                            f"del programa (${prog_spec.min_property_value:,.2f})."
                        ),
                    )
                )
            if (
                sim_input.calc_mode == CalcMode.POR_INGRESOS
                and d21 < prog_spec.min_income
            ):
                alerts.append(
                    ValidationAlert(
                        code="MIN_INCOME",
                        severity="warning",
                        message=(
                            f"El ingreso mensual (${d21:,.2f}) es menor al mínimo "
                            f"del programa (${prog_spec.min_income:,.2f})."
                        ),
                    )
                )
            if requested_loan > max_loan:
                alerts.append(
                    ValidationAlert(
                        code="LOAN_ABOVE_MAX",
                        severity="warning",
                        message=(
                            f"El crédito solicitado (${requested_loan:,.2f}) supera el "
                            f"crédito máximo autorizado (${max_loan:,.2f})."
                        ),
                    )
                )
            if requested_loan < prog_spec.min_loan_amount:
                alerts.append(
                    ValidationAlert(
                        code="LOAN_BELOW_MIN",
                        severity="warning",
                        message=(
                            f"El crédito solicitado (${requested_loan:,.2f}) es menor al "
                            f"monto mínimo del programa (${prog_spec.min_loan_amount:,.2f})."
                        ),
                    )
                )
            policy_max = (
                CONSTANTS.policy_max_loan_ir5
                if sim_input.risk_index == 5
                else prog_spec.max_loan_amount
            )
            if requested_loan > policy_max:
                alerts.append(
                    ValidationAlert(
                        code="LOAN_ABOVE_POLICY_MAX",
                        severity="warning",
                        message=(
                            f"El monto de crédito (${requested_loan:,.2f}) excede el tope "
                            f"de política (${policy_max:,.2f})."
                        ),
                    )
                )
            if requires_appraisal_quote:
                alerts.append(
                    ValidationAlert(
                        code="APPRAISAL_CUSTOM_QUOTE",
                        severity="info",
                        message=(
                            "Valor de vivienda superior a $30,000,000.00: "
                            "'Favor de Cotizar' avalúo aproximado."
                        ),
                    )
                )
            if sim_input.manual_opening_commission_rate is not None and (
                sim_input.manual_opening_commission_rate > Decimal("0.5")
                or sim_input.manual_opening_commission_rate < ZERO
            ):
                alerts.append(
                    ValidationAlert(
                        code="INVALID_MANUAL_COMMISSION",
                        severity="error",
                        message="La comisión manual debe capturarse en formato decimal entre 0 y 0.50.",
                    )
                )

        sizing = LoanSizingResult(
            housing_value=housing_value,
            max_loan=max_loan,
            requested_loan=requested_loan,
            financed_expenses=financed_expenses,
            initial_balance=initial_balance,
            financing_pct=financing_pct,
            infonavit_loan_total=infonavit_loan_total,
            ssv_total=ssv_total,
            total_resources=total_resources,
            infonavit_origination_expense=info_orig,
            taxes_and_rights=taxes_and_rights,
            notary_fees=notary_fees,
            appraisal_cost=appraisal_cost,
            requires_appraisal_quote=requires_appraisal_quote,
            opening_commission=opening_commission,
            net_origination_expenses=net_origination_expenses,
            down_payment=down_payment,
            client_investment=client_investment,
            min_required_income=min_required_income,
        )
        return sizing, tuple(alerts)
