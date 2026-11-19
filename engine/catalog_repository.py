"""Repositorio inmutable de catálogos, constantes y tablas auxiliares (Sección 4).

Todos los valores numéricos, tablas de pricing, tramos de avalúo, constantes
UMA 2026 y registros RECA viven aislados en este módulo para facilitar su
mantenimiento o reemplazo por otra institución financiera.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping, Optional

from .models import Campaign, CreditProgram, LoanTerm


@dataclass(frozen=True)
class ProgramSpec:
    """Parámetros base de un programa comercial de crédito (Sección 4.1)."""

    program: CreditProgram
    name: str
    opening_commission_rate: Decimal
    prepay_commission_rate: Decimal
    ltv_rule: str  # "MATRIX_AI_AJ" | "MATRIX_AH" | "FIXED_95" | "FIXED_90"
    min_income: Decimal
    min_loan_amount: Decimal
    max_loan_amount: Decimal
    min_property_value: Decimal
    pti: Decimal
    brand_code: str


@dataclass(frozen=True)
class LtvRow:
    """Fila de la matriz de aforo LTV por Índice de Riesgo (Sección 4.2)."""

    risk_index: int
    emp_with_support_le_10m: Decimal
    emp_no_support_le_10m: Decimal
    indep_le_10m: Decimal
    indep_pasivo_le_10m: Decimal
    emp_le_15m: Decimal
    indep_le_15m: Decimal
    le_20m: Decimal
    le_25m: Optional[Decimal]
    gt_25m: Optional[Decimal]
    pti_ref: Decimal


@dataclass(frozen=True)
class CampaignPricingSpec:
    """Tabla de tasas y pagos por millar por (Campaña, Índice de Riesgo) (Sección 4.3)."""

    campaign: Campaign
    risk_index: int
    valora_rate: Decimal
    valora_ppm_by_term: Mapping[LoanTerm, Decimal]
    valora_annual_increase: Decimal
    valora_floor_rate: Decimal
    valora_ceiling_rate: Decimal
    po_rate: Decimal
    po_ppm_by_term: Mapping[LoanTerm, Decimal]
    po_rate_drop_per_year: Decimal


@dataclass(frozen=True)
class AppraisalTier:
    """Tramo de costo de avalúo hipotecario (Sección 4.4)."""

    min_value: Decimal
    max_value: Decimal
    appraisal_cost: Decimal
    switch_ref_cost: Decimal


@dataclass(frozen=True)
class RecaEntry:
    """Registro normativo de Contrato de Adhesión CONDUSEF (Sección 4.6)."""

    reca_key: str
    record_no: int
    contract_name: str
    reca_number: str
    expedition_date: str
    program_id: int
    scheme_id: int
    joint_flag: int


@dataclass(frozen=True)
class SystemConstants:
    """Constantes operativas, seguros, gastos y parámetros UMA 2026 (Sección 4.5)."""

    life_insurance_rate: Decimal = Decimal("0.0006")
    damage_insurance_rate: Decimal = Decimal("0.00031")
    vat_factor: Decimal = Decimal("1.16")
    pasivo_financed_cap_rate: Decimal = Decimal("0.06")
    infonavit_origination_rate: Decimal = Decimal("0.03")
    default_tax_rate: Decimal = Decimal("0.03")
    default_notary_rate: Decimal = Decimal("0.02")
    cicb_max_infonavit_loan: Decimal = Decimal("885445.60")
    cicb_infonavit_share: Decimal = Decimal("0.30")
    uma_daily_2026: Decimal = Decimal("117.31")
    uma_salary_cap_multiplier: Decimal = Decimal("25")
    employer_infonavit_rate: Decimal = Decimal("0.05")
    bimonthly_avg_days: Decimal = Decimal("60.8")
    bimonthly_cap_amount: Decimal = Decimal("8915.56")
    employer_annual_increase: Decimal = Decimal("0.03")
    policy_max_loan_default: Decimal = Decimal("15000000")
    policy_max_loan_ir5: Decimal = Decimal("7000000")
    valora_annual_rate_drop: Decimal = Decimal("0.0025")
    interest_day_count_base: Decimal = Decimal("360")
    lti_multiplier_ir_gt_3_valora: Decimal = Decimal("25")
    appraisal_quote_threshold: Decimal = Decimal("30000000")
    late_fee_default: Decimal = Decimal("500.00")
    late_fee_722: Decimal = Decimal("350.00")


CONSTANTS = SystemConstants()


PROGRAMS: Mapping[CreditProgram, ProgramSpec] = MappingProxyType(
    {
        CreditProgram.ADQUISICION_TRADICIONAL: ProgramSpec(
            program=CreditProgram.ADQUISICION_TRADICIONAL,
            name="Adquisición Tradicional",
            opening_commission_rate=Decimal("0.0125"),
            prepay_commission_rate=Decimal("0.03"),
            ltv_rule="MATRIX_AI_AJ",
            min_income=Decimal("10000"),
            min_loan_amount=Decimal("250000"),
            max_loan_amount=Decimal("15000000"),
            min_property_value=Decimal("400000"),
            pti=Decimal("0.55"),
            brand_code="CREDIRESIDENCIAL",
        ),
        CreditProgram.APOYO_INFONAVIT: ProgramSpec(
            program=CreditProgram.APOYO_INFONAVIT,
            name="Adquisición con Apoyo Infonavit",
            opening_commission_rate=Decimal("0.0075"),
            prepay_commission_rate=Decimal("0.00"),
            ltv_rule="MATRIX_AH",
            min_income=Decimal("7500"),
            min_loan_amount=Decimal("250000"),
            max_loan_amount=Decimal("15000000"),
            min_property_value=Decimal("400000"),
            pti=Decimal("0.65"),
            brand_code="CREDIRESIDENCIAL",
        ),
        CreditProgram.COFINAVIT: ProgramSpec(
            program=CreditProgram.COFINAVIT,
            name="Cofinavit",
            opening_commission_rate=Decimal("0.0075"),
            prepay_commission_rate=Decimal("0.00"),
            ltv_rule="FIXED_95",
            min_income=Decimal("7500"),
            min_loan_amount=Decimal("120000"),
            max_loan_amount=Decimal("15000000"),
            min_property_value=Decimal("300000"),
            pti=Decimal("0.65"),
            brand_code="CREDIRESIDENCIAL",
        ),
        CreditProgram.PASIVO_HIPOTECARIO: ProgramSpec(
            program=CreditProgram.PASIVO_HIPOTECARIO,
            name="Pasivo Hipotecario",
            opening_commission_rate=Decimal("0.00"),
            prepay_commission_rate=Decimal("0.03"),
            ltv_rule="MATRIX_AI_AJ",
            min_income=Decimal("10000"),
            min_loan_amount=Decimal("125000"),
            max_loan_amount=Decimal("15000000"),
            min_property_value=Decimal("0"),
            pti=Decimal("0.65"),
            brand_code="CREDIRESIDENCIAL",
        ),
        CreditProgram.PASIVO_APOYO_INFONAVIT: ProgramSpec(
            program=CreditProgram.PASIVO_APOYO_INFONAVIT,
            name="Pasivo Hipotecario con Apoyo Infonavit",
            opening_commission_rate=Decimal("0.00"),
            prepay_commission_rate=Decimal("0.03"),
            ltv_rule="MATRIX_AH",
            min_income=Decimal("10000"),
            min_loan_amount=Decimal("125000"),
            max_loan_amount=Decimal("15000000"),
            min_property_value=Decimal("0"),
            pti=Decimal("0.65"),
            brand_code="CREDIRESIDENCIAL",
        ),
        CreditProgram.LIQUIDEZ_VIVIENDA: ProgramSpec(
            program=CreditProgram.LIQUIDEZ_VIVIENDA,
            name="Liquidez Vivienda",
            opening_commission_rate=Decimal("0.0125"),
            prepay_commission_rate=Decimal("0.03"),
            ltv_rule="MATRIX_AI_AJ",
            min_income=Decimal("20000"),
            min_loan_amount=Decimal("150000"),
            max_loan_amount=Decimal("2500000"),
            min_property_value=Decimal("1000000"),
            pti=Decimal("0.55"),
            brand_code="CREDILIQUIDEZ",
        ),
        CreditProgram.CICB_COFINAVIT: ProgramSpec(
            program=CreditProgram.CICB_COFINAVIT,
            name="CI+CB Cofinavit",
            opening_commission_rate=Decimal("0.0125"),
            prepay_commission_rate=Decimal("0.00"),
            ltv_rule="FIXED_90",
            min_income=Decimal("10000"),
            min_loan_amount=Decimal("250000"),
            max_loan_amount=Decimal("15000000"),
            min_property_value=Decimal("300000"),
            pti=Decimal("0.55"),
            brand_code="CREDIRESIDENCIAL",
        ),
    }
)


LTV_MATRIX: Mapping[int, LtvRow] = MappingProxyType(
    {
        1: LtvRow(
            risk_index=1,
            emp_with_support_le_10m=Decimal("0.95"),
            emp_no_support_le_10m=Decimal("0.95"),
            indep_le_10m=Decimal("0.90"),
            indep_pasivo_le_10m=Decimal("0.95"),
            emp_le_15m=Decimal("0.95"),
            indep_le_15m=Decimal("0.90"),
            le_20m=Decimal("0.70"),
            le_25m=Decimal("0.65"),
            gt_25m=Decimal("0.60"),
            pti_ref=Decimal("0.55"),
        ),
        2: LtvRow(
            risk_index=2,
            emp_with_support_le_10m=Decimal("0.95"),
            emp_no_support_le_10m=Decimal("0.95"),
            indep_le_10m=Decimal("0.90"),
            indep_pasivo_le_10m=Decimal("0.95"),
            emp_le_15m=Decimal("0.95"),
            indep_le_15m=Decimal("0.90"),
            le_20m=Decimal("0.70"),
            le_25m=Decimal("0.65"),
            gt_25m=Decimal("0.50"),
            pti_ref=Decimal("0.55"),
        ),
        3: LtvRow(
            risk_index=3,
            emp_with_support_le_10m=Decimal("0.95"),
            emp_no_support_le_10m=Decimal("0.90"),
            indep_le_10m=Decimal("0.85"),
            indep_pasivo_le_10m=Decimal("0.95"),
            emp_le_15m=Decimal("0.70"),
            indep_le_15m=Decimal("0.70"),
            le_20m=Decimal("0.55"),
            le_25m=Decimal("0.50"),
            gt_25m=None,
            pti_ref=Decimal("0.55"),
        ),
        4: LtvRow(
            risk_index=4,
            emp_with_support_le_10m=Decimal("0.85"),
            emp_no_support_le_10m=Decimal("0.85"),
            indep_le_10m=Decimal("0.75"),
            indep_pasivo_le_10m=Decimal("0.85"),
            emp_le_15m=Decimal("0.55"),
            indep_le_15m=Decimal("0.55"),
            le_20m=Decimal("0.55"),
            le_25m=None,
            gt_25m=None,
            pti_ref=Decimal("0.50"),
        ),
        5: LtvRow(
            risk_index=5,
            emp_with_support_le_10m=Decimal("0.85"),
            emp_no_support_le_10m=Decimal("0.85"),
            indep_le_10m=Decimal("0.75"),
            indep_pasivo_le_10m=Decimal("0.85"),
            emp_le_15m=Decimal("0.55"),
            indep_le_15m=Decimal("0.55"),
            le_20m=Decimal("0.55"),
            le_25m=None,
            gt_25m=None,
            pti_ref=Decimal("0.45"),
        ),
    }
)


# W-11: Parametrizado por (Campaign, risk_index) para facilitar reactivaciones futuras de IR 2..5.
PRICING_TABLE: Mapping[tuple[Campaign, int], CampaignPricingSpec] = MappingProxyType(
    {
        (Campaign.NINGUNA, 1): CampaignPricingSpec(
            campaign=Campaign.NINGUNA,
            risk_index=1,
            valora_rate=Decimal("0.1075"),
            valora_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_20: Decimal("9.31"),
                    LoanTerm.ANIOS_15: Decimal("10.40"),
                    LoanTerm.ANIOS_10: Decimal("12.83"),
                }
            ),
            valora_annual_increase=Decimal("0.0220"),
            valora_floor_rate=Decimal("0.1000"),
            valora_ceiling_rate=Decimal("0.1200"),
            po_rate=Decimal("0.1075"),
            po_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_7: Decimal("17.10"),
                    LoanTerm.ANIOS_10: Decimal("13.73"),
                    LoanTerm.ANIOS_15: Decimal("11.32"),
                    LoanTerm.ANIOS_20: Decimal("10.27"),
                }
            ),
            po_rate_drop_per_year=Decimal("0.0015"),
        ),
        (Campaign.WEALTH_MANAGEMENT, 1): CampaignPricingSpec(
            campaign=Campaign.WEALTH_MANAGEMENT,
            risk_index=1,
            valora_rate=Decimal("0.0925"),
            valora_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_20: Decimal("8.12"),
                    LoanTerm.ANIOS_15: Decimal("9.30"),
                    LoanTerm.ANIOS_10: Decimal("11.84"),
                }
            ),
            valora_annual_increase=Decimal("0.0260"),
            valora_floor_rate=Decimal("0.0900"),
            valora_ceiling_rate=Decimal("0.1050"),
            po_rate=Decimal("0.0950"),
            po_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_7: Decimal("16.42"),
                    LoanTerm.ANIOS_10: Decimal("13.02"),
                    LoanTerm.ANIOS_15: Decimal("10.53"),
                    LoanTerm.ANIOS_20: Decimal("9.42"),
                }
            ),
            po_rate_drop_per_year=Decimal("0.0010"),
        ),
        (Campaign.HIPOTECA_GREEN, 1): CampaignPricingSpec(
            campaign=Campaign.HIPOTECA_GREEN,
            risk_index=1,
            valora_rate=Decimal("0.0975"),
            valora_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_20: Decimal("8.44"),
                    LoanTerm.ANIOS_15: Decimal("9.60"),
                    LoanTerm.ANIOS_10: Decimal("12.14"),
                }
            ),
            valora_annual_increase=Decimal("0.0250"),
            valora_floor_rate=Decimal("0.0950"),
            valora_ceiling_rate=Decimal("0.1075"),
            po_rate=Decimal("0.1000"),
            po_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_7: Decimal("16.70"),
                    LoanTerm.ANIOS_10: Decimal("13.30"),
                    LoanTerm.ANIOS_15: Decimal("10.84"),
                    LoanTerm.ANIOS_20: Decimal("9.75"),
                }
            ),
            po_rate_drop_per_year=Decimal("0.0010"),
        ),
        (Campaign.VINCULACION, 1): CampaignPricingSpec(
            campaign=Campaign.VINCULACION,
            risk_index=1,
            valora_rate=Decimal("0.0925"),
            valora_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_20: Decimal("8.12"),
                    LoanTerm.ANIOS_15: Decimal("9.30"),
                    LoanTerm.ANIOS_10: Decimal("11.84"),
                }
            ),
            valora_annual_increase=Decimal("0.0260"),
            valora_floor_rate=Decimal("0.0900"),
            valora_ceiling_rate=Decimal("0.1050"),
            po_rate=Decimal("0.0950"),
            po_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_7: Decimal("16.42"),
                    LoanTerm.ANIOS_10: Decimal("13.02"),
                    LoanTerm.ANIOS_15: Decimal("10.53"),
                    LoanTerm.ANIOS_20: Decimal("9.42"),
                }
            ),
            po_rate_drop_per_year=Decimal("0.0010"),
        ),
        (Campaign.ENGANCHE_ALTO_PASIVO, 1): CampaignPricingSpec(
            campaign=Campaign.ENGANCHE_ALTO_PASIVO,
            risk_index=1,
            valora_rate=Decimal("0.0975"),
            valora_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_20: Decimal("8.44"),
                    LoanTerm.ANIOS_15: Decimal("9.60"),
                    LoanTerm.ANIOS_10: Decimal("12.14"),
                }
            ),
            valora_annual_increase=Decimal("0.0250"),
            valora_floor_rate=Decimal("0.0950"),
            valora_ceiling_rate=Decimal("0.1075"),
            po_rate=Decimal("0.1000"),
            po_ppm_by_term=MappingProxyType(
                {
                    LoanTerm.ANIOS_7: Decimal("16.70"),
                    LoanTerm.ANIOS_10: Decimal("13.30"),
                    LoanTerm.ANIOS_15: Decimal("10.84"),
                    LoanTerm.ANIOS_20: Decimal("9.75"),
                }
            ),
            po_rate_drop_per_year=Decimal("0.0010"),
        ),
    }
)


# 22 tramos completos de avalúo hipotecario (filas 91..112 de la Sección 4.4).
APPRAISAL_TIERS: tuple[AppraisalTier, ...] = (
    AppraisalTier(Decimal("0.01"), Decimal("500000.00"), Decimal("1900.00"), Decimal("1253.00")),
    AppraisalTier(Decimal("500001.00"), Decimal("1000000.00"), Decimal("3300.00"), Decimal("1740.00")),
    AppraisalTier(Decimal("1000001.00"), Decimal("1500000.00"), Decimal("4500.00"), Decimal("2784.00")),
    AppraisalTier(Decimal("1500001.00"), Decimal("2000000.00"), Decimal("5750.00"), Decimal("2784.00")),
    AppraisalTier(Decimal("2000001.00"), Decimal("2500000.00"), Decimal("7000.00"), Decimal("4663.00")),
    AppraisalTier(Decimal("2500001.00"), Decimal("3000000.00"), Decimal("8200.00"), Decimal("4663.00")),
    AppraisalTier(Decimal("3000001.00"), Decimal("4000000.00"), Decimal("11000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("4000001.00"), Decimal("5000000.00"), Decimal("13900.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("5000001.00"), Decimal("6000000.00"), Decimal("15500.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("6000001.00"), Decimal("7000000.00"), Decimal("19000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("7000001.00"), Decimal("8000000.00"), Decimal("20000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("8000001.00"), Decimal("9000000.00"), Decimal("20100.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("9000001.00"), Decimal("10000000.00"), Decimal("22500.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("10000001.00"), Decimal("11000000.00"), Decimal("27000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("11000001.00"), Decimal("12000000.00"), Decimal("28000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("12000001.00"), Decimal("13000000.00"), Decimal("30000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("13000001.00"), Decimal("14000000.00"), Decimal("32000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("14000001.00"), Decimal("15000000.00"), Decimal("34000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("15000001.00"), Decimal("20000000.00"), Decimal("37000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("20000001.00"), Decimal("25000000.00"), Decimal("39000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("25000001.00"), Decimal("30000000.00"), Decimal("40000.00"), Decimal("5000.00")),
    AppraisalTier(Decimal("30000001.00"), Decimal("30000000.00"), Decimal("40000.00"), Decimal("5000.00")),
)


# Catálogo RECA (Sección 4.6) aislado para reemplazar fácilmente por registros propios.
RECA_CATALOG: Mapping[str, RecaEntry] = MappingProxyType(
    {
        "1-2-1": RecaEntry("1-2-1", 9, "Adquisición Pagos Oportunos", "0319-138-038229/06-03318-1225", "2025-12-11", 1, 2, 1),
        "2-2-1": RecaEntry("2-2-1", 10, "Adquisición Con Apoyo Pagos Oportunos", "0319-138-038230/04-03319-1225", "2025-12-11", 2, 2, 1),
        "1-1-1": RecaEntry("1-1-1", 11, "Adquisición Valora", "0319-138-038232/05-03320-1225", "2025-12-11", 1, 1, 1),
        "2-1-1": RecaEntry("2-1-1", 12, "Adquisición Con Apoyo Valora", "0319-138-038235/04-03321-1225", "2025-12-11", 2, 1, 1),
        "4-2-1": RecaEntry("4-2-1", 21, "Pago de Pasivos Pagos Oportunos", "0319-138-007480/26-03330-1225", "2025-12-11", 4, 2, 1),
        "4-1-1": RecaEntry("4-1-1", 22, "Pago de Pasivos Valora", "0319-138-007481/26-03331-1225", "2025-12-11", 4, 1, 1),
        "6-2-1": RecaEntry("6-2-1", 25, "Liquidez Vivienda Pagos Oportunos", "0319-138-007482/27-03334-1225", "2025-12-11", 6, 2, 1),
        "6-1-1": RecaEntry("6-1-1", 26, "Liquidez Vivienda Valora", "0319-138-007483/27-03335-1225", "2025-12-11", 6, 1, 1),
        "3-2-1": RecaEntry("3-2-1", 27, "Cofinavit Pagos Oportunos", "0319-138-038237/04-03336-1225", "2025-12-11", 3, 2, 1),
        "3-2-2": RecaEntry("3-2-2", 28, "Cofinavit Conyugales Pagos Oportunos", "0319-138-038238/04-03337-1225", "2025-12-11", 3, 2, 2),
        "3-1-1": RecaEntry("3-1-1", 29, "Cofinavit Valora", "0319-138-038239/04-03338-1225", "2025-12-11", 3, 1, 1),
        "3-1-2": RecaEntry("3-1-2", 30, "Cofinavit Conyugales Valora", "0319-138-038240/04-03339-1225", "2025-12-11", 3, 1, 2),
        "5-2-1": RecaEntry("5-2-1", 23, "Pago de Pasivos Pagos Oportunos con Apoyo Infonavit", "0319-138-024405/17-03332-1225", "2025-12-11", 5, 2, 1),
        "5-1-1": RecaEntry("5-1-1", 24, "Pago de Pasivos Valora con Apoyo Infonavit", "0319-138-024404/17-03333-1225", "2025-12-11", 5, 1, 1),
        "7-1-1": RecaEntry("7-1-1", 44, "Cofinavit CI+CB Valora", "0319-138-035429/08-03354-1225", "2025-12-11", 7, 1, 1),
        "7-1-2": RecaEntry("7-1-2", 45, "Cofinavit CI+CB Conyugal Valora", "0319-138-035430/08-03355-1225", "2025-12-11", 7, 1, 2),
        "7-2-1": RecaEntry("7-2-1", 46, "Cofinavit CI+CB Pagos Oportunos", "0319-138-035431/08-03356-1225", "2025-12-11", 7, 2, 1),
        "7-2-2": RecaEntry("7-2-2", 47, "Cofinavit CI+CB Conyugal Pagos Oportunos", "0319-138-035432/08-03357-1225", "2025-12-11", 7, 2, 2),
    }
)


class CatalogRepository:
    """Acceso de solo lectura a todos los catálogos operativos del simulador.

    Nota (W-12): la hoja histórica 'Pol' se omite deliberadamente; la única
    fuente de verdad operativa son los catálogos de Simulador v2026.11 y RECAS.
    """

    def get_program(self, program: CreditProgram) -> ProgramSpec:
        return PROGRAMS[program]

    def get_ltv_row(self, risk_index: int) -> LtvRow:
        if risk_index not in LTV_MATRIX:
            raise ValueError(f"Índice de riesgo inválido: {risk_index}. Debe estar entre 1 y 5.")
        return LTV_MATRIX[risk_index]

    def get_pricing(self, campaign: Campaign, risk_index: int = 1) -> CampaignPricingSpec:
        key = (campaign, risk_index)
        if key in PRICING_TABLE:
            return PRICING_TABLE[key]
        # W-11: si se solicita IR 2..5 sin filas cargadas, hace fallback explícito a IR=1.
        fallback_key = (campaign, 1)
        if fallback_key in PRICING_TABLE:
            return PRICING_TABLE[fallback_key]
        raise KeyError(f"No existe pricing configurado para {campaign.name} con IR={risk_index}.")

    def lookup_appraisal_cost(self, housing_value: Decimal) -> Decimal:
        """Replica VLOOKUP aproximado en S91:U112 con corrección W-04 para housing_value <= 0."""
        # W-04: evitar #N/A cuando O24 <= 0 retornando 0.00.
        if housing_value <= Decimal("0"):
            return Decimal("0")
        matched = APPRAISAL_TIERS[0].appraisal_cost
        for tier in APPRAISAL_TIERS:
            if housing_value >= tier.min_value:
                matched = tier.appraisal_cost
            else:
                break
        return matched

    def find_reca(self, reca_key: str) -> Optional[RecaEntry]:
        return RECA_CATALOG.get(reca_key)


DEFAULT_CATALOG = CatalogRepository()
