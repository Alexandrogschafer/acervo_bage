"""
A03 — subordinada 1: deslocamento por FACE DE LOGRADOURO na grade de 2010.

Hipótese (conferência visual do responsável, 2026-09-23; resultados_s1.md § 12):
no urbano, a grade de 2010 agrega por face de quadra e, quando a face cruza
células, reparte os domicílios pela extensão dela supondo distribuição uniforme
(Grade Estatística, 2016, p. 18–19). Isso desloca domicílios entre células mesmo
sem desagregação. A grade de 2022 posiciona pelo endereço do CNEFE. Uma célula
atravessada só pela "cauda" de uma face pode então ter domicílio em 2010 e
nenhum em 2022 (extinta), e a vizinha o inverso (nova).

Este script MEDE; não reclassifica nada e não altera a camada de trabalho
(confere o sha256_conteudo dela antes de ler, pelo s1_extintas.ler_camada).

MÉTODO
------
1. Faces de 2010 (base de faces de logradouros do Censo 2010, os 5 distritos de
   Bagé; só o distrito-sede tem atributos). TOT_RES = total de espécies
   residenciais da face (endereços do CNEFE 2010, ocupados ou não).
2. Recorte face × unidade harmonizada (= célula de 2010): comprimento de cada
   trecho e fração da face em cada unidade. Célula MAIOR da face = a que tem a
   maior fração. Trecho "de fora" = trecho de face cuja maior parte está em
   outra célula.
3. MODELO UNIFORME (o do IBGE): alloc_u = Σ TOT_RES × fração do comprimento.
   Validação: correlação com DOM_OCU de 2010 nas células de 200 m.
4. MODELO POR PONTOS: cada domicílio do CNEFE 2022 (espécie 1 ou 2) é ligado à
   face residencial de 2010 mais próxima, até RAIO_FACE_M; alloc_p = Σ TOT_RES
   × fração dos pontos de 2022 da face que cai em cada célula. Face sem ponto
   de 2022 fica com a repartição uniforme. É o 2010 "reposicionado pelos
   endereços de 2022", supondo que os endereços da face ficaram no lugar — o
   que não se verifica: demolição de um lado da face e repartição uniforme dão
   o mesmo alloc_p. Declarado como limite do teste. Pelo mesmo motivo, face
   que GANHOU endereços entre 2010 e 2022 puxa o 2010 para onde houve
   crescimento. Variante conservadora (alloc_pe): só reposiciona face com
   domicílios do CNEFE 2022 ≤ TOT_RES de 2010; as outras ficam uniformes.
5. Escala: k = DOM_OCU / alloc_u nas células de 200 m de setor urbano de 2010
   (ocupados / endereços residenciais).
6. Grupos testados, no cenário adotado (setor 430160205000136 à parte):
   extintas URBANAS = extintas de 200 m com centroide em setor urbano de 2010
   (o critério é o do método de 2010, que é por setor); novas urbanas, idem.
7. Sensibilidade (só medida): dom_10 reposicionado = dom_10 + k × (alloc_p −
   alloc_u), arredondado, e as classes e a faixa da expansão recalculadas com
   as funções do s1. Classes são sobre domicílios; a população não é
   reposicionada, e a divergência de sinal não é recalculada.

LÊ a camada de trabalho, data/raw/ (grade 2010, faces 2010, CNEFE 2022, malha
de setores 2010), derivados/s1_desagregacao_2010.json (via camada) e config/.
ESCREVE só derivados/s1_faces_2010.json.
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

import s1_expansao_adensamento as s1  # noqa: E402
import s1_extintas as ex  # noqa: E402
from scripts.utils import metadados, paths  # noqa: E402

SAIDA = s1.DERIV / "s1_faces_2010.json"
DIR_FACES = paths.caminho("raw_vetor", "ibge", "censo_2010", "faces_logradouros")

# distância máxima do domicílio do CNEFE 2022 à face residencial de 2010 a que é
# ligado. 40 m ≈ p90 medido nas células de 200 m de setor urbano (gravado no JSON).
RAIO_FACE_M = 40
LIMIAR_ARREDONDAMENTO = 0.5
FAIXAS_DIST_M = [0, 25, 50, 100, 200, float("inf")]
ROTULOS_DIST = ["até 25 m", "25–50 m", "50–100 m", "100–200 m", "> 200 m"]


# --------------------------------------------------------------------------
# entradas
# --------------------------------------------------------------------------

def ler_faces(crs) -> tuple[gpd.GeoDataFrame, dict]:
    zips = sorted(DIR_FACES.glob(f"{paths.codigo_ibge()}*.zip"))
    if not zips:
        raise SystemExit(f"PARADO — sem faces de 2010 em {paths.relativo(DIR_FACES)}: "
                         "rodar scripts/download/baixar_censo_ibge.py")
    partes, por_arquivo = [], {}
    for z in zips:
        g = gpd.read_file(f"zip://{ex.conferido(z)}!{z.stem}_face.shp").to_crs(crs)
        g["arquivo"] = z.name
        por_arquivo[z.name] = {"faces": int(len(g)),
                               "com_TOT_RES": int(g["TOT_RES"].notna().sum()),
                               "TOT_RES": int(g["TOT_RES"].fillna(0).sum())}
        partes.append(g)
    f = gpd.GeoDataFrame(pd.concat(partes, ignore_index=True), geometry="geometry", crs=crs)
    f["TOT_RES"] = f["TOT_RES"].fillna(0)
    f["L"] = f.length
    return f, por_arquivo


def recorte(f: gpd.GeoDataFrame, u: gpd.GeoDataFrame) -> pd.DataFrame:
    """Trechos face × unidade (só faces com TOT_RES > 0)."""
    fr = f[f["TOT_RES"] > 0][["TOT_RES", "L", "geometry"]].reset_index(names="fi")
    ov = gpd.overlay(fr, u[["unidade", "geometry"]], how="intersection", keep_geom_type=False)
    ov["l"] = ov.length
    ov = ov[ov["l"] > 0].copy()
    ov["frac"] = ov["l"] / ov["L"]
    soma = ov.groupby("fi")["frac"].sum()
    if (soma < 0.999).any():
        raise SystemExit(f"PARADO — {int((soma < 0.999).sum())} faces fora do universo de unidades")
    maior = ov.sort_values("frac", ascending=False).drop_duplicates("fi").set_index("fi")
    ov["cel_maior"] = ov["fi"].map(maior["unidade"])
    ov["de_fora"] = ov["unidade"] != ov["cel_maior"]
    return pd.DataFrame(ov.drop(columns="geometry"))


def ligar_pontos(pts: gpd.GeoDataFrame, f: gpd.GeoDataFrame, u: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Domicílio do CNEFE 2022 → face residencial de 2010 mais próxima (até RAIO_FACE_M) e célula."""
    fr = f[f["TOT_RES"] > 0]
    arvore = shapely.STRtree(fr.geometry.values)
    (ip, iface), dist = arvore.query_nearest(pts.geometry.values, return_distance=True,
                                             all_matches=False)
    pts = pts.copy()
    pts["d_face"] = np.nan
    pts.loc[pts.index[ip], "d_face"] = dist
    ip2, iface2 = arvore.query_nearest(pts.geometry.values, max_distance=RAIO_FACE_M,
                                       all_matches=False)
    pts["fi"] = pd.NA
    pts.loc[pts.index[ip2], "fi"] = fr.index.values[iface2]
    j = gpd.sjoin(pts[["geometry"]], u[["unidade", "geometry"]], predicate="within", how="left")
    pts["cel"] = j[~j.index.duplicated()]["unidade"]
    return pts


