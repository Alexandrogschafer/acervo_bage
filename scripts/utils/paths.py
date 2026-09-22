"""
Carrega config/config.yaml e resolve caminhos contra a raiz do repositório.

Ponto de entrada obrigatório para qualquer parâmetro do acervo: código IBGE,
CRS, caminho de diretório. Nenhum script deve repetir esses valores — se
aparecer um `"EPSG:31981"` ou um `"4301602"` literal fora daqui e do YAML, é
bug.

Toda falta de chave levanta `ChaveDeConfigAusente` dizendo qual chave faltou e
em que arquivo procurá-la — nunca um KeyError cru.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    import geopandas as gpd

# .../repo/scripts/utils/paths.py -> .../repo
RAIZ: Path = Path(__file__).resolve().parents[2]
CAMINHO_CONFIG: Path = RAIZ / "config" / "config.yaml"


class ErroDeConfig(Exception):
    """Base dos erros de configuração do acervo."""


class ConfigAusente(ErroDeConfig):
    """config/config.yaml não existe ou não é YAML válido."""


class ChaveDeConfigAusente(ErroDeConfig):
    """Uma chave esperada não está no config."""


@lru_cache(maxsize=1)
def carregar_config(caminho: Path | None = None) -> dict[str, Any]:
    """Lê e devolve o config inteiro, em cache.

    Args:
        caminho: config alternativo (para teste). Default: config/config.yaml.

    Returns:
        O documento YAML como dicionário.

    Raises:
        ConfigAusente: se o arquivo não existe, não é YAML ou não é um mapa.
    """
    alvo = caminho or CAMINHO_CONFIG
    if not alvo.exists():
        raise ConfigAusente(
            f"config não encontrado em {alvo}. "
            "Ele é a fonte única de parâmetros do acervo e precisa existir."
        )
    try:
        dados = yaml.safe_load(alvo.read_text(encoding="utf-8"))
    except yaml.YAMLError as erro:
        raise ConfigAusente(f"{alvo} não é YAML válido: {erro}") from erro

    if not isinstance(dados, dict):
        raise ConfigAusente(f"{alvo} deveria ser um mapa YAML, veio {type(dados).__name__}.")
    return dados


def valor(*chaves: str) -> Any:
    """Devolve um valor aninhado do config, com erro legível se faltar.

    Args:
        *chaves: caminho da chave, ex.: `valor("municipio", "codigo_ibge")`.

    Returns:
        O valor encontrado.

    Raises:
        ChaveDeConfigAusente: nomeando a chave que faltou e o caminho completo.
    """
    atual: Any = carregar_config()
    percorridas: list[str] = []
    for chave in chaves:
        percorridas.append(chave)
        if not isinstance(atual, dict) or chave not in atual:
            disponiveis = sorted(atual) if isinstance(atual, dict) else "(não é um mapa)"
            raise ChaveDeConfigAusente(
                f"chave '{'.'.join(percorridas)}' ausente em {CAMINHO_CONFIG}. "
                f"Chaves disponíveis nesse nível: {disponiveis}"
            )
        atual = atual[chave]
    return atual


def caminho(nome: str, *extras: str) -> Path:
    """Resolve um caminho declarado em `paths:` contra a raiz do repositório.

    Args:
        nome: chave dentro de `paths:` (ex.: "acervo_limites").
        *extras: segmentos a anexar (ex.: um nome de arquivo).

    Returns:
        Caminho absoluto. NÃO cria o diretório nem exige que exista.

    Raises:
        ChaveDeConfigAusente: se `nome` não está em `paths:`.
    """
    return RAIZ.joinpath(valor("paths", nome), *extras)


def relativo(alvo: Path | str) -> str:
    """Converte um caminho absoluto para relativo à raiz, com barras `/`.

    Usado em catálogos e metadados: caminho absoluto de máquina não serve num
    repositório compartilhado.
    """
    absoluto = Path(alvo).resolve()
    try:
        return absoluto.relative_to(RAIZ).as_posix()
    except ValueError:
        return absoluto.as_posix()


# ---- atalhos de leitura frequente -----------------------------------------

def codigo_ibge() -> str:
    """Código IBGE do município do acervo (string, com zeros à esquerda)."""
    return str(valor("municipio", "codigo_ibge"))


def nome_municipio() -> str:
    """Nome do município do acervo."""
    return str(valor("municipio", "nome"))


def uf() -> str:
    """Sigla da UF do município do acervo."""
    return str(valor("municipio", "uf"))


def crs_producao() -> str:
    """CRS métrico de trabalho — onde toda medição acontece."""
    return str(valor("crs", "producao"))


def crs_publicacao() -> str:
    """CRS de publicação do geoportal."""
    return str(valor("crs", "publicacao"))


def crs_area() -> str:
    """CRS equivalente — onde toda medida de ÁREA acontece (ver scripts/utils/medidas.py)."""
    return str(valor("crs", "area"))


def area_estudo() -> Path:
    """Caminho absoluto do recorte de referência do acervo."""
    return RAIZ / str(valor("area_estudo"))


def carregar_area_estudo(alvo: Path | str | None = None) -> "gpd.GeoDataFrame":
    """Carrega a área de estudo já reprojetada para o CRS de produção.

    O arquivo é gravado em EPSG:4326 (a RFC 7946 exige WGS 84 em GeoJSON) por
    `scripts/processamento/area_estudo.py`; toda medição, porém, acontece no
    CRS de produção, então a reprojeção é feita aqui, na leitura, e nenhum
    chamador precisa lembrar dela.

    Args:
        alvo: arquivo alternativo (para teste). Default: `area_estudo:` do config.

    Returns:
        GeoDataFrame com a feição única do município, no CRS de produção.

    Raises:
        FileNotFoundError: se o arquivo não existe (area_estudo.py não rodou).
        ValueError: se o arquivo não declara CRS.
    """
    import geopandas as gpd  # import tardio: paths é importado por scripts sem geo

    arquivo = Path(alvo) if alvo else area_estudo()
    if not arquivo.exists():
        raise FileNotFoundError(
            f"área de estudo não encontrada em {relativo(arquivo)}. "
            "Rode primeiro: python scripts/processamento/area_estudo.py"
        )
    gdf = gpd.read_file(arquivo)
    if gdf.crs is None:
        raise ValueError(f"{relativo(arquivo)} não declara CRS — verifique a geração.")
    return gdf.to_crs(crs_producao())
