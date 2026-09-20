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

from scripts.geoportal.common import DIR_GEOPORTAL, logger  # noqa: E402

CAMINHO_FONTES = RAIZ_PROJETO / "data" / "catalogo_fontes.csv"
CAMINHO_CAMADAS = RAIZ_PROJETO / "data" / "catalogo_camadas.csv"
CAMINHO_SAIDA = DIR_GEOPORTAL / "catalogo.json"


def _itens(bruto: str | None) -> list[str]:
    if not bruto:
        return []
    return [p.strip() for p in bruto.replace(",", ";").split(";") if p.strip()]


def _ler(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def main() -> None:
    fontes = {f["id"]: f for f in _ler(CAMINHO_FONTES)}
    camadas_saida = []

    for camada in _ler(CAMINHO_CAMADAS):
        publicacao = (camada.get("arquivo_publicacao") or "").strip()
        if not publicacao or not (RAIZ_PROJETO / publicacao).exists():
            logger.warning("camada '%s' sem arquivo de publicação em disco — fora do portal",
                           camada.get("id"))
            continue

        camadas_saida.append({
            "id": camada["id"],
            "nome": camada["nome"],
            "tema": camada["tema"],
            "arquivo": Path(publicacao).name,
            "versao": camada.get("versao", ""),
            "data": camada.get("data", ""),
            "situacao": camada.get("situacao", ""),
            "referencias_bibliograficas": _itens(camada.get("referencias_bibliograficas")),
            "fontes": [
                {
                    "id": id_fonte,
                    "nome": fontes[id_fonte]["nome"],
                    "instituicao": fontes[id_fonte]["instituicao"],
                    "url": fontes[id_fonte]["url"],
                    "licenca": fontes[id_fonte]["licenca"],
                }
                for id_fonte in _itens(camada.get("fontes"))
                if id_fonte in fontes
            ],
        })

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_SAIDA.write_text(
        json.dumps(
            {
                "gerado_em": datetime.now(timezone.utc).isoformat(),
                "gerado_por": "scripts/geoportal/exportar_catalogo.py",
                "origem": ["data/catalogo_fontes.csv", "data/catalogo_camadas.csv"],
                "camadas": camadas_saida,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("gerado: %s (%d camadas)", CAMINHO_SAIDA.relative_to(RAIZ_PROJETO),
                len(camadas_saida))


if __name__ == "__main__":
    main()
