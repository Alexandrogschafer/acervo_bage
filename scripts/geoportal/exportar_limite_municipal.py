"""
Publica o limite municipal no geoportal.

    config/area_estudo.geojson  (CRS de produção)
        -> data/geoportal/limite_municipal.geojson  (CRS de publicação)

Etapa de PUBLICAÇÃO: não recalcula nada, não altera geometria nem atributos —
só reprojeta para o CRS que o Leaflet consome. A cópia do acervo
correspondente (GeoPackage) é gerada por `scripts/download/vetor_ibge.py`.

Uso:
    python scripts/geoportal/exportar_limite_municipal.py [--forcar]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.geoportal.common import dir_geoportal, salvar_geojson_publicacao  # noqa: E402
from scripts.utils import paths  # noqa: E402
from scripts.utils.recorte_municipio import carregar_area_estudo  # noqa: E402

NOME_SAIDA: str = "limite_municipal.geojson"


def main() -> None:
    """Exporta o limite municipal para `data/geoportal/`."""
    parser = argparse.ArgumentParser(description="Publica o limite municipal no geoportal.")
    parser.add_argument("--forcar", action="store_true", help="Reexporta mesmo se já existir")
    args = parser.parse_args()

    salvar_geojson_publicacao(
        carregar_area_estudo(),
        dir_geoportal() / NOME_SAIDA,
        descricao=f"Limite municipal de {paths.nome_municipio()}/{paths.uf()} "
                  f"(área de estudo do acervo).",
        fonte={
            "caminho_origem": paths.relativo(paths.area_estudo()),
            "script_origem": "scripts/download/vetor_ibge.py",
            "instituicao": "IBGE — Malhas Territoriais",
        },
        transformacao=f"reprojeção {paths.crs_producao()} -> {paths.crs_publicacao()}, "
                      "sem alteração de geometria/atributos",
        forcar=args.forcar,
    )


if __name__ == "__main__":
    main()