# --------------------------------------------------------------------------
# modelos
# --------------------------------------------------------------------------

def modelos(ov: pd.DataFrame, pts: gpd.GeoDataFrame, f: gpd.GeoDataFrame) -> pd.DataFrame:
    """Por trecho (face, unidade): alloc_u (uniforme) e alloc_p (pelos pontos de 2022)."""
    pf = pts.dropna(subset=["fi", "cel"]).astype({"fi": int})
    npf = pf.groupby("fi").size()
    share = (pf.groupby(["fi", "cel"]).size().div(npf, level=0).rename("share_p")
             .reset_index().rename(columns={"cel": "unidade"}))
    o = ov.merge(share, on=["fi", "unidade"], how="outer")
    o["TOT_RES"] = o["fi"].map(f["TOT_RES"])
    o["frac"] = o["frac"].fillna(0)
    o["share_p"] = o["share_p"].fillna(0)
    o["de_fora"] = o["de_fora"].fillna(False).astype(bool)
    o["tem_pontos"] = o["fi"].isin(npf.index)
    o["alloc_u"] = o["TOT_RES"] * o["frac"]
    o["alloc_p"] = np.where(o["tem_pontos"], o["TOT_RES"] * o["share_p"], o["alloc_u"])
    o["alloc_u_de_fora"] = np.where(o["de_fora"], o["alloc_u"], 0.0)
    o["face_sem_crescimento"] = o["fi"].map(npf).fillna(0) <= o["TOT_RES"]
    o["alloc_pe"] = np.where(o["tem_pontos"] & o["face_sem_crescimento"],
                             o["TOT_RES"] * o["share_p"], o["alloc_u"])
    o["alloc_p_face_sem_ponto"] = np.where(~o["tem_pontos"], o["alloc_p"], 0.0)
    return o


