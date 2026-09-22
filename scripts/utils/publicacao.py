"""
Propagação da restrição de publicação.

Regra do acervo: **uma saída de estudo herda a restrição MAIS RESTRITIVA entre
todas as camadas que o estudo declara no manifesto.** Basta uma camada com
`pode_publicar=false` para a saída inteira ser `false`.

O motivo é simples: uma saída é feita a partir das camadas de entrada. Se uma
delas não pode ser redistribuída, o produto que a incorpora também não pode —
independentemente de quão transformado esteja. Restrição não se dilui em
processamento.

Dois pontos deliberados:

1. **Lista de camadas vazia devolve `False`**, não `True`. Um estudo que não
   declarou nenhuma camada não provou que pode publicar; o vácuo é tratado
   como "não sei", e "não sei" não autoriza publicação num repositório
   público. Estudo em reconhecimento fica assim até declarar suas entradas.
2. **Camada divergente ou ausente também bloqueia.** Se o acervo mudou desde
   que o estudo fixou o sha256, não dá para afirmar sob qual licença a saída
   foi produzida.

Módulo consultável por qualquer script — é o que `verificar_publicacao.py`
usa para decidir o que barrar no commit.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from scripts.utils import manifesto as mod_manifesto
from scripts.utils import paths


@dataclass(frozen=True)
class Decisao:
    """Resultado de uma consulta de publicação."""

    pode_publicar: bool
    motivo: str
    bloqueios: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.pode_publicar


def _catalogo_camadas() -> dict[str, dict[str, str]]:
    """Índice `id_camada -> linha` do catálogo de camadas."""
    alvo = paths.caminho("catalogo_camadas")
    if not alvo.exists():
        return {}
    with open(alvo, encoding="utf-8") as arquivo:
        return {linha["id_camada"]: linha for linha in csv.DictReader(arquivo)}


def _verdadeiro(texto: str | None) -> bool:
    """Interpreta a coluna booleana do CSV (`true`/`sim`/`1`)."""
    return str(texto or "").strip().lower() in {"true", "sim", "1", "yes"}


def pode_publicar_camada(id_camada: str) -> Decisao:
    """Diz se uma camada do acervo pode ser publicada.

    Args:
        id_camada: id em data/catalogo_camadas.csv.

    Returns:
        `Decisao`. Camada fora do catálogo devolve `False`: o que não está
        catalogado não tem licença conhecida.
    """
    linha = _catalogo_camadas().get(id_camada)
    if linha is None:
        return Decisao(False, f"camada '{id_camada}' não está em data/catalogo_camadas.csv",
                       [id_camada])
    if not _verdadeiro(linha.get("pode_publicar")):
        return Decisao(False, f"camada '{id_camada}' está marcada pode_publicar=false",
                       [id_camada])
    return Decisao(True, f"camada '{id_camada}' pode ser publicada")


def pode_publicar_estudo(estudo: str) -> Decisao:
    """Aplica a regra do mais restritivo sobre o manifesto de um estudo.

    Args:
        estudo: id do diretório em `estudos/` (ex.: "A03_expansao_adensamento").

    Returns:
        `Decisao` com todos os bloqueios encontrados — não só o primeiro, para
        quem for resolver ver o problema inteiro de uma vez.
    """
    caminho = mod_manifesto.caminho_manifesto(estudo)
    try:
        relatorio = mod_manifesto.resolver(caminho)
    except mod_manifesto.ManifestoInvalido as erro:
        return Decisao(False, f"manifesto de '{estudo}' ilegível: {erro}", [estudo])

    if not relatorio.camadas:
        return Decisao(
            False,
            f"estudo '{estudo}' não declara nenhuma camada no manifesto — sem entradas "
            "declaradas não há como afirmar que a saída pode ser publicada",
            [],
        )

    bloqueios: list[str] = []
    for camada in relatorio.camadas:
        if camada.situacao != "ok":
            bloqueios.append(f"{camada.id_camada}: {camada.situacao} — {camada.detalhe}")
        elif not camada.pode_publicar:
            bloqueios.append(f"{camada.id_camada}: pode_publicar=false no catálogo")

    if bloqueios:
        return Decisao(
            False,
            f"estudo '{estudo}': {len(bloqueios)} de {len(relatorio.camadas)} camadas "
            "impedem a publicação (regra do mais restritivo)",
            bloqueios,
        )
    return Decisao(
        True,
        f"estudo '{estudo}': todas as {len(relatorio.camadas)} camadas declaradas "
        "conferem e podem ser publicadas",
    )


def estudo_de(caminho: Path | str) -> str | None:
    """Descobre a qual estudo pertence um caminho sob `estudos/`.

    Returns:
        O id do estudo, ou `None` se o caminho não está sob `estudos/`.
    """
    partes = Path(str(caminho).replace("\\", "/")).parts
    raiz_estudos = Path(paths.valor("paths", "estudos")).name
    if len(partes) >= 2 and partes[0] == raiz_estudos:
        return partes[1]
    return None


def pode_publicar_saida(caminho: Path | str) -> Decisao:
    """Decide sobre um arquivo em `estudos/<id>/saidas/`.

    Args:
        caminho: caminho relativo à raiz do repositório.

    Returns:
        `Decisao` do estudo dono do arquivo.
    """
    estudo = estudo_de(caminho)
    if estudo is None:
        return Decisao(False, f"{caminho} não está sob estudos/<id>/", [str(caminho)])
    return pode_publicar_estudo(estudo)
