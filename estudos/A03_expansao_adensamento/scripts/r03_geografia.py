"""
A03 — reconhecimento, item 3: geografia entre censos.

  (a) 2010 -> 2022 pelo de/para oficial do IBGE
      (Historico_formacao_Setores_Censitarios_2010_2022.xlsx), com a cadeia de
      códigos de formação (FRM) de cada setor de 2022 até 2010;
  (b) malha urbana de 2000: hipóteses de CRS (declarado EPSG:32621 x UTM 21 SUL)
      medidas pela sobreposição com a malha de 2010 — RELATA, não decide;
  (c) 2000 -> 2010 por interseção de áreas (não há de/para oficial).

Toda ÁREA é medida no CRS de área do config (scripts/utils/medidas.py);
operações espaciais no CRS de produção. Escreve derivados/r03_geografia.json.

Regras de classificação (grafo bipartido setor_antigo—setor_novo, por
componente conexo):
    1 antigo : 1 novo  -> 1:1
    1 : n              -> divisão
    n : 1              -> fusão
    n : m              -> redesenho (divisão e agregação misturadas)
  2010->2022: as arestas vêm do de/para; um 1:1 só é "série limpa" se TODA a
  cadeia de códigos de formação for 111 (manutenção plena, mesmo
  município/distrito/situação). 1:1 com segundo dígito 6 = ajuste vetorial;
  terceiro dígito != 1 = mudança de situação ou distrito.
  2000->2010: não há de/para, então a relação é GEOMÉTRICA: aresta se a
  interseção (com os setores antigos erodidos de E metros, tolerância a
  diferenças de traçado de borda) for >= L da área de qualquer um dos dois.
  (L, E) são CALIBRADOS no par 2010->2022, onde o de/para oficial é o
  gabarito: escolhe-se o par que mais reproduz a classe oficial de cada setor
  de 2022, e a concordância obtida é o erro esperado do método em 2000->2010.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.utils import medidas, paths  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
CODIGO = paths.codigo_ibge()
VET = paths.caminho("raw_vetor", "ibge")
PROD = paths.crs_producao()
IOU_LIMPO = 0.90

# CRS testados para a malha urbana de 2000. O .prj declara 32621 (UTM 21 N,
# WGS 84). As alternativas são as leituras "sul" do mesmo fuso, em três datums.
HIPOTESES_2000 = {
    "EPSG:32621 (declarado: WGS 84 / UTM 21N)": "EPSG:32621",
    "EPSG:32721 (WGS 84 / UTM 21S)": "EPSG:32721",
    "EPSG:29191 (SAD69 / UTM 21S)": "EPSG:29191",
    "EPSG:31981 (SIRGAS 2000 / UTM 21S)": "EPSG:31981",
}
# A malha rural de 2000 vem sem .prj, em graus. CRS decidido pelo responsável em
# 2026-09-22: SAD69 geográfico (registrado no .json irmão do arquivo); a malha
# urbana, SAD69 / UTM 21S (EPSG:29191). As hipóteses abaixo continuam medidas
# como registro da decisão.
CRS_RURAL_2000 = "EPSG:4618"


def componentes(arestas: set[tuple[str, str]]) -> list[tuple[set[str], set[str]]]:
    """Componentes conexos do grafo bipartido (antigos, novos)."""
    viz = defaultdict(set)
    for a, b in arestas:
        viz[("A", a)].add(("B", b))
        viz[("B", b)].add(("A", a))
    vistos, comps = set(), []
    for no in viz:
        if no in vistos:
            continue
        pilha, comp = [no], set()
        while pilha:
            n = pilha.pop()
            if n in vistos:
                continue
            vistos.add(n)
            comp.add(n)
            pilha.extend(viz[n] - vistos)
        comps.append(({x for t, x in comp if t == "A"}, {x for t, x in comp if t == "B"}))
    return comps


def tipo(antigos: set, novos: set) -> str:
    if len(antigos) == 1 and len(novos) == 1:
        return "1:1"
    if len(antigos) == 1:
        return "divisao"
    if len(novos) == 1:
        return "fusao"
    return "redesenho"


# --------------------------------------------------------------------------
# malhas
# --------------------------------------------------------------------------

def malha_2022() -> gpd.GeoDataFrame:
    g = gpd.read_file(VET / "censo_2022" / "RS_setores_CD2022.gpkg", where=f"CD_MUN = '{CODIGO}'")
    return g[["CD_SETOR", "SITUACAO", "geometry"]].to_crs(PROD)


def malha_2010() -> gpd.GeoDataFrame:
    g = gpd.read_file(f"zip://{VET / 'censo_2010' / 'rs_setores_censitarios.zip'}",
                      where=f"CD_GEOCODM = '{CODIGO}'")
    return g[["CD_GEOCODI", "TIPO", "geometry"]].rename(columns={"CD_GEOCODI": "cod"}).to_crs(PROD)


def malha_2000(crs_urbana: str) -> gpd.GeoDataFrame:
    """127 setores urbanos (individuais) + rurais, sem as envoltórias urbanas."""
    u = gpd.read_file(f"zip://{VET / 'censo_2000' / '4301602.zip'}")
    u = u.set_crs(crs_urbana, allow_override=True)[["ID_", "geometry"]].rename(columns={"ID_": "cod"})
    u["origem"] = "urbana"
    r = gpd.read_file(f"zip://{VET / 'censo_2000' / 'rs_setores_censitarios.zip'}")
    r = r[r["GEOCODIGO"].astype(str).str.startswith(CODIGO)].copy()
    r["cod"] = r["GEOCODIGO"].astype(str).str[:15]
    r["faixa"] = r["GEOCODIGO"].astype(str).str.contains("-")
    # envoltórias: feições da malha rural cujo código-base está na urbana
    r = r[~r["cod"].isin(set(u["cod"]))]
    r = r.set_crs(CRS_RURAL_2000).dissolve(by="cod", as_index=False)[["cod", "geometry"]]
    r["origem"] = "rural"
    u = u.to_crs(PROD)
    r = r.to_crs(PROD)
    g = pd.concat([u, r], ignore_index=True)
    g["geometry"] = g.geometry.make_valid()
    return gpd.GeoDataFrame(g, crs=PROD)


# --------------------------------------------------------------------------
# (a) 2010 -> 2022
# --------------------------------------------------------------------------

def depara_2010_2022(m2010: gpd.GeoDataFrame, m2022: gpd.GeoDataFrame) -> dict:
    arq = next((DERIV / "planilhas" / "c2022").glob("Historico_formacao*.csv"))
    df = pd.read_csv(arq, sep=";", dtype=str)
    df = df[df["GEOCODIGO_2022_DIVULGAÇÃO"].str.startswith(CODIGO)
            | df["GEOCODIGO_2010"].str.startswith(CODIGO)]
    frm_cols = [c for c in df.columns if c.startswith("FRM_")]

    arestas, cadeias = set(), defaultdict(list)
    for _, l in df.iterrows():
        par = (l["GEOCODIGO_2010"], l["GEOCODIGO_2022_DIVULGAÇÃO"])
        arestas.add(par)
        cadeias[par].append([str(l[c]) for c in frm_cols])

    resultado = {"linhas_de_para": int(len(df)),
                 "setores_2010_no_de_para": len({a for a, _ in arestas}),
                 "setores_2022_no_de_para": len({b for _, b in arestas}),
                 "setores_2010_na_malha_fora_do_de_para": sorted(set(m2010["cod"]) - {a for a, _ in arestas}),
                 "setores_2022_na_malha_fora_do_de_para": sorted(set(m2022["CD_SETOR"]) - {b for _, b in arestas}),
                 "fora_do_municipio": sorted({x for par in arestas for x in par if not x.startswith(CODIGO)})}

    geo10 = m2010.set_index("cod").geometry
    geo22 = m2022.set_index("CD_SETOR").geometry
    classes = defaultdict(lambda: {"componentes": 0, "setores_2010": 0, "setores_2022": 0})
    detalhe_1a1 = defaultdict(int)
    serie_limpa, iou_limpos = [], []
    for antigos, novos in componentes(arestas):
        t = tipo(antigos, novos)
        classes[t]["componentes"] += 1
        classes[t]["setores_2010"] += len(antigos)
        classes[t]["setores_2022"] += len(novos)
        if t != "1:1":
            continue
        (a,), (b,) = antigos, novos
        codigos = [c for cad in cadeias[(a, b)] for c in cad if c and c != "nan"]
        if all(c == "111" for c in codigos):
            sub = "limpo (toda a cadeia 111)"
            serie_limpa.append(b)
            if a in geo10.index and b in geo22.index:
                g1, g2 = geo10[a], geo22[b]
                iou_limpos.append(medidas.area_m2(g1.intersection(g2)) / medidas.area_m2(g1.union(g2)))
        elif any(len(c) == 3 and c[1] == "6" for c in codigos):
            sub = "ajuste vetorial (x6x)"
        elif any(len(c) == 3 and c[2] != "1" for c in codigos):
            sub = "mudança de situação ou distrito (xx2..xx6)"
        else:
            sub = "outro (divisão/agregação que resultou em 1:1)"
        detalhe_1a1[sub] += 1
    resultado.update({
        "classes": dict(classes), "detalhe_1a1": dict(detalhe_1a1),
        "setores_2022_serie_limpa": len(serie_limpa),
        "iou_serie_limpa": ({"n": len(iou_limpos), "min": min(iou_limpos),
                             "mediana": float(pd.Series(iou_limpos).median())} if iou_limpos else None),
        "_arestas": arestas,
        "codigos_frm_encontrados": pd.Series(
            [c for cads in cadeias.values() for cad in cads for c in cad if c and c != "nan"]
        ).value_counts().to_dict(),
    })
    return resultado


# --------------------------------------------------------------------------
# (b) hipóteses de CRS de 2000 e (c) 2000 -> 2010
# --------------------------------------------------------------------------

def hipoteses_crs(m2010: gpd.GeoDataFrame) -> dict:
    uniao10 = m2010.geometry.union_all()
    r = gpd.read_file(f"zip://{VET / 'censo_2000' / 'rs_setores_censitarios.zip'}")
    envoltoria = r[r["GEOCODIGO"].astype(str).str.contains(f"{CODIGO}05000001-")].set_crs(
        CRS_RURAL_2000).to_crs(PROD).geometry.union_all()
    out = {}
    for rotulo, crs in HIPOTESES_2000.items():
        u = gpd.read_file(f"zip://{VET / 'censo_2000' / '4301602.zip'}").set_crs(crs, allow_override=True)
        u = u.to_crs(PROD)
        u["geometry"] = u.geometry.make_valid()
        uniao00 = u.geometry.union_all()
        area00 = medidas.area_m2(uniao00)
        inter = medidas.area_m2(uniao00.intersection(uniao10))
        # melhor IoU de cada setor de 2000 com algum setor de 2010
        melhores, dx, dy = [], [], []
        for g in u.geometry:
            cand = m2010[m2010.intersects(g)]
            pares = [(medidas.area_m2(g.intersection(h)) / medidas.area_m2(g.union(h)), h)
                     for h in cand.geometry]
            iou, h = max(pares, key=lambda p: p[0], default=(0.0, None))
            melhores.append(iou)
            if h is not None and iou >= 0.3:
                dx.append(h.centroid.x - g.centroid.x)
                dy.append(h.centroid.y - g.centroid.y)
        centro = gpd.GeoSeries([uniao00.centroid], crs=PROD).to_crs("EPSG:4326").iloc[0]
        out[rotulo] = {
            "centroide_lon_lat": [round(centro.x, 4), round(centro.y, 4)],
            "area_malha_urbana_km2": round(area00 / 1e6, 3),
            "fracao_dentro_da_malha_2010": round(inter / area00, 4) if area00 else 0,
            "fracao_dentro_da_envoltoria_urbana_rural_2000": round(
                medidas.area_m2(uniao00.intersection(envoltoria)) / area00, 4) if area00 else 0,
            "iou_setor_melhor_par_2010_mediana": round(float(pd.Series(melhores).median()), 4),
            "setores_com_iou_ge_0_9": int(sum(m >= 0.9 for m in melhores)),
            "deslocamento_medio_para_2010_m": ([round(float(pd.Series(dx).mean()), 1),
                                                round(float(pd.Series(dy).mean()), 1)] if dx else None),
            "pares_usados_no_deslocamento": len(dx),
            "crs_medicao_area": medidas.crs_medicao_area(),
        }
    return out


def classes_por_setor(arestas: set[tuple[str, str]]) -> dict[str, str]:
    """Classe (1:1, divisão, fusão, redesenho) de cada setor NOVO."""
    out = {}
    for antigos, novos in componentes(arestas):
        t = tipo(antigos, novos)
        for n in novos:
            out[n] = t
    return out


def arestas_geometricas(antigos: gpd.GeoDataFrame, novos: gpd.GeoDataFrame,
                        limiar: float, erosao: float) -> set[tuple[str, str]]:
    """(antigo, novo) se a interseção >= limiar da área de um dos dois.

    Os antigos são erodidos de `erosao` metros (no CRS de produção) antes da
    interseção — tolerância a diferença de traçado de borda entre as malhas.
    """
    area_a = dict(zip(antigos["cod"], medidas.areas_m2(antigos)))
    area_n = dict(zip(novos["cod"], medidas.areas_m2(novos)))
    a = antigos[["cod", "geometry"]].copy()
    if erosao:
        erodido = a.geometry.buffer(-erosao)
        a["geometry"] = erodido.where(~erodido.is_empty, a.geometry)
    inter = gpd.overlay(a, novos[["cod", "geometry"]].rename(columns={"cod": "cod_n"}),
                        how="intersection", keep_geom_type=True)
    inter["m2"] = medidas.areas_m2(inter)
    area_a_ef = dict(zip(a["cod"], medidas.areas_m2(a)))
    return {(r.cod, r.cod_n) for r in inter.itertuples()
            if r.m2 >= limiar * area_a_ef[r.cod] or r.m2 >= limiar * area_n[r.cod_n]}


def resumo_classes(arestas: set[tuple[str, str]]) -> dict:
    classes = defaultdict(lambda: {"componentes": 0, "setores_antigos": 0, "setores_novos": 0})
    for antigos, novos in componentes(arestas):
        t = tipo(antigos, novos)
        classes[t]["componentes"] += 1
        classes[t]["setores_antigos"] += len(antigos)
        classes[t]["setores_novos"] += len(novos)
    return dict(classes)


GRADE = [(l, e) for l in (0.05, 0.10, 0.25, 0.50) for e in (0, 20, 40)]


def calibrar(m2010: gpd.GeoDataFrame, m2022: gpd.GeoDataFrame, arestas_oficiais: set) -> dict:
    """Concordância do método geométrico com o de/para oficial, 2010->2022."""
    oficial = classes_por_setor(arestas_oficiais)
    novos = m2022.rename(columns={"CD_SETOR": "cod"})
    grade = []
    for limiar, erosao in GRADE:
        geo = classes_por_setor(arestas_geometricas(m2010, novos, limiar, erosao))
        acerto = sum(geo.get(c) == t for c, t in oficial.items()) / len(oficial)
        grade.append({"limiar": limiar, "erosao_m": erosao, "concordancia": round(acerto, 4)})
    melhor = max(grade, key=lambda g: g["concordancia"])
    return {"grade": grade, "melhor": melhor}


def main() -> None:
    m2010, m2022 = malha_2010(), malha_2022()
    resultado = {"a_2010_2022": depara_2010_2022(m2010, m2022)}
    arestas_oficiais = resultado["a_2010_2022"].pop("_arestas")
    calib = calibrar(m2010, m2022, arestas_oficiais)
    resultado["calibracao_metodo_geometrico_2010_2022"] = calib
    hip = hipoteses_crs(m2010)
    resultado["b_hipoteses_crs_2000"] = hip
    melhor = max(hip, key=lambda k: hip[k]["iou_setor_melhor_par_2010_mediana"])
    m2000 = malha_2000(HIPOTESES_2000[melhor])
    lim, ero = calib["melhor"]["limiar"], calib["melhor"]["erosao_m"]
    arestas = arestas_geometricas(m2000, m2010, lim, ero)
    compat = pd.read_csv(next((DERIV / "bage" / "c2000").glob("Compatibiliza*.csv")), sep=";", dtype=str)
    resultado["c_2000_2010"] = {
        "condicionado_a": f"malha urbana de 2000 lida como {melhor}; rural como {CRS_RURAL_2000} (suposição)",
        "metodo": f"interseção >= {lim:.0%} de um dos setores, antigos erodidos {ero} m "
                  f"(calibrado em 2010->2022: concordância {calib['melhor']['concordancia']:.1%})",
        "setores_2000": int(len(m2000)), "setores_2010": int(len(m2010)),
        "setores_2000_que_foram_para_outro_municipio_em_2001": sorted(compat["Cod_setor"]),
        "classes": resumo_classes(arestas),
        "setores_2000_sem_par_em_bage_2010": sorted(set(m2000["cod"]) - {a for a, _ in arestas}),
        "setores_2010_sem_par": sorted(set(m2010["cod"]) - {b for _, b in arestas}),
        "sensibilidade": [{"limiar": l, "erosao_m": e,
                           "classes": resumo_classes(arestas_geometricas(m2000, m2010, l, e))}
                          for l, e in GRADE],
    }
    (DERIV / "r03_geografia.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=str)[:15000])


if __name__ == "__main__":
    main()
