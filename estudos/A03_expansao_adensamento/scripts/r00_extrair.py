"""
A03 — reconhecimento, passo 0: extrai do bruto do Censo o que o reconhecimento
lê, filtrado para o município do config, em estudos/A03_expansao_adensamento/derivados/.

LÊ só data/raw/ (o bruto do IBGE; nada é alterado lá) e ESCREVE só em
derivados/ (fora do git). Idempotente: o que já foi extraído não é refeito.

Planilhas (XLS BIFF8 de 2000 e 2010, XLSX, ODS) são convertidas para CSV com
pandas (leitores xlrd, openpyxl e odfpy, em requirements.txt). CSV de saída:
UTF-8, separador ';', uma por aba (`<arquivo>__<aba>.csv`), grade crua (sem
interpretar cabeçalho, tudo como texto).

Saídas:
    derivados/bage/c2000/<arquivo>.csv    linhas do município (tabelas do universo)
    derivados/bage/c2010/<arquivo>.csv
    derivados/bage/c2022/<arquivo>.csv
    derivados/planilhas/...               planilhas convertidas inteiras (docs, totais)
    derivados/texto/...                   documentação em texto (pdftotext)

Uso:
    python estudos/A03_expansao_adensamento/scripts/r00_extrair.py
"""

from __future__ import annotations

import csv
import io
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from scripts.utils import paths  # noqa: E402

ESTUDO = Path(__file__).resolve().parents[1]
DERIVADOS = ESTUDO / "derivados"
CODIGO = paths.codigo_ibge()
TAB = paths.caminho("raw_tabular", "ibge")
VET = paths.caminho("raw_vetor", "ibge")



def nome_zip(info: zipfile.ZipInfo) -> str:
    """Nome de membro de zip antigo (cp437 gravado como latin-1/cp850)."""
    if info.flag_bits & 0x800:
        return info.filename
    bruto = info.filename.encode("cp437")
    for cod in ("utf-8", "cp850", "latin-1"):
        try:
            return bruto.decode(cod)
        except UnicodeDecodeError:
            continue
    return info.filename


def converter(planilha: Path, destino: Path) -> list[Path]:
    """Converte uma planilha para CSV, uma por aba, grade crua como texto."""
    destino.mkdir(parents=True, exist_ok=True)
    feitos = sorted(destino.glob(f"{planilha.stem}__*.csv"))
    if feitos:
        return feitos
    abas = pd.read_excel(planilha, sheet_name=None, header=None, dtype=str)
    for nome, df in abas.items():
        seguro = "".join(c if c.isalnum() else "_" for c in str(nome))
        df.to_csv(destino / f"{planilha.stem}__{seguro}.csv", sep=";", index=False,
                  header=False, encoding="utf-8")
    return sorted(destino.glob(f"{planilha.stem}__*.csv"))


