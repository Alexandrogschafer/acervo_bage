"""
A03 — subordinada 1: investigação das 232 unidades "extintas".

Motivo: a conferência visual do responsável (2026-09-23) apontou que parte das
unidades extintas está sobre áreas sem ocupação visível em imagem de satélite.
Este script INVESTIGA; não reclassifica nada e não altera a camada de trabalho
(lê `saidas/s1_celulas_2010_2022.gpkg` e confere o sha256_conteudo dela contra
o .json irmão antes de usar).

Itens (resultados_s1.md § 10):
  1. perfil das extintas: domicílios de 2010 por resolução e dentro/fora da
     área urbanizada de 2022 (mediana, p90, máximo; quantas com 1, 2, 3, <= 5);
  2. teste de deslocamento: saldo e ganho bruto de domicílios das vizinhas
     (rainha; raio de 1 e 2 km), comparado com o que a extinta perdeu, com
     linha de base (as mesmas medidas em torno de outras unidades de 1 km) e
     contagem de pares extinta–nova contra rótulos permutados;
  3. CNEFE 2022 dentro das extintas, por espécie e nível de geocodificação;
  4. (documentação — no resultados_s1.md, não medida aqui) e verificações de
     dado que a complementam: supressão de célula pequena nas duas edições,
     nível de geocodificação 5/6 no CNEFE, centroides dos setores de 2010;
  5. o mesmo olhar sobre as novas (o outro lado de um deslocamento).

VIZINHANÇA. O universo é o das unidades harmonizadas com centroide no
município (= as células de 2010 com centroide no município; ver
s1_expansao_adensamento.harmonizar). Unidade sem domicílio nos dois anos entra
com variação 0. Rainha: toca a unidade (tolerância de 1 m, a do s1). Raio R:
unidades cujo centroide está a até R da BORDA da unidade. Vizinhas fora do
município não entram (efeito de borda, declarado).

LÊ a camada de trabalho, data/raw/ (grade 2010, CNEFE 2022, malha de setores
2010), derivados/bage/c2010/Basico_RS.csv (do r00) e config/. ESCREVE só:
    derivados/s1_extintas.json                  números (versionado)
    derivados/s1_extintas_unidades.gpkg (+ .json irmão)   extintas e novas com
        as medidas por unidade, para a conferência no mapa (fora do git)
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402

from grade_estatistica import ler_grade  # noqa: E402
from s1_expansao_adensamento import LIMIAR_DENTRO, TOLERANCIA_CONTIGUIDADE_M, agrupamentos  # noqa: E402
from scripts.utils import hashes, medidas, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

ESTUDO = Path(__file__).resolve().parents[1]
DERIV = ESTUDO / "derivados"
CAMADA = ESTUDO / "saidas" / "s1_celulas_2010_2022.gpkg"
SAIDA_JSON = DERIV / "s1_extintas.json"
SAIDA_GPKG = DERIV / "s1_extintas_unidades.gpkg"

VET = paths.caminho("raw_vetor", "ibge")
DIR_CNEFE = VET / "censo_2022" / "cnefe"
MALHA_2010 = VET / "censo_2010" / "rs_setores_censitarios.zip"

RAIOS_M = (1000, 2000)
DISTANCIAS_PARES_M = (2000, 5000)
PERMUTACOES = 9999
SEMENTE = 20260923

ESPECIES = {"1": "domicilio_particular", "2": "domicilio_coletivo",
            "3": "estab_agropecuario", "4": "estab_ensino", "5": "estab_saude",
            "6": "estab_outras_finalidades", "7": "edificacao_em_construcao",
            "8": "estab_religioso"}
GRUPO_ESPECIE = {"1": "domicilio_particular", "2": "domicilio_coletivo",
                 "3": "estab_agropecuario"}      # o resto: "outros"


# --------------------------------------------------------------------------
# entradas
# --------------------------------------------------------------------------

def conferido(arquivo: Path) -> Path:
    """Arquivo bruto com o sha256 do .json irmão; para se divergir."""
    meta = metadados.ler(arquivo)
    if not hashes.confere(arquivo, meta["sha256"]):
        raise SystemExit(f"PARADO — {paths.relativo(arquivo)} diverge do sha256 do .json irmão")
    return arquivo


def ler_camada() -> gpd.GeoDataFrame:
    esperado = metadados.ler(CAMADA)["sha256_conteudo"]
    if sha256_conteudo(CAMADA) != esperado:
        raise SystemExit("PARADO — a camada de trabalho mudou desde o .json irmão; "
                         "rodar s1_expansao_adensamento.py antes")
    return gpd.read_file(CAMADA)


def universo(camada: gpd.GeoDataFrame, area: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Todas as unidades harmonizadas no município, com a camada por cima."""
    g10 = ler_grade("2010", area.geometry)
    g10 = g10[g10["centroide_no_municipio"]]
    u = (g10[["ID_UNICO", "geometry"]].rename(columns={"ID_UNICO": "unidade"})
         .merge(camada.drop(columns="geometry"), on="unidade", how="left"))
    fora = set(camada["unidade"]) - set(u["unidade"])
    if fora:
        raise SystemExit(f"PARADO — {len(fora)} unidades da camada fora do universo: {sorted(fora)[:5]}")
    u["classe"] = u["classe"].fillna("vazia")
    for c in ("dom_10", "dom_22", "pop_10", "pop_22", "d_dom"):
        u[c] = u[c].fillna(0).astype(int)
    u["resolucao"] = u["resolucao"].fillna("1 km")
    u.loc[u["unidade"].str.startswith("200M") & (u["classe"] == "vazia"), "resolucao"] = "200 m"
    u["res_grupo"] = np.where(u["resolucao"] == "200 m", "200 m", "1 km")
    u["dentro_au"] = u["fracao_au"].fillna(0) >= LIMIAR_DENTRO
    u["toca_limite"] = u.intersects(area.union_all().boundary)
    return gpd.GeoDataFrame(u.reset_index(drop=True), geometry="geometry", crs=area.crs)


