"""
A03 — dimensionamento, bloco 2: Bagé é caso comum ou fora da curva?

Compara Bagé com o RS e com o Brasil e situa Bagé entre os municípios do RS.

O que existe em data/raw/ e o que não:
  2022  agregados por setor no recorte BR -> qualquer município do país, e daí
        RS e Brasil por soma. Conferido contra
        `Populacao_residente_por_situacao_do_domicilio_municipios.xlsx`, a
        tabela oficial de população por município da própria divulgação.
  2010  agregados por setor SÓ no recorte RS -> RS e seus municípios. NÃO há,
        no acervo, nada por município para o Brasil em 2010: a comparação
        2010 -> 2022 com o Brasil fica registrada como AUSENTE, não estimada.

Indicadores (os mesmos para os três recortes, para serem comparáveis):
  - população residente;
  - domicílios particulares ocupados (2010: `Basico V001`, que são os DPP
    ocupados; 2022: `basico v0007` = DPPO + DPIO, sem supressão);
  - pessoas por domicílio particular ocupado = população / ocupados (não é
    "moradores em DPPO / DPPO", que só existe em 2022 e sofre supressão; o
    d01 mede os dois em Bagé, para dimensionar a diferença);
  - % de não ocupados = (vagos + uso ocasional) / domicílios particulares —
    SÓ 2022, porque 2010 não publica não ocupados (d01).

Posição de Bagé no RS: percentil do crescimento de domicílios, do crescimento
de população e da DIFERENÇA entre os dois em pontos percentuais. A diferença é
o indicador principal porque a razão entre as duas variações explode onde a
população quase não mudou — em Bagé a razão é alta justamente por isso; a razão
é relatada, mas o ranking usa a diferença.

LÊ só data/raw/ e derivados/; ESCREVE só derivados/d02_comparacao.json.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from scripts.utils import paths  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
TAB22 = paths.caminho("raw_tabular", "ibge", "censo_2022")
TAB10 = paths.caminho("raw_tabular", "ibge", "censo_2010")
CODIGO = paths.codigo_ibge()
UF_RS = "43"
# faixa de porte usada para o grupo de comparação: municípios de 50 mil a 200 mil
# habitantes em 2022 (Bagé tem 117.938)
PORTE = (50_000, 200_000)


def num(coluna: pd.Series) -> pd.Series:
    return pd.to_numeric(coluna.astype(str).str.strip().str.replace(",", "."), errors="coerce")


def municipios_2022() -> pd.DataFrame:
    """Soma por município dos setores do Brasil (recorte BR do básico de 2022)."""
    destino = DERIV / "_bruto" / "d02_municipios_2022.csv"
    if not destino.exists():
        zip_ = TAB22 / "Agregados_por_setores_basico_BR_20260520.zip"
        with zipfile.ZipFile(zip_) as z, z.open(z.namelist()[0]) as bruto:
            partes = []
            for pedaco in pd.read_csv(bruto, sep=";", dtype=str, encoding="latin-1",
                                      chunksize=200_000,
                                      usecols=["CD_MUN", "NM_MUN", "CD_UF", "SITUACAO",
                                               "v0001", "v0003", "v0007", "v0008", "v0009"]):
                for c in ("v0001", "v0003", "v0007", "v0008", "v0009"):
                    pedaco[c] = num(pedaco[c])
                partes.append(pedaco.groupby(["CD_MUN", "NM_MUN", "CD_UF"], as_index=False)
                              [["v0001", "v0003", "v0007", "v0008", "v0009"]].sum())
        df = (pd.concat(partes).groupby(["CD_MUN", "NM_MUN", "CD_UF"], as_index=False).sum())
        destino.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(destino, sep=";", index=False)
    df = pd.read_csv(destino, sep=";", dtype={"CD_MUN": str, "CD_UF": str})
    return df.rename(columns={"v0001": "pop", "v0003": "particulares", "v0007": "ocupados",
                              "v0008": "uso_ocasional", "v0009": "vagos"})


def municipios_2010_rs() -> pd.DataFrame:
    """Soma por município dos setores do RS (único recorte de 2010 no acervo)."""
    destino = DERIV / "_bruto" / "d02_municipios_2010_rs.csv"
    if not destino.exists():
        with zipfile.ZipFile(TAB10 / "RS_20260615.zip") as z:
            nomes = {n.rsplit("/", 1)[-1].lower(): n for n in z.namelist()
                     if n.lower().endswith(".csv")}
            def ler(arquivo: str, colunas: list[str]) -> pd.DataFrame:
                with z.open(nomes[arquivo]) as bruto:
                    df = pd.read_csv(bruto, sep=";", dtype=str, encoding="latin-1",
                                     usecols=["Cod_setor"] + colunas)
                df["mun"] = df["Cod_setor"].str.strip().str[:7]
                for c in colunas:
                    df[c] = num(df[c])
                return df.groupby("mun", as_index=False)[colunas].sum()
            basico = ler("basico_rs.csv", ["V001", "V002"])
            dom02 = ler("domicilio02_rs.csv", ["V001"]).rename(columns={"V001": "pop"})
        df = basico.rename(columns={"V001": "ocupados", "V002": "moradores"}).merge(dom02, on="mun")
        destino.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(destino, sep=";", index=False)
    return pd.read_csv(destino, sep=";", dtype={"mun": str})


def conferir_populacao_2022(m22: pd.DataFrame) -> dict:
    """Soma dos setores × tabela oficial de população por município da divulgação."""
    arq = DERIV / "planilhas" / "c2022" / \
        "Populacao_residente_por_situacao_do_domicilio_municipios__result_html.csv"
    oficial = pd.read_csv(arq, sep=";", dtype=str, header=None, skiprows=2,
                          names=["nome", "cod", "urbana", "rural", "total"])
    oficial = oficial[oficial["cod"].str.fullmatch(r"\d{7}", na=False)]
    oficial["total"] = num(oficial["total"])
    j = m22.merge(oficial, left_on="CD_MUN", right_on="cod", how="inner")
    dif = (j["pop"] - j["total"])
    return {"municipios_conferidos": int(len(j)),
            "municipios_com_diferenca": int((dif != 0).sum()),
            "diferenca_total": int(dif.sum()),
            "bage_soma_setores": int(j.loc[j["CD_MUN"] == CODIGO, "pop"].iloc[0]),
            "bage_tabela_oficial": int(j.loc[j["CD_MUN"] == CODIGO, "total"].iloc[0])}


def indicadores(pop: float, ocupados: float, particulares=None, nao_ocupados=None) -> dict:
    r = {"populacao": int(pop), "domicilios_particulares_ocupados": int(ocupados),
         "pessoas_por_domicilio_ocupado": round(pop / ocupados, 3)}
    if particulares is not None:
        r["domicilios_particulares"] = int(particulares)
        r["nao_ocupados"] = int(nao_ocupados)
        r["nao_ocupados_pct"] = round(100 * nao_ocupados / particulares, 2)
    return r


def var_pct(a: float, b: float) -> float:
    return round(100 * (b - a) / a, 2)


def percentil(serie: pd.Series, valor: float) -> float:
    """% dos municípios com valor MENOR que o de Bagé."""
    return round(100 * float((serie < valor).mean()), 1)


def main() -> None:
    m22 = municipios_2022()
    m10 = municipios_2010_rs()
    rs22 = m22[m22["CD_UF"] == UF_RS]

    # --- recortes: Bagé, RS, Brasil ---------------------------------------
    b22 = m22[m22["CD_MUN"] == CODIGO].iloc[0]
    b10 = m10[m10["mun"] == CODIGO].iloc[0]
    recortes = {
        "bage": {"2010": indicadores(b10["pop"], b10["ocupados"]),
                 "2022": indicadores(b22["pop"], b22["ocupados"], b22["particulares"],
                                     b22["uso_ocasional"] + b22["vagos"])},
        "rs": {"2010": indicadores(m10["pop"].sum(), m10["ocupados"].sum()),
               "2022": indicadores(rs22["pop"].sum(), rs22["ocupados"].sum(),
                                   rs22["particulares"].sum(),
                                   (rs22["uso_ocasional"] + rs22["vagos"]).sum())},
        "brasil": {"2010": "AUSENTE em data/raw/: 2010 só tem o recorte RS",
                   "2022": indicadores(m22["pop"].sum(), m22["ocupados"].sum(),
                                       m22["particulares"].sum(),
                                       (m22["uso_ocasional"] + m22["vagos"]).sum())},
    }
    for nome in ("bage", "rs"):
        a, b = recortes[nome]["2010"], recortes[nome]["2022"]
        vp = var_pct(a["populacao"], b["populacao"])
        vd = var_pct(a["domicilios_particulares_ocupados"], b["domicilios_particulares_ocupados"])
        recortes[nome]["variacao"] = {
            "populacao_pct": vp, "ocupados_pct": vd,
            "diferenca_pp": round(vd - vp, 2), "razao_ocupados_sobre_populacao": round(vd / vp, 2),
            "pessoas_por_domicilio": {"2010": a["pessoas_por_domicilio_ocupado"],
                                      "2022": b["pessoas_por_domicilio_ocupado"]}}

    # --- posição de Bagé entre os municípios do RS ------------------------
    rs = rs22.merge(m10, left_on="CD_MUN", right_on="mun", suffixes=("_22", "_10"))
    rs = rs[(rs["pop_10"] > 0) & (rs["ocupados_10"] > 0)]
    rs["var_pop"] = 100 * (rs["pop_22"] - rs["pop_10"]) / rs["pop_10"]
    rs["var_dom"] = 100 * (rs["ocupados_22"] - rs["ocupados_10"]) / rs["ocupados_10"]
    rs["dif_pp"] = rs["var_dom"] - rs["var_pop"]
    rs["nao_ocup_pct"] = 100 * (rs["uso_ocasional"] + rs["vagos"]) / rs["particulares"]
    bage = rs[rs["CD_MUN"] == CODIGO].iloc[0]

    def ranking(quadro: pd.DataFrame, rotulo: str) -> dict:
        return {"rotulo": rotulo, "municipios": int(len(quadro)),
                "bage": {"var_pop_pct": round(float(bage["var_pop"]), 2),
                         "var_dom_pct": round(float(bage["var_dom"]), 2),
                         "diferenca_pp": round(float(bage["dif_pp"]), 2),
                         "nao_ocupados_pct": round(float(bage["nao_ocup_pct"]), 2)},
                "percentil_de_bage": {
                    "diferenca_pp": percentil(quadro["dif_pp"], bage["dif_pp"]),
                    "var_dom_pct": percentil(quadro["var_dom"], bage["var_dom"]),
                    "var_pop_pct": percentil(quadro["var_pop"], bage["var_pop"]),
                    "nao_ocupados_pct": percentil(quadro["nao_ocup_pct"], bage["nao_ocup_pct"])},
                "mediana": {"diferenca_pp": round(float(quadro["dif_pp"].median()), 2),
                            "var_dom_pct": round(float(quadro["var_dom"].median()), 2),
                            "var_pop_pct": round(float(quadro["var_pop"].median()), 2),
                            "nao_ocupados_pct": round(float(quadro["nao_ocup_pct"].median()), 2)},
                "quartis_diferenca_pp": [round(float(v), 2) for v in
                                         quadro["dif_pp"].quantile([0.25, 0.5, 0.75])],
                "acima_de_bage": {
                    "diferenca_pp": int((quadro["dif_pp"] > bage["dif_pp"]).sum()),
                    "nao_ocupados_pct": int((quadro["nao_ocup_pct"] > bage["nao_ocup_pct"]).sum())}}

    porte = rs[(rs["pop_22"] >= PORTE[0]) & (rs["pop_22"] <= PORTE[1])]
    posicao = {"rs_todos": ranking(rs, "todos os municípios do RS com dado nos dois censos"),
               "rs_porte_semelhante": ranking(
                   porte, f"municípios do RS com população 2022 entre {PORTE[0]:,} e "
                          f"{PORTE[1]:,}".replace(",", "."))}
    # também: municípios do RS que cresceram em domicílios e perderam população
    posicao["rs_divergentes"] = {
        "municipios_com_dom_sobe_e_pop_cai": int(((rs["var_dom"] > 0) & (rs["var_pop"] < 0)).sum()),
        "municipios_com_dom_sobe": int((rs["var_dom"] > 0).sum()),
        "municipios_com_pop_cai": int((rs["var_pop"] < 0).sum()),
        "total": int(len(rs))}

    resultado = {"recortes": recortes, "posicao_de_bage": posicao,
                 "conferencia_populacao_2022": conferir_populacao_2022(m22),
                 "faixa_de_porte": {"minimo": PORTE[0], "maximo": PORTE[1],
                                    "municipios_no_rs": int(len(porte))}}
    (DERIV / "d02_comparacao.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    for nome in ("bage", "rs"):
        v = recortes[nome]["variacao"]
        print(f"{nome:<7} pop {v['populacao_pct']:+.2f} %  ocupados {v['ocupados_pct']:+.2f} %  "
              f"dif {v['diferenca_pp']:+.2f} pp  razão {v['razao_ocupados_sobre_populacao']}  "
              f"pessoas/dom {v['pessoas_por_domicilio']['2010']} -> "
              f"{v['pessoas_por_domicilio']['2022']}")
    print("brasil 2022", recortes["brasil"]["2022"])
    for chave in ("rs_todos", "rs_porte_semelhante"):
        p = posicao[chave]
        print(f"{chave} ({p['municipios']} municípios): Bagé dif {p['bage']['diferenca_pp']} pp "
              f"-> percentil {p['percentil_de_bage']['diferenca_pp']} (mediana "
              f"{p['mediana']['diferenca_pp']}); não ocupados {p['bage']['nao_ocupados_pct']} % "
              f"-> percentil {p['percentil_de_bage']['nao_ocupados_pct']} (mediana "
              f"{p['mediana']['nao_ocupados_pct']} %); acima de Bagé: "
              f"{p['acima_de_bage']}")
    print("divergentes:", posicao["rs_divergentes"])
    print("conferência população 2022:", resultado["conferencia_populacao_2022"])


if __name__ == "__main__":
    main()
