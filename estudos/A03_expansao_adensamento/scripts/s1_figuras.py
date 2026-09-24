"""
A03 — subordinada 1: figuras (mapas estáticos) a partir da camada de trabalho.

    saidas/s1_mapa_classes_{urbano,municipio}.png
    saidas/s1_mapa_var_domicilios_{urbano,municipio}.png
    saidas/s1_mapa_var_populacao_{urbano,municipio}.png
    saidas/s1_mapa_divergencia_urbano.png   (subordinada 2: ganham domicílio e
                                             perdem moradores)

CENÁRIO ADOTADO (desde 2026-09-23, resultados_s1.md § 11): as unidades do setor
rural de 2010 430160205000136 ficam À PARTE. Elas continuam desenhadas na cor da
sua classe, com HACHURA e contorno, e ficam fora das contagens da legenda. A
lista vem de derivados/s1_desagregacao_2010.json, conferida contra a camada por
s1_geografias.unidades_a_parte().

Cada uma com `.json` irmão (scripts/utils/metadados.py), pendente e não
publicável até a conferência do responsável.

Base: limite municipal (camada `limite_municipal`, conferida) e o contorno da
ÁREA URBANIZADA de 2022 do IBGE (Tipo = "Área urbanizada"). NÃO há perímetro
urbano legal no acervo; a legenda diz o que a linha é.

Cor: paleta.py (ponto único do estudo, validada com o validador de paleta do
skill de visualização). Eixo ganho–perda: azul = ganho, laranja = perda, cinza =
sem mudança — nas classes (nova azul escuro, adensada azul claro, estável cinza,
esvaziada laranja claro, extinta laranja escuro) e na variação (divergente em
classes discretas, zero em cinza neutro).

Mapas no CRS de produção (EPSG:31981, métrico): a barra de escala é em metros
reais e o norte é o da quadrícula UTM (convergência meridiana < 1° em Bagé).

LÊ saidas/s1_celulas_2010_2022.gpkg, derivados/s1_desagregacao_2010.json, o
acervo e data/raw/ (área urbanizada).
ESCREVE só saidas/s1_mapa_*.png (+ .json).
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

import s1_expansao_adensamento as s1  # noqa: E402
from paleta import (COR_CONTEXTO, COR_DIVERGENCIA, CORES_CLASSE, DIVERGENTE,  # noqa: E402
                    SUPERFICIE)
from s1_geografias import unidades_a_parte  # noqa: E402
from scripts.utils import catalogo, metadados, paths  # noqa: E402

TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
HACHURA = "////"
ROTULOS = {"nova": "nova", "adensada": "adensada", "estavel": "estável",
           "esvaziada": "esvaziada", "extinta": "extinta"}
FAIXAS = {
    "d_dom": [-1e9, -50.5, -20.5, -5.5, -0.5, 0.5, 5.5, 20.5, 50.5, 1e9],
    "d_pop": [-1e9, -150.5, -50.5, -10.5, -0.5, 0.5, 10.5, 50.5, 150.5, 1e9],
}
ROTULOS_FAIXA = {
    "d_dom": ["≤ −51", "−50 a −21", "−20 a −6", "−5 a −1", "0", "1 a 5", "6 a 20",
              "21 a 50", "≥ 51"],
    "d_pop": ["≤ −151", "−150 a −51", "−50 a −11", "−10 a −1", "0", "1 a 10", "11 a 50",
              "51 a 150", "≥ 151"],
}
FONTE = ("Fonte: IBGE — Grade Estatística 2010 e 2022; Áreas Urbanizadas do Brasil 2022; "
         "Malha Municipal 2025. Unidade: célula da grade harmonizada 2010 × 2022 "
         "(41 células de 1 km de 2010 subdivididas em 200 m em 2022 comparadas a 1 km).\n"
         "Elaboração: ACERVO_BAGE, estudo A03 (subordinada 1). SIRGAS 2000 / UTM 21S "
         "(EPSG:31981). Camada de trabalho não conferida no mapa. Números adotados: setor de "
         "2010 430160205000136 à parte (resultados_s1.md § 11).")


def carregar():
    a_parte, setor = unidades_a_parte()
    celulas = gpd.read_file(s1.CAMADA)
    celulas["a_parte"] = celulas["unidade"].isin(a_parte)
    celulas.attrs["setor_a_parte"] = setor
    _, arq_limite = catalogo.camada_conferida("limite_municipal")
    limite = gpd.read_file(arq_limite).to_crs(celulas.crs)
    area = paths.carregar_area_estudo()
    au = gpd.read_file(f"/vsizip/{s1.AU_ZIP}/{s1.AU_SHP}",
                       bbox=tuple(area.to_crs("EPSG:4674").total_bounds)).to_crs(celulas.crs)
    au = au[(au["Tipo"] == s1.TIPO_URBANIZADA) & au.intersects(limite.union_all())]
    return celulas, limite, au


def extensao(nome: str, limite, au):
    if nome == "municipio":
        x0, y0, x1, y1 = limite.total_bounds
        m = 2000
    else:
        x0, y0, x1, y1 = au.total_bounds
        m = 1500
    return x0 - m, y0 - m, x1 + m, y1 + m


def escala_e_norte(ax, ext):
    x0, y0, x1, y1 = ext
    largura = x1 - x0
    alvo = largura / 5
    passo = next(v for v in (500, 1000, 2000, 5000, 10000, 20000, 50000) if v >= alvo * 0.6)
    bx, by = x0 + largura * 0.04, y0 + (y1 - y0) * 0.05
    altura = (y1 - y0) * 0.008
    ax.add_patch(Rectangle((bx, by), passo / 2, altura, facecolor=TINTA, edgecolor=TINTA,
                           lw=0.6, zorder=7))
    ax.add_patch(Rectangle((bx + passo / 2, by), passo / 2, altura, facecolor="white",
                           edgecolor=TINTA, lw=0.6, zorder=7))
    rot = f"{passo / 1000:g} km" if passo >= 1000 else f"{passo} m"
    fundo = dict(facecolor=SUPERFICIE, edgecolor="none", pad=1.2, alpha=0.9)
    ax.text(bx, by + altura * 2.2, "0", fontsize=7, color=TINTA, ha="center", bbox=fundo,
            zorder=7)
    ax.text(bx + passo, by + altura * 2.2, rot, fontsize=7, color=TINTA, ha="center",
            bbox=fundo, zorder=7)
    nx, ny = x1 - largura * 0.05, y1 - (y1 - y0) * 0.12
    comp = (y1 - y0) * 0.06
    ax.annotate("", xy=(nx, ny + comp), xytext=(nx, ny),
                arrowprops=dict(arrowstyle="-|>", color=TINTA, lw=1.2, mutation_scale=12))
    ax.text(nx, ny + comp * 1.15, "N", ha="center", va="bottom", fontsize=9,
            color=TINTA, fontweight="bold")


def base(ax, limite, au, ext):
    ax.set_facecolor(SUPERFICIE)
    limite.boundary.plot(ax=ax, color=TINTA, linewidth=0.9, zorder=4)
    au.boundary.plot(ax=ax, color="#2c2c2a", linewidth=0.6, linestyle=(0, (3, 1.5)), zorder=5)
    ax.set_xlim(ext[0], ext[2])
    ax.set_ylim(ext[1], ext[3])
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#d6d5d0")
        s.set_linewidth(0.6)
    escala_e_norte(ax, ext)


def marcar_a_parte(ax, celulas):
    """Hachura e contorno nas unidades à parte, por cima da cor da classe."""
    ap = celulas[celulas["a_parte"]]
    if not len(ap):
        return
    ap.plot(ax=ax, facecolor="none", edgecolor=TINTA_2, hatch=HACHURA, linewidth=0, zorder=6)
    gpd.GeoSeries([ap.union_all()], crs=ap.crs).boundary.plot(ax=ax, color=TINTA, linewidth=0.9,
                                                              zorder=6)


def alca_a_parte(celulas):
    n = int(celulas["a_parte"].sum())
    return Patch(facecolor="none", edgecolor=TINTA_2, hatch=HACHURA,
                 label=f"à parte: setor de 2010\n{celulas.attrs['setor_a_parte']}\n"
                       f"({n} unidades; grade de 2010\ndesagregada ali). Fora das\n"
                       "contagens e dos números\nadotados (resultados_s1 § 11)")


def linhas_base():
    return [Line2D([], [], color=TINTA, lw=0.9, label="limite municipal"),
            Line2D([], [], color="#2c2c2a", lw=0.6, linestyle=(0, (3, 1.5)),
                   label="área urbanizada 2022 (IBGE)")]


def salvar(fig, nome: str, descricao: str) -> Path:
    destino = s1.SAIDAS / f"{nome}.png"
    fig.savefig(destino, dpi=200, facecolor=SUPERFICIE)
    plt.close(fig)
    dados = metadados.montar(
        destino, tema="censo",
        fonte_id=f"{s1.FONTES};ibge_areas_urbanizadas_2022;ibge_malhas_municipais",
        versao="s1-v2", crs=paths.crs_producao(),
        licenca="IBGE — uso livre com citação da fonte", autorizacao_fonte=True,
        pode_publicar=False, status_conferencia="pendente",
        observacoes=(f"{descricao} Cenário adotado: setor de 2010 430160205000136 à parte "
                     "(hachurado; fora das contagens). Figura do A03, gerada de "
                     "saidas/s1_celulas_2010_2022.gpkg por scripts/s1_figuras.py. Não "
                     "conferida: não publicar antes da conferência do responsável."))
    metadados.escrever(destino, dados, sobrescrever=True)
    return destino


def figura(titulo: str, subtitulo: str, ext):
    """Mapa à esquerda, legenda numa coluna à direita (fora do dado)."""
    largura_mapa = 8.6                                   # polegadas
    altura_mapa = largura_mapa * (ext[3] - ext[1]) / (ext[2] - ext[0])
    topo, rodape, coluna = 0.95, 0.75, 3.2               # polegadas
    w, h = largura_mapa + coluna + 0.4, altura_mapa + topo + rodape
    fig = plt.figure(figsize=(w, h))
    fig.patch.set_facecolor(SUPERFICIE)
    ax = fig.add_axes([0.2 / w, rodape / h, largura_mapa / w, altura_mapa / h])
    fig.text(0.2 / w, 1 - 0.15 / h, titulo, fontsize=12.5, color=TINTA, fontweight="bold",
             va="top")
    fig.text(0.2 / w, 1 - 0.5 / h, subtitulo, fontsize=9, color=TINTA_2, va="top")
    fig.text(0.2 / w, 0.08 / h, FONTE, fontsize=6.3, color=TINTA_2, va="bottom", wrap=True)
    return fig, ax


def legenda(fig, ax, alcas, titulo):
    fig.legend(handles=alcas + linhas_base(), loc="upper left",
               bbox_to_anchor=(ax.get_position().x1 + 0.012, ax.get_position().y1),
               fontsize=8.5, frameon=False, labelcolor=TINTA, title=titulo,
               title_fontsize=8.5, alignment="left")


def mapa_classes(celulas, limite, au, nome_ext):
    ext = extensao(nome_ext, limite, au)
    rot = "área urbana" if nome_ext == "urbano" else "município inteiro"
    fig, ax = figura(f"Bagé — classes de mudança de domicílios por célula, 2010 → 2022 ({rot})",
                     "Domicílios ocupados na grade estatística do IBGE; unidade harmonizada "
                     "entre as edições. Hachurado: setor de 2010 à parte.", ext)
    for classe in s1.CLASSES:
        sub = celulas[celulas["classe"] == classe]
        sub.plot(ax=ax, color=CORES_CLASSE[classe], edgecolor=SUPERFICIE, linewidth=0.25,
                 zorder=3)
    marcar_a_parte(ax, celulas)
    base(ax, limite, au, ext)
    n = celulas.loc[~celulas["a_parte"], "classe"].value_counts()
    alcas = [Patch(facecolor=CORES_CLASSE[c], edgecolor="none",
                   label=f"{ROTULOS[c]} ({n.get(c, 0)} unidades)") for c in s1.CLASSES]
    legenda(fig, ax, alcas + [alca_a_parte(celulas)],
            "classe (domicílios 2010 → 2022)\nnúmeros adotados")
    return salvar(fig, f"s1_mapa_classes_{nome_ext}",
                  f"Mapa das classes de mudança de domicílios ({rot}).")


def mapa_variacao(celulas, limite, au, nome_ext, coluna):
    ext = extensao(nome_ext, limite, au)
    rot = "área urbana" if nome_ext == "urbano" else "município inteiro"
    o_que = "domicílios ocupados" if coluna == "d_dom" else "moradores"
    fig, ax = figura(f"Bagé — variação de {o_que} por célula, 2010 → 2022 ({rot})",
                     f"Diferença absoluta ({o_que} em 2022 − em 2010) na grade estatística "
                     "do IBGE; unidade harmonizada entre as edições. Hachurado: setor de 2010 à "
                     "parte.", ext)
    cmap = ListedColormap(DIVERGENTE)
    norm = BoundaryNorm(FAIXAS[coluna], cmap.N)
    celulas.plot(ax=ax, column=coluna, cmap=cmap, norm=norm, edgecolor=SUPERFICIE,
                 linewidth=0.25, zorder=3)
    marcar_a_parte(ax, celulas)
    base(ax, limite, au, ext)
    adot = celulas.loc[~celulas["a_parte"], coluna]
    faixa = np.digitize(adot, FAIXAS[coluna][1:-1])
    n = np.bincount(faixa, minlength=len(DIVERGENTE))
    alcas = [Patch(facecolor=c, edgecolor="none", label=f"{r} ({n[i]})")
             for i, (c, r) in enumerate(zip(DIVERGENTE, ROTULOS_FAIXA[coluna]))][::-1]
    legenda(fig, ax, alcas + [alca_a_parte(celulas)],
            f"variação de {o_que}\n(nº de unidades, números adotados)")
    nome = "s1_mapa_var_domicilios" if coluna == "d_dom" else "s1_mapa_var_populacao"
    return salvar(fig, f"{nome}_{nome_ext}", f"Mapa da variação de {o_que} ({rot}).")


def mapa_divergencia(celulas, limite, au):
    """Subordinada 2: unidades que ganham domicílio e perdem moradores (recorte urbano)."""
    ext = extensao("urbano", limite, au)
    div = celulas[(celulas["d_dom"] > 0) & (celulas["d_pop"] < 0)]
    div_adot = div[~div["a_parte"]]
    c = div.geometry.centroid
    fora = div[~(c.x.between(ext[0], ext[2]) & c.y.between(ext[1], ext[3]))]
    def num(v) -> str:  # +1.234 / −2.095 (milhar com ponto, sinal de menos tipográfico)
        return f"{int(v):+,}".replace(",", ".").replace("-", "−")
    fig, ax = figura(
        "Bagé — unidades que ganharam domicílios e perderam moradores, 2010 → 2022",
        f"{len(div_adot)} unidades: {num(div_adot['d_dom'].sum())} domicílios e "
        f"{num(div_adot['d_pop'].sum())} moradores (subordinada 2). Área urbana; "
        f"{len(fora)} unidades rurais ficam fora deste recorte ({num(fora['d_dom'].sum())} "
        f"domicílios, {num(fora['d_pop'].sum())} moradores).", ext)
    outras = celulas[~celulas.index.isin(div.index)]
    outras.plot(ax=ax, color=COR_CONTEXTO, edgecolor=SUPERFICIE, linewidth=0.25, zorder=2)
    div.plot(ax=ax, color=COR_DIVERGENCIA, edgecolor=SUPERFICIE, linewidth=0.25, zorder=3)
    marcar_a_parte(ax, celulas)
    base(ax, limite, au, ext)
    alcas = [Patch(facecolor=COR_DIVERGENCIA, edgecolor="none",
                   label=f"ganhou domicílios e perdeu\nmoradores ({len(div_adot)} unidades)"),
             Patch(facecolor=COR_CONTEXTO, edgecolor="none",
                   label=f"outras unidades com domicílio\nem algum ano "
                         f"({int((~outras['a_parte']).sum())})")]
    legenda(fig, ax, alcas + [alca_a_parte(celulas)], "unidades (números adotados)")
    return salvar(fig, "s1_mapa_divergencia_urbano",
                  "Mapa das unidades que ganham domicílio e perdem moradores (subordinada 2, "
                  "área urbana).")


def main() -> None:
    celulas, limite, au = carregar()
    gerados = []
    for ext in ("urbano", "municipio"):
        gerados.append(mapa_classes(celulas, limite, au, ext))
        gerados.append(mapa_variacao(celulas, limite, au, ext, "d_dom"))
        gerados.append(mapa_variacao(celulas, limite, au, ext, "d_pop"))
    gerados.append(mapa_divergencia(celulas, limite, au))
    for g in gerados:
        print(paths.relativo(g))


if __name__ == "__main__":
    main()
