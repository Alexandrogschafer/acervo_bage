"""
A03 — subordinada 1: expansão ou adensamento, na grade estatística 2010 × 2022.

UNIDADE HARMONIZADA
-------------------
A grade de 2022 NÃO é a de 2010 em toda parte: onde 2010 tinha uma célula de
1 km, 2022 pode ter as 25 células de 200 m que a compõem (a grade é aninhada).
Juntar as duas edições por `ID_UNICO` e tratar o ausente como zero — o que o
d03 fazia — transforma essa troca de resolução em "células novas" (as filhas de
200 m) e "células extintas" (a mãe de 1 km), sem que nada tenha mudado no
território. Aqui a comparação é feita sobre a UNIDADE HARMONIZADA:

    célula com o mesmo ID_UNICO nos dois anos    -> ela mesma
    célula de 2010 subdividida em 2022           -> a célula de 2010, com o
                                                    2022 = soma das filhas

O script EXIGE que cada célula que só existe numa edição esteja contida numa
célula da outra edição e que as filhas cubram exatamente a mãe (área em
crs.area). Sobra qualquer coisa: PARA e relata. A classificação ingênua (por
ID_UNICO) também é calculada, só para a conciliação com o d03.

RECORTE: a unidade é de Bagé quando seu CENTROIDE cai no município (a mesma
regra do d03, aplicada à unidade harmonizada).

CLASSES (sobre domicílios ocupados; `dom` = DOM_OCU em 2010, TOTAL_DOM em 2022):
    nova       dom_10 = 0 e dom_22 > 0
    adensada   dom_10 > 0 e dom_22 > dom_10
    estavel    dom_10 > 0 e dom_22 = dom_10
    esvaziada  dom_10 > 0 e 0 < dom_22 < dom_10
    extinta    dom_10 > 0 e dom_22 = 0
(unidades sem domicílio nos dois anos ficam fora da camada de trabalho)

REFERÊNCIAS DECLARADAS
- centro: centro médio dos domicílios de 2010 (centroides das unidades
  ponderados por dom_10), no CRS de produção. É do próprio dado, reprodutível,
  e anterior à mudança medida.
- área urbanizada de 2022: IBGE, Áreas Urbanizadas do Brasil 2022, polígonos de
  Bagé com Tipo = "Área urbanizada" (densa e pouco densa). Sensibilidade: todos
  os tipos (inclui "Loteamento vazio" e "Outros equipamentos urbanos"). Unidade
  DENTRO quando >= 50 % da sua área está na área urbanizada (área em crs.area).
- contiguidade: rainha (unidades que compartilham aresta ou vértice), com
  tolerância de 1 m para o arredondamento da reprojeção.

Distâncias no CRS de produção; áreas no CRS de área (scripts/utils/medidas.py).

UNIDADES À PARTE (desde 2026-09-23, resultados_s1.md § 11): a camada traz o campo
booleano `a_parte_setor_136`, verdadeiro nas unidades do setor rural de 2010
430160205000136, declarado à parte no cenário adotado. A lista vem de
derivados/s1_desagregacao_2010.json (cruzamento_com_as_classes.unidades_a_parte),
que por sua vez é calculado SOBRE esta camada. Ordem de execução:
    s1_expansao_adensamento.py -> s1_desagregacao_2010.py -> (de novo, se a lista
    mudou) s1_expansao_adensamento.py
O s1_desagregacao_2010.py confere que a marca da camada é igual à lista que ele
calcula e PARA se divergir. O campo não muda classe nenhuma.

LÊ data/raw/ (grades, área urbanizada), o acervo (limite, setores — pelo
catálogo, conferido), derivados/d01_descompasso.json e
derivados/s1_desagregacao_2010.json. ESCREVE só:
    saidas/s1_celulas_2010_2022.gpkg (+ .json irmão)   camada de trabalho
    derivados/s1_caracterizacao.json                  números
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
from shapely.geometry import Point  # noqa: E402

from grade_estatistica import ler_grade  # noqa: E402
from scripts.utils import catalogo, medidas, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

ESTUDO = Path(__file__).resolve().parents[1]
DERIV = ESTUDO / "derivados"
SAIDAS = ESTUDO / "saidas"
CAMADA = SAIDAS / "s1_celulas_2010_2022.gpkg"

AU_ZIP = paths.caminho("raw_vetor", "ibge", "areas_urbanizadas_2022",
                       "AreasUrbanizadas2022_Brasil.zip")
AU_SHP = "AreasUrbanizadas2022_Brasil/AU_2026_AreasUrbanizadas_2022_Brasil.shp"
TIPO_URBANIZADA = "Área urbanizada"
LIMIAR_DENTRO = 0.5
TOLERANCIA_CONTIGUIDADE_M = 1.0
FAIXAS_KM = [0, 1, 2, 3, 4, 6, 10, np.inf]

CLASSES = ["nova", "adensada", "estavel", "esvaziada", "extinta"]
DESAG = DERIV / "s1_desagregacao_2010.json"
CAMPO_A_PARTE = "a_parte_setor_136"
CHAVE_CONFERENCIAS = "conferencias_visuais_do_responsavel"
FONTES = "ibge_grade_estatistica_2010;ibge_grade_estatistica_2022"


# --------------------------------------------------------------------------
# harmonização
# --------------------------------------------------------------------------

def resolucao(ids: pd.Series) -> pd.Series:
    return ids.str[:4].map({"200M": "200 m", "1KME": "1 km"})


def harmonizar(g10: gpd.GeoDataFrame, g22: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """Unidades comparáveis entre as edições (ver docstring). Para se sobrar célula."""
    ids10, ids22 = set(g10["ID_UNICO"]), set(g22["ID_UNICO"])
    so10 = g10[~g10["ID_UNICO"].isin(ids22)].copy()
    so22 = g22[~g22["ID_UNICO"].isin(ids10)].copy()

    def filhas_de(maes: gpd.GeoDataFrame, filhas: gpd.GeoDataFrame) -> pd.DataFrame:
        pontos = filhas.copy()
        pontos["geometry"] = filhas.geometry.representative_point()
        j = gpd.sjoin(pontos[["ID_UNICO", "geometry"]],
                      maes[["ID_UNICO", "geometry"]].rename(columns={"ID_UNICO": "mae"}),
                      predicate="within", how="left")
        return j[["ID_UNICO", "mae"]]

    # mãe = célula de 1 km; filha = célula de 200 m (a grade é aninhada)
    grossa10 = so10[so10["ID_UNICO"].str.startswith("1KME")]
    fina22 = so22[so22["ID_UNICO"].str.startswith("200M")]
    grossa22 = so22[so22["ID_UNICO"].str.startswith("1KME")]
    fina10 = so10[so10["ID_UNICO"].str.startswith("200M")]
    if len(grossa22) or len(fina10):
        # 2010 fina -> 2022 grossa: não observado; não tratado aqui
        raise SystemExit(f"PARADO — há {len(fina10)} células de 200 m só em 2010 e "
                         f"{len(grossa22)} de 1 km só em 2022; o script só trata a "
                         "subdivisão 2010 (1 km) -> 2022 (200 m).")
    f22 = filhas_de(grossa10, fina22)    # filhas de 2022 dentro de mães de 2010
    orfas22 = f22[f22["mae"].isna()]["ID_UNICO"].tolist()
    orfas10 = sorted(set(grossa10["ID_UNICO"]) - set(f22["mae"].dropna()))
    if orfas22 or orfas10:
        raise SystemExit(f"PARADO — células sem correspondência: só em 2022 {orfas22[:10]}, "
                         f"só em 2010 {orfas10[:10]}")

    # as filhas cobrem exatamente a mãe?
    area_maes = pd.Series(medidas.areas_m2(so10.geometry).values, index=so10["ID_UNICO"])
    area_filhas = pd.Series(medidas.areas_m2(so22.geometry).values, index=so22["ID_UNICO"])
    soma_filhas = area_filhas.groupby(f22.set_index("ID_UNICO")["mae"]).sum()
    n_filhas = f22.groupby("mae").size()
    desvio = (soma_filhas - area_maes.loc[soma_filhas.index]).abs()
    if float(desvio.max()) > 50.0:
        raise SystemExit(f"PARADO — filhas não cobrem a mãe (desvio máximo "
                         f"{float(desvio.max()):.1f} m²)")

    vals22 = so22.set_index("ID_UNICO")[["pop", "dom"]]
    agreg = vals22.groupby(f22.set_index("ID_UNICO")["mae"]).sum()

    comuns = (g10.set_index("ID_UNICO")[["pop", "dom", "geometry"]]
              .join(g22.set_index("ID_UNICO")[["pop", "dom"]], rsuffix="_22", how="inner"))
    comuns = comuns.rename(columns={"pop": "pop_10", "dom": "dom_10"})
    comuns["harmonizada"] = False
    maes = so10.set_index("ID_UNICO")[["pop", "dom", "geometry"]].rename(
        columns={"pop": "pop_10", "dom": "dom_10"})
    maes = maes.join(agreg.rename(columns={"pop": "pop_22", "dom": "dom_22"}))
    maes["harmonizada"] = True
    unidades = pd.concat([comuns, maes])
    unidades.index.name = "unidade"
    unidades = gpd.GeoDataFrame(unidades.reset_index(), geometry="geometry", crs=g10.crs)
    unidades["resolucao"] = resolucao(unidades["unidade"])
    unidades.loc[unidades["harmonizada"], "resolucao"] = "1 km (2022 em 200 m)"

    relatorio = {
        "celulas_comuns": int(len(comuns)),
        "celulas_2010_subdivididas_em_2022": int(len(maes)),
        "filhas_2022_por_mae": sorted({int(v) for v in n_filhas}),
        "celulas_2022_filhas": int(len(so22)),
        "desvio_maximo_area_filhas_x_mae_m2": round(float(desvio.max()), 3),
        "crs_medicao_area": medidas.crs_medicao_area(),
        "celulas_de_2010_contidas_em_2022": 0,
    }
    return unidades, relatorio


def classificar(dom10: pd.Series, dom22: pd.Series) -> pd.Series:
    c = pd.Series(pd.NA, index=dom10.index, dtype="object")
    c[(dom10 == 0) & (dom22 > 0)] = "nova"
    c[(dom10 > 0) & (dom22 > dom10)] = "adensada"
    c[(dom10 > 0) & (dom22 == dom10)] = "estavel"
    c[(dom10 > 0) & (dom22 > 0) & (dom22 < dom10)] = "esvaziada"
    c[(dom10 > 0) & (dom22 == 0)] = "extinta"
    return c


def classificacao_ingenua(g10: gpd.GeoDataFrame, g22: gpd.GeoDataFrame) -> dict:
    """O que o d03 media: junção por ID_UNICO, ausente = 0 (só para conciliar)."""
    a = g10[g10["centroide_no_municipio"]].set_index("ID_UNICO")[["dom"]]
    b = g22[g22["centroide_no_municipio"]].set_index("ID_UNICO")[["dom"]]
    j = a.join(b, how="outer", lsuffix="_10", rsuffix="_22").fillna(0)
    c = classificar(j["dom_10"], j["dom_22"]).dropna()
    # célula que só existe numa edição: é a mãe de 1 km (2010) ou uma filha de 200 m (2022)
    so_numa_edicao = pd.Series(~j.index.isin(a.index) | ~j.index.isin(b.index),
                               index=j.index).loc[c.index]
    return {k: {"celulas": int((c == k).sum()),
                "celulas_de_troca_de_resolucao": int(((c == k) & so_numa_edicao).sum())}
            for k in CLASSES}


# --------------------------------------------------------------------------
# caracterização
# --------------------------------------------------------------------------

def agrupamentos(geoms: gpd.GeoSeries) -> np.ndarray:
    """Rótulo de agrupamento contíguo (rainha, tolerância de 1 m) por unidade."""
    geoms = geoms.reset_index(drop=True)
    arvore = shapely.STRtree(geoms.values)
    a, b = arvore.query(geoms.buffer(TOLERANCIA_CONTIGUIDADE_M).values, predicate="intersects")
    pai = list(range(len(geoms)))

    def raiz(i: int) -> int:
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i
    for i, j in zip(a, b):
        ri, rj = raiz(int(i)), raiz(int(j))
        if ri != rj:
            pai[ri] = rj
    raizes = [raiz(i) for i in range(len(geoms))]
    mapa = {r: k for k, r in enumerate(dict.fromkeys(raizes))}
    return np.array([mapa[r] for r in raizes])


def resumo_distancia(d_km: pd.Series, peso: pd.Series) -> dict:
    ordem = np.argsort(d_km.values)
    acum = np.cumsum(peso.values[ordem]) / peso.sum()
    mediana_ponderada = float(d_km.values[ordem][np.searchsorted(acum, 0.5)])
    faixas = pd.cut(d_km, FAIXAS_KM, right=False)
    tab = pd.DataFrame({"unidades": d_km.groupby(faixas, observed=False).size(),
                        "domicilios": peso.groupby(faixas, observed=False).sum()})
    return {
        "mediana_km": round(float(d_km.median()), 2),
        "p25_km": round(float(d_km.quantile(0.25)), 2),
        "p75_km": round(float(d_km.quantile(0.75)), 2),
        "maximo_km": round(float(d_km.max()), 2),
        "mediana_ponderada_por_domicilio_km": round(mediana_ponderada, 2),
        "faixas": [{"faixa_km": f"{i.left:g}–{i.right:g}" if np.isfinite(i.right) else f">= {i.left:g}",
                    "unidades": int(r.unidades), "domicilios": int(r.domicilios)}
                   for i, r in tab.iterrows()],
    }


def caracterizar(u: gpd.GeoDataFrame, classe: str, peso_col: str) -> dict:
    s = u[u["classe"] == classe]
    peso = s[peso_col]
    rot = agrupamentos(s.geometry)
    grupos = (pd.DataFrame({"g": rot, "dom": peso.values, "area": s["area_m2"].values})
              .groupby("g").agg(unidades=("dom", "size"), domicilios=("dom", "sum"),
                                area_km2=("area", lambda x: x.sum() / 1e6))
              .sort_values(["unidades", "domicilios"], ascending=False))
    dentro = s["fracao_au"] >= LIMIAR_DENTRO
    dentro_todos = s["fracao_au_todos_tipos"] >= LIMIAR_DENTRO
    return {
        "unidades": int(len(s)),
        "peso": f"{peso_col} (domicílios {'de 2022' if peso_col == 'dom_22' else 'de 2010'})",
        "distancia_ao_centro": resumo_distancia(s["dist_centro_km"], peso),
        "contiguidade": {
            "agrupamentos": int(len(grupos)),
            "unidades_isoladas": int((grupos["unidades"] == 1).sum()),
            "maior_agrupamento": {"unidades": int(grupos["unidades"].iloc[0]),
                                  "domicilios": int(grupos["domicilios"].iloc[0])},
            "pct_domicilios_no_maior": round(100 * grupos["domicilios"].iloc[0] / peso.sum(), 1),
            "tamanhos_dos_10_maiores": [
                {"unidades": int(r.unidades), "domicilios": int(r.domicilios),
                 "area_km2": round(float(r.area_km2), 2)} for r in grupos.head(10).itertuples()],
            "distribuicao_de_tamanho": {
                "1": int((grupos["unidades"] == 1).sum()),
                "2-4": int(grupos["unidades"].between(2, 4).sum()),
                "5-9": int(grupos["unidades"].between(5, 9).sum()),
                "10-49": int(grupos["unidades"].between(10, 49).sum()),
                ">=50": int((grupos["unidades"] >= 50).sum())},
        },
        "area_urbanizada_2022": {
            "regra": f"dentro = >= {int(LIMIAR_DENTRO * 100)} % da área da unidade na área urbanizada",
            "dentro": {"unidades": int(dentro.sum()), "domicilios": int(peso[dentro].sum())},
            "fora": {"unidades": int((~dentro).sum()), "domicilios": int(peso[~dentro].sum())},
            "pct_domicilios_dentro": round(100 * peso[dentro].sum() / peso.sum(), 1),
            "toca_a_area_urbanizada": int((s["fracao_au"] > 0).sum()),
            "sensibilidade_todos_os_tipos": {
                "dentro": {"unidades": int(dentro_todos.sum()),
                           "domicilios": int(peso[dentro_todos].sum())},
                "pct_domicilios_dentro": round(100 * peso[dentro_todos].sum() / peso.sum(), 1)},
        },
        "por_resolucao": {r: int(n) for r, n in s["resolucao"].value_counts().items()},
    }


def faixa_expansao(u: gpd.GeoDataFrame) -> dict:
    """Quanto do ganho bruto é expansão, com a incerteza da resolução de 1 km.

    Uma unidade de 1 km que já tinha domicílio e ganhou é "adensada" nesta
    resolução, mas pode conter ocupação nova dentro dela. As 41 harmonizadas são
    as que o IBGE passou a gradear em 200 m em 2022 — onde a urbanização chegou.
    Limite inferior: só as unidades novas. Superior: novas + ganho das adensadas
    harmonizadas.
    """
    ganho = u[u["d_dom"] > 0]
    novas = int(ganho.loc[ganho["classe"] == "nova", "d_dom"].sum())
    ad = ganho[ganho["classe"] == "adensada"]
    por_res = {r: {"unidades": int((ad["resolucao"] == r).sum()),
                   "domicilios_ganhos": int(ad.loc[ad["resolucao"] == r, "d_dom"].sum())}
               for r in ("200 m", "1 km", "1 km (2022 em 200 m)")}
    harm = por_res["1 km (2022 em 200 m)"]["domicilios_ganhos"]
    bruto = int(ganho["d_dom"].sum())
    return {
        "ganho_bruto_de_domicilios": bruto,
        "em_unidades_novas": novas,
        "em_unidades_adensadas": int(ad["d_dom"].sum()),
        "adensadas_por_resolucao": por_res,
        "expansao_pct_limite_inferior": round(100 * novas / bruto, 1),
        "expansao_pct_limite_superior": round(100 * (novas + harm) / bruto, 1),
        "leitura": "inferior = só unidades novas; superior = novas + ganho das adensadas "
                   "de 1 km que o IBGE subdividiu em 200 m em 2022",
    }


def dispersao(serie: pd.Series) -> dict:
    """Como no d03: perdas entram em valor absoluto (mediana, p90 e máximo)."""
    return {"n": int(len(serie)), "soma": int(serie.sum()),
            "mediana": float(serie.median()) if len(serie) else None,
            "p90": round(float(serie.quantile(0.90)), 1) if len(serie) else None,
            "maximo": int(serie.max()) if len(serie) else None}


def movimento_e_divergencia(u: gpd.GeoDataFrame) -> dict:
    """O dimensionamento § 3.3 refeito na unidade harmonizada (resultados_s1.md § 8).

    Mesmas regras do d03, aplicadas às unidades com domicílio em algum dos dois
    anos: ganho/perda bruta de domicílios e de população e divergência de sinal.
    """
    g_dom, p_dom = u.loc[u["d_dom"] > 0, "d_dom"], u.loc[u["d_dom"] < 0, "d_dom"]
    g_pop, p_pop = u.loc[u["d_pop"] > 0, "d_pop"], u.loc[u["d_pop"] < 0, "d_pop"]
    div = u[(u["d_dom"] > 0) & (u["d_pop"] < 0)]
    inv = u[(u["d_dom"] < 0) & (u["d_pop"] > 0)]
    return {
        "unidades_com_domicilio_em_algum_ano": int(len(u)),
        "domicilios": {"ganharam": dispersao(g_dom), "perderam": dispersao(p_dom.abs()),
                       "sem_mudanca": int((u["d_dom"] == 0).sum())},
        "populacao": {"ganharam": dispersao(g_pop), "perderam": dispersao(p_pop.abs()),
                      "sem_mudanca": int((u["d_pop"] == 0).sum())},
        "movimento_bruto_de_domicilios": int(g_dom.sum() + p_dom.abs().sum()),
        "saldo_de_domicilios": int(u["d_dom"].sum()),
        "saldo_de_populacao": int(u["d_pop"].sum()),
        "divergencia_de_sinal": {
            "ganham_domicilio_e_perdem_populacao": {
                "unidades": int(len(div)),
                "pct_das_unidades": round(100 * len(div) / len(u), 1),
                "domicilios_ganhos": int(div["d_dom"].sum()),
                "populacao_perdida": int(div["d_pop"].sum())},
            "perdem_domicilio_e_ganham_populacao": {
                "unidades": int(len(inv)),
                "pct_das_unidades": round(100 * len(inv) / len(u), 1)},
        },
    }


def troca_de_resolucao(g10: gpd.GeoDataFrame, g22: gpd.GeoDataFrame) -> dict:
    """Mães e filhas em Bagé, nas edições como o IBGE as publica (resultados_s1.md § 8).

    Cada edição recortada pelo centroide da própria célula (regra do d03): as
    células só em 2010 são as mães de 1 km; as só em 2022, as filhas de 200 m.
    """
    a = g10[g10["centroide_no_municipio"]]
    b = g22[g22["centroide_no_municipio"]]
    maes = a[~a["ID_UNICO"].isin(set(b["ID_UNICO"]))]
    filhas = b[~b["ID_UNICO"].isin(set(a["ID_UNICO"]))]

    def resumo(g: gpd.GeoDataFrame) -> dict:
        return {"celulas": int(len(g)),
                "resolucoes": sorted(set(resolucao(g["ID_UNICO"]).dropna())),
                "com_domicilio": int((g["dom"] > 0).sum()),
                "domicilios": int(g["dom"].sum()), "populacao": int(g["pop"].sum())}
    return {
        "recorte": "centroide da célula no município, em cada edição",
        "celulas_de_mesmo_id": int(a["ID_UNICO"].isin(set(b["ID_UNICO"])).sum()),
        "maes_2010": resumo(maes),
        "filhas_2022": resumo(filhas),
    }


def densidade(u: gpd.GeoDataFrame) -> list[dict]:
    linhas = []
    for classe in CLASSES:
        s = u[u["classe"] == classe]
        for res in ("200 m", "1 km (inclui harmonizadas)"):
            r = s[s["resolucao"] == "200 m"] if res == "200 m" else s[s["resolucao"] != "200 m"]
            if not len(r):
                continue
            km2 = r["area_m2"].sum() / 1e6
            linhas.append({
                "classe": classe, "resolucao": res, "unidades": int(len(r)),
                "area_km2": round(km2, 2),
                "dom_por_km2_2010": round(r["dom_10"].sum() / km2, 1),
                "dom_por_km2_2022": round(r["dom_22"].sum() / km2, 1),
                "mediana_dom_por_unidade_2010": float(r["dom_10"].median()),
                "mediana_dom_por_unidade_2022": float(r["dom_22"].median()),
            })
    return linhas


# --------------------------------------------------------------------------

def conferencias_visuais_anteriores() -> dict:
    """Registro das conferências visuais do responsável, preservado entre execuções.

    Decisão do responsável (2026-09-23): a conferência visual da camada de trabalho
    fica em `verificacoes.conferencias_visuais_do_responsavel`, e NÃO no bloco
    "--- conferência ---" de `observacoes`, que só `scripts/utils/promover.py`
    grava e que promoveria a camada. O registro é do responsável: o script o
    carrega do `.json` anterior sem alterar, seja qual for o conteúdo novo.
    """
    if not metadados.caminho_irmao(CAMADA).exists():
        return {}
    anteriores = metadados.ler(CAMADA).get("verificacoes", {}).get(CHAVE_CONFERENCIAS)
    return {CHAVE_CONFERENCIAS: anteriores} if anteriores else {}


def marca_a_parte(unidades: pd.Series) -> pd.Series:
    """Unidades à parte no cenário adotado, lidas de s1_desagregacao_2010.json."""
    if not DESAG.exists():
        raise SystemExit(f"PARADO — falta {DESAG.name}: rodar s1_desagregacao_2010.py")
    lista = set(json.loads(DESAG.read_text(encoding="utf-8"))
                ["cruzamento_com_as_classes"]["unidades_a_parte"])
    fora = lista - set(unidades)
    if fora:
        raise SystemExit(f"PARADO — {len(fora)} unidades à parte fora da camada: {sorted(fora)[:5]}")
    return unidades.isin(lista)


def main() -> None:
    area = paths.carregar_area_estudo()
    limite = area.union_all()
    bruto10 = ler_grade("2010", area.geometry)
    bruto22 = ler_grade("2022", area.geometry)

    unidades, harmonizacao = harmonizar(bruto10, bruto22)
    unidades["centroide_no_municipio"] = unidades.geometry.centroid.within(limite)
    u = unidades[unidades["centroide_no_municipio"]].copy()
    total_grade = {"2010": {"populacao": int(u["pop_10"].sum()), "domicilios": int(u["dom_10"].sum())},
                   "2022": {"populacao": int(u["pop_22"].sum()), "domicilios": int(u["dom_22"].sum())}}

    u["classe"] = classificar(u["dom_10"], u["dom_22"])
    u = u[u["classe"].notna()].copy()
    for c in ("pop_10", "pop_22", "dom_10", "dom_22"):
        u[c] = u[c].astype(int)
    u["d_dom"] = u["dom_22"] - u["dom_10"]
    u["d_pop"] = u["pop_22"] - u["pop_10"]
    u["dr_dom"] = np.where(u["dom_10"] > 0, u["d_dom"] / u["dom_10"].where(u["dom_10"] > 0), np.nan)
    u["dr_pop"] = np.where(u["pop_10"] > 0, u["d_pop"] / u["pop_10"].where(u["pop_10"] > 0), np.nan)
    u["area_m2"] = medidas.areas_m2(u.geometry).values

    # centro: centro médio dos domicílios de 2010
    cent = u.geometry.centroid
    centro = Point(float(np.average(cent.x, weights=u["dom_10"])),
                   float(np.average(cent.y, weights=u["dom_10"])))
    u["dist_centro_km"] = cent.distance(centro) / 1e3
    _, arq_setores = catalogo.camada_conferida("setores_2022")
    setores = gpd.read_file(arq_setores).to_crs(u.crs)
    setor_centro = setores[setores.contains(centro)]
    # sensibilidade: o mesmo centro só com as unidades de 200 m (a grade urbana)
    urb = u["resolucao"] == "200 m"
    centro_200m = Point(float(np.average(cent[urb].x, weights=u.loc[urb, "dom_10"])),
                        float(np.average(cent[urb].y, weights=u.loc[urb, "dom_10"])))

    # área urbanizada 2022
    au_todos = gpd.read_file(f"/vsizip/{AU_ZIP}/{AU_SHP}",
                             bbox=tuple(area.to_crs("EPSG:4674").total_bounds)).to_crs(u.crs)
    au_todos = au_todos[au_todos.intersects(limite)]
    au = au_todos[au_todos["Tipo"] == TIPO_URBANIZADA]
    for nome, camada in (("fracao_au", au), ("fracao_au_todos_tipos", au_todos)):
        uniao = camada.union_all()
        inter = u.geometry.intersection(uniao)
        u[nome] = (medidas.areas_m2(inter).values / u["area_m2"]).round(4)

    # conferência contra o município
    muni = json.loads((DERIV / "d01_descompasso.json").read_text(encoding="utf-8"))
    ref = {"2010": {"populacao": muni["censo_2010"]["total"]["populacao"],
                    "domicilios": muni["censo_2010"]["total"]["dpp_ocupados"]},
           "2022": {"populacao": muni["censo_2022"]["total"]["populacao"],
                    "domicilios": muni["censo_2022"]["total"]["dp_ocupados_dppo_mais_dpio"]}}
    conferencia = {ano: {v: {"grade": total_grade[ano][v], "municipio": ref[ano][v],
                             "diferenca": total_grade[ano][v] - ref[ano][v],
                             "diferenca_pct": round(100 * (total_grade[ano][v] - ref[ano][v])
                                                    / ref[ano][v], 2)}
                         for v in ("populacao", "domicilios")} for ano in ("2010", "2022")}

    por_classe = (u.groupby("classe")
                  .agg(unidades=("unidade", "size"), dom_2010=("dom_10", "sum"),
                       dom_2022=("dom_22", "sum"), pop_2010=("pop_10", "sum"),
                       pop_2022=("pop_22", "sum"), d_dom=("d_dom", "sum"), d_pop=("d_pop", "sum"),
                       area_km2=("area_m2", lambda x: x.sum() / 1e6))
                  .reindex(CLASSES))
    ingenua = classificacao_ingenua(bruto10, bruto22)

    resultado = {
        "harmonizacao": harmonizacao,
        "recorte": "centroide da unidade harmonizada no município (config/area_estudo.geojson)",
        "unidades_no_municipio": int(u.shape[0]) ,
        "unidades_harmonizadas_com_domicilio": int(u["harmonizada"].sum()),
        "conferencia_contra_o_municipio": conferencia,
        "fonte_do_total_municipal": "derivados/d01_descompasso.json (2010: dpp_ocupados; "
                                    "2022: dp_ocupados_dppo_mais_dpio)",
        "por_classe": [{"classe": k, **{c: (round(float(v), 2) if c == "area_km2" else int(v))
                                        for c, v in r.items()}}
                       for k, r in por_classe.iterrows()],
        "conciliacao_com_d03": {
            "d03_por_id_unico": {k: v["celulas"] for k, v in ingenua.items()},
            "d03_celulas_que_sao_troca_de_resolucao": {k: v["celulas_de_troca_de_resolucao"]
                                                       for k, v in ingenua.items()},
            "harmonizado": {k: int(por_classe.loc[k, "unidades"]) for k in CLASSES},
        },
        "centro": {
            "definicao": "centro médio dos domicílios de 2010 (centroides das unidades "
                         "ponderados por dom_10)",
            "crs": str(u.crs.to_string()),
            "x": round(centro.x, 1), "y": round(centro.y, 1),
            "setor_2022": (setor_centro["CD_SETOR"].iloc[0] if len(setor_centro) else None),
            "situacao_do_setor": (setor_centro["SITUACAO"].iloc[0] if len(setor_centro) else None),
            "observacao": "NM_BAIRRO está vazio nos 199 setores de 2022: o ponto é "
                          "identificado pelo setor, não pelo bairro",
            "sensibilidade_so_unidades_de_200m": {
                "x": round(centro_200m.x, 1), "y": round(centro_200m.y, 1),
                "distancia_ao_centro_km": round(centro_200m.distance(centro) / 1e3, 2)},
        },
        "faixa_da_expansao": faixa_expansao(u),
        "area_urbanizada_2022": {
            "fonte": "ibge_areas_urbanizadas_2022 (data/raw/vetor/ibge/areas_urbanizadas_2022/)",
            "tipo_usado": TIPO_URBANIZADA,
            "area_km2": round(float(medidas.areas_m2(au.geometry).sum() / 1e6), 2),
            "area_km2_todos_os_tipos": round(float(medidas.areas_m2(au_todos.geometry).sum() / 1e6), 2),
            "poligonos": int(len(au)), "poligonos_todos_os_tipos": int(len(au_todos)),
            "crs_medicao_area": medidas.crs_medicao_area(),
        },
        "caracterizacao": {
            "nova": caracterizar(u, "nova", "dom_22"),
            "adensada": caracterizar(u, "adensada", "dom_22"),
            "extinta": caracterizar(u, "extinta", "dom_10"),
        },
        "densidade_por_classe": densidade(u),
        "movimento_e_divergencia": movimento_e_divergencia(u),
        "troca_de_resolucao_em_bage": troca_de_resolucao(bruto10, bruto22),
        "moradores_por_classe": [
            {"classe": k, "pop_2010": int(r.pop_2010), "pop_2022": int(r.pop_2022),
             "d_pop": int(r.d_pop), "d_dom": int(r.d_dom),
             "moradores_por_domicilio_2010": (round(r.pop_2010 / r.dom_2010, 2) if r.dom_2010 else None),
             "moradores_por_domicilio_2022": (round(r.pop_2022 / r.dom_2022, 2) if r.dom_2022 else None)}
            for k, r in por_classe.iterrows()],
        "crs_medicao_area": medidas.crs_medicao_area(),
        "crs_medicao_distancia": paths.crs_producao(),
    }
    DERIV.mkdir(exist_ok=True)
    (DERIV / "s1_caracterizacao.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    # camada de trabalho (saidas/, fora do git) + .json irmão
    SAIDAS.mkdir(exist_ok=True)
    u[CAMPO_A_PARTE] = marca_a_parte(u["unidade"])
    colunas = ["unidade", "resolucao", "harmonizada", "dom_10", "dom_22", "pop_10", "pop_22",
               "d_dom", "d_pop", "dr_dom", "dr_pop", "classe", "area_m2", "dist_centro_km",
               "fracao_au", "fracao_au_todos_tipos", CAMPO_A_PARTE, "geometry"]
    saida = u[colunas].sort_values("unidade").reset_index(drop=True)
    if CAMADA.exists():
        CAMADA.unlink()
    saida.to_file(CAMADA, driver="GPKG", layer="s1_celulas_2010_2022")
    dados = metadados.montar(
        CAMADA, tema="censo", fonte_id=FONTES, versao="s1-v1", crs=paths.crs_producao(),
        licenca="IBGE — uso livre com citação da fonte", autorizacao_fonte=True,
        pode_publicar=False, status_conferencia="pendente",
        observacoes=(
            "Camada de TRABALHO do A03 (subordinada 1): unidade harmonizada da grade "
            "estatística 2010 × 2022 com domicílio em algum dos dois anos, restrita a Bagé "
            "(centroide). Classes nova/adensada/estavel/esvaziada/extinta sobre domicílios "
            "ocupados. Campo a_parte_setor_136: unidades do setor rural de 2010 "
            "430160205000136, à parte no cenário adotado (resultados_s1.md § 11). "
            "41 células de 1 km de 2010 subdivididas em 200 m em 2022 comparadas "
            "na célula de 1 km (2022 = soma das 25 filhas). Não conferida no mapa: não vai "
            "para o acervo antes da conferência visual do responsável. Script: "
            "estudos/A03_expansao_adensamento/scripts/s1_expansao_adensamento.py."),
    )
    dados["sha256_conteudo"] = sha256_conteudo(CAMADA)
    dados["verificacoes"] = {"unidades": int(len(saida)),
                             "unidades_a_parte_setor_136": int(saida[CAMPO_A_PARTE].sum()),
                             "conferencia_contra_o_municipio": conferencia,
                             "crs_medicao_area": medidas.crs_medicao_area(),
                             **conferencias_visuais_anteriores()}
    metadados.escrever(CAMADA, dados, sobrescrever=True)

    print("harmonização:", harmonizacao)
    print("conferência:", json.dumps(conferencia, ensure_ascii=False))
    print(por_classe.to_string())
    print("conciliação d03:", resultado["conciliacao_com_d03"])
    print("centro:", resultado["centro"])
    print("movimento e divergência:", json.dumps(resultado["movimento_e_divergencia"],
                                                ensure_ascii=False))
    print("troca de resolução:", resultado["troca_de_resolucao_em_bage"])


if __name__ == "__main__":
    main()
