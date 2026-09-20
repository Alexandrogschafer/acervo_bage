"""
Recorte espacial pela área de estudo do acervo.

A área de estudo é lida sempre do arquivo único apontado por
`config/config.yaml` (`area_estudo:`), gerado por
`scripts/download/vetor_ibge.py`. Nenhum script deve recriar o polígono do
município por conta própria: duas definições do mesmo recorte divergem, e a
divergência aparece tarde, num número que ninguém consegue explicar.

O CRS de trabalho também vem do config — ver `scripts/utils/paths.py`.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd

from scripts.utils import paths


def carregar_area_estudo(caminho: Path | None = None) -> gpd.GeoDataFrame:
    """Carrega a área de estudo de referência, já no CRS de produção.

    Args:
        caminho: arquivo alternativo; default vem de `config.yaml`.

    Returns:
        GeoDataFrame reprojetado para o CRS de produção do acervo.

    Raises:
        FileNotFoundError: se o arquivo não existe (vetor_ibge.py não rodou).
        ValueError: se o arquivo não declara CRS.
    """
    alvo = Path(caminho) if caminho else paths.area_estudo()
    if not alvo.exists():
        raise FileNotFoundError(
            f"área de estudo não encontrada em {paths.relativo(alvo)}. "
            f"Rode primeiro: python scripts/download/vetor_ibge.py "
            f"--codigo-ibge {paths.codigo_ibge()}"
        )

    gdf = gpd.read_file(alvo)
    if gdf.crs is None:
        raise ValueError(
            f"{paths.relativo(alvo)} não possui CRS definido — verifique a geração."
        )

    crs_producao = paths.crs_producao()
    if gdf.crs.to_string() != crs_producao:
        gdf = gdf.to_crs(crs_producao)
    return gdf


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
