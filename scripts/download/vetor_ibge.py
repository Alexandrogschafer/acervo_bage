"""
Gera a camada canônica do limite municipal a partir da malha municipal do IBGE:

    data/raw/vetor/ibge/municipio_<ano>/<UF>_Municipios_<ano>.zip   (bruto, UF inteira)
        -> data/acervo/limites/limite-municipal_ibge_<ano>_municipal.gpkg  (camada `limite_municipal`)
           data/acervo/limites/limite-municipal_ibge_<ano>_municipal.json  (.json irmão)

A área de estudo (config/area_estudo.geojson) NÃO é gravada aqui: ela é
derivada desta camada por `scripts/processamento/area_estudo.py`, em EPSG:4326.

Município, CRS e caminhos vêm todos de `config/config.yaml` via
`scripts/utils/paths.py` — nada fixo neste arquivo.

ORIGEM DO DADO
--------------
O bruto é obtido por `scripts/download/baixar_malhas_ibge.py`, que navega as
listagens do geoftp do IBGE a partir de `organizacao_do_territorio/` sem
montar URL por adivinhação, grava o ZIP em `data/raw/vetor/ibge/<edicao>/` com
o `.json` irmão e registra a fonte no catálogo. Este script:

- sem opção: chama esse download (navegação + HEAD; só baixa se preciso) e
  depois recorta;
- `--local`: NÃO acessa a rede. Usa o ZIP já em `data/raw/`, conferindo o
  sha256 do ZIP contra o seu `.json` irmão. Neste modo, se o CONTEÚDO do
  GeoPackage (o que está em disco, ou o que seria gerado) divergir do
  `sha256_conteudo` registrado, o script ABORTA sem gravar nada: é o modo de
  regravar metadado, não de trocar dado;
- `--verificar`: não grava nada; gera o GeoPackage num temporário a partir do
  ZIP local e compara o conteúdo com o registrado.

METADADO
--------
O `.json` irmão segue o esquema de `scripts/utils/metadados.py`
(`metadados.montar`): status_conferencia, pode_publicar, observacoes,
sha256_conteudo, medidas, verificacoes. Campos que o `.json` anterior tinha e
este script não gera (anotação à mão, esquema antigo) são PRESERVADOS em
`complementos`, em vez de descartados.

Conferência: a nota do responsável (bloco "--- conferência ---") segue a regra
de `metadados.reconciliar`: o mesmo CONTEÚDO preserva status, pode_publicar e
a nota no `.json` e na linha do catálogo; dado novo despromove. Um `.json` de
esquema antigo (sem status) é reconciliado contra a linha do catálogo, que é
onde a conferência dele estava registrada. O script nunca promove.

Determinismo: o GeoPackage é gravado com `last_change` fixado no Last-Modified
da malha de origem, e só substitui o existente se o CONTEÚDO mudou — uma
camada conferida com o mesmo dado nunca é regravada.

Uso:
    python scripts/download/vetor_ibge.py
    python scripts/download/vetor_ibge.py --local
    python scripts/download/vetor_ibge.py --local --ano 2025
    python scripts/download/vetor_ibge.py --verificar
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import tempfile
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import geopandas as gpd
import pyogrio

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.utils import catalogo, medidas, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vetor_ibge")

# tudo vem do config — ver config/config.yaml
CRS_PADRAO = paths.crs_producao()
CODIGO_IBGE_DEFAULT = paths.codigo_ibge()
ID_CAMADA = "limite_municipal"
TEMA = "limites"

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

# Campos do `.json` de esquema antigo que este script agora gera, com o mesmo
# significado, em outro lugar (observacoes, edicao, medidas, verificacoes).
# Qualquer OUTRO campo fora do esquema vai para `complementos` — inclusive
# datas antigas (data_acesso, data_processamento), que registram fatos daquela
# execução e não são recalculáveis.
LEGADO_COBERTO = frozenset({
    "descricao", "municipio", "codigo_ibge", "fonte", "edicao_malha", "sha256_origem",
    "last_modified_origem", "crs_origem", "crs_saida",
    "transformacao_aplicada", "n_features", "area_km2_geometrica", "crs_medicao_area",
    "area_km2_oficial_ibge", "colunas",
})


class ConteudoDivergente(RuntimeError):
    """`--local`: o conteúdo do GeoPackage não é o registrado — nada foi gravado."""


# --------------------------------------------------------------------------
# bruto: ZIP da malha em data/raw/
# --------------------------------------------------------------------------

def uf_de(codigo_ibge: str) -> str:
    uf = UF_POR_CODIGO.get(codigo_ibge[:2])
    if uf is None:
        raise RuntimeError(f"Código IBGE '{codigo_ibge}' não começa com um código de UF válido.")
    return uf


def zip_local(uf: str, ano: str | None) -> tuple[Path, dict, str]:
    """O ZIP da malha já em data/raw/, conferido contra o seu `.json` irmão.

    Returns:
        (caminho do ZIP, `.json` irmão, edição — ex.: "municipio_2025")
    """
    base = paths.caminho("raw_vetor", "ibge")
    edicoes = sorted(d.name for d in base.glob("municipio_*") if d.is_dir())
    edicao = f"municipio_{ano}" if ano else (edicoes[-1] if edicoes else "")
    if edicao not in edicoes:
        raise RuntimeError(f"edição '{edicao or '?'}' não está em {paths.relativo(base)} "
                           f"(há: {edicoes}). Baixe com baixar_malhas_ibge.py.")
    candidatos = sorted((base / edicao).glob(f"{uf}_Municipios_*.zip"))
    if len(candidatos) != 1:
        raise RuntimeError(f"esperava 1 '{uf}_Municipios_AAAA.zip' em "
                           f"{paths.relativo(base / edicao)}, achei {candidatos}")
    caminho_zip = candidatos[0]
    meta = metadados.ler(caminho_zip)
    if sha256_arquivo(caminho_zip) != str(meta.get("sha256", "")).lower():
        raise RuntimeError(f"{paths.relativo(caminho_zip)}: sha256 do ZIP diverge do seu "
                           ".json — o bruto mudou depois de registrado.")
    return caminho_zip, meta, edicao


def obter_bruto(uf: str, ano: str | None, forcar: bool) -> None:
    """Navega o geoftp e baixa o ZIP se preciso (delegado a baixar_malhas_ibge.py)."""
    from scripts.download import baixar_malhas_ibge

    produto = baixar_malhas_ibge.resolver_municipal(uf, ano)
    baixar_malhas_ibge.baixar(produto, forcar)
    logger.info("catálogo de fontes: %s", baixar_malhas_ibge.registrar_fonte(produto))


def last_modified_de(meta_zip: dict) -> str:
    achado = re.search(r"Last-Modified da origem: ([^.]+GMT)", meta_zip.get("observacoes", ""))
    if not achado:
        raise RuntimeError("Last-Modified da origem ausente no .json do ZIP — sem carimbo "
                           "determinístico.")
    return achado.group(1)


# --------------------------------------------------------------------------
# recorte e GeoPackage
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


def carimbo_gpkg(last_modified: str) -> str:
    """`last_change` fixo do GeoPackage: o Last-Modified da malha de origem.

    Mesma técnica de limites_ibge.py: a mesma entrada gera o mesmo carimbo, em
    vez da hora da execução.
    """
    return (parsedate_to_datetime(last_modified).astimezone(timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%S.000Z"))


def _gravar(municipio: gpd.GeoDataFrame, destino: Path, carimbo: str) -> None:
    pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": carimbo})
    try:
        municipio.to_file(destino, driver="GPKG", layer=ID_CAMADA)
    finally:
        pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": None})


def gravar_gpkg(municipio: gpd.GeoDataFrame, destino: Path, carimbo: str,
                exigir_conteudo: str | None = None) -> bool:
    """Grava o GeoPackage com carimbo fixo; devolve True se substituiu o existente.

    Se o existente já tem o mesmo CONTEÚDO (sha256_conteudo), NÃO é
    substituído, e o sha256 conferido continua valendo.

    Args:
        exigir_conteudo: se dado, o GeoPackage em disco E o gerado têm de ter
            este sha256_conteudo; senão `ConteudoDivergente`, sem gravar nada.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        novo = Path(tmp) / destino.name
        _gravar(municipio, novo, carimbo)
        conteudo_novo = sha256_conteudo(novo)
        conteudo_disco = sha256_conteudo(destino) if destino.exists() else None
        if exigir_conteudo is not None:
            problemas = []
            if conteudo_disco != exigir_conteudo:
                problemas.append(f"em disco {str(conteudo_disco)[:12]}…")
            if conteudo_novo != exigir_conteudo:
                problemas.append(f"gerado do ZIP {conteudo_novo[:12]}…")
            if problemas:
                raise ConteudoDivergente(
                    f"{paths.relativo(destino)}: sha256_conteudo registrado "
                    f"{exigir_conteudo[:12]}…, mas {' e '.join(problemas)}. Nada foi gravado."
                )
        if conteudo_disco == conteudo_novo:
            return False
        novo.replace(destino)
    return True


