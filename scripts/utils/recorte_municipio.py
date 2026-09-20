"""
Recorte espacial pela área de estudo do acervo.

A área de estudo é lida sempre de um único arquivo de referência
(config/area_estudo.geojson), gerado por scripts/download/vetor_ibge.py.
Nenhum script deve recriar o polígono do município por conta própria.

CRS padrão do acervo: EPSG:31981 (SIRGAS 2000 / UTM 21S).
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd

CRS_PADRAO = "EPSG:31981"
CAMINHO_AREA_ESTUDO_PADRAO = Path(__file__).resolve().parents[2] / "config" / "area_estudo.geojson"


def carregar_area_estudo(caminho: Path = CAMINHO_AREA_ESTUDO_PADRAO) -> gpd.GeoDataFrame:
    """Carrega a área de estudo de referência, já no CRS padrão do acervo."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"Área de estudo não encontrada em {caminho}. "
            "Rode primeiro: python scripts/download/vetor_ibge.py --codigo-ibge <codigo>"
        )
    gdf = gpd.read_file(caminho)
    if gdf.crs is None:
        raise ValueError(f"{caminho} não possui CRS definido — verifique a geração do arquivo.")
    if gdf.crs.to_string() != CRS_PADRAO:
        gdf = gdf.to_crs(CRS_PADRAO)
    return gdf


def recortar_vetor(
    gdf: gpd.GeoDataFrame, area_estudo: gpd.GeoDataFrame | None = None
) -> gpd.GeoDataFrame:
    """Recorta um GeoDataFrame pela área de estudo (clip), reprojetando se preciso."""
    if area_estudo is None:
        area_estudo = carregar_area_estudo()
    if gdf.crs is None:
        raise ValueError("GeoDataFrame de entrada não possui CRS definido.")
    if gdf.crs.to_string() != CRS_PADRAO:
        gdf = gdf.to_crs(CRS_PADRAO)
    return gpd.clip(gdf, area_estudo)
