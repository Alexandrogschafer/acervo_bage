"""
Gera `docs/indice_camadas_estudos.md`: quem consome o quê.

Varre todos os `estudos/*/manifesto.yaml` e monta as duas leituras que
interessam na prática:

  - **camada -> estudos**: antes de mexer numa camada do acervo, ver quem
    quebra;
  - **fonte bruta -> estudos**: o mesmo para o dado bruto de `data/raw/`, que
    os estudos declaram em `fontes_brutas:`;
  - **estudo -> camadas e fontes brutas**: ao retomar um estudo, ver sobre qual
    estado do acervo e de que arquivos brutos ele foi feito.

ARQUIVO GERADO. Não editar à mão — a próxima execução sobrescreve.

Uso:
    python scripts/utils/indice.py
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# executado como script (`python scripts/utils/indice.py`), a raiz do
# repositório não entra no sys.path sozinha
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import manifesto as mod_manifesto  # noqa: E402
from scripts.utils import paths  # noqa: E402

NOME_SAIDA: str = "indice_camadas_estudos.md"

SIMBOLO: dict[str, str] = {"ok": "ok", "divergente": "⚠ divergente", "ausente": "✕ ausente"}


def _celula(texto: str) -> str:
    """Escapa o que quebraria a tabela Markdown."""
    return (str(texto) or "—").replace("|", "\\|").replace("\n", " ").strip() or "—"


def montar(relatorios: list[mod_manifesto.RelatorioManifesto]) -> str:
    """Monta o conteúdo Markdown do índice.

    Args:
        relatorios: um por estudo, vindos de `manifesto.resolver_todos()`.

    Returns:
        O documento inteiro como string.
    """
    agora = datetime.now(timezone.utc).astimezone()
    linhas: list[str] = [
        "# Índice — camadas do acervo × estudos",
        "",
        "> **ARQUIVO GERADO. Não edite à mão.**",
        "> Regere com `python scripts/utils/indice.py`; qualquer edição manual",
        "> é perdida na próxima execução. A fonte são os",
        "> `estudos/*/manifesto.yaml`, resolvidos contra `data/catalogo_camadas.csv`",
        "> (bloco `camadas:`) e `data/catalogo_fontes.csv` + o `.json` irmão de cada",
        "> arquivo (bloco `fontes_brutas:`).",
        "",
        f"- **Gerado em:** {agora.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"- **Estudos encontrados:** {len(relatorios)}",
        "",
        "`camadas:` é produto curado do acervo (`data/catalogo_camadas.csv`);",
        "`fontes_brutas:` é dado bruto em `data/raw/` (`data/catalogo_fontes.csv`).",
        "A diferença está em `docs/convencoes.md`.",
        "",
    ]

    # ---- camada -> estudos ----
    consumo: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for relatorio in relatorios:
        for camada in relatorio.camadas:
            consumo[camada.id_camada].append((relatorio.estudo, camada.situacao))

    linhas += ["## Camada → estudos que a consomem", ""]
    if not consumo:
        linhas += [
            "Nenhuma camada é consumida por estudo nenhum: todos os manifestos estão",
            "com `camadas: []`. É o esperado enquanto os estudos estão em",
            "reconhecimento — a lista se preenche quando cada estudo declarar suas",
            "entradas.",
            "",
        ]
    else:
        linhas += ["| Camada | Estudos | Situação |", "| --- | --- | --- |"]
        for id_camada in sorted(consumo):
            usos = consumo[id_camada]
            estudos = ", ".join(f"`{e}`" for e, _ in usos)
            situacoes = ", ".join(sorted({SIMBOLO.get(s, s) for _, s in usos}))
            linhas.append(f"| `{_celula(id_camada)}` | {estudos} | {situacoes} |")
        linhas.append("")

    # ---- estudo -> camadas ----
    # ---- fonte bruta -> estudos ----
    consumo_bruto: dict[str, list[tuple[str, str]]] = defaultdict(list)
    arquivos_por_fonte: dict[str, set[str]] = defaultdict(set)
    for relatorio in relatorios:
        for fonte in relatorio.fontes_brutas:
            consumo_bruto[fonte.fonte_id].append((relatorio.estudo, fonte.situacao))
            arquivos_por_fonte[fonte.fonte_id].add(fonte.arquivo)

    linhas += ["## Fonte bruta → estudos que a consomem", ""]
    if not consumo_bruto:
        linhas += ["Nenhum estudo declara fonte bruta em `fontes_brutas:`.", ""]
    else:
        linhas += ["| Fonte | Arquivos | Estudos | Situação |", "| --- | ---: | --- | --- |"]
        for id_fonte in sorted(consumo_bruto):
            usos = consumo_bruto[id_fonte]
            estudos = ", ".join(sorted({f"`{e}`" for e, _ in usos}))
            situacoes = ", ".join(sorted({SIMBOLO.get(s, s) for _, s in usos}))
            linhas.append(f"| `{_celula(id_fonte)}` | {len(arquivos_por_fonte[id_fonte])} "
                          f"| {estudos} | {situacoes} |")
        linhas.append("")

    linhas += ["## Estudo → camadas e fontes brutas que consome", ""]
    if not relatorios:
        linhas += ["Nenhum estudo encontrado em `estudos/`.", ""]
    for relatorio in relatorios:
        linhas += [
            f"### `{relatorio.estudo}`",
            "",
            f"- **Manifesto:** `{relatorio.caminho}`",
            f"- **Status:** {_celula(relatorio.status)}",
            f"- **Pergunta:** {_celula(relatorio.pergunta)}",
            f"- **Referências:** "
            + (", ".join(f"`{r}`" for r in relatorio.referencias_bib) or "—"),
            "",
        ]
        linhas += ["**Camadas do acervo**", ""]
        if not relatorio.camadas:
            linhas += ["Nenhuma camada declarada ainda.", ""]
        else:
            linhas += [
                "| Camada | Versão (manifesto) | Situação | Detalhe |",
                "| --- | --- | --- | --- |",
            ]
            for camada in relatorio.camadas:
                linhas.append(
                    f"| `{_celula(camada.id_camada)}` | {_celula(camada.versao_manifesto)} "
                    f"| {SIMBOLO.get(camada.situacao, camada.situacao)} "
                    f"| {_celula(camada.detalhe)} |"
                )
            linhas.append("")

        linhas += ["**Fontes brutas (`data/raw/`)**", ""]
        if not relatorio.fontes_brutas:
            linhas += ["Nenhuma fonte bruta declarada.", ""]
            continue
        linhas += [
            "| Fonte | Arquivo | Versão (manifesto) | Situação | Detalhe |",
            "| --- | --- | --- | --- | --- |",
        ]
        for fonte in relatorio.fontes_brutas:
            linhas.append(
                f"| `{_celula(fonte.fonte_id)}` | `{_celula(fonte.arquivo)}` "
                f"| {_celula(fonte.versao_manifesto)} "
                f"| {SIMBOLO.get(fonte.situacao, fonte.situacao)} "
                f"| {_celula(fonte.detalhe)} |"
            )
        linhas.append("")

    return "\n".join(linhas)


def main() -> None:
    """Gera o índice em `docs/`."""
    parser = argparse.ArgumentParser(description="Gera o índice camadas × estudos.")
    parser.add_argument("--saida", type=Path, default=paths.caminho("docs", NOME_SAIDA))
    args = parser.parse_args()

    relatorios = mod_manifesto.resolver_todos()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(montar(relatorios) + "\n", encoding="utf-8")

    total_camadas = sum(len(r.camadas) for r in relatorios)
    total_fontes = sum(len(r.fontes_brutas) for r in relatorios)
    problemas = sum(len(r.problemas) for r in relatorios)
    problemas_fontes = sum(len(r.problemas_fontes) for r in relatorios)
    print(f"gerado: {paths.relativo(args.saida)}")
    print(f"  estudos: {len(relatorios)} | camadas declaradas: {total_camadas} "
          f"(com problema: {problemas}) | fontes brutas declaradas: {total_fontes} "
          f"(com problema: {problemas_fontes})")


if __name__ == "__main__":
    main()
