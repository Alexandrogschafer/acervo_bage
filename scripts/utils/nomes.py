"""
Padrão de nomes de arquivo do acervo:

    {tema}_{fonte}_{ano-ou-periodo}_{resolucao}.{ext}

Exemplos válidos:
    limite-municipal_ibge_2025_municipal.gpkg
    setores_ibge-censo_2022_setor-censitario.gpkg
    precipitacao_inmet_2010-2025_mensal.csv

Regra estrutural: `_` separa os quatro componentes, então `_` NÃO pode
aparecer dentro de um componente — dentro use `-`. É isso que torna o nome
decomponível de volta sem ambiguidade, e é por isso que existe
`decompor()`: o nome do arquivo é metadado legível por máquina, não enfeite.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

SEPARADOR: str = "_"
# componente: minúsculas, dígitos e hífen; começa e termina em alfanumérico
PADRAO_COMPONENTE: re.Pattern[str] = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PADRAO_EXTENSAO: re.Pattern[str] = re.compile(r"^[a-z0-9]+$")
N_COMPONENTES: int = 4


class NomeInvalido(ValueError):
    """Nome de arquivo fora do padrão do acervo."""


@dataclass(frozen=True)
class NomeArquivo:
    """Os quatro componentes de um nome do acervo, mais a extensão."""

    tema: str
    fonte: str
    periodo: str
    resolucao: str
    extensao: str

    def __str__(self) -> str:
        return (
            SEPARADOR.join((self.tema, self.fonte, self.periodo, self.resolucao))
            + f".{self.extensao}"
        )


def normalizar(componente: str) -> str:
    """Põe um componente no formato aceito: minúsculo, sem acento, com hífen.

    Converte espaços, `_`, `/` e pontuação em `-`, remove acentos e colapsa
    hífens repetidos. Serve para aceitar entrada humana ("Limite Municipal")
    sem que cada script invente sua própria limpeza.

    Args:
        componente: texto livre.

    Returns:
        Componente normalizado.

    Raises:
        NomeInvalido: se nada sobrar depois da normalização.
    """
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", str(componente))
        if unicodedata.category(c) != "Mn"
    )
    limpo = re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")
    limpo = re.sub(r"-{2,}", "-", limpo)
    if not limpo:
        raise NomeInvalido(f"componente vazio depois de normalizar: {componente!r}")
    return limpo


def montar(
    tema: str,
    fonte: str,
    periodo: str,
    resolucao: str,
    extensao: str,
    normalizar_componentes: bool = True,
) -> str:
    """Monta um nome no padrão do acervo.

    Args:
        tema: assunto da camada (ex.: "limite-municipal").
        fonte: origem (ex.: "ibge").
        periodo: ano ou intervalo (ex.: "2025", "2010-2025").
        resolucao: granularidade (ex.: "municipal", "30m", "mensal").
        extensao: sem o ponto (ex.: "gpkg").
        normalizar_componentes: aplica `normalizar()` antes de validar.

    Returns:
        O nome completo do arquivo.

    Raises:
        NomeInvalido: se algum componente não couber no padrão.
    """
    partes = [tema, fonte, periodo, resolucao]
    if normalizar_componentes:
        partes = [normalizar(p) for p in partes]

    rotulos = ("tema", "fonte", "periodo", "resolucao")
    for rotulo, parte in zip(rotulos, partes):
        if not PADRAO_COMPONENTE.fullmatch(parte):
            raise NomeInvalido(
                f"componente '{rotulo}'={parte!r} fora do padrão: use minúsculas, "
                f"dígitos e hífen (o '_' separa componentes e não pode aparecer dentro)"
            )

    ext = str(extensao).lstrip(".").lower()
    if not PADRAO_EXTENSAO.fullmatch(ext):
        raise NomeInvalido(f"extensão inválida: {extensao!r}")

    return SEPARADOR.join(partes) + f".{ext}"


def decompor(nome: str) -> NomeArquivo:
    """Quebra um nome do acervo de volta nos seus componentes.

    Args:
        nome: nome do arquivo (com ou sem diretório).

    Returns:
        O `NomeArquivo` correspondente.

    Raises:
        NomeInvalido: se o nome não estiver no padrão.
    """
    base = str(nome).replace("\\", "/").rsplit("/", 1)[-1]
    if "." not in base:
        raise NomeInvalido(f"nome sem extensão: {nome!r}")

    miolo, _, ext = base.rpartition(".")
    partes = miolo.split(SEPARADOR)
    if len(partes) != N_COMPONENTES:
        raise NomeInvalido(
            f"nome {nome!r} tem {len(partes)} componente(s), esperado {N_COMPONENTES}: "
            f"{{tema}}_{{fonte}}_{{ano-ou-periodo}}_{{resolucao}}.{{ext}}"
        )

    for parte in partes:
        if not PADRAO_COMPONENTE.fullmatch(parte):
            raise NomeInvalido(f"componente {parte!r} fora do padrão em {nome!r}")
    if not PADRAO_EXTENSAO.fullmatch(ext.lower()):
        raise NomeInvalido(f"extensão inválida em {nome!r}")

    return NomeArquivo(*partes, extensao=ext.lower())


def valido(nome: str) -> bool:
    """`True` se o nome está no padrão do acervo — versão booleana de `decompor`."""
    try:
        decompor(nome)
    except NomeInvalido:
        return False
    return True
