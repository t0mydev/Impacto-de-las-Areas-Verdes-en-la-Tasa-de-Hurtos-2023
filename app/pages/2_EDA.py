import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Análisis EDA | Áreas Verdes RM",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        h1 { color: #2c5f2e !important; }
        h2 { color: #2c5f2e !important; border-bottom: 2px solid #d8e8d9; padding-bottom: 0.3rem; }
        h3 { color: #4a7c59 !important; }
        div[data-testid="stMetric"] {
            background-color: #f4f9f4;
            border: 1px solid #d8e8d9;
            border-radius: 10px;
            padding: 0.6rem 0.9rem;
        }
        div[data-testid="stMetricLabel"] p { color: #2c5f2e; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

COLOR_Y, COLOR_X, COLOR_CTX = "#c0392b", "#27ae60", "#7f8c8d"
PALETA_SECTORES = {"Centro": "#1b4332", "Norte": "#40916c", "Oriente": "#74c69d", "Poniente": "#b7e4c7",
                   "Sur": "#95a83f"}
MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
OMS = 9
_ST_VERSION = tuple(int(x) for x in st.__version__.split(".")[:2])
ANCHO_COMPLETO = {"width": "stretch"} if _ST_VERSION >= (1, 46) else {"use_container_width": True}


def fmt_num(valor, decimales=0):
    """Formato numérico chileno: punto como separador de miles y coma decimal."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def mostrar_plotly(fig):
    st.plotly_chart(fig, **ANCHO_COMPLETO)


def describir_r(r):
    a = abs(r)
    fuerza = "muy débil" if a < 0.1 else "débil" if a < 0.3 else "moderada" if a < 0.5 else "fuerte"
    return fuerza, ("positiva" if r > 0 else "negativa")


def _leer_csv(nombre):
    base = os.path.dirname(os.path.abspath(__file__))
    rutas = [
        f"data/processed/{nombre}",
        f"../data/processed/{nombre}",
        f"../../data/processed/{nombre}",
        os.path.normpath(os.path.join(base, "..", "..", "data", "processed", nombre)),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            return pd.read_csv(ruta)
    return None


@st.cache_data
def load_data():
    """Devuelve (dataset comunal, serie mensual o None)."""
    return _leer_csv("rm_comunas_2023.csv"), _leer_csv("rm_hurtos_mensuales_2023.csv")


df, df_mensual = load_data()
if df is None:
    st.error("No se encontró `data/processed/rm_comunas_2023.csv`. Ejecuta `python scripts/build_dataset.py`.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Filtros del EDA")
    sectores = sorted(df["sector"].unique())
    sectores_sel = st.multiselect("Sectores", sectores, default=sectores)
    excl_out = st.checkbox(
        "Excluir outliers comerciales (Santiago y Providencia)", value=False,
        help="Estas comunas tienen tasas muy altas por población flotante, lo que puede distorsionar las "
             "distribuciones.")
    solo_cat = st.checkbox(
        "Solo comunas con catastro MINVU", value=True,
        help="Para el análisis de X se requieren las 44 comunas con datos de áreas verdes.")

    df_filtrado = df[df["sector"].isin(sectores_sel)].copy()
    if excl_out:
        df_filtrado = df_filtrado[~df_filtrado["comuna"].isin(["Santiago", "Providencia"])]
    if solo_cat:
        df_filtrado = df_filtrado[df_filtrado["tiene_catastro_minvu"]]
    df_xy = df_filtrado.dropna(subset=["area_verde_m2_hab"]).copy()

    st.divider()
    st.metric("Comunas en análisis", len(df_filtrado))
    st.caption(f"{len(df_xy)} con dato de áreas verdes (X).")

st.title("🔬 Análisis Exploratorio de Datos (EDA)")
st.markdown("Exploración de la **variable objetivo Y** (tasa de hurtos), la **variable explicativa X** (m² de áreas "
            "verdes por habitante) y sus relaciones. Usa los filtros de la barra lateral para ver cómo cambian los "
            "resultados.")

if len(df_xy) < 5:
    st.error("Los filtros dejan menos de 5 comunas con datos completos. Amplía la selección en la barra lateral.")
    st.stop()

# ═════════════════════════════════════════════════════════════
# SECCIÓN 3.2 — ANÁLISIS UNIVARIADO
# ═════════════════════════════════════════════════════════════
st.header("🔬 Sección 3.2 — Análisis Univariado")

# ── VIZ 1: Distribución de Y ─────────────────────────────────
st.subheader("1. Distribución de la Tasa de Hurtos (Y)")
y = df_filtrado["tasa_hurtos_100k"]
skew_y = y.skew()
q1y, q3y = y.quantile([0.25, 0.75])
lim_y = q3y + 1.5 * (q3y - q1y)
outl_y = df_filtrado[y > lim_y].sort_values("tasa_hurtos_100k", ascending=False)

col_viz, col_stats = st.columns([3, 1])
with col_viz:
    fig_y = make_subplots(rows=1, cols=2, subplot_titles=("Histograma", "Boxplot"), horizontal_spacing=0.08)
    fig_y.add_trace(go.Histogram(x=y, nbinsx=15, marker_color=COLOR_Y, marker_line_color="white",
                                 marker_line_width=1, name="Comunas",
                                 hovertemplate="Tasa: %{x}<br>Comunas: %{y}<extra></extra>"), row=1, col=1)
    fig_y.add_vline(x=y.median(), line_dash="dash", line_color="black", row=1, col=1,
                    annotation_text=f"Mediana: {fmt_num(y.median())}", annotation_position="top right")
    fig_y.add_trace(go.Box(x=y, orientation="h", boxpoints="all", jitter=0.4, marker_color=COLOR_Y,
                           name="Tasa", text=df_filtrado["comuna"],
                           hovertemplate="%{text}: %{x:.0f}<extra></extra>"), row=1, col=2)
    fig_y.update_xaxes(title_text="Hurtos por 100.000 hab.", row=1, col=1)
    fig_y.update_xaxes(title_text="Hurtos por 100.000 hab.", row=1, col=2)
    fig_y.update_yaxes(title_text="N° de comunas", row=1, col=1)
    fig_y.update_yaxes(showticklabels=False, row=1, col=2)
    fig_y.add_annotation(xref="paper", yref="paper", x=0.44, y=0.98, xanchor="right", showarrow=False,
                         text=f"Asimetría = {fmt_num(skew_y, 2)}", bgcolor="rgba(253,242,241,0.9)",
                         bordercolor=COLOR_Y, borderwidth=1)
    fig_y.update_layout(title="Distribución de Tasa de Hurtos por 100.000 hab.", height=380,
                        template="plotly_white", showlegend=False)
    mostrar_plotly(fig_y)
with col_stats:
    st.metric("Media", fmt_num(y.mean(), 1))
    st.metric("Mediana", fmt_num(y.median(), 1))
    st.metric("Desv. estándar", fmt_num(y.std(), 1))
    st.metric("Asimetría (skew)", fmt_num(skew_y, 2))

lista_out_y = ", ".join(f"{c} ({fmt_num(v)})" for c, v in zip(outl_y["comuna"], outl_y["tasa_hurtos_100k"]))
st.info(
    f"**Interpretación:** la distribución es **asimétrica a la derecha** (skew = {fmt_num(skew_y, 2)}; con todas las "
    "comunas es 3,44): la media supera a la mediana porque unas pocas comunas concentran tasas muy altas. "
    + (f"Con la regla IQR se identifican **{len(outl_y)} outliers**: {lista_out_y}. Son polos comerciales, de "
       "servicios y transporte con gran población flotante, que la tasa (calculada sobre residentes) amplifica. "
       if len(outl_y) else "Con los filtros actuales no se detectan outliers por la regla IQR. ")
    + "Para la pregunta, esto implica que la correlación con X puede estar dominada por pocos casos extremos."
)

# ── VIZ 2: Distribución de X ─────────────────────────────────
st.subheader("2. Distribución de Áreas Verdes por Habitante (X)")
x = df_xy["area_verde_m2_hab"]
skew_x = x.skew()
n_oms = int((x >= OMS).sum())
sobre_oms = df_xy[x >= OMS].sort_values("area_verde_m2_hab", ascending=False)["comuna"].tolist()

col_viz, col_stats = st.columns([3, 1])
with col_viz:
    fig_x = make_subplots(rows=1, cols=2, subplot_titles=("Histograma", "Boxplot"), horizontal_spacing=0.08)
    fig_x.add_trace(go.Histogram(x=x, nbinsx=12, marker_color=COLOR_X, marker_line_color="white",
                                 marker_line_width=1, name="Comunas",
                                 hovertemplate="m²/hab: %{x}<br>Comunas: %{y}<extra></extra>"), row=1, col=1)
    fig_x.add_vline(x=OMS, line_dash="dash", line_color="black", row=1, col=1,
                    annotation_text="OMS: 9 m²/hab", annotation_position="top right")
    fig_x.add_trace(go.Box(x=x, orientation="h", boxpoints="all", jitter=0.4, marker_color=COLOR_X,
                           name="m²/hab", text=df_xy["comuna"],
                           hovertemplate="%{text}: %{x:.1f} m²/hab<extra></extra>"), row=1, col=2)
    fig_x.update_xaxes(title_text="m² de área verde por habitante", row=1, col=1)
    fig_x.update_xaxes(title_text="m² de área verde por habitante", row=1, col=2)
    fig_x.update_yaxes(title_text="N° de comunas", row=1, col=1)
    fig_x.update_yaxes(showticklabels=False, row=1, col=2)
    fig_x.update_layout(title=f"Distribución de Áreas Verdes por Habitante – {len(df_xy)} comunas con catastro",
                        height=380, template="plotly_white", showlegend=False)
    mostrar_plotly(fig_x)
with col_stats:
    st.metric("Media", f"{fmt_num(x.mean(), 1)} m²/hab")
    st.metric("Mediana", f"{fmt_num(x.median(), 1)} m²/hab")
    st.metric("Asimetría (skew)", fmt_num(skew_x, 2))
    st.metric("Comunas ≥ 9 m²/hab", f"{n_oms} de {len(df_xy)}")

med_sector_x = df_xy.groupby("sector")["area_verde_m2_hab"].median().sort_values()
st.info(
    f"**Interpretación:** X también es **asimétrica a la derecha** (skew = {fmt_num(skew_x, 2)}; con las 44 comunas es "
    f"1,48), aunque menos que Y. La mediana es solo {fmt_num(x.median(), 1)} m²/hab y **apenas {n_oms} de {len(df_xy)} "
    f"comunas alcanzan el estándar OMS** de 9 m²/hab"
    + (f" ({', '.join(sobre_oms)})" if sobre_oms else "")
    + ". "
    + (f"Hay desigualdad entre sectores: la mediana va de {fmt_num(med_sector_x.iloc[0], 1)} m²/hab en "
       f"{med_sector_x.index[0]} a {fmt_num(med_sector_x.iloc[-1], 1)} m²/hab en {med_sector_x.index[-1]}. "
       if len(med_sector_x) > 1 else "")
    + "El déficit es generalizado, por lo que la variación de X entre comunas es limitada para explicar Y."
)

# ── VIZ 3: Y por sector (estática) ───────────────────────────
st.subheader("3. Tasa de Hurtos por Sector de la RM (Y ~ Categoría)")
orden_sector = df_filtrado.groupby("sector")["tasa_hurtos_100k"].median().sort_values(ascending=False).index.tolist()
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=df_filtrado, x="tasa_hurtos_100k", y="sector", hue="sector", order=orden_sector,
            palette=PALETA_SECTORES, legend=False, width=0.6, showfliers=False, ax=ax)
sns.stripplot(data=df_filtrado, x="tasa_hurtos_100k", y="sector", order=orden_sector, color="#222222",
              jitter=0.18, alpha=0.6, size=5, ax=ax)
for i, s in enumerate(orden_sector):
    med = df_filtrado.loc[df_filtrado["sector"] == s, "tasa_hurtos_100k"].median()
    ax.text(med, i - 0.36, f"Mediana: {fmt_num(med)}", ha="center", fontsize=8.5, color="#333333")
ax.set_xlabel("Tasa de hurtos por 100.000 hab.")
ax.set_ylabel("Sector")
ax.set_title("Distribución de Tasa de Hurtos por Sector – RM 2023", color="#2c5f2e", fontsize=13)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

med_sector_y = df_filtrado.groupby("sector")["tasa_hurtos_100k"].median().sort_values(ascending=False)
st.info(
    f"**Interpretación:** el sector **{med_sector_y.index[0]}** tiene la mediana más alta "
    f"({fmt_num(med_sector_y.iloc[0])} por 100k hab.)"
    + (f" y **{med_sector_y.index[-1]}** la más baja ({fmt_num(med_sector_y.iloc[-1])}). " if len(med_sector_y) > 1
       else ". ")
    + "Los sectores **Centro y Oriente** concentran la actividad comercial, financiera y de servicios (Santiago, "
      "Providencia, Las Condes, La Reina), lo que eleva la tasa; además el Centro muestra la mayor dispersión por los "
      "valores extremos de Providencia y Santiago. **Sur y Norte**, de carácter más residencial, tienen medianas más "
      "bajas. La ubicación geográfica, por tanto, es un factor de contexto relevante para Y."
)

# ── VIZ 4: Composición de espacios (estática) ────────────────
st.subheader("4. Composición de Espacios Públicos Catastrados (X ~ Categoría)")
plazas = int(df_xy["cantidad_plazas"].sum())
parques = int(df_xy["cantidad_parques"].sum())
total_esp = plazas + parques
sc1, sc2 = st.columns([1.2, 1])
with sc1:
    fig, ax = plt.subplots(figsize=(6, 3.5))
    barras = ax.barh(["Parques", "Plazas"], [parques, plazas], color=["#1e8449", "#a9dfbf"], edgecolor="#2c5f2e")
    for b, v in zip(barras, [parques, plazas]):
        ax.text(b.get_width() + total_esp * 0.01, b.get_y() + b.get_height() / 2,
                f"{fmt_num(v)} ({fmt_num(v / total_esp * 100, 1)}%)", va="center", fontsize=10)
    ax.set_xlim(0, plazas * 1.3)
    ax.set_xlabel("Cantidad de espacios")
    ax.set_title("Espacios catastrados por tipo – RM 2023", color="#2c5f2e")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
with sc2:
    st.info(
        f"**Interpretación:** el **{fmt_num(plazas / total_esp * 100, 1)}%** de los {fmt_num(total_esp)} espacios "
        f"catastrados son plazas y solo el {fmt_num(parques / total_esp * 100, 1)}% son parques. Por esto, medir por "
        "superficie (m²/hab) es más representativo que contar espacios: un gran parque aporta más área verde que "
        "decenas de plazas pequeñas, y es la superficie la que define la disponibilidad real de X."
    )

st.divider()

# ═════════════════════════════════════════════════════════════
# SECCIÓN 3.3 — RELACIONES ENTRE VARIABLES
# ═════════════════════════════════════════════════════════════
st.header("🔗 Sección 3.3 — Relaciones entre Variables")

# ── VIZ 5: Scatter X vs Y ────────────────────────────────────
st.subheader("5. Relación Áreas Verdes vs Tasa de Hurtos (X vs Y)")
r_pearson, p_valor = stats.pearsonr(df_xy["area_verde_m2_hab"], df_xy["tasa_hurtos_100k"])
r_spearman = df_xy[["area_verde_m2_hab", "tasa_hurtos_100k"]].corr(method="spearman").loc[
    "area_verde_m2_hab", "tasa_hurtos_100k"]
r_pobreza = df_xy["pct_pobreza"].corr(df_xy["tasa_hurtos_100k"])
fuerza, direccion = describir_r(r_pearson)

fig5 = px.scatter(
    df_xy, x="area_verde_m2_hab", y="tasa_hurtos_100k", color="sector", color_discrete_map=PALETA_SECTORES,
    size="poblacion", size_max=40, hover_name="comuna",
    hover_data={"area_verde_m2_hab": ":.1f", "tasa_hurtos_100k": ":.0f", "pct_pobreza": ":.1f",
                "poblacion": ":,"},
    trendline="ols", trendline_scope="overall", trendline_color_override=COLOR_Y,
    labels={"area_verde_m2_hab": "Área verde (m²/hab)", "tasa_hurtos_100k": "Tasa de hurtos (por 100.000 hab.)",
            "pct_pobreza": "Pobreza (%)", "poblacion": "Población", "sector": "Sector"},
    title=f"Relación entre Área Verde (m²/hab) y Tasa de Hurtos – {len(df_xy)} comunas RM 2023",
)
fig5.for_each_trace(lambda t: t.update(name="Tendencia lineal (MCO)") if t.mode == "lines" else None)
fig5.add_vline(x=OMS, line_dash="dash", line_color=COLOR_CTX, annotation_text="OMS: 9 m²/hab",
               annotation_position="bottom right")
y_max = df_xy["tasa_hurtos_100k"].max() * 1.08
x_max = max(df_xy["area_verde_m2_hab"].max() * 1.05, OMS + 1)
fig5.add_shape(type="rect", x0=OMS, x1=x_max, y0=800, y1=y_max, fillcolor="rgba(192,57,43,0.05)",
               line=dict(color="rgba(192,57,43,0.3)", dash="dot"), layer="below")
fig5.add_annotation(x=(OMS + x_max) / 2, y=y_max, yanchor="top", text="Zona comercial alta", showarrow=False,
                    font=dict(color=COLOR_Y, size=12))
fig5.add_annotation(xref="paper", yref="paper", x=0.01, y=0.99, xanchor="left", yanchor="top", showarrow=False,
                    align="left", text=f"r de Pearson = {r_pearson:.3f}<br>p-valor = {p_valor:.3f}",
                    bgcolor="rgba(244,249,244,0.9)", bordercolor="#2c5f2e", borderwidth=1)
fig5.update_layout(height=520, template="plotly_white", legend_title="Sector")
mostrar_plotly(fig5)

col_corr, col_interp = st.columns([1, 2.5])
with col_corr:
    st.metric("Pearson r", f"{r_pearson:.3f}", f"{direccion} {fuerza}",
              delta_color="normal" if r_pearson > 0 else "inverse")
    st.metric("Spearman ρ", f"{r_spearman:.3f}")
    st.metric("Pobreza ↔ Hurtos (r)", f"{r_pobreza:.3f}")
with col_interp:
    st.warning(
        f"**Interpretación — la paradoja:** la correlación es **{direccion} y {fuerza}** (r = {r_pearson:.3f}, "
        f"p = {p_valor:.3f}): en apariencia, más áreas verdes se asocian a **más** hurtos, lo contrario a la hipótesis "
        f"de prevención situacional. Con Spearman (ρ = {r_spearman:.3f}) la relación se debilita, señal de que "
        "depende de pocas comunas extremas (zona sombreada: comunas sobre el estándar OMS y con tasa > 800). "
        f"La clave es la **pobreza**: se correlaciona negativamente con los hurtos (r = {r_pobreza:.3f}) y también con "
        "las áreas verdes. Las comunas de altos ingresos tienen más áreas verdes **y** más comercio, población "
        "flotante y denuncia, por lo que la pobreza actúa como **variable de confusión** y la relación X–Y no es causal."
    )

# ── VIZ 6: Boxplot Y por tercil de X ─────────────────────────
st.subheader("6. ¿Cambia la Tasa de Hurtos según la Dotación de Área Verde?")
q33, q67 = df_xy["area_verde_m2_hab"].quantile([1 / 3, 2 / 3])
etiquetas = [f"Baja (< {fmt_num(q33, 1)} m²/hab)", f"Media ({fmt_num(q33, 1)}–{fmt_num(q67, 1)} m²/hab)",
             f"Alta (> {fmt_num(q67, 1)} m²/hab)"]
df_box = df_xy.copy()
df_box["categoria_av"] = pd.qcut(df_box["area_verde_m2_hab"].rank(method="first"), q=3, labels=etiquetas)
fig6 = px.box(
    df_box, x="categoria_av", y="tasa_hurtos_100k", color="categoria_av",
    color_discrete_map=dict(zip(etiquetas, ["#d73027", "#f1c40f", "#1a9850"])),
    category_orders={"categoria_av": etiquetas}, points="all", hover_name="comuna",
    hover_data={"area_verde_m2_hab": ":.1f", "categoria_av": False},
    labels={"categoria_av": "Nivel de área verde (terciles)", "tasa_hurtos_100k": "Tasa de hurtos (por 100.000 hab.)",
            "area_verde_m2_hab": "Área verde (m²/hab)"},
    title="Distribución de Tasa de Hurtos por Nivel de Área Verde",
)
fig6.update_layout(height=450, template="plotly_white", showlegend=False)
mostrar_plotly(fig6)

meds = df_box.groupby("categoria_av", observed=True)["tasa_hurtos_100k"].median().reindex(etiquetas)
grupos = [g["tasa_hurtos_100k"].values for _, g in df_box.groupby("categoria_av", observed=True)]
kw_h, kw_p = stats.kruskal(*grupos)
st.info(
    f"**Interpretación:** las medianas por tercil son Baja = {fmt_num(meds.iloc[0])}, Media = {fmt_num(meds.iloc[1])} "
    f"y Alta = {fmt_num(meds.iloc[2])} hurtos por 100k hab. La prueba de Kruskal-Wallis (H = {fmt_num(kw_h, 2)}, "
    f"p = {fmt_num(kw_p, 3)}) indica que las diferencias **{'son' if kw_p < 0.05 else 'no son'} estadísticamente "
    "significativas**. La diferencia entre grupos no es tan clara como sugiere el coeficiente de Pearson: hay gran "
    "superposición entre las cajas y el tercil alto está influido por comunas comerciales de altos ingresos. Esto "
    "vuelve a apuntar a la pobreza (y la centralidad comercial) como factor de confusión."
)

# ── VIZ 7: Scatter con pobreza (estática) ────────────────────
st.subheader("7. Relación X vs Y codificada por Nivel de Pobreza Comunal")
fig, ax = plt.subplots(figsize=(10, 6))
sc = ax.scatter(df_xy["area_verde_m2_hab"], df_xy["tasa_hurtos_100k"], c=df_xy["pct_pobreza"], cmap="viridis_r",
                s=90, edgecolors="black", alpha=0.85)
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label("% Pobreza por Ingresos (SAE 2023)")
m, b = np.polyfit(df_xy["area_verde_m2_hab"], df_xy["tasa_hurtos_100k"], 1)
xr = np.linspace(df_xy["area_verde_m2_hab"].min(), df_xy["area_verde_m2_hab"].max(), 100)
ax.plot(xr, m * xr + b, linestyle="--", color=COLOR_Y, linewidth=2, label=f"Tendencia lineal (r = {r_pearson:.2f})")
ax.axvline(OMS, color="gray", linestyle=":", linewidth=1.5, label="Estándar OMS (9 m²/hab)")
for com in ["Providencia", "Santiago", "Vitacura", "La Pintana", "Cerro Navia", "Las Condes", "Cerrillos",
            "Lo Barnechea"]:
    fila = df_xy[df_xy["comuna"] == com]
    if not fila.empty:
        ax.annotate(com, (fila["area_verde_m2_hab"].iloc[0], fila["tasa_hurtos_100k"].iloc[0]),
                    textcoords="offset points", xytext=(6, 5), fontsize=8.5,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="gray"))
ax.set_xlabel("m² de áreas verdes por habitante (X)")
ax.set_ylabel("Tasa de hurtos por 100.000 hab. (Y)")
ax.set_title("Áreas verdes vs hurtos, coloreado por % de pobreza – RM 2023", color="#2c5f2e", fontsize=13)
ax.legend(loc="upper left", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(linestyle=":", alpha=0.5)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.info(
    "**Interpretación — tres grupos:** (1) **Polos comerciales** (Providencia, Santiago, Estación Central): tasas "
    "extremas por población flotante, con cualquier nivel de área verde. (2) **Sector oriente de altos ingresos** "
    "(Vitacura, Las Condes, Lo Barnechea, La Reina): colores oscuros (baja pobreza), más área verde y tasas medias-altas. "
    "(3) **Periferia vulnerable** (La Pintana, Cerro Navia, Lo Espejo): colores claros (alta pobreza), poca área verde "
    "y tasas bajas de hurtos denunciados. Como la pobreza ordena a la vez X e Y, **es la variable de confusión que "
    "explica la paradoja**: la correlación positiva X–Y refleja el gradiente socioeconómico más que un efecto de las "
    "áreas verdes. Cerrillos es una excepción interesante: mucha área verde y pobreza media con tasa alta."
)

# ── VIZ 8: Serie mensual ─────────────────────────────────────
st.subheader("8. Evolución Mensual de Hurtos en la RM – 2023 (Componente T)")
if df_mensual is None:
    st.warning("No se encontró `rm_hurtos_mensuales_2023.csv`; se omite la serie mensual.")
else:
    top10 = df_mensual.groupby("comuna")["hurtos"].sum().nlargest(10).index.tolist()
    c_ctrl, c_graf = st.columns([1, 3.2])
    with c_ctrl:
        seleccion = st.multiselect("Comunas a visualizar", ["Total RM"] + top10, default=["Total RM"],
                                   help="Las 10 comunas con más hurtos anuales en 2023.")
        escala = st.radio("Eje Y", ["Escala lineal", "Escala logarítmica"],
                          help="La escala logarítmica permite comparar comunas con volúmenes muy distintos.")
    total_rm = df_mensual.groupby("mes")["hurtos"].sum()
    fig8 = go.Figure()
    if "Total RM" in seleccion:
        fig8.add_trace(go.Scatter(x=MESES_ES, y=total_rm.values, mode="lines+markers", name="Total RM",
                                  line=dict(color="#1f4e9c", width=4), marker=dict(size=8),
                                  hovertemplate="%{x}: %{y:,.0f} hurtos<extra>Total RM</extra>"))
    colores = px.colors.qualitative.Set2 + px.colors.qualitative.Dark2
    for i, com in enumerate([c for c in seleccion if c != "Total RM"]):
        serie = df_mensual[df_mensual["comuna"] == com].sort_values("mes")
        fig8.add_trace(go.Scatter(x=[MESES_ES[m - 1] for m in serie["mes"]], y=serie["hurtos"],
                                  mode="lines+markers", name=com, line=dict(width=2, color=colores[i % len(colores)]),
                                  hovertemplate="%{x}: %{y:,.0f} hurtos<extra>" + com + "</extra>"))
    fig8.update_layout(title="Evolución Mensual de Hurtos – RM 2023", height=420, template="plotly_white",
                       xaxis_title="Mes (2023)", yaxis_title="Casos de hurtos", legend_title="Serie",
                       separators=",.")
    fig8.update_xaxes(categoryorder="array", categoryarray=MESES_ES)
    if escala == "Escala logarítmica":
        fig8.update_yaxes(type="log")
    with c_graf:
        if seleccion:
            mostrar_plotly(fig8)
        else:
            st.warning("Selecciona al menos una serie para visualizar.")

    mes_max, mes_min = MESES_ES[total_rm.idxmax() - 1], MESES_ES[total_rm.idxmin() - 1]
    cv = total_rm.std() / total_rm.mean() * 100
    dic_vs_prom = (total_rm.loc[12] / total_rm.mean() - 1) * 100
    st.info(
        f"**Interpretación:** en la RM se registraron en promedio {fmt_num(total_rm.mean())} hurtos mensuales. El mes con "
        f"más casos fue **{mes_max}** ({fmt_num(total_rm.max())}) y el con menos, **{mes_min}** ({fmt_num(total_rm.min())})."
        f" Diciembre se ubicó un {fmt_num(abs(dic_vs_prom), 1)}% {'sobre' if dic_vs_prom > 0 else 'bajo'} el promedio, "
        "coherente con la mayor actividad comercial de fin de año. La variación mensual es moderada "
        f"(coeficiente de variación ≈ {fmt_num(cv)}%) y las comunas mantienen su orden relativo durante todo el año, "
        "por lo que el **total anual 2023 es una medida representativa** de cada comuna para responder la pregunta."
    )

st.divider()

# ═════════════════════════════════════════════════════════════
# SÍNTESIS
# ═════════════════════════════════════════════════════════════
st.header("💡 Síntesis del EDA")
with st.expander("Ver síntesis completa", expanded=True):
    st.markdown(
        f"""
**Hallazgos univariados**
- **Y (tasa de hurtos)** es muy asimétrica (skew = 3,44 con las 52 comunas): pocas comunas comerciales
  —Providencia, Estación Central, Santiago, La Reina y Cerrillos— concentran tasas extremas.
- **X (m²/hab)** es menos asimétrica (skew = 1,48), pero con déficit generalizado: solo **7 de 44** comunas superan
  el estándar OMS de 9 m²/hab.
- El 92,5% de los espacios catastrados son plazas, por lo que la superficie es mejor medida que el conteo.

**Hallazgos de relaciones**
- Correlación **positiva débil-moderada** entre X e Y (r = 0,371 con las 44 comunas; con los filtros actuales
  r = {r_pearson:.3f}). Spearman es más débil (ρ ≈ 0,23), señal de dependencia de casos extremos.
- **Paradoja explicada por la pobreza:** la pobreza se asocia negativamente con los hurtos (r = −0,517) y con las
  áreas verdes; las comunas ricas tienen más verde, más comercio y más denuncias.

**Limitaciones**
- El catastro MINVU solo cubre 44 de 52 comunas (las rurales quedan fuera del análisis X–Y).
- La tasa se calcula con población **residente**, no flotante, lo que infla los polos comerciales.
- Los hurtos registrados dependen de la propensión a denunciar.

**Conexión con la pregunta**
> La correlación positiva aparente (r = 0,371) no implica causalidad; la pobreza es la variable de confusión que
> explica el patrón.
"""
    )

st.divider()
st.caption("EIN092B Visualización | Avance 2 – 2026-II | Fuentes: CEAD, MINVU/INE, SAE")
