"""
Gera a área de estudo do acervo a partir da camada canônica `limite_municipal`:

    data/acervo/limites/limite-municipal_ibge_<ano>_municipal.gpkg   (origem, conferida)
        -> config/area_estudo.geojson                               (EPSG:4326, RFC 7946)
           config/area_estudo.json                                  (.json irmão)

A área de estudo é o LIMITE MUNICIPAL EXATO. Buffer, quando for preciso
(raster, bacias), é parâmetro de cada script consumidor e nunca é embutido
aqui: um recorte "com folga" no arquivo de referência contaminaria em silêncio
toda medição feita sobre ele.

Por que derivar de `limite_municipal` e não da malha bruta: o limite municipal
tem UMA definição no acervo, a camada conferida no catálogo (produzida por
`scripts/download/vetor_ibge.py`). Se a área de estudo fosse recortada da malha
de novo, haveria duas definições do mesmo polígono. O sha256 da camada de
origem fica registrado em `camada_origem` do `.json` irmão; se a camada mudar
sem reconferência, o script recusa a derivação (`catalogo.camada_conferida`).

GeoJSON em EPSG:4326 porque a RFC 7946 exige WGS 84. Medições (área,
perímetro) são sempre feitas no CRS de produção. Quem consome usa
`paths.carregar_area_estudo()`, que devolve o recorte já no CRS de produção.

Idempotente: se o GeoJSON gerado é byte a byte igual ao existente e o `.json`
irmão aponta para o mesmo sha256 de origem, nada é regravado.

Uso:
    python scripts/processamento/area_estudo.py
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import catalogo, metadados, paths  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

ID_CAMADA_ORIGEM = "limite_municipal"
COLUNA_CODIGO = "CD_MUN"


def carregar_origem() -> tuple[gpd.GeoDataFrame, dict, dict]:
    """Lê `limite_municipal`, conferindo sha256, feição única, código e validade.

    Returns:
        (gdf no CRS de produção, linha do catálogo, .json irmão da camada)
    """
    linha, arquivo = catalogo.camada_conferida(ID_CAMADA_ORIGEM)
    if linha["status_conferencia"] != "conferido":
        raise RuntimeError(
            f"'{ID_CAMADA_ORIGEM}' está '{linha['status_conferencia']}' no catálogo; "
            "a área de estudo só se deriva de camada conferida."
        )
    gdf = gpd.read_file(arquivo)
    if gdf.crs is None:
        raise RuntimeError(f"{linha['arquivo']} não declara CRS.")
    gdf = gdf.to_crs(paths.crs_producao())

    if len(gdf) != 1:
        raise RuntimeError(f"{linha['arquivo']}: esperava 1 feição, achei {len(gdf)}")
    codigo = str(gdf[COLUNA_CODIGO].iloc[0]).strip()
    if codigo != paths.codigo_ibge():
        raise RuntimeError(
            f"{linha['arquivo']} é o município {codigo}, mas o config pede "
            f"{paths.codigo_ibge()}."
        )
    if not gdf.geometry.iloc[0].is_valid:
        raise RuntimeError(f"{linha['arquivo']}: geometria inválida — não derivo dela.")
    return gdf, linha, metadados.ler(arquivo)


def edicao_de(meta_origem: dict) -> str:
    """Edição da malha (ex.: 'municipio_2025'), lida da URL de origem registrada."""
    achado = re.search(r"/(municipio_\d{4})/", meta_origem.get("url_origem", ""))
    if not achado:
        raise RuntimeError("não achei a edição da malha no url_origem de limite_municipal.")
    return achado.group(1)


def main() -> None:
    municipio, linha, meta_origem = carregar_origem()
    edicao = edicao_de(meta_origem)
    destino = paths.area_estudo()

    geometria = municipio.geometry.iloc[0]
    area_km2 = geometria.area / 1e6
    perimetro_km = geometria.length / 1e3

    # grava num temporário e só substitui se mudou (idempotência)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        novo = Path(tmp) / destino.name
        municipio.to_crs(paths.crs_publicacao()).to_file(
            novo, driver="GeoJSON", RFC7946="YES", WRITE_NAME="NO",
        )
        sha_novo = sha256_arquivo(novo)

        origem_registrada = None
        if destino.exists() and metadados.caminho_irmao(destino).exists():
            origem_registrada = metadados.ler(destino).get("camada_origem", {}).get("sha256")
        if (destino.exists() and sha256_arquivo(destino) == sha_novo
                and origem_registrada == linha["sha256"]):
            print(f"sem mudança: {paths.relativo(destino)} já corresponde a "
                  f"{ID_CAMADA_ORIGEM} ({linha['sha256'][:12]}…)")
            return
        novo.replace(destino)

    # confere a ida e volta 4326 -> produção (a RFC 7946 limita a 7 casas decimais)
    relido = paths.carregar_area_estudo(destino)
    if len(relido) != 1 or not relido.geometry.iloc[0].is_valid:
        raise RuntimeError(f"{paths.relativo(destino)} relido não tem 1 feição válida.")
    desvio_m2 = relido.geometry.iloc[0].symmetric_difference(geometria).area

    dados = metadados.montar(
        destino,
        tema="limites",
        fonte_id=linha["fonte_id"],
        versao=edicao,
        crs=paths.crs_publicacao(),
        licenca=linha["licenca"],
        autorizacao_fonte=True,
        pode_publicar=linha["pode_publicar"].strip().lower() == "true",
        status_conferencia="pendente",
        observacoes=(
            f"Área de estudo do acervo = limite municipal exato de "
            f"{paths.nome_municipio()}/{paths.uf()}, sem buffer. Derivada de "
            f"'{ID_CAMADA_ORIGEM}' só por reprojeção {paths.crs_producao()} -> "
            f"{paths.crs_publicacao()} (RFC 7946). Não é camada do catálogo. "
            "pode_publicar herdado da camada de origem; status 'pendente' porque "
            "este arquivo reprojetado ainda não foi aberto no mapa."
        ),
    )
    dados["edicao"] = edicao
    dados["camada_origem"] = {
        "id_camada": ID_CAMADA_ORIGEM,
        "arquivo": linha["arquivo"],
        "sha256": linha["sha256"],
        "versao": linha["versao"],
        "status_conferencia": linha["status_conferencia"],
        "url_origem": meta_origem.get("url_origem"),
        "sha256_malha_bruta": meta_origem.get("sha256_origem"),
    }
    dados["medidas"] = {
        "crs_medicao": paths.crs_producao(),
        "area_km2": round(area_km2, 3),
        "perimetro_km": round(perimetro_km, 3),
        "area_km2_oficial_ibge": (
            float(municipio["AREA_KM2"].iloc[0]) if "AREA_KM2" in municipio else None
        ),
    }
    dados["verificacoes"] = {
        "n_feicoes": 1,
        "geometria_valida": True,
        "codigo_ibge": paths.codigo_ibge(),
        "desvio_ida_e_volta_m2": round(desvio_m2, 2),
    }
    metadados.escrever(destino, dados, sobrescrever=True)

    print(f"área de estudo ... {paths.relativo(destino)} ({paths.crs_publicacao()})")
    print(f"origem ........... {ID_CAMADA_ORIGEM} ({linha['sha256'][:12]}…), {edicao}")
    print(f"área ............. {area_km2:,.3f} km² (em {paths.crs_producao()})")
    print(f"perímetro ........ {perimetro_km:,.3f} km")
    print(f"desvio ida-volta . {desvio_m2:,.2f} m² (arredondamento RFC 7946)")


if __name__ == "__main__":
    main()
