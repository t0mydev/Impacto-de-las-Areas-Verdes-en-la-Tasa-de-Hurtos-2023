# Áreas Verdes y Hurtos en la Región Metropolitana (2023)

**Asignatura:** EIN092B — Visualización de Datos  
**Avance 2 — Semestre 2026-II**  
**Profesor:** Jesús A. Parra  
**Equipo:** Vicente Paredes · Tomás Armijo · Francisca Matamala

---

## Pregunta de Investigación

¿Existe una relación entre la disponibilidad de áreas verdes (m² por habitante) y la tasa de hurtos (por 100.000 habitantes) en las 52 comunas de la Región Metropolitana durante 2023?

**Variables:**  
- **Y (objetivo):** Tasa de hurtos por 100.000 habitantes (`tasa_hurtos_100k`)  
- **X (explicativa):** Metros cuadrados de áreas verdes por habitante (`area_verde_m2_hab`)  
- **T (contexto):** 52 comunas de la RM, año 2023

---

## Estructura del Repositorio

```
proyecto_viz/
├── app/
│   ├── app.py                          # Página de inicio de la aplicación Streamlit
│   └── pages/
│       ├── 1_Contexto_y_Datos.py       # Fuentes de datos y calidad (secciones 3.1-3.2)
│       ├── 2_EDA.py                    # Análisis exploratorio univariado y bivariado
│       └── 3_Analisis_de_la_Pregunta.py # Correlación, mapa, series y regresión
├── data/
│   ├── raw/                            # Datos originales sin modificar
│   └── processed/                      # Datos procesados listos para análisis
│       ├── rm_comunas_2023.csv         # Tabla comunal consolidada (52 filas × 15 cols)
│       └── rm_hurtos_mensuales_2023.csv # Serie mensual de hurtos (624 filas)
├── figures/                            # Figuras estáticas exportadas (9 archivos PNG)
├── notebooks/
│   ├── estructura_y_calidad_datos.ipynb # Sección 3.1: Estructura y calidad de datos
│   └── analisis_exploratorio.ipynb      # Secciones 3.2-3.3: EDA completo
├── scripts/
│   └── build_dataset.py                # Script de construcción del dataset procesado
├── requirements.txt                    # Dependencias Python
└── README.md                           # Este archivo
```

---

## Fuentes de Datos

| Dataset | Fuente | Filas | Período |
|---------|--------|-------|---------|
| Catastro Áreas Verdes | IDE MINVU – INE | 18.173 | 2022-2023 |
| Registros delictuales | CEAD – Subsec. Prevención del Delito | 1.987.200 | 2001-2023 |
| Demografía y pobreza | SAE – Min. Desarrollo Social | 346 | 2023 |

---

## Instalación y Uso

### Requisitos
- Python 3.10+
- Las dependencias listadas en `requirements.txt`

### Pasos

```bash
# 1. Clonar el repositorio
git clone <url_repositorio>
cd proyecto_viz

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación Streamlit
streamlit run app/app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

### Ejecutar notebooks

```bash
# Abrir Jupyter desde la raíz del proyecto
jupyter notebook
# Navegar a notebooks/ y abrir en orden:
# 1. estructura_y_calidad_datos.ipynb
# 2. analisis_exploratorio.ipynb
```

---

## Hallazgos Principales

1. **Correlación positiva débil-moderada** (Pearson r = 0,371; p = 0,013) entre m²/hab de áreas verdes y tasa de hurtos.  
2. **Resultado contraintuitivo** explicado por variables confundidoras: comunas de ingresos altos tienen más áreas verdes *y* más hurtos por actividad comercial y población flotante.  
3. **La pobreza es el principal predictor negativo** (r = −0,517): las comunas más pobres presentan menores tasas de hurto, no mayores.  
4. **Alta concentración:** 5 comunas explican el 45,3% de todos los hurtos de la RM (Providencia, Santiago, Estación Central, La Reina, Cerrillos).  
5. **Sin catastro MINVU:** 8 comunas rurales quedan fuera del análisis de áreas verdes (Tiltil, Calera de Tango, Paine, Curacaví, María Pinto, San Pedro, El Monte, Isla de Maipo).

---

## Descripción de las Páginas Streamlit

| Página | Propósito |
|--------|-----------|
| **🏠 Inicio** | Presentación del proyecto, equipo y navegación guiada |
| **📋 Contexto y Datos** | Cobertura geográfica, calidad de datos y diccionario de variables |
| **📊 EDA** | Distribuciones, relaciones bivariadas y análisis multivariado |
| **🔍 Análisis de la Pregunta** | Correlación, mapa choropleth, serie temporal y regresión |

---

## Dependencias Principales

```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
scipy>=1.11.0
statsmodels>=0.14.0
```

Ver `requirements.txt` para la lista completa con todas las versiones fijadas.