# --------------------------------------------------------------------------
# metadado
# --------------------------------------------------------------------------

def _linha_catalogo(destino: Path) -> dict | None:
    rel = paths.relativo(destino)
    return next((l for l in catalogo.ler("catalogo_camadas") if l["arquivo"] == rel), None)


def _fonte(fonte_id: str) -> dict:
    fonte = next((l for l in catalogo.ler("catalogo_fontes") if l["id_fonte"] == fonte_id), None)
    if fonte is None:
        raise RuntimeError(f"fonte '{fonte_id}' não está em catalogo_fontes.csv")
    return fonte


def antigo_para_reconciliar(antigo: dict | None, linha: dict | None) -> dict | None:
    """Estado anterior para `metadados.reconciliar`.

    `.json` de esquema antigo não tem status: a conferência dele estava na linha
    do catálogo, e é de lá que vêm status, pode_publicar e a nota.
    """
    if antigo is None or "status_conferencia" in antigo or linha is None:
        return antigo
    return {**antigo,
            "status_conferencia": linha["status_conferencia"],
            "pode_publicar": linha["pode_publicar"].strip().lower() == "true",
            "observacoes": linha["observacoes"]}


def complementos_de(antigo: dict | None) -> dict:
    """Campos do `.json` anterior que este script não gera — preservados."""
    if not antigo:
        return {}
    conhecidos = set(metadados.CAMPOS) | set(metadados.CAMPOS_OPCIONAIS) | LEGADO_COBERTO
    extras = {k: v for k, v in antigo.items() if k not in conhecidos}
    return {**(antigo.get("complementos") or {}), **extras}


