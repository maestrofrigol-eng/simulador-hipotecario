"""Modelos de dominio inmutables y enumeraciones del motor hipotecario.

Usa estrictamente ``decimal.Decimal`` para montos y tasas y ``datetime.date``
para fechas, sin dependencias de capa visual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import IntEnum
from typing import Mapping, Optional


MAX_PERIODS = 240
DECIMAL_PREC = 34


class CreditProgram(IntEnum):
    """Catálogo de programas comerciales de crédito (Simulador!U39)."""

    ADQUISICION_TRADICIONAL = 1
    APOYO_INFONAVIT = 2
    COFINAVIT = 3
    PASIVO_HIPOTECARIO = 4
    PASIVO_APOYO_INFONAVIT = 5
    LIQUIDEZ_VIVIENDA = 6
    CICB_COFINAVIT = 7

    @property
    def label(self) -> str:
        return {
            CreditProgram.ADQUISICION_TRADICIONAL: "Adquisición Tradicional",
            CreditProgram.APOYO_INFONAVIT: "Adquisición con Apoyo Infonavit",
            CreditProgram.COFINAVIT: "Cofinavit",
            CreditProgram.PASIVO_HIPOTECARIO: "Pasivo Hipotecario",
            CreditProgram.PASIVO_APOYO_INFONAVIT: "Pasivo Hipotecario con Apoyo Infonavit",
            CreditProgram.LIQUIDEZ_VIVIENDA: "Liquidez Vivienda",
            CreditProgram.CICB_COFINAVIT: "CI+CB Cofinavit",
        }[self]

    @property
    def is_pasivo(self) -> bool:
        return self in (
            CreditProgram.PASIVO_HIPOTECARIO,
            CreditProgram.PASIVO_APOYO_INFONAVIT,
        )

    @property
    def is_apoyo_infonavit(self) -> bool:
        return self in (
            CreditProgram.APOYO_INFONAVIT,
            CreditProgram.PASIVO_APOYO_INFONAVIT,
        )

    @property
    def is_cofinavit_family(self) -> bool:
        return self in (CreditProgram.COFINAVIT, CreditProgram.CICB_COFINAVIT)


class Campaign(IntEnum):
    """Campañas comerciales disponibles (Simulador!W61 / W62)."""

    NINGUNA = 1
    WEALTH_MANAGEMENT = 2
    HIPOTECA_GREEN = 3
    VINCULACION = 4
    ENGANCHE_ALTO_PASIVO = 5

    def label(self, program: Optional[CreditProgram] = None) -> str:
        if self == Campaign.ENGANCHE_ALTO_PASIVO:
            if program is not None and program.is_pasivo:
                return "Pasivo"
            return "Enganche Alto / Pasivo" if program is None else "Enganche Alto"
        return {
            Campaign.NINGUNA: "Ninguna",
            Campaign.WEALTH_MANAGEMENT: "Wealth Management",
            Campaign.HIPOTECA_GREEN: "Hipoteca Green",
            Campaign.VINCULACION: "Vinculación",
        }[self]


class CalcMode(IntEnum):
    """Modalidad de cálculo del valor base (Simulador!Y41)."""

    POR_VALOR_INMUEBLE = 1
    POR_INGRESOS = 2
    POR_IMPORTE_CREDITO = 3

    @property
    def label(self) -> str:
        return {
            CalcMode.POR_VALOR_INMUEBLE: "Por Valor del Inmueble",
            CalcMode.POR_INGRESOS: "Por Ingresos",
            CalcMode.POR_IMPORTE_CREDITO: "Por Importe de Crédito",
        }[self]


class EconomicActivity(IntEnum):
    """Actividad económica del acreditado (Simulador!X29)."""

    EMPLEADO = 1
    INDEPENDIENTE = 2

    @property
    def label(self) -> str:
        return {
            EconomicActivity.EMPLEADO: "Empleado",
            EconomicActivity.INDEPENDIENTE: "Independiente",
        }[self]


class ProductScheme(IntEnum):
    """Esquema de amortización (Simulador!T68)."""

    VALORA = 1
    PAGOS_OPORTUNOS = 2

    @property
    def label(self) -> str:
        return {
            ProductScheme.VALORA: "Valora",
            ProductScheme.PAGOS_OPORTUNOS: "Pagos Oportunos",
        }[self]


class LoanTerm(IntEnum):
    """Plazo del crédito (Simulador!T62)."""

    ANIOS_7 = 1
    ANIOS_10 = 2
    ANIOS_15 = 3
    ANIOS_20 = 4

    @property
    def years(self) -> int:
        return {
            LoanTerm.ANIOS_7: 7,
            LoanTerm.ANIOS_10: 10,
            LoanTerm.ANIOS_15: 15,
            LoanTerm.ANIOS_20: 20,
        }[self]

    @property
    def months(self) -> int:
        return self.years * 12

    @property
    def label(self) -> str:
        return f"{self.years} años"


class CommissionType(IntEnum):
    """Modalidad de comisión (Simulador!T41)."""

    CONTRATACION_CREDITO = 1
    PAGO_ANTICIPADO = 2

    @property
    def label(self) -> str:
        return {
            CommissionType.CONTRATACION_CREDITO: "Contratación - crédito",
            CommissionType.PAGO_ANTICIPADO: "Pago anticipado",
        }[self]


class InsuranceOption(IntEnum):
    """Opción de seguros del crédito (Simulador!U29).

    1 = Seguros externos (sin seguros incluidos en la mensualidad).
    2 = Seguros incluidos (calcula seguro de vida/desempleo y daños).
    """

    SEGUROS_EXTERNOS = 1
    SEGUROS_INCLUIDOS = 2

    @property
    def label(self) -> str:
        return {
            InsuranceOption.SEGUROS_EXTERNOS: "Seguros externos",
            InsuranceOption.SEGUROS_INCLUIDOS: "Seguros incluidos",
        }[self]

    @property
    def is_external(self) -> bool:
        return self == InsuranceOption.SEGUROS_EXTERNOS


class PrepayMode(IntEnum):
    """Aplicación de anticipos a capital (Tabla!AE3)."""

    DISMINUCION_PLAZO = 1
    DISMINUCION_PAGO = 2

    @property
    def label(self) -> str:
        return {
            PrepayMode.DISMINUCION_PLAZO: "Disminución de plazo",
            PrepayMode.DISMINUCION_PAGO: "Disminución de pago",
        }[self]


def normalize_prepayments(
    prepayments: Optional[Mapping[int, Decimal] | tuple[Decimal, ...] | list[Decimal]],
) -> tuple[Decimal, ...]:
    """Convierte un diccionario {periodo_1_a_240: monto} o secuencia a tupla de 240 Decimals."""
    result = [Decimal("0")] * MAX_PERIODS
    if prepayments is None:
        return tuple(result)
    if isinstance(prepayments, Mapping):
        for period, amount in prepayments.items():
            if 1 <= period <= MAX_PERIODS and amount is not None:
                val = Decimal(str(amount))
                if val < Decimal("0"):
                    raise ValueError(f"El prepago del periodo {period} no puede ser negativo.")
                result[period - 1] = val
    else:
        for idx, amount in enumerate(prepayments):
            if idx >= MAX_PERIODS:
                break
            if amount is not None:
                val = Decimal(str(amount))
                if val < Decimal("0"):
                    raise ValueError(f"El prepago del periodo {idx + 1} no puede ser negativo.")
                result[idx] = val
    return tuple(result)


@dataclass(frozen=True)
class SimulationInput:
    """Entradas completas e inmutables para ejecutar una cotización hipotecaria."""

    quote_date: date = field(default_factory=date.today)
    advisor_name: str = ""
    branch: str = ""
    client_name: str = ""
    advisor_phone: str = ""
    client_phone: str = ""

    program: CreditProgram = CreditProgram.ADQUISICION_TRADICIONAL
    campaign: Campaign = Campaign.NINGUNA
    calc_mode: CalcMode = CalcMode.POR_INGRESOS
    base_value: Decimal = Decimal("0")
    destructible_value: Optional[Decimal] = None
    infonavit_salary: Decimal = Decimal("0")
    economic_activity: EconomicActivity = EconomicActivity.EMPLEADO
    scheme: ProductScheme = ProductScheme.VALORA
    term: LoanTerm = LoanTerm.ANIOS_20
    risk_index: int = 1
    commission_type: CommissionType = CommissionType.CONTRATACION_CREDITO
    insurance_option: InsuranceOption = InsuranceOption.SEGUROS_INCLUIDOS

    manual_opening_commission_rate: Optional[Decimal] = None
    requested_loan: Optional[Decimal] = None
    finance_notary_fees: bool = True
    manual_tax_rate: Optional[Decimal] = None
    manual_notary_rate: Optional[Decimal] = None

    ssv_titular: Decimal = Decimal("0")
    infonavit_credit_titular: Decimal = Decimal("0")
    ssv_spouse_cicb: Decimal = Decimal("0")
    ssv_spouse_cofinavit: Decimal = Decimal("0")
    infonavit_credit_spouse: Decimal = Decimal("0")
    exact_infonavit_expenses: Decimal = Decimal("0")

    prepay_mode: PrepayMode = PrepayMode.DISMINUCION_PLAZO
    prepayments: tuple[Decimal, ...] = field(
        default_factory=lambda: tuple(Decimal("0") for _ in range(MAX_PERIODS))
    )

    def __post_init__(self) -> None:
        if len(self.prepayments) != MAX_PERIODS:
            object.__setattr__(self, "prepayments", normalize_prepayments(self.prepayments))

    @classmethod
    def reset_to_defaults(cls, quote_date: Optional[date] = None) -> SimulationInput:
        """Equivalente limpio a Borrar_datos: limpia campos opcionales y usa crédito máximo."""
        return cls(quote_date=quote_date or date.today())


@dataclass(frozen=True)
class ValidationAlert:
    """Alerta de negocio o validación no bloqueante."""

    code: str
    severity: str  # "warning" | "error" | "info"
    message: str


@dataclass(frozen=True)
class PricingResult:
    """Resultado de resolución comercial y de pricing (Bloque A)."""

    effective_campaign: Campaign
    initial_rate: Decimal
    ppm: Decimal
    annual_payment_increase: Decimal
    floor_rate: Decimal
    ceiling_rate: Decimal
    po_rate_drop_per_year: Decimal
    ltv: Decimal
    pti: Decimal
    opening_commission_rate: Decimal
    prepay_commission_rate: Decimal


@dataclass(frozen=True)
class LoanSizingResult:
    """Resultado de dimensionamiento de crédito, gastos e inversión (Bloques B y C)."""

    housing_value: Decimal
    max_loan: Decimal
    requested_loan: Decimal
    financed_expenses: Decimal
    initial_balance: Decimal
    financing_pct: Decimal
    infonavit_loan_total: Decimal
    ssv_total: Decimal
    total_resources: Decimal

    infonavit_origination_expense: Decimal
    taxes_and_rights: Decimal
    notary_fees: Decimal
    appraisal_cost: Decimal
    requires_appraisal_quote: bool
    opening_commission: Decimal
    net_origination_expenses: Decimal
    down_payment: Decimal
    client_investment: Decimal
    min_required_income: Decimal


@dataclass(frozen=True)
class AmortizationRow:
    """Fila mensual de la tabla de amortización (A15:Y254)."""

    period: int
    cut_date: Optional[date]
    days_in_month: int
    initial_balance: Decimal
    scheduled_payment: Decimal  # Erogación (D)
    interest: Decimal  # Interés (F)
    principal: Decimal  # Amortización (H)
    prepayment: Decimal  # Prepago (J)
    prepayment_penalty: Decimal  # Penalización (L)
    infonavit_support: Decimal  # Apoyo Infonavit (N)
    annual_rate: Decimal  # Tasa anual (P)
    final_balance: Decimal  # Saldo final (R)
    life_insurance: Decimal  # Seguro de vida y desempleo (T)
    damage_insurance: Decimal  # Seguro de daños (V)
    total_monthly_payment: Decimal  # Pago mensual total (Y)


@dataclass(frozen=True)
class AmortizationTotals:
    """Totales acumulados (fila 256) y métricas de liquidación y CAT."""

    total_scheduled_payment: Decimal  # D256
    total_interest: Decimal  # F256
    total_principal: Decimal  # H256
    total_prepayments: Decimal  # J256
    total_penalties: Decimal  # L256
    total_infonavit_support: Decimal  # N256
    total_life_insurance: Decimal  # T256
    total_damage_insurance: Decimal  # V256
    total_amount_to_pay: Decimal  # Y256 / Carat!D12

    official_cat: Decimal  # I40 / B11 (corrida base contractual AT:BB)
    real_cat: Decimal  # AK10 (corrida real con prepagos/apoyo)
    first_monthly_payment: Decimal  # I41 / Y15
    payoff_period: int  # AE14
    payoff_years: int  # Y10
    payoff_months: int  # Y11
    initial_bimonthly_support: Decimal  # N16


@dataclass(frozen=True)
class ContractCoverData:
    """Datos estructurados de la Carátula de Crédito CONDUSEF y registro RECA."""

    client_name: str
    commercial_product_name: str
    term_label: str
    currency_label: str
    official_cat: Decimal
    initial_rate: Decimal
    loan_amount: Decimal
    total_amount_to_pay: Decimal
    opening_commission_text: str
    late_payment_fee: Decimal
    late_payment_penalty_text: str
    prepayment_commission_text: str
    reca_key: str
    reca_number: str
    reca_contract_name: str
    reca_expedition_date: str


@dataclass(frozen=True)
class SimulationResponse:
    """Respuesta completa del simulador con las tres vistas del modelo original."""

    inputs: SimulationInput
    pricing: PricingResult
    sizing: LoanSizingResult
    schedule: tuple[AmortizationRow, ...]
    totals: AmortizationTotals
    contract_cover: ContractCoverData
    alerts: tuple[ValidationAlert, ...]
