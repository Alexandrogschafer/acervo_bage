"""
Baixa a malha municipal do IBGE e gera a camada canônica do limite municipal:

    data/acervo/limites/limite-municipal_ibge_{ano}_municipal.gpkg  (camada `limite_municipal`)

A área de estudo (config/area_estudo.geojson) NÃO é mais gravada aqui: ela é
derivada desta camada por `scripts/processamento/area_estudo.py`, em EPSG:4326.

Município, CRS e caminhos vêm todos de `config/config.yaml` via
`scripts/utils/paths.py` — nada fixo neste arquivo.

REGRA DE ORIGEM DO DADO
-----------------------
O download vem exclusivamente do servidor de arquivos do IBGE
(geoftp.ibge.gov.br) e NENHUMA URL é montada por adivinhação: o script parte
da raiz e desce pelas listagens de diretório, conferindo em cada nível que o
nome esperado realmente está listado. Se o IBGE reorganizar a árvore, o
script falha dizendo qual nível sumiu — em vez de baixar silenciosamente um
arquivo errado ou 404. A API de malhas (servicodados.ibge.gov.br) não é
usada aqui de propósito: o produto do geoftp traz os atributos oficiais
(inclusive AREA_KM2, do Áreas Territoriais), que o GeoJSON da API não traz.

Idempotente: o ZIP já baixado não é baixado de novo (a menos de --forcar), e
a conferência é por sha256, não por data de arquivo local.

Parametrizado por código IBGE (default: o do config) — a UF é deduzida dos 2
primeiros dígitos do código, então o script roda para qualquer município do
país sem edição.

Uso:
    python scripts/download/vetor_ibge.py
    python scripts/download/vetor_ibge.py --codigo-ibge 4322400
    python scripts/download/vetor_ibge.py --ano 2024 --forcar
    python scripts/download/vetor_ibge.py --verificar

--verificar NÃO grava nada no repositório: exige o ZIP já baixado, gera o
GeoPackage num diretório temporário do sistema e compara o CONTEÚDO
(sha256_conteudo: geometria normalizada + atributos + CRS, ver
scripts/utils/conteudo.py) com o registrado no `.json` de `limite_municipal`.
O sha256 do arquivo é mostrado só como informação: ele muda com o layout
físico do SQLite sem que o dado mude.

Determinismo: o GeoPackage é gravado com `last_change` fixado no Last-Modified
da malha de origem (como em limites_ibge.py), e só substitui o existente se o
CONTEÚDO mudou — uma camada conferida com o mesmo dado nunca é regravada.

Conferência: a linha de `limite_municipal` no catálogo segue a regra da nota
de conferência (scripts/utils/metadados.py): o mesmo conteúdo preserva
status, pode_publicar e o bloco "--- conferência ---"; dado novo despromove.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import tempfile
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import geopandas as gpd
import pyogrio
import requests

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.utils import medidas, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vetor_ibge")

# tudo vem do config — ver config/config.yaml
CRS_PADRAO = paths.crs_producao()
CODIGO_IBGE_DEFAULT = paths.codigo_ibge()

# Único host autorizado para este script (ver "REGRA DE ORIGEM DO DADO").
HOST_GEOFTP = "https://geoftp.ibge.gov.br/"
# Ponto de partida da navegação: só o primeiro nível é nomeado aqui; todos os
# demais são resolvidos lendo a listagem do nível anterior.
RAIZ_NAVEGACAO = "organizacao_do_territorio/"
CAMINHO_ESPERADO = ["malhas_territoriais/", "malhas_municipais/"]

DIR_RAW_VETOR = paths.caminho("raw_vetor")
DIR_ACERVO_LIMITES = paths.caminho("acervo_limites")

# Códigos de UF do IBGE (2 primeiros dígitos do código municipal) -> sigla,
# que é como os diretórios do geoftp são nomeados. Tabela fechada e estável
# (Divisão Territorial Brasileira); não é hardcode de município.
UF_POR_CODIGO = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP",
    "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB",
    "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
    "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS",
    "51": "MT", "52": "GO", "53": "DF",
}

# Nomes possíveis da coluna de código do município, entre as várias edições
# da malha (o IBGE já usou CD_GEOCODM e CD_GEOCMU antes do CD_MUN atual).
COLUNAS_CODIGO_MUNICIPIO = ("CD_MUN", "CD_GEOCODM", "CD_GEOCMU", "GEOCODIGO")

TIMEOUT = 120


# --------------------------------------------------------------------------
# navegação pelas listagens do geoftp
# --------------------------------------------------------------------------

def listar_diretorio(url: str) -> list[str]:
    """Lê uma listagem de diretório do geoftp e devolve as entradas filhas.

    Descarta links de navegação do Apache (ordenação `?C=`), o link para o
    diretório pai e qualquer link que aponte para fora do host.
    """
    if not url.startswith(HOST_GEOFTP):
        raise RuntimeError(f"URL fora do host autorizado ({HOST_GEOFTP}): {url}")

    resposta = requests.get(url, timeout=TIMEOUT)
    resposta.raise_for_status()

    entradas = []
    for href in re.findall(r'href="([^"]+)"', resposta.text):
        # só entradas relativas (filhos deste diretório): descarta "?C=N;O=D"
        # (ordenação), "/caminho/absoluto" (pai) e "http..." (externos)
        if href.startswith(("?", "/", "http://", "https://", "#")):
            continue
        entradas.append(href)
    return entradas


def entrar(url_pai: str, nome: str) -> str:
    """Desce um nível, exigindo que `nome` esteja listado em `url_pai`."""
    entradas = listar_diretorio(url_pai)
    if nome not in entradas:
        raise RuntimeError(
            f"'{nome}' não está listado em {url_pai}. "
            f"Entradas encontradas: {sorted(entradas)[:20]}"
        )
    logger.info("listagem ok: %s -> %s", url_pai, nome)
    return url_pai + nome


def resolver_url_malha(codigo_ibge: str, ano: str | None) -> tuple[str, str, str]:
    """Navega o geoftp até o ZIP da malha municipal da UF do código informado.

    Retorna (url_do_zip, nome_do_arquivo, ano_da_edicao).
    """
    uf = UF_POR_CODIGO.get(codigo_ibge[:2])
    if uf is None:
        raise RuntimeError(
            f"Código IBGE '{codigo_ibge}' não começa com um código de UF válido."
        )

    url = entrar(HOST_GEOFTP, RAIZ_NAVEGACAO)
    for nivel in CAMINHO_ESPERADO:
        url = entrar(url, nivel)

    # edições disponíveis: 'municipio_2000/' ... 'municipio_2025/'
    edicoes = {}
    for entrada in listar_diretorio(url):
        achado = re.fullmatch(r"municipio_(\d{4})/", entrada)
        if achado:
            edicoes[achado.group(1)] = entrada
    if not edicoes:
        raise RuntimeError(f"Nenhuma edição 'municipio_AAAA/' listada em {url}")

    ano_escolhido = ano or max(edicoes)
    if ano_escolhido not in edicoes:
        raise RuntimeError(
            f"Edição {ano_escolhido} não existe. Disponíveis: {sorted(edicoes)}"
        )
    logger.info("edição da malha: %s (disponíveis: %s)", ano_escolhido, sorted(edicoes))

    url = entrar(url, edicoes[ano_escolhido])
    url = entrar(url, "UFs/")
    url = entrar(url, f"{uf}/")

    # o arquivo de municípios da UF, entre os produtos da pasta (a mesma pasta
    # traz UF, regiões imediatas e intermediárias — não servem aqui)
    candidatos = [
        e for e in listar_diretorio(url)
        if re.fullmatch(rf"{uf}_Municipios_\d{{4}}\.zip", e, flags=re.IGNORECASE)
    ]
    if len(candidatos) != 1:
        raise RuntimeError(
            f"Esperava exatamente 1 arquivo '{uf}_Municipios_AAAA.zip' em {url}, "
            f"achei {candidatos}"
        )
    nome_arquivo = candidatos[0]
    return url + nome_arquivo, nome_arquivo, ano_escolhido


# --------------------------------------------------------------------------
# download idempotente
# --------------------------------------------------------------------------

def baixar(url: str, destino: Path, forcar: bool) -> dict:
    """Baixa `url` para `destino` (streaming) e devolve os metadados da coleta.

    Idempotente: se o destino já existe e `forcar` é False, não rebaixa —
    apenas relê o tamanho/sha256 do arquivo em disco e o Last-Modified da
    origem (HEAD), para o metadado refletir a origem atual.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)

    cabecalho = requests.head(url, timeout=TIMEOUT)
    cabecalho.raise_for_status()
    last_modified = cabecalho.headers.get("Last-Modified")
    tamanho_origem = cabecalho.headers.get("Content-Length")

    if destino.exists() and not forcar:
        logger.info("já existe, não rebaixando: %s (use --forcar)", destino.name)
    else:
        logger.info("baixando %s (%s bytes) -> %s", url, tamanho_origem, destino.name)
        with requests.get(url, stream=True, timeout=TIMEOUT) as resposta:
            resposta.raise_for_status()
            with open(destino, "wb") as saida:
                for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                    saida.write(bloco)

    tamanho_local = destino.stat().st_size
    if tamanho_origem and int(tamanho_origem) != tamanho_local:
        raise RuntimeError(
            f"Download incompleto: origem diz {tamanho_origem} bytes, "
            f"arquivo local tem {tamanho_local}"
        )

    return {
        "url": url,
        "last_modified_origem": last_modified,
        "tamanho_bytes": tamanho_local,
        "sha256": sha256_arquivo(destino),
        "data_acesso": datetime.now(timezone.utc).isoformat(),
    }


