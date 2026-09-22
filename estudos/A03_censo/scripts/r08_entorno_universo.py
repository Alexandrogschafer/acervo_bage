"""
A03 — § 1.4: universo do entorno urbanístico em 2010, em 2022 e o universo COMUM.

Substitui a contagem ad hoc que estava escrita no reconhecimento. Mede:

  (a) 2010: setores de Bagé com entorno coletado, pelo critério do PRÓPRIO IBGE
      ("Os setores onde não houve coleta, das informações do entorno, são
      aqueles que nos arquivos entorno01 … entorno05 apresentam valor zero para
      todas as informações" — documentação da Base de informações por setor
      censitário do Censo 2010). Do teste ficam de fora só os dois TOTAIS do
      setor — `V001` do Entorno01 (DPP) e `V422` do Entorno03 (moradores em
      DPP) —, que aparecem mesmo onde não houve coleta do entorno;
  (b) 2022: setores com linha na tabela do entorno por domicílios;
  (c) o universo COMUM: como o geocódigo não é estável entre censos (§ 3.1), a
      interseção é feita por ÁREA MÍNIMA COMUM — os componentes conexos do
      de/para oficial 2010→2022 (mesma construção do r03). Uma AMC só entra no
      universo comum se TODOS os seus setores de 2010 e TODOS os de 2022 têm
      entorno; AMC com parte dos setores sem entorno é relatada à parte, porque
      nela o total do item não é comparável.

LÊ só derivados/ (produzidos por r00, r03 e r06); ESCREVE só
derivados/r08_entorno_universo.json (fora do git).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from r03_geografia import componentes  # noqa: E402

from scripts.utils import paths  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
CODIGO = paths.codigo_ibge()
ARQUIVOS_2010 = [f"Entorno0{i}_RS.csv" for i in range(1, 6)]
# totais do setor (DPP no Entorno01, moradores em DPP no Entorno03): existem mesmo onde
# não houve coleta do entorno, e por isso não contam como resposta. Conferido item a
# item: com eles no teste, 21 setores rurais de situação 8 entrariam como "com entorno"
# tendo só o total de moradores preenchido.
NAO_E_RESPOSTA = {("Entorno01_RS.csv", "V001"), ("Entorno03_RS.csv", "V422")}


def ler_2010() -> tuple[pd.DataFrame, dict]:
    """Setores de 2010 com entorno coletado, pelo critério do IBGE."""
    respostas, situacao, dpp = {}, None, None
    for nome in ARQUIVOS_2010:
        df = pd.read_csv(DERIV / "bage" / "c2010" / nome, sep=";", dtype=str,
                         encoding="latin-1").set_index("Cod_setor")
        if situacao is None:
            situacao = df["Situacao_setor"].astype(int)
            dpp = pd.to_numeric(df["V001"].str.replace(",", "."), errors="coerce").fillna(0)
        colunas = [c for c in df.columns if c.startswith("V")
                   and (nome, c) not in NAO_E_RESPOSTA]
        v = df[colunas].apply(lambda c: pd.to_numeric(c.str.replace(",", "."), errors="coerce"))
        respostas[nome] = v.fillna(0).sum(axis=1)
    soma = pd.DataFrame(respostas).sum(axis=1)
    tem = soma > 0
    urbano = situacao <= 3
    return pd.DataFrame({"tem_entorno": tem, "urbano": urbano, "dpp": dpp}), {
        "criterio": ("alguma variável de Entorno01–Entorno05 diferente de zero, excluídos os "
                     "totais do setor: V001 do Entorno01 (DPP) e V422 do Entorno03 (moradores "
                     "em DPP)"),
        "setores_na_tabela": int(len(tem)),
        "com_entorno": int(tem.sum()),
        "com_entorno_urbanos": f"{int((tem & urbano).sum())}/{int(urbano.sum())}",
        "com_entorno_rurais": f"{int((tem & ~urbano).sum())}/{int((~urbano).sum())}",
        "situacao_dos_rurais_com_entorno": situacao[tem & ~urbano].value_counts().to_dict(),
        "dpp_nos_setores_com_entorno": int(dpp[tem].sum()),
        "dpp_no_municipio": int(dpp.sum()),
    }


def ler_2022() -> tuple[pd.Series, dict]:
    """Setores de 2022 com linha na tabela do entorno por domicílios."""
    basico = pd.read_csv(DERIV / "bage" / "c2022" / "Agregados_por_setores_basico.csv",
                         sep=";", dtype=str)
    setores = basico["CD_SETOR"].str.strip()
    urbano = pd.Series(basico["SITUACAO"].str.lower().str.startswith("urb").values, index=setores)
    ent = pd.read_csv(DERIV / "bage" / "c2022" / "entorno_domicilios.csv", sep=";", dtype=str)
    com_linha = set(ent[ent.columns[0]].str.strip())
    tem = pd.Series(setores.isin(com_linha).values, index=setores)
    return tem, {
        "criterio": "setor com linha na tabela do entorno por domicílios",
        "setores_na_malha": int(len(tem)),
        "com_entorno": int(tem.sum()),
        "com_entorno_urbanos": f"{int((tem & urbano).sum())}/{int(urbano.sum())}",
        "com_entorno_rurais": f"{int((tem & ~urbano).sum())}/{int((~urbano).sum())}",
    }


def universo_comum(tem10: pd.Series, tem22: pd.Series) -> dict:
    """AMCs (componentes conexos do de/para) com entorno nos DOIS anos."""
    arq = next((DERIV / "planilhas" / "c2022").glob("Historico_formacao*.csv"))
    df = pd.read_csv(arq, sep=";", dtype=str)
    df = df[df["GEOCODIGO_2022_DIVULGAÇÃO"].str.startswith(CODIGO)
            | df["GEOCODIGO_2010"].str.startswith(CODIGO)]
    arestas = set(zip(df["GEOCODIGO_2010"], df["GEOCODIGO_2022_DIVULGAÇÃO"]))

    classes: dict[str, dict] = {}
    for antigos, novos in componentes(arestas):
        # setor de 2010 fora da tabela de entorno (os 4 sem linha, § 2) conta como sem
        e10 = [bool(tem10.get(a, False)) for a in antigos]
        e22 = [bool(tem22.get(b, False)) for b in novos]
        if all(e10) and all(e22):
            classe = "com entorno nos dois anos (universo da série)"
        elif not any(e10) and not any(e22):
            classe = "sem entorno em nenhum dos dois anos"
        elif any(e10) and not any(e22):
            classe = "só 2010"
        elif any(e22) and not any(e10):
            classe = "só 2022"
        else:
            classe = "parcial (algum setor sem entorno em um dos anos)"
        r = classes.setdefault(classe, {"amcs": 0, "setores_2010": 0, "setores_2022": 0,
                                        "setores_2010_com_entorno": 0,
                                        "setores_2022_com_entorno": 0})
        r["amcs"] += 1
        r["setores_2010"] += len(antigos)
        r["setores_2022"] += len(novos)
        r["setores_2010_com_entorno"] += sum(e10)
        r["setores_2022_com_entorno"] += sum(e22)
    return {"amcs": sum(c["amcs"] for c in classes.values()), "por_classe": classes}


def main() -> None:
    t2010, r2010 = ler_2010()
    tem22, r2022 = ler_2022()
    resultado = {"entorno_2010": r2010, "entorno_2022": r2022,
                 "universo_comum": universo_comum(t2010["tem_entorno"], tem22)}
    (DERIV / "r08_entorno_universo.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print(f"2010: {r2010['com_entorno']} setores com entorno de {r2010['setores_na_tabela']} "
          f"(urbanos {r2010['com_entorno_urbanos']}, rurais {r2010['com_entorno_rurais']}; "
          f"situação dos rurais {r2010['situacao_dos_rurais_com_entorno']}); "
          f"DPP {r2010['dpp_nos_setores_com_entorno']:,} de {r2010['dpp_no_municipio']:,}")
    print(f"2022: {r2022['com_entorno']} setores com entorno de {r2022['setores_na_malha']} "
          f"(urbanos {r2022['com_entorno_urbanos']}, rurais {r2022['com_entorno_rurais']})")
    print(f"AMCs: {resultado['universo_comum']['amcs']}")
    for classe, r in resultado["universo_comum"]["por_classe"].items():
        print(f"  {r['amcs']:>3}  {classe}  (setores 2010 {r['setores_2010']}, com entorno "
              f"{r['setores_2010_com_entorno']}; 2022 {r['setores_2022']}, com entorno "
              f"{r['setores_2022_com_entorno']})")


if __name__ == "__main__":
    main()
