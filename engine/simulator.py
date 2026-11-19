"""Orquestador puro del motor financiero (DAG de evaluación Sección 5.1)."""

from __future__ import annotations

from .amortization_engine import run_amortization
from .catalog_repository import CatalogRepository, DEFAULT_CATALOG
from .contract_cover import assemble_contract_cover
from .loan_sizing import calculate_loan_sizing
from .models import SimulationInput, SimulationResponse
from .pricing_resolver import resolve_pricing


def run_simulation(
    sim_input: SimulationInput,
    catalog: CatalogRepository = DEFAULT_CATALOG,
) -> SimulationResponse:
    """Ejecuta el pipeline completo siguiendo el orden DAG de la Sección 5.1.

    Notas de diseño:
    - W-02: el bloque roto 'Cálculo Porción A' (Simulador!S2:AA26) se omite por no
      alimentar ninguna salida operativa.
    - W-06 / W-08: se omiten credenciales hardcodeadas y macros VBA huérfanas.
    - W-12: la hoja histórica 'Pol' no se carga como catálogo operativo.
    """
    pricing = resolve_pricing(sim_input, catalog=catalog)
    sizing, alerts = calculate_loan_sizing(sim_input, pricing, catalog=catalog)
    schedule, totals = run_amortization(sim_input, pricing, sizing)
    contract_cover = assemble_contract_cover(
        sim_input=sim_input,
        pricing=pricing,
        sizing=sizing,
        totals=totals,
        catalog=catalog,
    )
    return SimulationResponse(
        inputs=sim_input,
        pricing=pricing,
        sizing=sizing,
        schedule=schedule,
        totals=totals,
        contract_cover=contract_cover,
        alerts=alerts,
    )
