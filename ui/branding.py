"""Textos, identidad y metadatos editables de la aplicación (marca blanca).

Modifica únicamente este archivo para adaptar el simulador a una nueva
institución financiera, logotipo, avisos legales y leyendas al pie.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BrandConfig:
    """Configuración centralizada de marca e identidad textual."""

    app_title: str = "Simulador Hipotecario"
    app_subtitle: str = (
        "Cotización integral de financiamiento residencial, gastos de originación, "
        "tabla de amortización y Carátula CONDUSEF."
    )
    institution_name: str = "Institución Financiera (Marca Blanca)"
    page_icon: str = "🏠"
    logo_path: Optional[str] = None  # Ejemplo: "assets/logo.png"
    logo_placeholder_text: str = "TU LOGOTIPO AQUÍ"
    currency_code: str = "MXN"
    footer_disclaimer: str = (
        "Simulación de carácter informativo. Las cifras, tasas, seguros y CAT "
        "pueden variar al momento de la contratación formal según políticas vigentes."
    )
    condusef_note: str = (
        "El Costo Anual Total (CAT) se calcula sin IVA con fines informativos y de "
        "comparación conforme a la corrida base contractual."
    )


BRAND = BrandConfig()
