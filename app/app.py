import os

import pandas as pd
import streamlit as st
from scipy import stats

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Áreas Verdes y Hurtos – RM 2023",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# ESTILOS CSS (consistentes con todas las páginas)
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        html, body, [class*="css"] { font-family: "Source Sans Pro", "Segoe UI", sans-serif; }
        h1, h2 { color: #2c5f2e !important; }
        h3 { color: #4a7c59 !important; }
        div[data-testid="stMetric"] {
            background-color: #f4f9f4;
            border: 1px solid #d8e8d9;
            border-radius: 10px;
            padding: 0.8rem 1rem;
        }
        div[data-testid="stMetricLabel"] p { color: #2c5f2e; font-weight: 600; }
        .tarjeta {
            border-radius: 10px;
            padding: 1rem 1.2rem;
            min-height: 175px;
            border: 1px solid #d8e8d9;
        }
        .tarjeta h4 { margin: 0 0 0.4rem 0; font-size: 1.05rem; }
        .tarjeta .valor { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.4rem; }
        .tarjeta p { font-size: 0.92rem; color: #3d3d3d; margin: 0; }
        .tarjeta-y { background: #fdf2f1; border-left: 6px solid #c0392b; }
        .tarjeta-y h4, .tarjeta-y .valor { color: #c0392b; }
        .tarjeta-x { background: #eef8f1; border-left: 6px solid #27ae60; }
        .tarjeta-x h4, .tarjeta-x .valor { color: #1e8449; }
        .tarjeta-t { background: #f4f5f6; border-left: 6px solid #7f8c8d; }
        .tarjeta-t h4, .tarjeta-t .valor { color: #5d6d6e; }
        .fuente { background: #f4f9f4; border: 1px solid #d8e8d9; border-radius: 10px;
                  padding: 1rem 1.2rem; min-height: 165px; }
        .fuente h4 { color: #2c5f2e; margin: 0 0 0.4rem 0; font-size: 1.02rem; }
        .fuente p { font-size: 0.92rem; color: #3d3d3d; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_num(valor, decimales=0):
    """Formato numérico chileno: punto como separador de miles y coma decimal."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data
def load_data():
    """Busca el dataset comunal procesado en rutas relativas y absolutas."""
    base = os.path.dirname(os.path.abspath(__file__))
    rutas = [
        "data/processed/rm_comunas_2023.csv",
        "../data/processed/rm_comunas_2023.csv",
        "../../data/processed/rm_comunas_2023.csv",
        os.path.normpath(os.path.join(base, "..", "data", "processed", "rm_comunas_2023.csv")),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            return pd.read_csv(ruta)
    return None


df = load_data()

# ─────────────────────────────────────────────────────────────
# 1. ENCABEZADO
# ─────────────────────────────────────────────────────────────
st.title("🌿 Áreas Verdes y Delincuencia en la Región Metropolitana")
st.subheader("¿Más verde significa menos hurtos?")

# ─────────────────────────────────────────────────────────────
# 2. CONTEXTO DEL AVANCE 1
# ─────────────────────────────────────────────────────────────
st.info(
    "**Pregunta de investigación (Avance 1):** ¿Existe correlación entre los metros cuadrados de áreas verdes "
    "y la tasa de hurtos en las comunas de la Región Metropolitana durante el año 2023?"
)
st.markdown(
    "El diseño urbano y la distribución de los espacios públicos influyen en la calidad de vida de las ciudades. "
    "En el marco de las *Smart Cities* existe un debate abierto: ¿una mayor superficie de áreas verdes fomenta la "
    "cohesión social y disuade la delincuencia, o genera zonas de vulnerabilidad? Esta aplicación explora esa "
    "relación con datos oficiales de 2023."
)

# ─────────────────────────────────────────────────────────────
# 3. VARIABLES DEL PROYECTO
# ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="tarjeta tarjeta-y">
            <h4>📍 Variable Objetivo (Y)</h4>
            <div class="valor">Tasa de hurtos por 100.000 habitantes</div>
            <p>Casos policiales de <em>hurtos</em> (sustracción sin violencia) registrados por el CEAD en 2023,
            normalizados por la población residente de cada comuna.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        <div class="tarjeta tarjeta-x">
            <h4>🌳 Variable Explicativa (X)</h4>
            <div class="valor">m² de áreas verdes por habitante</div>
            <p>Superficie de plazas y parques del catastro MINVU-INE dividida por la población comunal,
            comparable con el estándar de referencia de 9 m²/hab.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
        <div class="tarjeta tarjeta-t">
            <h4>📅 Contexto (T)</h4>
            <div class="valor">Año 2023 — 52 comunas de la RM</div>
            <p>Periodo anual consolidado (enero–diciembre 2023). La dimensión contextual clave es la
            distribución espacial entre comunas y sectores de la región.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ─────────────────────────────────────────────────────────────
# 5. MÉTRICAS CLAVE
# ─────────────────────────────────────────────────────────────
st.header("📊 Cifras Clave del Proyecto")
if df is None:
    st.warning("⚠️ No se encontró `data/processed/rm_comunas_2023.csv`. Ejecuta `python scripts/build_dataset.py`.")
else:
    df_xy = df.dropna(subset=["area_verde_m2_hab", "tasa_hurtos_100k"])
    r, p = stats.pearsonr(df_xy["area_verde_m2_hab"], df_xy["tasa_hurtos_100k"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Comunas analizadas", len(df))
    m2.metric("Con catastro MINVU", int(df["tiene_catastro_minvu"].sum()),
              help=f"{len(df) - int(df['tiene_catastro_minvu'].sum())} comunas no tienen catastro de áreas verdes.")
    m3.metric("Total hurtos 2023", fmt_num(df["hurtos_total"].sum()))
    m4.metric("Correlación AV↔Hurtos", f"r = {fmt_num(r, 3)}",
              help=f"Coeficiente de Pearson entre m²/hab y tasa de hurtos (n = {len(df_xy)}, p = {fmt_num(p, 3)}).")
    st.caption(
        f"La correlación es positiva y moderada (r = {fmt_num(r, 3)}): a primera vista, las comunas con más área verde "
        "registran más hurtos. Las páginas de análisis muestran por qué este resultado no implica causalidad."
    )

st.divider()

# ─────────────────────────────────────────────────────────────
# 7. FUENTES DE DATOS
# ─────────────────────────────────────────────────────────────
st.header("🗃️ Fuentes de Datos")
f1, f2, f3 = st.columns(3)
fuentes = [
    (f1, "🚨 CEAD – Subsecretaría de Prevención del Delito",
     "Casos policiales mensuales de <strong>hurtos</strong> por comuna. Se filtra el año 2023 y la Región "
     "Metropolitana para construir la variable Y."),
    (f2, "🌳 MINVU / INE – Catastro de Áreas Verdes",
     "Polígonos de plazas y parques urbanos con su superficie. Se agregan por comuna para obtener los m² de "
     "áreas verdes (variable X)."),
    (f3, "👥 SAE – Ministerio de Desarrollo Social",
     "Población proyectada y porcentaje de pobreza por ingresos por comuna. Permite normalizar X e Y y "
     "aporta contexto socioeconómico."),
]
for col, titulo, desc in fuentes:
    with col:
        st.markdown(f'<div class="fuente"><h4>{titulo}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────────────────────
# 9. GUÍA DE NAVEGACIÓN
# ─────────────────────────────────────────────────────────────
st.header("🧭 Guía de Navegación")
st.markdown(
    """
Usa el menú lateral (flecha **›** arriba a la izquierda) para recorrer la aplicación:

| Página | Propósito |
|---|---|
| 📋 **Contexto y Datos** | Continuidad con el Avance 1, estructura del dataset, calidad de los datos y decisiones de limpieza. |
| 🔬 **Análisis EDA** | Distribuciones de X e Y (análisis univariado), comparación por sector y relaciones bivariadas. |
| 🔍 **Análisis de la Pregunta** | Correlación X–Y con filtros interactivos, mapa espacial de la RM y hallazgos preliminares. |
"""
)
st.success("💡 Recomendación: recorre las páginas en orden para seguir el hilo desde los datos hasta la respuesta a la pregunta.")

# ─────────────────────────────────────────────────────────────
# 10. PIE DE PÁGINA
# ─────────────────────────────────────────────────────────────
st.divider()
st.caption("EIN092B Visualización | Avance 2 – 2026-II | Integrantes: Vicente Paredes, Tomás Armijo, Francisca Matamala")