def ler_cnefe(crs: str) -> gpd.GeoDataFrame:
    cand = sorted(DIR_CNEFE.glob(f"{paths.codigo_ibge()}_*.zip"))
    if len(cand) != 1:
        raise SystemExit(f"PARADO — esperado 1 arquivo CNEFE do município em {DIR_CNEFE}, há {len(cand)}")
    with zipfile.ZipFile(conferido(cand[0])) as z:
        membro = next(n for n in z.namelist() if n.endswith(".csv"))
        df = pd.read_csv(z.open(membro), sep=";", dtype=str, encoding="latin-1",
                         usecols=["COD_ESPECIE", "NV_GEO_COORD", "LATITUDE", "LONGITUDE"])
    # lido como SIRGAS 2000, como no r05 (o CSV não declara datum)
    return gpd.GeoDataFrame(
        df[["COD_ESPECIE", "NV_GEO_COORD"]],
        geometry=gpd.points_from_xy(pd.to_numeric(df["LONGITUDE"]), pd.to_numeric(df["LATITUDE"])),
        crs="EPSG:4674").to_crs(crs)


# --------------------------------------------------------------------------
# 1. perfil
# --------------------------------------------------------------------------

def perfil(s: pd.Series) -> dict:
    return {"unidades": int(len(s)), "domicilios": int(s.sum()),
            "mediana": float(s.median()) if len(s) else None,
            "p90": round(float(s.quantile(0.9)), 1) if len(s) else None,
            "maximo": int(s.max()) if len(s) else None,
            "com_1": int((s == 1).sum()), "com_2": int((s == 2).sum()),
            "com_3": int((s == 3).sum()), "ate_5": int((s <= 5).sum())}


def perfil_por_grupo(s: gpd.GeoDataFrame, col: str) -> dict:
    out = {"todas": perfil(s[col])}
    for res in ("200 m", "1 km"):
        r = s[s["res_grupo"] == res]
        out[res] = {"todas": perfil(r[col]),
                    "dentro_da_area_urbanizada": perfil(r.loc[r["dentro_au"], col]),
                    "fora_da_area_urbanizada": perfil(r.loc[~r["dentro_au"], col])}
    out["1 km"]["das_quais_harmonizadas"] = int((s["resolucao"] == "1 km (2022 em 200 m)").sum())
    return out


