"""
A03 — reconhecimento, item 2: soma dos setores × total oficial, por censo,
com urbano e rural (e por distrito, onde o total oficial existe por distrito);
e a busca dos setores de 2010 que estão na malha e não na tabela.

Lê derivados/ (de r00_extrair.py) e o bruto em data/raw/. Escreve
derivados/r02_totais.json.

Grandezas comparadas: cada soma é confrontada com o total oficial DA MESMA
GRANDEZA (população residente × população residente; moradores em DPP ×
moradores em DPP). Misturar as duas foi a origem da diferença "de recorte" de
2000 registrada em docs/ressalvas_censo_bage.md.
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

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.utils import paths  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
BAGE = DERIV / "bage"
PL = DERIV / "planilhas"
CODIGO = paths.codigo_ibge()
TAB = paths.caminho("raw_tabular", "ibge")
VET = paths.caminho("raw_vetor", "ibge")


def num(serie: pd.Series) -> pd.Series:
    """Texto do IBGE -> número ('1.234,5', '1234,5', 'X', vazio)."""
    s = serie.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def ler(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, sep=";", dtype=str, encoding="utf-8")


def urbano(situacao: pd.Series) -> pd.Series:
    """Situação 1-3 urbana, 4-8 rural (2000 e 2010); 'Urbana'/'Rural' (2022)."""
    s = situacao.astype(str).str.strip()
    return s.isin(["1", "2", "3"]) | s.str.lower().str.startswith("urb")


def por_situacao(df: pd.DataFrame, col_sit: str, colunas: dict[str, str]) -> dict:
    u = urbano(df[col_sit])
    out = {}
    for rotulo, col in colunas.items():
        v = num(df[col])
        out[rotulo] = {"total": float(v.sum()), "urbana": float(v[u].sum()),
                       "rural": float(v[~u].sum()), "setores_sem_valor": int(v.isna().sum())}
    return out


def linha_oficial(arquivo: Path, codigo: str) -> list[str]:
    """Linha da planilha oficial cujo último campo é o código geográfico."""
    with open(arquivo, encoding="utf-8") as f:
        for linha in csv.reader(f, delimiter=";"):
            if linha and linha[-1].strip() == codigo:
                return linha
    raise KeyError(f"{codigo} não achado em {arquivo.name}")


def oficial_2010(tabela: str, codigo: str) -> list[float | None]:
    arq = next(PL.glob(f"c2010_tabelas/Tabela_{tabela}__Tabela_*_RS.csv"))
    return [None if c.strip() == "-" else float(c) for c in linha_oficial(arq, codigo)[1:-1]
            if re.fullmatch(r"[-\d.]+", c.strip())]


def totais_2022() -> dict:
    b = ler(BAGE / "c2022" / "Agregados_por_setores_basico.csv")
    d1 = ler(BAGE / "c2022" / "Agregados_por_setores_caracteristicas_domicilio1.csv")
    soma = por_situacao(b, "SITUACAO", {"populacao_V0001": "v0001",
                                        "domicilios_particulares_ocupados_V0007": "v0007",
                                        "domicilios_total_V0002": "v0002"})
    d1 = d1.merge(b[["CD_SETOR", "SITUACAO"]], left_on="CD_setor", right_on="CD_SETOR", how="left")
    soma.update(por_situacao(d1, "SITUACAO", {"dppo_V00001": "V00001"}))
    arq = next(PL.glob("c2022/Populacao_residente_por_situacao_do_domicilio_municipios__*.csv"))
    ofi = None
    with open(arq, encoding="utf-8") as f:
        for linha in csv.reader(f, delimiter=";"):
            if any(c.strip() == CODIGO for c in linha) or any("Bagé" in c for c in linha):
                ofi = linha
                break
    so_basico = sorted(set(b["CD_SETOR"]) - set(d1["CD_setor"]))
    return {"soma_setores": soma, "linha_oficial_populacao": ofi,
            "setores_no_basico": len(b), "setores_nos_demais_temas": len(d1),
            "setores_so_no_basico": [
                {"cd_setor": c, **b.loc[b["CD_SETOR"] == c, ["SITUACAO", "CD_TIPO", "v0001", "v0002", "v0007"]]
                 .iloc[0].to_dict()} for c in so_basico]}


def totais_2010() -> dict:
    b = ler(BAGE / "c2010" / "Basico_RS.csv")
    d2 = ler(BAGE / "c2010" / "Domicilio02_RS.csv")
    d2 = d2.drop(columns=[c for c in d2.columns if c.startswith("Situacao")]).merge(
        b[["Cod_setor", "Situacao_setor"]], on="Cod_setor", how="left")
    soma = por_situacao(b, "Situacao_setor", {"dpp_V001": "V001", "moradores_dpp_V002": "V002"})
    soma.update(por_situacao(d2, "Situacao_setor",
                             {"moradores_particulares_e_coletivos_Domicilio02_V001": "V001"}))
    distritos = {}
    for cod in sorted(b["Cod_distrito"].unique()):
        sub = b[b["Cod_distrito"] == cod]
        sub2 = d2[d2["Cod_setor"].isin(sub["Cod_setor"])]
        p = oficial_2010("4.23.1.1", cod)
        dm = oficial_2010("4.23.5.1", cod)
        distritos[cod] = {
            "nome": sub["Nome_do_distrito"].iloc[0], "setores_na_tabela": len(sub),
            "populacao_soma": float(num(sub2["V001"]).sum()), "populacao_oficial": p[0],
            "dpp_soma": float(num(sub["V001"]).sum()), "dpp_oficial": dm[0],
            "moradores_dpp_soma": float(num(sub["V002"]).sum()), "moradores_dpp_oficial": dm[3],
        }
    return {"soma_setores": soma,
            "oficial_municipio": {"populacao": oficial_2010("4.23.1.1", CODIGO),
                                  "dpp_e_moradores": oficial_2010("4.23.5.1", CODIGO)},
            "por_distrito": distritos, "setores_na_tabela": len(b)}


def totais_2000() -> dict:
    b = ler(next((BAGE / "c2000").glob("Basico_RS__*.csv")))
    p1 = ler(next((BAGE / "c2000").glob("Pessoa1_RS__*.csv")))
    soma = por_situacao(b, "Situacao", {"dpp_Var01": "Var01", "moradores_dpp_Var12": "Var12"})
    soma.update(por_situacao(p1, "Situacao", {"populacao_V1330": "V1330",
                                              "pessoas_dom_particulares_V1331": "V1331",
                                              "pessoas_dpp_V1332": "V1332",
                                              "pessoas_dom_improvisados_V1333": "V1333",
                                              "pessoas_dom_coletivos_V1334": "V1334"}))
    oficial = {}
    for arq, rotulo in (("3102", "populacao_sexo_situacao"), ("3301", "dpp_saneamento")):
        caminho = next(PL.glob(f"c2000_popmun/*{arq}*.csv"))
        oficial[rotulo] = linha_oficial(caminho, CODIGO)
    return {"soma_setores": soma, "oficial": oficial, "setores_na_tabela": len(b)}


def lacuna_2010() -> dict:
    """Setores de Bagé na malha 2010 que não têm linha na tabela; onde aparecem."""
    malha = gpd.read_file(f"zip://{VET / 'censo_2010' / 'rs_setores_censitarios.zip'}",
                          where=f"CD_GEOCODM = '{CODIGO}'")
    tabela = set(ler(BAGE / "c2010" / "Basico_RS.csv")["Cod_setor"].str.strip())
    faltam = sorted(set(malha["CD_GEOCODI"]) - tabela)
    detalhe = malha[malha["CD_GEOCODI"].isin(faltam)][
        ["CD_GEOCODI", "TIPO", "NM_DISTRIT", "CD_GEOCODD"]].to_dict("records")

    ocorrencias: dict[str, list[str]] = {c: [] for c in faltam}

    def procurar(rotulo: str, texto: str) -> None:
        for c in faltam:
            if c in texto:
                ocorrencias[c].append(rotulo)

    # 1) todos os membros do pacote de agregados de 2010 (CSV e planilhas)
    with zipfile.ZipFile(TAB / "censo_2010" / "RS_20260615.zip") as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            nome = info.filename.encode("cp437").decode("cp850", errors="replace")
            dados = z.read(info)
            if nome.lower().endswith(".csv"):
                procurar(f"RS_20260615.zip:{nome}", dados.decode("latin-1"))
            else:
                df = pd.read_excel(io.BytesIO(dados), sheet_name=None, header=None, dtype=str)
                procurar(f"RS_20260615.zip:{nome}", "\n".join(
                    ";".join(map(str, r)) for d in df.values() for r in d.itertuples(index=False)))
    # 2) documentação (Descrição_RS.xls e demais)
    for arq in (PL / "c2010_doc").glob("*.csv"):
        procurar(f"Documentacao:{arq.name}", arq.read_text(encoding="utf-8"))
    for arq in (DERIV / "texto" / "c2010").glob("*.txt"):
        procurar(f"Documentacao:{arq.name}", arq.read_text(encoding="utf-8"))
    # 3) tabelas por município/distrito/bairro (ODS)
    for arq in (PL / "c2010_tabelas").glob("*.csv"):
        procurar(f"rio_grande_do_sul.zip:{arq.name}", arq.read_text(encoding="utf-8"))
    # 4) de/para 2010->2022 do IBGE (divulgação de 2022, mas cita códigos de 2010)
    for arq in (PL / "c2022").glob("Historico_formacao*.csv"):
        procurar(f"Historico_formacao_2010_2022:{arq.name}", arq.read_text(encoding="utf-8"))
    return {"setores_malha": int(len(malha)), "setores_tabela": len(tabela),
            "faltam": detalhe, "ocorrencias": ocorrencias}


def main() -> None:
    resultado = {"2022": totais_2022(), "2010": totais_2010(), "2000": totais_2000(),
                 "lacuna_2010": lacuna_2010()}
    saida = DERIV / "r02_totais.json"
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=str),
                     encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=1, default=str)[:12000])


if __name__ == "__main__":
    main()
