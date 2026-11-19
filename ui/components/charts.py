"""Gráficas interactivas con Plotly consumiendo la paleta de ``ui/theme.py``."""

from __future__ import annotations

import plotly.graph_objects as go

from engine.models import SimulationResponse
from ui.theme import PALETTE


def build_balance_chart(response: SimulationResponse) -> go.Figure:
    """Evolución mensual del saldo insoluto y la tasa anual aplicada."""
    active_rows = [r for r in response.schedule if r.initial_balance > 0]
    periods = [r.period for r in active_rows]
    balances = [float(r.final_balance) for r in active_rows]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=balances,
            mode="lines",
            name="Saldo insoluto",
            line={"color": PALETTE["chart_balance"], "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(27, 73, 101, 0.12)",
            hovertemplate="Mes %{x}<br>Saldo final: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Evolución del saldo insoluto",
        xaxis_title="Periodo (meses)",
        yaxis_title="Saldo (MXN)",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        plot_bgcolor=PALETTE["bg_surface"],
        paper_bgcolor=PALETTE["bg_surface"],
        font={"color": PALETTE["text_primary"]},
        margin={"l": 16, "r": 16, "t": 44, "b": 16},
        height=340,
    )
    return fig


def build_payment_composition_chart(response: SimulationResponse) -> go.Figure:
    """Composición anual acumulada de pagos (capital, interés, seguros y prepagos)."""
    active_rows = [r for r in response.schedule if r.initial_balance > 0]
    by_year: dict[int, dict[str, float]] = {}

    for row in active_rows:
        yr = ((row.period - 1) // 12) + 1
        bucket = by_year.setdefault(
            yr, {"principal": 0.0, "interest": 0.0, "insurance": 0.0, "prepayment": 0.0}
        )
        bucket["principal"] += float(row.principal)
        bucket["interest"] += float(row.interest)
        bucket["insurance"] += float(row.life_insurance + row.damage_insurance)
        bucket["prepayment"] += float(row.prepayment)

    years = sorted(by_year.keys())
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=years,
            y=[by_year[y]["principal"] for y in years],
            name="Amortización a capital",
            marker_color=PALETTE["chart_principal"],
        )
    )
    fig.add_trace(
        go.Bar(
            x=years,
            y=[by_year[y]["interest"] for y in years],
            name="Intereses",
            marker_color=PALETTE["chart_interest"],
        )
    )
    fig.add_trace(
        go.Bar(
            x=years,
            y=[by_year[y]["insurance"] for y in years],
            name="Seguros (vida + daños)",
            marker_color=PALETTE["chart_insurance"],
        )
    )
    if any(by_year[y]["prepayment"] > 0 for y in years):
        fig.add_trace(
            go.Bar(
                x=years,
                y=[by_year[y]["prepayment"] for y in years],
                name="Prepagos a capital",
                marker_color=PALETTE["chart_prepayment"],
            )
        )

    fig.update_layout(
        title="Composición anual del flujo de pagos",
        barmode="stack",
        xaxis_title="Año del crédito",
        yaxis_title="Monto anual (MXN)",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        plot_bgcolor=PALETTE["bg_surface"],
        paper_bgcolor=PALETTE["bg_surface"],
        font={"color": PALETTE["text_primary"]},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        margin={"l": 16, "r": 16, "t": 60, "b": 16},
        height=340,
    )
    return fig
