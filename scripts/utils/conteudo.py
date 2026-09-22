"""
Hash de CONTEÚDO de uma camada vetorial: `sha256_conteudo`.

O sha256 do arquivo muda sem que o dado mude: o GeoPackage é um banco SQLite,
e a ordem física das páginas, o contador de alterações do cabeçalho e o
carimbo `last_change` de `gpkg_contents` dependem de como e quando o arquivo
foi escrito. Duas gravações da mesma geometria com os mesmos atributos podem
ter sha256 diferentes. Para dizer "é o mesmo dado", o acervo compara o
conteúdo:

    CRS           identificador da autoridade (ex.: "EPSG:31981"), ou WKT2
                  quando não há autoridade
    colunas       nomes, em ordem alfabética
    feições       cada uma serializada como atributos (JSON canônico, colunas
                  em ordem alfabética, nulos e NaN como null) + WKB da geometria
                  NORMALIZADA (shapely.normalize: orientação e vértice inicial
                  canônicos; little-endian, sem SRID); as feições são ordenadas
                  pelo sha256 dessa serialização

A ordenação pela própria feição faz o hash independer do fid e da ordem de
gravação sem exigir que se escolha uma coluna identificadora por camada — é
um id intrínseco, e o validador consegue recalcular o hash só com o arquivo.
Nenhuma coordenada é arredondada: conteúdo igual é igualdade exata.

Camada com várias tabelas (GeoPackage multi-camada) entra por camada, em
ordem de nome.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date, datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pyogrio
import shapely

VERSAO_ALGORITMO = "conteudo-v1"


def _valor(v):
    """Valor de atributo em forma JSON canônica."""
    if v is None:
        return None
    if isinstance(v, np.generic):
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, (bytes, bytearray)):
        return v.hex()
    return v


def _crs(gdf: gpd.GeoDataFrame) -> str:
    if gdf.crs is None:
        return ""
    autoridade = gdf.crs.to_authority()
    return ":".join(autoridade) if autoridade else gdf.crs.to_wkt()


def hash_gdf(gdf: gpd.GeoDataFrame) -> str:
    """sha256 de conteúdo de um GeoDataFrame (ver docstring do módulo)."""
    coluna_geom = gdf.geometry.name
    colunas = sorted(c for c in gdf.columns if c != coluna_geom)
    geoms = shapely.normalize(np.asarray(gdf.geometry.values))
    wkbs = shapely.to_wkb(geoms, byte_order=1, include_srid=False)

    feicoes = []
    for (_, linha), wkb in zip(gdf[colunas].iterrows(), wkbs):
        attrs = json.dumps([_valor(linha[c]) for c in colunas],
                           ensure_ascii=False, separators=(",", ":"), default=str)
        corpo = attrs.encode("utf-8") + b"\x00" + (wkb if wkb is not None else b"")
        feicoes.append(hashlib.sha256(corpo).digest())
    feicoes.sort()

    digest = hashlib.sha256()
    digest.update(f"{VERSAO_ALGORITMO}\ncrs:{_crs(gdf)}\n".encode())
    digest.update(("colunas:" + json.dumps(colunas, ensure_ascii=False) + "\n").encode())
    digest.update(f"n:{len(feicoes)}\n".encode())
    for f in feicoes:
        digest.update(f)
    return digest.hexdigest()


def sha256_conteudo(arquivo: Path | str) -> str:
    """sha256 de conteúdo de um arquivo vetorial (todas as camadas, por nome)."""
    camadas = sorted(str(nome) for nome, _ in pyogrio.list_layers(arquivo))
    if len(camadas) == 1:
        return hash_gdf(gpd.read_file(arquivo, layer=camadas[0]))
    digest = hashlib.sha256(f"{VERSAO_ALGORITMO}-multi\n".encode())
    for nome in camadas:
        digest.update(f"{nome}:{hash_gdf(gpd.read_file(arquivo, layer=nome))}\n".encode())
    return digest.hexdigest()
