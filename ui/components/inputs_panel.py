"""Panel lateral de captura de entradas, restricciones condicionales y presets TC1-TC3."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pandas as pd
import streamlit as st

from engine.models import (
    CalcMode,
    Campaign,
    CommissionType,
    CreditProgram,
    EconomicActivity,
    InsuranceOption,
    LoanTerm,
    PrepayMode,
    ProductScheme,
    SimulationInput,
    normalize_prepayments,
)

DEFAULT_STATE: dict[str, Any] = {
    "quote_date": date(2026, 11, 18),
    "advisor_name": "",
    "branch": "",
    "client_name": "",
    "advisor_phone": "",
    "client_phone": "",
    "program": CreditProgram.ADQUISICION_TRADICIONAL,
    "campaign": Campaign.NINGUNA,
    "calc_mode": CalcMode.POR_VALOR_INMUEBLE,
    "base_value": 3_000_000.0,
    "destructible_value": 2_400_000.0,
    "infonavit_salary": 0.0,
    "economic_activity": EconomicActivity.EMPLEADO,
    "scheme": ProductScheme.VALORA,
    "term": LoanTerm.ANIOS_20,
    "risk_index": 1,
    "commission_type": CommissionType.CONTRATACION_CREDITO,
    "insurance_option": InsuranceOption.SEGUROS_INCLUIDOS,
    "use_manual_opening_comm": False,
    "manual_opening_comm_pct": 1.25,
    "use_custom_requested_loan": False,
    "requested_loan": 0.0,
    "finance_notary_fees": True,
    "use_manual_tax": False,
    "manual_tax_pct": 3.0,
    "use_manual_notary": False,
    "manual_notary_pct": 2.0,
    "ssv_titular": 0.0,
    "infonavit_credit_titular": 0.0,
    "ssv_spouse_cicb": 0.0,
    "ssv_spouse_cofinavit": 0.0,
    "infonavit_credit_spouse": 0.0,
    "exact_infonavit_expenses": 0.0,
    "prepay_mode": PrepayMode.DISMINUCION_PLAZO,
    "prepayments_rows": [],
}


def _apply_preset(values: dict[str, Any]) -> None:
    for key, default_val in DEFAULT_STATE.items():
        st.session_state[key] = values.get(key, default_val)


def _preset_tc1() -> dict[str, Any]:
    return {
        "quote_date": date(2026, 11, 18),
        "client_name": "Escenario TC1 — Adquisición Tradicional",
        "program": CreditProgram.ADQUISICION_TRADICIONAL,
        "campaign": Campaign.NINGUNA,
        "calc_mode": CalcMode.POR_VALOR_INMUEBLE,
        "base_value": 3_000_000.0,
        "destructible_value": 2_400_000.0,
        "economic_activity": EconomicActivity.EMPLEADO,
        "scheme": ProductScheme.VALORA,
        "term": LoanTerm.ANIOS_20,
        "risk_index": 1,
        "commission_type": CommissionType.CONTRATACION_CREDITO,
        "insurance_option": InsuranceOption.SEGUROS_INCLUIDOS,
        "prepay_mode": PrepayMode.DISMINUCION_PLAZO,
        "prepayments_rows": [],
    }


def _preset_tc2() -> dict[str, Any]:
    return {
        "quote_date": date(2026, 11, 18),
        "client_name": "Escenario TC2 — Apoyo Infonavit Green",
        "program": CreditProgram.APOYO_INFONAVIT,
        "campaign": Campaign.HIPOTECA_GREEN,
        "calc_mode": CalcMode.POR_INGRESOS,
        "base_value": 60_000.0,
        "destructible_value": 0.0,
        "infonavit_salary": 45_000.0,
        "economic_activity": EconomicActivity.EMPLEADO,
        "scheme": ProductScheme.PAGOS_OPORTUNOS,
        "term": LoanTerm.ANIOS_15,
        "risk_index": 1,
        "commission_type": CommissionType.CONTRATACION_CREDITO,
        "insurance_option": InsuranceOption.SEGUROS_INCLUIDOS,
        "prepay_mode": PrepayMode.DISMINUCION_PLAZO,
        "prepayments_rows": [{"Periodo": 12, "Monto": 100_000.0}],
    }


def _preset_tc3() -> dict[str, Any]:
    return {
        "quote_date": date(2026, 11, 18),
        "client_name": "Escenario TC3 — Pasivo Hipotecario",
        "program": CreditProgram.PASIVO_HIPOTECARIO,
        "campaign": Campaign.NINGUNA,
        "calc_mode": CalcMode.POR_IMPORTE_CREDITO,
        "base_value": 2_000_000.0,
        "destructible_value": 1_800_000.0,
        "economic_activity": EconomicActivity.INDEPENDIENTE,
        "scheme": ProductScheme.VALORA,
        "term": LoanTerm.ANIOS_10,
        "risk_index": 1,
        "commission_type": CommissionType.PAGO_ANTICIPADO,
        "insurance_option": InsuranceOption.SEGUROS_INCLUIDOS,
        "finance_notary_fees": True,
        "use_manual_tax": True,
        "manual_tax_pct": 2.5,
        "use_manual_notary": True,
        "manual_notary_pct": 1.5,
        "prepay_mode": PrepayMode.DISMINUCION_PAGO,
        "prepayments_rows": [{"Periodo": 6, "Monto": 50_000.0}],
    }


def _preset_clean() -> dict[str, Any]:
    return {
        "quote_date": date.today(),
        "advisor_name": "",
        "branch": "",
        "client_name": "",
        "advisor_phone": "",
        "client_phone": "",
        "program": CreditProgram.ADQUISICION_TRADICIONAL,
        "campaign": Campaign.NINGUNA,
        "calc_mode": CalcMode.POR_INGRESOS,
        "base_value": 0.0,
        "destructible_value": 0.0,
        "infonavit_salary": 0.0,
        "economic_activity": EconomicActivity.EMPLEADO,
        "scheme": ProductScheme.VALORA,
        "term": LoanTerm.ANIOS_20,
        "risk_index": 1,
        "commission_type": CommissionType.CONTRATACION_CREDITO,
        "insurance_option": InsuranceOption.SEGUROS_INCLUIDOS,
        "use_manual_opening_comm": False,
        "use_custom_requested_loan": False,
        "requested_loan": 0.0,
        "finance_notary_fees": True,
        "use_manual_tax": False,
        "manual_tax_pct": 3.0,
        "use_manual_notary": False,
        "manual_notary_pct": 2.0,
        "ssv_titular": 0.0,
        "infonavit_credit_titular": 0.0,
        "ssv_spouse_cicb": 0.0,
        "ssv_spouse_cofinavit": 0.0,
        "infonavit_credit_spouse": 0.0,
        "exact_infonavit_expenses": 0.0,
        "prepay_mode": PrepayMode.DISMINUCION_PLAZO,
        "prepayments_rows": [],
    }


def _init_session_state() -> None:
    for key, val in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _allowed_campaigns(program: CreditProgram) -> list[Campaign]:
    options = [Campaign.NINGUNA, Campaign.WEALTH_MANAGEMENT]
    if program not in (
        CreditProgram.PASIVO_HIPOTECARIO,
        CreditProgram.PASIVO_APOYO_INFONAVIT,
        CreditProgram.LIQUIDEZ_VIVIENDA,
        CreditProgram.CICB_COFINAVIT,
    ):
        options.append(Campaign.HIPOTECA_GREEN)
    if program != CreditProgram.LIQUIDEZ_VIVIENDA:
        options.extend([Campaign.VINCULACION, Campaign.ENGANCHE_ALTO_PASIVO])
    return options


def _allowed_activities(program: CreditProgram) -> list[EconomicActivity]:
    if program == CreditProgram.CICB_COFINAVIT:
        return [EconomicActivity.INDEPENDIENTE]
    if program in (
        CreditProgram.APOYO_INFONAVIT,
        CreditProgram.COFINAVIT,
        CreditProgram.PASIVO_APOYO_INFONAVIT,
    ):
        return [EconomicActivity.EMPLEADO]
    return [EconomicActivity.EMPLEADO, EconomicActivity.INDEPENDIENTE]


def _allowed_terms(scheme: ProductScheme) -> list[LoanTerm]:
    if scheme == ProductScheme.VALORA:
        return [LoanTerm.ANIOS_10, LoanTerm.ANIOS_15, LoanTerm.ANIOS_20]
    return [LoanTerm.ANIOS_7, LoanTerm.ANIOS_10, LoanTerm.ANIOS_15, LoanTerm.ANIOS_20]


def _allowed_commissions(program: CreditProgram) -> list[CommissionType]:
    if program in (
        CreditProgram.APOYO_INFONAVIT,
        CreditProgram.COFINAVIT,
        CreditProgram.PASIVO_APOYO_INFONAVIT,
    ):
        return [CommissionType.CONTRATACION_CREDITO]
    return [CommissionType.CONTRATACION_CREDITO, CommissionType.PAGO_ANTICIPADO]


def render_inputs_sidebar() -> SimulationInput:
    """Renderiza el panel lateral de parámetros y devuelve un ``SimulationInput`` inmutable."""
    _init_session_state()

    with st.sidebar:
        st.subheader("Escenarios rápidos")
        c1, c2, c3 = st.columns(3)
        if c1.button("TC1", use_container_width=True, help="Adquisición Tradicional Valora 20a"):
            _apply_preset(_preset_tc1())
            st.rerun()
        if c2.button("TC2", use_container_width=True, help="Apoyo Infonavit PO 15a Green + Prepago"):
            _apply_preset(_preset_tc2())
            st.rerun()
        if c3.button("TC3", use_container_width=True, help="Pasivo Valora 10a + Gastos Financiados"):
            _apply_preset(_preset_tc3())
            st.rerun()

        if st.button("Limpiar datos", use_container_width=True):
            _apply_preset(_preset_clean())
            st.rerun()

        st.subheader("1. Configuración comercial")
        quote_date = st.date_input("Fecha de cotización", key="quote_date")

        program = st.selectbox(
            "Programa / Tipo de crédito",
            options=list(CreditProgram),
            format_func=lambda p: p.label,
            key="program",
        )

        allowed_camps = _allowed_campaigns(program)
        if st.session_state["campaign"] not in allowed_camps:
            st.session_state["campaign"] = allowed_camps[0]
        campaign = st.selectbox(
            "Campaña comercial",
            options=allowed_camps,
            format_func=lambda c: c.label(program),
            key="campaign",
        )

        scheme = st.selectbox(
            "Producto / Esquema",
            options=list(ProductScheme),
            format_func=lambda s: s.label,
            key="scheme",
        )

        allowed_terms = _allowed_terms(scheme)
        if st.session_state["term"] not in allowed_terms:
            st.session_state["term"] = allowed_terms[-1]
        term = st.selectbox(
            "Plazo del crédito",
            options=allowed_terms,
            format_func=lambda t: t.label,
            key="term",
        )

        allowed_acts = _allowed_activities(program)
        if st.session_state["economic_activity"] not in allowed_acts:
            st.session_state["economic_activity"] = allowed_acts[0]
        economic_activity = st.selectbox(
            "Actividad económica",
            options=allowed_acts,
            format_func=lambda a: a.label,
            key="economic_activity",
        )

        risk_index = st.selectbox(
            "Índice de riesgo (IR)",
            options=[1, 2, 3, 4, 5],
            key="risk_index",
            help="Catálogo activo parametrizado para IR=1; soporta reactivación futura de IR 2..5.",
        )

        allowed_comms = _allowed_commissions(program)
        if st.session_state["commission_type"] not in allowed_comms:
            st.session_state["commission_type"] = allowed_comms[0]
        commission_type = st.selectbox(
            "Tipo de comisión",
            options=allowed_comms,
            format_func=lambda c: c.label,
            key="commission_type",
        )

        insurance_option = st.selectbox(
            "Esquema de seguros",
            options=[InsuranceOption.SEGUROS_INCLUIDOS, InsuranceOption.SEGUROS_EXTERNOS],
            format_func=lambda i: i.label,
            key="insurance_option",
        )

        st.subheader("2. Datos financieros")
        calc_mode = st.selectbox(
            "Modalidad de cálculo",
            options=list(CalcMode),
            format_func=lambda m: m.label,
            key="calc_mode",
        )

        base_labels = {
            CalcMode.POR_VALOR_INMUEBLE: "Valor de la vivienda (MXN)",
            CalcMode.POR_INGRESOS: "Ingreso mensual bruto (MXN)",
            CalcMode.POR_IMPORTE_CREDITO: "Importe de crédito deseado (MXN)",
        }
        base_value = st.number_input(
            base_labels[calc_mode],
            min_value=0.0,
            step=50_000.0 if calc_mode != CalcMode.POR_INGRESOS else 5_000.0,
            format="%.2f",
            key="base_value",
        )

        destructible_value = st.number_input(
            "Valor destructible (opcional, 0 = valor vivienda)",
            min_value=0.0,
            step=50_000.0,
            format="%.2f",
            key="destructible_value",
        )

        infonavit_salary = 0.0
        if program.is_apoyo_infonavit:
            infonavit_salary = st.number_input(
                "Sueldo de cotización mensual (Apoyo Infonavit)",
                min_value=0.0,
                step=1_000.0,
                format="%.2f",
                key="infonavit_salary",
            )

        use_custom_loan = st.checkbox(
            "Especificar crédito solicitado distinto al máximo",
            key="use_custom_requested_loan",
        )
        requested_loan_val = None
        if use_custom_loan:
            custom_loan = st.number_input(
                "Crédito solicitado (MXN)",
                min_value=0.0,
                step=50_000.0,
                format="%.2f",
                key="requested_loan",
            )
            requested_loan_val = Decimal(str(custom_loan))

        finance_notary_fees = True
        if program.is_pasivo:
            finance_notary_fees = st.checkbox(
                "Financiar gastos notariales (hasta 6%)",
                key="finance_notary_fees",
            )

        ssv_titular = Decimal("0")
        infonavit_credit_titular = Decimal("0")
        ssv_spouse_cicb = Decimal("0")
        ssv_spouse_cofinavit = Decimal("0")
        infonavit_credit_spouse = Decimal("0")
        exact_infonavit_expenses = Decimal("0")

        if program.is_cofinavit_family:
            with st.expander("Parámetros Cofinavit / CI+CB", expanded=True):
                ssv_titular = Decimal(
                    str(
                        st.number_input(
                            "SSV Titular / Acreditado (MXN)",
                            min_value=0.0,
                            step=10_000.0,
                            format="%.2f",
                            key="ssv_titular",
                        )
                    )
                )
                if program == CreditProgram.COFINAVIT:
                    infonavit_credit_titular = Decimal(
                        str(
                            st.number_input(
                                "Crédito Infonavit Titular (MXN)",
                                min_value=0.0,
                                step=10_000.0,
                                format="%.2f",
                                key="infonavit_credit_titular",
                            )
                        )
                    )
                    ssv_spouse_cofinavit = Decimal(
                        str(
                            st.number_input(
                                "SSV Cónyuge (Cofinavit, activa RECA conyugal)",
                                min_value=0.0,
                                step=10_000.0,
                                format="%.2f",
                                key="ssv_spouse_cofinavit",
                            )
                        )
                    )
                    infonavit_credit_spouse = Decimal(
                        str(
                            st.number_input(
                                "Crédito Infonavit Cónyuge (MXN)",
                                min_value=0.0,
                                step=10_000.0,
                                format="%.2f",
                                key="infonavit_credit_spouse",
                            )
                        )
                    )
                    exact_infonavit_expenses = Decimal(
                        str(
                            st.number_input(
                                "Gastos exactos Infonavit (opcional)",
                                min_value=0.0,
                                step=1_000.0,
                                format="%.2f",
                                key="exact_infonavit_expenses",
                            )
                        )
                    )
                else:
                    ssv_spouse_cicb = Decimal(
                        str(
                            st.number_input(
                                "SSV Cónyuge (CI+CB, activa RECA conyugal)",
                                min_value=0.0,
                                step=10_000.0,
                                format="%.2f",
                                key="ssv_spouse_cicb",
                            )
                        )
                    )

        with st.expander("Gastos manuales y comisiones (opcional)", expanded=False):
            st.caption("Valores por defecto: 3.0% Impuestos y Derechos + 2.0% Honorarios (5.0% total).")
            use_manual_tax = st.checkbox("Sobrescribir % Impuestos y Derechos", key="use_manual_tax")
            manual_tax_rate = None
            if use_manual_tax:
                tax_pct = st.number_input(
                    "% Impuestos y Derechos",
                    min_value=0.0,
                    max_value=20.0,
                    step=0.1,
                    format="%.2f",
                    key="manual_tax_pct",
                )
                manual_tax_rate = Decimal(str(tax_pct)) / Decimal("100")

            use_manual_notary = st.checkbox("Sobrescribir % Honorarios Notariales", key="use_manual_notary")
            manual_notary_rate = None
            if use_manual_notary:
                notary_pct = st.number_input(
                    "% Honorarios Notariales",
                    min_value=0.0,
                    max_value=20.0,
                    step=0.1,
                    format="%.2f",
                    key="manual_notary_pct",
                )
                manual_notary_rate = Decimal(str(notary_pct)) / Decimal("100")

            use_manual_comm = st.checkbox(
                "Sobrescribir % Comisión por apertura",
                key="use_manual_opening_comm",
            )
            manual_opening_comm_rate = None
            if use_manual_comm:
                comm_pct = st.number_input(
                    "% Comisión por apertura (máx 50%)",
                    min_value=0.0,
                    max_value=50.0,
                    step=0.05,
                    format="%.2f",
                    key="manual_opening_comm_pct",
                )
                manual_opening_comm_rate = Decimal(str(comm_pct)) / Decimal("100")

        with st.expander("Prepagos a capital (240 periodos)", expanded=False):
            prepay_mode = st.selectbox(
                "Modo de aplicación del anticipo",
                options=list(PrepayMode),
                format_func=lambda m: m.label,
                key="prepay_mode",
            )
            df_prep = pd.DataFrame(
                st.session_state["prepayments_rows"]
                if st.session_state["prepayments_rows"]
                else [{"Periodo": 12, "Monto": 0.0}]
            )
            edited_prep = st.data_editor(
                df_prep,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Periodo": st.column_config.NumberColumn(
                        "Mes (1-240)", min_value=1, max_value=240, step=1
                    ),
                    "Monto": st.column_config.NumberColumn(
                        "Prepago (MXN)", min_value=0.0, step=10_000.0, format="%.2f"
                    ),
                },
                key="prepayments_editor",
            )
            prepayments_map: dict[int, Decimal] = {}
            for _, row in edited_prep.iterrows():
                if pd.notna(row.get("Periodo")) and pd.notna(row.get("Monto")):
                    p_int = int(row["Periodo"])
                    amt = Decimal(str(row["Monto"]))
                    if 1 <= p_int <= 240 and amt > Decimal("0"):
                        prepayments_map[p_int] = prepayments_map.get(p_int, Decimal("0")) + amt

        with st.expander("Datos informativos del cliente y ejecutivo", expanded=False):
            client_name = st.text_input("Nombre del cliente", key="client_name")
            client_phone = st.text_input("Teléfono del cliente", key="client_phone")
            advisor_name = st.text_input("Nombre del ejecutivo / bróker", key="advisor_name")
            advisor_phone = st.text_input("Teléfono del ejecutivo", key="advisor_phone")
            branch = st.text_input("Sucursal / Oficina", key="branch")

    return SimulationInput(
        quote_date=quote_date,
        advisor_name=advisor_name,
        branch=branch,
        client_name=client_name,
        advisor_phone=advisor_phone,
        client_phone=client_phone,
        program=program,
        campaign=campaign,
        calc_mode=calc_mode,
        base_value=Decimal(str(base_value)),
        destructible_value=(
            Decimal(str(destructible_value)) if destructible_value > 0 else None
        ),
        infonavit_salary=Decimal(str(infonavit_salary)),
        economic_activity=economic_activity,
        scheme=scheme,
        term=term,
        risk_index=int(risk_index),
        commission_type=commission_type,
        insurance_option=insurance_option,
        manual_opening_commission_rate=manual_opening_comm_rate,
        requested_loan=requested_loan_val,
        finance_notary_fees=finance_notary_fees,
        manual_tax_rate=manual_tax_rate,
        manual_notary_rate=manual_notary_rate,
        ssv_titular=ssv_titular,
        infonavit_credit_titular=infonavit_credit_titular,
        ssv_spouse_cicb=ssv_spouse_cicb,
        ssv_spouse_cofinavit=ssv_spouse_cofinavit,
        infonavit_credit_spouse=infonavit_credit_spouse,
        exact_infonavit_expenses=exact_infonavit_expenses,
        prepay_mode=prepay_mode,
        prepayments=normalize_prepayments(prepayments_map),
    )
