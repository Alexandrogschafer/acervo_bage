"""
A03 — subordinada 2: preparação da conferência dos dois maiores agrupamentos da
divergência de sinal (resultados_s2.md § 1: 21 e 18 unidades, a oeste e a
noroeste, a cerca de 2 km do centro).

Não reclassifica nada; confere o sha256_conteudo da camada antes de ler.

IMAGEM DE FUNDO: não há imagem de satélite no acervo, e trazer uma exigiria fonte
nova, com licença e procedência registradas (docs/convencoes.md). O fundo das
figuras é vetorial: as faces de logradouro de 2010 (ruas), a área urbanizada de 2022
do IBGE (densa e pouco densa) e as demais unidades da grade. Para olhar sobre a
imagem, a camada saidas/s2_agrupamentos_divergencia.gpkg vai para o QGIS, como na
conferência de 2026-09-23.

ESCREVE:
    derivados/s2_agrupamentos_divergencia.json   lista por agrupamento (versionado)
    derivados/s2_agrupamentos_divergencia.csv    a mesma lista, em tabela (fora do git)
    saidas/s2_agrupamentos_divergencia.gpkg      unidades dos dois agrupamentos (+ .json)
    saidas/s2_detalhe_agrupamento_{1,2}.png      figuras de detalhe (+ .json)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

import s1_expansao_adensamento as s1  # noqa: E402
import s1_extintas as ex  # noqa: E402
import s1_figuras as fig1  # noqa: E402
import s1_faces_2010 as faces  # noqa: E402
import s2_divergencia as s2  # noqa: E402
from scripts.utils import metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

NOME = "s2_agrupamentos_divergencia"
SAIDA_JSON = s1.DERIV / f"{NOME}.json"
SAIDA_CSV = s1.DERIV / f"{NOME}.csv"
SAIDA_GPKG = s1.SAIDAS / f"{NOME}.gpkg"
QUANTOS = 2
MARGEM_M = 300
COR_AU_DENSA = "#efeee9"
COR_AU_POUCO = "#f6f5f1"
COR_RUA = "#b9b8b2"
COR_OUTRA_DIV = "#ec7a6a"
FONTES = f"{s1.FONTES};ibge_censo2010_faces_logradouros;ibge_areas_urbanizadas_2022"
FONTE_TXT = ("Fonte: IBGE — Grade Estatística 2010 e 2022; Base de Faces de Logradouros do "
             "Censo 2010; Áreas Urbanizadas do Brasil 2022. Unidade: célula da grade "
             "harmonizada.\nElaboração: ACERVO_BAGE, estudo A03 (subordinada 2), "
             "scripts/s2_agrupamentos.py. SIRGAS 2000 / UTM 21S (EPSG:31981). Figura de "
             "trabalho para conferência: não publicar.")


def razao(p, d):
    return np.where(d > 0, np.round(p / d.where(d > 0), 2), np.nan)


def main() -> None:
    camada = ex.ler_camada()
    cx, cy = s2.centro(camada)
    v = camada[~camada[s1.CAMPO_A_PARTE]].copy()
    v["div"] = (v["d_dom"] > 0) & (v["d_pop"] < 0)
    d = v[v["div"]].copy()
    d["grupo"] = s1.agrupamentos(d.geometry)
    ordem = d.groupby("grupo").size().sort_values(ascending=False, kind="stable").index[:QUANTOS]

    au_todos = s2.ler_area_urbanizada(v.crs)
    area = paths.carregar_area_estudo()
    au = gpd.read_file(f"/vsizip/{s1.AU_ZIP}/{s1.AU_SHP}",
                       bbox=tuple(area.to_crs("EPSG:4674").total_bounds)).to_crs(v.crs)
    au = au[(au["Tipo"] == s1.TIPO_URBANIZADA) & au.intersects(area.union_all())]
    ruas, _ = faces.ler_faces(v.crs)

    linhas, resumo, gpkg = [], [], []
    for n, g in enumerate(ordem, start=1):
        a = d[d["grupo"] == g].copy()
        c = a.geometry.centroid
        a = a.assign(ordem_x=c.x.round(0), ordem_y=-c.y.round(0)).sort_values(["ordem_y", "ordem_x"])
        a["agrupamento"] = n
        a["n"] = range(1, len(a) + 1)
        a["razao_10"] = razao(a["pop_10"], a["dom_10"])
        a["razao_22"] = razao(a["pop_22"], a["dom_22"])
        cg = a.union_all().centroid
        rumo = s2.rumo(cg.x - cx, cg.y - cy)
        resumo.append({
            "agrupamento": n, "unidades": int(len(a)), "rumo": rumo,
            "rumo_mais_frequente_das_unidades": pd.Series(
                [s2.rumo(x - cx, y - cy) for x, y in zip(c.x, c.y)]).mode().iloc[0],
            "distancia_do_centro_km": round(float(np.hypot(cg.x - cx, cg.y - cy) / 1000), 1),
            "dom_10": int(a["dom_10"].sum()), "dom_22": int(a["dom_22"].sum()),
            "pop_10": int(a["pop_10"].sum()), "pop_22": int(a["pop_22"].sum()),
            "razao_agregada_10": round(a["pop_10"].sum() / a["dom_10"].sum(), 2),
            "razao_agregada_22": round(a["pop_22"].sum() / a["dom_22"].sum(), 2),
            "razao_mediana_10": round(float(np.nanmedian(a["razao_10"])), 2),
            "razao_mediana_22": round(float(np.nanmedian(a["razao_22"])), 2),
            "dentro_da_area_urbanizada_densa": int(
                (s2.medidas.areas_m2(a.geometry.intersection(au_todos[1])) / a["area_m2"] >= s1.LIMIAR_DENTRO).sum()),
            "figura": f"saidas/s2_detalhe_agrupamento_{n}.png",
        })
        cols = ["agrupamento", "n", "unidade", "resolucao", "dom_10", "dom_22", "pop_10", "pop_22",
                "razao_10", "razao_22", "d_dom", "d_pop", "dist_centro_km"]
        linhas.extend(a[cols].assign(dist_centro_km=a["dist_centro_km"].round(2)).to_dict("records"))
        gpkg.append(a[cols + ["geometry"]])
        desenhar(n, a, rumo, resumo[-1], v, d, au, ruas)

    tab = pd.DataFrame(linhas)
    tab.to_csv(SAIDA_CSV, index=False, sep=";", decimal=",")
    SAIDA_JSON.write_text(json.dumps({
        "objeto": "os dois maiores agrupamentos contíguos (rainha, 1 m) da divergência de sinal, "
                  "cenário adotado; preparação da conferência visual (resultados_s2.md § 1)",
        "camada_sha256_conteudo": metadados.ler(s1.CAMADA)["sha256_conteudo"],
        "agrupamentos": resumo,
        "unidades": [{k: (None if isinstance(x, float) and np.isnan(x) else x) for k, x in r.items()}
                     for r in linhas],
        "numeracao": "n = ordem de leitura na figura (de norte para sul, de oeste para leste)",
        "imagem_de_fundo": "não há imagem no acervo; fundo vetorial. Para imagem, abrir o gpkg no QGIS",
        "crs": paths.crs_producao(),
    }, ensure_ascii=False, indent=2, default=int), encoding="utf-8")

    camada_gpkg = gpd.GeoDataFrame(pd.concat(gpkg), crs=v.crs)
    if SAIDA_GPKG.exists():
        SAIDA_GPKG.unlink()
    camada_gpkg.to_file(SAIDA_GPKG, driver="GPKG", layer=NOME)
    dados = metadados.montar(
        SAIDA_GPKG, tema="censo", fonte_id=s1.FONTES, versao="s2-v1", crs=paths.crs_producao(),
        licenca="IBGE — uso livre com citação da fonte", autorizacao_fonte=True,
        pode_publicar=False, status_conferencia="pendente",
        observacoes=("Apoio à conferência visual dos dois maiores agrupamentos da divergência de "
                     "sinal do A03 (subordinada 2): unidades, com domicílios, moradores e razão "
                     "nos dois anos, e o número (n) usado nas figuras de detalhe. Script: "
                     "estudos/A03_expansao_adensamento/scripts/s2_agrupamentos.py."))
    dados["sha256_conteudo"] = sha256_conteudo(SAIDA_GPKG)
    metadados.escrever(SAIDA_GPKG, dados, sobrescrever=True)
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    print(tab.to_string(index=False))


def desenhar(n, a, rumo, r, v, d, au, ruas):
    x0, y0, x1, y1 = a.total_bounds
    lado = max(x1 - x0, y1 - y0) + 2 * MARGEM_M
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ext = (mx - lado / 2, my - lado / 2, mx + lado / 2, my + lado / 2)
    def br(x, casas=0) -> str:
        return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    rumos = rumo if rumo == r["rumo_mais_frequente_das_unidades"] else \
        f"{rumo}-{r['rumo_mais_frequente_das_unidades']}"
    fig, ax = fig1.figura(
        f"Bagé — agrupamento {n} da divergência de sinal ({len(a)} unidades, a {rumos}, "
        f"{br(r['distancia_do_centro_km'], 1)} km do centro)",
        f"Domicílios {br(r['dom_10'])} → {br(r['dom_22'])}; moradores {br(r['pop_10'])} → "
        f"{br(r['pop_22'])}; moradores por domicílio {br(r['razao_agregada_10'], 2)} → "
        f"{br(r['razao_agregada_22'], 2)}. Números das células = coluna n da lista.", ext)
    ax.set_facecolor(fig1.SUPERFICIE)
    au[au["Densidade"] == "Densa"].plot(ax=ax, color=COR_AU_DENSA, zorder=1)
    au[au["Densidade"] != "Densa"].plot(ax=ax, color=COR_AU_POUCO, zorder=1)
    v.plot(ax=ax, facecolor="none", edgecolor="#cfcec8", linewidth=0.5, zorder=2)
    ruas.plot(ax=ax, color=COR_RUA, linewidth=0.5, zorder=3)
    outras = d[~d["unidade"].isin(a["unidade"])]
    outras.plot(ax=ax, facecolor=COR_OUTRA_DIV, alpha=0.45, edgecolor="none", zorder=4)
    a.plot(ax=ax, facecolor=fig1.COR_DIVERGENCIA, alpha=0.55, edgecolor=fig1.COR_DIVERGENCIA,
           linewidth=1.0, zorder=5)
    for row in a.itertuples():
        p = row.geometry.centroid
        ax.text(p.x, p.y, str(row.n), ha="center", va="center", fontsize=8, fontweight="bold",
                color="white", zorder=8)
    ax.set_xlim(ext[0], ext[2])
    ax.set_ylim(ext[1], ext[3])
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    fig1.escala_e_norte(ax, ext)
    alcas = [Patch(facecolor=fig1.COR_DIVERGENCIA, alpha=0.55, edgecolor=fig1.COR_DIVERGENCIA,
                   label=f"agrupamento {n}: ganhou domicílios\ne perdeu moradores ({len(a)} unidades)"),
             Patch(facecolor=COR_OUTRA_DIV, alpha=0.45, edgecolor="none",
                   label="outras unidades divergentes"),
             Patch(facecolor="none", edgecolor="#cfcec8", label="demais unidades com domicílio"),
             Line2D([], [], color=COR_RUA, lw=0.8, label="faces de logradouro 2010 (ruas)"),
             Patch(facecolor=COR_AU_DENSA, edgecolor="none", label="área urbanizada 2022, densa"),
             Patch(facecolor=COR_AU_POUCO, edgecolor="#d6d5d0", label="área urbanizada 2022,\npouco densa")]
    fig.legend(handles=alcas, loc="upper left",
               bbox_to_anchor=(ax.get_position().x1 + 0.012, ax.get_position().y1),
               fontsize=8.5, frameon=False, labelcolor=fig1.TINTA, title="legenda",
               title_fontsize=8.5, alignment="left")
    tabela = "\n".join(f"{row.n:>2}  {row.dom_10:>3}→{row.dom_22:<3}  {row.pop_10:>3}→{row.pop_22:<3}  "
                       f"{row.razao_10:.2f}→{row.razao_22:.2f}".replace(".", ",")
                       for row in a.itertuples())
    fig.text(ax.get_position().x1 + 0.012, ax.get_position().y0,
             " n   domicílios  moradores  razão\n" + tabela, fontsize=6.6, family="monospace",
             color=fig1.TINTA, va="bottom")
    for t in fig.texts:
        if t.get_text().startswith("Fonte:"):
            t.set_text(FONTE_TXT)
    destino = s1.SAIDAS / f"s2_detalhe_agrupamento_{n}.png"
    fig.savefig(destino, dpi=200, facecolor=fig1.SUPERFICIE)
    plt.close(fig)
    dados = metadados.montar(
        destino, tema="censo", fonte_id=FONTES, versao="s2-v1", crs=paths.crs_producao(),
        licenca="IBGE — uso livre com citação da fonte", autorizacao_fonte=True,
        pode_publicar=False, status_conferencia="pendente",
        observacoes=(f"Figura de detalhe do agrupamento {n} da divergência de sinal (A03, "
                     "subordinada 2), para a conferência visual do responsável. Fundo vetorial "
                     "(sem imagem de satélite no acervo). Script: "
                     "estudos/A03_expansao_adensamento/scripts/s2_agrupamentos.py."))
    metadados.escrever(destino, dados, sobrescrever=True)


if __name__ == "__main__":
    main()
