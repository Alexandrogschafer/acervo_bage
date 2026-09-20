"""
Gera bibliografia/indice.md a partir de bibliografia/bage.bib.

O índice é uma leitura humana do `.bib` (que é gerado pelo Zotero e não é
feito para ser lido), cruzada com data/catalogo_camadas.csv para mostrar
quais camadas do geoportal citam cada referência.

O cabeçalho registra a data de geração e o **sha256 do .bib de origem**: é
assim que se percebe que o índice ficou defasado sem precisar comparar o
conteúdo linha a linha.

Arquivo GERADO — não editar à mão (regra (vii) do CLAUDE.md).

Uso:
    python scripts/bibliografia/gerar_indice.py
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.bibliografia.bibtex import ler_bib, limpar_latex  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

CAMINHO_BIB = RAIZ_PROJETO / "bibliografia" / "bage.bib"
CAMINHO_INDICE = RAIZ_PROJETO / "bibliografia" / "indice.md"
CAMINHO_CAMADAS = RAIZ_PROJETO / "data" / "catalogo_camadas.csv"

# campos que, na prática, cumprem o papel de "veículo", em ordem de preferência
CAMPOS_VEICULO = ("journal", "journaltitle", "booktitle", "publisher", "institution",
                  "school", "series", "howpublished")


def formatar_autores(bruto: str) -> str:
    """'Sobrenome, Nome and Outro, X' -> 'Sobrenome; Outro' (ou 'et al.')."""
    if not bruto:
        return "—"
    autores = [a.strip() for a in limpar_latex(bruto).split(" and ") if a.strip()]
    sobrenomes = [a.split(",")[0].strip() if "," in a else a.split()[-1] for a in autores]
    if len(sobrenomes) > 3:
        return f"{sobrenomes[0]} et al."
    return "; ".join(sobrenomes)


def camadas_por_chave() -> dict[str, list[str]]:
    """Mapeia chave bibliográfica -> ids de camadas que a citam."""
    ligacoes: dict[str, list[str]] = defaultdict(list)
    if not CAMINHO_CAMADAS.exists():
        return ligacoes
    with open(CAMINHO_CAMADAS, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            for chave in (linha.get("referencias_bibliograficas") or "").split(";"):
                chave = chave.strip()
                if chave:
                    ligacoes[chave].append(linha["id"])
    return ligacoes


def celula(texto: str) -> str:
    """Escapa o que quebraria a tabela Markdown."""
    return (texto or "—").replace("|", "\\|").replace("\n", " ").strip() or "—"


def montar_indice(entradas: list[dict], ligacoes: dict[str, list[str]], sha_bib: str) -> str:
    agora = datetime.now(timezone.utc).astimezone()

    linhas = [
        "# Índice bibliográfico — acervo de Bagé/RS",
        "",
        "> **Arquivo gerado.** Não edite à mão: rode",
        "> `python scripts/bibliografia/gerar_indice.py`.",
        "> A fonte é `bibliografia/bage.bib`, que por sua vez é exportado pelo",
        "> Zotero (Better BibTeX) — ver `bibliografia/README.md`.",
        "",
        f"- **Gerado em:** {agora.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"- **Fonte:** `bibliografia/bage.bib` ({len(entradas)} "
        f"{'entrada' if len(entradas) == 1 else 'entradas'})",
        f"- **sha256 do `.bib`:** `{sha_bib}`",
        "",
        "Se o sha256 acima não bater com o do `bage.bib` atual, este índice está",
        "defasado — regere antes de usar.",
        "",
        "| Chave | Autores | Ano | Título | Veículo | Tema | DOI/URL | Camadas ligadas |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for entrada in sorted(entradas, key=lambda e: (e.get("year", ""), e["chave"])):
        veiculo = next((limpar_latex(entrada[c]) for c in CAMPOS_VEICULO if entrada.get(c)), "")
        doi = entrada.get("doi", "").strip()
        url = entrada.get("url", "").strip()
        if doi:
            referencia = f"[{doi}](https://doi.org/{doi})"
        elif url:
            referencia = f"[link]({url})"
        else:
            referencia = "—"

        camadas = ligacoes.get(entrada["chave"], [])
        linhas.append(
            "| " + " | ".join([
                f"`{entrada['chave']}`",
                celula(formatar_autores(entrada.get("author", ""))),
                celula(entrada.get("year", "")),
                celula(limpar_latex(entrada.get("title", ""))),
                celula(veiculo),
                celula(limpar_latex(entrada.get("keywords", ""))),
                referencia,
                ", ".join(f"`{c}`" for c in camadas) if camadas else "—",
            ]) + " |"
        )

    orfas = sorted(set(ligacoes) - {e["chave"] for e in entradas})
    if orfas:
        linhas += [
            "",
            "## ⚠ Chaves citadas no catálogo que não existem no `.bib`",
            "",
            *[f"- `{c}` (camadas: {', '.join(ligacoes[c])})" for c in orfas],
            "",
            "Isso também faz `scripts/utils/validar_catalogos.py` falhar.",
        ]

    linhas.append("")
    return "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o índice legível da bibliografia.")
    parser.add_argument("--bib", type=Path, default=CAMINHO_BIB)
    parser.add_argument("--saida", type=Path, default=CAMINHO_INDICE)
    args = parser.parse_args()

    if not args.bib.exists():
        raise SystemExit(
            f"{args.bib} não existe. Exporte a coleção 'Bagé' do Zotero "
            "(Better BibTeX) para esse caminho — ver bibliografia/README.md."
        )

    entradas = ler_bib(args.bib)
    conteudo = montar_indice(entradas, camadas_por_chave(), sha256_arquivo(args.bib))
    args.saida.write_text(conteudo, encoding="utf-8")
    print(f"gerado: {args.saida.relative_to(RAIZ_PROJETO)} ({len(entradas)} entradas)")


if __name__ == "__main__":
    main()