# --------------------------------------------------------------------------
# 2. vizinhança
# --------------------------------------------------------------------------

class Vizinhanca:
    def __init__(self, u: gpd.GeoDataFrame):
        self.geo = u.geometry.values
        self.arvore = shapely.STRtree(self.geo)
        self.arvore_c = shapely.STRtree(u.geometry.centroid.values)

    def de(self, i: int, modo: str | int) -> np.ndarray:
        if modo == "rainha":
            idx = self.arvore.query(shapely.buffer(self.geo[i], TOLERANCIA_CONTIGUIDADE_M),
                                    predicate="intersects")
        else:
            idx = self.arvore_c.query(shapely.buffer(self.geo[i], modo), predicate="intersects")
        return idx[idx != i]


def medir_vizinhanca(u: gpd.GeoDataFrame, viz: Vizinhanca, sel: np.ndarray, modo) -> pd.DataFrame:
    d, cl, d22 = u["d_dom"].values, u["classe"].values, u["dom_22"].values
    linhas = []
    for i in sel:
        v = viz.de(i, modo)
        dv = d[v]
        novas = v[cl[v] == "nova"]
        linhas.append({"i": i, "vizinhas": len(v), "saldo": int(dv.sum()),
                       "ganho_bruto": int(dv[dv > 0].sum()),
                       "novas_vizinhas": len(novas), "dom_22_nas_novas": int(d22[novas].sum())})
    return pd.DataFrame(linhas).set_index("i")


def resumo_deslocamento(m: pd.DataFrame, perda: pd.Series) -> dict:
    perda = perda.loc[m.index]
    s, g = m["saldo"], m["ganho_bruto"]
    return {
        "unidades": int(len(m)),
        "mediana_de_vizinhas": float(m["vizinhas"].median()),
        "saldo_das_vizinhas": {
            ">= perda": int((s >= perda).sum()),
            "entre 0 e perda (exclusive)": int(((s > 0) & (s < perda)).sum()),
            "= 0": int((s == 0).sum()),
            "< 0": int((s < 0).sum()),
            "quantis_p10_p25_p50_p75_p90": [round(float(x), 1) for x in s.quantile([.1, .25, .5, .75, .9])],
        },
        "ganho_bruto_das_vizinhas": {
            ">= perda": int((g >= perda).sum()),
            "= 0": int((g == 0).sum()),
            "quantis_p10_p25_p50_p75_p90": [round(float(x), 1) for x in g.quantile([.1, .25, .5, .75, .9])],
        },
        "com_unidade_nova_vizinha": int((m["novas_vizinhas"] > 0).sum()),
        "com_novas_vizinhas_somando_dom_22_>=_perda": int((m["dom_22_nas_novas"] >= perda).sum()),
    }


def linha_de_base(u: gpd.GeoDataFrame, viz: Vizinhanca) -> dict:
    """As medidas que não dependem da perda, em torno de outras unidades de 1 km."""
    grupos = {
        "extintas": (u["classe"] == "extinta"),
        "ocupadas_nao_extintas_nem_novas": u["classe"].isin(["adensada", "estavel", "esvaziada"]),
        "vazias_nos_dois_anos": (u["classe"] == "vazia"),
    }
    out = {}
    for nome, mask in grupos.items():
        sel = np.where(mask & (u["res_grupo"] == "1 km"))[0]
        out[nome] = {"unidades": int(len(sel))}
        for modo in ("rainha", *RAIOS_M):
            m = medir_vizinhanca(u, viz, sel, modo)
            out[nome][rotulo(modo)] = {
                "pct_saldo_das_vizinhas_>=_1": round(100 * float((m["saldo"] >= 1).mean()), 1),
                "pct_com_unidade_nova_vizinha": round(100 * float((m["novas_vizinhas"] > 0).mean()), 1),
            }
    return out


