"""Ensamblador de clave RECA y datos estructurados de Carátula CONDUSEF (Bloque E)."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from .catalog_repository import CONSTANTS, CatalogRepository, DEFAULT_CATALOG
from .models import (
    AmortizationTotals,
    CommissionType,
    ContractCoverData,
    CreditProgram,
    LoanSizingResult,
    PricingResult,
    SimulationInput,
)

ZERO = Decimal("0")


def _fmt_money(amount: Decimal) -> str:
    q = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"${q:,.2f}"


def _fmt_pct(rate: Decimal, decimals: int = 2) -> str:
    quant = Decimal("1").scaleb(-decimals)
    q = (rate * Decimal("100")).quantize(quant, rounding=ROUND_HALF_UP)
    return f"{q}%"


def build_reca_key(sim_input: SimulationInput) -> str:
    """Construye la clave compuesta RECAS!A1: <Programa>-<Esquema>-<Mancomunado>."""
    is_joint = (
        sim_input.ssv_spouse_cofinavit > ZERO
        or sim_input.infonavit_credit_spouse > ZERO
        or (
            sim_input.program == CreditProgram.CICB_COFINAVIT
            and sim_input.ssv_spouse_cicb > ZERO
        )
    )
    joint_flag = 2 if is_joint else 1
    return f"{int(sim_input.program)}-{int(sim_input.scheme)}-{joint_flag}"


def assemble_contract_cover(
    sim_input: SimulationInput,
    pricing: PricingResult,
    sizing: LoanSizingResult,
    totals: AmortizationTotals,
    catalog: CatalogRepository = DEFAULT_CATALOG,
) -> ContractCoverData:
    """Genera el DTO estructurado de la Carátula de Crédito CONDUSEF (Carat_cont)."""
    prog_spec = catalog.get_program(sim_input.program)
    reca_key = build_reca_key(sim_input)
    reca_entry = catalog.find_reca(reca_key)

    if sim_input.base_value == ZERO:
        reca_number = ""
        reca_contract_name = ""
        reca_expedition_date = ""
    elif reca_entry is not None:
        reca_number = reca_entry.reca_number
        reca_contract_name = reca_entry.contract_name
        reca_expedition_date = reca_entry.expedition_date
    else:
        reca_number = "Revisa los datos ingresados"
        reca_contract_name = ""
        reca_expedition_date = ""

    # Excepción regulatoria explícita en Carat_cont!C20 para clave RECA 7-2-2
    late_payment_fee = (
        CONSTANTS.late_fee_722 if reca_key == "7-2-2" else CONSTANTS.late_fee_default
    )
    late_payment_penalty_text = (
        f"Penalización por pago tardío: {_fmt_money(late_payment_fee)} más IVA por evento."
    )

    if sizing.opening_commission > ZERO:
        opening_commission_text = (
            f"Comisión por apertura: {_fmt_pct(pricing.opening_commission_rate, 2)} "
            f"({_fmt_money(sizing.opening_commission)} más IVA, evento único)."
        )
    else:
        opening_commission_text = "Comisión por apertura: $0.00 (0.00% / exenta)."

    if (
        sim_input.commission_type == CommissionType.PAGO_ANTICIPADO
        and pricing.prepay_commission_rate > ZERO
    ):
        prepayment_commission_text = (
            f"Comisión por pago anticipado: {_fmt_pct(pricing.prepay_commission_rate, 2)} "
            "más IVA sobre el monto del prepago."
        )
    else:
        prepayment_commission_text = "Comisión por pago anticipado: 0.00% (sin penalización)."

    commercial_product_name = (
        f"{prog_spec.brand_code} {sim_input.scheme.label.upper()} {sim_input.term.label}"
    )

    return ContractCoverData(
        client_name=sim_input.client_name.strip() or "Cliente / Acreditado",
        commercial_product_name=commercial_product_name,
        term_label=sim_input.term.label,
        currency_label="Pesos Mexicanos (MXN)",
        official_cat=totals.official_cat,
        initial_rate=pricing.initial_rate,
        loan_amount=sizing.initial_balance,
        total_amount_to_pay=totals.total_amount_to_pay,
        opening_commission_text=opening_commission_text,
        late_payment_fee=late_payment_fee,
        late_payment_penalty_text=late_payment_penalty_text,
        prepayment_commission_text=prepayment_commission_text,
        reca_key=reca_key,
        reca_number=reca_number,
        reca_contract_name=reca_contract_name,
        reca_expedition_date=reca_expedition_date,
    )
