# Simulador Hipotecario (Marca Blanca — Python 3.11+ / Streamlit)

Aplicación modular de cotización hipotecaria en pesos mexicanos (MXN) construida con **desacoplamiento total entre el motor financiero (`engine/`) y la capa visual (`ui/`)**.

## Características principales

- **Motor financiero puro (`engine/`)**: 100 % Python estándar con `decimal.Decimal` (`prec=34`, sin redondeos intermedios) y `datetime.date`. Cero dependencias de Streamlit.
- **Siete programas comerciales y dos esquemas**: Adquisición Tradicional, Apoyo Infonavit, Cofinavit, Pasivo Hipotecario, Pasivo con Apoyo Infonavit, Liquidez Vivienda y CI+CB Cofinavit, bajo esquemas **Valora** y **Pagos Oportunos**.
- **Tabla de amortización a 240 periodos**: calendario Actual/360 (corte día 3 o 17), corrida base contractual para CAT oficial (Newton-Raphson con tolerancia `1e-12`), prepagos con disminución de plazo o de pago, aportaciones bimestrales patronales y descarga en **CSV** y **Excel (`.xlsx`)**.
- **Carátula CONDUSEF y RECA**: ensamble automático de clave compuesta RECA, comisiones aplicables y excepción de penalización de `$350.00 + IVA` para clave `7-2-2`.

## Estructura del proyecto

```text
simulador_hipotecario/
├── .streamlit/
│   └── config.toml            # Tema base de Streamlit (colores y fuente)
├── engine/                    # Motor financiero puro (sin imports de Streamlit)
│   ├── models.py              # Enums y dataclasses inmutables (@dataclass(frozen=True))
│   ├── catalog_repository.py  # Catálogos aislados: programas, LTV, pricing, avalúos, UMA 2026 y RECA
│   ├── pricing_resolver.py    # Campaña efectiva, tasas, PPM, incremento anual, piso y LTV
│   ├── loan_sizing.py         # Crédito máximo, Cofinavit/CI+CB, gastos financiados, originación e inversión
│   ├── amortization_engine.py # Fechas de corte Actual/360, corrida base/principal y TIR/CAT
│   ├── contract_cover.py      # Clave RECA y Carátula CONDUSEF
│   └── simulator.py           # Orquestador DAG del cálculo completo
├── ui/                        # Capa visual modular
│   ├── branding.py            # Textos de marca, institución, logotipo y avisos legales
│   ├── theme.py               # Paleta de colores (UI + Plotly), formateadores y CSS mínimo
│   └── components/
│       ├── inputs_panel.py    # Panel lateral con restricciones condicionales, prepagos y presets TC1-TC3
│       ├── summary_tab.py     # Pestaña 1: KPIs, gastos, alertas y gráficas
│       ├── amortization_tab.py# Pestaña 2: 240 periodos, vista mensual/anual y descarga CSV/XLSX
│       ├── cover_tab.py       # Pestaña 3: Carátula regulatoria CONDUSEF y RECA
│       └── charts.py          # Gráficas interactivas con Plotly
├── tests/
│   ├── test_simulator.py      # Pruebas unitarias TC1, TC2, TC3 y reglas de validación
│   └── test_exports_and_app.py# Pruebas de exportación CSV/XLSX y carga de app.py con AppTest
├── app.py                     # Punto de entrada ligero de Streamlit
├── requirements.txt
└── README.md
```

## Instalación y ejecución

1. Crea y activa un entorno virtual en Python 3.11+:

```bash
python3 -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```bash
streamlit run app.py
```

4. Ejecuta las pruebas unitarias:

```bash
pytest -v
```

## Cómo personalizar la marca y mejorar el diseño

La arquitectura está preparada para iterar la identidad y el aspecto visual **sin tocar la lógica financiera** de `engine/`:

1. **Nombre de la institución, títulos, logotipo y avisos al pie → `ui/branding.py`**
   - Edita la instancia `BRAND` (`app_title`, `app_subtitle`, `institution_name`, `footer_disclaimer`, `condusef_note`).
   - Para mostrar un logotipo real, coloca tu archivo en `assets/logo.png` y asigna `logo_path="assets/logo.png"`.

2. **Colores de la app, tipografía base y tema Streamlit → `.streamlit/config.toml` y `ui/theme.py`**
   - Ajusta `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor` y `font` en `.streamlit/config.toml`.
   - Edita el diccionario `PALETTE` en `ui/theme.py` para actualizar simultáneamente los acentos de CSS y todas las series de color de las gráficas Plotly.
   - Modifica el bloque `CUSTOM_CSS` en `ui/theme.py` si deseas ajustar bordes, tarjetas o espaciados.

3. **Rediseño independiente por sección → `ui/components/`**
   - `ui/components/inputs_panel.py`: formulario lateral, presets y editor de prepagos.
   - `ui/components/summary_tab.py`: distribución de KPIs, tablas de gastos y alertas.
   - `ui/components/charts.py`: estilos, tipos y títulos de gráficas Plotly.
   - `ui/components/amortization_tab.py`: columnas visibles, formato de tabla y botones de exportación.
   - `ui/components/cover_tab.py`: presentación visual de la Carátula CONDUSEF.

4. **Catálogos comerciales y registros RECA propios → `engine/catalog_repository.py`**
   - Cuando necesites sustituir tasas, pagos por millar, matriz LTV, tramos de avalúo, UMA o claves RECA por los de tu institución, actualiza únicamente `engine/catalog_repository.py`.
