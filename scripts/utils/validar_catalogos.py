"""
Valida os catálogos do acervo antes do commit.

O repositório é público e o dado pesado não é versionado: o que sustenta a
confiança no acervo são os dois catálogos e a bibliografia. Se apontarem para
arquivo que não existe, fonte que não existe, referência que não existe ou
camada publicável sem licença, o acervo está mentindo sobre si mesmo.

Confere:
  1. todo arquivo citado por uma camada existe em disco;
  2. todo `fonte_id` citado por uma camada existe em catalogo_fontes.csv;
  3. toda chave de `referencias_bib` existe em bibliografia/bage.bib;
  4. nenhuma camada com `pode_publicar=true` tem licença vazia ou fonte sem
     `autorizacao_fonte=true` — restrição da fonte não se dilui na camada;
  5. o sha256 registrado da camada bate com o arquivo em disco (se o arquivo
     mudou depois de conferido, a conferência caducou);
  6. `tema` é um dos temas de data/acervo/ e `status_conferencia` é válido;
  7. a área de estudo (config/area_estudo.geojson), que é versionada mas não é
     camada do catálogo, segue a MESMA regra de publicação pelo seu `.json`
     irmão: `pode_publicar=true` só com `status_conferencia=conferido`; e o
     sha256 do `.json` bate com o arquivo. Se a camada de origem mudou no
     catálogo desde a derivação, é aviso (regerar com area_estudo.py).

Complementa — não substitui — `verificar_publicacao.py`: aquele barra o
commit, este confere a coerência interna dos catálogos.

rc=0 se tudo passa; rc=1 se há erro (avisos não reprovam).

Uso:
    python scripts/utils/validar_catalogos.py
    python scripts/utils/validar_catalogos.py --camadas /tmp/camadas_ruim.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.bibliografia.bibtex import chaves as chaves_bib  # noqa: E402
from scripts.utils import paths  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

COLUNAS_FONTES: frozenset[str] = frozenset({
    "id_fonte", "nome", "instituicao", "url", "data_acesso", "formato",
    "tamanho_bytes", "sha256", "licenca", "autorizacao_fonte", "pode_publicar",
    "observacoes",
})
COLUNAS_CAMADAS: frozenset[str] = frozenset({
    "id_camada", "tema", "arquivo", "fonte_id", "versao", "crs", "data_producao",
    "sha256", "status_conferencia", "referencias_bib", "licenca", "pode_publicar",
    "observacoes",
})

TEMAS_VALIDOS: frozenset[str] = frozenset({
    "limites", "censo", "hidrografia", "viario", "cadastro", "educacao",
    "saude", "ambiental",
})
STATUS_VALIDOS: frozenset[str] = frozenset({"pendente", "conferido"})
VERDADEIRO: frozenset[str] = frozenset({"true", "sim", "1", "yes"})


def _verdadeiro(texto: str | None) -> bool:
    """Interpreta a coluna booleana do CSV."""
    return str(texto or "").strip().lower() in VERDADEIRO


def _itens(bruto: str | None) -> list[str]:
    """Quebra uma célula multivalorada ('a; b' ou 'a, b') em lista limpa."""
    if not bruto:
        return []
    return [p.strip() for p in bruto.replace(",", ";").split(";") if p.strip()]


def _ler_csv(caminho: Path, esperadas: frozenset[str], erros: list[str]) -> list[dict]:
    """Lê um CSV de catálogo e confere as colunas."""
    if not caminho.exists():
        erros.append(f"catálogo não encontrado: {paths.relativo(caminho)}")
        return []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)
        faltando = esperadas - set(leitor.fieldnames or [])
        if faltando:
            erros.append(f"{caminho.name}: colunas ausentes: {sorted(faltando)}")
    return linhas


def validar(
    caminho_fontes: Path,
    caminho_camadas: Path,
    caminho_bib: Path,
    raiz: Path,
) -> tuple[list[str], list[str]]:
    """Roda todas as conferências.

    Returns:
        `(erros, avisos)` — erros reprovam, avisos não.
    """
    erros: list[str] = []
    avisos: list[str] = []

    fontes = _ler_csv(caminho_fontes, COLUNAS_FONTES, erros)
    camadas = _ler_csv(caminho_camadas, COLUNAS_CAMADAS, erros)

    if caminho_bib.exists():
        chaves = chaves_bib(caminho_bib)
    else:
        chaves = set()
        erros.append(f"bibliografia não encontrada: {paths.relativo(caminho_bib)}")

    # ---- fontes ----
    por_id: dict[str, dict] = {}
    for i, fonte in enumerate(fontes, start=2):  # linha 1 é o cabeçalho
        identificador = (fonte.get("id_fonte") or "").strip()
        if not identificador:
            erros.append(f"catalogo_fontes.csv linha {i}: fonte sem id_fonte")
            continue
        if identificador in por_id:
            erros.append(f"catalogo_fontes.csv linha {i}: id_fonte duplicado '{identificador}'")
        por_id[identificador] = fonte

        if _verdadeiro(fonte.get("pode_publicar")) and not _verdadeiro(
            fonte.get("autorizacao_fonte")
        ):
            erros.append(
                f"fonte '{identificador}': pode_publicar=true mas "
                "autorizacao_fonte não é true — a autorização é o que sustenta a permissão"
            )
        if not (fonte.get("licenca") or "").strip():
            avisos.append(f"fonte '{identificador}': sem licença declarada")

    # ---- camadas ----
    vistos: set[str] = set()
    for i, camada in enumerate(camadas, start=2):
        identificador = (camada.get("id_camada") or "").strip()
        if not identificador:
            erros.append(f"catalogo_camadas.csv linha {i}: camada sem id_camada")
            continue
        if identificador in vistos:
            erros.append(f"catalogo_camadas.csv linha {i}: id_camada duplicado '{identificador}'")
        vistos.add(identificador)

        publicavel = _verdadeiro(camada.get("pode_publicar"))

        # (6) vocabulário controlado
        tema = (camada.get("tema") or "").strip()
        if tema not in TEMAS_VALIDOS:
            erros.append(
                f"camada '{identificador}': tema '{tema}' não é um tema do acervo "
                f"{sorted(TEMAS_VALIDOS)}"
            )
        status = (camada.get("status_conferencia") or "").strip()
        if status not in STATUS_VALIDOS:
            erros.append(
                f"camada '{identificador}': status_conferencia '{status}' inválido "
                f"{sorted(STATUS_VALIDOS)}"
            )
        if publicavel and status != "conferido":
            erros.append(
                f"camada '{identificador}': pode_publicar=true com "
                f"status_conferencia='{status}' — só se publica o que foi conferido no mapa"
            )

        # (1) arquivo existe
        arquivo_rel = (camada.get("arquivo") or "").strip()
        caminho_arquivo = raiz / arquivo_rel if arquivo_rel else None
        if not arquivo_rel:
            erros.append(f"camada '{identificador}': coluna 'arquivo' vazia")
        elif not caminho_arquivo.exists():
            erros.append(
                f"camada '{identificador}': arquivo não existe em disco: {arquivo_rel}"
            )

        # (5) sha256
        sha_registrado = (camada.get("sha256") or "").strip().lower()
        if caminho_arquivo and caminho_arquivo.is_file():
            if not sha_registrado:
                erros.append(f"camada '{identificador}': sha256 não registrado")
            else:
                sha_real = sha256_arquivo(caminho_arquivo)
                if sha_real != sha_registrado:
                    erros.append(
                        f"camada '{identificador}': sha256 divergente — catálogo diz "
                        f"{sha_registrado[:12]}…, arquivo tem {sha_real[:12]}…. "
                        "O arquivo mudou depois de conferido: reconferir no mapa e "
                        "atualizar o catálogo."
                    )

        # (2) fonte existe + (4) licença/autorização
        ids_fonte = _itens(camada.get("fonte_id"))
        if not ids_fonte:
            erros.append(f"camada '{identificador}': nenhuma fonte declarada")
        for id_fonte in ids_fonte:
            if id_fonte not in por_id:
                erros.append(
                    f"camada '{identificador}': fonte '{id_fonte}' não existe em "
                    "catalogo_fontes.csv"
                )
                continue
            fonte = por_id[id_fonte]
            if publicavel:
                if not (fonte.get("licenca") or "").strip():
                    erros.append(
                        f"camada '{identificador}' tem pode_publicar=true mas a fonte "
                        f"'{id_fonte}' não tem licença declarada"
                    )
                if not _verdadeiro(fonte.get("autorizacao_fonte")):
                    erros.append(
                        f"camada '{identificador}' tem pode_publicar=true mas a fonte "
                        f"'{id_fonte}' está com autorizacao_fonte=false"
                    )

        if publicavel and not (camada.get("licenca") or "").strip():
            erros.append(
                f"camada '{identificador}' tem pode_publicar=true e licença vazia"
            )

        # (3) chaves bibliográficas
        for chave in _itens(camada.get("referencias_bib")):
            if chave not in chaves:
                erros.append(
                    f"camada '{identificador}': chave bibliográfica '{chave}' não "
                    f"existe em {caminho_bib.name}"
                )

    return erros, avisos


def validar_area_estudo(caminho: Path, caminho_camadas: Path) -> tuple[list[str], list[str]]:
    """Confere a área de estudo pelo seu `.json` irmão (conferência 7).

    Returns:
        `(erros, avisos)`.
    """
    erros: list[str] = []
    avisos: list[str] = []
    rotulo = paths.relativo(caminho)
    meta_caminho = caminho.with_suffix(".json")
    if not caminho.is_file():
        return [f"área de estudo não existe: {rotulo}"], avisos
    if not meta_caminho.is_file():
        return [f"área de estudo sem .json irmão: {paths.relativo(meta_caminho)}"], avisos

    meta = json.loads(meta_caminho.read_text(encoding="utf-8"))
    status = str(meta.get("status_conferencia", "")).strip()
    if status not in STATUS_VALIDOS:
        erros.append(f"área de estudo {rotulo}: status_conferencia '{status}' inválido")
    if meta.get("pode_publicar") is True and status != "conferido":
        erros.append(
            f"área de estudo {rotulo}: pode_publicar=true com "
            f"status_conferencia='{status}' — só se publica o que foi conferido no mapa"
        )
    if str(meta.get("sha256", "")).lower() != sha256_arquivo(caminho):
        erros.append(
            f"área de estudo {rotulo}: sha256 do .json não bate com o arquivo — "
            "regerar com scripts/processamento/area_estudo.py"
        )

    origem = meta.get("camada_origem") or {}
    if origem.get("id_camada") and caminho_camadas.exists():
        with open(caminho_camadas, encoding="utf-8") as arquivo:
            linhas = {l["id_camada"]: l for l in csv.DictReader(arquivo)}
        linha = linhas.get(origem["id_camada"])
        if linha is None:
            avisos.append(
                f"área de estudo {rotulo}: camada de origem '{origem['id_camada']}' "
                "não está mais no catálogo"
            )
        elif linha["sha256"].strip().lower() != str(origem.get("sha256", "")).lower():
            avisos.append(
                f"área de estudo {rotulo}: derivada de '{origem['id_camada']}' com sha256 "
                f"{str(origem.get('sha256'))[:12]}…, mas o catálogo agora tem "
                f"{linha['sha256'][:12]}… — regerar com area_estudo.py"
            )
    return erros, avisos


def main() -> None:
    """Executa a validação e define o código de saída."""
    parser = argparse.ArgumentParser(description="Valida os catálogos do acervo.")
    parser.add_argument("--fontes", type=Path, default=paths.caminho("catalogo_fontes"))
    parser.add_argument("--camadas", type=Path, default=paths.caminho("catalogo_camadas"))
    parser.add_argument("--bib", type=Path, default=paths.caminho("bibliografia_bib"))
    parser.add_argument("--raiz", type=Path, default=paths.RAIZ,
                        help="Raiz para resolver os caminhos relativos dos catálogos")
    parser.add_argument("--area-estudo", type=Path, default=paths.area_estudo(),
                        help="GeoJSON da área de estudo (default: o do config)")
    args = parser.parse_args()

    erros, avisos = validar(args.fontes, args.camadas, args.bib, args.raiz)
    erros_area, avisos_area = validar_area_estudo(args.area_estudo, args.camadas)
    erros += erros_area
    avisos += avisos_area

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