def rotulo(modo) -> str:
    return "rainha" if modo == "rainha" else f"raio_{modo // 1000}_km"


def pares_por_permutacao(u: gpd.GeoDataFrame) -> dict:
    """Pares de unidades de 1 km ocupadas em algum ano, por classe, contra rótulos permutados.

    Se a extinção fosse o mesmo domicílio posicionado em célula vizinha, pares
    extinta–nova apareceriam MAIS do que o acaso. O acaso é a permutação das
    classes entre as mesmas unidades (a geografia da ocupação fica fixa).
    """
    occ = u[(u["classe"] != "vazia") & (u["res_grupo"] == "1 km")].reset_index(drop=True)
    arvore = shapely.STRtree(occ.geometry.values)
    cent = occ.geometry.centroid
    arestas = {"rainha": arvore.query(occ.geometry.buffer(TOLERANCIA_CONTIGUIDADE_M).values,
                                      predicate="intersects")}
    arvore_c = shapely.STRtree(cent.values)
    for d in DISTANCIAS_PARES_M:
        arestas[f"centroides_a_ate_{d // 1000}_km"] = arvore_c.query(
            cent.values, predicate="dwithin", distance=d)
    combinacoes = [("extinta", "nova"), ("extinta", "extinta"), ("extinta", "esvaziada"),
                   ("nova", "nova")]
    rng = np.random.default_rng(SEMENTE)
    rotulos = occ["classe"].values
    perms = [rng.permutation(rotulos) for _ in range(PERMUTACOES)]
    out = {"unidades": int(len(occ)), "por_classe": occ["classe"].value_counts().to_dict(),
           "permutacoes": PERMUTACOES, "semente": SEMENTE}
    for nome, (a, b) in arestas.items():
        m = a < b
        a, b = a[m], b[m]
        out[nome] = {}
        for x, y in combinacoes:
            def conta(lab):
                return int((((lab[a] == x) & (lab[b] == y)) | ((lab[a] == y) & (lab[b] == x))).sum())
            obs = conta(rotulos)
            p = np.array([conta(lab) for lab in perms])
            out[nome][f"{x}-{y}"] = {
                "observados": obs, "esperado_media": round(float(p.mean()), 1),
                "p5_p95": [float(np.percentile(p, 5)), float(np.percentile(p, 95))],
                "p_mais_que_o_acaso": round(((p >= obs).sum() + 1) / (PERMUTACOES + 1), 4),
                "p_menos_que_o_acaso": round(((p <= obs).sum() + 1) / (PERMUTACOES + 1), 4)}
    return out


# --------------------------------------------------------------------------
# 3. CNEFE
# --------------------------------------------------------------------------

def cnefe_por_unidade(u: gpd.GeoDataFrame, pts: gpd.GeoDataFrame) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    j = gpd.sjoin(pts, u[["unidade", "geometry"]], predicate="within", how="inner")
    j["grupo"] = j["COD_ESPECIE"].map(GRUPO_ESPECIE).fillna("outros")
    tab = pd.crosstab(j["unidade"], j["COD_ESPECIE"]).rename(columns=ESPECIES)
    tab = tab.reindex(columns=list(ESPECIES.values()), fill_value=0)
    tab["outros"] = tab.drop(columns=list(GRUPO_ESPECIE.values())).sum(axis=1)
    tab["enderecos"] = tab[list(ESPECIES.values())].sum(axis=1)
    return tab, j


