"""
Recorte espacial pela área de estudo do acervo.

A área de estudo é lida sempre do arquivo único apontado por
`config/config.yaml` (`area_estudo:`), gerado por
`scripts/processamento/area_estudo.py` a partir da camada `limite_municipal`.
Nenhum script deve recriar o polígono do município por conta própria: duas definições do mesmo recorte divergem, e a
divergência aparece tarde, num número que ninguém consegue explicar.

O CRS de trabalho também vem do config — ver `scripts/utils/paths.py`.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd

from scripts.utils import paths


def carregar_area_estudo(caminho: Path | None = None) -> gpd.GeoDataFrame:
    """Carrega a área de estudo de referência, já no CRS de produção.

    Mantido por compatibilidade: delega a `paths.carregar_area_estudo()`, que
    é o ponto único de leitura.
    """
    return paths.carregar_area_estudo(caminho)


def recortar_vetor(
    gdf: gpd.GeoDataFrame,
    area_estudo: gpd.GeoDataFrame | None = None,
) -> gpd.GeoDataFrame:
    """Recorta um GeoDataFrame pela área de estudo (clip), reprojetando se preciso.

    Args:
        gdf: camada a recortar; precisa ter CRS declarado.
        area_estudo: recorte alternativo; default é o do acervo.

    Returns:
        A camada recortada, no CRS de produção.

    Raises:
        ValueError: se `gdf` não declara CRS — recortar sem saber o CRS de
            entrada produz resultado silenciosamente errado.
    """
    if area_estudo is None:
        area_estudo = carregar_area_estudo()
    if gdf.crs is None:
        raise ValueError("GeoDataFrame de entrada não possui CRS definido.")

    crs_producao = paths.crs_producao()
    if gdf.crs.to_string() != crs_producao:
        gdf = gdf.to_crs(crs_producao)
    return gpd.clip(gdf, area_estudo)
