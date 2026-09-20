"""
Exporta o limite municipal para o geoportal:

    config/area_estudo.geojson (EPSG:31981)
        -> data/geoportal/limite_municipal.geojson (EPSG:4326)

É a etapa de PUBLICAÇÃO: não recalcula nada, não altera geometria nem
atributos — só reprojeta para o CRS que o Leaflet consome. O arquivo de
produção correspondente (GeoPackage) é gerado por
scripts/download/vetor_ibge.py.

Uso:
    python scripts/geoportal/exportar_limite_municipal.py
    python scripts/geoportal/exportar_limite_municipal.py --forcar
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.geoportal.common import DIR_GEOPORTAL, salvar_geojson_wgs84  # noqa: E402
from scripts.utils.recorte_municipio import CAMINHO_AREA_ESTUDO_PADRAO, carregar_area_estudo  # noqa: E402

NOME_SAIDA = "limite_municipal.geojson"


def main() -> None:
    parser = argparse.ArgumentParser(description="Publica o limite municipal no geoportal.")
    parser.add_argument("--forcar", action="store_true", help="Reexporta mesmo se já existir")
    args = parser.parse_args()

    area_estudo: gpd.GeoDataFrame = carregar_area_estudo()

    salvar_geojson_wgs84(
        area_estudo,
        DIR_GEOPORTAL / NOME_SAIDA,
        descricao="Limite municipal (área de estudo do acervo).",
        fonte={
            "caminho_origem": str(CAMINHO_AREA_ESTUDO_PADRAO.relative_to(RAIZ_PROJETO)),
            "script_origem": "scripts/download/vetor_ibge.py",
            "instituicao": "IBGE — Malhas Territoriais",
        },
        transformacao="reprojeção EPSG:31981 -> EPSG:4326, sem alteração de geometria/atributos",
        forcar=args.forcar,
    )


if __name__ == "__main__":
    main()