def por_unidade(u: gpd.GeoDataFrame, o: pd.DataFrame) -> gpd.GeoDataFrame:
    cruza = o[o["frac"] > 0]
    a = o.groupby("unidade")[["alloc_u", "alloc_p", "alloc_pe", "alloc_u_de_fora",
                              "alloc_p_face_sem_ponto"]].sum()
    a["faces"] = cruza.groupby("unidade")["fi"].nunique()
    a["faces_de_fora"] = cruza[cruza["de_fora"]].groupby("unidade")["fi"].nunique()
    u = u.join(a, on="unidade")
    cols = list(a.columns)
    u[cols] = u[cols].fillna(0)
    return u


def validacao(u: gpd.GeoDataFrame) -> dict:
    out = {}
    for (res, sit), g in u[u["res_grupo"] == "200 m"].groupby(["res_grupo", u["setor_2010"].fillna("fora da malha")]):
        out[f"{res} / setor {sit} de 2010"] = {
            "celulas": int(len(g)), "dom_10_grade": int(g["dom_10"].sum()),
            "tot_res_repartido_uniforme": round(float(g["alloc_u"].sum()), 1),
            "correlacao_dom_10_x_uniforme": round(float(np.corrcoef(g["dom_10"], g["alloc_u"])[0, 1]), 3),
            "com_dom_10_e_uniforme_menor_que_0,5": int(((g["dom_10"] > 0) & (g["alloc_u"] < 0.5)).sum()),
            "sem_dom_10_e_uniforme_>=_1": int(((g["dom_10"] == 0) & (g["alloc_u"] >= 1)).sum())}
    return out


# --------------------------------------------------------------------------
# testes por grupo
# --------------------------------------------------------------------------

def vizinhas_rainha(u: gpd.GeoDataFrame) -> dict[int, np.ndarray]:
    arvore = shapely.STRtree(u.geometry.values)
    a, b = arvore.query(u.geometry.buffer(s1.TOLERANCIA_CONTIGUIDADE_M).values, predicate="intersects")
    m = a != b
    return pd.Series(b[m]).groupby(a[m]).apply(np.array).to_dict()


def faixas(d: np.ndarray) -> dict:
    c = pd.cut(pd.Series(d, dtype=float), FAIXAS_DIST_M, right=True, labels=ROTULOS_DIST, include_lowest=True)
    return {str(k): int(v) for k, v in c.value_counts(sort=False).items()}


def quantis(d: np.ndarray) -> list | None:
    return [round(float(x), 0) for x in np.quantile(d, [.1, .25, .5, .75, .9])] if len(d) else None


