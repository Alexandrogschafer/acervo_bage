"""
A03 — subordinada 2: as unidades que ganham domicílio e perdem população.

Conferência visual do responsável (2026-09-23, resultados_s1.md § 12): as 137
unidades da divergência de sinal estão dispersas pela cidade, não contíguas;
há 5 unidades rurais e 6 grandes rurais junto à borda urbana; as urbanas,
menores, espalhadas; poucas no miolo central mais denso. Este script MEDE essa
leitura; não reclassifica nada (confere o sha256_conteudo da camada).

Cenário adotado: sem as unidades do setor de 2010 430160205000136 (nenhuma das
137 está nele). Divergente = d_dom > 0 e d_pop < 0 (a regra do § 8).

1. CONTIGUIDADE. Agrupamentos rainha (a função do s1) e contagem de pares
   divergente–divergente contra a permutação do rótulo entre as ADENSADAS (só
   elas podem divergir: a nova não tem população em 2010).
2. GRUPOS pela geografia (nunca pelo rótulo de situação do setor):
     urbana       unidade de 200 m;
     rural junto à borda   unidade de 1 km (inclui as harmonizadas) a menos de
                           DIST_BORDA_M da área urbanizada de 2022;
     rural remota          as demais de 1 km.
   Direção a partir do centro do § 1 (rumo em 8 setores).
3. RAZÃO moradores/domicílio em 2010 e 2022: mediana nas divergentes contra o
   restante das unidades ocupadas nos dois anos (urbanas e rurais em separado),
   com permutação do rótulo para a diferença de medianas. Convergência = a
   divergente parte acima da razão da cidade e termina mais perto dela;
   esvaziamento = não parte acima.
4. ÁREA CONSOLIDADA MAIS DENSA, em quatro recortes:
     densa IBGE   ≥ 50 % da unidade na "Área urbanizada" de Densidade "Densa"
                  (Áreas Urbanizadas 2022);
     quartil      unidade de 200 m com dom_10 no quartil superior das
                  unidades de 200 m ocupadas em 2010;
     miolo        unidade de 200 m a até 1 km e a até 1,5 km do centro do § 1
                  (a leitura da conferência: "miolo central").
   Esperado = divergentes de 200 m × fração das adensadas de 200 m na zona.
5. A UNIDADE RURAL GRANDE ISOLADA A LESTE da mancha urbana: a divergente de 1 km
   junto à borda mais a leste do centro. Domicílios e moradores nos dois anos e
   os endereços do CNEFE 2022 dentro dela (espécie, tipo, localidade, nível).

LÊ a camada de trabalho, data/raw/ (área urbanizada 2022, CNEFE 2022) e config/.
ESCREVE só derivados/s2_divergencia.json.
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

import s1_expansao_adensamento as s1  # noqa: E402
import s1_extintas as ex  # noqa: E402
from scripts.utils import medidas, metadados, paths  # noqa: E402

SAIDA = s1.DERIV / "s2_divergencia.json"
DIST_BORDA_M = 1000
RAIOS_MIOLO_KM = (1, 1.5)
PERMUTACOES = 9999
SEMENTE = 20260923
RUMOS = ["leste", "nordeste", "norte", "noroeste", "oeste", "sudoeste", "sul", "sudeste"]
ESPECIES = {"1": "domicilio_particular", "2": "domicilio_coletivo", "3": "estab_agropecuario",
            "4": "estab_ensino", "5": "estab_saude", "6": "estab_outras_finalidades",
            "7": "edificacao_em_construcao", "8": "estab_religioso"}


def ler_area_urbanizada(crs) -> tuple[object, object]:
    area = paths.carregar_area_estudo()
    au = gpd.read_file(f"/vsizip/{s1.AU_ZIP}/{s1.AU_SHP}",
                       bbox=tuple(area.to_crs("EPSG:4674").total_bounds)).to_crs(crs)
    au = au[(au["Tipo"] == s1.TIPO_URBANIZADA) & au.intersects(area.union_all())]
    return au.union_all(), au[au["Densidade"] == "Densa"].union_all()


def centro(c: gpd.GeoDataFrame) -> tuple[float, float]:
    """O centro do § 1: centro médio dos domicílios de 2010, com todas as unidades."""
    p = c.geometry.centroid
    return float(np.average(p.x, weights=c["dom_10"])), float(np.average(p.y, weights=c["dom_10"]))


def rumo(dx: float, dy: float) -> str:
    return RUMOS[int(((np.degrees(np.arctan2(dy, dx)) + 22.5) % 360) // 45)]


# --------------------------------------------------------------------------
# 1. contiguidade
# --------------------------------------------------------------------------

def contiguidade(v: gpd.GeoDataFrame) -> dict:
    d = v[v["div"]].copy()
    d["grupo"] = s1.agrupamentos(d.geometry)
    tam = d.groupby("grupo").size()
    ad = v[v["classe"] == "adensada"].reset_index(drop=True)
    arvore = shapely.STRtree(ad.geometry.values)
    a, b = arvore.query(ad.geometry.buffer(s1.TOLERANCIA_CONTIGUIDADE_M).values, predicate="intersects")
    m = a < b
    a, b = a[m], b[m]
    rot = ad["div"].values
    obs = int((rot[a] & rot[b]).sum())
    rng = np.random.default_rng(SEMENTE)
    perm = np.array([(lambda r: int((r[a] & r[b]).sum()))(rng.permutation(rot)) for _ in range(PERMUTACOES)])
    return {
        "divergentes": int(len(d)),
        "agrupamentos": int(len(tam)),
        "isoladas": int((tam == 1).sum()),
        "agrupamentos_de_2_a_4": int(tam.between(2, 4).sum()),
        "agrupamentos_de_5_ou_mais": int((tam >= 5).sum()),
        "maior_agrupamento": int(tam.max()),
        "maiores_agrupamentos": [
            {"unidades": int(len(g)), "dom_10": int(g["dom_10"].sum()), "d_dom": int(g["d_dom"].sum()),
             "d_pop": int(g["d_pop"].sum()),
             "distancia_ao_centro_km_mediana": round(float(g["dist_centro_km"].median()), 1),
             "rumo_mais_frequente": g["rumo"].mode().iloc[0]}
            for _, g in sorted(d.groupby("grupo"), key=lambda x: -len(x[1]))[:5]],
        "unidades_em_agrupamento_de_5_ou_mais": int(tam[tam >= 5].sum()),
        "pares_rainha_divergente_divergente_entre_as_adensadas": {
            "adensadas": int(len(ad)), "das_quais_divergentes": int(rot.sum()),
            "observados": obs, "esperado_media": round(float(perm.mean()), 1),
            "p5_p95": [float(np.percentile(perm, 5)), float(np.percentile(perm, 95))],
            "p_mais_que_o_acaso": round(((perm >= obs).sum() + 1) / (PERMUTACOES + 1), 4),
            "permutacoes": PERMUTACOES, "semente": SEMENTE},
    }


# --------------------------------------------------------------------------
# 2. grupos
# --------------------------------------------------------------------------

def grupos(d: gpd.GeoDataFrame) -> dict:
    out = {}
    for nome, g in d.groupby("grupo_geo"):
        out[nome] = {
            "unidades": int(len(g)), "por_resolucao": g["resolucao"].value_counts().to_dict(),
            "dom_10": int(g["dom_10"].sum()), "dom_22": int(g["dom_22"].sum()),
            "pop_10": int(g["pop_10"].sum()), "pop_22": int(g["pop_22"].sum()),
            "dentro_da_area_urbanizada": int((g["fracao_au"] >= s1.LIMIAR_DENTRO).sum()),
            "distancia_ao_centro_km_min_mediana_max": [round(float(x), 1) for x in
                                                       (g["dist_centro_km"].min(), g["dist_centro_km"].median(), g["dist_centro_km"].max())],
            "por_rumo": g["rumo"].value_counts().to_dict(),
        }
        if nome != "urbana (200 m)":
            out[nome]["unidades_lista"] = [
                {"unidade": r.unidade, "resolucao": r.resolucao, "dom_10": int(r.dom_10), "dom_22": int(r.dom_22),
                 "pop_10": int(r.pop_10), "pop_22": int(r.pop_22), "dist_centro_km": round(float(r.dist_centro_km), 1),
                 "rumo": r.rumo, "dist_area_urbanizada_m": round(float(r.dist_au_m), 0)}
                for r in g.sort_values("dist_centro_km").itertuples()]
    return out


# --------------------------------------------------------------------------
# 3. razão moradores/domicílio
# --------------------------------------------------------------------------

def dif_medianas(x: np.ndarray, rot: np.ndarray) -> float:
    return float(np.median(x[rot]) - np.median(x[~rot]))


def teste_mediana(x: np.ndarray, rot: np.ndarray, rng) -> dict:
    obs = dif_medianas(x, rot)
    perm = np.array([dif_medianas(x, rng.permutation(rot)) for _ in range(PERMUTACOES)])
    return {"diferenca_de_medianas": round(obs, 3),
            "p_divergentes_acima": round(((perm >= obs).sum() + 1) / (PERMUTACOES + 1), 4),
            "p_divergentes_abaixo": round(((perm <= obs).sum() + 1) / (PERMUTACOES + 1), 4)}


def razao(v: gpd.GeoDataFrame, r_cidade: dict) -> dict:
    oc = v[(v["dom_10"] > 0) & (v["dom_22"] > 0)].copy()
    oc["r10"] = oc["pop_10"] / oc["dom_10"]
    oc["r22"] = oc["pop_22"] / oc["dom_22"]
    oc["urb"] = np.where(oc["resolucao"] == "200 m", "urbanas (200 m)", "rurais (1 km)")
    rng = np.random.default_rng(SEMENTE)
    out = {"razao_da_cidade": r_cidade,
           "regra": "unidades ocupadas nos dois anos; restante = ocupadas não divergentes"}
    for nome, g in oc.groupby("urb"):
        rot = g["div"].values
        lin = {}
        for rotulo, s in (("divergentes", g[rot]), ("restante", g[~rot])):
            lin[rotulo] = {
                "unidades": int(len(s)),
                "mediana_2010": round(float(s["r10"].median()), 2),
                "mediana_2022": round(float(s["r22"].median()), 2),
                "agregada_2010": round(float(s["pop_10"].sum() / s["dom_10"].sum()), 2),
                "agregada_2022": round(float(s["pop_22"].sum() / s["dom_22"].sum()), 2),
                "pct_acima_da_razao_da_cidade_2010": round(100 * float((s["r10"] > r_cidade["2010"]).mean()), 1),
                "mediana_da_queda_da_razao": round(float((s["r10"] - s["r22"]).median()), 2)}
        dv = g[rot]
        conv = (dv["r10"] > r_cidade["2010"]) & ((dv["r22"] - r_cidade["2022"]).abs() < (dv["r10"] - r_cidade["2010"]).abs())
        lin["teste_2010"] = teste_mediana(g["r10"].values, rot, rng)
        lin["teste_2022"] = teste_mediana(g["r22"].values, rot, rng)
        lin["divergentes_que_convergem"] = {
            "partem_acima_da_cidade_e_terminam_mais_perto": int(conv.sum()),
            "partem_acima_da_cidade": int((dv["r10"] > r_cidade["2010"]).sum()),
            "partem_na_razao_da_cidade_ou_abaixo": int((dv["r10"] <= r_cidade["2010"]).sum())}
        out[nome] = lin
    return out


# --------------------------------------------------------------------------
# 4. área consolidada mais densa
# --------------------------------------------------------------------------

def area_densa(v: gpd.GeoDataFrame, densa) -> dict:
    v = v.copy()
    v["fracao_densa"] = medidas.areas_m2(v.geometry.intersection(densa)) / v["area_m2"]
    m200 = v["resolucao"] == "200 m"
    oc200 = v[m200 & (v["dom_10"] > 0)]
    p75 = float(oc200["dom_10"].quantile(0.75))
    zonas = {"densa_ibge": v["fracao_densa"] >= s1.LIMIAR_DENTRO,
             "quartil_superior_dom_10": m200 & (v["dom_10"] >= p75),
             **{f"miolo_central_ate_{str(r).replace('.', ',')}_km_do_centro": m200 & (v["dist_centro_km"] <= r)
                for r in RAIOS_MIOLO_KM}}
    out = {"quartil_superior_dom_10_limiar": p75}
    ad200 = v[m200 & (v["classe"] == "adensada")]
    d200 = v[m200 & v["div"]]
    for nome, z in zonas.items():
        frac = float(z[ad200.index].mean())
        out[nome] = {
            "unidades_200m_ocupadas_em_2010_na_zona": int((z & m200 & (v["dom_10"] > 0)).sum()),
            "adensadas_200m_na_zona": int(z[ad200.index].sum()),
            "divergentes_200m_na_zona": int(z[d200.index].sum()),
            "divergentes_200m": int(len(d200)),
            "esperado_pela_fracao_das_adensadas": round(frac * len(d200), 1),
            "pct_das_divergentes_na_zona": round(100 * float(z[d200.index].mean()), 1),
            "pct_das_adensadas_na_zona": round(100 * frac, 1)}
    return out


# --------------------------------------------------------------------------
# 5. a unidade a leste
# --------------------------------------------------------------------------

def cnefe_na_unidade(geom, crs) -> dict:
    cand = sorted(ex.DIR_CNEFE.glob(f"{paths.codigo_ibge()}_*.zip"))
    with zipfile.ZipFile(ex.conferido(cand[0])) as z:
        membro = next(n for n in z.namelist() if n.endswith(".csv"))
        df = pd.read_csv(z.open(membro), sep=";", dtype=str, encoding="latin-1",
                         usecols=["COD_ESPECIE", "COD_TIPO_ESPECI", "NV_GEO_COORD", "DSC_LOCALIDADE",
                                  "COD_SETOR", "LATITUDE", "LONGITUDE"])
    g = gpd.GeoDataFrame(df.drop(columns=["LATITUDE", "LONGITUDE"]),
                         geometry=gpd.points_from_xy(pd.to_numeric(df["LONGITUDE"]), pd.to_numeric(df["LATITUDE"])),
                         crs="EPSG:4674").to_crs(crs)
    w = g[g.within(geom)]
    return {"enderecos": int(len(w)),
            "por_especie": {ESPECIES.get(k, k): int(n) for k, n in w["COD_ESPECIE"].value_counts().items()},
            "tipo_de_edificacao_dos_domicilios": w["COD_TIPO_ESPECI"].dropna().value_counts().to_dict(),
            "localidades": w["DSC_LOCALIDADE"].value_counts().to_dict(),
            "setores_2022": w["COD_SETOR"].value_counts().to_dict(),
            "nivel_de_geocodificacao": w["NV_GEO_COORD"].value_counts().to_dict()}


# --------------------------------------------------------------------------

def main() -> None:
    camada = ex.ler_camada()
    cx, cy = centro(camada)
    v = camada[~camada[s1.CAMPO_A_PARTE]].copy()
    v["div"] = (v["d_dom"] > 0) & (v["d_pop"] < 0)
    au, densa = ler_area_urbanizada(v.crs)
    v["dist_au_m"] = v.geometry.distance(au)
    c = v.geometry.centroid
    v["rumo"] = [rumo(x - cx, y - cy) for x, y in zip(c.x, c.y)]
    v["grupo_geo"] = np.select(
        [v["resolucao"] == "200 m", v["dist_au_m"] < DIST_BORDA_M],
        ["urbana (200 m)", f"rural (1 km) junto à borda, a menos de {DIST_BORDA_M} m da área urbanizada"],
        f"rural (1 km) remota, a {DIST_BORDA_M} m ou mais da área urbanizada")
    d = v[v["div"]]
    r_cidade = {"2010": round(float(v["pop_10"].sum() / v["dom_10"].sum()), 3),
                "2022": round(float(v["pop_22"].sum() / v["dom_22"].sum()), 3)}

    borda = d[d["grupo_geo"].str.startswith("rural (1 km) junto")].copy()
    borda["dx"] = borda.geometry.centroid.x - cx
    leste = borda.loc[borda["dx"].idxmax()]
    outras = d[d["unidade"] != leste["unidade"]]
    isolada = not outras.intersects(leste.geometry.buffer(s1.TOLERANCIA_CONTIGUIDADE_M)).any()

    resultado = {
        "objeto": "divergência de sinal (ganha domicílio e perde população), cenário adotado",
        "camada": {"arquivo": paths.relativo(s1.CAMADA),
                   "sha256_conteudo_conferido": metadados.ler(s1.CAMADA)["sha256_conteudo"]},
        "divergentes": {"unidades": int(len(d)), "d_dom": int(d["d_dom"].sum()), "d_pop": int(d["d_pop"].sum()),
                        "no_setor_136": int(camada.loc[(camada["d_dom"] > 0) & (camada["d_pop"] < 0), s1.CAMPO_A_PARTE].sum())},
        "1_contiguidade": contiguidade(v),
        "2_grupos": grupos(d),
        "3_razao_moradores_por_domicilio": razao(v, r_cidade),
        "4_area_consolidada_mais_densa": area_densa(v, densa),
        "5_unidade_rural_a_leste": {
            "unidade": leste["unidade"], "resolucao": leste["resolucao"],
            "dom_10": int(leste["dom_10"]), "dom_22": int(leste["dom_22"]),
            "pop_10": int(leste["pop_10"]), "pop_22": int(leste["pop_22"]),
            "razao_2010": round(leste["pop_10"] / leste["dom_10"], 2),
            "razao_2022": round(leste["pop_22"] / leste["dom_22"], 2),
            "dist_centro_km": round(float(leste["dist_centro_km"]), 1), "rumo": leste["rumo"],
            "dist_area_urbanizada_m": round(float(leste["dist_au_m"]), 0),
            "fracao_na_area_urbanizada": round(float(leste["fracao_au"]), 3),
            "isolada_de_outras_divergentes": bool(isolada),
            "cnefe_2022": cnefe_na_unidade(leste.geometry, v.crs)},
        "centro_EPSG31981": [round(cx, 0), round(cy, 0)],
        "crs_medicao_distancia": paths.crs_producao(),
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=int), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=int))


if __name__ == "__main__":
    main()
