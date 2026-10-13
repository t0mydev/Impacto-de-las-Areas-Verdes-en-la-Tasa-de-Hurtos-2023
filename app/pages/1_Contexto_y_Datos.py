import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Contexto y Datos | Áreas Verdes RM",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        h1, h2 { color: #2c5f2e !important; }
        h2 { border-bottom: 2px solid #d8e8d9; padding-bottom: 0.3rem; }
        h3 { color: #4a7c59 !important; }
        div[data-testid="stMetric"] {
            background-color: #f4f9f4;
            border: 1px solid #d8e8d9;
            border-radius: 10px;
            padding: 0.8rem 1rem;
        }
        div[data-testid="stMetricLabel"] p { color: #2c5f2e; font-weight: 600; }
        .tarjeta { background: #f4f9f4; border: 1px solid #d8e8d9; border-left: 6px solid #2c5f2e;
                   border-radius: 10px; padding: 1rem 1.2rem; min-height: 150px; }
        .tarjeta h4 { color: #2c5f2e; margin: 0 0 0.5rem 0; }
        .tarjeta p { margin: 0; color: #333333; }
        .tarjeta-pregunta { border-left-color: #c0392b; background: #fdf6f5; }
        .tarjeta-pregunta h4 { color: #c0392b; }
    </style>
    """,
    unsafe_allow_html=True,
)

_ST_VERSION = tuple(int(x) for x in st.__version__.split(".")[:2])
ANCHO_COMPLETO = {"width": "stretch"} if _ST_VERSION >= (1, 46) else {"use_container_width": True}
COLOR_Y, COLOR_X, COLOR_CTX = "#c0392b", "#27ae60", "#7f8c8d"


def fmt_num(valor, decimales=0):
    """Formato numérico chileno: punto como separador de miles y coma decimal."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def scatter_mapa(**kwargs):
    """Usa px.scatter_map (Plotly ≥ 5.24) si existe; si no, px.scatter_mapbox."""
    if hasattr(px, "scatter_map"):
        kwargs["map_style"] = kwargs.pop("mapbox_style", "open-street-map")
        return px.scatter_map(**kwargs)
    return px.scatter_mapbox(**kwargs)


@st.cache_data
def load_data():
    """Busca rm_comunas_2023.csv en rutas relativas y absolutas."""
    base = os.path.dirname(os.path.abspath(__file__))
    rutas = [
        "data/processed/rm_comunas_2023.csv",
        "../data/processed/rm_comunas_2023.csv",
        "../../data/processed/rm_comunas_2023.csv",
        os.path.normpath(os.path.join(base, "..", "..", "data", "processed", "rm_comunas_2023.csv")),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            return pd.read_csv(ruta)
    return None


df = load_data()
if df is None:
    st.error("No se encontró `data/processed/rm_comunas_2023.csv`. Ejecuta `python scripts/build_dataset.py`.")
    st.stop()

n_total = len(df)
n_cat = int(df["tiene_catastro_minvu"].sum())
n_sin = n_total - n_cat

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Opciones de Visualización")
    filtro_tabla = st.radio("Mostrar tabla de comunas",
                            [f"Todas ({n_total})", f"Con catastro MINVU ({n_cat})", f"Sin catastro ({n_sin})"])
    orden = st.radio("Ordenar por", ["Tasa de Hurtos ↓", "Área Verde ↓", "Población ↓", "Nombre A-Z"])
    destacar = st.checkbox("Destacar comunas sin catastro", value=True)
    st.divider()
    st.markdown("*Datos: 2023 – Región Metropolitana*")

st.title("📋 Contexto y Datos")
st.markdown("Esta página documenta **de dónde vienen los datos, cómo se prepararon y qué tan confiables son** "
            "antes de pasar al análisis exploratorio.")

# ═════════════════════════════════════════════════════════════
# CONTINUIDAD CON EL AVANCE 1
# ═════════════════════════════════════════════════════════════
st.header("📌 Continuidad con el Avance 1")
c_izq, c_der = st.columns(2)
with c_izq:
    st.markdown(
        """<div class="tarjeta"><h4>🏙️ Problemática</h4><p>El diseño urbano y la distribución de los espacios
        públicos impactan directamente en la calidad de vida. En el marco de las <em>Smart Cities</em> se debate si
        una mayor superficie de áreas verdes fomenta la cohesión social —actuando como disuasivo de la
        delincuencia— o si, por el contrario, genera zonas de vulnerabilidad.</p></div>""",
        unsafe_allow_html=True,
    )
with c_der:
    st.markdown(
        """<div class="tarjeta tarjeta-pregunta"><h4>❓ Pregunta de investigación</h4><p><strong>¿Existe
        correlación entre los metros cuadrados de áreas verdes y la tasa de hurtos en las comunas de la Región
        Metropolitana durante el año 2023?</strong></p></div>""",
        unsafe_allow_html=True,
    )

st.write("")
a1, a2, a3 = st.columns(3)
a1.metric("Alcance temporal T", "Año 2023", "Datos anuales consolidados", delta_color="off")
a2.metric("Alcance territorial", f"{n_total} comunas", "Región Metropolitana", delta_color="off")
a3.metric("Tipo de delito", "Hurtos en general", "Sustracción sin violencia", delta_color="off")

st.divider()

# ═════════════════════════════════════════════════════════════
# DESCRIPCIÓN DEL DATASET
# ═════════════════════════════════════════════════════════════
st.header("📊 Descripción del Dataset")
st.markdown("El dataset final integra **tres fuentes oficiales** unidas por el código único territorial (CUT).")
d1, d2, d3 = st.columns(3)
with d1:
    st.markdown("#### 🌳 MINVU / INE")
    st.metric("Registros crudos", fmt_num(18173), "Espacios públicos (nacional)", delta_color="off")
    st.markdown("Catastro de **plazas y parques urbanos** con su superficie (`Shape_Area`). Se filtra la RM "
                "(CUT que inicia con 13) y se agrega por comuna → **m² de áreas verdes**.")
with d2:
    st.markdown("#### 🚨 CEAD")
    st.metric("Registros crudos", fmt_num(1987200), "Comuna × mes × delito (2010–2025)", delta_color="off")
    st.markdown("Casos policiales de la Subsecretaría de Prevención del Delito. Se filtra **2023**, "
                "**Región Metropolitana** y delito **Hurtos** → total anual y serie mensual.")
with d3:
    st.markdown("#### 👥 SAE – Desarrollo Social")
    st.metric("Registros crudos", fmt_num(352), "Comunas de Chile", delta_color="off")
    st.markdown("Estimación de pobreza para áreas pequeñas: **población proyectada** y **% de pobreza por "
                "ingresos**. Se usan las 52 comunas de la RM para normalizar y contextualizar.")

st.divider()

# ═════════════════════════════════════════════════════════════
# ESTRUCTURA DEL DATASET CONSOLIDADO
# ═════════════════════════════════════════════════════════════
st.header("🗂️ Estructura del Dataset Consolidado")
e1, e2, e3 = st.columns(3)
e1.metric("Observaciones", f"{n_total} comunas", "Unidad: comuna", delta_color="off")
e2.metric("Variables", df.shape[1],
          f"{df.select_dtypes('number').shape[1]} numéricas · {df.shape[1] - df.select_dtypes('number').shape[1]} "
          "categóricas/lógicas", delta_color="off")
e3.metric("Comunas con catastro", n_cat, f"{n_sin} sin catastro MINVU", delta_color="off")

tabla = df.copy()
if filtro_tabla.startswith("Con catastro"):
    tabla = tabla[tabla["tiene_catastro_minvu"]]
elif filtro_tabla.startswith("Sin catastro"):
    tabla = tabla[~tabla["tiene_catastro_minvu"]]

orden_cols = {
    "Tasa de Hurtos ↓": ("tasa_hurtos_100k", False),
    "Área Verde ↓": ("area_verde_m2_hab", False),
    "Población ↓": ("poblacion", False),
    "Nombre A-Z": ("comuna", True),
}
col_orden, asc = orden_cols[orden]
tabla = tabla.sort_values(col_orden, ascending=asc, na_position="last")

columnas = ["comuna", "sector", "clasificacion_zona", "poblacion", "area_verde_m2_hab", "tasa_hurtos_100k",
            "pct_pobreza", "tiene_catastro_minvu"]
tabla = tabla[columnas].copy()
mostrar_todas = filtro_tabla.startswith("Todas")
if destacar and mostrar_todas:
    tabla.insert(0, "estado", np.where(tabla["tiene_catastro_minvu"], "✅", "⚠️ Sin catastro"))

config = {
    "estado": st.column_config.TextColumn("Estado"),
    "comuna": st.column_config.TextColumn("Comuna"),
    "sector": st.column_config.TextColumn("Sector"),
    "clasificacion_zona": st.column_config.TextColumn("Zona"),
    "poblacion": st.column_config.NumberColumn("Población", format="localized"),
    "area_verde_m2_hab": st.column_config.NumberColumn("Área verde (m²/hab)", format="%.2f"),
    "tasa_hurtos_100k": st.column_config.NumberColumn("Tasa hurtos (100k hab.)", format="%.1f"),
    "pct_pobreza": st.column_config.NumberColumn("Pobreza (%)", format="%.1f%%"),
    "tiene_catastro_minvu": st.column_config.CheckboxColumn("Catastro MINVU"),
}
if destacar and mostrar_todas:
    estilo = tabla.style.apply(
        lambda fila: ["background-color: #fff4e5" if not fila["tiene_catastro_minvu"] else "" for _ in fila], axis=1)
    st.dataframe(estilo, hide_index=True, column_config=config, height=420, **ANCHO_COMPLETO)
    st.caption(f"🟧 Las filas resaltadas corresponden a las {n_sin} comunas sin catastro MINVU: su área verde "
               "queda vacía (NaN) y no se usan en el análisis bivariado.")
else:
    st.dataframe(tabla, hide_index=True, column_config=config, height=420, **ANCHO_COMPLETO)
st.caption(f"Mostrando {len(tabla)} comunas · ordenadas por {orden.replace(' ↓', ' (descendente)')}.")

with st.expander("📖 Diccionario de variables e interpretación", expanded=True):
    st.markdown(
        """
| Variable | Tipo | Descripción |
|---|---|---|
| `comuna` | Nominal | Nombre de la comuna (unidad de observación). |
| `sector` | Categórica | Sector geográfico de la RM (Centro, Norte, Oriente, Poniente, Sur). |
| `clasificacion_zona` | Ordinal | Grado de urbanización: Urbano denso, Urbano, Periurbano, Rural. |
| `poblacion` | Numérica discreta | Población proyectada (SAE). Denominador de los indicadores. |
| `area_verde_m2_hab` | Numérica continua | **X**: m² de áreas verdes catastradas por habitante. |
| `tasa_hurtos_100k` | Numérica continua | **Y**: hurtos 2023 por cada 100.000 habitantes. |
| `pct_pobreza` | Numérica continua | % de personas en pobreza por ingresos (contexto socioeconómico). |
| `tiene_catastro_minvu` | Binaria | Indica si la comuna está cubierta por el catastro MINVU. |

**¿Por qué m²/hab y no m² totales?** Los m² totales favorecen a las comunas más grandes y pobladas: Maipú o
Puente Alto suman mucha superficie, pero la reparten entre más de 580.000 habitantes. Dividir por la población
mide la **disponibilidad real de área verde por persona**, la hace comparable con el estándar de referencia de
9 m²/hab y la pone en la misma escala que la variable Y, que también está normalizada (por 100.000 habitantes).
"""
    )

st.divider()

# ═════════════════════════════════════════════════════════════
# CALIDAD DE LOS DATOS
# ═════════════════════════════════════════════════════════════
st.header("🔍 Calidad de los Datos")

# ── 1. Valores faltantes ─────────────────────────────────────
with st.expander("1. Valores Faltantes", expanded=True):
    motivos_av = "8 comunas sin catastro MINVU (zonas rurales no catastradas)"
    motivos = {
        "area_verde_total_ha": motivos_av, "area_verde_m2_hab": motivos_av,
        "cantidad_plazas": motivos_av, "cantidad_parques": motivos_av,
    }
    faltantes = pd.DataFrame({
        "columna": df.columns,
        "valores_faltantes": df.isnull().sum().values,
        "porcentaje": (df.isnull().mean() * 100).round(1).values,
    })
    faltantes["motivo"] = faltantes.apply(
        lambda f: motivos.get(f["columna"], "Sin faltantes") if f["valores_faltantes"] > 0 else "Sin faltantes",
        axis=1)
    col_t, col_g = st.columns([1.2, 1])
    with col_t:
        st.dataframe(faltantes, hide_index=True, height=420, column_config={
            "columna": "Columna", "valores_faltantes": "Valores faltantes",
            "porcentaje": st.column_config.NumberColumn("% faltante", format="%.1f%%"), "motivo": "Motivo",
        }, **ANCHO_COMPLETO)
    con_faltantes = faltantes[faltantes["valores_faltantes"] > 0].sort_values("porcentaje")
    with col_g:
        if not con_faltantes.empty:
            fig, ax = plt.subplots(figsize=(6, 3.6))
            barras = ax.barh(con_faltantes["columna"], con_faltantes["porcentaje"], color=COLOR_CTX)
            for b, v, n in zip(barras, con_faltantes["porcentaje"], con_faltantes["valores_faltantes"]):
                ax.text(b.get_width() + 0.5, b.get_y() + b.get_height() / 2, f"{fmt_num(v, 1)}% ({n})",
                        va="center", fontsize=9)
            ax.set_xlim(0, max(30, con_faltantes["porcentaje"].max() * 1.4))
            ax.set_xlabel("% de comunas sin dato")
            ax.set_title("Variables con valores faltantes", color="#2c5f2e")
            ax.spines[["top", "right"]].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        sin_lista = ", ".join(df.loc[~df["tiene_catastro_minvu"], "comuna"])
        st.info(f"Los faltantes se concentran **solo** en las variables de áreas verdes ({fmt_num(n_sin / n_total * 100, 1)}%"
                f" de las comunas): {sin_lista}. Y, población y pobreza están completas.")

# ── 2. Decisiones de limpieza ────────────────────────────────
with st.expander("2. Decisiones de Limpieza y Preparación", expanded=True):
    st.markdown(
        """
| Decisión | Justificación |
|---|---|
| NaN (no 0) para áreas verdes sin catastro | Ausencia de catastro ≠ ausencia de áreas verdes |
| Normalización por población | Elimina el sesgo de comunas más grandes |
| Filtro 2023 + RM + Hurtos | Acota al horizonte temporal T, alcance territorial y tipo de delito Y |
"""
    )
    st.caption("Además, se verificó que no existen registros duplicados por comuna (clave CUT única) y que las 52 "
               "comunas tienen dato de hurtos. Detalle en `notebooks/estructura_y_calidad_datos.ipynb`.")

# ── 3. Outliers ──────────────────────────────────────────────
def outliers_iqr(serie):
    q1, q3 = serie.quantile([0.25, 0.75])
    lim = q3 + 1.5 * (q3 - q1)
    return serie[serie > lim], lim


with st.expander("3. Valores Atípicos (Outliers)", expanded=True):
    o_y, lim_y = outliers_iqr(df["tasa_hurtos_100k"])
    o_x, lim_x = outliers_iqr(df["area_verde_m2_hab"].dropna())
    oy, ox = st.columns(2)
    with oy:
        st.markdown(f"##### 🚨 Y – Tasa de hurtos ({len(o_y)} outliers)")
        st.caption(f"Regla IQR: valores > Q3 + 1,5·IQR = {fmt_num(lim_y, 1)} hurtos por 100k hab.")
        t_y = df.loc[o_y.index, ["comuna", "sector", "tasa_hurtos_100k", "hurtos_total"]].sort_values(
            "tasa_hurtos_100k", ascending=False)
        st.dataframe(t_y, hide_index=True, column_config={
            "comuna": "Comuna", "sector": "Sector",
            "tasa_hurtos_100k": st.column_config.NumberColumn("Tasa (100k hab.)", format="%.1f"),
            "hurtos_total": st.column_config.NumberColumn("Hurtos 2023", format="localized"),
        }, **ANCHO_COMPLETO)
        st.warning("**No se eliminan:** son fenómenos reales. Corresponden a polos comerciales, de servicios y de "
                   "transporte (Providencia, Santiago, Estación Central) que reciben gran población flotante no "
                   "contabilizada en la población residente. Se analizan con y sin ellos en las páginas siguientes.")
    with ox:
        st.markdown(f"##### 🌳 X – Áreas verdes ({len(o_x)} outliers)")
        st.caption(f"Regla IQR: valores > Q3 + 1,5·IQR = {fmt_num(lim_x, 2)} m²/hab.")
        t_x = df.loc[o_x.index, ["comuna", "sector", "area_verde_m2_hab", "pct_pobreza"]].sort_values(
            "area_verde_m2_hab", ascending=False)
        st.dataframe(t_x, hide_index=True, column_config={
            "comuna": "Comuna", "sector": "Sector",
            "area_verde_m2_hab": st.column_config.NumberColumn("m²/hab", format="%.2f"),
            "pct_pobreza": st.column_config.NumberColumn("Pobreza (%)", format="%.1f%%"),
        }, **ANCHO_COMPLETO)
        st.warning("**No se eliminan, pero se analizan por separado:** coinciden con las únicas comunas que superan "
                   "el estándar de 9 m²/hab. La mayoría son de altos ingresos del sector oriente; Recoleta y "
                   "Cerrillos rompen ese patrón por la presencia de grandes parques o cerros urbanos.")

# ── 4. Cobertura ─────────────────────────────────────────────
with st.expander("4. Cobertura Temporal y Espacial", expanded=True):
    k1, k2 = st.columns([1, 1.6])
    with k1:
        st.markdown(
            f"""
**📅 Cobertura temporal**
- Enero–Diciembre 2023 (**12 meses**).
- Se usan datos **anuales consolidados**; la serie mensual se conserva como contexto.

**🗺️ Cobertura espacial**
- **{n_total} de {n_total}** comunas de la RM (**100%**) para hurtos, población y pobreza.
- Solo **{n_cat}** comunas con catastro MINVU (**{fmt_num(n_cat / n_total * 100, 0)}%**).
- Las {n_sin} comunas sin catastro son rurales o periurbanas del borde de la región (ver mapa).
"""
        )
    with k2:
        df_mapa = df.assign(Catastro=np.where(df["tiene_catastro_minvu"], "Con catastro", "Sin catastro"))
        fig = scatter_mapa(
            data_frame=df_mapa, lat="lat", lon="lon", color="Catastro", hover_name="comuna",
            hover_data={"sector": True, "poblacion": ":,", "lat": False, "lon": False, "Catastro": False},
            labels={"sector": "Sector", "poblacion": "Población"},
            color_discrete_map={"Con catastro": COLOR_X, "Sin catastro": "#95a5a6"},
            zoom=9, center={"lat": -33.45, "lon": -70.65}, mapbox_style="open-street-map", height=420,
        )
        fig.update_traces(marker=dict(size=12))
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title="Catastro MINVU")
        st.plotly_chart(fig, **ANCHO_COMPLETO)

st.divider()

# ═════════════════════════════════════════════════════════════
# ESTADÍSTICAS DESCRIPTIVAS
# ═════════════════════════════════════════════════════════════
st.header("📈 Estadísticas Descriptivas Generales")
nombres = {
    "tasa_hurtos_100k": "Tasa de hurtos (100k hab.)",
    "area_verde_m2_hab": "Área verde (m²/hab)",
    "poblacion": "Población",
    "pct_pobreza": "Pobreza (%)",
}
desc = df[list(nombres)].describe().T.rename(index=nombres)
desc = desc.rename(columns={"count": "N", "mean": "Media", "std": "Desv. estándar", "min": "Mínimo",
                            "25%": "Q1 (25%)", "50%": "Mediana", "75%": "Q3 (75%)", "max": "Máximo"})
desc["Asimetría"] = df[list(nombres)].skew().values
st.dataframe(desc.style.format(lambda v: fmt_num(v, 2)).background_gradient(
    cmap="Greens", subset=["Asimetría"]), **ANCHO_COMPLETO)

y, x = df["tasa_hurtos_100k"], df["area_verde_m2_hab"].dropna()
st.info(
    f"**Interpretación:** la tasa de hurtos (Y) tiene media {fmt_num(y.mean(), 1)} y mediana {fmt_num(y.median(), 1)}: "
    f"la media supera a la mediana y la asimetría es {fmt_num(y.skew(), 2)}, lo que indica que unas pocas comunas "
    f"concentran tasas muy altas. El área verde (X) también es asimétrica ({fmt_num(x.skew(), 2)}), con mediana de solo "
    f"{fmt_num(x.median(), 1)} m²/hab —muy por debajo del estándar de 9 m²/hab—. La población varía entre "
    f"{fmt_num(df['poblacion'].min())} y {fmt_num(df['poblacion'].max())} habitantes, lo que justifica normalizar ambos "
    "indicadores. Estas distribuciones sesgadas anticipan que la correlación entre X e Y será sensible a los valores "
    "extremos, por lo que en las páginas siguientes se complementa Pearson con Spearman y se analizan los outliers."
)

st.divider()
st.caption("EIN092B Visualización | Avance 2 – 2026-II | Fuentes: CEAD, MINVU/INE, SAE")
