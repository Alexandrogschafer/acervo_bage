"""
A03 — interpretação: em que período de ocupação caem as unidades já analisadas.

    subordinada 2: os dois maiores agrupamentos da divergência de sinal (21 e 18)
    subordinada 1: as 354 novas (por resolução) e as 56 extintas urbanas (por
                   fenômeno), com o agrupamento 053/054

CAMADA DE INTERPRETAÇÃO, NÃO DE PRODUÇÃO — ORIGEM NÃO REDISTRIBUÍVEL
--------------------------------------------------------------------
data/externos/revia_bg/evolucao_urbana/ é cópia (REVIA_BG, evolucao_urbana_evo_v1)
dos polígonos convertidos da prancha 03/18 "Condicionantes – Evolução Urbana" do
dossiê de tombamento do IPHAN (SICG, 2009), sem licença registrada: "não
redistribuir os polígonos" (pode_publicar=false). Serve para DATAR e interpretar no
texto; nenhuma camada nem figura sai dela. Por isso NÃO está no manifesto, como
bairros_loteamentos (i01). O sha256_conteudo de cada shapefile é conferido contra o
.json irmão antes de ler. ferrovia.shp (sem .prj) não é lida.

INCREMENTOS
-----------
Os polígonos são cumulativos até 1960 (1825 ⊂ 1850 ⊂ 1900 ⊂ 1938; 1960 cobre 74,5 %
de 1938) e os dois últimos são manchas destacadas. Critério do REVIA_BG, uniforme: o
INCREMENTO de cada período é o polígono dele menos a união de todos os anteriores,
em ordem cronológica. Os incrementos são disjuntos e cobrem a união dos sete.
Acampamento (1811) e charqueadas não são períodos e não entram.

ATRIBUIÇÃO: cada unidade vai para o incremento com a MAIOR ÁREA DE INTERSEÇÃO; a
parte da unidade fora de todos os incrementos concorre como FORA ("fora do traçado
urbano mapeado até 2001"). Empate: o período mais antigo. Operações no CRS de
produção; áreas medidas no CRS de área (scripts/utils/medidas.py).

BORDA SEM DATA FIRME (decisão do responsável, 2026-09-24): o polígono de 1938 é
generalizado e tem 551,9 ha que o de 1960 não cobre. A unidade atribuída a 1938 com
metade ou mais da própria área nessa parte vai para "borda sem data firme", separada
das datações firmes; o período pela maior área fica na lista por unidade.

FORA não é sinônimo de "ocupação urbana posterior a 2001" para toda unidade: o mapa
desenha o traçado URBANO. Para células de 200 m na borda da cidade, fora = não
ocupada no traçado de 2001; para células de 1 km no campo, fora = rural, não
urbana, em 2001 — a leitura fica separada por resolução.

ESCREVE:
    derivados/i02_evolucao_urbana.json          agregados por grupo (versionado)
    derivados/i02_evolucao_urbana_unidades.csv  lista por unidade (fora do git)
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
import shapely  # noqa: E402

import i01_bairros_loteamentos as i01  # noqa: E402
import s1_expansao_adensamento as s1  # noqa: E402
import s1_extintas as ex  # noqa: E402
from scripts.utils import medidas, metadados, paths  # noqa: E402

EVO = paths.caminho("externos", "revia_bg", "evolucao_urbana")
SAIDA = s1.DERIV / "i02_evolucao_urbana.json"
LISTA = s1.DERIV / "i02_evolucao_urbana_unidades.csv"
FORA = "fora do traçado mapeado até 2001"
# ordem cronológica; rótulos da legenda do mapa (forma abreviada do REVIA_BG)
PERIODOS = {
    "urbano_1825": "déc. 1820 (primeiro loteamento)",
    "urbano_1850": "metade do séc. XIX",
    "urbano_1900": "início do séc. XX",
    "urbano_1938": "1938",
    "urbano_1960": "1960",
    "urbano_1961_1970": "1970",
    "urbano_1970_2001": "2001",
}
BORDA = "borda sem data firme"
ORDEM = [*PERIODOS.values(), BORDA, FORA]
GENERALIZADO_1938 = (
    "o polígono de 1938 é o traçado daquele ano em REPRESENTAÇÃO GENERALIZADA (REVIA_BG, "
    "ESTADO.md, _evo_v2): datar por ele significa 'até 1938, no máximo'. Ele tem área que o de "
    "1960 não cobre. DECISÃO DO RESPONSÁVEL (2026-09-24): a unidade atribuída a 1938 com metade "
    "ou mais da própria área nessa parte vai para 'borda sem data firme', não para '1938'")
ORIGEM = ("data/externos/revia_bg/evolucao_urbana/: cópia do REVIA_BG (evolucao_urbana_evo_v1) "
          "dos polígonos da prancha 03/18 do dossiê de tombamento do IPHAN (SICG, 2009), SEM "
          "licença de redistribuição — serve para DATAR e interpretar no texto, não para publicar "
          "camada nem mapa")


def incrementos() -> tuple[gpd.GeoDataFrame, list[dict], object]:
    """Incremento disjunto de cada período (polígono menos a união dos anteriores), e a
    parte do polígono de 1938 que o de 1960 não cobre (ver GENERALIZADO_1938)."""
    crs = paths.crs_producao()
    linhas, tabela, acumulado, poligonos = [], [], None, {}
    for base, rotulo in PERIODOS.items():
        g = i01.conferido(EVO / f"{base}.shp").to_crs(crs)
        poligono = shapely.make_valid(g.geometry.union_all())
        poligonos[base] = poligono
        inc = poligono if acumulado is None else shapely.make_valid(poligono.difference(acumulado))
        acumulado = poligono if acumulado is None else shapely.make_valid(acumulado.union(poligono))
        linhas.append({"periodo": rotulo, "ordem": len(linhas), "geometry": inc})
        tabela.append({"periodo": rotulo,
                       "ha_poligono": round(medidas.area_m2(poligono) / 1e4, 1),
                       "ha_incremento": round(medidas.area_m2(inc) / 1e4, 1)})
    so_1938 = shapely.make_valid(poligonos["urbano_1938"].difference(poligonos["urbano_1960"]))
    return gpd.GeoDataFrame(linhas, crs=crs), tabela, so_1938


def atribuir(u: gpd.GeoDataFrame, inc: gpd.GeoDataFrame, so_1938) -> pd.DataFrame:
    """Incremento de maior área de interseção por unidade (ou FORA), com as frações."""
    u = u[["unidade", "geometry"]].reset_index(drop=True).to_crs(paths.crs_producao())
    area_u = medidas.areas_m2(u).set_axis(u["unidade"])
    pedacos = gpd.overlay(u, inc, how="intersection", keep_geom_type=True)
    pedacos["m2"] = medidas.areas_m2(pedacos).values
    pedacos = pedacos.groupby(["unidade", "periodo", "ordem"], as_index=False)["m2"].sum()
    coberta = pedacos.groupby("unidade")["m2"].sum().reindex(area_u.index, fill_value=0.0)
    fora = pd.DataFrame({"unidade": area_u.index, "periodo": FORA, "ordem": len(PERIODOS),
                         "m2": (area_u - coberta).clip(lower=0).values})
    todos = pd.concat([pedacos, fora], ignore_index=True)
    todos["frac"] = todos["m2"] / todos["unidade"].map(area_u)
    maior = (todos.sort_values(["unidade", "m2", "ordem"], ascending=[True, False, True])
             .drop_duplicates("unidade").set_index("unidade"))
    frac_so_1938 = (medidas.areas_m2(gpd.GeoDataFrame(
        geometry=u.geometry.intersection(so_1938), crs=u.crs)).set_axis(u["unidade"]) / area_u)
    # decisão do responsável, 2026-09-24: 1938 só onde o de 1960 confirma o traçado
    borda = (maior["periodo"] == PERIODOS["urbano_1938"]) & (frac_so_1938.reindex(maior.index) >= 0.5)
    return pd.DataFrame({
        "periodo": maior["periodo"].where(~borda, BORDA),
        "periodo_pela_maior_area": maior["periodo"],
        "frac_do_maior": maior["frac"].round(3),
        "frac_coberta": (coberta / area_u).round(3),
        "periodos_tocados": pedacos.groupby("unidade").size().reindex(area_u.index, fill_value=0),
        "frac_1938_sem_1960": frac_so_1938.round(3),
    })


def resumo(g: pd.DataFrame, peso: str) -> dict:
    n, total = len(g), g[peso].sum()
    por = []
    for periodo in ORDEM:
        x = g[g["periodo"] == periodo]
        if len(x):
            por.append({"periodo": periodo, "unidades": int(len(x)),
                        "pct_unidades": round(100 * len(x) / n, 1), peso: int(x[peso].sum()),
                        f"pct_{peso}": round(100 * x[peso].sum() / total, 1) if total else 0.0})
    return {
        "unidades": int(n), peso: int(total), "por_periodo": por,
        "inteiramente_fora_de_todos_os_poligonos": {
            "unidades": int((g["frac_coberta"] == 0).sum()),
            peso: int(g.loc[g["frac_coberta"] == 0, peso].sum())},
        "unidades_que_tocam_mais_de_um_periodo": int((g["periodos_tocados"] > 1).sum()),
        "unidades_atribuidas_com_menos_de_metade_da_area": int((g["frac_do_maior"] < 0.5).sum()),
    }


def main() -> None:
    inc, tabela_inc, so_1938 = incrementos()
    camada = ex.ler_camada()
    v = camada[~camada[s1.CAMPO_A_PARTE]].set_index("unidade", drop=False)
    lista = []

    ag = i01.conferido(i01.AGRUP)
    at = atribuir(ag, inc, so_1938).join(ag.set_index("unidade")[["agrupamento", "dom_10"]])
    agrupamentos = {str(k): resumo(x, "dom_10") for k, x in at.groupby("agrupamento")}
    lista.append(at.assign(grupo="s2_agrupamento_" + at["agrupamento"].astype(str)))

    novas = v[v["classe"] == "nova"]
    at_n = atribuir(novas, inc, so_1938).join(novas[["dom_22", "resolucao"]])
    novas_out = {"todas": resumo(at_n, "dom_22"),
                 **{f"resolucao_{r}": resumo(x, "dom_22") for r, x in at_n.groupby("resolucao")}}
    lista.append(at_n.assign(grupo="s1_nova_" + at_n["resolucao"].astype(str)))

    faces = json.loads(i01.FACES.read_text(encoding="utf-8"))
    fen = faces["extintas_urbanas_por_fenomeno"]
    fenomeno = {u: i01.FENOMENOS[k] for k in i01.FENOMENOS for u in fen[k]["unidades_lista"]}
    agrup_053 = set(faces["agrupamento_053_054"]["unidades"])
    ext = v.loc[list(fenomeno)]
    at_e = atribuir(ext, inc, so_1938).join(ext[["dom_10"]])
    at_e["fenomeno"] = at_e.index.map(fenomeno)
    extintas = {"todas": resumo(at_e, "dom_10"),
                **{f: resumo(x, "dom_10") for f, x in at_e.groupby("fenomeno")},
                "agrupamento_053_054": resumo(at_e[at_e.index.isin(agrup_053)], "dom_10")}
    lista.append(at_e.assign(grupo="s1_extinta: " + at_e["fenomeno"]))

    resultado = {
        "objeto": "interpretação: período de ocupação (evolução urbana do IPHAN) das unidades dos "
                  "resultados_s1 e s2 (cenário adotado, setor 136 à parte)",
        "origem": ORIGEM,
        "evolucao_urbana": {
            "pasta": paths.relativo(EVO), "no_manifesto": False,
            "sha256_conteudo": {b: metadados.ler(EVO / f"{b}.shp")["sha256_conteudo"]
                                for b in PERIODOS},
            "incrementos": tabela_inc,
            "ha_do_poligono_1938_fora_do_de_1960": round(medidas.area_m2(so_1938) / 1e4, 1),
            "generalizacao_1938": GENERALIZADO_1938,
            "nao_usados": "urbano_acampamentos e charqueadas_evolucao (não são períodos); "
                          "ferrovia (sem .prj)",
        },
        "camada_sha256_conteudo": metadados.ler(s1.CAMADA)["sha256_conteudo"],
        "agrupamentos_sha256_conteudo": metadados.ler(i01.AGRUP)["sha256_conteudo"],
        "criterio": "incremento de cada período = polígono menos a união dos anteriores (critério "
                    "do REVIA_BG); cada unidade vai para o incremento de maior área de interseção; "
                    f"a parte fora de todos concorre como '{FORA}'; empate: o período mais antigo; "
                    f"atribuída a 1938 com metade ou mais da área na parte do polígono de 1938 que o "
                    f"de 1960 não cobre -> '{BORDA}' (decisão do responsável, 2026-09-24)",
        "leitura_do_fora": "células de 200 m: não ocupadas no traçado urbano de 2001; células de "
                           "1 km: rurais em 2001 — o mapa desenha só o traçado urbano",
        "figuras": "não mudam: o período entra como texto, não como camada",
        "s2_agrupamentos_divergencia": agrupamentos,
        "s1_novas": novas_out,
        "s1_extintas_urbanas": extintas,
        "lista_por_unidade": f"{paths.relativo(LISTA)} (fora do git)",
        "crs_operacao": paths.crs_producao(),
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    colunas = ["grupo", "periodo", "periodo_pela_maior_area", "frac_do_maior", "frac_coberta", "periodos_tocados",
               "frac_1938_sem_1960",
               "dom_10", "dom_22"]
    pd.concat(lista).rename_axis("unidade").reindex(columns=colunas).to_csv(LISTA, encoding="utf-8")
    print(f"gravado: {paths.relativo(SAIDA)} e {paths.relativo(LISTA)}")


if __name__ == "__main__":
    main()
