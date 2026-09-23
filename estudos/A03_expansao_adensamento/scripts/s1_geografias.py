"""
A03 — subordinada 1: as geografias do § 5 no cenário adotado (setor 136 à parte).

Desde 2026-09-23 os números principais da subordinada 1 excluem as unidades do
setor rural de 2010 430160205000136 (resultados_s1.md § 11). Este script refaz,
com as MESMAS funções de s1_expansao_adensamento.py (caracterizar, densidade),
as geografias do § 5 em dois cenários:

    adotado        sem as unidades à parte
    todas          todas as unidades (sensibilidade; = s1_caracterizacao.json)

As unidades à parte vêm de derivados/s1_desagregacao_2010.json (bloco
cruzamento_com_as_classes.unidades_a_parte), que precisa ter sido gerado sobre
esta mesma camada (sha256_conteudo conferido). O CENTRO não muda: é a referência
declarada no § 1 (centro médio dos domicílios de 2010 com todas as unidades) e
as distâncias já estão na camada.

LÊ saidas/s1_celulas_2010_2022.gpkg e derivados/s1_desagregacao_2010.json.
ESCREVE só derivados/s1_geografias.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402

import s1_expansao_adensamento as s1  # noqa: E402
from scripts.utils import medidas, metadados  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

DESAG = s1.DERIV / "s1_desagregacao_2010.json"
SAIDA = s1.DERIV / "s1_geografias.json"


def unidades_a_parte() -> tuple[list[str], str]:
    """Lista das unidades à parte, conferindo que vem desta mesma camada."""
    d = json.loads(DESAG.read_text(encoding="utf-8"))
    atual = sha256_conteudo(s1.CAMADA)
    if atual != metadados.ler(s1.CAMADA)["sha256_conteudo"] or d.get("camada_sha256_conteudo") != atual:
        raise SystemExit("PARADO — a camada de trabalho não é a usada em s1_desagregacao_2010.json; "
                         "rodar s1_desagregacao_2010.py antes")
    c = d["cruzamento_com_as_classes"]
    return c["unidades_a_parte"], ";".join(c["setores_com_assinatura"])


def cenario(u: gpd.GeoDataFrame) -> dict:
    return {
        "unidades": int(len(u)),
        "caracterizacao": {"nova": s1.caracterizar(u, "nova", "dom_22"),
                           "adensada": s1.caracterizar(u, "adensada", "dom_22"),
                           "extinta": s1.caracterizar(u, "extinta", "dom_10")},
        "densidade_por_classe": s1.densidade(u),
    }


def main() -> None:
    a_parte, setores = unidades_a_parte()
    u = gpd.read_file(s1.CAMADA)
    fora = set(a_parte) - set(u["unidade"])
    if fora:
        raise SystemExit(f"PARADO — {len(fora)} unidades à parte fora da camada")
    adotado = u[~u["unidade"].isin(a_parte)].copy()
    resultado = {
        "cenario_adotado": f"sem as {len(a_parte)} unidades do setor de 2010 {setores} "
                           "(resultados_s1.md § 11)",
        "camada_sha256_conteudo": metadados.ler(s1.CAMADA)["sha256_conteudo"],
        "centro": "o do § 1 (todas as unidades), sem mudança; distâncias lidas da camada",
        "adotado": cenario(adotado),
        "todas_as_unidades": cenario(u),
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=int), encoding="utf-8")
    for nome in ("adotado", "todas_as_unidades"):
        c = resultado[nome]["caracterizacao"]
        print(nome, {k: (v["unidades"], v["distancia_ao_centro"]["mediana_ponderada_por_domicilio_km"],
                         v["area_urbanizada_2022"]["pct_domicilios_dentro"]) for k, v in c.items()})


if __name__ == "__main__":
    main()
