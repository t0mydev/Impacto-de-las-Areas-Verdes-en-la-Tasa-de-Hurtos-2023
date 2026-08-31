# Impacto-de-las-Areas-Verdes-en-la-Tasa-de-Hurtos-2023

## Integrantes
- Vicente Paredes
- Francisca Matamala
- Tomás Armijo

## Problemática General
El diseño urbano y la distribución de los espacios públicos impactan directamente en la calidad de vida de las ciudades. Existe un debate continuo en el marco de las *Smart Cities* sobre si una mayor superficie de áreas verdes fomenta la cohesión social (actuando como disuasivo para la delincuencia) o si, por el contrario, genera zonas de vulnerabilidad.

## Motivación
Comprender cómo interactúa el entorno urbano con la seguridad ciudadana es clave para la planificación. Nos motiva abordar este desafío estructurando un análisis de datos sólido, apoyado en distribuciones estadísticas. El objetivo es transformar registros en crudo en evidencia visual que aporte valor analítico a las políticas de urbanismo, evaluando empíricamente estas relaciones a nivel de arquitectura urbana.

## Pregunta Inicial
¿Existe correlación entre los metros cuadrados de áreas verdes y la tasa de hurtos en las comunas de la Región Metropolitana durante el año 2023?

## Alcance
- **Fenómeno específico:** Relación espacial entre la superficie total de áreas verdes públicas y la cantidad de hurtos.
- **Población/Región:** Comunas de la Región Metropolitana de Santiago.
- **Unidad de observación:** La comuna.
- **Periodo temporal:** Año 2023.

## Fuente de los Datasets
1. **Áreas Verdes:** Catastro de Áreas Verdes (Minvu/INE).
2. **Hurtos:** Centro de Estudios y Análisis del Delito (CEAD).
*(Nota: Por restricciones de distribución y tamaño, los datos originales no están alojados en este repositorio. Las instrucciones de obtención se encuentran en la carpeta `data/`).*

## Breve Descripción de los Datos
- **Dataset Áreas Verdes (`Areas_Verdes_Minvu_INE.csv`):** Contiene 18.173 observaciones a nivel nacional correspondientes a espacios públicos. Posee variables categóricas y numéricas (como la superficie en metros cuadrados, la comuna y la región). Para este proyecto, se aislará únicamente la información de la `METROPOLITANA DE SANTIAGO`.
- **Dataset Delincuencia (`cead_delincuencia_chile.parquet`):** Contiene el detalle de ilícitos registrados clasificados por fecha, región y comuna. Esta granularidad permitirá cruzar los reportes policiales (hurtos) con la disponibilidad espacial de áreas verdes.

## Estructura General del Repositorio
- `data/raw/`: Datos originales sin modificar.
- `data/processed/`: Datos generados luego de la limpieza y transformación (filtrado por RM y 2023).
- `notebooks/`: Cuadernos de exploración, limpieza, análisis y pruebas estadísticas de correlación.
- `src/`: Funciones y código reutilizable.
- `figures/`: Gráficos y recursos visuales.
- `app/`: Aplicación Streamlit u otros componentes del producto final interactivo.
