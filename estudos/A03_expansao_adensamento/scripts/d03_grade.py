"""
A03 — dimensionamento, bloco 3: redistribuição na grade estatística 2010 × 2022.

Antes de medir, CONFERE que as duas edições da grade são a mesma geografia: o
identificador `ID_UNICO` das células de 200 m / 1 km e a geometria delas. Se as
células não coincidirem, o script PARA e relata — comparar célula a célula duas
grades diferentes produziria "redistribuição" que é só mudança de malha.

Conferência de conteúdo: a soma das células dentro de Bagé é comparada com o
total do município medido no d01. Isso também é o que sustenta a leitura dos
campos, já que a documentação da grade de 2010 não lista os campos:
2010 `POP`/`DOM_OCU`, 2022 `TOTAL`/`TOTAL_DOM`.

Uma célula é de Bagé quando seu CENTROIDE cai no município (regra única para os
dois anos, que não parte células de borda). O relatório diz quantas células a
borda corta e quanto isso pesa.

LÊ só data/raw/ e config/; ESCREVE só derivados/d03_grade.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.utils import medidas, paths  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
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


def conferir_geografia(g10: gpd.GeoDataFrame, g22: gpd.GeoDataFrame) -> dict:
    """As duas edições são a mesma grade? IDs e geometria das células comuns."""
    ids10, ids22 = set(g10["ID_UNICO"]), set(g22["ID_UNICO"])
    comuns = sorted(ids10 & ids22)
    a = g10.set_index("ID_UNICO").loc[comuns].geometry
    b = g22.set_index("ID_UNICO").loc[comuns].geometry
    distancia = a.centroid.distance(b.centroid, align=True)
    areas_a, areas_b = medidas.areas_m2(a), medidas.areas_m2(b)
    return {
        "celulas_2010": len(ids10), "celulas_2022": len(ids22), "celulas_comuns": len(comuns),
        "so_em_2010": len(ids10 - ids22), "so_em_2022": len(ids22 - ids10),
        "distancia_maxima_entre_centroides_m": round(float(distancia.max()), 6),
        "diferenca_maxima_de_area_m2": round(float((areas_a - areas_b).abs().max()), 6),
        "tamanhos_de_celula_m2_2010": sorted({round(float(v)) for v in areas_a}),
        "mesma_geografia": bool(float(distancia.max()) < 0.01
                                and float((areas_a - areas_b).abs().max()) < 1.0),
    }


def dispersao(serie: pd.Series) -> dict:
    return {"n": int(len(serie)), "soma": int(serie.sum()),
            "mediana": float(serie.median()) if len(serie) else None,
            "p90": float(serie.quantile(0.90)) if len(serie) else None,
            "maximo": float(serie.max()) if len(serie) else None}


def main() -> None:
    area = paths.carregar_area_estudo()
    area = area.geometry if isinstance(area, gpd.GeoDataFrame) else area
    bruto10, bruto22 = ler_grade("2010", area), ler_grade("2022", area)
    # o total por borda mostra se a diferença para o município é de recorte ou do dado
    borda = {ano: {regra: {"populacao": int(g.loc[g[regra], "pop"].sum()),
                           "domicilios": int(g.loc[g[regra], "dom"].sum()),
                           "celulas": int(g[regra].sum())}
                   for regra in ("centroide_no_municipio", "toca_o_municipio")}
             for ano, g in (("2010", bruto10), ("2022", bruto22))}
    g10 = bruto10[bruto10["centroide_no_municipio"]].reset_index(drop=True)
    g22 = bruto22[bruto22["centroide_no_municipio"]].reset_index(drop=True)

    conferencia = conferir_geografia(g10, g22)
    if not conferencia["mesma_geografia"]:
        (DERIV / "d03_grade.json").write_text(
            json.dumps({"PARADO": "as duas edições da grade não são a mesma geografia",
                        "conferencia": conferencia}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        raise SystemExit(f"PARADO — grades diferentes: {conferencia}")

    j = (g10.set_index("ID_UNICO")[["pop", "dom"]]
         .join(g22.set_index("ID_UNICO")[["pop", "dom"]], how="outer",
               lsuffix="_10", rsuffix="_22").fillna(0))
    j["d_dom"] = j["dom_22"] - j["dom_10"]
    j["d_pop"] = j["pop_22"] - j["pop_10"]
    ocupadas = j[(j["dom_10"] > 0) | (j["dom_22"] > 0)]

    ganho, perda = ocupadas[ocupadas["d_dom"] > 0], ocupadas[ocupadas["d_dom"] < 0]
    ganho_p, perda_p = ocupadas[ocupadas["d_pop"] > 0], ocupadas[ocupadas["d_pop"] < 0]
    divergentes = ocupadas[(ocupadas["d_dom"] > 0) & (ocupadas["d_pop"] < 0)]
    divergentes_inv = ocupadas[(ocupadas["d_dom"] < 0) & (ocupadas["d_pop"] > 0)]

    resultado = {
        "conferencia_geografia": conferencia,
        "conferencia_totais": {
            "2010": {"populacao": int(g10["pop"].sum()), "domicilios": int(g10["dom"].sum())},
            "2022": {"populacao": int(g22["pop"].sum()), "domicilios": int(g22["dom"].sum())},
            "comparar_com": "d01_descompasso.json (município)",
            "por_regra_de_borda": borda,
        },
        "celulas": {"na_grade_de_bage": int(len(j)),
                    "com_domicilio_em_algum_ano": int(len(ocupadas)),
                    "so_com_domicilio_em_2022": int(((ocupadas["dom_10"] == 0)
                                                     & (ocupadas["dom_22"] > 0)).sum()),
                    "so_com_domicilio_em_2010": int(((ocupadas["dom_10"] > 0)
                                                     & (ocupadas["dom_22"] == 0)).sum())},
        "domicilios": {"ganharam": dispersao(ganho["d_dom"]),
                       "perderam": dispersao(perda["d_dom"].abs()),
                       "sem_mudanca": int((ocupadas["d_dom"] == 0).sum())},
        "populacao": {"ganharam": dispersao(ganho_p["d_pop"]),
                      "perderam": dispersao(perda_p["d_pop"].abs()),
                      "sem_mudanca": int((ocupadas["d_pop"] == 0).sum())},
        "de_onde_vem_o_ganho_de_domicilios": {
            "em_celulas_novas": int(ganho.loc[ganho["dom_10"] == 0, "d_dom"].sum()),
            "em_celulas_que_ja_tinham_domicilio": int(ganho.loc[ganho["dom_10"] > 0,
                                                                "d_dom"].sum()),
            "saldo_liquido": int(ocupadas["d_dom"].sum()),
            "celulas_novas": int((ganho["dom_10"] == 0).sum()),
            "celulas_ja_ocupadas_que_cresceram": int((ganho["dom_10"] > 0).sum()),
            "populacao_nas_celulas_novas": int(ganho.loc[ganho["dom_10"] == 0, "d_pop"].sum()),
        },
        "divergencia_de_sinal": {
            "ganham_domicilio_e_perdem_populacao": {
                "celulas": int(len(divergentes)),
                "pct_das_ocupadas": round(100 * len(divergentes) / len(ocupadas), 1),
                "domicilios_ganhos": int(divergentes["d_dom"].sum()),
                "populacao_perdida": int(divergentes["d_pop"].sum())},
            "perdem_domicilio_e_ganham_populacao": {
                "celulas": int(len(divergentes_inv)),
                "pct_das_ocupadas": round(100 * len(divergentes_inv) / len(ocupadas), 1)},
        },
    }
    (DERIV / "d03_grade.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    print("geografia:", conferencia)
    print("totais na grade:", {k: v for k, v in resultado["conferencia_totais"].items()
                               if k != "por_regra_de_borda"})
    print("borda:", borda)
    print("células:", resultado["celulas"])
    print("domicílios ganharam:", resultado["domicilios"]["ganharam"])
    print("domicílios perderam:", resultado["domicilios"]["perderam"])
    print("população ganharam:", resultado["populacao"]["ganharam"])
    print("população perderam:", resultado["populacao"]["perderam"])
    print("origem do ganho:", resultado["de_onde_vem_o_ganho_de_domicilios"])
    print("divergência:", resultado["divergencia_de_sinal"])


if __name__ == "__main__":
    main()