def resumo_cnefe(s: gpd.GeoDataFrame, j: gpd.GeoDataFrame) -> dict:
    """s: unidades da classe já com as contagens do CNEFE."""
    dp = s["domicilio_particular"]
    dom = dp + s["domicilio_coletivo"]
    pontos = j[j["unidade"].isin(set(s["unidade"]))]
    out = {
        "unidades": int(len(s)),
        "enderecos_por_grupo": {g: int(s[g].sum()) for g in
                                ("domicilio_particular", "domicilio_coletivo", "estab_agropecuario", "outros")},
        "enderecos_por_especie": {e: int(s[e].sum()) for e in ESPECIES.values()},
        "nivel_de_geocodificacao": {str(k): int(v) for k, v in
                                    pontos["NV_GEO_COORD"].value_counts().sort_index().items()},
        "unidades_com_domicilio_particular": int((dp > 0).sum()),
        "unidades_com_domicilio_particular_ou_coletivo": int((dom > 0).sum()),
        "unidades_so_com_agropecuario_ou_outros": int(((dom == 0) & (s["enderecos"] > 0)).sum()),
        "unidades_sem_nenhum_endereco": int((s["enderecos"] == 0).sum()),
        # o CNEFE lido é só o de Bagé: numa unidade que cruza o limite, o endereço
        # do município vizinho não aparece (conferência incompleta)
        "tocam_o_limite_municipal": int(s["toca_limite"].sum()),
        "sem_nenhum_endereco_e_tocam_o_limite": int(((s["enderecos"] == 0) & s["toca_limite"]).sum()),
    }
    for res in ("200 m", "1 km"):
        r = s[s["res_grupo"] == res]
        rd = r["domicilio_particular"] + r["domicilio_coletivo"]
        out[res] = {"unidades": int(len(r)), "com_domicilio_particular_ou_coletivo": int((rd > 0).sum()),
                    "sem_nenhum_endereco": int((r["enderecos"] == 0).sum()),
                    "dentro_da_area_urbanizada_com_domicilio": int(((rd > 0) & r["dentro_au"]).sum())}
    return out


def ocupacao_cnefe(u: gpd.GeoDataFrame) -> dict:
    """Domicílios ocupados da grade 2022 / domicílios (part. + col.) do CNEFE, por resolução."""
    out = {}
    for res in ("200 m", "1 km"):
        r = u[u["res_grupo"] == res]
        cn = int((r["domicilio_particular"] + r["domicilio_coletivo"]).sum())
        out[res] = {"dom_ocupados_grade_2022": int(r["dom_22"].sum()), "domicilios_cnefe": cn,
                    "razao_pct": round(100 * r["dom_22"].sum() / cn, 1) if cn else None}
    return out


# --------------------------------------------------------------------------
# 4. verificações que complementam a documentação
# --------------------------------------------------------------------------

def celulas_pequenas(area: gpd.GeoDataFrame) -> dict:
    """Há supressão de célula pequena? Conta células com 1–4 domicílios e nulos, por edição."""
    out = {}
    for ano in ("2010", "2022"):
        g = ler_grade(ano, area.geometry)
        g = g[g["centroide_no_municipio"]]
        res = g["ID_UNICO"].str[:4].map({"200M": "200 m", "1KME": "1 km"})
        out[ano] = {"nulos_populacao": int(g["pop"].isna().sum()), "nulos_domicilios": int(g["dom"].isna().sum()),
                    "populacao_sem_domicilio": int(((g["pop"] > 0) & (g["dom"] == 0)).sum()),
                    "domicilio_sem_populacao": int(((g["dom"] > 0) & (g["pop"] == 0)).sum())}
        for r in ("200 m", "1 km"):
            d = g.loc[res == r, "dom"]
            out[ano][r] = {"celulas": int(len(d)), "com_domicilio": int((d > 0).sum()),
                           **{f"com_{k}": int((d == k).sum()) for k in (1, 2, 3, 4)}}
    return out


def malha_2010(crs: str) -> gpd.GeoDataFrame:
    return gpd.read_file(f"zip://{conferido(MALHA_2010)}",
                         where=f"CD_GEOCODM = '{paths.codigo_ibge()}'")[
        ["CD_GEOCODI", "TIPO", "geometry"]].to_crs(crs)


def situacao_2010(u: gpd.GeoDataFrame, m: gpd.GeoDataFrame) -> pd.Series:
    """Situação (URBANO/RURAL) do setor de 2010 onde cai o centroide da unidade.

    Em 2010 o CNEFE só tinha coordenada na área rural (metodologia do Censo
    2010, § 1.4.3.6): o domicílio de setor urbano entrou na grade de 2010 por
    alguma alocação, não pela coordenada do endereço.
    """
    c = gpd.GeoDataFrame(geometry=u.geometry.centroid, crs=u.crs)
    j = gpd.sjoin(c, m, predicate="within", how="left")
    j = j[~j.index.duplicated()]
    return j["TIPO"].reindex(u.index)


