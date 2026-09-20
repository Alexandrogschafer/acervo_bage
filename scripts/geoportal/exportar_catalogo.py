"""
Exporta os catálogos CSV para data/geoportal/catalogo.json.

O geoportal é estático: não lê CSV nem consulta banco. Para que o rodapé
mostre fonte e licença de cada camada SEM ninguém redigitar isso no HTML
(onde envelheceria em silêncio), o portal consome este JSON, que é uma
projeção dos dois catálogos — a mesma fonte de verdade que o validador
confere.

Só entram camadas cujo arquivo de publicação existe em data/geoportal/.
Camadas em outra situação que não 'publicada' saem marcadas, para o portal
poder exibi-las como preliminares em vez de escondê-las.

Uso:
    python scripts/geoportal/exportar_catalogo.py
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.geoportal.common import dir_geoportal, logger  # noqa: E402
from scripts.utils import paths  # noqa: E402

CAMINHO_FONTES = paths.caminho("catalogo_fontes")
CAMINHO_CAMADAS = paths.caminho("catalogo_camadas")
CAMINHO_SAIDA = dir_geoportal() / "catalogo.json"


def _itens(bruto: str | None) -> list[str]:
    if not bruto:
        return []
    return [p.strip() for p in bruto.replace(",", ";").split(";") if p.strip()]


def _ler(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def main() -> None:
    fontes = {f["id_fonte"]: f for f in _ler(CAMINHO_FONTES)}
    camadas_saida = []

    for camada in _ler(CAMINHO_CAMADAS):
        # só entra no portal camada que possa ser publicada E que já tenha um
        # GeoJSON de publicação em data/geoportal/
        if str(camada.get("pode_publicar", "")).strip().lower() not in {"true", "sim", "1"}:
            logger.warning("camada '%s' com pode_publicar=false — fora do portal",
                           camada.get("id_camada"))
            continue

        # convenção: o GeoJSON publicado leva o nome do id da camada
        # (data/acervo/... pode ter nome longo do padrão {tema}_{fonte}_..., mas
        # no portal o que identifica é o id do catálogo) — ver docs/convencoes.md
        nome_publicacao = f"{camada['id_camada']}.geojson"
        if not (CAMINHO_SAIDA.parent / nome_publicacao).exists():
            logger.warning("camada '%s' sem GeoJSON de publicação (%s) — fora do portal",
                           camada.get("id_camada"), nome_publicacao)
            continue

        camadas_saida.append({
            "id": camada["id_camada"],
            "tema": camada["tema"],
            "arquivo": nome_publicacao,
            "versao": camada.get("versao", ""),
            "data": camada.get("data_producao", ""),
            "status_conferencia": camada.get("status_conferencia", ""),
            "licenca": camada.get("licenca", ""),
            "referencias_bib": _itens(camada.get("referencias_bib")),
            "fontes": [
                {
                    "id": id_fonte,
                    "nome": fontes[id_fonte]["nome"],
                    "instituicao": fontes[id_fonte]["instituicao"],
                    "url": fontes[id_fonte]["url"],
                    "licenca": fontes[id_fonte]["licenca"],
                }
                for id_fonte in _itens(camada.get("fonte_id"))
                if id_fonte in fontes
            ],
        })

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(
        json.dumps(
            {
                "gerado_em": datetime.now(timezone.utc).isoformat(),
                "gerado_por": "scripts/geoportal/exportar_catalogo.py",
                "origem": [paths.relativo(CAMINHO_FONTES), paths.relativo(CAMINHO_CAMADAS)],
                "camadas": camadas_saida,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("gerado: %s (%d camadas)", paths.relativo(CAMINHO_SAIDA), len(camadas_saida))


if __name__ == "__main__":
    main()
