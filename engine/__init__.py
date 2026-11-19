"""Motor financiero puro del Simulador Hipotecario (sin dependencias de interfaz)."""

from .models import (
    AmortizationRow,
    AmortizationTotals,
    CalcMode,
    Campaign,
    CommissionType,
    ContractCoverData,
    CreditProgram,
    EconomicActivity,
    InsuranceOption,
    LoanSizingResult,
    LoanTerm,
    PrepayMode,
    PricingResult,
    ProductScheme,
    SimulationInput,
    SimulationResponse,
    ValidationAlert,
)
from .simulator import run_simulation

__all__ = [
    "AmortizationRow",
    "AmortizationTotals",
    "CalcMode",
    "Campaign",
    "CommissionType",
    "ContractCoverData",
    "CreditProgram",
    "EconomicActivity",
    "InsuranceOption",
    "LoanSizingResult",
    "LoanTerm",
    "PrepayMode",
    "PricingResult",
    "ProductScheme",
    "SimulationInput",
    "SimulationResponse",
    "ValidationAlert",
    "run_simulation",
]
