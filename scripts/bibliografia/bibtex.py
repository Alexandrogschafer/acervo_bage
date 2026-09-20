"""
Leitor mínimo de BibTeX.

Por que não uma biblioteca: o acervo consome o `.bib` em dois pontos só
(gerar o índice e validar as chaves citadas no catálogo de camadas), e o
arquivo é gerado pelo Better BibTeX — formato regular, sem as
excentricidades que justificariam uma dependência a mais no requirements.

Cobre o que o Better BibTeX emite: entradas `@tipo{chave, campo = {...}}`,
valores entre chaves/aspas/nus, chaves aninhadas, concatenação com `#`
ignorada, comentários de linha iniciados por `%`, e as entradas de serviço
(@comment/@preamble/@string), que são descartadas.
"""

from __future__ import annotations

import re
from pathlib import Path

TIPOS_IGNORADOS = {"comment", "preamble", "string"}

# acentos LaTeX mais comuns no material em português -> caractere Unicode
_ACENTOS = {"'": "́", "`": "̀", "^": "̂", '"': "̈", "~": "̃"}


def _remover_comentarios(texto: str) -> str:
    """Remove linhas de comentário (`%` como primeiro caractere não-branco)."""
    return "\n".join(l for l in texto.splitlines() if not l.lstrip().startswith("%"))


def _ler_valor(texto: str, i: int) -> tuple[str, int]:
    """Lê um valor de campo a partir de `i`; devolve (valor, índice após o valor)."""
    while i < len(texto) and texto[i].isspace():
        i += 1
    if i >= len(texto):
        return "", i

    if texto[i] == "{":
        profundidade, inicio = 0, i
        while i < len(texto):
            if texto[i] == "{":
                profundidade += 1
            elif texto[i] == "}":
                profundidade -= 1
                if profundidade == 0:
                    return texto[inicio + 1:i], i + 1
            i += 1
        raise ValueError("chave '{' não fechada no .bib")

    if texto[i] == '"':
        inicio = i + 1
        i += 1
        while i < len(texto):
            if texto[i] == '"' and texto[i - 1] != "\\":
                return texto[inicio:i], i + 1
            i += 1
        raise ValueError("aspas não fechadas no .bib")

    # valor nu (número ou macro): vai até a vírgula ou o fim da entrada
    inicio = i
    while i < len(texto) and texto[i] not in ",}":
        i += 1
    return texto[inicio:i].strip(), i


def limpar_latex(valor: str) -> str:
    """Converte acentos LaTeX em Unicode e remove as chaves de agrupamento."""
    valor = re.sub(
        r"\{?\\([`'^\"~])\{?([A-Za-z])\}?\}?",
        lambda m: (m.group(2) + _ACENTOS[m.group(1)]),
        valor,
    )
    valor = re.sub(r"\{?\\c\{?([A-Za-z])\}?\}?", lambda m: m.group(1) + "̧", valor)
    valor = valor.replace("\\&", "&").replace("--", "–")
    valor = valor.replace("{", "").replace("}", "")
    import unicodedata

    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", valor).strip())


def ler_bib(caminho: Path) -> list[dict]:
    """Lê um arquivo .bib e devolve [{'tipo','chave', <campos...>}, ...]."""
    texto = _remover_comentarios(caminho.read_text(encoding="utf-8"))
    entradas: list[dict] = []
    i = 0

    while True:
        arroba = texto.find("@", i)
        if arroba == -1:
            break
        casamento = re.match(r"@([A-Za-z]+)\s*\{", texto[arroba:])
        if not casamento:
            i = arroba + 1
            continue

        tipo = casamento.group(1).lower()
        i = arroba + casamento.end()

        if tipo in TIPOS_IGNORADOS:
            # pula o bloco inteiro, contando chaves
            profundidade = 1
            while i < len(texto) and profundidade:
                profundidade += (texto[i] == "{") - (texto[i] == "}")
                i += 1
            continue

        fim_chave = texto.find(",", i)
        if fim_chave == -1:
            break
        entrada = {"tipo": tipo, "chave": texto[i:fim_chave].strip()}
        i = fim_chave + 1

        while i < len(texto):
            while i < len(texto) and (texto[i].isspace() or texto[i] == ","):
                i += 1
            if i < len(texto) and texto[i] == "}":
                i += 1
                break
            nome = re.match(r"([A-Za-z][\w-]*)\s*=", texto[i:])
            if not nome:
                break
            i += nome.end()
            valor, i = _ler_valor(texto, i)
            entrada[nome.group(1).lower()] = valor.strip()

        entradas.append(entrada)

    return entradas


def chaves(caminho: Path) -> set[str]:
    """Só o conjunto de chaves de citação — o que o validador de catálogos usa."""
    return {e["chave"] for e in ler_bib(caminho)}