def montar_metadado(destino: Path, municipio: gpd.GeoDataFrame, codigo: str,
                    caminho_zip: Path, meta_zip: dict, edicao: str,
                    linha: dict | None, fonte: dict, antigo: dict | None) -> dict:
    geometria = municipio.geometry.iloc[0]
    area_km2 = medidas.area_m2(geometria) / 1e6            # CRS de área (equivalente)
    oficial = float(municipio["AREA_KM2"].iloc[0]) if "AREA_KM2" in municipio.columns else None
    nome = next((str(municipio[c].iloc[0]) for c in ("NM_MUN", "NM_MUNICIP")
                 if c in municipio.columns), None)

    dados = metadados.montar(
        destino, tema=TEMA, fonte_id=meta_zip["fonte_id"],
        versao=(linha["versao"] if linha else edicao), crs=CRS_PADRAO,
        licenca=fonte["licenca"],
        autorizacao_fonte=fonte["autorizacao_fonte"].strip().lower() == "true",
        pode_publicar=False, status_conferencia="pendente",
        url_origem=meta_zip.get("url_origem"),
        observacoes=(
            f"Limite municipal de {nome} ({codigo}) — cópia principal do ACERVO. "
            f"Feição do código {codigo} na malha municipal do IBGE ({edicao}, UF "
            f"inteira, {paths.relativo(caminho_zip)}), reprojetada para {CRS_PADRAO}. "
            "Área em ESRI:102033 (equivalente); perímetro no CRS de produção. "
            "pode_publicar só vira true na promoção, depois da conferência visual. "
            "Citar: IBGE, Malhas Territoriais. Script: scripts/download/vetor_ibge.py."
        ),
    )
    dados["edicao"] = edicao
    dados["sha256_conteudo"] = sha256_conteudo(destino)
    dados["medidas"] = {
        "area_km2": round(area_km2, 3),
        "crs_medicao_area": medidas.crs_medicao_area(),
        "perimetro_km": round(geometria.length / 1e3, 3),
        "crs_medicao_distancia": CRS_PADRAO,
        "area_km2_oficial_ibge": oficial,
        "area_menos_oficial_km2": (round(area_km2 - oficial, 3) if oficial else None),
    }
    dados["verificacoes"] = {
        "codigo_ibge": codigo,
        "municipio": nome,
        "n_feicoes": int(len(municipio)),
        "geometria_valida": bool(geometria.is_valid),
        "colunas": [c for c in municipio.columns if c != "geometry"],
        "transformacao_aplicada": (f"seleção da feição de código {codigo} na malha da UF + "
                                   f"reprojeção para {CRS_PADRAO}"),
        "origem_bruta": {
            "arquivo": paths.relativo(caminho_zip),
            "sha256": meta_zip["sha256"],
            "crs": meta_zip.get("crs"),
            "last_modified_origem": last_modified_de(meta_zip),
            "data_acesso": meta_zip.get("data_producao"),
        },
    }
    complementos = complementos_de(antigo)
    if complementos:
        dados["complementos"] = complementos
    return dados


