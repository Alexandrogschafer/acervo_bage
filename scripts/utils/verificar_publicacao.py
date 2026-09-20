"""
Barreira de publicação — roda como hook de pre-commit.

Este repositório é público. O erro que ele existe para evitar não é o commit
feio: é o `git add .` distraído que joga para dentro um arquivo do acervo, um
derivado de estudo ou uma saída cuja licença não permite redistribuição. Uma
vez publicado, o arquivo fica no histórico mesmo depois de removido.

Percorre os arquivos ESTAGIADOS (`git diff --cached --name-only`) e recusa o
commit, nomeando o arquivo e o motivo, quando o caminho:

  (a) consta em data/catalogo_camadas.csv com `pode_publicar=false`;
  (b) está sob data/acervo/, data/externos/ ou estudos/*/derivados/ sem ser
      `.json` — o dado em si nunca é versionado, só o seu rastro;
  (c) está sob estudos/*/saidas/ e o manifesto do estudo resolve para
      `pode_publicar=false` (regra do mais restritivo, scripts/utils/publicacao.py).

Exceções da regra (b): `.gitkeep` e `manifesto.yaml`. São exigidos pelo
contrato do .gitignore (o primeiro mantém o diretório vazio na árvore, o
segundo é o contrato do estudo) e não carregam dado. Sem essa exceção, a
regra (b) e o .gitignore se contradiriam e nenhum commit inicial passaria.

Saída: rc=0 libera o commit; rc=1 recusa.

Uso:
    python scripts/utils/verificar_publicacao.py            # arquivos estagiados
    python scripts/utils/verificar_publicacao.py --arquivos a.gpkg b.json
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import paths  # noqa: E402
from scripts.utils import publicacao  # noqa: E402

# nomes que podem ficar sob as áreas de dado por não conterem dado
ISENTOS: frozenset[str] = frozenset({".gitkeep", "manifesto.yaml"})

# prefixos onde só o rastro (.json) é versionável — regra (b)
PREFIXOS_SO_JSON: tuple[str, ...] = ("data/acervo/", "data/externos/")


@dataclass(frozen=True)
class Recusa:
    """Um arquivo barrado, com a regra que o barrou."""

    arquivo: str
    regra: str
    motivo: str


def arquivos_estagiados() -> list[str]:
    """Caminhos estagiados para commit (adicionados, copiados ou modificados).

    Returns:
        Lista de caminhos relativos à raiz do repositório.
    """
    resultado = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, cwd=paths.RAIZ, check=False,
    )
    if resultado.returncode != 0:
        print(f"aviso: não consegui listar os arquivos estagiados: {resultado.stderr.strip()}",
              file=sys.stderr)
        return []
    return [linha.strip() for linha in resultado.stdout.splitlines() if linha.strip()]


def _camadas_bloqueadas() -> dict[str, str]:
    """Índice `arquivo -> id_camada` das camadas com `pode_publicar=false`."""
    alvo = paths.caminho("catalogo_camadas")
    if not alvo.exists():
        return {}
    bloqueadas: dict[str, str] = {}
    with open(alvo, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            if str(linha.get("pode_publicar", "")).strip().lower() not in {"true", "sim", "1"}:
                caminho = (linha.get("arquivo") or "").strip()
                if caminho:
                    bloqueadas[caminho] = linha.get("id_camada", "")
    return bloqueadas


def _sob(caminho: str, prefixo: str) -> bool:
    """`True` se `caminho` está sob `prefixo` (comparação por barras `/`)."""
    return caminho.replace("\\", "/").startswith(prefixo)


def _sob_estudo(caminho: str, subdir: str) -> bool:
    """`True` se o caminho é `estudos/<id>/<subdir>/...`."""
    partes = caminho.replace("\\", "/").split("/")
    return len(partes) >= 4 and partes[0] == "estudos" and partes[2] == subdir


def verificar(arquivos: list[str]) -> list[Recusa]:
    """Aplica as três regras a uma lista de caminhos.

    Args:
        arquivos: caminhos relativos à raiz do repositório.

    Returns:
        As recusas encontradas — lista vazia significa commit liberado.
    """
    bloqueadas = _camadas_bloqueadas()
    recusas: list[Recusa] = []
    # cache por estudo: resolver manifesto custa hash de arquivo grande
    decisao_por_estudo: dict[str, publicacao.Decisao] = {}

    for arquivo in arquivos:
        normalizado = arquivo.replace("\\", "/")
        nome = Path(normalizado).name

        # (a) camada explicitamente não publicável
        if normalizado in bloqueadas:
            recusas.append(Recusa(
                normalizado, "a",
                f"consta em data/catalogo_camadas.csv como camada "
                f"'{bloqueadas[normalizado]}' com pode_publicar=false",
            ))
            continue

        if nome in ISENTOS:
            continue

        # (b) área de dado: só o .json irmão é versionável
        if any(_sob(normalizado, p) for p in PREFIXOS_SO_JSON) or \
                _sob_estudo(normalizado, "derivados"):
            if not normalizado.endswith(".json"):
                recusas.append(Recusa(
                    normalizado, "b",
                    "está em área de dado (data/acervo/, data/externos/ ou "
                    "estudos/*/derivados/) e não é um .json de metadado — o dado "
                    "não é versionado, só o seu rastro",
                ))
            continue

        # (c) saída de estudo cujo manifesto não autoriza publicar
        if _sob_estudo(normalizado, "saidas"):
            estudo = publicacao.estudo_de(normalizado)
            if estudo is None:
                continue
            if estudo not in decisao_por_estudo:
                decisao_por_estudo[estudo] = publicacao.pode_publicar_estudo(estudo)
            decisao = decisao_por_estudo[estudo]
            if not decisao.pode_publicar:
                recusas.append(Recusa(
                    normalizado, "c",
                    f"saída do estudo '{estudo}', que resolve para pode_publicar=false: "
                    f"{decisao.motivo}",
                ))

    return recusas


def main() -> int:
    """Executa a verificação e devolve o código de saída do hook."""
    parser = argparse.ArgumentParser(description="Barreira de publicação do ACERVO_BAGE.")
    parser.add_argument("--arquivos", nargs="*", default=None,
                        help="Caminhos a verificar (default: os arquivos estagiados)")
    args = parser.parse_args()

    arquivos = args.arquivos if args.arquivos is not None else arquivos_estagiados()
    if not arquivos:
        print("barreira de publicação: nada a verificar.")
        return 0

    recusas = verificar(arquivos)
    if not recusas:
        print(f"barreira de publicação: OK — {len(arquivos)} arquivo(s) liberados.")
        return 0

    print()
    print("=" * 74)
    print("COMMIT RECUSADO PELA BARREIRA DE PUBLICAÇÃO")
    print("=" * 74)
    for recusa in recusas:
        print(f"\n  arquivo: {recusa.arquivo}")
        print(f"  regra:   ({recusa.regra})")
        print(f"  motivo:  {recusa.motivo}")
    print()
    print(f"{len(recusas)} arquivo(s) barrado(s). Para resolver, escolha um:")
    print("  - remova o arquivo do índice:  git restore --staged <arquivo>")
    print("  - versione só o .json irmão dele;")
    print("  - se a publicação for mesmo autorizada, corrija a licença/autorização")
    print("    no catálogo ou o manifesto do estudo — e não o hook.")
    print("  (emergência documentada: git commit --no-verify)")
    print()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