def por_situacao_2010(u: gpd.GeoDataFrame) -> dict:
    out = {}
    for classe in ("extinta", "nova"):
        s = u[u["classe"] == classe]
        out[classe] = {}
        for (res, tipo), g in s.groupby(["res_grupo", s["setor_2010"].fillna("fora da malha")]):
            out[classe][f"{res} / setor {tipo}"] = {
                "unidades": int(len(g)), "sem_nenhum_endereco_cnefe": int((g["enderecos"] == 0).sum()),
                "dom_10": int(g["dom_10"].sum()), "dom_22": int(g["dom_22"].sum())}
    return out


def setores_2010_nas_classes(u: gpd.GeoDataFrame, m: gpd.GeoDataFrame) -> dict:
    """Centroide e ponto representativo dos setores de 2010 de Bagé: em que classe caem?

    Se a grade de 2010 pusesse no centro do setor o domicílio rural sem
    coordenada, as extintas concentrariam esses pontos.
    """
    out = {"setores": m["TIPO"].value_counts().to_dict()}
    for nome, pts in (("centroide", m.geometry.centroid), ("ponto_representativo", m.geometry.representative_point())):
        p = gpd.GeoDataFrame(m[["TIPO"]], geometry=pts, crs=m.crs)
        j = gpd.sjoin(p, u[["classe", "geometry"]], predicate="within")
        out[nome] = {t: j.loc[j["TIPO"] == t, "classe"].value_counts().to_dict() for t in sorted(j["TIPO"].unique())}
    return out


def agrupamentos_de_extintas(u: gpd.GeoDataFrame, m2010_cod: gpd.GeoDataFrame) -> list[dict]:
    """Os 10 maiores agrupamentos contíguos de extintas (por domicílios de 2010), com
    os setores de 2010 onde caem os centroides e quantas unidades não têm endereço."""
    e = u[u["classe"] == "extinta"].copy()
    e["grupo"] = agrupamentos(e.geometry)
    c = gpd.GeoDataFrame(geometry=e.geometry.centroid, crs=e.crs)
    j = gpd.sjoin(c, m2010_cod, predicate="within", how="left")
    e["setor_2010_cod"] = j[~j.index.duplicated()]["CD_GEOCODI"].reindex(e.index)
    g = (e.groupby("grupo")
         .agg(unidades=("unidade", "size"), dom_10=("dom_10", "sum"), pop_10=("pop_10", "sum"),
              sem_nenhum_endereco=("enderecos", lambda s: int((s == 0).sum())),
              domicilios_cnefe=("domicilio_particular", "sum"),
              resolucoes=("res_grupo", lambda s: sorted(set(s))),
              setores_2010=("setor_2010_cod", lambda s: sorted(set(s.dropna())))))
    g = g.sort_values(["dom_10", "unidades"], ascending=False).head(10)
    return [{k: (int(v) if isinstance(v, (int, np.integer)) else v) for k, v in r.items()}
            for r in g.to_dict("records")]


