"""Agrega las celdas faltantes a los notebooks del Avance 2 (sección 3.1 y 3.3)."""
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPLOADS = Path("/home/ubuntu/Uploads")
OUT = ROOT / "notebooks"


def lines(text):
    text = text.strip("\n")
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]


def code(text, with_id):
    cell = {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": lines(text)}
    if with_id:
        cell["id"] = uuid.uuid4().hex[:8]
    return cell


def md(text, with_id):
    cell = {"cell_type": "markdown", "metadata": {}, "source": lines(text)}
    if with_id:
        cell["id"] = uuid.uuid4().hex[:8]
    return cell


# ───────────────────────── 4A ─────────────────────────
AUDIT_CODE = '''
# Auditoría por dataset: tipos de variables, valores faltantes y duplicados
print("="*60)
print("AUDITORÍA: DATASET ÁREAS VERDES (MINVU) — post-limpieza")
print("="*60)
print(f"Forma: {df_av_comunal.shape[0]} filas, {df_av_comunal.shape[1]} columnas")
print("\\nTipos de variables:")
print(df_av_comunal.dtypes)
print("\\nValores faltantes:")
print(df_av_comunal.isnull().sum())
print(f"\\nRegistros duplicados: {df_av_comunal.duplicated().sum()}")

print("\\n" + "="*60)
print("AUDITORÍA: DATASET CEAD (Hurtos) — post-filtro 2023 RM")
print("="*60)
print(f"Forma: {df_hurtos_comunal.shape[0]} filas, {df_hurtos_comunal.shape[1]} columnas")
print("\\nTipos de variables:")
print(df_hurtos_comunal.dtypes)
print("\\nValores faltantes:")
print(df_hurtos_comunal.isnull().sum())
print(f"Registros duplicados: {df_hurtos_comunal.duplicated().sum()}")

print("\\n" + "="*60)
print("AUDITORÍA: DATASET SAE (Población) — 52 comunas RM")
print("="*60)
print(f"Forma: {df_sae_clean.shape[0]} filas, {df_sae_clean.shape[1]} columnas")
print("\\nTipos de variables:")
print(df_sae_clean.dtypes)
print("\\nValores faltantes:")
print(df_sae_clean.isnull().sum())
print(f"Registros duplicados: {df_sae_clean.duplicated().sum()}")
'''

AUDIT_MD = '''
### 🔍 Síntesis de Auditoría de Calidad

| Dataset | Filas | Variables | Faltantes | Duplicados |
|---------|-------|-----------|-----------|------------|
| MINVU (áreas verdes) | 44 comunas | 5 | Ninguno | Ninguno |
| CEAD (hurtos) | 52 comunas | 2 | Ninguno | Ninguno |
| SAE (población) | 52 comunas | 4 | Ninguno | Ninguno |

**Tipos de variables identificados:**
- **Numéricas continuas:** m2_areas_verdes, m2_areas_verdes_per_capita, tasa_hurtos_100k, poblacion, pct_pobreza
- **Numéricas discretas:** total_hurtos_2023, cantidad_plazas, cantidad_parques, cantidad_espacios_publicos
- **Binaria:** tiene_catastro_minvu
- **Identificador:** CUT (clave territorial)
- **Nominal:** comuna

**Decisión:** No se encontraron registros duplicados en ninguna de las 3 fuentes. Los valores faltantes en áreas verdes (8 comunas sin catastro MINVU) se tratan como NaN justificado.
'''

# ───────────────────────── 4B ─────────────────────────
B_MD1 = '''
---
## 8. Análisis complementario de la Sección 3.3

### 8.1 Diferencias de Y entre grupos categóricos (Sector geográfico)
Se analiza si la tasa de hurtos varía significativamente entre los sectores de la RM.
'''

B_CODE1 = '''
import matplotlib.pyplot as plt
import seaborn as sns

# El dataset consolidado no trae el sector geográfico: se incorpora desde el dataset procesado de la app
if 'sector' not in df.columns:
    df_sectores = pd.read_csv(os.path.join('..', 'data', 'processed', 'rm_comunas_2023.csv'),
                              usecols=['cut', 'sector'])
    df = df.merge(df_sectores, left_on='CUT', right_on='cut', how='left').drop(columns='cut')
    print(f"Sector incorporado. Comunas sin sector: {df['sector'].isna().sum()}")

# Paleta consistente por sector
paleta_sectores = {
    'Centro': '#1b4332',
    'Norte': '#40916c',
    'Oriente': '#74c69d',
    'Poniente': '#b7e4c7',
    'Sur': '#95a83f'
}

# Ordenar sectores por mediana
orden_sector = (df.groupby('sector')['tasa_hurtos_100k']
                .median()
                .sort_values(ascending=False)
                .index.tolist())

fig, ax = plt.subplots(figsize=(10, 5))

# Boxplot
sns.boxplot(data=df, x='tasa_hurtos_100k', y='sector', hue='sector', legend=False,
            order=orden_sector, palette=paleta_sectores,
            orient='h', width=0.6, ax=ax,
            flierprops=dict(marker='o', markersize=5, alpha=0.5))

# Puntos individuales (stripplot)
sns.stripplot(data=df, x='tasa_hurtos_100k', y='sector',
              order=orden_sector, color='#222222',
              orient='h', size=5, alpha=0.7, jitter=True, ax=ax)

ax.set_xlabel('Tasa de hurtos por 100.000 habitantes (2023)', fontsize=11)
ax.set_ylabel('Sector de la RM', fontsize=11)
ax.set_title('Distribución de la Tasa de Hurtos por Sector – RM 2023', fontsize=13, fontweight='bold')
ax.grid(axis='x', linestyle=':', alpha=0.6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Anotar medianas
for i, sector in enumerate(orden_sector):
    mediana = df[df['sector'] == sector]['tasa_hurtos_100k'].median()
    ax.text(mediana + 20, i - 0.35, f'{mediana:.0f}', va='center', fontsize=9, color='black', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'hurtos_por_sector.png'), dpi=150, bbox_inches='tight')
plt.show()

# Estadísticas por sector
print("Estadísticas de tasa_hurtos_100k por sector:")
print(df.groupby('sector')['tasa_hurtos_100k'].agg(['median','mean','std','count']).round(1))
'''

B_MD2 = '''
### 🔍 Interpretación de Y por Sector

- **Visualización:** Boxplot horizontal por sector con puntos individuales.
- **Observación:** El sector **Oriente** presenta la mediana más alta (≈ 705 hurtos por 100k hab), explicada por Las Condes, Vitacura y La Reina. El sector **Centro** tiene una mediana similar (≈ 628) pero la **media más alta (≈ 1.076)** y la mayor dispersión, impulsada por Providencia (2.795) y Santiago (1.468), polos de actividad comercial y turística. En el sector Poniente, Estación Central (1.481) y Cerrillos (981) aparecen como valores extremos de su grupo. Los sectores **Sur** (≈ 287) y **Norte** (≈ 264) muestran las medianas más bajas.
- **Interpretación:** Las diferencias entre sectores reflejan más la concentración de actividad comercial y de servicios que la disponibilidad de áreas verdes. El sector Oriente, con alta dotación de áreas verdes y bajo índice de pobreza, tiene tasas moderadas-altas por la misma razón.
- **Conexión con la pregunta:** Las diferencias sectoriales sugieren que la ubicación geográfica y la densidad comercial median la relación entre áreas verdes y hurtos, reforzando la necesidad de controlar por estas variables.
'''

B_MD3 = '''
### 8.2 Exploración de relación no lineal entre X e Y
Dado que ambas variables son asimétricas (skew Y=3.44, skew X=1.48), se evalúa si una transformación logarítmica mejora la visualización de la relación lineal.
'''

B_CODE2 = '''
import numpy as np
from scipy import stats

# Filtrar comunas con catastro y valores positivos para el log
df_log = df_cat.copy()
df_log['log_x'] = np.log(df_log['m2_areas_verdes_per_capita'])
df_log['log_y'] = np.log(df_log['tasa_hurtos_100k'])

# Correlaciones transformadas
r_log, p_log = stats.pearsonr(df_log['log_x'], df_log['log_y'])
print(f"Correlación Pearson en escala logarítmica: r = {r_log:.3f}, p = {p_log:.3f}")
print(f"Comparación: escala original r = {r_pearson:.3f}, log-log r = {r_log:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Panel izquierdo: escala original
axes[0].scatter(df_cat['m2_areas_verdes_per_capita'], df_cat['tasa_hurtos_100k'],
                alpha=0.75, edgecolors='black', s=55, color='steelblue')
m, b = np.polyfit(df_cat['m2_areas_verdes_per_capita'], df_cat['tasa_hurtos_100k'], 1)
xr = np.linspace(df_cat['m2_areas_verdes_per_capita'].min(), df_cat['m2_areas_verdes_per_capita'].max(), 100)
axes[0].plot(xr, m*xr + b, 'r--', linewidth=2)
axes[0].set_title(f'Escala original (r = {r_pearson:.3f})', fontsize=12, fontweight='bold')
axes[0].set_xlabel('m² de áreas verdes por habitante (X)')
axes[0].set_ylabel('Tasa de hurtos por 100k hab. (Y)')
axes[0].grid(linestyle=':', alpha=0.6)
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)

# Panel derecho: escala log-log
axes[1].scatter(df_log['log_x'], df_log['log_y'],
                alpha=0.75, edgecolors='black', s=55, color='#27ae60')
m2, b2 = np.polyfit(df_log['log_x'], df_log['log_y'], 1)
xr2 = np.linspace(df_log['log_x'].min(), df_log['log_x'].max(), 100)
axes[1].plot(xr2, m2*xr2 + b2, 'r--', linewidth=2)
axes[1].set_title(f'Escala log-log (r = {r_log:.3f})', fontsize=12, fontweight='bold')
axes[1].set_xlabel('log(m² de áreas verdes por habitante)')
axes[1].set_ylabel('log(Tasa de hurtos por 100k hab.)')
axes[1].grid(linestyle=':', alpha=0.6)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)

# Anotar comunas clave en log-log
destacadas_log = ['Providencia', 'Santiago', 'Vitacura', 'La Pintana', 'Cerrillos', 'Pirque', 'San José De Maipo']
for com in destacadas_log:
    sub = df_log[df_log['comuna'] == com]
    if len(sub) > 0:
        axes[1].annotate(com, (sub['log_x'].values[0], sub['log_y'].values[0]),
                         textcoords='offset points', xytext=(5, 3), fontsize=8,
                         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray'))

plt.suptitle('Comparación de Relación X vs Y: Escala Original vs Logarítmica',
             fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'relacion_log_vs_original.png'), dpi=150, bbox_inches='tight')
plt.show()
'''

B_MD4 = '''
### 🔍 Interpretación de la relación no lineal

- **Visualización:** Comparación de la relación X vs Y en escala original y escala logarítmica (log-log).
- **Observación:** La correlación en escala log-log es **r = 0,318** (p = 0,035), algo menor que la original (r = 0,371). En escala logarítmica los outliers comerciales pierden peso, pero aparecen como extremos a la izquierda Pirque y San José de Maipo (menos de 0,2 m²/hab catastrados). La nube de puntos mantiene una dispersión alta en ambas escalas, por lo que la relación **no mejora con la transformación logarítmica**.
- **Interpretación:** La relación entre áreas verdes y hurtos no sigue un patrón no lineal claro. La dispersión alta y la presencia de outliers comerciales (Providencia, Santiago) dominan el patrón en escala original. Esto confirma que la correlación observada está mediada por variables de confusión (nivel socioeconómico, actividad comercial) más que por una relación funcional directa entre X e Y.
- **Decisión:** Para el análisis principal se mantiene la escala original con la correlación de Pearson como medida, complementada con Spearman (ρ = 0,228) para robustez ante la asimetría.
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    nb1 = json.loads((UPLOADS / "estructura_y_calidad_datos.ipynb").read_text(encoding="utf-8"))
    ids1 = any("id" in c for c in nb1["cells"])
    # Celda 10 = encabezado "## 5. Auditoría de Calidad", celda 11 = describe(): se inserta entre ambas
    idx = next(i for i, c in enumerate(nb1["cells"]) if "describe()" in "".join(c["source"]))
    nb1["cells"][idx:idx] = [code(AUDIT_CODE, ids1), md(AUDIT_MD, ids1)]
    # Bug preexistente: groupby sobre 'comuna' categórica genera producto cartesiano sin observed=True
    for c in nb1["cells"]:
        s = "".join(c["source"])
        old = "groupby(['cut_comuna', 'comuna', 'fecha'], as_index=False)"
        if old in s:
            c["source"] = s.replace(old, old[:-1] + ", observed=True)").splitlines(keepends=True)
    (OUT / "estructura_y_calidad_datos.ipynb").write_text(
        json.dumps(nb1, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    nb2 = json.loads((UPLOADS / "analisis_exploratorio.ipynb").read_text(encoding="utf-8"))
    ids2 = any("id" in c for c in nb2["cells"])
    nb2["cells"].extend([md(B_MD1, ids2), code(B_CODE1, ids2), md(B_MD2, ids2), md(B_MD3, ids2),
                         code(B_CODE2, ids2), md(B_MD4, ids2)])
    (OUT / "analisis_exploratorio.ipynb").write_text(
        json.dumps(nb2, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"NB1: {len(nb1['cells'])} celdas (auditoría en índice {idx}) | NB2: {len(nb2['cells'])} celdas")


if __name__ == "__main__":
    main()
