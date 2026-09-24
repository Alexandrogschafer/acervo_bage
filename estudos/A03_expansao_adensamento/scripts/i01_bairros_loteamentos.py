"""
A03 — interpretação: em que bairro ou loteamento caem as unidades já analisadas.

    subordinada 2: os dois maiores agrupamentos da divergência de sinal (21 e 18)
    subordinada 1: as 354 novas e as 56 extintas urbanas (por fenômeno), com o
                   agrupamento 053/054

CAMADA DE INTERPRETAÇÃO, NÃO DE PRODUÇÃO
----------------------------------------
data/externos/bairros_loteamentos_bage/bairros_loteamentos_bage.gpkg é material
REVISADO pelo responsável a partir do geobage (Prefeitura de Bagé), SEM
autorização de republicação (pode_publicar=false). Serve para NOMEAR e interpretar
no texto; nenhuma camada nem figura sai dela. Por isso NÃO está no manifesto: se
estivesse, a regra do mais restritivo tornaria o estudo inteiro não publicável.
O sha256_conteudo do arquivo é conferido contra o .json irmão antes de ler.

A camada é UM mosaico de 114 polígonos (bairros, vilas e loteamentos lado a lado,
sem hierarquia, sem campo de tipo e sem data de aprovação). O "tipo" abaixo é só o
que o NOME declara (prefixo LOTEAMENTO / BAIRRO / VILA); o resto fica "sem tipo no
nome". Não há "loteamento dentro de bairro" a contar.

ATRIBUIÇÃO: cada unidade vai para o polígono com a MAIOR ÁREA DE INTERSEÇÃO; a
parte da unidade fora de todos os polígonos concorre como "fora da camada". Empate
de área não ocorre na prática; se ocorrer, vence o de menor id. Operações no CRS de
produção; áreas medidas no CRS de área (scripts/utils/medidas.py).

ESCREVE:
    derivados/i01_bairros_loteamentos.json          agregados por grupo (versionado)
    derivados/i01_bairros_loteamentos_unidades.csv  lista por unidade (fora do git)

A lista que liga cada unidade a um nome de bairro ou loteamento NÃO vai no JSON
versionado: é derivada de material sem autorização de republicação (formato do i02,
padronizado em 2026-09-24). Até o commit d312258 ela estava no JSON.
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

import s1_expansao_adensamento as s1  # noqa: E402
import s1_extintas as ex  # noqa: E402
import s2_divergencia as s2  # noqa: E402
from scripts.utils import medidas, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

BAIRROS = paths.caminho("externos", "bairros_loteamentos_bage", "bairros_loteamentos_bage.gpkg")
AGRUP = s1.SAIDAS / "s2_agrupamentos_divergencia.gpkg"
FACES = s1.DERIV / "s1_faces_2010.json"
SAIDA = s1.DERIV / "i01_bairros_loteamentos.json"
LISTA = s1.DERIV / "i01_bairros_loteamentos_unidades.csv"
FORA = "(fora da camada)"
ORIGEM = ("bairros_loteamentos_bage.gpkg: material revisado pelo responsável a partir do "
          "geobage (Prefeitura de Bagé), sem autorização de republicação — serve para nomear e "
          "interpretar no texto, não para publicar camada nem mapa")
PROXIMO_ATE_M = 500
FENOMENOS = {
    "esvaziamento_medido_face_perdeu_os_enderecos": "esvaziamento medido",
    "deslocamento_por_reparticao": "indício de deslocamento por repartição da face",
    "outros": "outras",
}


def conferido(arquivo: Path) -> gpd.GeoDataFrame:
    if sha256_conteudo(arquivo) != metadados.ler(arquivo)["sha256_conteudo"]:
        raise SystemExit(f"PARADO — {paths.relativo(arquivo)} mudou desde o .json irmão")
    return gpd.read_file(arquivo)


def tipo_pelo_nome(nome: str) -> str:
    for prefixo, tipo in (("LOTEAMENTO", "loteamento"), ("BAIRRO", "bairro"), ("VILA", "vila")):
        if nome.startswith(prefixo):
            return tipo
    return "sem tipo no nome"


def atribuir(u: gpd.GeoDataFrame, b: gpd.GeoDataFrame) -> pd.DataFrame:
    """Polígono de maior área de interseção por unidade (ou FORA), com as frações."""
    u = u[["unidade", "geometry"]].reset_index(drop=True).to_crs(paths.crs_producao())
    area_u = medidas.areas_m2(u).set_axis(u["unidade"])
    pedacos = gpd.overlay(u, b[["id", "nome", "geometry"]], how="intersection", keep_geom_type=True)
    pedacos["m2"] = medidas.areas_m2(pedacos).values
    pedacos = pedacos.groupby(["unidade", "id", "nome"], as_index=False)["m2"].sum()
    coberta = pedacos.groupby("unidade")["m2"].sum().reindex(area_u.index, fill_value=0.0)
    fora = pd.DataFrame({"unidade": area_u.index, "id": -1, "nome": FORA,
                         "m2": (area_u - coberta).clip(lower=0).values})
    todos = pd.concat([pedacos, fora], ignore_index=True)
    todos["frac"] = todos["m2"] / todos["unidade"].map(area_u)
    maior = (todos.sort_values(["unidade", "m2", "id"], ascending=[True, False, True])
             .drop_duplicates("unidade").set_index("unidade"))
    prox = gpd.sjoin_nearest(u, b[["nome", "geometry"]], how="left", distance_col="dist_m")
    prox = prox.sort_values("dist_m").drop_duplicates("unidade").set_index("unidade")
    au, _ = s2.ler_area_urbanizada(u.crs)
    return pd.DataFrame({
        "nome": maior["nome"], "frac_do_maior": maior["frac"].round(3),
        "mais_proximo": prox["nome"].reindex(area_u.index),
        "dist_mais_proximo_m": prox["dist_m"].reindex(area_u.index).round(0),
        "toca_area_urbanizada": u.set_index("unidade").intersects(au).reindex(area_u.index),
        "frac_coberta": (coberta / area_u).round(3),
        "polígonos_tocados": pedacos.groupby("unidade").size().reindex(area_u.index, fill_value=0),
    })


def tabela(g: pd.DataFrame, peso: str | None) -> list[dict]:
    n = len(g)
    linhas = []
    for nome, x in g.groupby("nome"):
        linha = {"nome": nome, "tipo_pelo_nome": "—" if nome == FORA else tipo_pelo_nome(nome),
                 "unidades": int(len(x)), "pct_unidades": round(100 * len(x) / n, 1)}
        if peso:
            linha[peso] = int(x[peso].sum())
            linha[f"pct_{peso}"] = round(100 * x[peso].sum() / g[peso].sum(), 1) if g[peso].sum() else 0.0
        linhas.append(linha)
    chave = peso or "unidades"
    return sorted(linhas, key=lambda r: (-r[chave], -r["unidades"], r["nome"]))


def fora_da_camada(g: pd.DataFrame, peso: str | None) -> dict:
    """As atribuídas a FORA: onde estão e qual o polígono mais próximo (só para nomear a
    vizinhança, NÃO é atribuição)."""
    f = g[g["nome"] == FORA]
    faixas = pd.cut(f["dist_mais_proximo_m"], [-1, 0, 200, PROXIMO_ATE_M, 1000, float("inf")],
                    labels=["toca um polígono", "até 200 m", f"200 a {PROXIMO_ATE_M} m",
                            f"{PROXIMO_ATE_M} m a 1 km", "mais de 1 km"])
    perto = f[f["dist_mais_proximo_m"] <= PROXIMO_ATE_M]
    viz = []
    for nome, x in perto.groupby("mais_proximo"):
        viz.append({"mais_proximo": nome, "unidades": int(len(x)),
                    **({peso: int(x[peso].sum())} if peso else {})})
    return {
        "unidades": int(len(f)), **({peso: int(f[peso].sum())} if peso else {}),
        "tocam_area_urbanizada_2022": int(f["toca_area_urbanizada"].sum()),
        "por_distancia_ao_poligono_mais_proximo": {
            str(k): int(n) for k, n in faixas.value_counts(sort=False).items()},
        f"poligono_mais_proximo_ate_{PROXIMO_ATE_M}_m": sorted(
            viz, key=lambda r: (-r.get(peso or "unidades", 0), -r["unidades"], r["mais_proximo"])),
    }


def cobertura(b: gpd.GeoDataFrame) -> dict:
    """Quanto da área urbanizada de 2022 do IBGE a camada cobre."""
    au, densa = s2.ler_area_urbanizada(b.crs)
    uniao = b.union_all()
    out = {}
    for nome, geo in (("area_urbanizada_2022", au), ("area_urbanizada_2022_densa", densa)):
        total = medidas.area_m2(geo)
        dentro = medidas.area_m2(geo.intersection(uniao))
        out[nome] = {"km2": round(total / 1e6, 2), "km2_coberta_pela_camada": round(dentro / 1e6, 2),
                     "pct_coberta": round(100 * dentro / total, 1)}
    out["camada_km2"] = round(medidas.area_m2(uniao) / 1e6, 2)
    out["camada_km2_fora_da_area_urbanizada"] = round(medidas.area_m2(uniao.difference(au)) / 1e6, 2)
    return out


def resumo(g: pd.DataFrame, peso: str | None) -> dict:
    return {
        "unidades": int(len(g)),
        **({peso: int(g[peso].sum())} if peso else {}),
        "por_poligono": tabela(g, peso),
        "por_tipo_pelo_nome": {
            t: int(n) for t, n in g["nome"].map(
                lambda x: FORA if x == FORA else tipo_pelo_nome(x)).value_counts().items()},
        "unidades_que_tocam_mais_de_um_poligono": int((g["polígonos_tocados"] > 1).sum()),
        "unidades_fora_de_qualquer_poligono": int((g["frac_coberta"] == 0).sum()),
        "unidades_atribuidas_com_menos_de_metade_da_area": int((g["frac_do_maior"] < 0.5).sum()),
        "fora_da_camada": fora_da_camada(g, peso),
    }


def main() -> None:
    b = conferido(BAIRROS).to_crs(paths.crs_producao())
    camada = ex.ler_camada()
    v = camada[~camada[s1.CAMPO_A_PARTE]].set_index("unidade", drop=False)

    ag = conferido(AGRUP)
    at = atribuir(ag, b).join(ag.set_index("unidade")[["agrupamento", "dom_10", "pop_10"]])
    agrupamentos = {str(k): resumo(x, "dom_10") for k, x in at.groupby("agrupamento")}
    por_unidade = [at.assign(grupo="s2_agrupamento_" + at["agrupamento"].astype(str))]

    novas = v[v["classe"] == "nova"]
    at_n = atribuir(novas, b).join(novas[["dom_22", "resolucao"]])
    novas_out = {"todas": resumo(at_n, "dom_22"),
                 **{f"resolucao_{r}": resumo(x, "dom_22") for r, x in at_n.groupby("resolucao")}}
    por_unidade.append(at_n.assign(grupo="s1_nova_" + at_n["resolucao"].astype(str)))

    faces = json.loads(FACES.read_text(encoding="utf-8"))
    fen = faces["extintas_urbanas_por_fenomeno"]
    lista = {u: FENOMENOS[k] for k in FENOMENOS for u in fen[k]["unidades_lista"]}
    agrup_053 = set(faces["agrupamento_053_054"]["unidades"])
    ext = v.loc[list(lista)]
    at_e = atribuir(ext, b).join(ext[["dom_10"]])
    at_e["fenomeno"] = at_e.index.map(lista)
    extintas = {"todas": resumo(at_e, "dom_10"),
                **{f: resumo(x, "dom_10") for f, x in at_e.groupby("fenomeno")},
                "agrupamento_053_054": resumo(at_e[at_e.index.isin(agrup_053)], "dom_10")}
    por_unidade.append(at_e.assign(grupo="s1_extinta: " + at_e["fenomeno"]))

    resultado = {
        "objeto": "interpretação: bairro ou loteamento das unidades dos resultados_s1 e s2 "
                  "(cenário adotado, setor 136 à parte)",
        "origem_dos_nomes": ORIGEM,
        "bairros_loteamentos": {"arquivo": paths.relativo(BAIRROS),
                                "sha256_conteudo": metadados.ler(BAIRROS)["sha256_conteudo"],
                                "no_manifesto": False, "poligonos": int(len(b)),
                                "cobertura": cobertura(b)},
        "camada_sha256_conteudo": metadados.ler(s1.CAMADA)["sha256_conteudo"],
        "agrupamentos_sha256_conteudo": metadados.ler(AGRUP)["sha256_conteudo"],
        "criterio": "maior área de interseção entre a unidade e cada polígono; a parte da unidade "
                    "fora de todos os polígonos concorre como '(fora da camada)'; empate: menor id",
        "mais_proximo": "para as unidades atribuídas a '(fora da camada)': o polígono mais "
                        f"próximo, até {PROXIMO_ATE_M} m, só para nomear a vizinhança — não é "
                        "atribuição",
        "tipo_pelo_nome": "prefixo do nome (LOTEAMENTO / BAIRRO / VILA); a camada não tem campo "
                          "de tipo, nem hierarquia bairro–loteamento, nem data de aprovação",
        "figuras": "não mudam: bairro e loteamento entram como texto, não como camada",
        "s2_agrupamentos_divergencia": agrupamentos,
        "s1_novas": novas_out,
        "s1_extintas_urbanas": extintas,
        "crs_operacao": paths.crs_producao(),
        "lista_por_unidade": f"{paths.relativo(LISTA)} (fora do git)",
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    colunas = ["grupo", "nome", "frac_do_maior", "mais_proximo", "dist_mais_proximo_m",
               "frac_coberta", "polígonos_tocados", "dom_10", "dom_22"]
    pd.concat(por_unidade).rename_axis("unidade").reindex(columns=colunas).to_csv(
        LISTA, encoding="utf-8")
    print(f"gravado: {paths.relativo(SAIDA)} e {paths.relativo(LISTA)}")


if __name__ == "__main__":
    main()