def extintas_por_setor_2010(u: gpd.GeoDataFrame, m2010_cod: gpd.GeoDataFrame) -> list[dict]:
    """Setores de 2010 com mais domicílios em unidades extintas (centroide da unidade),
    com o total de DPP do setor no agregado de 2010 (V001, Basico, extraído pelo r00)."""
    c = gpd.GeoDataFrame(u[["classe", "dom_10", "dom_22", "enderecos"]],
                         geometry=u.geometry.centroid, crs=u.crs)
    j = gpd.sjoin(c, m2010_cod, predicate="within")
    j = j[~j.index.duplicated()]
    basico = pd.read_csv(DERIV / "bage" / "c2010" / "Basico_RS.csv", sep=";", dtype=str,
                         usecols=["Cod_setor", "Situacao_setor", "V001"]).set_index("Cod_setor")
    linhas = []
    for cod, s in j.groupby("CD_GEOCODI"):
        e = s[s["classe"] == "extinta"]
        if not len(e):
            continue
        linhas.append({"setor_2010": cod, "tipo": s["TIPO"].iloc[0],
                       "situacao_setor_2010": basico["Situacao_setor"].get(cod),
                       "dpp_do_setor_2010_V001": (int(basico["V001"][cod]) if cod in basico.index else None),
                       "dom_10_na_grade_centroide_no_setor": int(s["dom_10"].sum()),
                       "dom_22_na_grade_centroide_no_setor": int(s["dom_22"].sum()),
                       "extintas": int(len(e)), "dom_10_nas_extintas": int(e["dom_10"].sum()),
                       "extintas_sem_nenhum_endereco": int((e["enderecos"] == 0).sum())})
    return sorted(linhas, key=lambda r: -r["dom_10_nas_extintas"])[:10]


# --------------------------------------------------------------------------