def cnefe_em_volta(g: gpd.GeoDataFrame, u: gpd.GeoDataFrame, viz: dict, pts: gpd.GeoDataFrame,
                   o: pd.DataFrame) -> dict:
    """Domicílios do CNEFE 2022 nas vizinhas rainha e nas faces de 2010 que atravessam a unidade."""
    pc = pts.dropna(subset=["cel"])
    por_cel = {c: grp for c, grp in pc.groupby("cel")}
    unidades = u["unidade"].values
    n_viz, d_viz, n_na_face_dentro, d_face_fora, n_face_fora = [], [], 0, [], 0
    for i, row in g.iterrows():
        vizinhas = unidades[viz.get(i, np.array([], dtype=int))]
        partes = [por_cel[c] for c in vizinhas if c in por_cel]
        p = pd.concat(partes) if partes else pc.iloc[:0]
        n_viz.append(len(p))
        d_viz.extend(p.geometry.distance(row.geometry).tolist())
        faces = o.loc[(o["unidade"] == row["unidade"]) & (o["frac"] > 0), "fi"].unique()
        pf = pts[pts["fi"].isin(faces)]
        dentro = pf["cel"] == row["unidade"]
        n_na_face_dentro += int(dentro.sum())
        n_face_fora += int((~dentro).sum())
        d_face_fora.extend(pf[~dentro].geometry.distance(row.geometry).tolist())
    d_viz, d_face_fora = np.array(d_viz), np.array(d_face_fora)
    return {
        "vizinhas_rainha": {
            "domicilios_cnefe_2022": int(sum(n_viz)),
            "mediana_por_unidade": float(np.median(n_viz)) if n_viz else None,
            "unidades_sem_nenhum_nas_vizinhas": int(sum(n == 0 for n in n_viz)),
            "distancia_a_unidade_m_p10_p25_p50_p75_p90": quantis(d_viz),
            "por_faixa_de_distancia": faixas(d_viz)},
        "nas_faces_de_2010_que_atravessam_a_unidade": {
            "domicilios_cnefe_2022": n_na_face_dentro + n_face_fora,
            "dentro_da_propria_unidade": n_na_face_dentro,
            "fora_dela": n_face_fora,
            "distancia_dos_de_fora_a_unidade_m_p10_p25_p50_p75_p90": quantis(d_face_fora),
            "por_faixa_de_distancia": faixas(d_face_fora)},
    }


def faces_vs_2022(units: pd.Series, o: pd.DataFrame, pts: gpd.GeoDataFrame, f: gpd.GeoDataFrame) -> dict:
    """As faces que atravessam as unidades: endereços residenciais de 2010 × domicílios do CNEFE 2022."""
    fi = o.loc[o["unidade"].isin(units) & (o["frac"] > 0), "fi"].unique()
    n22 = pts.dropna(subset=["fi"]).astype({"fi": int}).groupby("fi").size()
    d = pd.DataFrame({"fi": fi})
    d["tot_res_2010"] = d["fi"].map(f["TOT_RES"])
    d["cnefe_2022"] = d["fi"].map(n22).fillna(0)
    return {"faces": int(len(d)), "tot_res_2010": int(d["tot_res_2010"].sum()),
            "domicilios_cnefe_2022_ligados": int(d["cnefe_2022"].sum()),
            "faces_com_cnefe_2022_>=_tot_res_2010": int((d["cnefe_2022"] >= d["tot_res_2010"]).sum()),
            "faces_sem_nenhum_domicilio_cnefe_2022": int((d["cnefe_2022"] == 0).sum()),
            "tot_res_2010_nas_faces_sem_domicilio_2022": int(d.loc[d["cnefe_2022"] == 0, "tot_res_2010"].sum())}


def aditivo(g: pd.DataFrame, k: float, col: str) -> pd.Series:
    """dom_10 reposicionado: o da grade corrigido pela diferença entre os modelos."""
    return np.floor(g["dom_10"] + k * (g[col] - g["alloc_u"]) + 0.5).clip(lower=0).astype(int)


def mecanismo_extinta(g: pd.DataFrame, k: float) -> pd.Series:
    return pd.Series(np.select(
        [g["faces"] == 0,
         g["alloc_p"] * k < LIMIAR_ARREDONDAMENTO,
         g["alloc_p_face_sem_ponto"] >= 0.5 * g["alloc_p"]],
        ["sem face residencial de 2010",
         "some com o reposicionamento (os endereços da face estão em outra célula em 2022)",
         "face sem nenhum domicílio no CNEFE 2022 (a face perdeu os endereços)"],
        "permanece: pontos de 2022 da face na própria unidade"), index=g.index)


