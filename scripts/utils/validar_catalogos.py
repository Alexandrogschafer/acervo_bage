"""
Valida os catálogos do acervo antes do commit.

Este repositório é público e o dado pesado não é versionado: o que sustenta a
confiança no acervo são os dois catálogos + a bibliografia. Se eles apontarem
para arquivo que não existe, fonte que não existe, referência que não existe
ou camada publicada sem licença, o acervo está mentindo. Este script é a
barreira contra isso.

Confere:
  1. todo arquivo citado existe (arquivo de produção, arquivo de publicação e
     script responsável);
  2. todo id de fonte citado por uma camada existe em catalogo_fontes.csv;
  3. toda chave bibliográfica citada por uma camada existe em bage.bib;
  4. nenhuma camada PUBLICADA tem fonte sem licença ou sem autorização de
     republicação ("sim"); "a confirmar" não autoriza publicar;
  5. o sha256 registrado da camada bate com o arquivo de publicação em disco
     (regra (vi) do CLAUDE.md: produto derivado só é congelado depois da
     conferência no mapa — se o arquivo mudou, o congelamento caducou).

Saída: rc=0 se tudo passa; rc=1 se há qualquer erro (avisos não reprovam).

Uso:
    python scripts/utils/validar_catalogos.py
    python scripts/utils/validar_catalogos.py --camadas /tmp/camadas_ruim.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.bibliografia.bibtex import chaves as chaves_bib  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

CAMINHO_FONTES = RAIZ_PROJETO / "data" / "catalogo_fontes.csv"
CAMINHO_CAMADAS = RAIZ_PROJETO / "data" / "catalogo_camadas.csv"
CAMINHO_BIB = RAIZ_PROJETO / "bibliografia" / "bage.bib"

COLUNAS_FONTES = {"id", "tema", "nome", "instituicao", "url", "licenca",
                  "autorizacao_para_republicar", "resolucao_ou_escala", "periodo",
                  "script_responsavel", "data_acesso", "sha256", "observacoes"}
COLUNAS_CAMADAS = {"id", "nome", "tema", "arquivo_producao", "arquivo_publicacao",
                   "fontes", "referencias_bibliograficas", "versao", "sha256",
                   "data", "situacao"}

# situações em que a camada está de fato publicada no geoportal — é nelas que
# a exigência de licença + autorização morde
SITUACOES_PUBLICADAS = {"publicada"}

AUTORIZACAO_OK = {"sim"}


def _itens(bruto: str | None) -> list[str]:
    """Quebra uma célula multivalorada ('a; b' ou 'a, b') em lista limpa."""
    if not bruto:
        return []
    return [p.strip() for p in bruto.replace(",", ";").split(";") if p.strip()]


def _ler_csv(caminho: Path, colunas_esperadas: set[str], erros: list[str]) -> list[dict]:
    if not caminho.exists():
        erros.append(f"catálogo não encontrado: {caminho}")
        return []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)
        faltando = colunas_esperadas - set(leitor.fieldnames or [])
        if faltando:
            erros.append(f"{caminho.name}: colunas ausentes: {sorted(faltando)}")
    return linhas


def validar(caminho_fontes: Path, caminho_camadas: Path, caminho_bib: Path,
            raiz: Path) -> tuple[list[str], list[str]]:
    """Roda todas as conferências. Devolve (erros, avisos)."""
    erros: list[str] = []
    avisos: list[str] = []

    fontes = _ler_csv(caminho_fontes, COLUNAS_FONTES, erros)
    camadas = _ler_csv(caminho_camadas, COLUNAS_CAMADAS, erros)

    if caminho_bib.exists():
        chaves = chaves_bib(caminho_bib)
    else:
        chaves = set()
        erros.append(f"bibliografia não encontrada: {caminho_bib}")

    # ---- catálogo de fontes -------------------------------------------------
    por_id: dict[str, dict] = {}
    for i, fonte in enumerate(fontes, start=2):  # linha 1 é o cabeçalho
        identificador = (fonte.get("id") or "").strip()
        if not identificador:
            erros.append(f"catalogo_fontes.csv linha {i}: fonte sem id")
            continue
        if identificador in por_id:
            erros.append(f"catalogo_fontes.csv linha {i}: id duplicado '{identificador}'")
        por_id[identificador] = fonte

        script = (fonte.get("script_responsavel") or "").strip()
        if script and not (raiz / script).exists():
            erros.append(
                f"fonte '{identificador}': script responsável não existe: {script}"
            )
        if not script:
            avisos.append(
                f"fonte '{identificador}': sem script responsável "
                "(ok para consulta pontual; obrigatório se virar insumo de camada)"
            )

    # ---- catálogo de camadas ------------------------------------------------
    vistos: set[str] = set()
    for i, camada in enumerate(camadas, start=2):
        identificador = (camada.get("id") or "").strip()
        if not identificador:
            erros.append(f"catalogo_camadas.csv linha {i}: camada sem id")
            continue
        if identificador in vistos:
            erros.append(f"catalogo_camadas.csv linha {i}: id duplicado '{identificador}'")
        vistos.add(identificador)

        situacao = (camada.get("situacao") or "").strip().lower()
        publicada = situacao in SITUACOES_PUBLICADAS

        # (1) arquivos citados existem
        for coluna in ("arquivo_producao", "arquivo_publicacao"):
            caminho_citado = (camada.get(coluna) or "").strip()
            if not caminho_citado:
                erros.append(f"camada '{identificador}': {coluna} vazio")
                continue
            if not (raiz / caminho_citado).exists():
                erros.append(
                    f"camada '{identificador}': {coluna} não existe em disco: {caminho_citado}"
                )

        # (5) sha256 do arquivo de publicação
        publicacao = (camada.get("arquivo_publicacao") or "").strip()
        sha_registrado = (camada.get("sha256") or "").strip().lower()
        caminho_publicacao = raiz / publicacao if publicacao else None
        if caminho_publicacao and caminho_publicacao.exists():
            if not sha_registrado:
                erros.append(f"camada '{identificador}': sha256 não registrado")
            else:
                sha_real = sha256_arquivo(caminho_publicacao)
                if sha_real != sha_registrado:
                    erros.append(
                        f"camada '{identificador}': sha256 divergente — catálogo diz "
                        f"{sha_registrado[:12]}…, arquivo tem {sha_real[:12]}…. "
                        "O arquivo mudou depois de congelado: reconferir no mapa e "
                        "atualizar o catálogo (regra (vi) do CLAUDE.md)."
                    )

        # (2) ids de fonte existem
        ids_fonte = _itens(camada.get("fontes"))
        if not ids_fonte:
            erros.append(f"camada '{identificador}': nenhuma fonte declarada")
        for id_fonte in ids_fonte:
            if id_fonte not in por_id:
                erros.append(
                    f"camada '{identificador}': fonte '{id_fonte}' não existe em "
                    "catalogo_fontes.csv"
                )
                continue

            # (4) licença e autorização, só para camada publicada
            fonte = por_id[id_fonte]
            licenca = (fonte.get("licenca") or "").strip()
            autorizacao = (fonte.get("autorizacao_para_republicar") or "").strip().lower()
            if publicada:
                if not licenca:
                    erros.append(
                        f"camada '{identificador}' está PUBLICADA mas a fonte "
                        f"'{id_fonte}' não tem licença declarada"
                    )
                if autorizacao not in AUTORIZACAO_OK:
                    erros.append(
                        f"camada '{identificador}' está PUBLICADA mas a fonte "
                        f"'{id_fonte}' tem autorizacao_para_republicar="
                        f"'{autorizacao or '(vazio)'}' — só 'sim' autoriza publicar"
                    )
            elif not licenca or autorizacao not in AUTORIZACAO_OK:
                avisos.append(
                    f"camada '{identificador}' (situação '{situacao}'): fonte "
                    f"'{id_fonte}' ainda sem licença/autorização — resolver antes de publicar"
                )

        # (3) chaves bibliográficas existem
        for chave in _itens(camada.get("referencias_bibliograficas")):
            if chave not in chaves:
                erros.append(
                    f"camada '{identificador}': chave bibliográfica '{chave}' não "
                    f"existe em {caminho_bib.name}"
                )

    return erros, avisos


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida os catálogos do acervo.")
    parser.add_argument("--fontes", type=Path, default=CAMINHO_FONTES)
    parser.add_argument("--camadas", type=Path, default=CAMINHO_CAMADAS)
    parser.add_argument("--bib", type=Path, default=CAMINHO_BIB)
    parser.add_argument("--raiz", type=Path, default=RAIZ_PROJETO,
                        help="Raiz para resolver os caminhos relativos dos catálogos")
    args = parser.parse_args()

    erros, avisos = validar(args.fontes, args.camadas, args.bib, args.raiz)

    for aviso in avisos:
        print(f"AVISO: {aviso}")
    for erro in erros:
        print(f"ERRO:  {erro}")

    if erros:
        print(f"\nFALHOU — {len(erros)} erro(s), {len(avisos)} aviso(s).")
        raise SystemExit(1)
    print(f"\nOK — catálogos consistentes ({len(avisos)} aviso(s)).")


if __name__ == "__main__":
    main()
