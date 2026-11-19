"""Pestaña 3: Carátula de Crédito regulatoria CONDUSEF y registro RECA."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from engine.models import SimulationResponse
from ui.branding import BRAND
from ui.theme import format_cat, format_currency, format_percent


def render_cover_tab(response: SimulationResponse) -> None:
    """Renderiza la Carátula CONDUSEF estructurada, comisiones, penalización y RECA."""
    cover = response.contract_cover

    st.markdown(
        f"""
        <div class="cover-box">
            <strong>{BRAND.institution_name}</strong><br/>
            <span><strong>Carátula de Crédito Hipotecario</strong></span><br/>
            <span>Nombre del cliente: <strong>{cover.client_name}</strong></span><br/>
            <span>Producto comercial: <strong>{cover.commercial_product_name}</strong></span><br/>
            <span>Moneda: {cover.currency_label} &nbsp;|&nbsp; Plazo: {cover.term_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Cuadro regulatorio CONDUSEF")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("CAT (sin IVA)", format_cat(cover.official_cat))
    r2.metric("Tasa de interés anual", format_percent(cover.initial_rate, 2))
    r3.metric("Monto del crédito", format_currency(cover.loan_amount))
    r4.metric("Monto total a pagar", format_currency(cover.total_amount_to_pay))

    st.caption(BRAND.condusef_note)

    st.subheader("Comisiones y penalizaciones aplicables")
    comm_table = pd.DataFrame(
        [
            ("Comisión por apertura", cover.opening_commission_text),
            ("Penalización por pago tardío", cover.late_payment_penalty_text),
            ("Comisión por pago anticipado", cover.prepayment_commission_text),
        ],
        columns=["Concepto regulatorio", "Condición aplicable"],
    )
    st.dataframe(comm_table, use_container_width=True, hide_index=True)

    st.subheader("Registro de Contratos de Adhesión (RECA)")
    reca_table = pd.DataFrame(
        [
            ("Clave compuesta RECA", cover.reca_key),
            ("Número de registro RECA", cover.reca_number or "Sin captura de valor base"),
            ("Denominación del contrato", cover.reca_contract_name or "—"),
            ("Fecha de expedición", cover.reca_expedition_date or "—"),
        ],
        columns=["Campo RECA", "Detalle"],
    )
    st.dataframe(reca_table, use_container_width=True, hide_index=True)
