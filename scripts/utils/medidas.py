"""
Medida de ÁREA no CRS equivalente do acervo (`crs.area` do config).

O CRS de produção (UTM) é conforme, não equivalente: fora do meridiano central
ele infla a área — em Bagé, na borda leste do fuso 21, ~0,12%. Por isso a regra
é dividida:

- operações espaciais (união, diferença, dissolve, buffer), distâncias e
  perímetros: no CRS de PRODUÇÃO;
- ÁREA: a geometria resultante é reprojetada para o CRS de ÁREA e medida lá.

Todo número de área gravado em metadado deve vir acompanhado de
`crs_medicao_area` (valor: `crs_medicao_area()`).
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd
from shapely.geometry.base import BaseGeometry

from scripts.utils import paths


def crs_medicao_area() -> str:
    """Valor a gravar no campo `crs_medicao_area` de cada medida."""
    return paths.crs_area()


def areas_m2(gdf: gpd.GeoDataFrame | gpd.GeoSeries) -> pd.Series:
    """Área de cada feição, em m², medida no CRS de área."""
    if gdf.crs is None:
        raise ValueError("sem CRS declarado — não dá para medir área com segurança.")
    return gdf.to_crs(paths.crs_area()).area


def area_m2(geometria: BaseGeometry, crs: str | None = None) -> float:
    """Área de uma geometria, em m², medida no CRS de área.

    Args:
        geometria: geometria shapely.
        crs: CRS em que a geometria está (default: o de produção).
    """
    if geometria.is_empty:
        return 0.0
    serie = gpd.GeoSeries([geometria], crs=crs or paths.crs_producao())
    return float(areas_m2(serie).iloc[0])
