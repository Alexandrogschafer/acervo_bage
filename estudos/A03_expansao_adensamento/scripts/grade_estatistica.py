"""
A03 — leitura da grade estatística do IBGE (2010 e 2022), comum aos scripts.

Tirada de `d03_grade.py` em 2026-09-23, quando o d03 foi marcado SUPERADO pelo
`s1_expansao_adensamento.py`: o s1 lia a grade chamando o d03, e script vigente
não depende de script superado. O código é o mesmo, sem mudança de comportamento.

A leitura NÃO harmoniza as edições: devolve as células como o IBGE as publica.
Comparar 2010 com 2022 exige a unidade harmonizada (mãe de 1 km contra a soma
das 25 filhas de 200 m) — ver `s1_expansao_adensamento.harmonizar` e
docs/ressalvas_censo_bage.md § 7.

LÊ só data/raw/ e config/.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.utils import paths  # noqa: E402

VET = paths.caminho("raw_vetor", "ibge")
QUADRANTES = ("grade_id14.zip", "grade_id04.zip")
CRS_GRADE = "EPSG:4674"   # declarado nos quatro shapefiles (§ 3.4 do reconhecimento)
CAMPOS = {"2010": {"pop": "POP", "dom": "DOM_OCU"}, "2022": {"pop": "TOTAL", "dom": "TOTAL_DOM"}}


def ler_grade(ano: str, area: gpd.GeoSeries) -> gpd.GeoDataFrame:
    """Células dos dois quadrantes cujo centroide cai no município."""
    campos = CAMPOS[ano]
    limite = area.union_all()
    # o bbox do filtro vai no CRS DO ARQUIVO (a grade vem em EPSG:4674), não no de produção
    caixa = tuple(area.to_crs(CRS_GRADE).total_bounds)
    partes = []
    for arquivo in QUADRANTES:
        caminho = f"zip://{VET / f'censo_{ano}' / 'grade_estatistica' / arquivo}"
        g = gpd.read_file(caminho, columns=["ID_UNICO", campos["pop"], campos["dom"]],
                          bbox=caixa)
        partes.append(g.to_crs(area.crs))
    g = pd.concat(partes, ignore_index=True)
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=area.crs)
    g = g.rename(columns={campos["pop"]: "pop", campos["dom"]: "dom"})
    g["centroide_no_municipio"] = g.geometry.centroid.within(limite)
    g["toca_o_municipio"] = g.intersects(limite)
    return g[["ID_UNICO", "pop", "dom", "centroide_no_municipio", "toca_o_municipio",
              "geometry"]].reset_index(drop=True)
