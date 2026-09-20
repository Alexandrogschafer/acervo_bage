"""
Hash de arquivos — usado pelo catálogo de fontes, pelo catálogo de camadas e
pelos metadados .json irmãos.

O repositório não versiona dado pesado: o que garante que o arquivo em
data/raw/ da máquina A é o mesmo da máquina B é o sha256 registrado no
catálogo. Por isso o cálculo fica num único lugar.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

TAMANHO_BLOCO = 1024 * 1024  # 1 MiB — arquivos do IBGE chegam a centenas de MB


def sha256_arquivo(caminho: Path) -> str:
    """Retorna o sha256 hexadecimal de um arquivo, lido em blocos."""
    digest = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(TAMANHO_BLOCO), b""):
            digest.update(bloco)
    return digest.hexdigest()