def filtrar_csv(linhas: io.TextIOBase, destino: Path, coluna_codigo: str,
                separador: str = ";") -> int:
    """Grava o cabeçalho e as linhas cujo código começa com o do município."""
    leitor = csv.reader(linhas, delimiter=separador, quotechar='"')
    cabecalho = next(leitor)
    indice = [c.strip() for c in cabecalho].index(coluna_codigo)
    destino.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(destino, "w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida, delimiter=";")
        escritor.writerow([c.strip() for c in cabecalho])
        for linha in leitor:
            if len(linha) > indice and linha[indice].strip().startswith(CODIGO):
                escritor.writerow(linha)
                n += 1
    return n


def extrair_2022() -> None:
    for arq in sorted((TAB / "censo_2022").glob("Agregados_por_setores_*.zip")):
        destino = DERIVADOS / "bage" / "c2022" / (arq.stem.split("_BR")[0] + ".csv")
        if destino.exists():
            continue
        with zipfile.ZipFile(arq) as z:
            membro = next(i for i in z.infolist() if i.filename.endswith(".csv"))
            with z.open(membro) as bruto:
                texto = io.TextIOWrapper(bruto, encoding="latin-1", newline="")
                cab = texto.readline()
                col = cab.strip().split(";")[0].strip('"')
                n = filtrar_csv(io.StringIO(cab + "".join(
                    l for l in texto if l.startswith(f'"{CODIGO}') or l.startswith(CODIGO)
                )), destino, col)
        print(f"2022 {destino.name}: {n} setores")


def extrair_2010() -> None:
    arq = TAB / "censo_2010" / "RS_20260615.zip"
    with zipfile.ZipFile(arq) as z:
        for info in z.infolist():
            nome = nome_zip(info)
            if "/CSV/" not in nome or not nome.endswith(".csv"):
                continue
            destino = DERIVADOS / "bage" / "c2010" / Path(nome).name
            if destino.exists():
                continue
            with z.open(info) as bruto:
                n = filtrar_csv(io.TextIOWrapper(bruto, encoding="latin-1", newline=""),
                                destino, "Cod_setor")
            print(f"2010 {destino.name}: {n} setores")


def extrair_2000() -> None:
    arq = TAB / "censo_2000" / "Agregado_de_setores_2000_RS.zip"
    pasta = DERIVADOS / "_bruto" / "c2000"
    with zipfile.ZipFile(arq) as z:
        for info in z.infolist():
            nome = nome_zip(info)
            if info.is_dir():
                continue
            alvo = pasta / Path(nome).name
            if not alvo.exists():
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_bytes(z.read(info))
    for xls in sorted(pasta.glob("*")):
        if xls.suffix.lower() != ".xls":
            continue
        destino = DERIVADOS / "bage" / "c2000" / f"{xls.stem}.csv"
        if destino.exists():
            continue
        for csv_inteiro in converter(xls, DERIVADOS / "planilhas" / "c2000"):
            with open(csv_inteiro, encoding="utf-8", newline="") as f:
                cab = f.readline()
                colunas = [c.strip().strip('"') for c in cab.split(";")]
                col = next((c for c in colunas if c.lower().replace(" ", "_") in ("cod_setor", "código_do_setor")), None)
                if col is None:
                    continue
                f.seek(0)
                alvo = DERIVADOS / "bage" / "c2000" / f"{csv_inteiro.stem}.csv"
                n = filtrar_csv(f, alvo, col)
                print(f"2000 {alvo.name}: {n} setores")


def planilhas_e_textos() -> None:
    """Totais oficiais, dicionários, de/para e documentação."""
    pl = DERIVADOS / "planilhas"
    # 2000: totais por município
    for zp in ("PopMun_43_31.zip", "PopMun_43_33.zip"):
        with zipfile.ZipFile(TAB / "censo_2000" / zp) as z:
            for info in z.infolist():
                alvo = DERIVADOS / "_bruto" / "c2000_popmun" / Path(nome_zip(info)).name.strip()
                if not alvo.exists():
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    alvo.write_bytes(z.read(info))
                converter(alvo, pl / "c2000_popmun")
    # 2010: tabelas por município (ODS)
    with zipfile.ZipFile(TAB / "censo_2010" / "rio_grande_do_sul.zip") as z:
        for info in z.infolist():
            alvo = DERIVADOS / "_bruto" / "c2010_tabelas" / nome_zip(info).replace(" ", "_")
            if not alvo.exists():
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_bytes(z.read(info))
            converter(alvo, pl / "c2010_tabelas")
    # 2010: documentação (PDF do layout)
    with zipfile.ZipFile(TAB / "censo_2010" / "doc" / "Documentacao_Agregado_dos_Setores_2010_20231030.zip") as z:
        for info in z.infolist():
            nome = nome_zip(info)
            if nome.lower().endswith(".pdf") or nome.endswith("_RS.xls"):
                alvo = DERIVADOS / "_bruto" / "c2010_doc" / Path(nome).name.replace(" ", "_")
                if not alvo.exists():
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    alvo.write_bytes(z.read(info))
    for pdf in (DERIVADOS / "_bruto" / "c2010_doc").glob("*.pdf"):
        texto(pdf, DERIVADOS / "texto" / "c2010")
    for xls in (DERIVADOS / "_bruto" / "c2010_doc").glob("*.xls"):
        converter(xls, pl / "c2010_doc")
    # 2000: documentação
    for arq in (DERIVADOS / "_bruto" / "c2000").glob("*.pdf"):
        texto(arq, DERIVADOS / "texto" / "c2000")
    for arq in (DERIVADOS / "_bruto" / "c2000").glob("*.txt"):
        destino = DERIVADOS / "texto" / "c2000" / arq.name
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists():
            destino.write_text(arq.read_bytes().decode("cp850", errors="replace"), encoding="utf-8")
    # 2022: dicionários, de/para, totais
    for xl in [TAB / "censo_2022" / "doc" / "dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx",
               TAB / "censo_2022" / "doc" / "Historico_formacao_Setores_Censitarios_2010_2022.xlsx",
               TAB / "censo_2022" / "doc" / "Dicionario_CNEFE_Censo_2022.xls",
               TAB / "censo_2022" / "Populacao_residente_por_situacao_do_domicilio_municipios.xlsx"]:
        converter(xl, pl / "c2022")
    for pdf in (TAB / "censo_2022" / "doc").glob("*.pdf"):
        texto(pdf, DERIVADOS / "texto" / "c2022")


def texto(pdf: Path, destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    alvo = destino / f"{pdf.stem}.txt"
    if not alvo.exists():
        subprocess.run(["pdftotext", "-layout", str(pdf), str(alvo)], check=True)


def main() -> None:
    DERIVADOS.mkdir(exist_ok=True)
    extrair_2022()
    extrair_2010()
    extrair_2000()
    planilhas_e_textos()
    print("ok")


if __name__ == "__main__":
    main()
