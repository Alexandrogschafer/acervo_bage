"""
A03 — subordinada 3: figuras do entorno de 2022 nas áreas de crescimento.

    saidas/s3_mapa_entorno_itens_urbano.png
        os 5 itens que discriminam (pavimentação, obstáculo na calçada, arborização
        5+, bueiro, rampa), % de domicílios por setor de 2022, com as NOVAS e as
        ADENSADAS sobrepostas em contorno
    saidas/s3_mapa_pavimentacao_urbano.png
        o item de maior dispersão (IQR 76,6) em tamanho de leitura
    saidas/s3_datacao_novas_200m.png
        item 3: novas de 200 m posteriores a 2001 × preenchimento de vazio interno
        no tecido de 1938–1960, nos 10 itens, com a cidade como referência;
        principal e sensibilidade (≥ 70 % num setor) lado a lado

Cor (paleta.py): coropleta em VIOLETA (magnitude; fora do eixo ganho–perda);
setor sem entorno em COR_CONTEXTO com hachura; áreas de crescimento em contorno de
tinta (novas de 200 m: traço cheio com halo claro; adensadas de 200 m: tracejado
fino), porque cor de classe por cima da coropleta confundiria as duas codificações
(o azul das novas some sobre o violeta escuro: ΔE 1,6 em deuteranopia). As unidades
de 1 km (campo, setores sem entorno) não são desenhadas. Os dois grupos do item 3 em PAR_NOVAS,
com forma diferente e rótulo de valor em cada marcador.

A figura do item 3 depende da datação do i02 (fonte não redistribuível): além de
pendente, ela é marcada com autorização da fonte = false. Nenhuma figura é
publicável antes da conferência do responsável.

LÊ derivados/s3_entorno.json e s3_unidades_setor.csv (de s3_entorno.py), a camada
de trabalho, a camada setores_2022 (conferida) e o que s1_figuras.carregar() lê.
ESCREVE só saidas/s3_*.png (+ .json).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patheffects  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

import s1_expansao_adensamento as s1  # noqa: E402
import s1_figuras as f1  # noqa: E402
import s3_entorno as s3  # noqa: E402
from paleta import COR_CONTEXTO, PAR_NOVAS, SUPERFICIE, VIOLETA  # noqa: E402
from scripts.utils import catalogo, metadados, paths  # noqa: E402

TINTA, TINTA_2 = f1.TINTA, f1.TINTA_2
# contorno das novas em tinta com halo claro: o azul da classe "nova" some sobre o
# violeta escuro (validate_palette.js: ΔE 1,6 deutan contra #5e3594)
FAIXAS = [0, 20, 40, 60, 80, 100.0001]
ROT_FAIXAS = ["0 a 20 %", "20 a 40 %", "40 a 60 %", "60 a 80 %", "80 a 100 %"]
MAPA_ITENS = [
    ("VIA PAVIMENTADA", "via pavimentada"),
    ("OBSTÁCULO NA CALÇADA", "obstáculo na calçada (mais é pior)"),
    ("ARBORIZAÇÃO", "arborização: 5 ou mais árvores"),
    ("BUEIRO", "bueiro"),
    ("RAMPA PARA CADEIRANTE", "rampa para cadeirante"),
]
ROTULO_ITEM = {
    "VIA PAVIMENTADA": "via pavimentada", "OBSTÁCULO NA CALÇADA": "obstáculo na calçada ↓",
    "ARBORIZAÇÃO": "arborização (5+ árvores)", "BUEIRO": "bueiro",
    "RAMPA PARA CADEIRANTE": "rampa para cadeirante", "PONTO DE ÔNIBUS": "ponto de ônibus",
    "CALÇADA": "calçada", "CIRCULAÇÃO DA VIA": "circulação: caminhão/ônibus",
    "ILUMINAÇÃO PÚBLICA": "iluminação pública (controle)",
    "VIA SINALIZADA PARA BICICLETA": "via para bicicleta (ausência)",
}
FONTE = ("Fonte: IBGE — Censo 2022, entorno dos domicílios por setor; malha de setores 2022; "
         "Grade Estatística 2010 e 2022; Áreas Urbanizadas 2022; Malha Municipal 2025.\n"
         "Elaboração: ACERVO_BAGE, estudo A03 (subordinada 3). SIRGAS 2000 / UTM 21S "
         "(EPSG:31981). Classes da grade harmonizada, cenário adotado (setor de 2010 "
         "430160205000136 à parte). Não conferida no mapa.")


def salvar(fig, nome: str, descricao: str, fontes: str, autoriza: bool) -> Path:
    destino = s1.SAIDAS / f"{nome}.png"
    fig.savefig(destino, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)
    dados = metadados.montar(
        destino, tema="censo", fonte_id=fontes, versao="s3-v1", crs=paths.crs_producao(),
        licenca="IBGE — uso livre com citação da fonte" + (
            "" if autoriza else "; agrupamento pela evolução urbana do IPHAN (não "
                                "redistribuível): só interpretação"),
        autorizacao_fonte=autoriza, pode_publicar=False, status_conferencia="pendente",
        observacoes=(f"{descricao} Figura do A03 (subordinada 3), gerada por "
                     "scripts/s3_figuras.py de derivados/s3_entorno.json. Não conferida: não "
                     "publicar antes da conferência do responsável."))
    metadados.escrever(destino, dados, sobrescrever=destino.with_suffix(".json").exists())
    return destino


def carregar():
    celulas, limite, au = f1.carregar()
    celulas = celulas[~celulas["a_parte"]]
    _, arq = catalogo.camada_conferida("setores_2022")
    setores = gpd.read_file(arq).to_crs(celulas.crs)
    entorno, municipio = s3.entorno_por_setor()
    setores = setores.join(entorno, on="CD_SETOR")
    return celulas, limite, au, setores, municipio


def coropleta(ax, setores, coluna, celulas, limite, au, ext):
    com = setores[setores[coluna].notna()]
    sem = setores[setores[coluna].isna()]
    sem.plot(ax=ax, facecolor=COR_CONTEXTO, edgecolor=SUPERFICIE, hatch="....",
             linewidth=0.3, zorder=2)
    classe = np.digitize(com[coluna].to_numpy(), FAIXAS[1:-1])
    for k, cor in enumerate(VIOLETA):
        com[classe == k].plot(ax=ax, color=cor, edgecolor=SUPERFICIE, linewidth=0.35,
                              zorder=2)
    urbanas = celulas[celulas["resolucao"] == "200 m"]
    aden = urbanas[urbanas["classe"] == "adensada"]
    gpd.GeoSeries([aden.union_all()], crs=aden.crs).boundary.plot(
        ax=ax, color=TINTA_2, linewidth=0.5, linestyle=(0, (2, 1.2)), zorder=6)
    novas = urbanas[urbanas["classe"] == "nova"]
    contorno = gpd.GeoSeries([novas.union_all()], crs=novas.crs).boundary
    contorno.plot(ax=ax, color=SUPERFICIE, linewidth=2.6, zorder=6)     # halo claro
    contorno.plot(ax=ax, color=TINTA, linewidth=1.1, zorder=6)
    f1.base(ax, limite, au, ext)


def alcas_coropleta(celulas):
    n = celulas[celulas["resolucao"] == "200 m"]["classe"].value_counts()
    return ([Patch(facecolor=c, edgecolor="none", label=r) for c, r in zip(VIOLETA, ROT_FAIXAS)]
            + [Patch(facecolor=COR_CONTEXTO, edgecolor="#b9b8b2", hatch="....",
                     label="setor sem entorno\n(31 dos 199)"),
               Line2D([], [], color=TINTA, lw=1.1,
                      path_effects=[patheffects.Stroke(linewidth=2.6, foreground=SUPERFICIE),
                                    patheffects.Normal()],
                      label=f"contorno das novas de 200 m\n({n.get('nova', 0)} unidades)"),
               Line2D([], [], color=TINTA_2, lw=0.5, linestyle=(0, (2, 1.2)),
                      label=f"contorno das adensadas de 200 m\n({n.get('adensada', 0)} unidades)")])


def mapa_itens(celulas, limite, au, setores, municipio) -> Path:
    ext = f1.extensao("urbano", limite, au)
    razao = (ext[3] - ext[1]) / (ext[2] - ext[0])
    lm = 4.1
    w = 3 * lm + 0.6
    h = 2 * lm * razao + 1.6
    fig = plt.figure(figsize=(w, h))
    fig.patch.set_facecolor(SUPERFICIE)
    fig.text(0.2 / w, 1 - 0.15 / h, "Bagé — entorno dos domicílios por setor (Censo 2022) e "
             "as áreas de crescimento 2010 → 2022", fontsize=12.5, color=TINTA,
             fontweight="bold", va="top")
    fig.text(0.2 / w, 1 - 0.5 / h, "% de domicílios em face com o item, por setor de 2022. "
             "Contornos: células novas e adensadas de 200 m (a grade urbana).",
             fontsize=9, color=TINTA_2, va="top")
    fig.text(0.2 / w, 0.08 / h, FONTE, fontsize=6.3, color=TINTA_2, va="bottom")
    alt = lm * razao
    for i, (coluna, rotulo) in enumerate(MAPA_ITENS):
        lin, col = divmod(i, 3)
        ax = fig.add_axes([(0.2 + col * lm) / w, (0.75 + (1 - lin) * alt) / h,
                           (lm - 0.1) / w, (alt - 0.3) / h])
        coropleta(ax, setores, coluna, celulas, limite, au, ext)
        ax.set_title(f"{rotulo} — cidade {municipio[coluna]:.1f} %".replace(".", ","),
                     fontsize=9, color=TINTA, loc="left")
    ax_leg = fig.add_axes([(0.2 + 2 * lm) / w, 0.75 / h, (lm - 0.1) / w, (alt - 0.3) / h])
    ax_leg.axis("off")
    ax_leg.legend(handles=alcas_coropleta(celulas) + f1.linhas_base(), loc="upper left",
                  fontsize=8.5, frameon=False, labelcolor=TINTA, alignment="left",
                  title="% de domicílios com o item\n(por setor de 2022)", title_fontsize=8.5)
    return salvar(fig, "s3_mapa_entorno_itens_urbano",
                  "Mapa em painéis dos 5 itens do entorno que discriminam, por setor, com as "
                  "novas e as adensadas em contorno.",
                  "ibge_censo2022_entorno_setores;ibge_malha_setores_2022;"
                  f"{s1.FONTES};ibge_areas_urbanizadas_2022;ibge_malhas_municipais", True)


def mapa_pavimentacao(celulas, limite, au, setores, municipio) -> Path:
    ext = f1.extensao("urbano", limite, au)
    fig, ax = f1.figura("Bagé — via pavimentada no entorno dos domicílios (Censo 2022) e as "
                        "áreas de crescimento",
                        f"% de domicílios em face pavimentada, por setor de 2022 (cidade "
                        f"{municipio['VIA PAVIMENTADA']:.1f} %; IQR entre setores 76,6 "
                        "pontos)".replace(".", ","), ext)
    fig.texts[-1].set_text(FONTE)
    coropleta(ax, setores, "VIA PAVIMENTADA", celulas, limite, au, ext)
    f1.legenda(fig, ax, alcas_coropleta(celulas), "% de domicílios em face\npavimentada")
    return salvar(fig, "s3_mapa_pavimentacao_urbano",
                  "Mapa da via pavimentada por setor, com as novas e as adensadas em contorno.",
                  "ibge_censo2022_entorno_setores;ibge_malha_setores_2022;"
                  f"{s1.FONTES};ibge_areas_urbanizadas_2022;ibge_malhas_municipais", True)


def painel_datacao(ax, bloco, cidade, titulo):
    x = bloco["datacao_novas_200m"]
    itens = list(ROTULO_ITEM)
    y = np.arange(len(itens))[::-1]
    ax.set_facecolor(SUPERFICIE)
    for yy in y:
        ax.axhline(yy, color="#ecebe6", lw=0.6, zorder=0)
    ax.scatter([cidade[i] for i in itens], y, marker="|", s=160, color=TINTA, lw=1.6,
               zorder=3, label="cidade (município)")
    estilos = {"posterior_a_2001": ("o", 0.17), "vazio_interno_1938_1960": ("s", -0.17)}
    for g, (marca, dy) in estilos.items():
        v = [x[g]["itens"][i]["pct"] for i in itens]
        ax.scatter(v, y + dy, marker=marca, s=46, color=PAR_NOVAS[g], edgecolor=SUPERFICIE,
                   lw=1.0, zorder=4)
        for vv, yy in zip(v, y + dy):
            ax.text(vv + 1.8, yy, f"{vv:.0f}", fontsize=6.8, color=TINTA_2, va="center",
                    zorder=5, bbox=dict(facecolor=SUPERFICIE, edgecolor="none", pad=0.4))
    ax.set_yticks(y)
    ax.set_yticklabels([ROTULO_ITEM[i] for i in itens], fontsize=8.5, color=TINTA)
    ax.set_xlim(-2, 108)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100 %"], fontsize=8, color=TINTA_2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#d6d5d0")
    ax.tick_params(axis="y", length=0)
    a, b = x["posterior_a_2001"], x["vazio_interno_1938_1960"]
    ax.set_title(f"{titulo}\nposteriores a 2001: {a['unidades_com_entorno']} unidades, "
                 f"{a['dom_22']} dom., {a['setores_distintos']} setores (3 maiores: "
                 f"{a['peso_nos_3_maiores_setores_pct']:.0f} % do peso)\n"
                 f"vazio interno 1938–1960: {b['unidades_com_entorno']} unidades, "
                 f"{b['dom_22']} dom., {b['setores_distintos']} setores (3 maiores: "
                 f"{b['peso_nos_3_maiores_setores_pct']:.0f} % do peso)",
                 fontsize=8.3, color=TINTA, loc="left")


def figura_datacao() -> Path:
    d = json.loads(s3.SAIDA.read_text(encoding="utf-8"))
    cidade = d["principal"]["referencia_cidade_pct"]
    sens = next(k for k in d if k.startswith("sensibilidade"))
    fig, axs = plt.subplots(1, 2, figsize=(13.2, 6.6), sharey=True)
    fig.patch.set_facecolor(SUPERFICIE)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.76, bottom=0.17, wspace=0.08)
    painel_datacao(axs[0], d["principal"], cidade, "Principal (todas as unidades)")
    painel_datacao(axs[1], d[sens], cidade, "Sensibilidade: só unidades com ≥ 70 % da área "
                                            "num único setor")
    fig.text(0.012, 0.975, "Bagé — entorno de 2022 nas novas urbanas de 200 m, pela datação "
             "da ocupação", fontsize=12.5, color=TINTA, fontweight="bold", va="top")
    fig.text(0.012, 0.925, "% de domicílios com o item, ponderado pelos domicílios de 2022. "
             "Interpretação: a datação vem de fonte não redistribuível (evolução urbana do "
             "IPHAN).", fontsize=9, color=TINTA_2, va="top")
    alcas = [Line2D([], [], marker="o", ls="", color=PAR_NOVAS["posterior_a_2001"],
                    markersize=7, label="ocupação posterior a 2001 (fora do traçado de 2001)"),
             Line2D([], [], marker="s", ls="", color=PAR_NOVAS["vazio_interno_1938_1960"],
                    markersize=7, label="preenchimento de vazio interno (tecido de 1938–1960)"),
             Line2D([], [], marker="|", ls="", color=TINTA, markersize=11, mew=1.6,
                    label="cidade (município inteiro)")]
    fig.legend(handles=alcas, loc="upper left", bbox_to_anchor=(0.012, 0.9), ncol=3,
               fontsize=8.5, frameon=False, labelcolor=TINTA)
    fig.text(0.012, 0.02, "Fonte: IBGE — Censo 2022 (entorno por setor), Grade Estatística "
             "2010 e 2022, malha de setores 2022; datação: REVIA_BG sobre a prancha 03/18 do "
             "dossiê de tombamento do IPHAN (2009). Cada valor é o de um setor: os grupos têm "
             "poucos setores e as diferenças não se\nmantêm entre as duas colunas. ↓ = mais é "
             "pior. Elaboração: ACERVO_BAGE, A03 (subordinada 3). Não conferida; não publicar.",
             fontsize=6.4, color=TINTA_2, va="bottom")
    return salvar(fig, "s3_datacao_novas_200m",
                  "Item 3: novas de 200 m posteriores a 2001 × vazio interno do tecido de "
                  "1938–1960, nos 10 itens do entorno; principal e sensibilidade.",
                  "ibge_censo2022_entorno_setores;ibge_malha_setores_2022;"
                  f"{s1.FONTES};revia_bg_evolucao_urbana", False)


def main() -> None:
    celulas, limite, au, setores, municipio = carregar()
    feitos = [mapa_itens(celulas, limite, au, setores, municipio),
              mapa_pavimentacao(celulas, limite, au, setores, municipio),
              figura_datacao()]
    for f in feitos:
        print("gravado:", paths.relativo(f))


if __name__ == "__main__":
    main()
