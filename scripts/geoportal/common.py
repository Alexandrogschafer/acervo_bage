"""
Utilitários de PUBLICAÇÃO do geoportal.

Separação que vale para todo o acervo (ver docs/convencoes.md):

  - **acervo**     -> `data/acervo/<tema>/`, no CRS de produção
                      (config `crs.producao`), com todos os atributos. É a
                      cópia principal, fora do git, rastreada por sha256.
  - **publicação** -> `data/geoportal/`, no CRS de publicação (config
                      `crs.publicacao`), que é o único que o Leaflet consome.
                      Versionado: o portal estático precisa dele em runtime.

Qualquer transformação métrica (simplificação, buffer, área) acontece ANTES,
no CRS de produção; a reprojeção para publicação é sempre o último passo.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

from scripts.utils import paths
from scripts.utils.hashes import hash_e_tamanho

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("geoportal")


def dir_geoportal() -> Path:
    """Diretório de publicação do portal, vindo do config."""
    return paths.caminho("geoportal")


def salvar_geojson_publicacao(
    gdf: gpd.GeoDataFrame,
    caminho_saida: Path,
    descricao: str,
    fonte: dict,
    transformacao: str,
    forcar: bool = False,
) -> Path:
    """Reprojeta para o CRS de publicação e exporta GeoJSON + `.json` irmão.

    Idempotente: se o arquivo já existe e `forcar` é False, só loga e sai.

    Args:
        gdf: camada a publicar, com CRS declarado.
        caminho_saida: destino `.geojson` em `data/geoportal/`.
        descricao: o que é a camada, em uma frase.
        fonte: procedência (caminho de origem, script, instituição).
        transformacao: o que foi feito entre o acervo e este arquivo.
        forcar: reexporta mesmo se já existir.

    Returns:
        Caminho do GeoJSON.

    Raises:
        ValueError: se `gdf` não declara CRS.
    """
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    if caminho_saida.exists() and not forcar:
        logger.info("já existe, pulando: %s", paths.relativo(caminho_saida))
        return caminho_saida

    if gdf.crs is None:
        raise ValueError(f"GeoDataFrame sem CRS antes de exportar para {caminho_saida}")

    crs_publicacao = paths.crs_publicacao()
    gdf_publicacao = (
        gdf.to_crs(crs_publicacao) if gdf.crs.to_string() != crs_publicacao else gdf
    )
    gdf_publicacao.to_file(caminho_saida, driver="GeoJSON")

    sha256, tamanho = hash_e_tamanho(caminho_saida)
    metadados = {
        "descricao": descricao,
        "fonte": fonte,
        "crs_saida": crs_publicacao,
        "transformacao_aplicada": transformacao,
        "n_features": int(len(gdf_publicacao)),
        "colunas": [c for c in gdf_publicacao.columns if c != "geometry"],
        "sha256": sha256,
        "tamanho_bytes": tamanho,
        "data_processamento": datetime.now(timezone.utc).isoformat(),
    }
    caminho_saida.with_suffix(".json").write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    logger.info("gerado: %s (%d feições, %.1f KB)",
                paths.relativo(caminho_saida), len(gdf_publicacao), tamanho / 1024)
    return caminho_saida
