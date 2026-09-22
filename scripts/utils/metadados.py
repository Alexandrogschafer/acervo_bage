"""
Gera o `.json` irmão de qualquer produto do acervo.

Todo arquivo de dado — bruto, de acervo, derivado de estudo ou publicado —
tem ao lado um `.json` com o mesmo nome base. Como o dado pesado não é
versionado e o `.json` é, esse arquivo é o ÚNICO rastro público do produto:
de onde veio, sob qual licença, se pode ser publicado, se já foi conferido.

Campos (todos obrigatórios no arquivo gerado, mesmo que vazios):

    arquivo             caminho relativo à raiz do repositório
    tema                tema do acervo (ver data/acervo/<tema>/)
    fonte_id            id em data/catalogo_fontes.csv
    versao              versão do produto
    crs                 CRS do arquivo (vazio para tabular)
    data_producao       ISO 8601 com fuso
    sha256              hash do arquivo
    tamanho_bytes       tamanho do arquivo
    licenca             texto da licença da fonte
    autorizacao_fonte   bool — a fonte autoriza redistribuição?
    pode_publicar       bool — este produto pode ir para o repositório público?
    referencias_bib     lista de chaves de bibliografia/bage.bib
    campos_removidos    lista de campos suprimidos (ex.: dado pessoal)
    status_conferencia  "pendente" | "conferido"
    observacoes         texto livre

Campos OPCIONAIS de procedência, aceitos em qualquer produto e gravados só
quando informados (um produto gerado aqui dentro não os tem):

    repo_origem         repositório de onde o arquivo veio
    commit              commit exato, quando a origem é versionada
    url_origem          URL do repositório/arquivo de origem
    data_commit         data do commit de origem (ISO 8601)
    nome_original       nome do arquivo na origem, quando foi renomeado aqui

Campos OPCIONAIS de derivação e medida, também gravados só quando informados
(o chamador os acrescenta ao dicionário de `montar()` antes de `escrever()`):

    edicao              edição da fonte (ex.: "municipio_2025", "censo_2022")
    camada_origem       {id_camada, arquivo, sha256, versao} da camada do
                        acervo de que o produto foi derivado
    medidas             medidas geométricas, sempre no CRS de produção
    verificacoes        resultado das conferências automáticas do produtor

Existem porque cópia de terceiro só é rastreável se o arquivo disser de qual
ponto exato da origem ele saiu: "veio do repositório X" não permite reencontrar
nada se X mudou depois. O par (repo, commit) permite.

`pode_publicar` é deliberadamente separado de `autorizacao_fonte`: a fonte
pode autorizar redistribuição e mesmo assim o produto não poder ser publicado
(ex.: derivado que reidentifica endereço). Nunca deduza um do outro aqui — a
propagação para saídas de estudo é responsabilidade de `publicacao.py`.

Por segurança, `escrever()` NUNCA sobrescreve um `.json` existente sem
`sobrescrever=True`: metadado apagado por engano é rastro perdido.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Sequence

from scripts.utils import paths
from scripts.utils.hashes import hash_e_tamanho

StatusConferencia = Literal["pendente", "conferido"]

STATUS_VALIDOS: frozenset[str] = frozenset({"pendente", "conferido"})

CAMPOS: tuple[str, ...] = (
    "arquivo", "tema", "fonte_id", "versao", "crs", "data_producao", "sha256",
    "tamanho_bytes", "licenca", "autorizacao_fonte", "pode_publicar",
    "referencias_bib", "campos_removidos", "status_conferencia", "observacoes",
)

# Procedência: opcionais, só aparecem no .json quando informados.
CAMPOS_OPCIONAIS: tuple[str, ...] = (
    "repo_origem", "commit", "url_origem", "data_commit", "nome_original",
    "edicao", "camada_origem", "medidas", "verificacoes",
)


class MetadadoExistente(FileExistsError):
    """O `.json` irmão já existe e `sobrescrever` não foi pedido."""


def caminho_irmao(arquivo: Path | str) -> Path:
    """Caminho do `.json` irmão de um arquivo de dado.

    `x/y/limite.gpkg` -> `x/y/limite.json`.
    """
    return Path(arquivo).with_suffix(".json")


def montar(
    arquivo: Path | str,
    tema: str,
    fonte_id: str,
    versao: str,
    licenca: str,
    autorizacao_fonte: bool,
    pode_publicar: bool,
    crs: str = "",
    referencias_bib: Sequence[str] | None = None,
    campos_removidos: Sequence[str] | None = None,
    status_conferencia: StatusConferencia = "pendente",
    observacoes: str = "",
    data_producao: datetime | None = None,
    repo_origem: str | None = None,
    commit: str | None = None,
    url_origem: str | None = None,
    data_commit: str | None = None,
    nome_original: str | None = None,
) -> dict[str, Any]:
    """Monta o dicionário de metadados de um produto, lendo hash e tamanho do disco.

    Args:
        arquivo: produto já gravado em disco (precisa existir: hash e tamanho
            saem dele, não de parâmetro — parâmetro mente, arquivo não).
        tema: tema do acervo.
        fonte_id: id da fonte em data/catalogo_fontes.csv.
        versao: versão do produto.
        licenca: texto da licença.
        autorizacao_fonte: a fonte autoriza redistribuição?
        pode_publicar: este produto pode ir para o repositório público?
        crs: CRS do arquivo; vazio para produto tabular.
        referencias_bib: chaves de bibliografia/bage.bib.
        campos_removidos: campos suprimidos do produto.
        status_conferencia: "pendente" até a conferência visual do responsável.
        observacoes: texto livre.
        data_producao: default = agora, com fuso local.
        repo_origem: repositório de origem, quando é cópia de terceiro.
        commit: commit exato da origem.
        url_origem: URL da origem.
        data_commit: data do commit de origem (ISO 8601).
        nome_original: nome do arquivo na origem, se renomeado aqui.

    Returns:
        Dicionário com os campos de `CAMPOS`, mais os de `CAMPOS_OPCIONAIS`
        que tiverem sido informados.

    Raises:
        FileNotFoundError: se `arquivo` não existe.
        ValueError: se `status_conferencia` for inválido.
    """
    if status_conferencia not in STATUS_VALIDOS:
        raise ValueError(
            f"status_conferencia={status_conferencia!r} inválido; "
            f"use um de {sorted(STATUS_VALIDOS)}"
        )

    sha256, tamanho = hash_e_tamanho(arquivo)
    momento = data_producao or datetime.now(timezone.utc).astimezone()

    procedencia = {
        "repo_origem": repo_origem,
        "commit": commit,
        "url_origem": url_origem,
        "data_commit": data_commit,
        "nome_original": nome_original,
    }

    return {
        "arquivo": paths.relativo(arquivo),
        "tema": str(tema),
        "fonte_id": str(fonte_id),
        "versao": str(versao),
        "crs": str(crs),
        "data_producao": momento.isoformat(),
        "sha256": sha256,
        "tamanho_bytes": tamanho,
        "licenca": str(licenca),
        "autorizacao_fonte": bool(autorizacao_fonte),
        "pode_publicar": bool(pode_publicar),
        "referencias_bib": list(referencias_bib or []),
        "campos_removidos": list(campos_removidos or []),
        "status_conferencia": status_conferencia,
        "observacoes": str(observacoes),
        **{c: str(v) for c, v in procedencia.items() if v is not None},
    }


def escrever(
    arquivo: Path | str,
    metadados: dict[str, Any],
    sobrescrever: bool = False,
) -> Path:
    """Grava o `.json` irmão: UTF-8, indent=2, chaves ordenadas.

    Args:
        arquivo: o produto (não o `.json`).
        metadados: dicionário, normalmente vindo de `montar()`.
        sobrescrever: obrigatório para substituir um `.json` já existente.

    Returns:
        Caminho do `.json` gravado.

    Raises:
        MetadadoExistente: se o `.json` existe e `sobrescrever` é False.
        ValueError: se faltar ou sobrar campo em relação a `CAMPOS`.
    """
    faltando = set(CAMPOS) - set(metadados)
    se_sobrando = set(metadados) - set(CAMPOS) - set(CAMPOS_OPCIONAIS)
    if faltando or se_sobrando:
        raise ValueError(
            f"metadados fora do esquema — faltando: {sorted(faltando)}; "
            f"não previstos: {sorted(se_sobrando)}"
        )

    destino = caminho_irmao(arquivo)
    if destino.exists() and not sobrescrever:
        raise MetadadoExistente(
            f"{paths.relativo(destino)} já existe. Passe sobrescrever=True se a "
            "substituição for intencional — metadado apagado por engano é rastro perdido."
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destino


def ler(arquivo: Path | str) -> dict[str, Any]:
    """Lê o `.json` irmão de um produto.

    Raises:
        FileNotFoundError: se o `.json` não existe.
    """
    destino = caminho_irmao(arquivo)
    if not destino.exists():
        raise FileNotFoundError(f"metadado não encontrado: {paths.relativo(destino)}")
    return json.loads(destino.read_text(encoding="utf-8"))


def gerar(arquivo: Path | str, sobrescrever: bool = False, **campos: Any) -> Path:
    """Atalho: `montar()` + `escrever()` numa chamada."""
    return escrever(arquivo, montar(arquivo, **campos), sobrescrever=sobrescrever)
