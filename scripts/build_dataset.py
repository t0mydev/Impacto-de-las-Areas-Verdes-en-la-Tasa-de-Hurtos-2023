"""Construye data/processed/rm_comunas_2023.csv a partir de los datos reales del proyecto.

Fuentes (data/raw):
- comunas_rm_consolidado_2023.csv : población, pobreza (SAE), m² áreas verdes (MINVU-INE), hurtos 2023 (CEAD)
- hurtos_mensuales_rm_2023.csv    : hurtos mensuales 2023 por comuna (CEAD)

Se agregan atributos de contexto espacial: sector, centroide aproximado y clasificación de zona.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# CUT: (sector, lat, lon, clasificacion_zona)
CONTEXTO = {
    13101: ("Centro", -33.4489, -70.6693, "Urbano_denso"),   # Santiago
    13102: ("Poniente", -33.4972, -70.7219, "Urbano"),       # Cerrillos
    13103: ("Poniente", -33.4316, -70.7434, "Urbano_denso"), # Cerro Navia
    13104: ("Norte", -33.3811, -70.6689, "Urbano_denso"),    # Conchalí
    13105: ("Sur", -33.5710, -70.6699, "Urbano_denso"),      # El Bosque
    13106: ("Poniente", -33.4611, -70.6944, "Urbano_denso"), # Estación Central
    13107: ("Norte", -33.3600, -70.6500, "Urbano"),          # Huechuraba
    13108: ("Norte", -33.4188, -70.6594, "Urbano_denso"),    # Independencia
    13109: ("Sur", -33.5300, -70.6640, "Urbano_denso"),      # La Cisterna
    13110: ("Oriente", -33.5230, -70.5929, "Urbano"),        # La Florida
    13111: ("Sur", -33.5346, -70.6202, "Urbano_denso"),      # La Granja
    13112: ("Sur", -33.5757, -70.6282, "Urbano"),            # La Pintana
    13113: ("Oriente", -33.4532, -70.5438, "Urbano"),        # La Reina
    13114: ("Oriente", -33.4117, -70.5794, "Urbano"),        # Las Condes
    13115: ("Oriente", -33.3550, -70.5200, "Periurbano"),    # Lo Barnechea
    13116: ("Sur", -33.5200, -70.6922, "Urbano_denso"),      # Lo Espejo
    13117: ("Poniente", -33.4517, -70.7308, "Urbano_denso"), # Lo Prado
    13118: ("Centro", -33.4933, -70.5981, "Urbano_denso"),   # Macul
    13119: ("Poniente", -33.5100, -70.7600, "Urbano"),       # Maipú
    13120: ("Centro", -33.4561, -70.6003, "Urbano_denso"),   # Ñuñoa
    13121: ("Sur", -33.4973, -70.6706, "Urbano_denso"),      # Pedro Aguirre Cerda
    13122: ("Oriente", -33.4897, -70.5339, "Urbano"),        # Peñalolén
    13123: ("Centro", -33.4323, -70.6097, "Urbano_denso"),   # Providencia
    13124: ("Poniente", -33.4400, -70.7833, "Urbano"),       # Pudahuel
    13125: ("Norte", -33.3593, -70.7269, "Urbano"),          # Quilicura
    13126: ("Poniente", -33.4370, -70.7050, "Urbano_denso"), # Quinta Normal
    13127: ("Norte", -33.4136, -70.6469, "Urbano_denso"),    # Recoleta
    13128: ("Norte", -33.3997, -70.7261, "Urbano_denso"),    # Renca
    13129: ("Centro", -33.4934, -70.6342, "Urbano_denso"),   # San Joaquín
    13130: ("Centro", -33.5007, -70.6486, "Urbano_denso"),   # San Miguel
    13131: ("Sur", -33.5404, -70.6455, "Urbano_denso"),      # San Ramón
    13132: ("Oriente", -33.3892, -70.5823, "Urbano"),        # Vitacura
    13201: ("Sur", -33.6100, -70.5773, "Urbano"),            # Puente Alto
    13202: ("Sur", -33.6370, -70.5590, "Rural"),             # Pirque
    13203: ("Oriente", -33.6440, -70.3520, "Rural"),         # San José de Maipo
    13301: ("Norte", -33.2027, -70.6730, "Periurbano"),      # Colina
    13302: ("Norte", -33.2890, -70.8980, "Rural"),           # Lampa
    13303: ("Norte", -33.0870, -70.9240, "Rural"),           # Tiltil
    13401: ("Sur", -33.5953, -70.7003, "Urbano"),            # San Bernardo
    13402: ("Sur", -33.7320, -70.7460, "Periurbano"),        # Buin
    13403: ("Sur", -33.6290, -70.7820, "Periurbano"),        # Calera de Tango
    13404: ("Sur", -33.8100, -70.7600, "Periurbano"),        # Paine
    13501: ("Poniente", -33.6890, -71.2130, "Rural"),        # Melipilla
    13502: ("Poniente", -34.0350, -71.0980, "Rural"),        # Alhué
    13503: ("Poniente", -33.4040, -71.1500, "Rural"),        # Curacaví
    13504: ("Poniente", -33.5150, -71.1200, "Rural"),        # María Pinto
    13505: ("Poniente", -33.8970, -71.4600, "Rural"),        # San Pedro
    13601: ("Poniente", -33.6640, -70.9260, "Periurbano"),   # Talagante
    13602: ("Poniente", -33.6800, -71.0170, "Periurbano"),   # El Monte
    13603: ("Poniente", -33.7520, -70.8870, "Periurbano"),   # Isla de Maipo
    13604: ("Poniente", -33.5600, -70.8230, "Periurbano"),   # Padre Hurtado
    13605: ("Poniente", -33.6110, -70.8900, "Periurbano"),   # Peñaflor
}

NOMBRES = {"San José De Maipo": "San José de Maipo", "Calera De Tango": "Calera de Tango",
           "Isla De Maipo": "Isla de Maipo"}


def main() -> None:
    src = pd.read_csv(RAW / "comunas_rm_consolidado_2023.csv")
    faltantes = set(src["CUT"]) - set(CONTEXTO)
    assert not faltantes, f"Comunas sin contexto espacial: {faltantes}"

    ctx = pd.DataFrame.from_dict(CONTEXTO, orient="index",
                                 columns=["sector", "lat", "lon", "clasificacion_zona"])
    df = src.merge(ctx, left_on="CUT", right_index=True, how="left")
    df["comuna"] = df["comuna"].replace(NOMBRES)

    out = pd.DataFrame({
        "comuna": df["comuna"],
        "sector": df["sector"],
        "poblacion": df["poblacion"].astype(int),
        "area_verde_total_ha": (df["m2_areas_verdes"] / 10_000).round(2),
        "area_verde_m2_hab": (df["m2_areas_verdes"] / df["poblacion"]).round(2),
        "hurtos_total": df["total_hurtos_2023"].astype(int),
        "tasa_hurtos_100k": (df["total_hurtos_2023"] / df["poblacion"] * 100_000).round(1),
        "lat": df["lat"],
        "lon": df["lon"],
        "clasificacion_zona": df["clasificacion_zona"],
        # Columnas adicionales de contexto (útiles para análisis complementarios)
        "cut": df["CUT"],
        "pct_pobreza": (df["pct_pobreza"] * 100).round(2),
        "cantidad_plazas": df["cantidad_plazas"],
        "cantidad_parques": df["cantidad_parques"],
        "tiene_catastro_minvu": df["tiene_catastro_minvu"],
    })
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "rm_comunas_2023.csv", index=False, encoding="utf-8")

    mens = pd.read_csv(RAW / "hurtos_mensuales_rm_2023.csv")
    mens = mens.merge(out[["cut", "comuna", "sector", "poblacion"]], left_on="CUT", right_on="cut",
                      suffixes=("_raw", ""))
    mens = mens[["cut", "comuna", "sector", "poblacion", "fecha", "mes", "hurtos"]]
    mens["hurtos"] = mens["hurtos"].astype(int)
    mens.to_csv(OUT / "rm_hurtos_mensuales_2023.csv", index=False, encoding="utf-8")

    print(f"rm_comunas_2023.csv: {out.shape} | sin área verde: {out['area_verde_m2_hab'].isna().sum()}")
    print(f"rm_hurtos_mensuales_2023.csv: {mens.shape}")


if __name__ == "__main__":
    main()
