"""
A03 — dimensionamento, bloco 1: o descompasso no nível município.

População, domicílios particulares permanentes, DPP ocupados, moradores por
domicílio ocupado e domicílios não ocupados em Bagé, em 2010 e 2022, com urbano
e rural separados.

Universos (documentação do IBGE, citada em dimensionamento.md):
  2010  `Basico V001` = DPP, que em 2010 são os OCUPADOS — os fechados entraram
        aqui por imputação (Documentação dos agregados, "Tratamento dos
        domicílios fechados"). Vagos e de uso ocasional NÃO são publicados por
        setor em 2010: o script registra a ausência, não estima.
  2022  `basico v0003` = domicílios particulares (DPPO + DPPV + DPPUO + DPIO);
        `v0007` = ocupados (DPPO + DPIO); `v0008` = uso ocasional; `v0009` =
        vagos. O DPPO puro é `caracteristicas_domicilio1 V00001` e os moradores
        em DPPO, `V00005` — é esse o par comparável com 2010.

LÊ só derivados/bage/ (extraídos por r00 e r06); ESCREVE só
derivados/d01_descompasso.json (fora do git).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
B10 = DERIV / "bage" / "c2010"
B22 = DERIV / "bage" / "c2022"


def num(coluna: pd.Series) -> pd.Series:
    """Texto do IBGE -> número; 'X' (suprimido) e vazio viram NaN."""
    return pd.to_numeric(coluna.astype(str).str.strip().str.replace(",", "."), errors="coerce")


def ler_2010() -> dict:
    basico = pd.read_csv(B10 / "Basico_RS.csv", sep=";", dtype=str, encoding="latin-1")
    dom02 = pd.read_csv(B10 / "Domicilio02_RS.csv", sep=";", dtype=str, encoding="latin-1")
    urbano = basico["Situacao_setor"].astype(int) <= 3
    pop = num(dom02.set_index(dom02["Cod_setor"]).reindex(basico["Cod_setor"])["V001"]).values
    dpp, moradores = num(basico["V001"]), num(basico["V002"])
    saida = {"suprimidos": {"basico_V001": int(num(basico["V001"]).isna().sum()),
                            "domicilio02_V001": int(pd.isna(pop).sum())},
             "setores": int(len(basico))}
    for rotulo, sel in (("total", slice(None)), ("urbano", urbano.values), ("rural", (~urbano).values)):
        p, d, m = pd.Series(pop)[sel].sum(), dpp[sel].sum(), moradores[sel].sum()
        saida[rotulo] = {"populacao": int(p), "dpp_ocupados": int(d),
                         "moradores_em_dpp": int(m), "moradores_por_domicilio": round(m / d, 3)}
    saida["nao_ocupados"] = ("NÃO PUBLICADO por setor em 2010: os agregados por setor só "
                             "trazem DPP ocupados (com os fechados imputados). Vagos e de uso "
                             "ocasional não estão em data/raw/ para 2010, nem por setor nem nas "
                             "tabelas municipais 4.23.x do RS.")
    return saida


def ler_2022() -> dict:
    basico = pd.read_csv(B22 / "Agregados_por_setores_basico.csv", sep=";", dtype=str)
    cd1 = pd.read_csv(B22 / "Agregados_por_setores_caracteristicas_domicilio1.csv",
                      sep=";", dtype=str).set_index("CD_setor")
    cd1 = cd1.reindex(basico["CD_SETOR"].str.strip())
    urbano = basico["SITUACAO"].str.lower().str.startswith("urb").values
    col = {c: num(basico[c]) for c in ("v0001", "v0002", "v0003", "v0004", "v0007", "v0008", "v0009")}
    dppo, moradores_dppo = num(cd1["V00001"]), num(cd1["V00005"])
    dpio = num(cd1["V00002"])
    # onde o DPPO não é publicado (4 setores com X e 1 sem linha), o teto do que falta é
    # o v0007 do próprio setor, que não tem supressão
    sem_dppo = dppo.isna().values
    saida = {"suprimidos": {"basico_v0001": int(col["v0001"].isna().sum()),
                            "cd1_V00001": int(dppo.isna().sum()),
                            "cd1_V00005": int(moradores_dppo.isna().sum())},
             "setores_sem_dppo_publicado": basico["CD_SETOR"][sem_dppo].str.strip().tolist(),
             "teto_do_dppo_que_falta_v0007_desses_setores": int(col["v0007"][sem_dppo].sum()),
             "setores": int(len(basico))}
    for rotulo, sel in (("total", slice(None)), ("urbano", urbano), ("rural", ~urbano)):
        particulares = col["v0003"][sel].sum()
        ocup = col["v0007"][sel].sum()
        d, m = dppo[sel].sum(), moradores_dppo[sel].sum()
        uo, vagos = col["v0008"][sel].sum(), col["v0009"][sel].sum()
        saida[rotulo] = {
            "populacao": int(col["v0001"][sel].sum()),
            "domicilios_total": int(col["v0002"][sel].sum()),
            "domicilios_particulares": int(particulares),
            "domicilios_coletivos": int(col["v0004"][sel].sum()),
            "dp_ocupados_dppo_mais_dpio": int(ocup),
            "dpp_ocupados": int(d),
            "dp_improvisados_ocupados": int(dpio[sel].sum()),
            "moradores_em_dppo": int(m),
            "moradores_por_domicilio": round(m / d, 3),
            "uso_ocasional": int(uo),
            "vagos": int(vagos),
            "nao_ocupados": int(uo + vagos),
            "nao_ocupados_pct_dos_particulares": round(100 * (uo + vagos) / particulares, 2),
        }
    return saida


def reclassificacao_urbano_rural() -> dict:
    """Quanto do salto urbano é mudança de classificação da Base Territorial.

    Pelo de/para oficial 2010->2022 (mesma construção do r03/r08): população de
    2010 em setores RURAIS cujas áreas aparecem, em 2022, só em setores URBANOS.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from r03_geografia import componentes  # noqa: PLC0415

    arq = next((DERIV / "planilhas" / "c2022").glob("Historico_formacao*.csv"))
    df = pd.read_csv(arq, sep=";", dtype=str)
    codigo = str(pd.read_csv(B10 / "Basico_RS.csv", sep=";", dtype=str,
                             encoding="latin-1")["Cod_setor"].iloc[0])[:7]
    df = df[df["GEOCODIGO_2022_DIVULGAÇÃO"].str.startswith(codigo)
            | df["GEOCODIGO_2010"].str.startswith(codigo)]
    arestas = set(zip(df["GEOCODIGO_2010"], df["GEOCODIGO_2022_DIVULGAÇÃO"]))

    b10 = pd.read_csv(B10 / "Basico_RS.csv", sep=";", dtype=str, encoding="latin-1")
    d02 = pd.read_csv(B10 / "Domicilio02_RS.csv", sep=";", dtype=str,
                      encoding="latin-1").set_index("Cod_setor")
    urbano10 = dict(zip(b10["Cod_setor"], b10["Situacao_setor"].astype(int) <= 3))
    pop10 = num(d02["V001"]).to_dict()
    dpp10 = dict(zip(b10["Cod_setor"], num(b10["V001"])))
    b22 = pd.read_csv(B22 / "Agregados_por_setores_basico.csv", sep=";", dtype=str)
    urbano22 = dict(zip(b22["CD_SETOR"].str.strip(),
                        b22["SITUACAO"].str.lower().str.startswith("urb")))

    virou_urbano = {"populacao_2010": 0.0, "dpp_2010": 0.0, "setores_2010": 0, "amcs": 0}
    for antigos, novos in componentes(arestas):
        rurais = [a for a in antigos if urbano10.get(a) is False]
        if not rurais or not all(urbano22.get(n, False) for n in novos):
            continue
        virou_urbano["amcs"] += 1
        virou_urbano["setores_2010"] += len(rurais)
        virou_urbano["populacao_2010"] += sum(pop10.get(a, 0) or 0 for a in rurais)
        virou_urbano["dpp_2010"] += sum(dpp10.get(a, 0) or 0 for a in rurais)
    return {k: (int(v) if isinstance(v, float) else v) for k, v in virou_urbano.items()}


