"""Pestaña 2: Tabla de Amortización (240 periodos), vista mensual/anual y exportación CSV/XLSX."""

from __future__ import annotations

from io import BytesIO

import pandas as pd

from engine.models import SimulationResponse
from ui.theme import format_currency, format_percent


def build_schedule_dataframe(
    response: SimulationResponse,
    annual_view: bool = False,
) -> pd.DataFrame:
    """Construye un DataFrame limpio para visualización y exportación (marca blanca)."""
    records = []
    for row in response.schedule:
        if annual_view and (row.period % 12 != 0 and row.period != response.totals.payoff_period):
            continue
        records.append(
            {
                "Periodo": row.period,
                "Fecha corte": row.cut_date.isoformat() if row.cut_date else "",
                "Días": row.days_in_month,
                "Saldo Inicial": round(float(row.initial_balance), 2),
                "Erogación": round(float(row.scheduled_payment), 2),
                "Interés": round(float(row.interest), 2),
                "Amortización": round(float(row.principal), 2),
                "Prepago": round(float(row.prepayment), 2),
                "Penalización": round(float(row.prepayment_penalty), 2),
                "Apoyo Infonavit": round(float(row.infonavit_support), 2),
                "Tasa Anual (%)": round(float(row.annual_rate) * 100, 2),
                "Saldo Final": round(float(row.final_balance), 2),
                "Seguro Vida": round(float(row.life_insurance), 2),
                "Seguro Daños": round(float(row.damage_insurance), 2),
                "Pago Mensual Total": round(float(row.total_monthly_payment), 2),
            }
        )
    return pd.DataFrame(records)


def export_schedule_csv(response: SimulationResponse) -> bytes:
    """Exporta los 240 periodos en formato CSV UTF-8 con BOM (compatible con Excel)."""
    df = build_schedule_dataframe(response, annual_view=False)
    return df.to_csv(index=False).encode("utf-8-sig")


def export_schedule_excel(response: SimulationResponse) -> bytes:
    """Exporta resumen y tabla de amortización a un libro Excel (.xlsx) marca blanca."""
    df_schedule = build_schedule_dataframe(response, annual_view=False)
    totals = response.totals
    sizing = response.sizing
    cover = response.contract_cover

    summary_df = pd.DataFrame(
        [
            ("Programa", response.inputs.program.label),
            ("Esquema", response.inputs.scheme.label),
            ("Plazo", response.inputs.term.label),
            ("Valor de vivienda", round(float(sizing.housing_value), 2)),
            ("Crédito a amortizar", round(float(sizing.initial_balance), 2)),
            ("Mensualidad mes 1", round(float(totals.first_monthly_payment), 2)),
            ("CAT oficial (sin IVA) %", round(float(totals.official_cat) * 100, 4)),
            ("CAT real %", round(float(totals.real_cat) * 100, 4)),
            ("Liquidación real (meses)", totals.payoff_period),
            ("Total intereses", round(float(totals.total_interest), 2)),
            ("Total seguros vida", round(float(totals.total_life_insurance), 2)),
            ("Total seguros daños", round(float(totals.total_damage_insurance), 2)),
            ("Monto total a pagar", round(float(totals.total_amount_to_pay), 2)),
            ("Clave RECA", cover.reca_key),
            ("Registro RECA", cover.reca_number),
        ],
        columns=["Concepto", "Valor"],
    )

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Resumen", index=False)
        df_schedule.to_excel(writer, sheet_name="Tabla_Amortizacion", index=False)
    return buffer.getvalue()


def render_amortization_tab(response: SimulationResponse) -> None:
    """Renderiza la tabla de 240 periodos, totales acumulados, conmutador y descargas."""
    import streamlit as st

    totals = response.totals

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Total erogación", format_currency(totals.total_scheduled_payment))
    t2.metric("Total intereses", format_currency(totals.total_interest))
    t3.metric(
        "Total seguros (vida + daños)",
        format_currency(totals.total_life_insurance + totals.total_damage_insurance),
    )
    t4.metric("Monto total a pagar", format_currency(totals.total_amount_to_pay))

    c_info, c_view = st.columns([2, 1])
    with c_info:
        if totals.payoff_period > 0:
            st.success(
                f"Liquidación real estimada: **{totals.payoff_years} años, "
                f"{totals.payoff_months} meses** (Periodo {totals.payoff_period}) | "
                f"CAT oficial: **{format_percent(totals.official_cat, 2)}** | "
                f"CAT real: **{format_percent(totals.real_cat, 2)}**"
            )
        else:
            st.info("Sin saldo por amortizar.")
    with c_view:
        view_mode = st.radio(
            "Vista de tabla",
            options=["Mensual (240 periodos)", "Anual (cierres de año)"],
            horizontal=True,
            key="amortization_view_mode",
        )

    annual_view = view_mode.startswith("Anual")
    df_display = build_schedule_dataframe(response, annual_view=annual_view)

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=460,
    )

    st.subheader("Descargar tabla de amortización")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            label="Descargar CSV",
            data=export_schedule_csv(response),
            file_name="tabla_amortizacion_hipotecaria.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            label="Descargar Excel (.xlsx)",
            data=export_schedule_excel(response),
            file_name="simulacion_hipotecaria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
