"""
A03 — dimensionamento, bloco 4: como o entorno urbanístico de 2022 se distribui
em Bagé, por domicílio e por face, e se a variação entre setores é grande o
bastante para diferenciar áreas.

Duas leituras, porque respondem a coisas diferentes:
  - MUNICÍPIO: % de domicílios (e de faces) com o item, somando tudo — é o
    retrato do município;
  - ENTRE SETORES: a mesma % calculada em CADA setor, cada setor com peso 1, e
    a dispersão dessa distribuição (mínimo, quartis, p10/p90, máximo, desvio
    padrão, amplitude interquartil). É essa dispersão que diz se o item
    diferencia áreas: item que está em ~100 % de todo setor não separa nada.

O denominador de cada item é o próprio item (sim + não + não declarado), não o
universo do setor: assim "não declarado" não vira "não". A fatia de não
declarado é relatada à parte, por item.

Os nomes dos itens e das categorias saem do dicionário do IBGE
(`doc/dicionarios_de_dados_entorno.zip`, convertido por r06), não de lista
escrita à mão.

LÊ só derivados/ (extraídos por r06); ESCREVE só derivados/d04_entorno.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
B22 = DERIV / "bage" / "c2022"
PL = DERIV / "planilhas" / "c2022"
UNIDADES = {
    "domicilios": ("entorno_domicilios.csv",
                   "dicionario_entorno_domicilios__dicionario_entorno_domicilios_v.csv"),
    "faces": ("entorno_faces.csv", "dicionario_entorno_faces__Planilha1.csv"),
}


def ler_dicionario(arquivo: str) -> tuple[dict[str, dict[str, str]], str]:
    """{item: {categoria: variável}} e a variável do universo, pelo dicionário."""
    df = pd.read_csv(PL / arquivo, sep=";", dtype=str).dropna()
    itens: dict[str, dict[str, str]] = {}
    universo = ""
    for _, linha in df.iterrows():
        var, desc = linha["Variável"].strip(), linha["Descrição"]
        partes = re.findall(r"\[([^\]]+)\]", desc)
        rotulo = partes[-1].strip()
        if " - " not in rotulo:            # [FACES NO SETOR] / [... APLICAÇÃO DO ENTORNO]
            universo = universo or var
            continue
        item, categoria = rotulo.rsplit(" - ", 1)
        item = re.sub(r"^(DOMICÍLIOS EM FACE COM|FACE COM)\s*", "", item.strip()).strip()
        itens.setdefault(item, {})[categoria.strip()] = var
    return itens, universo


def num(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    return df[colunas].apply(lambda c: pd.to_numeric(c.astype(str).str.strip()
                                                     .str.replace(",", "."), errors="coerce"))


def resumo(serie: pd.Series) -> dict:
    q = serie.quantile([0.10, 0.25, 0.50, 0.75, 0.90])
    return {"minimo": round(float(serie.min()), 1), "p10": round(float(q[0.10]), 1),
            "q1": round(float(q[0.25]), 1), "mediana": round(float(q[0.50]), 1),
            "q3": round(float(q[0.75]), 1), "p90": round(float(q[0.90]), 1),
            "maximo": round(float(serie.max()), 1),
            "iqr": round(float(q[0.75] - q[0.25]), 1),
            "desvio_padrao": round(float(serie.std()), 1)}


def medir(unidade: str) -> dict:
    arquivo, dicionario = UNIDADES[unidade]
    df = pd.read_csv(B22 / arquivo, sep=";", dtype=str)
    itens, universo = ler_dicionario(dicionario)
    setor = df.columns[0]
    saida = {"variavel_do_universo": universo,
             "setores": int(len(df)),
             "universo_total": int(num(df, [universo])[universo].sum()),
             "itens": {}}
    for item, categorias in itens.items():
        colunas = list(categorias.values())
        v = num(df, colunas)
        total = v.sum(axis=1)
        municipio = v.sum()
        # categoria principal: "SIM" quando o item é binário; senão, cada categoria
        principais = ["SIM"] if "SIM" in categorias else [c for c in categorias if c != "SALTADO"]
        registro = {"variaveis": categorias,
                    "total_no_municipio": int(municipio.sum()),
                    "pct_no_municipio": {}, "entre_setores_pct": {},
                    "setores_com_o_item_medido": int((total > 0).sum())}
        for categoria in principais:
            coluna = categorias[categoria]
            registro["pct_no_municipio"][categoria] = round(
                100 * float(municipio[coluna]) / float(municipio.sum()), 1)
            por_setor = (100 * v[coluna] / total)[total > 0]
            registro["entre_setores_pct"][categoria] = resumo(por_setor)
        if "NÃO DECLARADO" in categorias:
            registro["pct_nao_declarado_no_municipio"] = round(
                100 * float(municipio[categorias["NÃO DECLARADO"]]) / float(municipio.sum()), 1)
        if "SALTADO" in categorias:
            registro["pct_saltado_no_municipio"] = round(
                100 * float(municipio[categorias["SALTADO"]]) / float(municipio.sum()), 1)
        saida["itens"][item] = registro
    saida["setor_coluna"] = setor
    return saida


def main() -> None:
    resultado = {unidade: medir(unidade) for unidade in UNIDADES}
    (DERIV / "d04_entorno.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    for unidade, r in resultado.items():
        print(f"\n== {unidade}: {r['setores']} setores, universo {r['universo_total']:,} "
              f"({r['variavel_do_universo']})")
        print(f"{'item':<34} {'categoria':<26} {'município':>9} {'mediana':>8} {'q1':>6} "
              f"{'q3':>6} {'p10':>6} {'p90':>6} {'iqr':>6} {'n.decl.':>8}")
        for item, reg in r["itens"].items():
            for categoria, pct in reg["pct_no_municipio"].items():
                d = reg["entre_setores_pct"][categoria]
                print(f"{item[:33]:<34} {categoria[:25]:<26} {pct:>8.1f}% {d['mediana']:>8} "
                      f"{d['q1']:>6} {d['q3']:>6} {d['p10']:>6} {d['p90']:>6} {d['iqr']:>6} "
                      f"{reg.get('pct_nao_declarado_no_municipio', ''):>8}")


if __name__ == "__main__":
    main()
