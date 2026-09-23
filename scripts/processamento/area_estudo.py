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

GeoJSON em EPSG:4326 porque a RFC 7946 exige WGS 84. A área é medida no CRS
de área (equivalente, `crs.area`); o perímetro, no CRS de produção. Quem consome usa
`paths.carregar_area_estudo()`, que devolve o recorte já no CRS de produção.

Idempotente: o GeoJSON só é regravado se o CONTEÚDO mudar (sha256_conteudo:
geometria + atributos + CRS, scripts/utils/conteudo.py, gravado no `.json`); o
`.json` irmão, só se o seu conteúdo mudar. Se o dado é o mesmo que foi
conferido, a conferência (status, pode_publicar e o bloco "--- conferência ---"
de observacoes) é preservada; se mudou, volta a pendente/false e o bloco sai
(metadados.reconciliar).

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

from scripts.utils import catalogo, medidas, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

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
    area_km2 = medidas.area_m2(geometria) / 1e6          # CRS de área (equivalente)
    perimetro_km = geometria.length / 1e3                # CRS de produção

    # grava num temporário e só substitui se mudou (idempotência)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        novo = Path(tmp) / destino.name
        municipio.to_crs(paths.crs_publicacao()).to_file(
            novo, driver="GeoJSON", RFC7946="YES", WRITE_NAME="NO",
        )
        # só substitui se o CONTEÚDO mudou (geometria + atributos + CRS)
        if not (destino.exists() and sha256_conteudo(destino) == sha256_conteudo(novo)):
            novo.replace(destino)

    meta_atual = (metadados.ler(destino) if metadados.caminho_irmao(destino).exists()
                  else None)
    origem_publicavel = linha["pode_publicar"].strip().lower() == "true"

    # confere a ida e volta 4326 -> produção (a RFC 7946 limita a 7 casas decimais)
    relido = paths.carregar_area_estudo(destino)
    if len(relido) != 1 or not relido.geometry.iloc[0].is_valid:
        raise RuntimeError(f"{paths.relativo(destino)} relido não tem 1 feição válida.")
    desvio_m2 = medidas.area_m2(relido.geometry.iloc[0].symmetric_difference(geometria))

    dados = metadados.montar(
        destino,
        tema="limites",
        fonte_id=linha["fonte_id"],
        versao=edicao,
        crs=paths.crs_publicacao(),
        licenca=linha["licenca"],
        autorizacao_fonte=True,
        pode_publicar=False,
        status_conferencia="pendente",
        observacoes=(
            f"Área de estudo do acervo = limite municipal exato de "
            f"{paths.nome_municipio()}/{paths.uf()}, sem buffer. Derivada de "
            f"'{ID_CAMADA_ORIGEM}' só por reprojeção {paths.crs_producao()} -> "
            f"{paths.crs_publicacao()} (RFC 7946). Não é camada do catálogo. "
            "Enquanto status_conferencia=pendente, pode_publicar=false; na promoção "
            "(conferência no mapa), pode_publicar passa a valer o da camada de origem "
            f"({linha['pode_publicar'].strip().lower()}). Área medida em "
            f"{paths.crs_area()} (equivalente); perímetro em {paths.crs_producao()}."
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
        "sha256_malha_bruta": (meta_origem.get("verificacoes", {}).get("origem_bruta", {})
                               .get("sha256") or meta_origem.get("sha256_origem")),
    }
    oficial = float(municipio["AREA_KM2"].iloc[0]) if "AREA_KM2" in municipio else None
    dados["medidas"] = {
        "area_km2": round(area_km2, 3),
        "crs_medicao_area": medidas.crs_medicao_area(),
        "perimetro_km": round(perimetro_km, 3),
        "crs_medicao_distancia": paths.crs_producao(),
        "area_km2_oficial_ibge": oficial,
        "area_menos_oficial_km2": (round(area_km2 - oficial, 3) if oficial else None),
    }
    dados["verificacoes"] = {
        "n_feicoes": 1,
        "geometria_valida": True,
        "codigo_ibge": paths.codigo_ibge(),
        "desvio_ida_e_volta_m2": round(desvio_m2, 2),
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    dados["sha256_conteudo"] = sha256_conteudo(destino)
    # nota de conferência (metadados.reconciliar): preservada se o CONTEÚDO é o
    # conferido; despromovida se mudou. O script nunca promove.
    dados = metadados.reconciliar(meta_atual, dados, teto_publicacao=origem_publicavel)
    sem_data = lambda d: {k: v for k, v in d.items() if k != "data_producao"}  # noqa: E731
    if meta_atual is not None and sem_data(meta_atual) == sem_data(dados):
        print(f"sem mudança: {paths.relativo(destino)} já corresponde a "
              f"{ID_CAMADA_ORIGEM} ({linha['sha256'][:12]}…)")
        return
    metadados.escrever(destino, dados, sobrescrever=True, teto_publicacao=origem_publicavel)

    print(f"área de estudo ... {paths.relativo(destino)} ({paths.crs_publicacao()})")
    print(f"origem ........... {ID_CAMADA_ORIGEM} ({linha['sha256'][:12]}…), {edicao}")
    print(f"área ............. {area_km2:,.3f} km² (em {paths.crs_area()}; "
          f"oficial IBGE {oficial} km²)")
    print(f"perímetro ........ {perimetro_km:,.3f} km")
    print(f"desvio ida-volta . {desvio_m2:,.2f} m² (arredondamento RFC 7946)")


if __name__ == "__main__":
    main()