def mecanismo_nova(g: pd.DataFrame, k: float) -> pd.Series:
    return pd.Series(np.select(
        [g["alloc_p"] * k >= LIMIAR_ARREDONDAMENTO,
         g["alloc_u"] > 0],
        ["teria domicílio em 2010 com o reposicionamento (endereços de 2022 em face de 2010)",
         "cauda de face de 2010, sem endereço de 2022 ligado: continua nova"],
        "sem face residencial de 2010 ligada: rua ou ocupação nova"), index=g.index)


FENOMENO = {
    "some com o reposicionamento (os endereços da face estão em outra célula em 2022)":
        "deslocamento_por_reparticao",
    "face sem nenhum domicílio no CNEFE 2022 (a face perdeu os endereços)":
        "esvaziamento_medido_face_perdeu_os_enderecos",
}


def fenomenos_das_extintas(ext: gpd.GeoDataFrame, k: float, agrup: pd.Series) -> dict:
    """As extintas urbanas separadas pelos dois fenômenos (decisão de 2026-09-23), com a
    geografia do resultados_s1 § 5.1 (distância à área urbanizada de 2022) e a lista."""
    from s1_geografias import FAIXAS_BORDA_M, area_urbanizada
    e = ext.copy()
    e["fenomeno"] = mecanismo_extinta(e, k).map(FENOMENO).fillna("outros")
    e["dist_au_m"] = e.geometry.distance(area_urbanizada(e.crs))
    e["faixa"] = pd.cut(e["dist_au_m"], FAIXAS_BORDA_M, right=False,
                        labels=["dentro ou tocando", "até 500 m", "500 m a 1 km", "1 a 2 km", "> 2 km"])
    out = {}
    for nome, g in e.groupby("fenomeno"):
        out[nome] = {
            "unidades": int(len(g)), "dom_10": int(g["dom_10"].sum()), "pop_10": int(g["pop_10"].sum()),
            "no_agrupamento_053_054": {"unidades": int(g["unidade"].isin(agrup).sum()),
                                       "dom_10": int(g.loc[g["unidade"].isin(agrup), "dom_10"].sum())},
            "por_distancia_a_area_urbanizada_2022": {
                str(f): {"unidades": int(len(x)), "dom_10": int(x["dom_10"].sum())}
                for f, x in g.groupby("faixa", observed=False)},
            "fora_da_area_urbanizada_a_menos_de_1_km": {
                "unidades": int(((g["dist_au_m"] > 0) & (g["dist_au_m"] < 1000)).sum()),
                "dom_10": int(g.loc[(g["dist_au_m"] > 0) & (g["dist_au_m"] < 1000), "dom_10"].sum())},
            "unidades_lista": sorted(g["unidade"].tolist()),
        }
    return out


