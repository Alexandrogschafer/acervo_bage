"""
Leitura e atualização dos catálogos do acervo.

    data/catalogo_fontes.csv    uma linha por fonte (chave: id_fonte)
    data/catalogo_camadas.csv   uma linha por camada (chave: id_camada)

Dois usos:

- `camada_conferida()` resolve o `id_camada` para o arquivo em disco e EXIGE
  que ele seja o registrado: sha256 do arquivo igual ao do catálogo, OU — se o
  arquivo foi regravado com outros bytes — `sha256_conteudo` recalculado igual
  ao gravado no `.json` irmão (scripts/utils/conteudo.py). Um produtor que
  deriva algo de uma camada do acervo não deve usar um dado que mudou desde a
  conferência: o derivado ficaria amarrado a um dado que ninguém conferiu.
- `upsert()` acrescenta ou atualiza linhas pela chave, preservando o
  cabeçalho, a ordem e todas as demais linhas.
"""

from __future__ import annotations

import csv
from pathlib import Path

from scripts.utils import paths
from scripts.utils.hashes import sha256_arquivo


class CamadaIndisponivel(RuntimeError):
    """A camada não está no catálogo, sumiu do disco ou mudou desde o registro."""


def ler(nome: str) -> list[dict[str, str]]:
    """Lê um catálogo pelo nome da chave em `paths:` (ex.: "catalogo_camadas")."""
    with open(paths.caminho(nome), encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def camada_conferida(id_camada: str) -> tuple[dict[str, str], Path]:
    """Devolve a linha do catálogo e o caminho da camada, conferindo o sha256.

    Raises:
        CamadaIndisponivel: se o id não existe, o arquivo não existe ou o
            sha256 do arquivo diverge do registrado.
    """
    linhas = {l["id_camada"]: l for l in ler("catalogo_camadas")}
    if id_camada not in linhas:
        raise CamadaIndisponivel(f"camada '{id_camada}' não está em catalogo_camadas.csv")
    linha = linhas[id_camada]
    arquivo = paths.RAIZ / linha["arquivo"]
    if not arquivo.is_file():
        raise CamadaIndisponivel(f"camada '{id_camada}': arquivo ausente: {linha['arquivo']}")
    real = sha256_arquivo(arquivo)
    if real != linha["sha256"].strip().lower():
        situacao = conteudo_confere(arquivo)
        if situacao is not True:
            motivo = ("e o .json irmão não tem sha256_conteudo" if situacao is None
                      else "e o sha256_conteudo também diverge — o DADO mudou")
            raise CamadaIndisponivel(
                f"camada '{id_camada}': sha256 do arquivo ({real[:12]}…) diverge do "
                f"catálogo ({linha['sha256'][:12]}…) {motivo}. Reconferir antes de "
                "derivar qualquer coisa dele."
            )
    return linha, arquivo


def conteudo_confere(arquivo: Path) -> bool | None:
    """Compara o sha256_conteudo do `.json` irmão com o recalculado do arquivo.

    Returns:
        True se bate, False se diverge, None se o `.json` não registra o hash.
    """
    import json

    from scripts.utils.conteudo import sha256_conteudo

    irmao = arquivo.with_suffix(".json")
    if not irmao.is_file():
        return None
    registrado = json.loads(irmao.read_text(encoding="utf-8")).get("sha256_conteudo")
    if not registrado:
        return None
    return sha256_conteudo(arquivo) == str(registrado).strip().lower()


def upsert(nome: str, chave: str, novas: list[dict[str, str]]) -> tuple[int, int]:
    """Acrescenta ou atualiza linhas por `chave`, preservando cabeçalho e ordem.

    Coluna que não existe no cabeçalho é erro — catálogo não ganha coluna por
    efeito colateral de script.

    Returns:
        `(acrescentadas, atualizadas)`.
    """
    caminho = paths.caminho(nome)
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        campos = list(leitor.fieldnames or [])
        existentes = list(leitor)

    por_chave = {linha[chave]: i for i, linha in enumerate(existentes)}
    acrescentadas = atualizadas = 0
    for nova in novas:
        sobrando = set(nova) - set(campos)
        if sobrando:
            raise ValueError(f"{caminho.name}: colunas não previstas {sorted(sobrando)}")
        completa = {c: str(nova.get(c, "")) for c in campos}
        indice = por_chave.get(completa[chave])
        if indice is None:
            existentes.append(completa)
            por_chave[completa[chave]] = len(existentes) - 1
            acrescentadas += 1
        else:
            existentes[indice] = completa
            atualizadas += 1

    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(existentes)
    return acrescentadas, atualizadas
