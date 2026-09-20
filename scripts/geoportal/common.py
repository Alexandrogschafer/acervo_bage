"""
Utilitários compartilhados dos scripts de PUBLICAÇÃO do geoportal.

Separação que vale para todo o acervo (ver CLAUDE.md):
  - PRODUÇÃO   -> GeoPackage em data/processed/, no CRS de trabalho
                  (EPSG:31981), versionado por hash no catálogo de camadas;
  - PUBLICAÇÃO -> GeoJSON em data/geoportal/, em EPSG:4326, que é o único
                  CRS que o Leaflet consome.

Qualquer transformação métrica (simplificação, buffer, área) é feita ANTES,
no CRS métrico; a reprojeção para 4326 é sempre o último passo.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.utils.hashes import sha256_arquivo  # noqa: E402

DIR_GEOPORTAL = RAIZ_PROJETO / "data" / "geoportal"
CRS_LEAFLET = "EPSG:4326"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("geoportal")


def salvar_geojson_wgs84(
    gdf: gpd.GeoDataFrame,
    caminho_saida: Path,
    descricao: str,
    fonte: dict,
    transformacao: str,
    forcar: bool = False,
) -> Path:
    """Reprojeta para EPSG:4326 e exporta GeoJSON + .json de metadados irmão.

    Idempotente: se o arquivo já existe e `forcar` é False, só loga e sai.
    """
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    if caminho_saida.exists() and not forcar:
        logger.info("já existe, pulando: %s", caminho_saida.relative_to(RAIZ_PROJETO))
        return caminho_saida

    if gdf.crs is None:
        raise ValueError(f"GeoDataFrame sem CRS definido antes de exportar para {caminho_saida}")
    gdf_wgs84 = gdf.to_crs(CRS_LEAFLET) if gdf.crs.to_string() != CRS_LEAFLET else gdf

    gdf_wgs84.to_file(caminho_saida, driver="GeoJSON")

    metadados = {
        "descricao": descricao,
        "fonte": fonte,
        "crs_saida": CRS_LEAFLET,
        "transformacao_aplicada": transformacao,
        "n_features": int(len(gdf_wgs84)),
        "colunas": [c for c in gdf_wgs84.columns if c != "geometry"],
        "sha256": sha256_arquivo(caminho_saida),
        "data_processamento": datetime.now(timezone.utc).isoformat(),
    }
    caminho_saida.with_suffix(".json").write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    logger.info(
        "gerado: %s (%d feições, %.1f KB)",
        caminho_saida.relative_to(RAIZ_PROJETO),
        len(gdf_wgs84),
        caminho_saida.stat().st_size / 1024,
    )
    return caminho_saida
