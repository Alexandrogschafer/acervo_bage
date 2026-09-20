"""
Lê o manifesto de um estudo e o confronta com o acervo.

Cada estudo declara, em `estudos/<id>/manifesto.yaml`, exatamente quais
camadas do acervo consome e em que versão/sha256. O manifesto é um CONTRATO:
diz sobre qual estado do acervo aquele resultado foi produzido.

Este módulo resolve esse contrato contra `data/catalogo_camadas.csv` e contra
os arquivos em disco, e devolve, por camada:

    "ok"          o sha256 fixado bate com o arquivo atual do acervo;
    "divergente"  a camada existe, mas mudou desde que o estudo a fixou;
    "ausente"     o id não está no catálogo, ou o arquivo sumiu do disco.

**Nunca atualiza o manifesto sozinho.** Divergência é aviso, não correção: se
o acervo mudou, quem decide se o estudo continua válido é o responsável, não
um script. Reescrever o sha256 automaticamente apagaria justamente a
evidência de que o resultado foi produzido sobre outro dado.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

from scripts.utils import paths
from scripts.utils.hashes import sha256_arquivo

Situacao = Literal["ok", "divergente", "ausente"]

NOME_MANIFESTO: str = "manifesto.yaml"


class ManifestoInvalido(ValueError):
    """Manifesto ausente, ilegível ou fora do esquema."""


@dataclass(frozen=True)
class CamadaResolvida:
    """Resultado da conferência de uma camada declarada no manifesto."""

    id_camada: str
    situacao: Situacao
    detalhe: str
    versao_manifesto: str = ""
    sha256_manifesto: str = ""
    versao_catalogo: str = ""
    sha256_atual: str = ""
    arquivo: str = ""
    pode_publicar: bool = False


@dataclass(frozen=True)
class RelatorioManifesto:
    """Conferência completa do manifesto de um estudo."""

    estudo: str
    caminho: str
    pergunta: str
    status: str
    referencias_bib: list[str] = field(default_factory=list)
    camadas: list[CamadaResolvida] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """`True` se nenhuma camada está divergente ou ausente."""
        return all(c.situacao == "ok" for c in self.camadas)

    @property
    def problemas(self) -> list[CamadaResolvida]:
        """Só as camadas que não estão "ok"."""
        return [c for c in self.camadas if c.situacao != "ok"]


def caminho_manifesto(estudo: str) -> Path:
    """Caminho do manifesto de um estudo, pelo id do diretório."""
    return paths.caminho("estudos", estudo, NOME_MANIFESTO)


def listar_manifestos() -> list[Path]:
    """Todos os `manifesto.yaml` sob `estudos/`, em ordem alfabética."""
    raiz = paths.caminho("estudos")
    if not raiz.is_dir():
        return []
    return sorted(raiz.glob(f"*/{NOME_MANIFESTO}"))


def ler(caminho: Path | str) -> dict[str, Any]:
    """Lê um manifesto.yaml e confere o esquema mínimo.

    Args:
        caminho: arquivo `manifesto.yaml`.

    Returns:
        O manifesto como dicionário, com `camadas` e `referencias_bib`
        garantidamente listas.

    Raises:
        ManifestoInvalido: se o arquivo não existe, não é YAML, não é mapa ou
            não traz as chaves obrigatórias.
    """
    alvo = Path(caminho)
    if not alvo.exists():
        raise ManifestoInvalido(f"manifesto não encontrado: {paths.relativo(alvo)}")
    try:
        dados = yaml.safe_load(alvo.read_text(encoding="utf-8"))
    except yaml.YAMLError as erro:
        raise ManifestoInvalido(f"{paths.relativo(alvo)} não é YAML válido: {erro}") from erro

    if not isinstance(dados, dict):
        raise ManifestoInvalido(f"{paths.relativo(alvo)} deveria ser um mapa YAML.")

    faltando = {"estudo", "pergunta", "camadas", "status"} - set(dados)
    if faltando:
        raise ManifestoInvalido(
            f"{paths.relativo(alvo)}: chaves obrigatórias ausentes: {sorted(faltando)}"
        )

    dados["camadas"] = dados.get("camadas") or []
    dados["referencias_bib"] = dados.get("referencias_bib") or []
    if not isinstance(dados["camadas"], list):
        raise ManifestoInvalido(f"{paths.relativo(alvo)}: 'camadas' deve ser uma lista.")
    return dados


def _catalogo_camadas() -> dict[str, dict[str, str]]:
    """Índice `id_camada -> linha` de data/catalogo_camadas.csv."""
    alvo = paths.caminho("catalogo_camadas")
    if not alvo.exists():
        return {}
    with open(alvo, encoding="utf-8") as arquivo:
        return {linha["id_camada"]: linha for linha in csv.DictReader(arquivo)}


def resolver(caminho: Path | str) -> RelatorioManifesto:
    """Confere todas as camadas de um manifesto contra o acervo.

    Args:
        caminho: arquivo `manifesto.yaml`.

    Returns:
        O relatório, uma entrada por camada declarada.

    Raises:
        ManifestoInvalido: repassado de `ler()`.
    """
    alvo = Path(caminho)
    dados = ler(alvo)
    catalogo = _catalogo_camadas()
    resultados: list[CamadaResolvida] = []

    for item in dados["camadas"]:
        if not isinstance(item, dict) or "id" not in item:
            resultados.append(CamadaResolvida(
                id_camada=str(item), situacao="ausente",
                detalhe="entrada malformada: esperado {id:, versao:, sha256:}",
            ))
            continue

        id_camada = str(item["id"])
        versao_manifesto = str(item.get("versao", ""))
        sha_manifesto = str(item.get("sha256", "")).strip().lower()

        linha = catalogo.get(id_camada)
        if linha is None:
            resultados.append(CamadaResolvida(
                id_camada=id_camada, situacao="ausente",
                detalhe="id não existe em data/catalogo_camadas.csv",
                versao_manifesto=versao_manifesto, sha256_manifesto=sha_manifesto,
            ))
            continue

        arquivo_rel = linha.get("arquivo", "")
        arquivo_abs = paths.RAIZ / arquivo_rel
        comum = {
            "id_camada": id_camada,
            "versao_manifesto": versao_manifesto,
            "sha256_manifesto": sha_manifesto,
            "versao_catalogo": linha.get("versao", ""),
            "arquivo": arquivo_rel,
            "pode_publicar": str(linha.get("pode_publicar", "")).strip().lower() == "true",
        }

        if not arquivo_abs.is_file():
            resultados.append(CamadaResolvida(
                situacao="ausente",
                detalhe=f"catálogo aponta para {arquivo_rel}, que não está em disco",
                **comum,
            ))
            continue

        sha_atual = sha256_arquivo(arquivo_abs)
        if not sha_manifesto:
            resultados.append(CamadaResolvida(
                situacao="divergente", sha256_atual=sha_atual,
                detalhe="manifesto não fixou sha256 — sem isso o contrato não prova nada",
                **comum,
            ))
        elif sha_atual != sha_manifesto:
            resultados.append(CamadaResolvida(
                situacao="divergente", sha256_atual=sha_atual,
                detalhe=(f"o arquivo do acervo mudou desde que o estudo o fixou "
                         f"(manifesto {sha_manifesto[:12]}…, disco {sha_atual[:12]}…)"),
                **comum,
            ))
        elif versao_manifesto and versao_manifesto != linha.get("versao", ""):
            resultados.append(CamadaResolvida(
                situacao="divergente", sha256_atual=sha_atual,
                detalhe=(f"sha256 bate, mas a versão não: manifesto {versao_manifesto}, "
                         f"catálogo {linha.get('versao')}"),
                **comum,
            ))
        else:
            resultados.append(CamadaResolvida(
                situacao="ok", sha256_atual=sha_atual, detalhe="confere", **comum,
            ))

    return RelatorioManifesto(
        estudo=str(dados["estudo"]),
        caminho=paths.relativo(alvo),
        pergunta=str(dados.get("pergunta", "")),
        status=str(dados.get("status", "")),
        referencias_bib=[str(r) for r in dados["referencias_bib"]],
        camadas=resultados,
    )


def resolver_todos() -> list[RelatorioManifesto]:
    """Resolve o manifesto de todos os estudos."""
    return [resolver(caminho) for caminho in listar_manifestos()]
