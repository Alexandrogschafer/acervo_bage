"""
A03 — subordinada 1: as geografias do § 5 no cenário adotado (setor 136 à parte).

Desde 2026-09-23 os números principais da subordinada 1 excluem as unidades do
setor rural de 2010 430160205000136 (resultados_s1.md § 11). Este script refaz,
com as MESMAS funções de s1_expansao_adensamento.py (caracterizar, densidade),
as geografias do § 5 em dois cenários:

    adotado        sem as unidades à parte
    todas          todas as unidades (sensibilidade; = s1_caracterizacao.json)

As unidades à parte vêm de derivados/s1_desagregacao_2010.json (bloco
cruzamento_com_as_classes.unidades_a_parte), que precisa ter sido gerado sobre
esta mesma camada (sha256_conteudo conferido). O CENTRO não muda: é a referência
declarada no § 1 (centro médio dos domicílios de 2010 com todas as unidades) e
as distâncias já estão na camada.

EXTINTAS: URBANO DE BORDA (bloco `extintas_urbano_de_borda`). Para cada cenário,
as extintas por situação do setor de 2010 (o do centroide da unidade, lido de
derivados/s1_extintas_unidades.gpkg) e por distância à área urbanizada de 2022
(0 = dentro ou tocando; distância da borda da unidade, no CRS de produção).

LÊ saidas/s1_celulas_2010_2022.gpkg, derivados/s1_desagregacao_2010.json,
derivados/s1_extintas_unidades.gpkg (conferido pelo sha256_conteudo) e data/raw/
(área urbanizada 2022).
ESCREVE só derivados/s1_geografias.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

import s1_expansao_adensamento as s1  # noqa: E402
from scripts.utils import medidas, metadados  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

DESAG = s1.DERIV / "s1_desagregacao_2010.json"
SAIDA = s1.DERIV / "s1_geografias.json"


def unidades_a_parte() -> tuple[list[str], str]:
    """Lista das unidades à parte, conferindo que vem desta mesma camada."""
    d = json.loads(DESAG.read_text(encoding="utf-8"))
    atual = sha256_conteudo(s1.CAMADA)
    if atual != metadados.ler(s1.CAMADA)["sha256_conteudo"] or d.get("camada_sha256_conteudo") != atual:
        raise SystemExit("PARADO — a camada de trabalho não é a usada em s1_desagregacao_2010.json; "
                         "rodar s1_desagregacao_2010.py antes")
    c = d["cruzamento_com_as_classes"]
    return c["unidades_a_parte"], ";".join(c["setores_com_assinatura"])


FAIXAS_BORDA_M = [0, 1, 500, 1000, 2000, float("inf")]


def area_urbanizada(crs) -> object:
    area = s1.paths.carregar_area_estudo()
    au = gpd.read_file(f"/vsizip/{s1.AU_ZIP}/{s1.AU_SHP}",
                       bbox=tuple(area.to_crs("EPSG:4674").total_bounds)).to_crs(crs)
    return au[(au["Tipo"] == s1.TIPO_URBANIZADA) & au.intersects(area.union_all())].union_all()


def extintas_de_borda(u: gpd.GeoDataFrame, apoio: gpd.GeoDataFrame, au) -> dict:
    e = u[u["classe"] == "extinta"].copy()
    e["setor_2010"] = e["unidade"].map(apoio.set_index("unidade")["setor_2010"]).fillna("fora da malha")
    e["dist_au_m"] = e.geometry.distance(au)
    e["faixa"] = pd.cut(e["dist_au_m"], FAIXAS_BORDA_M, right=False,
                        labels=["dentro ou tocando", "até 500 m", "500 m a 1 km", "1 a 2 km", "> 2 km"])
    tot = int(e["dom_10"].sum())
    por_sit = {s: {"unidades": int(len(g)), "dom_10": int(g["dom_10"].sum()),
                   "pct_dom_10": round(100 * g["dom_10"].sum() / tot, 1),
                   "por_resolucao": g["resolucao"].value_counts().to_dict()}
               for s, g in e.groupby("setor_2010")}
    por_faixa = {str(f): {"unidades": int(len(g)), "dom_10": int(g["dom_10"].sum())}
                 for f, g in e.groupby("faixa", observed=False)}
    urb = e[e["setor_2010"] == "URBANO"]
    return {"extintas": int(len(e)), "dom_10": tot,
            "por_situacao_do_setor_2010": por_sit,
            "por_distancia_a_area_urbanizada_2022": por_faixa,
            "setor_urbano_2010_e_fora_da_area_urbanizada_ate_1km": {
                "unidades": int(((urb["dist_au_m"] > 0) & (urb["dist_au_m"] < 1000)).sum()),
                "dom_10": int(urb.loc[(urb["dist_au_m"] > 0) & (urb["dist_au_m"] < 1000), "dom_10"].sum())},
            "crs_medicao_distancia": s1.paths.crs_producao()}


def cenario(u: gpd.GeoDataFrame) -> dict:
    return {
        "unidades": int(len(u)),
        "caracterizacao": {"nova": s1.caracterizar(u, "nova", "dom_22"),
                           "adensada": s1.caracterizar(u, "adensada", "dom_22"),
                           "extinta": s1.caracterizar(u, "extinta", "dom_10")},
        "densidade_por_classe": s1.densidade(u),
    }


def main() -> None:
    a_parte, setores = unidades_a_parte()
    u = gpd.read_file(s1.CAMADA)
    fora = set(a_parte) - set(u["unidade"])
    if fora:
        raise SystemExit(f"PARADO — {len(fora)} unidades à parte fora da camada")
    adotado = u[~u["unidade"].isin(a_parte)].copy()
    apoio_arq = s1.DERIV / "s1_extintas_unidades.gpkg"
    if sha256_conteudo(apoio_arq) != metadados.ler(apoio_arq)["sha256_conteudo"]:
        raise SystemExit("PARADO — s1_extintas_unidades.gpkg mudou desde o .json irmão")
    apoio = gpd.read_file(apoio_arq)
    au = area_urbanizada(u.crs)
    resultado = {
        "cenario_adotado": f"sem as {len(a_parte)} unidades do setor de 2010 {setores} "
                           "(resultados_s1.md § 11)",
        "camada_sha256_conteudo": metadados.ler(s1.CAMADA)["sha256_conteudo"],
        "centro": "o do § 1 (todas as unidades), sem mudança; distâncias lidas da camada",
        "adotado": cenario(adotado),
        "todas_as_unidades": cenario(u),
        "extintas_urbano_de_borda": {"adotado": extintas_de_borda(adotado, apoio, au),
                                     "todas_as_unidades": extintas_de_borda(u, apoio, au)},
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=int), encoding="utf-8")
    for nome in ("adotado", "todas_as_unidades"):
        c = resultado[nome]["caracterizacao"]
        print(nome, {k: (v["unidades"], v["distancia_ao_centro"]["mediana_ponderada_por_domicilio_km"],
                         v["area_urbanizada_2022"]["pct_domicilios_dentro"]) for k, v in c.items()})


if __name__ == "__main__":
    main()
