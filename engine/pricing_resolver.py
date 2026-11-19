"""Resolución de campaña efectiva, pricing y aforo LTV (Bloque A)."""

from __future__ import annotations

from decimal import Decimal, localcontext

from .catalog_repository import CatalogRepository, DEFAULT_CATALOG
from .models import (
    Campaign,
    CreditProgram,
    DECIMAL_PREC,
    EconomicActivity,
    LoanTerm,
    PricingResult,
    ProductScheme,
    SimulationInput,
)


def resolve_effective_campaign(
    program: CreditProgram,
    campaign: Campaign,
) -> Campaign:
    """Determina la campaña efectiva (Simulador!W62).

    En Pasivo Hipotecario (programas 4 y 5), si el usuario deja 'Ninguna' (1),
    se remapea automáticamente a la campaña 5 (Pasivo).
    """
    if campaign == Campaign.NINGUNA and program.is_pasivo:
        return Campaign.ENGANCHE_ALTO_PASIVO
    return campaign


def resolve_ltv(
    program: CreditProgram,
    economic_activity: EconomicActivity,
    risk_index: int,
    catalog: CatalogRepository = DEFAULT_CATALOG,
) -> Decimal:
    """Determina el porcentaje de aforo LTV (Simulador!X39).

    Paridad literal W-01: en el libro de Excel original la fórmula de AH48:AJ52
    compara contra una celda vacía (I21 = 0), por lo que siempre aplica la rama
    <= 10M. Se replica exactamente para garantizar paridad 100 % con Excel.
    Si en el futuro se corrige contra el monto de crédito, bastará con evaluar
    los tramos <=15M, <=20M, <=25M y >25M de ``LtvRow``.
    """
    if program == CreditProgram.COFINAVIT:
        return Decimal("0.95")
    if program == CreditProgram.CICB_COFINAVIT:
        return Decimal("0.90")

    row = catalog.get_ltv_row(risk_index)
    if program.is_apoyo_infonavit:
        return row.emp_with_support_le_10m

    if economic_activity == EconomicActivity.EMPLEADO:
        return row.emp_no_support_le_10m

    # Independiente: en Pasivo Hipotecario (4 o 5) aplica el aforo preferente de Pasivo.
    if program.is_pasivo:
        return row.indep_pasivo_le_10m
    return row.indep_le_10m


def resolve_pricing(
    sim_input: SimulationInput,
    catalog: CatalogRepository = DEFAULT_CATALOG,
) -> PricingResult:
    """Resuelve tasa inicial, PPM, incremento anual, piso, factor de baja y LTV."""
    if sim_input.scheme == ProductScheme.VALORA and sim_input.term == LoanTerm.ANIOS_7:
        raise ValueError("El plazo de 7 años aplica únicamente al esquema Pagos Oportunos.")

    with localcontext() as ctx:
        ctx.prec = DECIMAL_PREC

        prog_spec = catalog.get_program(sim_input.program)
        effective_campaign = resolve_effective_campaign(sim_input.program, sim_input.campaign)
        pricing_spec = catalog.get_pricing(effective_campaign, sim_input.risk_index)

        if sim_input.scheme == ProductScheme.PAGOS_OPORTUNOS:
            initial_rate = pricing_spec.po_rate
            ppm = pricing_spec.po_ppm_by_term[sim_input.term]
            annual_payment_increase = Decimal("0")
        else:
            initial_rate = pricing_spec.valora_rate
            ppm = pricing_spec.valora_ppm_by_term[sim_input.term]
            annual_payment_increase = pricing_spec.valora_annual_increase

        ltv = resolve_ltv(
            program=sim_input.program,
            economic_activity=sim_input.economic_activity,
            risk_index=sim_input.risk_index,
            catalog=catalog,
        )

        opening_comm_rate = (
            sim_input.manual_opening_commission_rate
            if sim_input.manual_opening_commission_rate is not None
            else prog_spec.opening_commission_rate
        )

        return PricingResult(
            effective_campaign=effective_campaign,
            initial_rate=initial_rate,
            ppm=ppm,
            annual_payment_increase=annual_payment_increase,
            floor_rate=pricing_spec.valora_floor_rate,
            ceiling_rate=pricing_spec.valora_ceiling_rate,
            po_rate_drop_per_year=pricing_spec.po_rate_drop_per_year,
            ltv=ltv,
            pti=prog_spec.pti,
            opening_commission_rate=opening_comm_rate,
            prepay_commission_rate=prog_spec.prepay_commission_rate,
        )
