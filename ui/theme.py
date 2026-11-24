"""Paleta de colores, formateadores financieros y CSS mínimo centralizado.

Edita ``PALETTE`` para cambiar colores de interfaz y gráficas de Plotly desde un
solo lugar. El bloque ``CUSTOM_CSS`` se mantiene deliberadamente corto y limpio
para facilitar futuras iteraciones visuales.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

PALETTE: dict[str, str] = {
    "primary": "#1B4965",
    "primary_light": "#2C6E91",
    "accent": "#2A9D8F",
    "warning": "#D97706",
    "danger": "#C53030",
    "bg_page": "#F8FAFC",
    "bg_surface": "#FFFFFF",
    "bg_muted": "#EDF2F7",
    "border": "#CBD5E1",
    "text_primary": "#1A202C",
    "text_muted": "#4A5568",
    # Colores para series de gráficas Plotly
    "chart_balance": "#1B4965",
    "chart_principal": "#2A9D8F",
    "chart_interest": "#E76F51",
    "chart_insurance": "#64748B",
    "chart_prepayment": "#F4A261",
}

CURRENCY_PREFIX = "$"
PERCENT_SUFFIX = "%"


def format_currency(amount: Decimal) -> str:
    """Formatea un Decimal como moneda MXN con ROUND_HALF_UP a 2 decimales."""
    q = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if q < Decimal("0"):
        return f"-{CURRENCY_PREFIX}{abs(q):,.2f}"
    return f"{CURRENCY_PREFIX}{q:,.2f}"


def format_percent(rate: Decimal, decimals: int = 2) -> str:
    """Formatea una tasa decimal (ej. 0.1075 -> '10.75%') con ROUND_HALF_UP."""
    quant = Decimal("1").scaleb(-decimals)
    pct = (rate * Decimal("100")).quantize(quant, rounding=ROUND_HALF_UP)
    return f"{pct}{PERCENT_SUFFIX}"


def format_cat(cat: Decimal) -> str:
    """Formatea el CAT regulatorio a 1 decimal (ej. 0.125356 -> '12.5%')."""
    return format_percent(cat, decimals=1)


# CSS mínimo y comentado para facilitar rediseños sin acoplar lógica HTML.
CUSTOM_CSS = f"""
<style>
    /* Contenedor superior de marca */
    .brand-header {{
        padding: 0.75rem 1rem;
        border-left: 4px solid {PALETTE["primary"]};
        background-color: {PALETTE["bg_surface"]};
        border-radius: 6px;
        margin-bottom: 1rem;
    }}
    .brand-logo-placeholder {{
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border: 1px dashed {PALETTE["border"]};
        border-radius: 4px;
        color: {PALETTE["text_muted"]};
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }}

    .footer-note {{
        color: {PALETTE["text_muted"]};
        font-size: 0.82rem;
        margin-top: 1.5rem;
        padding-top: 0.75rem;
        border-top: 1px solid {PALETTE["border"]};
    }}
</style>
"""