def main() -> None:
    area = paths.carregar_area_estudo()
    camada = ler_camada()
    u = universo(camada, area)
    viz = Vizinhanca(u)

    ext = u[u["classe"] == "extinta"]
    nov = u[u["classe"] == "nova"]

    # 2. deslocamento
    sel = ext.index.values
    medidas_viz = {rotulo(m): medir_vizinhanca(u, viz, sel, m) for m in ("rainha", *RAIOS_M)}
    deslocamento = {}
    for nome, m in medidas_viz.items():
        deslocamento[nome] = {"todas": resumo_deslocamento(m, u["dom_10"])}
        for res in ("200 m", "1 km"):
            idx = m.index[u.loc[m.index, "res_grupo"] == res]
            deslocamento[nome][res] = resumo_deslocamento(m.loc[idx], u["dom_10"])

    # 3. CNEFE
    pts = ler_cnefe(u.crs)
    tab, j = cnefe_por_unidade(u, pts)
    u = u.join(tab, on="unidade")
    cols_cnefe = list(tab.columns)
    u[cols_cnefe] = u[cols_cnefe].fillna(0).astype(int)
    m2010 = malha_2010(u.crs)
    u["setor_2010"] = situacao_2010(u, m2010)
    ext, nov = u[u["classe"] == "extinta"], u[u["classe"] == "nova"]
    dom_cn_ext = ext["domicilio_particular"] + ext["domicilio_coletivo"]
    dom_cn_nov = nov["domicilio_particular"] + nov["domicilio_coletivo"]

    resultado = {
        "objeto": "unidades extintas da camada de trabalho (dom_10 > 0 e dom_22 = 0)",
        "camada": {"arquivo": paths.relativo(CAMADA),
                   "sha256_conteudo_conferido": metadados.ler(CAMADA)["sha256_conteudo"]},
        "universo_de_vizinhanca": {"unidades": int(len(u)), "por_classe": u["classe"].value_counts().to_dict(),
                                   "regra": "unidades harmonizadas com centroide no município; "
                                            "sem domicílio nos dois anos = variação 0"},
        "1_perfil_extintas_dom_2010": perfil_por_grupo(ext, "dom_10"),
        "1_perfil_extintas_pop_2010": {"populacao": int(ext["pop_10"].sum()),
                                       "moradores_por_domicilio": round(ext["pop_10"].sum() / ext["dom_10"].sum(), 2)},
        "2_deslocamento": {
            "regra": "saldo = soma de d_dom das vizinhas; ganho bruto = soma das variações positivas; "
                     "perda = dom_10 da extinta. Rainha: toca (1 m). Raio R: centroide da vizinha a até "
                     "R da borda da extinta.",
            **deslocamento,
            "linha_de_base_1km": linha_de_base(u, viz),
            "pares_por_permutacao_1km": pares_por_permutacao(u),
        },
        "3_cnefe_nas_extintas": {
            **resumo_cnefe(ext, j),
            "extintas_com_domicilio_cnefe_>=_dom_2010": int((dom_cn_ext >= ext["dom_10"]).sum()),
            "extintas_com_domicilio_cnefe_por_dom_2010": {
                str(k): {"unidades": int(len(g)), "com_domicilio_cnefe": int((g > 0).sum())}
                for k, g in dom_cn_ext.groupby(ext["dom_10"].clip(upper=6).astype(str).replace("6", ">=6"))},
            "leitura": "o CNEFE lista o domicílio particular ocupado ou não (vago, uso ocasional); "
                       "a grade de 2022 conta só os ocupados",
        },
        "3_ocupacao_grade_sobre_cnefe": ocupacao_cnefe(u),
        "4_verificacoes": {
            "celulas_pequenas_nas_duas_edicoes": celulas_pequenas(area),
            "cnefe_nivel_de_geocodificacao_municipio": {str(k): int(v) for k, v in
                                                       pts["NV_GEO_COORD"].value_counts().sort_index().items()},
            "setores_2010_centroides_por_classe": setores_2010_nas_classes(u, m2010),
            "situacao_do_setor_2010_pelo_centroide_da_unidade": por_situacao_2010(u),
            "maiores_agrupamentos_de_extintas": agrupamentos_de_extintas(u, m2010),
            "setores_2010_com_mais_domicilios_extintos": extintas_por_setor_2010(u, m2010),
        },
        "5_novas": {
            "perfil_dom_2022": perfil_por_grupo(nov, "dom_22"),
            "cnefe": {**resumo_cnefe(nov, j),
                      "novas_com_dom_2022_maior_que_domicilios_cnefe": int((nov["dom_22"] > dom_cn_nov).sum()),
                      "novas_com_dom_2022_igual_a_domicilios_cnefe": int((nov["dom_22"] == dom_cn_nov).sum())},
        },
        "crs_medicao_distancia": paths.crs_producao(),
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    DERIV.mkdir(exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=int), encoding="utf-8")

    # extintas e novas, por unidade, para a conferência no mapa (fora do git)
    por_unidade = u[u["classe"].isin(["extinta", "nova"])].copy()
    for nome, m in medidas_viz.items():
        por_unidade = por_unidade.join(m[["saldo", "ganho_bruto", "novas_vizinhas"]]
                                       .add_prefix(f"viz_{nome}_"))
    colunas = (["unidade", "classe", "resolucao", "dentro_au", "toca_limite", "setor_2010", "dom_10", "dom_22", "pop_10", "pop_22", "d_dom"]
               + cols_cnefe + [c for c in por_unidade.columns if c.startswith("viz_")] + ["geometry"])
    por_unidade = por_unidade[colunas].sort_values(["classe", "unidade"]).reset_index(drop=True)
    if SAIDA_GPKG.exists():
        SAIDA_GPKG.unlink()
    por_unidade.to_file(SAIDA_GPKG, driver="GPKG", layer="s1_extintas_unidades")
    dados = metadados.montar(
        SAIDA_GPKG, tema="censo",
        fonte_id="ibge_grade_estatistica_2010;ibge_grade_estatistica_2022;ibge_cnefe2022",
        versao="s1-extintas-v1", crs=paths.crs_producao(),
        licenca="IBGE — uso livre com citação da fonte", autorizacao_fonte=True,
        pode_publicar=False, status_conferencia="pendente",
        observacoes=(
            "Apoio à conferência visual das unidades extintas e novas do A03 (subordinada 1): "
            "por unidade, contagem de endereços do CNEFE 2022 por espécie e saldo/ganho de "
            "domicílios das vizinhas (rainha, raio 1 e 2 km). Não reclassifica nada. Contagem "
            "de endereço por célula: não publicar. Script: "
            "estudos/A03_expansao_adensamento/scripts/s1_extintas.py."),
    )
    dados["sha256_conteudo"] = sha256_conteudo(SAIDA_GPKG)
    metadados.escrever(SAIDA_GPKG, dados, sobrescrever=True)
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=int)[:6000])


if __name__ == "__main__":
    main()