def escrever_metadado(caminho_dado: Path, metadados: dict) -> Path:
    """Grava o .json irmão de um arquivo de dado."""
    caminho = caminho_dado.with_suffix(".json")
    caminho.write_text(json.dumps(metadados, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("metadado: %s", caminho.relative_to(RAIZ_PROJETO))
    return caminho


# --------------------------------------------------------------------------
# recorte do município
# --------------------------------------------------------------------------

def recortar_municipio(caminho_zip: Path, codigo_ibge: str) -> gpd.GeoDataFrame:
    """Lê a malha da UF direto do ZIP e devolve só o município pedido."""
    # pyogrio/GDAL leem shapefile dentro de zip sem descompactar
    gdf = gpd.read_file(f"zip://{caminho_zip}")

    coluna = next((c for c in COLUNAS_CODIGO_MUNICIPIO if c in gdf.columns), None)
    if coluna is None:
        raise RuntimeError(
            f"Nenhuma coluna de código municipal em {caminho_zip.name}. "
            f"Colunas: {list(gdf.columns)}"
        )

    municipio = gdf[gdf[coluna].astype(str).str.strip() == codigo_ibge].copy()
    if len(municipio) != 1:
        raise RuntimeError(
            f"Esperava 1 feição para o código {codigo_ibge} na coluna {coluna}, "
            f"achei {len(municipio)}"
        )

    if municipio.crs is None:
        raise RuntimeError("Malha do IBGE veio sem CRS declarado — abortando.")
    logger.info("CRS de origem: %s | colunas: %s", municipio.crs.to_string(), list(municipio.columns))
    return municipio.to_crs(CRS_PADRAO)


def carimbo_gpkg(last_modified: str | None) -> str:
    """`last_change` fixo do GeoPackage: o Last-Modified da malha de origem.

    Mesma técnica de limites_ibge.py: a mesma entrada gera o mesmo carimbo, em
    vez da hora da execução.
    """
    if not last_modified:
        raise RuntimeError("Last-Modified da origem ausente — sem carimbo determinístico.")
    return (parsedate_to_datetime(last_modified).astimezone(timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%S.000Z"))


def gravar_gpkg(municipio: gpd.GeoDataFrame, destino: Path, carimbo: str) -> bool:
    """Grava o GeoPackage com carimbo fixo; devolve False se o existente já tem
    o mesmo CONTEÚDO (sha256_conteudo) — nesse caso o arquivo NÃO é substituído,
    e o sha256 conferido continua valendo."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        novo = Path(tmp) / destino.name
        pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": carimbo})
        try:
            municipio.to_file(novo, driver="GPKG", layer="limite_municipal")
        finally:
            pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": None})
        if destino.exists() and sha256_conteudo(destino) == sha256_conteudo(novo):
            return False
        novo.replace(destino)
    return True


def verificar_sem_gravar(caminho_zip: Path, codigo: str, ano: str) -> None:
    """Gera o gpkg fora do repositório e compara o CONTEÚDO com `limite_municipal`."""
    from scripts.utils import catalogo

    if not caminho_zip.exists():
        raise SystemExit(f"--verificar exige o ZIP já baixado: {paths.relativo(caminho_zip)}")
    linha, conferido = catalogo.camada_conferida("limite_municipal")
    registrado = json.loads(conferido.with_suffix(".json").read_text(encoding="utf-8")) \
        .get("sha256_conteudo")
    referencia = registrado or sha256_conteudo(conferido)

    municipio = recortar_municipio(caminho_zip, codigo)
    with tempfile.TemporaryDirectory(prefix="vetor_ibge_verificar_") as tmp:
        gerado = Path(tmp) / f"limite-municipal_ibge_{ano}_municipal.gpkg"
        municipio.to_file(gerado, driver="GPKG", layer="limite_municipal")
        conteudo_gerado = sha256_conteudo(gerado)
        sha_gerado = sha256_arquivo(gerado)

    print()
    print(f"camada conferida ........ {linha['arquivo']}")
    print(f"sha256_conteudo esperado  {referencia} "
          f"({'do .json irmão' if registrado else 'recalculado do arquivo conferido'})")
    print(f"sha256_conteudo gerado .. {conteudo_gerado}  "
          f"{'IGUAL — mesmo dado' if conteudo_gerado == referencia else 'DIFERENTE — o dado mudou'}")
    print(f"(sha256 do arquivo, só informativo: conferido {linha['sha256'][:12]}…, "
          f"gerado {sha_gerado[:12]}…)")
    print("nada foi gravado no repositório.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Baixa a malha municipal do IBGE (geoftp) e gera a área de estudo."
    )
    parser.add_argument("--codigo-ibge", default=CODIGO_IBGE_DEFAULT,
                        help=f"Código IBGE do município (default: {CODIGO_IBGE_DEFAULT}, "
                             f"{paths.nome_municipio()}/{paths.uf()} — vem do config)")
    parser.add_argument("--ano", default=None,
                        help="Edição da malha (default: a mais recente listada no geoftp)")
    parser.add_argument("--forcar", action="store_true",
                        help="Rebaixa o ZIP e regrava as saídas mesmo se já existirem")
    parser.add_argument("--verificar", action="store_true",
                        help="Não grava nada: compara o gpkg que seria gerado com a camada conferida")
    args = parser.parse_args()

    codigo = str(args.codigo_ibge).strip()

    url_zip, nome_zip, ano = resolver_url_malha(codigo, args.ano)
    caminho_zip = DIR_RAW_VETOR / nome_zip
    if args.verificar:
        verificar_sem_gravar(caminho_zip, codigo, ano)
        return
    coleta = baixar(url_zip, caminho_zip, args.forcar)
    escrever_metadado(caminho_zip, {
        "descricao": f"Malha municipal do IBGE, UF inteira, edição {ano} (arquivo bruto).",
        "fonte": "IBGE — Malhas Territoriais (geoftp)",
        "navegacao": "listagens do geoftp, a partir de organizacao_do_territorio/",
        "edicao": ano,
        **coleta,
    })

    municipio = recortar_municipio(caminho_zip, codigo)

    # área no CRS equivalente (crs.area), nunca no UTM de produção
    area_km2_geometrica = medidas.area_m2(municipio.geometry.iloc[0]) / 1e6
    area_km2_oficial = float(municipio["AREA_KM2"].iloc[0]) if "AREA_KM2" in municipio.columns else None
    nome_municipio = next(
        (str(municipio[c].iloc[0]) for c in ("NM_MUN", "NM_MUNICIP") if c in municipio.columns),
        None,
    )

    metadados_comuns = {
        "descricao": "Limite municipal — área de estudo de referência do acervo.",
        "municipio": nome_municipio,
        "codigo_ibge": codigo,
        "fonte": "IBGE — Malhas Territoriais (geoftp)",
        "url_origem": url_zip,
        "edicao_malha": ano,
        "sha256_origem": coleta["sha256"],
        "last_modified_origem": coleta["last_modified_origem"],
        "data_acesso": coleta["data_acesso"],
        "crs_origem": "EPSG:4674 (SIRGAS 2000)",
        "crs_saida": CRS_PADRAO,
        "transformacao_aplicada": (
            f"seleção da feição de código {codigo} na malha da UF + "
            f"reprojeção para {CRS_PADRAO} (SIRGAS 2000 / UTM 21S)"
        ),
        "n_features": int(len(municipio)),
        "area_km2_geometrica": round(area_km2_geometrica, 3),
        "crs_medicao_area": medidas.crs_medicao_area(),
        "area_km2_oficial_ibge": area_km2_oficial,
        "colunas": [c for c in municipio.columns if c != "geometry"],
        "data_processamento": datetime.now(timezone.utc).isoformat(),
    }
    # cópia do ACERVO (GeoPackage, CRS de produção). A publicação
    #    (GeoJSON do portal) é gerada à parte por scripts/geoportal/.
    caminho_gpkg = DIR_ACERVO_LIMITES / f"limite-municipal_ibge_{ano}_municipal.gpkg"
    irmao = caminho_gpkg.with_suffix(".json")
    conteudo_antigo = (json.loads(irmao.read_text(encoding="utf-8")).get("sha256_conteudo")
                       if irmao.is_file() else None)
    regravou = gravar_gpkg(municipio, caminho_gpkg, carimbo_gpkg(coleta["last_modified_origem"]))
    conteudo_novo = sha256_conteudo(caminho_gpkg)
    sha_novo = sha256_arquivo(caminho_gpkg)
    escrever_metadado(caminho_gpkg, {
        **metadados_comuns,
        "descricao": "Limite municipal — cópia principal do ACERVO (GeoPackage).",
        "sha256": sha_novo,
        "sha256_conteudo": conteudo_novo,
    })
    # a conferência de `limite_municipal` vive na linha do catálogo: mesmo
    # CONTEÚDO preserva status, pode_publicar e o bloco "--- conferência ---";
    # dado novo despromove (catalogo.reconciliar_linha). O script nunca promove.
    from scripts.utils import catalogo
    afetada = catalogo.registrar_regravacao(caminho_gpkg, sha_novo,
                                            mesmo_conteudo=conteudo_antigo == conteudo_novo)
    if afetada and conteudo_antigo != conteudo_novo:
        logger.warning("%s: o DADO mudou — '%s' volta a pendente e pode_publicar=false "
                       "até nova conferência no mapa", paths.relativo(caminho_gpkg), afetada)
    logger.info("acervo: %s (%s)", paths.relativo(caminho_gpkg),
                "gravado" if regravou else "mesmo conteúdo — arquivo mantido")

    print()
    print(f"município ....... {nome_municipio} ({codigo})")
    print(f"edição da malha . {ano}")
    print(f"feições ......... {len(municipio)}")
    print(f"CRS ............. {municipio.crs.to_string()}")
    print(f"área geométrica . {area_km2_geometrica:,.3f} km² (calculada em {paths.crs_area()})")
    if area_km2_oficial is not None:
        diferenca = abs(area_km2_geometrica - area_km2_oficial)
        print(f"área oficial IBGE {area_km2_oficial:,.3f} km² (atributo AREA_KM2 da malha)")
        print(f"diferença ....... {diferenca:,.3f} km² ({diferenca / area_km2_oficial * 100:.3f}%)")


if __name__ == "__main__":
    main()
