"""Pestaña 1: Resumen del Simulador, KPIs, desglose de gastos, alertas y gráficas."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from engine.models import SimulationResponse
from ui.components.charts import build_balance_chart, build_payment_composition_chart
from ui.theme import format_cat, format_currency, format_percent


def render_summary_tab(response: SimulationResponse) -> None:
    """Renderiza los KPIs principales, desglose de gastos e inversión, alertas y gráficas."""
    inp = response.inputs
    pricing = response.pricing
    sizing = response.sizing
    totals = response.totals

    for alert in response.alerts:
        if alert.severity == "error":
            st.error(alert.message)
        elif alert.severity == "warning":
            st.warning(alert.message)
        else:
            st.info(alert.message)

    st.caption(
        f"**Programa:** {inp.program.label}  |  "
        f"**Esquema:** {inp.scheme.label} ({inp.term.label})  |  "
        f"**Campaña efectiva:** {pricing.effective_campaign.label(inp.program)}"
    )

    # Fila 1 de KPIs principales
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Crédito a amortizar", format_currency(sizing.initial_balance))
    k2.metric("Mensualidad mes 1", format_currency(totals.first_monthly_payment))
    k3.metric("Tasa inicial anual", format_percent(pricing.initial_rate, 2))
    k4.metric("CAT oficial (sin IVA)", format_cat(totals.official_cat))

    # Fila 2 de KPIs complementarios
    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Valor de vivienda", format_currency(sizing.housing_value))
    k6.metric("% Financiamiento", format_percent(sizing.financing_pct, 1))
    k7.metric("Ingreso mínimo requerido", format_currency(sizing.min_required_income))
    payoff_text = (
        f"{totals.payoff_years} años, {totals.payoff_months} meses"
        if totals.payoff_period > 0
        else "N/A"
    )
    k8.metric("Liquidación real", payoff_text)

    st.subheader("Desglose de crédito, gastos de originación e inversión")
    col_left, col_right = st.columns(2)

    credit_rows = [
        ("Crédito máximo autorizado", format_currency(sizing.max_loan)),
        ("Crédito solicitado", format_currency(sizing.requested_loan)),
        ("Gastos notariales financiados", format_currency(sizing.financed_expenses)),
        ("Monto total a amortizar", format_currency(sizing.initial_balance)),
        ("Pago por millar (PPM)", format_currency(pricing.ppm)),
        ("Incremento anual de erogación", format_percent(pricing.annual_payment_increase, 2)),
        ("Tasa piso", format_percent(pricing.floor_rate, 2)),
        ("CAT real (con prepagos/apoyo)", format_percent(totals.real_cat, 2)),
    ]
    if sizing.infonavit_loan_total > 0 or sizing.ssv_total > 0:
        credit_rows.extend(
            [
                ("Crédito Infonavit", format_currency(sizing.infonavit_loan_total)),
                ("Subcuenta de Vivienda (SSV)", format_currency(sizing.ssv_total)),
                ("Recursos totales", format_currency(sizing.total_resources)),
            ]
        )
    if totals.initial_bimonthly_support > 0:
        credit_rows.append(
            ("Aportación bimestral inicial (Apoyo)", format_currency(totals.initial_bimonthly_support))
        )

    expense_rows = [
        ("Gastos de originación Infonavit (3%)", format_currency(sizing.infonavit_origination_expense)),
        ("Impuestos y derechos", format_currency(sizing.taxes_and_rights)),
        ("Honorarios notariales", format_currency(sizing.notary_fees)),
        (
            "Avalúo hipotecario"
            + (" (Favor de cotizar)" if sizing.requires_appraisal_quote else ""),
            format_currency(sizing.appraisal_cost),
        ),
        ("Comisión por apertura", format_currency(sizing.opening_commission)),
        ("Gastos financiados deducidos", format_currency(-sizing.financed_expenses)),
        ("Total gastos de originación netos", format_currency(sizing.net_origination_expenses)),
        ("Enganche", format_currency(sizing.down_payment)),
        ("Inversión inicial total del cliente", format_currency(sizing.client_investment)),
    ]

    with col_left:
        st.dataframe(
            pd.DataFrame(credit_rows, columns=["Concepto financiero", "Valor"]),
            use_container_width=True,
            hide_index=True,
        )
    with col_right:
        st.dataframe(
            pd.DataFrame(expense_rows, columns=["Gastos e inversión", "Importe"]),
            use_container_width=True,
            hide_index=True,
        )

    if totals.payoff_period > 0:
        st.subheader("Análisis visual del crédito")
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.plotly_chart(build_balance_chart(response), use_container_width=True)
        with c_chart2:
            st.plotly_chart(build_payment_composition_chart(response), use_container_width=True)