def variacao(a: float, b: float) -> dict:
    return {"2010": a, "2022": b, "abs": round(b - a, 3), "pct": round(100 * (b - a) / a, 2)}


def main() -> None:
    r10, r22 = ler_2010(), ler_2022()
    comparacao = {}
    for rotulo in ("total", "urbano", "rural"):
        a, b = r10[rotulo], r22[rotulo]
        comp = {"populacao": variacao(a["populacao"], b["populacao"]),
                "dpp_ocupados": variacao(a["dpp_ocupados"], b["dpp_ocupados"]),
                "moradores_por_domicilio": variacao(a["moradores_por_domicilio"],
                                                    b["moradores_por_domicilio"])}
        comp["razao_variacao_domicilios_sobre_populacao"] = (
            round(comp["dpp_ocupados"]["pct"] / comp["populacao"]["pct"], 2)
            if comp["populacao"]["pct"] else None)
        comparacao[rotulo] = comp
    resultado = {"censo_2010": r10, "censo_2022": r22, "variacao_2010_2022": comparacao,
                 "reclassificacao_urbano_rural": reclassificacao_urbano_rural()}
    (DERIV / "d01_descompasso.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    for rotulo in ("total", "urbano", "rural"):
        c = comparacao[rotulo]
        print(f"{rotulo:<7} população {c['populacao']['2010']:>7,} -> {c['populacao']['2022']:>7,} "
              f"({c['populacao']['pct']:+.2f} %)   DPPO {c['dpp_ocupados']['2010']:>6,} -> "
              f"{c['dpp_ocupados']['2022']:>6,} ({c['dpp_ocupados']['pct']:+.2f} %)   "
              f"mor/dom {c['moradores_por_domicilio']['2010']} -> "
              f"{c['moradores_por_domicilio']['2022']}")
    for rotulo in ("total", "urbano", "rural"):
        b = r22[rotulo]
        print(f"{rotulo:<7} 2022 não ocupados {b['nao_ocupados']:>5,} "
              f"({b['nao_ocupados_pct_dos_particulares']} % dos particulares) = vagos "
              f"{b['vagos']:,} + uso ocasional {b['uso_ocasional']:,}")
    print("reclassificação rural -> urbano:", resultado["reclassificacao_urbano_rural"])
    print("suprimidos:", r10["suprimidos"], r22["suprimidos"])


if __name__ == "__main__":
    main()
