"""Punto de entrada ligero de la aplicación Streamlit (Simulador Hipotecario marca blanca)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from engine import run_simulation
from ui.branding import BRAND
from ui.components.amortization_tab import render_amortization_tab
from ui.components.cover_tab import render_cover_tab
from ui.components.inputs_panel import render_inputs_sidebar
from ui.components.summary_tab import render_summary_tab
from ui.theme import CUSTOM_CSS


def _render_brand_header() -> None:
    if BRAND.logo_path and Path(BRAND.logo_path).is_file():
        col_logo, col_title = st.columns([1, 5])
        with col_logo:
            st.image(BRAND.logo_path, use_container_width=True)
        with col_title:
            st.title(BRAND.app_title)
            st.caption(f"{BRAND.institution_name} — {BRAND.app_subtitle}")
    else:
        st.markdown(
            f"""
            <div class="brand-header">
                <div class="brand-logo-placeholder">{BRAND.logo_placeholder_text}</div>
                <h2 style="margin: 0.15rem 0 0.25rem 0;">{BRAND.app_title}</h2>
                <div style="color: #4A5568; font-size: 0.92rem;">
                    <strong>{BRAND.institution_name}</strong> — {BRAND.app_subtitle}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title=BRAND.app_title,
        page_icon=BRAND.page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    _render_brand_header()
    sim_input = render_inputs_sidebar()

    try:
        response = run_simulation(sim_input)
    except ValueError as exc:
        st.error(f"Parámetros inválidos: {exc}")
        return

    tab_summary, tab_schedule, tab_cover = st.tabs(
        ["Simulador", "Tabla de Amortización", "Carátula CONDUSEF"]
    )
    with tab_summary:
        render_summary_tab(response)
    with tab_schedule:
        render_amortization_tab(response)
    with tab_cover:
        render_cover_tab(response)

    st.markdown(
        f'<div class="footer-note">{BRAND.footer_disclaimer}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
