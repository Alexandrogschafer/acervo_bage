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
     mudou depois de conferido, a conferência caducou) — com uma exceção: se
     o arquivo foi regravado com outros bytes mas o `sha256_conteudo` do seu
     `.json` irmão (geometria normalizada + atributos + CRS,
     scripts/utils/conteudo.py) bate com o recalculado, o DADO é o mesmo e a
     camada é aceita (aviso). Se o `.json` registra `sha256_conteudo`, ele é
     sempre recalculado e tem de bater;
  6. `tema` é um dos temas de data/acervo/ e `status_conferencia` é válido;
  7. a área de estudo (config/area_estudo.geojson), que é versionada mas não é
     camada do catálogo, segue a MESMA regra de publicação pelo seu `.json`
     irmão: `pode_publicar=true` só com `status_conferencia=conferido`; e o
     sha256 do `.json` bate com o arquivo. Se a camada de origem mudou no
     catálogo desde a derivação, é aviso (regerar com area_estudo.py). Se o
     `.json` registra `sha256_conteudo`, ele é recalculado e tem de bater;
  8. o bloco "--- conferência ---" de observacoes (scripts/utils/metadados.py)
     só existe com `status_conferencia=conferido` — nota de conferência em
     produto pendente é rastro de despromoção mal feita — e tem de estar fechado.
  9. o catálogo de legislação (data/catalogo_legislacao.csv): `id_norma`
     único; `tipo` e `situacao` no domínio; cada `arquivo` existe, tem `.json`
     irmão que aponta para ele com o MESMO sha256 da linha, e o sha256 bate com
     o arquivo em disco; a `fonte_id` do `.json` existe no catálogo de fontes;
     `.json` com `pode_publicar=true` tem licença e fonte que autoriza.

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
from scripts.utils import metadados, paths  # noqa: E402
from scripts.utils.catalogo import conteudo_confere  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402
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
        # (8) nota de conferência
        erro_bloco = _erro_de_bloco(f"camada '{identificador}'", status,
                                    camada.get("observacoes") or "")
        if erro_bloco:
            erros.append(erro_bloco)

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
                conteudo = conteudo_confere(caminho_arquivo)
                if sha_real != sha_registrado and conteudo is True:
                    avisos.append(
                        f"camada '{identificador}': arquivo regravado (sha256 "
                        f"{sha_real[:12]}… ≠ catálogo {sha_registrado[:12]}…), mas o "
                        "sha256_conteudo confere — mesmo dado, aceito."
                    )
                elif sha_real != sha_registrado:
                    motivo = (" e o sha256_conteudo do .json também diverge — o DADO mudou"
                              if conteudo is False else "")
                    erros.append(
                        f"camada '{identificador}': sha256 divergente — catálogo diz "
                        f"{sha_registrado[:12]}…, arquivo tem {sha_real[:12]}…{motivo}. "
                        "O arquivo mudou depois de conferido: reconferir no mapa e "
                        "atualizar o catálogo."
                    )
                elif conteudo is False:
                    erros.append(
                        f"camada '{identificador}': sha256_conteudo do .json irmão não "
                        "confere com o arquivo — metadado errado ou gerado de outro dado."
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


def _erro_de_bloco(rotulo: str, status: str, observacoes: str) -> str | None:
    """Conferência 8: bloco de conferência só em produto conferido, e bem fechado."""
    try:
        bloco = metadados.bloco_conferencia(observacoes)
    except ValueError as erro:
        return f"{rotulo}: {erro}"
    if bloco is not None and status != "conferido":
        return (f"{rotulo}: observacoes tem o bloco '{metadados.MARCADOR_INICIO}' mas "
                f"status_conferencia='{status}' — a despromoção tem de remover a nota")
    return None


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
    elif meta.get("sha256_conteudo") and \
            sha256_conteudo(caminho) != str(meta["sha256_conteudo"]).lower():
        erros.append(
            f"área de estudo {rotulo}: sha256_conteudo do .json não confere com o arquivo"
        )
    erro_bloco = _erro_de_bloco(f"área de estudo {rotulo}", status,
                                str(meta.get("observacoes", "")))
    if erro_bloco:
        erros.append(erro_bloco)

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


COLUNAS_LEGISLACAO: frozenset[str] = frozenset({
    "id_norma", "tipo", "numero", "ano", "data", "ementa", "assunto", "arquivo",
    "sha256", "situacao", "observacoes",
})
TIPOS_NORMA: frozenset[str] = frozenset({"lei", "lei complementar", "decreto"})
# vazio = o texto não diz; situação só se preenche quando o próprio texto a declara
SITUACOES_NORMA: frozenset[str] = frozenset({"", "vigente", "revogada", "alterada"})


def validar_legislacao(caminho: Path, caminho_fontes: Path,
                       raiz: Path) -> tuple[list[str], list[str]]:
    """Confere o catálogo de legislação contra os `.json` irmãos (conferência 9).

    Returns:
        `(erros, avisos)`.
    """
    erros: list[str] = []
    avisos: list[str] = []
    if not caminho.exists():
        return erros, avisos
    linhas = _ler_csv(caminho, COLUNAS_LEGISLACAO, erros)
    fontes: dict[str, dict[str, str]] = {}
    if caminho_fontes.exists():
        with open(caminho_fontes, encoding="utf-8") as arquivo:
            fontes = {f["id_fonte"]: f for f in csv.DictReader(arquivo)}

    vistos: set[str] = set()
    for i, linha in enumerate(linhas, start=2):
        ident = (linha.get("id_norma") or "").strip()
        rotulo = f"catalogo_legislacao.csv linha {i} ('{ident}')"
        if not ident:
            erros.append(f"{rotulo}: sem id_norma")
        elif ident in vistos:
            erros.append(f"{rotulo}: id_norma duplicado")
        vistos.add(ident)
        if (linha.get("tipo") or "").strip() not in TIPOS_NORMA:
            erros.append(f"{rotulo}: tipo '{linha.get('tipo')}' fora de {sorted(TIPOS_NORMA)}")
        if (linha.get("situacao") or "").strip() not in SITUACOES_NORMA:
            erros.append(f"{rotulo}: situacao '{linha.get('situacao')}' fora do domínio")

        relativo = (linha.get("arquivo") or "").strip()
        arquivo = raiz / relativo
        irmao = metadados.caminho_irmao(arquivo)
        if not irmao.is_file():
            erros.append(f"{rotulo}: sem .json irmão ({relativo})")
            continue
        meta = json.loads(irmao.read_text(encoding="utf-8"))
        sha_linha = (linha.get("sha256") or "").strip().lower()
        if meta.get("arquivo") != relativo:
            erros.append(f"{rotulo}: o .json irmão aponta para '{meta.get('arquivo')}'")
        if str(meta.get("sha256", "")).lower() != sha_linha:
            erros.append(f"{rotulo}: sha256 da linha difere do .json irmão")
        if not arquivo.is_file():
            erros.append(f"{rotulo}: arquivo não existe em disco ({relativo})")
        elif sha256_arquivo(arquivo) != sha_linha:
            erros.append(f"{rotulo}: sha256 da linha não bate com o arquivo em disco")

        fonte = fontes.get(str(meta.get("fonte_id", "")))
        if fonte is None:
            erros.append(f"{rotulo}: fonte '{meta.get('fonte_id')}' do .json não existe "
                         "em catalogo_fontes.csv")
        elif meta.get("pode_publicar") is True and (
                not str(meta.get("licenca", "")).strip()
                or not _verdadeiro(fonte.get("autorizacao_fonte"))):
            erros.append(f"{rotulo}: .json com pode_publicar=true sem licença ou com fonte "
                         "sem autorizacao_fonte=true")
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
    parser.add_argument("--legislacao", type=Path,
                        default=paths.caminho("catalogo_legislacao"))
    args = parser.parse_args()

    erros, avisos = validar(args.fontes, args.camadas, args.bib, args.raiz)
    erros_area, avisos_area = validar_area_estudo(args.area_estudo, args.camadas)
    erros += erros_area
    avisos += avisos_area
    erros_leg, avisos_leg = validar_legislacao(args.legislacao, args.fontes, args.raiz)
    erros += erros_leg
    avisos += avisos_leg

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
