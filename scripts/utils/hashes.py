"""
Hash e tamanho de arquivos.

O acervo não versiona dado pesado: o que garante que o arquivo da máquina A é
o mesmo da máquina B é o sha256 registrado no catálogo e no `.json` irmão. Por
isso o cálculo fica num único lugar, lido em blocos (os arquivos do IBGE
chegam a centenas de MB).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

TAMANHO_BLOCO: int = 1024 * 1024  # 1 MiB


def sha256_arquivo(caminho: Path | str, tamanho_bloco: int = TAMANHO_BLOCO) -> str:
    """Calcula o sha256 de um arquivo, lendo em blocos.

    Args:
        caminho: arquivo a ler.
        tamanho_bloco: bytes por leitura.

    Returns:
        Digest hexadecimal em minúsculas.

    Raises:
        FileNotFoundError: se o arquivo não existe.
    """
    alvo = Path(caminho)
    if not alvo.is_file():
        raise FileNotFoundError(f"arquivo não encontrado para hash: {alvo}")

    digest = hashlib.sha256()
    with open(alvo, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(tamanho_bloco), b""):
            digest.update(bloco)
    return digest.hexdigest()


def tamanho_bytes(caminho: Path | str) -> int:
    """Tamanho do arquivo em bytes.

    Raises:
        FileNotFoundError: se o arquivo não existe.
    """
    alvo = Path(caminho)
    if not alvo.is_file():
        raise FileNotFoundError(f"arquivo não encontrado: {alvo}")
    return alvo.stat().st_size


def hash_e_tamanho(caminho: Path | str) -> tuple[str, int]:
    """Devolve `(sha256, tamanho_bytes)` numa chamada só.

    Conveniência para quem preenche catálogo ou metadado, onde os dois andam
    sempre juntos.
    """
    return sha256_arquivo(caminho), tamanho_bytes(caminho)


def confere(caminho: Path | str, sha256_esperado: str) -> bool:
    """Diz se o arquivo bate com o sha256 esperado (comparação sem caixa)."""
    return sha256_arquivo(caminho) == str(sha256_esperado).strip().lower()
