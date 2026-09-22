"""
A03 — reconhecimento dos temas de 2022 baixados depois do reconhecimento inicial:
rendimento do responsável, entorno urbanístico (domicílios, moradores, faces) e
favelas e comunidades urbanas (FCU).

Por tema: linhas de Bagé extraídas para derivados/bage/c2022/, dicionários
convertidos para derivados/planilhas/c2022/, cobertura (quantos dos setores da
tabela básica têm linha) e sigilo (setores e células suprimidos, urbano/rural,
mesmos marcadores do § 4). Para FCU: se Bagé aparece, em quantas FCUs, setores,
moradores e domicílios.

LÊ só data/raw/ e derivados/; ESCREVE só em derivados/ (fora do git):
derivados/r06_temas_2022.json.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from scripts.utils import paths  # noqa: E402

ESTUDO = Path(__file__).resolve().parents[1]
DERIV = ESTUDO / "derivados"
BAGE = DERIV / "bage" / "c2022"
PL = DERIV / "planilhas" / "c2022"
TAB = paths.caminho("raw_tabular", "ibge", "censo_2022")
CODIGO = paths.codigo_ibge()

TEMAS = {  # rótulo -> arquivo zip
    "renda_responsavel": "Agregados_por_setores_renda_responsavel_BR_20260508_csv.zip",
    "entorno_domicilios": "Agregados_por_setores_entorno_domicílios_BR.zip",
    "entorno_moradores": "Agregados_por_setores_entorno_moradores_BR.zip",
    "entorno_faces": "Agregados_por_setores_entorno_faces_BR.zip",
}


def extrair(rotulo: str, arquivo: str) -> pd.DataFrame:
    destino = BAGE / f"{rotulo}.csv"
    if not destino.exists():
        with zipfile.ZipFile(TAB / arquivo) as z:
            membro = next(i for i in z.infolist() if i.filename.lower().endswith(".csv"))
            with z.open(membro) as bruto:
                texto = io.TextIOWrapper(bruto, encoding="latin-1", newline="")
                cab = texto.readline()
                linhas = [l for l in texto if l.lstrip('"').startswith(CODIGO)]
        destino.parent.mkdir(parents=True, exist_ok=True)
        leitor = csv.reader(io.StringIO(cab + "".join(linhas)), delimiter=";")
        with open(destino, "w", encoding="utf-8", newline="") as f:
            csv.writer(f, delimiter=";").writerows(leitor)
    return pd.read_csv(destino, sep=";", dtype=str, keep_default_na=False)


def dicionarios() -> dict[str, list[list[str]]]:
    PL.mkdir(parents=True, exist_ok=True)
    fontes = {"renda_responsavel": [TAB / "doc" / "dicionario_de_dados_renda_responsavel_20260508.xlsx"]}
    with zipfile.ZipFile(TAB / "doc" / "dicionarios_de_dados_entorno.zip") as z:
        for nome in z.namelist():
            alvo = DERIV / "_bruto" / "c2022_entorno_doc" / nome
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_bytes(z.read(nome))
            fontes.setdefault("entorno", []).append(alvo)
    saida = {}
    for rotulo, arquivos in fontes.items():
        for arq in arquivos:
            for aba, df in pd.read_excel(arq, sheet_name=None, header=None, dtype=str).items():
                df = df.dropna(how="all")
                df.to_csv(PL / f"{arq.stem}__{aba}.csv", sep=";", index=False, header=False)
                saida[f"{arq.stem}/{aba}"] = df.fillna("").values.tolist()
    return saida


def sigilo(df: pd.DataFrame, col_setor: str, urbanos: pd.Series) -> dict:
    df = df.set_index(df[col_setor].str.strip())
    variaveis = [c for c in df.columns if re.fullmatch(r"[Vv]\d+", c)]
    v = df.reindex(urbanos.index)[variaveis]
    presente = v.notna().all(axis=1) | v.notna().any(axis=1)
    v = v[presente].apply(lambda c: c.astype(str).str.strip())
    u = urbanos[presente]
    marc = {"X": v.eq("X"), "vazio": v.eq(""), ".": v.eq(".")}
    qualquer = marc["X"] | marc["vazio"] | marc["."]
    s = qualquer.any(axis=1)
    return {
        "n_variaveis": len(variaveis),
        "setores_com_linha": int(presente.sum()),
        "setores_sem_linha": sorted(set(urbanos.index) - set(df.index)),
        "setores_com_supressao": int(s.sum()),
        "urbanos_com_supressao": f"{int(s[u].sum())}/{int(u.sum())}",
        "rurais_com_supressao": f"{int(s[~u].sum())}/{int((~u).sum())}",
        "setores_com_todas_suprimidas": int(qualquer.all(axis=1).sum()),
        "celulas_suprimidas_pct": round(100 * float(qualquer.values.mean()), 2) if len(v) else None,
        "por_marcador": {k: int(m.values.sum()) for k, m in marc.items()},
        "variaveis_mais_suprimidas": qualquer.sum().sort_values(ascending=False).head(8).to_dict(),
    }


def favelas(setores_bage: set[str]) -> dict:
    arq = TAB / "FavelaseComunidadesUrbanas2022Setores_20250417.xlsx"
    abas = pd.read_excel(arq, sheet_name=None, header=None, dtype=str)
    out = {"abas": {}}
    for nome, df in abas.items():
        df = df.dropna(how="all")
        df.to_csv(PL / f"{arq.stem}__{nome}.csv", sep=";", index=False, header=False)
        texto = df.fillna("").astype(str)
        tem_mun = texto.apply(lambda c: c.str.contains(CODIGO, regex=False)).any(axis=1)
        tem_nome = texto.apply(lambda c: c.str.contains(r"\bBag[ée]\b", regex=True)).any(axis=1)
        setores_citados = sorted({m for cel in texto.values.ravel()
                                  for m in re.findall(rf"\b{CODIGO}\d{{8}}\b", cel)})
        out["abas"][nome] = {
            "linhas": int(len(df)),
            "cabecalho_provavel": texto.head(6).values.tolist(),
            "linhas_com_codigo_do_municipio": int(tem_mun.sum()),
            "linhas_com_nome_bage": int(tem_nome.sum()),
            "setores_de_bage_citados": setores_citados,
            "setores_citados_fora_da_malha_2022": sorted(set(setores_citados) - setores_bage),
            "amostra_linhas_bage": texto[tem_mun | tem_nome].head(20).values.tolist(),
        }
    return out


def main() -> None:
    basico = pd.read_csv(BAGE / "Agregados_por_setores_basico.csv", sep=";", dtype=str)
    urbanos = pd.Series(basico["SITUACAO"].str.lower().str.startswith("urb").values,
                        index=basico["CD_SETOR"].str.strip())
    resultado = {"setores_na_tabela_basica": int(len(urbanos)), "temas": {}}
    for rotulo, arquivo in TEMAS.items():
        df = extrair(rotulo, arquivo)
        col = df.columns[0]
        resultado["temas"][rotulo] = {"arquivo": arquivo, "coluna_setor": col,
                                       **sigilo(df, col, urbanos)}
    resultado["dicionarios"] = dicionarios()
    resultado["favelas"] = favelas(set(urbanos.index))
    (DERIV / "r06_temas_2022.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    for rotulo, r in resultado["temas"].items():
        print(f"{rotulo:<20} vars {r['n_variaveis']:>3}  com linha {r['setores_com_linha']:>3}/199  "
              f"supressão {r['setores_com_supressao']:>3} (u {r['urbanos_com_supressao']}, "
              f"r {r['rurais_com_supressao']})  todas {r['setores_com_todas_suprimidas']}  "
              f"células {r['celulas_suprimidas_pct']}%  {r['por_marcador']}  "
              f"sem linha: {r['setores_sem_linha']}")
    for aba, f in resultado["favelas"]["abas"].items():
        print(f"FCU aba {aba}: {f['linhas']} linhas; com código de Bagé {f['linhas_com_codigo_do_municipio']}; "
              f"com nome Bagé {f['linhas_com_nome_bage']}; setores de Bagé citados {len(f['setores_de_bage_citados'])}")


if __name__ == "__main__":
    main()
