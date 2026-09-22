"""
A03 — aglomerados subnormais 2010 × favelas e comunidades urbanas (FCU) 2022.

  - Bagé tem aglomerado subnormal em 2010? Tabela de setores
    (AGSN2010Setores.xls) e, como conferência independente, a tabela municipal
    das informações territoriais (tab01), com controle no RS.
  - Os setores de FCU de 2022 correspondem, pelo de/para oficial, a quais
    setores de 2010, e esses eram de aglomerado?
  - Cobertura da pesquisa do entorno nas FCU de Bagé (planilha do IBGE).

LÊ data/raw/ e derivados/; ESCREVE derivados/r07_aglomerados_2010.json.
"""

from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from scripts.utils import paths  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
CODIGO = paths.codigo_ibge()
T10 = paths.caminho("raw_tabular", "ibge", "censo_2010")
T22 = paths.caminho("raw_tabular", "ibge", "censo_2022")


def planilhas_do_zip(arq: Path) -> dict[str, pd.DataFrame]:
    out = {}
    with zipfile.ZipFile(arq) as z:
        for n in z.namelist():
            if n.lower().endswith((".xls", ".xlsx")):
                for aba, df in pd.read_excel(io.BytesIO(z.read(n)), sheet_name=None,
                                             header=None, dtype=str).items():
                    out[f"{Path(n).name}/{aba}"] = df.fillna("").astype(str)
    return out


def main() -> None:
    # 1) setores de aglomerado subnormal 2010
    agsn = planilhas_do_zip(T10 / "Setores_Censitarios_agsn_2010.zip")
    setores = next(df for k, df in agsn.items() if "Setores" in k.split("/")[-1])
    setores.columns = setores.iloc[0]
    setores = setores.iloc[1:]
    bage_agsn = setores[setores["CD_MUNICIP"].str.strip() == CODIGO]

    # 2) conferência na tabela municipal (tab01), com controle no RS
    tabs = planilhas_do_zip(T10 / "UFs_Municipios.zip")
    tab01 = next(df for k, df in tabs.items() if k.startswith("tab01"))
    i_rs = tab01.index[tab01[0].str.strip() == "Rio Grande do Sul"][0]
    bloco = []
    for _, l in tab01.loc[i_rs + 1:].iterrows():
        if l[0].strip() in ("Centro-Oeste", "") or not l[1].strip().isdigit():
            break
        bloco.append({"municipio": l[0].strip(), "aglomerados": int(l[1]),
                      "domicilios": int(l[2]), "moradores": int(l[3])})
    rs_total = tab01.loc[i_rs, [1, 2, 3]].tolist()

    # 3) setores de FCU 2022 -> de/para -> 2010
    fcu = pd.read_excel(T22 / "FavelaseComunidadesUrbanas2022Setores_20250417.xlsx",
                        sheet_name="Setores_FCUs", dtype=str)
    fcu_bage = fcu[fcu["CD_MUN"] == CODIGO]
    hist = pd.read_csv(next((DERIV / "planilhas" / "c2022").glob("Historico_formacao*.csv")),
                       sep=";", dtype=str)
    rastro = []
    for _, l in fcu_bage.iterrows():
        h = hist[hist["GEOCODIGO_2022_DIVULGAÇÃO"] == l["CD_SETOR"]]
        origem = sorted(set(h["GEOCODIGO_2010"]))
        rastro.append({
            "setor_2022": l["CD_SETOR"], "fcu": l["NM_FCU"], "cd_fcu": l["CD_FCU"],
            "setores_2010": origem,
            "frm_2022_divulgacao": sorted(set(h["FRM_2022_DIVULGAÇÃO"])),
            "setor_2010_era_aglomerado": any(o in set(setores["CD_SETOR"]) for o in origem),
            "irmaos_2022_do_setor_2010": sorted(set(
                hist[hist["GEOCODIGO_2010"].isin(origem)]["GEOCODIGO_2022_DIVULGAÇÃO"])),
        })

    # 4) cobertura do entorno nas FCU
    cob = pd.read_excel(T22 / "FCU_Entorno_Cobertura_das_FCUs_moradores_em_DPPO.xlsx", dtype=str)
    cob = cob[cob.iloc[:, 0].astype(str).str.startswith(CODIGO)]

    resultado = {
        "aglomerados_2010_setores_de_bage": int(len(bage_agsn)),
        "aglomerados_2010_setores_no_pais": int(len(setores)),
        "tab01_bage_listado": any(b["municipio"] == paths.nome_municipio() for b in bloco),
        "tab01_rs_total": rs_total, "tab01_rs_municipios": bloco,
        "fcu_2022_setores_de_bage": rastro,
        "cobertura_entorno_fcu_bage": cob.values.tolist(),
    }
    (DERIV / "r07_aglomerados_2010.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"aglomerados 2010 em Bagé: {len(bage_agsn)} setores (país: {len(setores)})")
    print(f"tab01: Bagé listado? {resultado['tab01_bage_listado']}; RS {rs_total} em {len(bloco)} municípios")
    for r in rastro:
        print(f"  {r['setor_2022']} {r['fcu']:<20} <- 2010 {r['setores_2010']} FRM {r['frm_2022_divulgacao']} "
              f"aglomerado 2010? {r['setor_2010_era_aglomerado']}")
    for c in resultado["cobertura_entorno_fcu_bage"]:
        print("  cobertura entorno:", c)


if __name__ == "__main__":
    main()
