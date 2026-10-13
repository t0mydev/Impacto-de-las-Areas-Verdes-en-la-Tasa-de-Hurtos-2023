import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import os

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Análisis de la Pregunta | Áreas Verdes y Hurtos RM",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        h1 { color: #1e4620; }
        h2 { color: #2c5f2e !important; border-bottom: 2px solid #d8e8d9; padding-bottom: 0.3rem; }
        h3 { color: #4a7c59 !important; }
        hr { border: none; border-top: 1px solid #dfe9e0; margin: 1.5rem 0; }
        div[data-testid="stMetric"] {
            background-color: #f4f9f4;
            border: 1px solid #d8e8d9;
            border-radius: 10px;
            padding: 0.8rem 1rem;
        }
        div[data-testid="stMetricLabel"] p { color: #2c5f2e; font-weight: 600; }
        .nota-fuente { color: #6b7b6e; font-size: 0.85rem; font-style: italic; }
    </style>
    """,
    unsafe_allow_html=True,
)

PALETA_SECTORES = {
    "Centro": "#1b4332",
    "Norte": "#40916c",
    "Oriente": "#74c69d",
    "Poniente": "#b7e4c7",
    "Sur": "#95a83f",
}
VARIABLES_ES = {
    "area_verde_total_ha": "Área verde total (ha)",
    "area_verde_m2_hab": "Área verde (m²/hab)",
    "hurtos_total": "Total de hurtos",
    "tasa_hurtos_100k": "Tasa de hurtos (100k hab.)",
    "poblacion": "Población",
    "pct_pobreza": "Pobreza por ingresos (%)",
}
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _rutas_candidatas(nombre_archivo):
    """Rutas relativas al cwd (según enunciado) y absolutas respecto de este archivo."""
    base = os.path.dirname(os.path.abspath(__file__))
    relativas = [
        f"../../data/processed/{nombre_archivo}",
        f"../data/processed/{nombre_archivo}",
        f"data/processed/{nombre_archivo}",
    ]
    absolutas = [os.path.normpath(os.path.join(base, "..", "..", "data", "processed", nombre_archivo))]
    return relativas + absolutas


@st.cache_data
def load_data():
    """Carga el dataset comunal procesado; si no se encuentra, usa datos de muestra."""
    for ruta in _rutas_candidatas("rm_comunas_2023.csv"):
        try:
            return pd.read_csv(ruta), True
        except (FileNotFoundError, OSError):
            continue
    muestra = pd.DataFrame({
        "comuna": ["Santiago", "Providencia", "Las Condes", "Maipú", "Puente Alto", "La Pintana"],
        "sector": ["Centro", "Centro", "Oriente", "Poniente", "Sur", "Sur"],
        "poblacion": [547366, 164397, 344516, 586963, 669122, 188869],
        "area_verde_total_ha": [181.8, 215.4, 137.4, 302.7, 218.9, 65.8],
        "area_verde_m2_hab": [3.32, 13.10, 3.99, 5.16, 3.27, 3.48],
        "hurtos_total": [8038, 4595, 2866, 1772, 2589, 500],
        "tasa_hurtos_100k": [1468.5, 2795.1, 831.9, 301.9, 386.9, 264.7],
        "lat": [-33.4489, -33.4323, -33.4117, -33.5100, -33.6100, -33.5757],
        "lon": [-70.6693, -70.6097, -70.5794, -70.7600, -70.5773, -70.6282],
        "clasificacion_zona": ["Urbano_denso", "Urbano_denso", "Urbano", "Urbano", "Urbano", "Urbano"],
    })
    return muestra, False


@st.cache_data
def load_monthly():
    """Carga los hurtos mensuales 2023 por comuna (opcional)."""
    for ruta in _rutas_candidatas("rm_hurtos_mensuales_2023.csv"):
        try:
            return pd.read_csv(ruta)
        except (FileNotFoundError, OSError):
            continue
    return None


_ST_VERSION = tuple(int(x) for x in st.__version__.split(".")[:2])
ANCHO_COMPLETO = {"width": "stretch"} if _ST_VERSION >= (1, 46) else {"use_container_width": True}


def mostrar_plotly(fig):
    """Compatibilidad entre versiones de Streamlit para el ancho de los gráficos."""
    st.plotly_chart(fig, **ANCHO_COMPLETO)


def fmt_num(valor, decimales=0):
    """Formato numérico chileno: punto como separador de miles y coma decimal."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def scatter_mapa(**kwargs):
    """Usa px.scatter_map (Plotly ≥ 5.24, MapLibre) si existe; si no, px.scatter_mapbox."""
    if hasattr(px, "scatter_map"):
        kwargs["map_style"] = kwargs.pop("mapbox_style", "open-street-map")
        return px.scatter_map(**kwargs)
    return px.scatter_mapbox(**kwargs)


def describir_r(r):
    """Fuerza y dirección de un coeficiente de correlación."""
    a = abs(r)
    fuerza = "muy débil" if a < 0.1 else "débil" if a < 0.3 else "moderada" if a < 0.5 else "fuerte"
    direccion = "positiva" if r > 0 else "negativa"
    return fuerza, direccion


df_raw, datos_reales = load_data()
df_mensual = load_monthly()
if not datos_reales:
    st.warning("⚠️ No se encontró `data/processed/rm_comunas_2023.csv`. Se están usando datos de muestra.")

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Filtros de Análisis")

    sectores_disp = sorted(df_raw["sector"].dropna().unique().tolist())
    sectores_sel = st.multiselect("Sectores a incluir", options=sectores_disp, default=sectores_disp)

    max_av = int(np.ceil(df_raw["area_verde_m2_hab"].max(skipna=True)))
    av_min = st.slider("Área verde mínima (m²/hab)", min_value=0, max_value=max_av, value=0, step=1)

    metrica = st.radio("Métrica de hurtos", ["Tasa por 100.000 hab.", "Total de hurtos"])
    mostrar_tendencia = st.checkbox("Mostrar línea de tendencia", value=True)

    excluir_rurales = st.checkbox(
        "Excluir comunas rurales",
        value=False,
        help="Comunas como San José de Maipo, Pirque o Tiltil tienen gran extensión natural, pero el "
             "catastro MINVU solo cubre áreas verdes urbanas consolidadas, por lo que sus valores per cápita "
             "no son comparables con las comunas urbanas.",
    )
    excluir_outliers = st.checkbox(
        "Excluir polos comerciales (Santiago y Providencia)",
        value=False,
        help="Estas comunas concentran población flotante (trabajo, comercio, turismo) que no se refleja "
             "en su población residente, lo que eleva artificialmente su tasa de hurtos.",
    )

    df = df_raw[df_raw["sector"].isin(sectores_sel)].copy()
    df = df[df["area_verde_m2_hab"].isna() | (df["area_verde_m2_hab"] >= av_min)] if av_min == 0 \
        else df[df["area_verde_m2_hab"] >= av_min]
    if excluir_rurales:
        df = df[df["clasificacion_zona"] != "Rural"]
    if excluir_outliers:
        df = df[~df["comuna"].isin(["Santiago", "Providencia"])]

    # Subconjunto con ambas variables (X e Y) disponibles para análisis bivariado
    df_xy = df.dropna(subset=["area_verde_m2_hab", "tasa_hurtos_100k"]).copy()

    st.divider()
    st.metric("Comunas seleccionadas", len(df))
    if len(df) != len(df_xy):
        st.caption(f"{len(df) - len(df_xy)} comuna(s) sin catastro MINVU de áreas verdes se excluyen "
                   "del análisis bivariado.")
    st.markdown("*Datos: 2023 – Región Metropolitana*")

col_y = "tasa_hurtos_100k" if metrica == "Tasa por 100.000 hab." else "hurtos_total"
etiqueta_y = "Tasa de Hurtos (por 100.000 hab.)" if col_y == "tasa_hurtos_100k" else "Total de Hurtos (2023)"

# ─────────────────────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────────────────────
st.title("🔍 Análisis de la Pregunta de Investigación")
st.info(
    "**Pregunta de investigación:** ¿Existe correlación entre los metros cuadrados de áreas verdes y la "
    "tasa de hurtos en las comunas de la Región Metropolitana durante el año 2023?"
)

if len(df_xy) < 3:
    st.error("Los filtros seleccionados dejan menos de 3 comunas con datos completos. "
             "Amplía la selección en la barra lateral para poder realizar el análisis.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Comunas analizadas", len(df))
c2.metric("Área verde promedio", f"{df['area_verde_m2_hab'].mean():.1f} m²/hab")
c3.metric("Tasa promedio de hurtos", f"{fmt_num(df['tasa_hurtos_100k'].mean())} / 100k hab.")
st.markdown(
    '<p class="nota-fuente">Fuentes: CEAD – Subsecretaría de Prevención del Delito (hurtos 2023); '
    "MINVU-INE (catastro de áreas verdes); Ministerio de Desarrollo Social – SAE (población y pobreza).</p>",
    unsafe_allow_html=True,
)

st.divider()

# ═════════════════════════════════════════════════════════════
# SECCIÓN 3.3: RELACIONES ENTRE VARIABLES
# ═════════════════════════════════════════════════════════════
st.header("📊 3.3 Relaciones entre Variables")

# Estadísticos globales (se usan en varias secciones)
pearson_r, p_value = stats.pearsonr(df_xy["area_verde_m2_hab"], df_xy[col_y])
spearman_rho, spearman_p = stats.spearmanr(df_xy["area_verde_m2_hab"], df_xy[col_y])
fuerza, direccion = describir_r(pearson_r)
significativa = p_value < 0.05

# ── VIZ 1: Dispersión ────────────────────────────────────────
st.subheader("Dispersión: Área Verde vs Tasa de Hurtos por Comuna")

fig = px.scatter(
    df_xy,
    x="area_verde_m2_hab",
    y=col_y,
    color="sector",
    color_discrete_map=PALETA_SECTORES,
    size="poblacion",
    size_max=45,
    hover_name="comuna",
    hover_data={
        "area_verde_m2_hab": ":.1f",
        "tasa_hurtos_100k": ":.0f",
        "hurtos_total": True,
        "poblacion": ":,",
        "clasificacion_zona": True,
    },
    trendline="ols" if mostrar_tendencia else None,
    trendline_scope="overall",
    trendline_color_override="#c0392b",
    labels={
        "area_verde_m2_hab": "Área Verde (m²/hab)",
        "tasa_hurtos_100k": "Tasa de Hurtos (por 100.000 hab.)",
        "hurtos_total": "Total de Hurtos",
        "poblacion": "Población",
        "clasificacion_zona": "Zona",
        "sector": "Sector",
    },
    title="Relación entre Área Verde y Tasa de Hurtos – Comunas RM 2023",
)
fig.update_layout(template="plotly_white", height=550, legend_title="Sector")
fig.for_each_trace(lambda t: t.update(name="Tendencia lineal (MCO)") if t.mode == "lines" else None)
fig.add_annotation(
    xref="paper", yref="paper", x=0.99, y=0.99, xanchor="right", yanchor="top",
    text=f"r = {pearson_r:.3f} (p={p_value:.3f})",
    showarrow=False, font=dict(size=14, color="#1e4620"),
    bgcolor="rgba(244,249,244,0.9)", bordercolor="#2c5f2e", borderwidth=1,
)
mostrar_plotly(fig)

col_stat, col_interp = st.columns([1, 1.4])
with col_stat:
    tabla = pd.DataFrame({
        "Estadístico": ["r de Pearson", "p-valor (Pearson)", "ρ de Spearman", "p-valor (Spearman)",
                        "n (comunas)", "Interpretación"],
        "Valor": [f"{pearson_r:.3f}", f"{p_value:.4f}", f"{spearman_rho:.3f}", f"{spearman_p:.4f}",
                  str(len(df_xy)),
                  f"Correlación {direccion} {fuerza}" + (" (significativa, α=0,05)" if significativa
                                                         else " (no significativa, α=0,05)")],
    })
    st.dataframe(tabla, hide_index=True, **ANCHO_COMPLETO)
with col_interp:
    tendencia_txt = "mayor" if pearson_r > 0.1 else "menor" if pearson_r < -0.1 else "similar"
    texto = (
        f"La correlación entre área verde y {etiqueta_y.lower()} es **{direccion} y {fuerza}** "
        f"(r = {pearson_r:.3f}, p = {p_value:.3f}). Esto sugiere que comunas con mayor superficie verde "
        f"por habitante tienden a registrar **{tendencia_txt}** nivel de hurtos. "
        f"El coeficiente de Spearman (ρ = {spearman_rho:.3f}, p = {spearman_p:.3f}), menos sensible a valores "
        "extremos, permite evaluar si la relación se sostiene sin el peso de las comunas atípicas. "
        "Sin embargo, esta relación puede estar mediada por factores socioeconómicos, de densidad urbana y de "
        "población flotante que requieren un análisis más profundo."
    )
    if significativa and abs(pearson_r) >= 0.3:
        st.success(texto)
    else:
        st.warning(texto)
    if {"Santiago", "Providencia"}.issubset(set(df_xy["comuna"])):
        st.caption("💡 Prueba activar *Excluir polos comerciales* en la barra lateral para ver cómo cambia "
                   "el coeficiente sin Santiago y Providencia.")

# ── VIZ 2: Box plot por nivel de área verde ──────────────────
st.subheader("Distribución de Hurtos según Nivel de Área Verde")

etiquetas_cat = ["Baja (<Q33)", "Media (Q33–Q67)", "Alta (>Q67)"]
df_box = df_xy.copy()
try:
    df_box["categoria_av"] = pd.qcut(df_box["area_verde_m2_hab"], q=3, labels=etiquetas_cat)
except ValueError:
    df_box["categoria_av"] = pd.qcut(df_box["area_verde_m2_hab"].rank(method="first"), q=3,
                                     labels=etiquetas_cat)

fig = px.box(
    df_box,
    x="categoria_av",
    y=col_y,
    color="categoria_av",
    color_discrete_map={"Baja (<Q33)": "#d73027", "Media (Q33–Q67)": "#fee08b", "Alta (>Q67)": "#1a9850"},
    category_orders={"categoria_av": etiquetas_cat},
    points="all",
    hover_name="comuna",
    hover_data={"area_verde_m2_hab": ":.1f", "categoria_av": False},
    title="Distribución de Tasa de Hurtos por Nivel de Área Verde",
    labels={
        "categoria_av": "Nivel de área verde (terciles de m²/hab)",
        "tasa_hurtos_100k": "Tasa de Hurtos (por 100.000 hab.)",
        "hurtos_total": "Total de Hurtos",
        "area_verde_m2_hab": "Área Verde (m²/hab)",
    },
)
fig.update_layout(height=480, template="plotly_white", showlegend=False)
mostrar_plotly(fig)

resumen_box = df_box.groupby("categoria_av", observed=True).agg(
    mediana=(col_y, "median"), n=(col_y, "size"),
    av_min=("area_verde_m2_hab", "min"), av_max=("area_verde_m2_hab", "max"),
).reindex(etiquetas_cat)
med_baja, med_media, med_alta = resumen_box["mediana"].tolist()
grupos = [g[col_y].values for _, g in df_box.groupby("categoria_av", observed=True)]
kw_stat, kw_p = stats.kruskal(*grupos) if all(len(g) > 1 for g in grupos) else (np.nan, np.nan)

if med_alta > med_baja * 1.1:
    patron = "aumenta"
elif med_alta < med_baja * 0.9:
    patron = "disminuye"
else:
    patron = "se mantiene relativamente estable"
st.info(
    f"**Interpretación:** las medianas de {etiqueta_y.lower()} por tercil son: Baja = {fmt_num(med_baja)}, "
    f"Media = {fmt_num(med_media)} y Alta = {fmt_num(med_alta)}. Es decir, la mediana **{patron}** a medida que crece "
    f"el área verde por habitante. La prueba de Kruskal-Wallis (H = {kw_stat:.2f}, p = {kw_p:.3f}) indica que las "
    f"diferencias entre grupos {'son' if kw_p < 0.05 else 'no son'} estadísticamente significativas (α = 0,05). "
    "La amplia dispersión dentro de cada grupo —y la presencia de valores extremos— muestra que el área verde, "
    "por sí sola, no basta para explicar el nivel de hurtos de una comuna; para la pregunta de investigación "
    "esto implica que cualquier asociación observada debe leerse junto con variables de contexto urbano."
)

# ── VIZ 3: Heatmap de correlaciones ──────────────────────────
st.subheader("Matriz de Correlaciones entre Variables Numéricas")

vars_corr = [v for v in ["area_verde_total_ha", "area_verde_m2_hab", "hurtos_total", "tasa_hurtos_100k",
                         "poblacion", "pct_pobreza"] if v in df_xy.columns]
corr = df_xy[vars_corr].corr().rename(index=VARIABLES_ES, columns=VARIABLES_ES)

col_hm, col_hm_txt = st.columns([1.3, 1])
with col_hm:
    fig, ax = plt.subplots(figsize=(8, 6))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn_r", vmin=-1, vmax=1, center=0,
                linewidths=0.5, cbar_kws={"label": "Coeficiente de Pearson"}, ax=ax)
    ax.set_title("Correlación entre variables – Comunas RM 2023", fontsize=13, color="#2c5f2e", pad=12)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
with col_hm_txt:
    corr_y = df_xy[vars_corr].corr()["tasa_hurtos_100k"].drop("tasa_hurtos_100k").sort_values(
        key=lambda s: s.abs(), ascending=False)
    lineas = "\n".join(
        f"- **{VARIABLES_ES[v]}**: r = {r:.2f} ({describir_r(r)[1]}, {describir_r(r)[0]})"
        for v, r in corr_y.items()
    )
    st.markdown("**Correlaciones con la tasa de hurtos (Y), ordenadas por magnitud:**\n\n" + lineas)
    var_top = corr_y.index[0]
    st.info(
        f"La variable más asociada a la tasa de hurtos es **{VARIABLES_ES[var_top]}** "
        f"(r = {corr_y.iloc[0]:.2f}). La relación con el área verde por habitante (r = "
        f"{corr_y.get('area_verde_m2_hab', np.nan):.2f}) debe compararse con la de la pobreza: una correlación "
        "negativa entre pobreza y hurtos denunciados suele reflejar que las comunas de mayores ingresos "
        "concentran comercio, población flotante y mayor propensión a denunciar, lo que actúa como posible "
        "variable de confusión en la relación área verde – hurtos."
    )

# ── VIZ 4: Ranking comunal ───────────────────────────────────
st.subheader("Ranking de Comunas: Tasa de Hurtos vs Área Verde")

df_rank = df_xy.sort_values(col_y, ascending=False).head(20).iloc[::-1]
norm = plt.Normalize(df_xy["area_verde_m2_hab"].min(), df_xy["area_verde_m2_hab"].max())
cmap = plt.get_cmap("RdYlGn")
colores = cmap(norm(df_rank["area_verde_m2_hab"].values))

fig, ax = plt.subplots(figsize=(11, max(4, 0.42 * len(df_rank) + 1.5)))
barras = ax.barh(df_rank["comuna"], df_rank[col_y], color=colores, edgecolor="#555555", linewidth=0.4)
for barra, valor, av in zip(barras, df_rank[col_y], df_rank["area_verde_m2_hab"]):
    ax.text(barra.get_width() + df_rank[col_y].max() * 0.01, barra.get_y() + barra.get_height() / 2,
            f"{fmt_num(valor)}  ({fmt_num(av, 1)} m²/hab)", va="center", fontsize=8.5, color="#333333")
ax.set_xlim(0, df_rank[col_y].max() * 1.22)
ax.set_xlabel("Tasa de hurtos por 100.000 hab." if col_y == "tasa_hurtos_100k" else "Total de hurtos (2023)")
ax.set_ylabel("Comuna")
ax.set_title("Ranking Comunal: Tasa de Hurtos y Nivel de Área Verde (2023)", fontsize=13, color="#2c5f2e")
ax.spines[["top", "right"]].set_visible(False)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, pad=0.01)
cbar.set_label("m²/hab de área verde")
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
if len(df_xy) > 20:
    st.caption(f"Se muestran las 20 comunas con mayor valor de un total de {len(df_xy)} comunas filtradas.")

top5 = df_xy.sort_values(col_y, ascending=False).head(5)
mediana_av = df_xy["area_verde_m2_hab"].median()
top5_bajo = top5[top5["area_verde_m2_hab"] < mediana_av]["comuna"].tolist()
top5_alto = top5[top5["area_verde_m2_hab"] >= mediana_av]["comuna"].tolist()
texto_rank = (
    f"**Interpretación:** de las 5 comunas con mayor nivel de hurtos, {len(top5_bajo)} tienen área verde "
    f"bajo la mediana ({mediana_av:.1f} m²/hab)"
    + (f" ({', '.join(top5_bajo)})" if top5_bajo else "")
    + f" y {len(top5_alto)} sobre ella"
    + (f" ({', '.join(top5_alto)})" if top5_alto else "")
    + ". Por lo tanto, **no se observa que las comunas con más hurtos sean sistemáticamente las con menos área "
      "verde**. "
)
if "Santiago" in df_xy["comuna"].values:
    texto_rank += (
        "**Santiago** es un caso especial: con poca área verde por residente, concentra el centro comercial, "
        "financiero y de transporte de la región, por lo que su tasa de hurtos —calculada sobre población "
        "residente— se ve inflada por la población flotante. "
    )
if "Providencia" in df_xy["comuna"].values:
    texto_rank += (
        "**Providencia** es la excepción más notable: combina una de las mayores dotaciones de área verde con la "
        "tasa de hurtos más alta, por su rol de polo comercial y de servicios."
    )
st.info(texto_rank)

st.divider()

# ═════════════════════════════════════════════════════════════
# SECCIÓN 3.4: COMPONENTE ESPACIAL / CONTEXTUAL
# ═════════════════════════════════════════════════════════════
st.header("🗺️ 3.4 Componente Espacial — Distribución Geográfica en la RM")
st.markdown("Como el proyecto tiene datos de **año 2023** (un único período), la dimensión contextual clave es "
            "la **distribución espacial** entre las 52 comunas de la Región Metropolitana.")

# ── VIZ 5: Mapa de burbujas ──────────────────────────────────
st.subheader("Distribución Espacial: Hurtos y Áreas Verdes por Comuna")

col_map_control, col_map = st.columns([1, 3.2])
with col_map_control:
    var_mapa = st.radio("Variable a visualizar en el mapa",
                        ["Tasa de Hurtos (por 100k hab.)", "Área Verde (m²/hab)", "Ambas variables"])
    st.markdown(
        "- **Tasa de hurtos:** incluye todas las comunas filtradas.\n"
        "- **Área verde / Ambas:** solo comunas con catastro MINVU.\n"
        "- Pasa el cursor sobre cada burbuja para ver el detalle."
    )

hover_mapa = {
    "sector": True, "clasificacion_zona": True, "poblacion": ":,", "area_verde_m2_hab": ":.1f",
    "area_verde_total_ha": ":.1f", "hurtos_total": ":,", "tasa_hurtos_100k": ":.0f", "lat": False, "lon": False,
}
labels_mapa = {
    "sector": "Sector", "clasificacion_zona": "Zona", "poblacion": "Población",
    "area_verde_m2_hab": "Área verde (m²/hab)", "area_verde_total_ha": "Área verde total (ha)",
    "hurtos_total": "Total de hurtos", "tasa_hurtos_100k": "Tasa de hurtos (100k hab.)",
}
params_mapa = dict(lat="lat", lon="lon", hover_name="comuna", hover_data=hover_mapa, labels=labels_mapa,
                   mapbox_style="open-street-map", zoom=9, center={"lat": -33.45, "lon": -70.65},
                   height=600, size_max=32, opacity=0.8)

if var_mapa == "Tasa de Hurtos (por 100k hab.)":
    fig = scatter_mapa(data_frame=df.dropna(subset=["lat", "lon"]), color="tasa_hurtos_100k",
                       size="tasa_hurtos_100k", color_continuous_scale="Reds",
                       title="Tasa de Hurtos por 100.000 hab. – Comunas RM 2023", **params_mapa)
elif var_mapa == "Área Verde (m²/hab)":
    fig = scatter_mapa(data_frame=df_xy, color="area_verde_m2_hab", size="area_verde_m2_hab",
                       color_continuous_scale="Greens", title="Área Verde (m²/hab) – Comunas RM 2023",
                       **params_mapa)
else:
    fig = scatter_mapa(data_frame=df_xy, color="tasa_hurtos_100k", size="area_verde_m2_hab",
                       color_continuous_scale="Reds",
                       title="Color = tasa de hurtos (100k hab.) · Tamaño = área verde (m²/hab) – RM 2023",
                       **params_mapa)
fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=50, b=0))
with col_map:
    mostrar_plotly(fig)
    if var_mapa == "Ambas variables":
        st.caption("🔴 Burbujas más rojas = mayor tasa de hurtos · ⚪ burbujas más grandes = más área verde "
                   "por habitante. Burbujas grandes y rojas indican comunas con mucha área verde y muchos hurtos.")

por_sector = df_xy.groupby("sector").agg(av=("area_verde_m2_hab", "mean"), tasa=("tasa_hurtos_100k", "mean"))
sector_max_h = por_sector["tasa"].idxmax()
sector_min_h = por_sector["tasa"].idxmin()
sector_max_av = por_sector["av"].idxmax()
sector_min_av = por_sector["av"].idxmin()
top_av = df_xy.nlargest(3, "area_verde_m2_hab")["comuna"].tolist()
st.info(
    f"**Interpretación espacial:** las tasas de hurtos más altas se concentran en el eje **centro-oriente** de la "
    f"RM (sector con mayor promedio: **{sector_max_h}**), donde se ubican los principales polos comerciales, "
    f"financieros y de transporte. Las comunas periféricas —especialmente del sector **{sector_min_h}**— muestran "
    f"tasas menores. Las áreas verdes están distribuidas de forma desigual: el sector **{sector_max_av}** presenta "
    f"la mayor dotación promedio por habitante y el sector **{sector_min_av}** la menor; las comunas con más área "
    f"verde por habitante son {', '.join(top_av)}, lo que muestra que la dotación verde depende tanto del nivel "
    "socioeconómico (sector oriente) como de la presencia de grandes parques o cerros urbanos. Este patrón sugiere "
    "que ambas variables comparten un gradiente territorial (centro-oriente vs. periferia) que podría explicar parte "
    "de la correlación observada."
)

# ── VIZ 6: Comparación por sector ────────────────────────────
st.subheader("Comparación por Sector de la RM: Área Verde y Tasa de Hurtos")

av_sector = por_sector["av"].sort_values(ascending=True)
h_sector = por_sector["tasa"].sort_values(ascending=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
verdes = sns.color_palette("Greens", n_colors=len(av_sector) + 2)[2:]
rojos = sns.color_palette("Reds", n_colors=len(h_sector) + 2)[2:]
b1 = ax1.barh(av_sector.index, av_sector.values, color=verdes, edgecolor="#2c5f2e")
b2 = ax2.barh(h_sector.index, h_sector.values, color=rojos, edgecolor="#8b1a1a")
for ax, barras, valores, fmt in [(ax1, b1, av_sector.values, "{:.1f}"), (ax2, b2, h_sector.values, "{:.0f}")]:
    for barra, v in zip(barras, valores):
        ax.text(barra.get_width() + max(valores) * 0.015, barra.get_y() + barra.get_height() / 2,
                fmt.format(v), va="center", fontsize=10)
    ax.set_xlim(0, max(valores) * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
ax1.set_title("Área Verde Promedio (m²/hab)", color="#2c5f2e", fontsize=12)
ax2.set_title("Tasa de Hurtos Promedio (por 100k hab.)", color="#8b1a1a", fontsize=12)
ax1.set_xlabel("m²/hab")
ax2.set_xlabel("Hurtos por 100.000 hab.")
ax1.set_ylabel("Sector")
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

rho_sector = stats.spearmanr(por_sector["av"], por_sector["tasa"])[0] if len(por_sector) >= 3 else np.nan
col_i1, col_i2 = st.columns(2)
with col_i1:
    st.success(
        f"**🌳 Área verde por sector:** el sector **{sector_max_av}** lidera con "
        f"{por_sector.loc[sector_max_av, 'av']:.1f} m²/hab en promedio, mientras que **{sector_min_av}** registra "
        f"solo {por_sector.loc[sector_min_av, 'av']:.1f} m²/hab. Todos los sectores se ubican por debajo del "
        "estándar de 9 m²/hab recomendado internacionalmente, lo que evidencia un déficit generalizado y desigual."
    )
with col_i2:
    st.error(
        (f"**🚨 Hurtos por sector:** **{sector_max_h}** presenta la tasa promedio más alta "
         f"({fmt_num(por_sector.loc[sector_max_h, 'tasa'])} por 100k hab.), mientras que **{sector_min_h}** registra "
         f"la más baja ({fmt_num(por_sector.loc[sector_min_h, 'tasa'])}). "
         if len(por_sector) > 1 else
         f"**🚨 Hurtos por sector:** solo se seleccionó el sector **{sector_max_h}**, con una tasa promedio de "
         f"{fmt_num(por_sector.loc[sector_max_h, 'tasa'])} por 100k hab. Selecciona más sectores para comparar. ")
        + ("Al comparar ambos rankings sectoriales (ρ de Spearman = "
           f"{rho_sector:.2f}), " if not np.isnan(rho_sector) else "")
        + ("se observa **coherencia espacial**: los sectores con más área verde tienden a tener más hurtos "
           "denunciados, en línea con la correlación comunal positiva."
           if rho_sector > 0.3 else
           "se observa que sectores con más área verde tienden a tener menos hurtos."
           if rho_sector < -0.3 else
           "no se aprecia una coherencia espacial clara entre ambas variables a escala sectorial."
           if not np.isnan(rho_sector) else "")
    )

# ── VIZ 7 (complementaria): Patrón mensual por sector ────────
if df_mensual is not None:
    st.subheader("Contexto Complementario: Hurtos Mensuales 2023 por Sector")
    dm = df_mensual[df_mensual["comuna"].isin(df["comuna"])]
    if not dm.empty:
        pob_sector = df.groupby("sector")["poblacion"].sum()
        mens_sector = dm.groupby(["sector", "mes"])["hurtos"].sum().reset_index()
        mens_sector["tasa_mensual_100k"] = mens_sector.apply(
            lambda f: f["hurtos"] / pob_sector[f["sector"]] * 100_000, axis=1)
        mens_sector["Mes"] = mens_sector["mes"].map(lambda m: MESES_ES[m - 1])
        fig = px.line(
            mens_sector, x="Mes", y="tasa_mensual_100k", color="sector", markers=True,
            color_discrete_map=PALETA_SECTORES, category_orders={"Mes": MESES_ES},
            labels={"tasa_mensual_100k": "Hurtos por 100.000 hab. (mensual)", "sector": "Sector"},
            title="Tasa mensual de hurtos por sector – RM 2023",
        )
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(template="plotly_white", height=430, legend_title="Sector")
        mostrar_plotly(fig)
        total_mes = dm.groupby("mes")["hurtos"].sum()
        mes_max, mes_min = MESES_ES[total_mes.idxmax() - 1], MESES_ES[total_mes.idxmin() - 1]
        cv = total_mes.std() / total_mes.mean() * 100
        st.info(
            f"**Interpretación:** aunque la pregunta se responde con el consolidado anual, la serie mensual confirma "
            f"que las diferencias entre sectores son **estables durante todo el año** (no dependen de un mes "
            f"puntual). El mes con más hurtos fue **{mes_max}** y el con menos, **{mes_min}**; la variación mensual "
            f"(coeficiente de variación ≈ {cv:.0f}%) es pequeña frente a la brecha entre sectores, lo que respalda el "
            "uso del total anual 2023 como medida representativa de cada comuna."
        )

st.divider()

# ═════════════════════════════════════════════════════════════
# HALLAZGOS PRELIMINARES
# ═════════════════════════════════════════════════════════════
st.header("💡 Hallazgos Preliminares")

outliers_presentes = [c for c in ["Santiago", "Providencia"] if c in df_xy["comuna"].values]
sin_outliers = df_xy[~df_xy["comuna"].isin(["Santiago", "Providencia"])]
r_sin = stats.pearsonr(sin_outliers["area_verde_m2_hab"], sin_outliers[col_y])[0] \
    if len(sin_outliers) >= 3 else np.nan
rurales = df_raw[df_raw["clasificacion_zona"] == "Rural"]
rurales_sin_dato = rurales[rurales["area_verde_m2_hab"].isna()]["comuna"].tolist()
rurales_bajo = rurales[rurales["area_verde_m2_hab"] < 1]["comuna"].tolist()

with st.expander("Ver hallazgos completos", expanded=True):
    st.markdown(
        f"""
**En relación a la pregunta de investigación:**
- Con los filtros actuales (n = {len(df_xy)} comunas), la correlación entre área verde por habitante y
  {etiqueta_y.lower()} es **{direccion} y {fuerza}** (r = {pearson_r:.3f}, p = {p_value:.3f}; ρ de Spearman =
  {spearman_rho:.3f}). No se observa que más área verde se asocie a menos hurtos; si existe asociación, es en
  sentido contrario al esperado por la hipótesis de "prevención situacional".
- {"Las comunas **" + " y ".join(outliers_presentes) + "** se alejan del patrón general: concentran comercio, "
   "servicios y población flotante, lo que eleva su tasa calculada sobre residentes. Sin ellas, el coeficiente "
   f"cambia a r = {r_sin:.3f}, lo que muestra la sensibilidad del resultado a estos casos." if outliers_presentes
   else "Al excluir Santiago y Providencia (polos comerciales), el coeficiente resultante es r = "
   f"{pearson_r:.3f}, lo que permite evaluar la relación en comunas predominantemente residenciales."}
- Las comunas rurales poseen gran extensión natural pero el catastro MINVU solo registra áreas verdes urbanas
  consolidadas: {", ".join(rurales_bajo) if rurales_bajo else "algunas comunas"} presentan menos de 1 m²/hab y
  {", ".join(rurales_sin_dato) if rurales_sin_dato else "ninguna"} no tienen catastro. Su baja densidad y bajos
  hurtos hacen que no sean comparables con la trama urbana.

**Limitaciones identificadas:**
- El período anual no permite análisis de tendencias temporales (la serie mensual solo aporta estacionalidad).
- La variable área verde incluye tanto parques urbanos como terrenos no consolidados, y no mide calidad ni
  mantención de los espacios.
- Factores socioeconómicos y de densidad no están controlados en la correlación simple.
- La tasa de hurtos puede estar influenciada por la denuncia (subregistro en comunas más vulnerables) y por la
  población flotante que no se refleja en la población residente.

**Próximos pasos sugeridos:**
- Incorporar variable de densidad poblacional como control.
- Explorar si la relación varía según tipo de área verde (parques urbanos vs. plazas vs. áreas naturales).
- Analizar con variable socioeconómica (pobreza SAE, ISOC, ingreso promedio) mediante correlación parcial o
  regresión múltiple.
"""
    )
    st.info("Los resultados presentados corresponden a datos de muestra. Al integrar los datos reales del proyecto, "
            "los patrones podrían variar."
            if not datos_reales else
            "Los resultados se calculan dinámicamente con los datos reales del proyecto (CEAD, MINVU-INE y SAE 2023) "
            "y se actualizan según los filtros aplicados en la barra lateral.")

# ─────────────────────────────────────────────────────────────
# PIE DE PÁGINA
# ─────────────────────────────────────────────────────────────
st.divider()
st.caption("EIN092B Visualización | Avance 2 – 2026-II | Datos: Región Metropolitana, 2023")
