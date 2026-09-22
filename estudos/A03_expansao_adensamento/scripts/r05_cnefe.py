"""
A03 — reconhecimento, item 5: CNEFE 2022 × malha de setores 2022.

Para cada endereço: o ponto (LATITUDE/LONGITUDE) cai dentro do setor indicado
no próprio COD_SETOR do CNEFE? Se não, a que distância (em metros, no CRS de
produção) da borda do setor indicado, e em que setor ele cai.

Escreve:
    derivados/r05_cnefe.json      resumo agregado (vai para o reconhecimento)
    derivados/r05_cnefe_fora.csv  LISTA dos endereços fora do setor indicado,
                                  com a distância — fica em derivados/ (fora do
                                  git): é dado de endereço, e o reconhecimento
                                  só publica agregados.

Código de setor do CNEFE: parte dos códigos é da malha INTERMEDIÁRIA/PRELIMINAR
de 2022 e não existe na malha de divulgação (o setor foi dividido na última
etapa). Esses códigos são resolvidos pelo de/para oficial
(Historico_formacao_Setores_Censitarios_2010_2022) para os setores de
divulgação que os sucederam; "dentro" vale se o ponto cai em qualquer um deles.
O resultado é dado nas duas leituras: estrita (código como está) e por sucessão.

CRS dos pontos: o CNEFE publica latitude/longitude em graus sem declarar o
datum no arquivo; lido como SIRGAS 2000 (EPSG:4674), o mesmo da malha de 2022.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

from scripts.utils import paths  # noqa: E402

DERIV = Path(__file__).resolve().parents[1] / "derivados"
CODIGO = paths.codigo_ibge()
VET = paths.caminho("raw_vetor", "ibge")
PROD = paths.crs_producao()
ESPECIES = {"1": "domicílio particular", "2": "domicílio coletivo", "3": "estab. agropecuário",
            "4": "estab. de ensino", "5": "estab. de saúde", "6": "estab. outras finalidades",
            "7": "edificação em construção", "8": "estab. religioso"}


def main() -> None:
    with zipfile.ZipFile(VET / "censo_2022" / "cnefe" / "4301602_BAGE.zip") as z:
        membro = next(n for n in z.namelist() if n.endswith(".csv"))
        df = pd.read_csv(z.open(membro), sep=";", dtype=str, encoding="latin-1")
    df["sufixo"] = df["COD_SETOR"].str[15:]
    df["setor"] = df["COD_SETOR"].str[:15]
    pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
        pd.to_numeric(df["LONGITUDE"]), pd.to_numeric(df["LATITUDE"])), crs="EPSG:4674").to_crs(PROD)

    malha = gpd.read_file(VET / "censo_2022" / "RS_setores_CD2022.gpkg",
                          where=f"CD_MUN = '{CODIGO}'")[["CD_SETOR", "SITUACAO", "geometry"]].to_crs(PROD)
    geo = malha.set_index("CD_SETOR").geometry

    cai = gpd.sjoin(pts[["COD_UNICO_ENDERECO", "geometry"]], malha[["CD_SETOR", "geometry"]],
                    how="left", predicate="within").drop_duplicates("COD_UNICO_ENDERECO")
    pts["setor_do_ponto"] = pts["COD_UNICO_ENDERECO"].map(
        dict(zip(cai["COD_UNICO_ENDERECO"], cai["CD_SETOR"])))
    pts["setor_existe_na_malha"] = pts["setor"].isin(geo.index)
    pts["dentro_estrito"] = pts["setor_do_ponto"] == pts["setor"]

    # sucessão: código intermediário/preliminar -> setores de divulgação
    h = pd.read_csv(next((DERIV / "planilhas" / "c2022").glob("Historico_formacao*.csv")),
                    sep=";", dtype=str)
    h = h[h["GEOCODIGO_2022_DIVULGAÇÃO"].str.startswith(CODIGO)]
    sucessores: dict[str, set[str]] = {}
    for col in ("GEOCODIGO_2022_INTERMEDIARIA", "GEOCODIGO_2022_PRELIMINAR"):
        for antigo, novo in zip(h[col], h["GEOCODIGO_2022_DIVULGAÇÃO"]):
            if antigo not in geo.index:
                sucessores.setdefault(antigo, set()).add(novo)
    alvo = {c: ({c} if c in geo.index else sucessores.get(c, set())) for c in pts["setor"].unique()}
    pts["dentro"] = [sp in alvo[s] for sp, s in zip(pts["setor_do_ponto"], pts["setor"])]
    geo_alvo = {c: gpd.GeoSeries([geo[x] for x in xs], crs=PROD).union_all()
                for c, xs in alvo.items() if xs}

    fora = pts[~pts["dentro"]].copy()
    fora["distancia_m"] = [
        round(p.distance(geo_alvo[s]), 1) if s in geo_alvo else None
        for p, s in zip(fora.geometry, fora["setor"])
    ]
    fora["mesmo_distrito"] = fora["setor_do_ponto"].str[:9] == fora["setor"].str[:9]

    faixas = pd.cut(fora["distancia_m"], [0, 10, 50, 100, 500, 1000, 5000, float("inf")],
                    right=False, labels=["<10 m", "10–50 m", "50–100 m", "100–500 m",
                                         "500 m–1 km", "1–5 km", "≥5 km"])
    resumo = {
        "enderecos": int(len(pts)),
        "sufixos_do_cod_setor": pts["sufixo"].value_counts(dropna=False).to_dict(),
        "cod_setor_inexistente_na_malha": int((~pts["setor_existe_na_malha"]).sum()),
        "codigos_inexistentes_resolvidos_por_sucessao": {
            c: sorted(alvo[c]) for c in sorted(pts.loc[~pts["setor_existe_na_malha"], "setor"].unique())},
        "leitura_estrita": {"dentro": int(pts["dentro_estrito"].sum()),
                            "pct_dentro": round(100 * pts["dentro_estrito"].mean(), 3)},
        "dentro_do_setor_indicado": int(pts["dentro"].sum()),
        "pct_dentro": round(100 * pts["dentro"].mean(), 3),
        "fora": int(len(fora)),
        "fora_sem_setor_nenhum (ponto fora da malha do município)": int(fora["setor_do_ponto"].isna().sum()),
        "fora_por_faixa_de_distancia": faixas.value_counts().sort_index().to_dict(),
        "distancia_fora_m": fora["distancia_m"].describe().round(1).to_dict(),
        "fora_no_mesmo_distrito": int(fora["mesmo_distrito"].sum()),
        "pct_dentro_por_nivel_geocodificacao": (
            pts.groupby("NV_GEO_COORD")["dentro"].agg(["size", "mean"])
            .assign(mean=lambda d: (100 * d["mean"]).round(3)).to_dict("index")),
        "fora_por_especie": fora["COD_ESPECIE"].map(ESPECIES).value_counts().to_dict(),
        "fora_por_situacao_do_setor_indicado": fora["setor"].map(
            malha.set_index("CD_SETOR")["SITUACAO"]).value_counts(dropna=False).to_dict(),
        "setores_indicados_com_mais_enderecos_fora": fora["setor"].value_counts().head(10).to_dict(),
        "crs_pontos": "EPSG:4674 (suposto: o CSV não declara datum)",
        "crs_distancia": PROD,
    }
    (DERIV / "r05_cnefe.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=str),
                                          encoding="utf-8")
    fora[["COD_UNICO_ENDERECO", "COD_SETOR", "setor_do_ponto", "distancia_m", "mesmo_distrito",
          "NV_GEO_COORD", "COD_ESPECIE", "LATITUDE", "LONGITUDE"]].sort_values(
        "distancia_m", ascending=False).to_csv(DERIV / "r05_cnefe_fora.csv", sep=";", index=False)
    print(json.dumps(resumo, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
