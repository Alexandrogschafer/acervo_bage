"""
A03 — subordinada 1: detecção INDIRETA da desagregação na grade de 2010.

A grade de 2010 é híbrida (IBGE, Grade Estatística, 2016, p. 16–21): setor com
ausência de localização < 50 % entra por agregação (pontos no rural, quadra/face
no urbano); > 50 %, por desagregação (dasimétrico por vias, por uso e cobertura,
ou ponderação zonal simples). A variável de abordagem por célula descrita na
p. 21 NÃO vem nos arquivos do geoftp (campos conferidos em 2026-09-23), e a
ausência de localização por setor não é publicada: a regra não se reconstrói.
Este script procura só INDÍCIOS no dado. Nada aqui é a variável oficial, e nada
é reclassificado.

TESTE A (pedido): na desagregação a população da célula é domicílios × moradores
por domicílio DO SETOR (p. 20–21). A célula é "compatível" com a razão r do seu
setor quando POP cabe no intervalo que o arredondamento final (p. 22) permite:
    (DOM_OCU − 0,5)·r − 0,5  <=  POP  <=  (DOM_OCU + 0,5)·r + 0,5
r = moradores em domicílios particulares e coletivos / domicílios particulares e
coletivos (2010: Domicilio02 V001 / Domicilio01 V001; 2022: basico v0001 /
v0007). Controles: a mesma medida na grade de 2022, que é vinculada por
coordenada (notas 01/2025, p. 7), e em 2010 contra a razão de um setor sorteado.
Se 2010 não se separa dos controles, o teste não discrimina e é DESCARTADO.

TESTE B (achado na exploração): a ponderação zonal e o dasimétrico binário dão
o MESMO par (domicílios, população) a células inteiras de igual área povoada no
mesmo setor. Assinatura B: célula com DOM_OCU >= 3, >= 90 % da área num só
setor, cujo par (DOM_OCU, POP) se repete numa vizinha rainha do mesmo setor.
Mesmo controle em 2022.

Setor de cada célula: o de maior área de interseção (em crs.area); "inteira"
quando ele cobre >= 90 % da célula (a tolerância da p. 20).

LÊ data/raw/ (grades, malha 2010), o acervo (setores_2022, conferida),
derivados/bage/ (agregados por setor, do r00), a camada de trabalho e a camada
de apoio do s1_extintas (conferindo o sha256_conteudo de ambas). ESCREVE só:
    derivados/s1_desagregacao_2010.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402

from grade_estatistica import ler_grade  # noqa: E402
from s1_expansao_adensamento import CLASSES, TOLERANCIA_CONTIGUIDADE_M  # noqa: E402
from scripts.utils import catalogo, medidas, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

ESTUDO = Path(__file__).resolve().parents[1]
DERIV = ESTUDO / "derivados"
BAGE = DERIV / "bage"
CAMADA = ESTUDO / "saidas" / "s1_celulas_2010_2022.gpkg"
APOIO = DERIV / "s1_extintas_unidades.gpkg"
SAIDA = DERIV / "s1_desagregacao_2010.json"
MALHA_2010 = paths.caminho("raw_vetor", "ibge", "censo_2010", "rs_setores_censitarios.zip")

PARTE_INTEIRA = 0.9          # p. 20 da metodologia de 2010
DOM_MIN_B = 3
FAIXAS_DOM = [0, 1, 2, 4, 7, 12, 20, 40, np.inf]
SEMENTE = 20260923


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.strip().str.replace(",", ".", regex=False), errors="coerce")


def conferida(arquivo: Path) -> gpd.GeoDataFrame:
    if sha256_conteudo(arquivo) != metadados.ler(arquivo)["sha256_conteudo"]:
        raise SystemExit(f"PARADO — {paths.relativo(arquivo)} mudou desde o .json irmão")
    return gpd.read_file(arquivo)


# --------------------------------------------------------------------------
# setores e razões
# --------------------------------------------------------------------------

def razoes_2010() -> pd.Series:
    d1 = pd.read_csv(BAGE / "c2010" / "Domicilio01_RS.csv", sep=";", dtype=str).set_index("Cod_setor")
    d2 = pd.read_csv(BAGE / "c2010" / "Domicilio02_RS.csv", sep=";", dtype=str).set_index("Cod_setor")
    return num(d2["V001"]) / num(d1["V001"])


def razoes_2022() -> pd.Series:
    b = pd.read_csv(BAGE / "c2022" / "Agregados_por_setores_basico.csv", sep=";", dtype=str)
    b = b.set_index(b["CD_SETOR"].str.strip())
    return num(b["v0001"]) / num(b["v0007"])


def malhas(crs: str) -> dict[str, gpd.GeoDataFrame]:
    m10 = gpd.read_file(f"zip://{MALHA_2010}", where=f"CD_GEOCODM = '{paths.codigo_ibge()}'")
    m10 = m10.rename(columns={"CD_GEOCODI": "setor", "TIPO": "situacao"})[["setor", "situacao", "geometry"]]
    _, arq = catalogo.camada_conferida("setores_2022")
    m22 = gpd.read_file(arq).rename(columns={"CD_SETOR": "setor", "SITUACAO": "situacao"})
    return {"2010": m10.to_crs(crs), "2022": m22[["setor", "situacao", "geometry"]].to_crs(crs)}


def celulas(ano: str, area: gpd.GeoDataFrame, malha: gpd.GeoDataFrame, r: pd.Series) -> gpd.GeoDataFrame:
    g = ler_grade(ano, area.geometry)
    g = g[g["centroide_no_municipio"]].reset_index(drop=True)
    g["cid"] = g.index
    inter = gpd.overlay(g[["cid", "geometry"]], malha, how="intersection", keep_geom_type=True)
    inter["a"] = medidas.areas_m2(inter.geometry).values
    total = inter.groupby("cid")["a"].sum()
    maior = inter.sort_values("a", ascending=False).drop_duplicates("cid").set_index("cid")
    g["setor"] = maior["setor"].reindex(g["cid"]).values
    g["situacao_setor"] = maior["situacao"].reindex(g["cid"]).values
    g["parte_no_setor"] = (maior["a"] / total).reindex(g["cid"]).values
    g["inteira"] = g["parte_no_setor"] >= PARTE_INTEIRA
    g["r_setor"] = r.reindex(g["setor"]).values
    g["res"] = g["ID_UNICO"].str[:4].map({"200M": "200 m", "1KME": "1 km"})
    return g


# --------------------------------------------------------------------------
# testes
# --------------------------------------------------------------------------

def compativel(pop: pd.Series, dom: pd.Series, r) -> pd.Series:
    return (pop >= (dom - 0.5) * r - 0.5) & (pop <= (dom + 0.5) * r + 0.5)


def teste_a(g10: gpd.GeoDataFrame, g22: gpd.GeoDataFrame, r10: pd.Series) -> tuple[dict, pd.Series]:
    rng = np.random.default_rng(SEMENTE)
    sorteada = rng.choice(r10.dropna().values, len(g10))
    c10 = compativel(g10["pop"], g10["dom"], g10["r_setor"])
    c22 = compativel(g22["pop"], g22["dom"], g22["r_setor"])
    cs = compativel(g10["pop"], g10["dom"], sorteada)
    faixa10 = pd.cut(g10["dom"], FAIXAS_DOM)
    faixa22 = pd.cut(g22["dom"], FAIXAS_DOM)
    linhas = []
    for res in ("1 km", "200 m"):
        for f in faixa10.cat.categories:
            m10 = (g10["res"] == res) & (faixa10 == f) & g10["inteira"]
            m22 = (g22["res"] == res) & (faixa22 == f) & g22["inteira"]
            if not (m10.sum() or m22.sum()):
                continue
            linhas.append({
                "resolucao": res, "faixa_dom": f"{f.left:g}–{f.right:g}" if np.isfinite(f.right) else f"> {f.left:g}",
                "celulas_2010": int(m10.sum()), "pct_compativel_2010": _pct(c10[m10]),
                "pct_compativel_2010_razao_sorteada": _pct(cs[m10]),
                "celulas_2022": int(m22.sum()), "pct_compativel_2022": _pct(c22[m22])})

    def por_setor(g, c):
        inf = g[g["inteira"] & (g["dom"] >= 5)].assign(c=c, razao=lambda x: x["pop"] / x["dom"])
        s = inf.groupby("setor").agg(n=("c", "size"), frac=("c", "mean"),
                                     cv=("razao", lambda x: x.std() / x.mean()))
        s = s[s["n"] >= 3]
        return {"setores_com_3_ou_mais_celulas_informativas": int(len(s)),
                "mediana_da_fracao_compativel": round(float(s["frac"].median()), 3),
                "setores_com_fracao_compativel_>=_0,8": int((s["frac"] >= 0.8).sum()),
                "mediana_do_cv_da_razao": round(float(s["cv"].median()), 3),
                "setores_com_cv_<_0,05": int((s["cv"] < 0.05).sum())}

    inf10 = g10["inteira"] & (g10["dom"] >= 5)
    inf22 = g22["inteira"] & (g22["dom"] >= 5)
    resumo = {
        "regra": "compatível: (DOM−0,5)·r − 0,5 <= POP <= (DOM+0,5)·r + 0,5, r do setor de maior área; "
                 "só células inteiras (>= 90 % num setor)",
        "razao_do_setor": {"2010": "Domicilio02 V001 / Domicilio01 V001", "2022": "basico v0001 / v0007"},
        "por_faixa": linhas,
        "celulas_informativas_dom_>=_5": {
            "2010": {"celulas": int(inf10.sum()), "pct_compativel": _pct(c10[inf10]),
                     "pct_compativel_razao_sorteada": _pct(cs[inf10])},
            "2022": {"celulas": int(inf22.sum()), "pct_compativel": _pct(c22[inf22])}},
        "por_setor": {"2010": por_setor(g10, c10), "2022": por_setor(g22, c22)},
    }
    return resumo, c10


def _pct(s: pd.Series):
    return round(100 * float(s.mean()), 1) if len(s) else None


def teste_b(g: gpd.GeoDataFrame) -> pd.Series:
    arvore = shapely.STRtree(g.geometry.values)
    a, b = arvore.query(g.geometry.buffer(TOLERANCIA_CONTIGUIDADE_M).values, predicate="intersects")
    m = a != b
    a, b = a[m], b[m]
    s, d, p = g["setor"].values, g["dom"].values, g["pop"].values
    ok = ((s[a] == s[b]) & (d[a] == d[b]) & (p[a] == p[b]) & (d[a] >= DOM_MIN_B)
          & g["inteira"].values[a] & g["inteira"].values[b])
    return pd.Series(np.isin(np.arange(len(g)), a[ok]), index=g.index)


def resumo_b(g: gpd.GeoDataFrame, b: pd.Series) -> dict:
    x = g[b]
    return {"celulas": int(len(x)), "por_resolucao": x["res"].value_counts().to_dict(),
            "setores": sorted(x["setor"].unique().tolist()),
            "pares": [{"setor": k[0], "dom": int(k[1]), "pop": int(k[2]), "celulas": int(n)}
                      for k, n in x.groupby(["setor", "dom", "pop"]).size().items()],
            "domicilios": int(x["dom"].sum()), "populacao": int(x["pop"].sum())}


# --------------------------------------------------------------------------
# regra do upgrade (notas 2022, p. 6)
# --------------------------------------------------------------------------

def upgrade(area: gpd.GeoDataFrame, m22: gpd.GeoDataFrame) -> dict:
    g10 = ler_grade("2010", area.geometry)
    g22 = ler_grade("2022", area.geometry)
    k = g10[g10["ID_UNICO"].str.startswith("1KME") & g10["centroide_no_municipio"]].copy()
    maes = set(k["ID_UNICO"]) - set(g22["ID_UNICO"])
    urb = m22[m22["situacao"].str.lower().str.startswith("urb")].union_all()
    k["a_urb"] = medidas.areas_m2(k.geometry.intersection(urb)).values
    out = {"regra_das_notas": "célula de 1 km de 2010 que passou a intersectar setor urbano de 2022 "
                              "é dividida em 200 m; não há o inverso",
           "maes_observadas_em_bage": len(maes)}
    for limiar in (0, 1, 10_000):
        prev = set(k.loc[k["a_urb"] > limiar, "ID_UNICO"])
        out[f"previstas_intersecao_>_{limiar}_m2"] = {"previstas": len(prev), "coincidem": len(prev & maes),
                                                     "so_previstas": len(prev - maes),
                                                     "so_observadas": len(maes - prev)}
    out["menor_intersecao_urbana_de_uma_mae_m2"] = round(float(k.loc[k["ID_UNICO"].isin(maes), "a_urb"].min()), 3)
    out["celulas_200m_de_2010_que_viraram_1km"] = int(
        (g10["ID_UNICO"].str.startswith("200M") & ~g10["ID_UNICO"].isin(set(g22["ID_UNICO"]))).sum())
    out["crs_medicao_area"] = medidas.crs_medicao_area()
    return out


# --------------------------------------------------------------------------
# cruzamento com as classes e efeito nos números
# --------------------------------------------------------------------------

def numeros_s1(u: pd.DataFrame) -> dict:
    ganho = u[u["d_dom"] > 0]
    bruto = int(ganho["d_dom"].sum())
    novas = int(ganho.loc[ganho["classe"] == "nova", "d_dom"].sum())
    harm = int(ganho.loc[(ganho["classe"] == "adensada") & ganho["harmonizada"], "d_dom"].sum())
    ext = u[u["classe"] == "extinta"]
    return {"unidades": int(len(u)), "ganho_bruto": bruto, "perda_bruta": int(-u.loc[u["d_dom"] < 0, "d_dom"].sum()),
            "domicilios_2010": int(u["dom_10"].sum()), "saldo": int(u["d_dom"].sum()),
            "novas": int((u["classe"] == "nova").sum()), "dom_novas": novas,
            "adensadas": int((u["classe"] == "adensada").sum()),
            "ganho_adensadas": int(ganho.loc[ganho["classe"] == "adensada", "d_dom"].sum()),
            "extintas": int(len(ext)), "dom_10_extintas": int(ext["dom_10"].sum()),
            "expansao_pct_inferior": round(100 * novas / bruto, 1) if bruto else None,
            "expansao_pct_superior": round(100 * (novas + harm) / bruto, 1) if bruto else None}


def cruzamento(u: gpd.GeoDataFrame, g10: gpd.GeoDataFrame, b10: pd.Series, c10: pd.Series,
               apoio: gpd.GeoDataFrame) -> dict:
    cel = g10.assign(b=b10.values, a=c10.values)[["ID_UNICO", "setor", "situacao_setor", "inteira", "b", "a"]]
    setores_b = set(cel.loc[cel["b"], "setor"])
    x = u.merge(cel.rename(columns={"ID_UNICO": "unidade"}), on="unidade", how="left")
    x["assinatura"] = np.where(x["b"].fillna(False).astype(bool), "desagregacao", "indeterminada")
    x["setor_com_assinatura"] = x["setor"].isin(setores_b)
    ap = apoio.set_index("unidade")
    ext = x[x["classe"] == "extinta"].copy()
    ext["sem_endereco"] = ap["enderecos"].reindex(ext["unidade"]).values == 0
    ext["com_domicilio"] = (ap["domicilio_particular"] + ap["domicilio_coletivo"]).reindex(ext["unidade"]).values > 0

    def conta(s: pd.DataFrame) -> dict:
        return {"unidades": int(len(s)),
                "assinatura_desagregacao": int((s["assinatura"] == "desagregacao").sum()),
                "em_setor_com_assinatura": int(s["setor_com_assinatura"].sum()),
                "dom_10_em_setor_com_assinatura": int(s.loc[s["setor_com_assinatura"], "dom_10"].sum()),
                "compativeis_teste_a_descartado": int(s["a"].fillna(False).astype(bool).sum())}

    por_classe = {k: conta(x[x["classe"] == k]) for k in CLASSES}
    por_classe["extinta"]["sem_nenhum_endereco_cnefe"] = conta(ext[ext["sem_endereco"]])
    por_classe["extinta"]["com_domicilio_cnefe"] = conta(ext[ext["com_domicilio"]])

    base = numeros_s1(x)
    sem_b = numeros_s1(x[x["assinatura"] != "desagregacao"])
    sem_setor = numeros_s1(x[~x["setor_com_assinatura"]])
    return {
        "setores_com_assinatura": sorted(setores_b),
        "por_classe": por_classe,
        "efeito_nos_numeros_da_subordinada_1": {
            "todas_as_unidades": base,
            "sem_as_celulas_com_assinatura": sem_b,
            "sem_as_unidades_dos_setores_com_assinatura": sem_setor,
            "leitura": "unidades harmonizadas; setor de 2010 = o de maior área; unidades sem "
                       "setor de 2010 com domicílio (vazias em 2010) ficam em 'indeterminada'"},
    }


def totais_municipio(g10: gpd.GeoDataFrame, b10: pd.Series) -> dict:
    setores_b = set(g10.loc[b10, "setor"])
    out = {}
    com = g10["dom"] > 0
    for nome, m in (("assinatura_desagregacao", b10 & com), ("indeterminada", ~b10 & com),
                    ("em_setor_com_assinatura", g10["setor"].isin(setores_b) & com)):
        out[nome] = {"celulas": int(m.sum()), "domicilios": int(g10.loc[m, "dom"].sum()),
                     "populacao": int(g10.loc[m, "pop"].sum())}
    out["total"] = {"celulas": int(com.sum()), "domicilios": int(g10["dom"].sum()),
                    "populacao": int(g10["pop"].sum())}
    return out


# --------------------------------------------------------------------------

def main() -> None:
    area = paths.carregar_area_estudo()
    ms = malhas(area.crs)
    r10, r22 = razoes_2010(), razoes_2022()
    g10 = celulas("2010", area, ms["2010"], r10)
    g22 = celulas("2022", area, ms["2022"], r22)

    com10, com22 = g10["dom"] > 0, g22["dom"] > 0
    a, c = teste_a(g10[com10], g22[com22], r10)
    c10 = c.reindex(g10.index, fill_value=False)
    b10, b22 = teste_b(g10), teste_b(g22)
    u = conferida(CAMADA)
    apoio = conferida(APOIO)

    resultado = {
        "natureza": "INDÍCIO; não é a variável oficial de abordagem (IBGE 2016, p. 21), que não "
                    "acompanha os arquivos do geoftp",
        "celulas_com_domicilio_no_municipio": {"2010": int(com10.sum()), "2022": int(com22.sum())},
        "teste_a_razao_do_setor": a,
        "teste_b_pares_identicos_contiguos": {
            "regra": f"DOM >= {DOM_MIN_B}, célula inteira num setor, par (DOM, POP) idêntico numa "
                     "vizinha rainha inteira no mesmo setor",
            "2010": resumo_b(g10, b10), "2022": resumo_b(g22, b22)},
        "classificacao_das_celulas_2010": {
            "regra": "assinatura de desagregação = teste B positivo; assinatura de agregação: "
                     "nenhuma célula (nenhum teste separa agregação do resto; ver resultados_s1.md "
                     "§ 10); indeterminada = as demais",
            "celulas_com_domicilio": int(com10.sum()),
            "desagregacao": int(b10.sum()), "indeterminada": int((com10 & ~b10).sum()),
            "agregacao": 0},
        "totais_2010_por_assinatura": totais_municipio(g10, b10),
        "cruzamento_com_as_classes": cruzamento(u, g10, b10, c10, apoio),
        "upgrade_2022": upgrade(area, ms["2022"]),
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=int), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=int))


if __name__ == "__main__":
    main()
