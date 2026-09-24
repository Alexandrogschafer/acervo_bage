"""
Registra a legislação municipal de Bagé e os documentos que chegaram junto.

    <origem>/*  ->  data/raw/legislacao/bage/   (+ `.json` irmão de cada arquivo)

A pasta de origem foi fornecida pelo responsável (Plano Diretor, leis
municipais, anexos, material do SICG/IPHAN, em PDF e DOC). O script só COPIA:
não renomeia (o nome original é procedência), não converte, não faz OCR, não
extrai camada de nenhum anexo cartográfico.

TRÊS REGIMES, DECLARADOS ARQUIVO A ARQUIVO
------------------------------------------
Nada aqui presume domínio público pelo simples fato de o arquivo estar na
mesma pasta que uma lei. Cada arquivo está numa das listas abaixo:

  LEI          texto de lei municipal. Não é objeto de proteção autoral
               (Lei 9.610/1998, art. 8º, IV): pode ser publicado.
  PROCESSO     documento de processo legislativo que não é texto de lei
               (relatório técnico de consultoria): licença não declarada.
  IPHAN        material do IPHAN (SICG, dossiê de tombamento, 2009),
               elaborado por equipe contratada: licença não declarada.

Um arquivo da origem que não esteja em nenhuma lista ABORTA a execução:
licença de arquivo novo é decisão do responsável, não do script.

O ANEXO CARTOGRÁFICO É OUTRO REGIME
-----------------------------------
O `pode_publicar=true` de um PDF de lei vale para o DOCUMENTO. Mapa anexo,
quando vier a ser extraído como camada, é base de dados: ganha linha própria
no catálogo de camadas, com `pode_publicar` decidido caso a caso (ver
docs/convencoes.md, "Legislação").

COLISÃO DE `.json` IRMÃO
------------------------
O `.json` irmão troca só a extensão (`metadados.caminho_irmao`). A ficha 2 do
SICG veio em .doc e em .pdf com o mesmo nome base, e os dois gerariam o mesmo
`.json`. O .doc vai para a subpasta `formato_doc/`, com o nome intacto.
Qualquer outra colisão aborta.

Conferências: sha256 da origem antes e depois da cópia, e da cópia contra a
origem; destino já existente com outro conteúdo aborta (não sobrescreve dado).
É idempotente: rodar de novo sobre a mesma origem não muda nada além de
`data_producao`, que vem da data do arquivo e portanto também não muda.

Uso:
    python scripts/acervo/registrar_legislacao.py --origem <pasta> --dry-run
    python scripts/acervo/registrar_legislacao.py --origem <pasta>
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import metadados, paths  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

TEMA = "legislacao"
VERSAO = "recebido-2026-09-22"
FONTE_LEI = "legislacao_municipal_bage"
FONTE_IPHAN = "iphan_sicg_bage_2009"

LICENCA_LEI = "legislação municipal — texto de lei, domínio público"
LICENCA_PROCESSO = (
    "não declarada — relatório técnico de consultoria contratada pela Prefeitura "
    "de Bagé, juntado ao processo legislativo 4413/17 (LC 069/2018); não é texto "
    "de lei e reproduz figuras e fotografias de terceiros"
)
LICENCA_IPHAN = (
    "não declarada — material do IPHAN (SICG e dossiê de tombamento do Conjunto "
    "Histórico e Paisagístico de Bagé, 2009), elaborado por equipe contratada; "
    "sem licença registrada; não é texto de lei"
)

# (licença, autorizacao_fonte, pode_publicar, fonte_id) por regime
REGIMES: dict[str, tuple[str, bool, bool, str]] = {
    "LEI": (LICENCA_LEI, True, True, FONTE_LEI),
    "PROCESSO": (LICENCA_PROCESSO, False, False, FONTE_LEI),
    "IPHAN": (LICENCA_IPHAN, False, False, FONTE_IPHAN),
}

PADRAO_LEI = re.compile(r"^LEI MUNICIPAL .*\.pdf$")
LEI = {
    "Plano Diretor.pdf",
    "plano_diretor_2017.pdf",
    "li_altera_macrozona_2015.pdf",
    "lei_altera_paragrafo_2015.pdf",
    "planmob.pdf",
}
PROCESSO = {"Lc69 - Anexos.pdf"}
IPHAN = {
    "03-MAPA-BAGE_EVOLUÇÃO URBANA.pdf",
    "MAPA SÍNTESE_bag_mapa síntese Model (1)).pdf",
    "M2-01 BAGÉ dez-09.docx",
    "M2-02 BAGE dez-09.doc",
    "Modulo 2 - Ficha 7 - Relatorio Fotografico.doc",
    "SICG - Modulo 1 - Ficha 2 - Contexto Imediato_Bagé _21-12-2009.doc",
    "SICG - Modulo 1 - Ficha 2 - Contexto Imediato_Bagé _21-12-2009.pdf",
    "SICG - Modulo 1 - Ficha 3 - Informacoes sobre a Protecao _16-12-2009.doc",
}
# nome base repetido em dois formatos: o .doc vai para a subpasta
SUBPASTA = {
    "SICG - Modulo 1 - Ficha 2 - Contexto Imediato_Bagé _21-12-2009.doc": "formato_doc",
}

# O que o arquivo É, lido no próprio documento (cabeçalho, capa ou carimbo).
# O nome do arquivo às vezes engana; o registro vale pelo conteúdo.
IDENTIFICACAO: dict[str, str] = {
    "Plano Diretor.pdf": "Lei Complementar nº 025/2007 (PDDUA), texto e anexos 01–11; "
    "anexos cartográficos nas pp. 48–72 e 77–92 (raster embutido, 300 ppi)",
    "plano_diretor_2017.pdf": "Lei Complementar nº 064, de 29/08/2017 (altera a LC 025/2007)",
    "li_altera_macrozona_2015.pdf": "Lei Complementar nº 055, de 23/01/2015",
    "lei_altera_paragrafo_2015.pdf": "Lei Complementar nº 054, de 23/01/2015 (o nome do "
    "arquivo não corresponde ao conteúdo: a lei altera uso rural para urbano)",
    "planmob.pdf": "Lei Complementar nº 069, de 08/01/2018 (PlanMob), texto sem os anexos",
    "Lc69 - Anexos.pdf": "PlanMob — Relatório 1, Pesquisas e Levantamentos (consultoria "
    "Prócidades), protocolado na Câmara em 10/11/2017, processo 4413/17; NÃO são os "
    "anexos normativos I–IV listados no art. 2º da LC 069/2018; mapas nas pp. 148–157",
    "LEI MUNICIPAL Nº 3456_99.pdf": "o cabeçalho diz Lei Municipal nº 3.556, de "
    "23/11/1999; o nome do arquivo diz 3456",
    "03-MAPA-BAGE_EVOLUÇÃO URBANA.pdf": "IPHAN, dossiê de tombamento, prancha 03/18 "
    "'Condicionantes – Evolução Urbana', 1:25.000, out/2009 (SNA Arquitetura); já "
    "processado no REVIA_BG — não reprocessar aqui",
    "MAPA SÍNTESE_bag_mapa síntese Model (1)).pdf": "IPHAN, dossiê de tombamento, "
    "prancha 01 'Mapa Síntese e Graus de Proteção', 2009 (SNA Arquitetura)",
}


def regime(nome: str) -> str:
    """Regime de licença do arquivo; aborta se ele não foi classificado."""
    if PADRAO_LEI.match(nome) or nome in LEI:
        return "LEI"
    if nome in PROCESSO:
        return "PROCESSO"
    if nome in IPHAN:
        return "IPHAN"
    raise SystemExit(
        f"'{nome}' não está classificado (LEI, PROCESSO ou IPHAN). Licença de "
        "arquivo novo é decisão do responsável: acrescente-o a uma das listas."
    )


def _comando(*args: str) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False).stdout
    except FileNotFoundError:
        return ""


def descrever(arquivo: Path) -> str:
    """Formato, páginas e se o PDF tem camada de texto (poppler)."""
    if arquivo.suffix.lower() != ".pdf":
        return f"formato {arquivo.suffix.lstrip('.').upper()} (Word), não convertido"
    info = _comando("pdfinfo", str(arquivo))
    paginas = re.search(r"^Pages:\s+(\d+)", info, re.M)
    criado = re.search(r"^CreationDate:\s+(.+)$", info, re.M)
    produtor = re.search(r"^Producer:\s+(.+)$", info, re.M)
    texto = "".join(_comando("pdftotext", str(arquivo), "-").split())
    if texto:
        camada = f"com camada de texto ({len(texto)} caracteres não brancos)"
    else:
        camada = "SEM camada de texto (imagem ou desenho; sem OCR)"
    partes = [f"PDF, {paginas.group(1) if paginas else '?'} página(s), {camada}"]
    if criado:
        partes.append(f"CreationDate do PDF: {criado.group(1).strip()}")
    if produtor:
        partes.append(f"Producer: {produtor.group(1).strip()}")
    return "; ".join(partes)


def destino_de(nome: str) -> Path:
    base = paths.caminho("raw_legislacao")
    return base / SUBPASTA[nome] / nome if nome in SUBPASTA else base / nome


def conferir_colisoes(nomes: list[str]) -> None:
    vistos: dict[Path, str] = {}
    for nome in nomes:
        irmao = metadados.caminho_irmao(destino_de(nome))
        if irmao in vistos:
            raise SystemExit(f"colisão de .json irmão: '{nome}' e '{vistos[irmao]}'")
        vistos[irmao] = nome


def registrar(origem: Path, dry_run: bool) -> None:
    arquivos = sorted(p for p in origem.iterdir() if p.is_file())
    nomes = [p.name for p in arquivos]
    for nome in nomes:
        regime(nome)
    conferir_colisoes(nomes)

    for arquivo in arquivos:
        nome = arquivo.name
        licenca, autorizacao, publicar, fonte_id = REGIMES[regime(nome)]
        destino = destino_de(nome)
        sha_origem = sha256_arquivo(arquivo)

        if destino.exists() and sha256_arquivo(destino) != sha_origem:
            raise SystemExit(f"{paths.relativo(destino)} existe com outro conteúdo — abortado")
        print(f"[{regime(nome):8}] {paths.relativo(destino)}")
        if dry_run:
            continue

        if not destino.exists():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(arquivo, destino)
        if sha256_arquivo(destino) != sha_origem or sha256_arquivo(arquivo) != sha_origem:
            raise SystemExit(f"sha256 divergente na cópia de '{nome}' — abortado")

        data_arquivo = datetime.fromtimestamp(arquivo.stat().st_mtime).astimezone()
        observacoes = [
            "origem: fornecido pelo responsável (pasta inserir_acervo_bage, 2026-09-22); "
            "arquivo exatamente como veio, nome original preservado",
            f"data do arquivo (mtime na origem): {data_arquivo.isoformat(timespec='seconds')}",
            descrever(destino),
        ]
        if nome in IDENTIFICACAO:
            observacoes.append(f"identificação: {IDENTIFICACAO[nome]}")
        observacoes.append(
            "sha256_conteudo não se aplica (documento, não camada vetorial); a "
            "identidade é o sha256 dos bytes"
        )
        if regime(nome) == "LEI":
            observacoes.append(
                "pode_publicar vale para o documento; anexo cartográfico extraído como "
                "camada é base de dados e tem pode_publicar próprio"
            )

        meta = metadados.montar(
            destino, tema=TEMA, fonte_id=fonte_id, versao=VERSAO, licenca=licenca,
            autorizacao_fonte=autorizacao, pode_publicar=publicar,
            observacoes=". ".join(observacoes) + ".", data_producao=data_arquivo,
        )
        metadados.escrever(destino, meta, sobrescrever=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--origem", type=Path, required=True,
                        help="pasta fornecida pelo responsável")
    parser.add_argument("--dry-run", action="store_true", help="só lista e confere")
    args = parser.parse_args()
    if not args.origem.is_dir():
        raise SystemExit(f"origem não é uma pasta: {args.origem}")
    registrar(args.origem, args.dry_run)


if __name__ == "__main__":
    main()