# --------------------------------------------------------------------------

def verificar_sem_gravar(caminho_zip: Path, meta_zip: dict, codigo: str,
                         destino: Path) -> None:
    """Gera o gpkg fora do repositório e compara o CONTEÚDO com o registrado."""
    registrado = json.loads(destino.with_suffix(".json").read_text(encoding="utf-8")) \
        .get("sha256_conteudo") if destino.with_suffix(".json").is_file() else None
    referencia = registrado or sha256_conteudo(destino)
    municipio = recortar_municipio(caminho_zip, codigo)
    with tempfile.TemporaryDirectory(prefix="vetor_ibge_verificar_") as tmp:
        gerado = Path(tmp) / destino.name
        _gravar(municipio, gerado, carimbo_gpkg(last_modified_de(meta_zip)))
        conteudo_gerado = sha256_conteudo(gerado)
    print()
    print(f"camada .................. {paths.relativo(destino)}")
    print(f"sha256_conteudo esperado  {referencia} "
          f"({'do .json irmão' if registrado else 'recalculado do arquivo'})")
    print(f"sha256_conteudo gerado .. {conteudo_gerado}  "
          f"{'IGUAL — mesmo dado' if conteudo_gerado == referencia else 'DIFERENTE — o dado mudou'}")
    print("nada foi gravado no repositório.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera a camada limite_municipal a partir da malha municipal do IBGE."
    )
    parser.add_argument("--codigo-ibge", default=CODIGO_IBGE_DEFAULT,
                        help=f"Código IBGE do município (default: {CODIGO_IBGE_DEFAULT}, "
                             f"{paths.nome_municipio()}/{paths.uf()} — vem do config)")
    parser.add_argument("--ano", default=None,
                        help="Edição da malha (default: a mais recente — listada no geoftp, "
                             "ou presente em data/raw/ com --local)")
    parser.add_argument("--local", action="store_true",
                        help="Não acessa a rede: usa o ZIP já em data/raw/ e aborta se o "
                             "conteúdo divergir do registrado")
    parser.add_argument("--forcar", action="store_true",
                        help="Rebaixa o ZIP mesmo se a origem mudou (ver baixar_malhas_ibge.py)")
    parser.add_argument("--verificar", action="store_true",
                        help="Não grava nada: compara o gpkg que seria gerado com o registrado")
    args = parser.parse_args()

    codigo = str(args.codigo_ibge).strip()
    uf = uf_de(codigo)
    if not (args.local or args.verificar):
        obter_bruto(uf, args.ano, args.forcar)
    caminho_zip, meta_zip, edicao = zip_local(uf, args.ano)
    ano = edicao.rsplit("_", 1)[-1]
    destino = DIR_ACERVO_LIMITES / f"limite-municipal_ibge_{ano}_municipal.gpkg"

    if args.verificar:
        verificar_sem_gravar(caminho_zip, meta_zip, codigo, destino)
        return

    irmao = destino.with_suffix(".json")
    antigo = json.loads(irmao.read_text(encoding="utf-8")) if irmao.is_file() else None
    exigir = None
    if args.local and antigo and destino.exists():
        exigir = antigo.get("sha256_conteudo") or sha256_conteudo(destino)

    municipio = recortar_municipio(caminho_zip, codigo)
    try:
        regravou = gravar_gpkg(municipio, destino, carimbo_gpkg(last_modified_de(meta_zip)),
                               exigir_conteudo=exigir)
    except ConteudoDivergente as erro:
        raise SystemExit(f"ABORTADO: {erro}") from erro

    linha = _linha_catalogo(destino)
    fonte = _fonte(meta_zip["fonte_id"])
    anterior = antigo_para_reconciliar(antigo, linha)
    dados = montar_metadado(destino, municipio, codigo, caminho_zip, meta_zip, edicao,
                            linha, fonte, antigo)
    teto = fonte["pode_publicar"].strip().lower() == "true"
    dados = metadados.reconciliar(anterior, dados, teto_publicacao=teto)
    mesmo = bool(anterior) and metadados.mesmo_conteudo(anterior, dados)

    sem_data = lambda d: {k: v for k, v in (d or {}).items() if k != "data_producao"}  # noqa: E731
    if sem_data(antigo) != sem_data(dados):
        metadados.escrever(destino, dados, sobrescrever=True, teto_publicacao=teto,
                           antigo_conferencia=anterior)
        logger.info("metadado: %s", paths.relativo(irmao))
    else:
        logger.info("metadado sem mudança: %s", paths.relativo(irmao))

    # a conferência de `limite_municipal` também vive na linha do catálogo:
    # mesma regra (catalogo.reconciliar_linha). O script nunca promove.
    afetada = catalogo.registrar_regravacao(destino, dados["sha256"], mesmo_conteudo=mesmo)
    if afetada and not mesmo:
        logger.warning("%s: o DADO mudou — '%s' volta a pendente e pode_publicar=false "
                       "até nova conferência no mapa", paths.relativo(destino), afetada)

    print()
    print(f"camada .......... {paths.relativo(destino)} "
          f"({'regravada' if regravou else 'mesmo conteúdo — arquivo mantido'})")
    print(f"bruto ........... {paths.relativo(caminho_zip)} ({edicao})")
    print(f"sha256_conteudo . {dados['sha256_conteudo']}")
    print(f"conferência ..... {dados['status_conferencia']} "
          f"(pode_publicar={str(dados['pode_publicar']).lower()})")
    print(f"área ............ {dados['medidas']['area_km2']:,.3f} km² "
          f"(em {paths.crs_area()}; oficial IBGE {dados['medidas']['area_km2_oficial_ibge']} km²)")


if __name__ == "__main__":
    main()