def resumo_grupo(g: gpd.GeoDataFrame, u, viz, pts, o, f, k, mec) -> dict:
    maior = o[o["frac"] > 0].drop_duplicates("fi").set_index("fi")["cel_maior"]
    idx_de = {c: i for i, c in enumerate(u["unidade"])}
    vizinha_da_maior, com_face_de_fora = 0, 0
    for i, row in g.iterrows():
        fis = o.loc[(o["unidade"] == row["unidade"]) & (o["frac"] > 0) & o["de_fora"], "fi"].unique()
        if len(fis):
            com_face_de_fora += 1
            vz = set(viz.get(i, []))
            vizinha_da_maior += all(idx_de[maior[x]] in vz for x in fis)
    m = mec(g, k)
    col_dom = "dom_10" if (g["dom_10"] > 0).all() else "dom_22"
    return {
        "unidades": int(len(g)), "dom_10": int(g["dom_10"].sum()), "dom_22": int(g["dom_22"].sum()),
        "atravessadas_por_face_residencial_de_2010": int((g["faces"] > 0).sum()),
        "atravessadas_por_face_cuja_maior_parte_cai_em_outra_celula": com_face_de_fora,
        "das_quais_a_celula_maior_e_vizinha_rainha_em_todas_as_faces": vizinha_da_maior,
        "todo_o_uniforme_vem_de_face_de_fora": int(((g["alloc_u"] > 0) & (g["alloc_u_de_fora"] >= g["alloc_u"] - 1e-9)).sum()),
        "tot_res_uniforme": round(float(g["alloc_u"].sum()), 1),
        "tot_res_uniforme_de_face_de_fora": round(float(g["alloc_u_de_fora"].sum()), 1),
        "pct_do_uniforme_de_face_de_fora": round(100 * g["alloc_u_de_fora"].sum() / g["alloc_u"].sum(), 1) if g["alloc_u"].sum() else None,
        "tot_res_pelos_pontos_2022": round(float(g["alloc_p"].sum()), 1),
        "dom_10_reposicionado_estimado_(k)": round(float(k * g["alloc_p"].sum()), 1),
        "unidades_com_dom_10_zero_se_reposicionado": {
            "substituicao_k_x_alloc_p_<_0,5": int((k * g["alloc_p"] < LIMIAR_ARREDONDAMENTO).sum()),
            "substituicao_variante_faces_sem_crescimento": int((k * g["alloc_pe"] < LIMIAR_ARREDONDAMENTO).sum()),
            "aditivo_dom_10_+_k_x_(alloc_p_-_alloc_u)": int((aditivo(g, k, "alloc_p") == 0).sum()),
            "aditivo_variante_faces_sem_crescimento": int((aditivo(g, k, "alloc_pe") == 0).sum())},
        "por_mecanismo": {str(nome): {"unidades": int(len(s)), col_dom: int(s[col_dom].sum())}
                          for nome, s in g.groupby(m)},
        "faces_2010_x_cnefe_2022": faces_vs_2022(g["unidade"], o, pts, f),
        "cnefe_2022_em_volta": cnefe_em_volta(g, u, viz, pts, o),
    }


def comparacao_classes(u: gpd.GeoDataFrame, grupo_urb: pd.Series) -> dict:
    """Mesma medida em adensadas/esvaziadas/estáveis urbanas: linha de base da 'face de fora'."""
    out = {}
    for cl in ("adensada", "esvaziada", "estavel"):
        g = u[grupo_urb & (u["classe"] == cl)]
        out[cl] = {"unidades": int(len(g)),
                   "com_face_de_fora": int((g["faces_de_fora"] > 0).sum()),
                   "todo_o_uniforme_vem_de_face_de_fora": int(((g["alloc_u"] > 0) & (g["alloc_u_de_fora"] >= g["alloc_u"] - 1e-9)).sum()),
                   "pct_do_uniforme_de_face_de_fora": round(100 * g["alloc_u_de_fora"].sum() / g["alloc_u"].sum(), 1)}
    return out


# --------------------------------------------------------------------------
# escala e sensibilidade
# --------------------------------------------------------------------------

def escala_cidade(u: gpd.GeoDataFrame, o: pd.DataFrame, f: gpd.GeoDataFrame, k: float) -> dict:
    urb = (u["res_grupo"] == "200 m") & (u["setor_2010"] == "URBANO")
    fr = f[f["TOT_RES"] > 0]
    ncel = o[o["frac"] > 0].groupby("fi")["unidade"].nunique()
    cruzam = ncel[ncel > 1].index
    g = u[urb]
    dif = (g["alloc_p"] - g["alloc_u"]) * k
    return {
        "faces_residenciais": int(len(fr)), "tot_res": int(fr["TOT_RES"].sum()),
        "faces_que_cruzam_celulas": int(len(cruzam)),
        "tot_res_em_faces_que_cruzam": int(f.loc[cruzam, "TOT_RES"].sum()),
        "pct_tot_res_em_faces_que_cruzam": round(100 * f.loc[cruzam, "TOT_RES"].sum() / fr["TOT_RES"].sum(), 1),
        "celulas_200m_setor_urbano": {
            "celulas": int(len(g)), "dom_10": int(g["dom_10"].sum()),
            "uniforme_em_trecho_de_face_de_fora_tot_res": round(float(g["alloc_u_de_fora"].sum()), 1),
            "pct_do_uniforme_em_trecho_de_face_de_fora": round(100 * g["alloc_u_de_fora"].sum() / g["alloc_u"].sum(), 1),
            "domicilios_2010_que_mudam_de_celula_com_o_reposicionamento_(k)": round(float(dif.abs().sum() / 2), 0),
            "pct_do_dom_10": round(100 * float(dif.abs().sum() / 2) / g["dom_10"].sum(), 1),
            "celulas_com_|mudanca|_>=_0,5": int((dif.abs() >= 0.5).sum()),
            "dom_10_nessas_celulas": int(g.loc[dif.abs() >= 0.5, "dom_10"].sum()),
            "celulas_com_|mudanca|_>=_10_pct_do_dom_10": int(((dif.abs() >= 0.1 * g["dom_10"]) & (dif.abs() >= 0.5)).sum()),
            "dom_10_nessas": int(g.loc[(dif.abs() >= 0.1 * g["dom_10"]) & (dif.abs() >= 0.5), "dom_10"].sum()),
        },
        "k_dom_ocupado_por_endereco_residencial": round(k, 3),
    }


