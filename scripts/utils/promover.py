"""
Promove um produto a `status_conferencia=conferido`, com a nota do responsável.

A promoção é o registro de que o responsável conferiu o produto NO MAPA
(docs/convencoes.md § 1, "Regra de promoção"). Este comando é o único caminho
que promove: nenhum script produtor promove, e regravar com dado novo despromove
(`metadados.reconciliar`).

    python scripts/utils/promover.py --id setores_2022 --nota "Conferido no QGIS ..."
    python scripts/utils/promover.py --id config/area_estudo.geojson --nota "..."

`--id` é o `id_camada` de data/catalogo_camadas.csv OU o caminho (relativo à
raiz) de um produto fora do catálogo que tenha `.json` irmão.

Antes de gravar QUALQUER coisa, confere:

1. o produto existe (no catálogo ou em disco) e tem `.json` irmão;
2. o `.json` registra `sha256_conteudo` e ele bate com o recalculado do
   arquivo — é o conferido que se congela; o `sha256` dos bytes também tem de
   bater (arquivo regravado: rodar o script produtor antes, que atualiza o
   `.json` sem perder nada);
3. a linha do catálogo, quando há, registra o mesmo `sha256` do `.json`;
4. toda fonte do produto (`fonte_id`, separadas por `;`) existe em
   data/catalogo_fontes.csv com `autorizacao_fonte=true`, e o `.json` também
   diz `autorizacao_fonte=true`;
5. produto derivado de camada do acervo (`camada_origem` no `.json`): a
   camada de origem está conferida.

`pode_publicar` sai da fonte e nunca é mais permissivo que ela: true só se
TODAS as fontes (e a camada de origem, quando há) têm `pode_publicar=true`.

Grava: `.json` irmão (`metadados.promover`) e, se há, a linha do catálogo
(`catalogo.promover`) — status conferido, pode_publicar e a nota no bloco
"--- conferência ---" de `observacoes`.

Produto já conferido é recusado, a menos de `--substituir-nota` (a nota antiga
é do responsável; trocá-la é decisão explícita).

rc=0 promovido; rc=1 recusado (nada gravado).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import catalogo, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402


class PromocaoRecusada(RuntimeError):
    """A promoção não pode ser feita; nada foi gravado."""


@dataclass(frozen=True)
class Alvo:
    arquivo: Path
    id_camada: str | None      # None: produto fora do catálogo


def _verdadeiro(texto) -> bool:
    return str(texto or "").strip().lower() in {"true", "sim", "1", "yes"}


def resolver(identificador: str) -> Alvo:
    """`id_camada` do catálogo, ou caminho de produto (dentro ou fora do catálogo)."""
    linhas = catalogo.ler("catalogo_camadas")
    por_id = {l["id_camada"]: l for l in linhas}
    if identificador in por_id:
        return Alvo(paths.RAIZ / por_id[identificador]["arquivo"], identificador)
    caminho = (paths.RAIZ / identificador).resolve()
    rel = paths.relativo(caminho)
    linha = next((l for l in linhas if l["arquivo"] == rel), None)
    if linha is not None:
        return Alvo(caminho, linha["id_camada"])
    if caminho.is_file():
        return Alvo(caminho, None)
    raise PromocaoRecusada(
        f"produto inexistente: '{identificador}' não é id_camada de "
        "data/catalogo_camadas.csv nem arquivo em disco"
    )


def conferir(alvo: Alvo, substituir_nota: bool) -> tuple[dict, bool]:
    """Todas as conferências da promoção. Devolve (`.json`, pode_publicar)."""
    rotulo = alvo.id_camada or paths.relativo(alvo.arquivo)
    if not alvo.arquivo.is_file():
        raise PromocaoRecusada(f"produto inexistente: {rotulo} aponta para "
                               f"{paths.relativo(alvo.arquivo)}, que não está em disco")
    if not metadados.caminho_irmao(alvo.arquivo).is_file():
        raise PromocaoRecusada(f"{rotulo}: sem .json irmão — produto sem rastro não se promove")
    meta = metadados.ler(alvo.arquivo)

    if meta.get("status_conferencia") == "conferido" and not substituir_nota:
        raise PromocaoRecusada(f"{rotulo} já está conferido; para trocar a nota do "
                               "responsável, use --substituir-nota")

    # (2) hash: o conferido é o que se congela
    registrado = str(meta.get("sha256_conteudo") or "").lower()
    if not registrado:
        raise PromocaoRecusada(f"{rotulo}: o .json não registra sha256_conteudo — rodar o "
                               "script produtor, que o grava, antes de promover")
    atual = sha256_conteudo(alvo.arquivo)
    if atual != registrado:
        raise PromocaoRecusada(
            f"{rotulo}: hash divergente — sha256_conteudo registrado {registrado[:12]}…, "
            f"arquivo em disco {atual[:12]}…. O dado não é o registrado; não promovo."
        )
    if sha256_arquivo(alvo.arquivo) != str(meta.get("sha256", "")).lower():
        raise PromocaoRecusada(
            f"{rotulo}: hash divergente — o sha256 do arquivo não é o do .json (arquivo "
            "regravado com o mesmo conteúdo). Rodar o script produtor para atualizar o "
            ".json e promover depois."
        )

    # (3) catálogo coerente com o .json
    if alvo.id_camada is not None:
        linha = next(l for l in catalogo.ler("catalogo_camadas")
                     if l["id_camada"] == alvo.id_camada)
        if linha["sha256"].strip().lower() != str(meta["sha256"]).lower():
            raise PromocaoRecusada(
                f"{rotulo}: hash divergente — catálogo registra sha256 "
                f"{linha['sha256'][:12]}…, o .json {str(meta['sha256'])[:12]}…"
            )

    # (4) fontes
    fontes = {l["id_fonte"]: l for l in catalogo.ler("catalogo_fontes")}
    ids_fonte = [f.strip() for f in str(meta.get("fonte_id", "")).split(";") if f.strip()]
    if not ids_fonte:
        raise PromocaoRecusada(f"{rotulo}: .json sem fonte_id")
    publicavel = True
    for id_fonte in ids_fonte:
        fonte = fontes.get(id_fonte)
        if fonte is None:
            raise PromocaoRecusada(f"{rotulo}: fonte '{id_fonte}' não está em "
                                   "data/catalogo_fontes.csv")
        if not _verdadeiro(fonte.get("autorizacao_fonte")):
            raise PromocaoRecusada(
                f"{rotulo}: fonte '{id_fonte}' está com autorizacao_fonte=false — produto "
                "de fonte que não autoriza redistribuição não se promove"
            )
        publicavel = publicavel and _verdadeiro(fonte.get("pode_publicar"))
    if meta.get("autorizacao_fonte") is not True:
        raise PromocaoRecusada(f"{rotulo}: o .json diz autorizacao_fonte=false")

    # (5) camada de origem
    origem = (meta.get("camada_origem") or {}).get("id_camada")
    if origem:
        linha_origem = next((l for l in catalogo.ler("catalogo_camadas")
                             if l["id_camada"] == origem), None)
        if linha_origem is None or linha_origem["status_conferencia"] != "conferido":
            raise PromocaoRecusada(f"{rotulo}: derivado de '{origem}', que não está "
                                   "conferida no catálogo")
        publicavel = publicavel and _verdadeiro(linha_origem.get("pode_publicar"))
    return meta, publicavel


def promover(identificador: str, nota: str, substituir_nota: bool = False) -> dict:
    """Confere tudo e promove. Devolve um resumo.

    Raises:
        PromocaoRecusada: com o motivo; nada foi gravado.
    """
    if not " ".join(str(nota or "").split()):
        raise PromocaoRecusada("--nota vazia: a nota da conferência é obrigatória")
    if metadados.MARCADOR_INICIO in nota or metadados.MARCADOR_FIM in nota:
        raise PromocaoRecusada("a nota não pode conter os marcadores do bloco de conferência")
    alvo = resolver(identificador)
    _, publicavel = conferir(alvo, substituir_nota)

    metadados.promover(alvo.arquivo, nota, pode_publicar=publicavel)
    if alvo.id_camada is not None:
        catalogo.promover(alvo.id_camada, nota, pode_publicar=publicavel)
    return {"produto": alvo.id_camada or paths.relativo(alvo.arquivo),
            "arquivo": paths.relativo(alvo.arquivo),
            "catalogo": alvo.id_camada is not None,
            "pode_publicar": publicavel}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Promove um produto a conferido, com a nota da conferência visual.")
    parser.add_argument("--id", required=True,
                        help="id_camada do catálogo, ou caminho de produto fora do catálogo "
                             "(ex.: config/area_estudo.geojson)")
    parser.add_argument("--nota", required=True,
                        help="texto da conferência do responsável (vai para o bloco "
                             "'--- conferência ---' de observacoes)")
    parser.add_argument("--substituir-nota", action="store_true",
                        help="aceita produto já conferido e troca a nota")
    args = parser.parse_args()
    try:
        r = promover(args.id, args.nota, args.substituir_nota)
    except PromocaoRecusada as erro:
        print(f"RECUSADO: {erro}", file=sys.stderr)
        print("nada foi gravado.", file=sys.stderr)
        raise SystemExit(1) from erro
    print(f"promovido: {r['produto']} ({r['arquivo']})")
    print(f"  status_conferencia = conferido | pode_publicar = {str(r['pode_publicar']).lower()}")
    print(f"  gravado em: .json irmão{' + data/catalogo_camadas.csv' if r['catalogo'] else ''}")


if __name__ == "__main__":
    main()
