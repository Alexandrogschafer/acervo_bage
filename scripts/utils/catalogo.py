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
  cabeçalho, a ordem e todas as demais linhas. Em catálogo com
  `status_conferencia`, aplica a MESMA regra da nota de conferência do `.json`
  irmão (scripts/utils/metadados.py): linha conferida regravada com o mesmo
  dado mantém status, pode_publicar e o bloco `--- conferência ---`; com dado
  novo, perde os três. `upsert()` nunca promove — só `promover()` promove.
"""

from __future__ import annotations

import csv
from pathlib import Path

from scripts.utils import metadados, paths
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


def reconciliar_linha(antiga: dict[str, str] | None, nova: dict[str, str],
                      mesmo_conteudo: bool) -> dict[str, str]:
    """Regra da nota de conferência aplicada a uma linha de catálogo.

    Mesma regra de `metadados.reconciliar()`, com os valores em texto do CSV.
    """
    linha = dict(nova)
    obs = metadados.sem_bloco(linha.get("observacoes", ""))
    if antiga and antiga.get("status_conferencia") == "conferido" and mesmo_conteudo:
        linha["status_conferencia"] = "conferido"
        linha["pode_publicar"] = antiga.get("pode_publicar", "false")
        linha["observacoes"] = metadados.com_bloco(
            obs, metadados.bloco_conferencia(antiga.get("observacoes", "")))
    else:
        if linha.get("status_conferencia") == "conferido" or \
                (antiga and antiga.get("status_conferencia") == "conferido"):
            linha["pode_publicar"] = "false"
        linha["status_conferencia"] = "pendente"
        linha["observacoes"] = obs
    return linha


def _ler_com_campos(nome: str) -> tuple[Path, list[str], list[dict[str, str]]]:
    caminho = paths.caminho(nome)
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        return caminho, list(leitor.fieldnames or []), list(leitor)


def _gravar(caminho: Path, campos: list[str], linhas: list[dict[str, str]]) -> None:
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)


def promover(id_camada: str, nota: str, pode_publicar: bool = True) -> dict[str, str]:
    """Promove a linha de uma camada a conferida, com o bloco de conferência.

    Exige que o arquivo em disco seja o registrado (`camada_conferida()`) e
    que o `.json` irmão já esteja promovido com a MESMA nota — a ordem é
    `metadados.promover()` e depois esta.
    """
    linha, arquivo = camada_conferida(id_camada)
    meta = metadados.ler(arquivo)
    bloco = metadados.montar_bloco(nota)
    if meta.get("status_conferencia") != "conferido" or \
            metadados.bloco_conferencia(meta.get("observacoes", "")) != bloco:
        raise ValueError(f"camada '{id_camada}': promover o .json irmão antes, com a mesma nota")
    caminho, campos, linhas = _ler_com_campos("catalogo_camadas")
    for atual in linhas:
        if atual["id_camada"] == id_camada:
            atual.update(status_conferencia="conferido",
                         pode_publicar="true" if pode_publicar else "false",
                         observacoes=metadados.com_bloco(atual["observacoes"], bloco))
            linha = atual
    _gravar(caminho, campos, linhas)
    return linha


def registrar_regravacao(arquivo: Path | str, sha256: str, mesmo_conteudo: bool) -> str | None:
    """Aplica a regra da nota de conferência à linha da camada cujo arquivo foi regravado.

    Para produtores que não montam a linha inteira do catálogo (ex.:
    `vetor_ibge.py`): atualiza o `sha256` e, pela `reconciliar_linha()`,
    preserva ou despromove a conferência.

    Returns:
        O `id_camada` afetado, ou `None` se nenhuma linha aponta para o arquivo.
    """
    rel = paths.relativo(arquivo)
    caminho, campos, linhas = _ler_com_campos("catalogo_camadas")
    afetado = None
    for i, atual in enumerate(linhas):
        if atual["arquivo"] == rel:
            linhas[i] = reconciliar_linha(atual, {**atual, "sha256": sha256}, mesmo_conteudo)
            afetado = atual["id_camada"]
    if afetado:
        _gravar(caminho, campos, linhas)
    return afetado


def upsert(nome: str, chave: str, novas: list[dict[str, str]],
           mesmo_conteudo: dict[str, bool] | None = None) -> tuple[int, int]:
    """Acrescenta ou atualiza linhas por `chave`, preservando cabeçalho e ordem.

    Coluna que não existe no cabeçalho é erro — catálogo não ganha coluna por
    efeito colateral de script.

    Args:
        mesmo_conteudo: por chave, se o dado novo é o mesmo da linha atual
            (decidido pelo produtor por `sha256_conteudo`, como no `.json`).
            Chave ausente: compara o `sha256` do arquivo.

    Returns:
        `(acrescentadas, atualizadas)`.
    """
    caminho, campos, existentes = _ler_com_campos(nome)
    com_status = "status_conferencia" in campos
    mesmo_conteudo = mesmo_conteudo or {}

    por_chave = {linha[chave]: i for i, linha in enumerate(existentes)}
    acrescentadas = atualizadas = 0
    for nova in novas:
        sobrando = set(nova) - set(campos)
        if sobrando:
            raise ValueError(f"{caminho.name}: colunas não previstas {sorted(sobrando)}")
        completa = {c: str(nova.get(c, "")) for c in campos}
        indice = por_chave.get(completa[chave])
        if com_status:
            antiga = existentes[indice] if indice is not None else None
            mesmo = mesmo_conteudo.get(completa[chave])
            if mesmo is None:
                mesmo = bool(antiga) and antiga.get("sha256", "").strip().lower() == \
                    completa.get("sha256", "").strip().lower()
            completa = reconciliar_linha(antiga, completa, mesmo)
        if indice is None:
            existentes.append(completa)
            por_chave[completa[chave]] = len(existentes) - 1
            acrescentadas += 1
        else:
            existentes[indice] = completa
            atualizadas += 1

    _gravar(caminho, campos, existentes)
    return acrescentadas, atualizadas