def sensibilidade(u: gpd.GeoDataFrame, k: float, col: str) -> dict:
    """Classes e faixa da expansão com o dom_10 reposicionado (cenário adotado). Só medido."""
    v = u[~u["a_parte_setor_136"].fillna(False).astype(bool)].copy()
    rep = aditivo(v, k, col)
    antes = v[v["classe"] != "vazia"].copy()
    cl_antes = v.set_index("unidade")["classe"]
    v["dom_10"] = rep
    v["d_dom"] = v["dom_22"] - v["dom_10"]
    v = v[(v["dom_10"] > 0) | (v["dom_22"] > 0)].copy()
    v["classe"] = s1.classificar(v["dom_10"], v["dom_22"])
    fx_antes, fx_depois = s1.faixa_expansao(antes), s1.faixa_expansao(v)

    def resumo(x):
        return {"unidades": int(len(x)),
                "por_classe": {c: {"unidades": int((x["classe"] == c).sum()),
                                   "dom_10": int(x.loc[x["classe"] == c, "dom_10"].sum()),
                                   "dom_22": int(x.loc[x["classe"] == c, "dom_22"].sum())} for c in s1.CLASSES},
                "dom_10_total": int(x["dom_10"].sum()),
                "perda_bruta": int(-x.loc[x["d_dom"] < 0, "d_dom"].sum())}
    cl_depois = v.set_index("unidade")["classe"].reindex(cl_antes.index).fillna("vazia")
    muda = cl_antes != cl_depois
    trans = pd.crosstab(cl_antes[muda], cl_depois[muda])
    return {
        "regra": f"dom_10 + k × ({col} − alloc_u), arredondado (0,5 para cima), mínimo 0; "
                 "cenário adotado; população não reposicionada",
        "adotado_atual": {**resumo(antes), "faixa_expansao": fx_antes},
        "reposicionado": {**resumo(v), "faixa_expansao": fx_depois},
        "transicoes_de_classe": {str(a): {str(b): int(n) for b, n in row.items() if n}
                                 for a, row in trans.iterrows()},
    }


# --------------------------------------------------------------------------

def main() -> None:
    area = paths.carregar_area_estudo()
    camada = ex.ler_camada()
    u = ex.universo(camada, area)
    u["setor_2010"] = ex.situacao_2010(u, ex.malha_2010(u.crs))
    u["a_parte_setor_136"] = u["a_parte_setor_136"].fillna(False).astype(bool)

    f, por_arquivo = ler_faces(u.crs)
    ov = recorte(f, u)
    pts = ex.ler_cnefe(u.crs)
    pts = pts[pts["COD_ESPECIE"].isin(["1", "2"])].reset_index(drop=True)
    pts = ligar_pontos(pts, f, u)
    o = modelos(ov, pts, f)
    u = por_unidade(u, o)

    urb200 = (u["res_grupo"] == "200 m") & (u["setor_2010"] == "URBANO")
    k = float(u.loc[urb200, "dom_10"].sum() / u.loc[urb200, "alloc_u"].sum())
    grupo_urb = urb200 & ~u["a_parte_setor_136"]
    viz = vizinhas_rainha(u)
    d_face = pts.loc[pts["cel"].isin(set(u.loc[urb200, "unidade"])), "d_face"]

    ext = u[grupo_urb & (u["classe"] == "extinta")]
    nov = u[grupo_urb & (u["classe"] == "nova")]
    ext_rural200 = u[(u["res_grupo"] == "200 m") & (u["setor_2010"] != "URBANO")
                     & ~u["a_parte_setor_136"] & (u["classe"] == "extinta")]

    ext_g = ext.copy()
    ext_g["grupo"] = s1.agrupamentos(ext_g.geometry)
    top = ext_g.groupby("grupo")["dom_10"].sum().idxmax()
    agrup = ext_g[ext_g["grupo"] == top]
    setores_agrup = f.loc[o.loc[o["unidade"].isin(agrup["unidade"]) & (o["frac"] > 0), "fi"].unique(),
                          "CD_SETOR"].value_counts().to_dict()

    resultado = {
        "objeto": "deslocamento de domicílios entre células pela repartição uniforme ao longo da "
                  "face de quadra na grade de 2010 (Grade Estatística, 2016, p. 18–19)",
        "camada": {"arquivo": paths.relativo(s1.CAMADA),
                   "sha256_conteudo_conferido": metadados.ler(s1.CAMADA)["sha256_conteudo"]},
        "faces_2010": {"arquivos": por_arquivo,
                       "nota": "só o distrito-sede (05) tem atributos; os outros 4 trazem só geometria"},
        "cnefe_2022": {"domicilios_especie_1_ou_2": int(len(pts)),
                       "raio_de_ligacao_a_face_m": RAIO_FACE_M,
                       "distancia_a_face_residencial_2010_nas_200m_de_setor_urbano_p50_p75_p90_p95_p99":
                           [round(float(x), 1) for x in d_face.quantile([.5, .75, .9, .95, .99])],
                       "ligados_a_alguma_face": int(pts["fi"].notna().sum())},
        "validacao_do_modelo_uniforme": validacao(u),
        "k": round(k, 3),
        "extintas_urbanas": {
            "definicao": "extintas de 200 m com centroide em setor urbano de 2010, fora do setor "
                         "430160205000136 (cenário adotado)",
            **resumo_grupo(ext, u, viz, pts, o, f, k, mecanismo_extinta),
            "linha_de_base_outras_classes_urbanas": comparacao_classes(u, grupo_urb),
        },
        "agrupamento_053_054": {
            "unidades": agrup["unidade"].tolist(), "dom_10": int(agrup["dom_10"].sum()),
            "setores_2010_das_faces": setores_agrup,
            "tot_res_uniforme": round(float(agrup["alloc_u"].sum()), 1),
            "tot_res_pelos_pontos_2022": round(float(agrup["alloc_p"].sum()), 1),
            "por_mecanismo": {str(n): int(len(s)) for n, s in agrup.groupby(mecanismo_extinta(agrup, k))},
            "faces_2010_x_cnefe_2022": faces_vs_2022(agrup["unidade"], o, pts, f),
        },
        "extintas_urbanas_por_fenomeno": {
            "decisao": "2026-09-23: classes mantidas; os dois fenômenos separados no texto "
                       "(resultados_s1.md § 12.4); outros = sem face residencial de 2010 ou "
                       "com ponto de 2022 na própria unidade",
            **fenomenos_das_extintas(ext, k, agrup["unidade"]),
        },
        "extintas_200m_em_setor_rural_2010": {
            "unidades": int(len(ext_rural200)), "dom_10": int(ext_rural200["dom_10"].sum()),
            "atravessadas_por_face_residencial_de_2010": int((ext_rural200["faces"] > 0).sum()),
            "tot_res_uniforme": round(float(ext_rural200["alloc_u"].sum()), 1)},
        "novas_urbanas": {
            "definicao": "novas de 200 m com centroide em setor urbano de 2010, fora do setor 136",
            **resumo_grupo(nov, u, viz, pts, o, f, k, mecanismo_nova),
        },
        "escala_no_urbano": escala_cidade(u, o, f, k),
        "sensibilidade_reposicionado": sensibilidade(u, k, "alloc_p"),
        "sensibilidade_reposicionado_faces_sem_crescimento": sensibilidade(u, k, "alloc_pe"),
        "crs_medicao_distancia": paths.crs_producao(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=int), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=int)[:9000])


if __name__ == "__main__":
    main()
