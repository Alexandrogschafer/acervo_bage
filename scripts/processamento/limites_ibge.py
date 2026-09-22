"""
Produz as camadas-base de setores e distritos do Censo 2022 em data/acervo/limites/:

    setores_2022    setores_ibge-censo_2022_setor-censitario.gpkg
                    setores do município, com TODOS os atributos originais
    distritos_2022  distritos_ibge-censo_2022_distrito.gpkg
                    dissolução dos setores pelo código de distrito (CD_DIST),
                    com código e nome do distrito

Entrada: a malha bruta baixada por `scripts/download/baixar_malhas_ibge.py`
(data/raw/vetor/ibge/<edicao>/<UF>_setores_CD2022.gpkg), conferida contra o
sha256 do seu `.json` irmão. Município, UF e CRS vêm de `config/config.yaml`.

O limite municipal NÃO é produzido aqui: a camada canônica é `limite_municipal`
(conferida, produzida por `scripts/download/vetor_ibge.py`), e ela é usada
apenas como REFERÊNCIA nas verificações.

VERIFICAÇÕES (relatadas e gravadas no `.json` irmão, nunca corrigidas):
  - nenhum setor com geometria inválida (se houver, o script PARA sem gravar);
  - a união dos setores coincide com `limite_municipal`: área da diferença
    simétrica em m² e em % da área do município, separada em "setores fora do
    limite" e "limite não coberto por setor";
  - a soma das áreas dos distritos é igual à área do município.
Toda medição é feita no CRS de produção.

STATUS: as camadas entram com status_conferencia=pendente e pode_publicar=false.
A fonte autoriza redistribuição (autorizacao_fonte=true), mas o acervo só
publica o que foi conferido no mapa (validar_catalogos.py). pode_publicar
vira true na promoção, junto com status_conferencia=conferido.

GeoPackage determinístico: `OGR_CURRENT_DATE` é fixado no Last-Modified da
malha de origem, então a mesma entrada gera os mesmos bytes e o mesmo sha256
em qualquer execução. Se o arquivo gerado for idêntico ao existente, nada é
regravado (nem o `.json`, nem o catálogo).

Uso:
    python scripts/processamento/limites_ibge.py
"""

from __future__ import annotations

import re
import sys
import tempfile
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import geopandas as gpd
import pyogrio

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import catalogo, metadados, nomes, paths  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

EDICAO_SETORES = "censo_2022"
ID_LIMITE = "limite_municipal"
LICENCA = "IBGE — uso livre com citação da fonte"
TEMA = "limites"

COL_MUN, COL_DIST, COL_NM_DIST = "CD_MUN", "CD_DIST", "NM_DIST"


# --------------------------------------------------------------------------
# entrada
# --------------------------------------------------------------------------

def carregar_setores() -> tuple[gpd.GeoDataFrame, dict, Path]:
    """Setores do município, no CRS de produção, com todos os atributos.

    Returns:
        (setores, .json irmão da malha bruta, caminho da malha bruta)
    """
    ano = EDICAO_SETORES.rsplit("_", 1)[-1]
    bruto = paths.caminho("raw_vetor", "ibge", EDICAO_SETORES,
                          f"{paths.uf()}_setores_CD{ano}.gpkg")
    if not bruto.exists():
        raise FileNotFoundError(
            f"{paths.relativo(bruto)} não existe. "
            "Rode antes: python scripts/download/baixar_malhas_ibge.py"
        )
    meta = metadados.ler(bruto)
    if sha256_arquivo(bruto) != meta["sha256"]:
        raise RuntimeError(f"{paths.relativo(bruto)} não bate com o sha256 do seu .json.")

    codigo = paths.codigo_ibge()
    setores = gpd.read_file(bruto)
    if COL_MUN not in setores.columns:
        raise RuntimeError(f"coluna {COL_MUN} ausente em {bruto.name}: {list(setores.columns)}")
    setores = setores[setores[COL_MUN].astype(str).str.strip() == codigo].copy()
    if setores.empty:
        raise RuntimeError(f"nenhum setor com {COL_MUN}={codigo} em {bruto.name}")
    if setores.crs is None:
        raise RuntimeError(f"{bruto.name} não declara CRS.")
    setores = setores.to_crs(paths.crs_producao()).reset_index(drop=True)
    return setores, meta, bruto


def carregar_limite() -> tuple[gpd.GeoDataFrame, dict]:
    """A camada canônica `limite_municipal`, no CRS de produção (sha256 conferido)."""
    linha, arquivo = catalogo.camada_conferida(ID_LIMITE)
    limite = gpd.read_file(arquivo).to_crs(paths.crs_producao())
    if len(limite) != 1:
        raise RuntimeError(f"{linha['arquivo']}: esperava 1 feição, achei {len(limite)}")
    return limite, linha


# --------------------------------------------------------------------------
# produtos
# --------------------------------------------------------------------------

def dissolver_distritos(setores: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Distritos = setores dissolvidos por CD_DIST (um nome por código, exigido)."""
    nomes_por_codigo = setores.groupby(COL_DIST)[COL_NM_DIST].nunique()
    ambiguos = nomes_por_codigo[nomes_por_codigo > 1]
    if not ambiguos.empty:
        raise RuntimeError(f"CD_DIST com mais de um NM_DIST: {list(ambiguos.index)}")

    distritos = (
        setores[[COL_DIST, COL_NM_DIST, "CD_MUN", "NM_MUN", "geometry"]]
        .dissolve(by=[COL_DIST, COL_NM_DIST, "CD_MUN", "NM_MUN"], as_index=False)
    )
    contagem = setores.groupby(COL_DIST).size().rename("N_SETORES")
    distritos = distritos.merge(contagem, left_on=COL_DIST, right_index=True)
    return distritos.sort_values(COL_DIST).reset_index(drop=True)


def verificar(setores: gpd.GeoDataFrame, distritos: gpd.GeoDataFrame,
              limite: gpd.GeoDataFrame) -> dict:
    """Mede, sem corrigir, a coerência dos produtos com o limite municipal."""
    mun = limite.geometry.iloc[0]
    area_mun = mun.area
    uniao = setores.geometry.union_all()

    fora = uniao.difference(mun).area
    descoberto = mun.difference(uniao).area
    simetrica = uniao.symmetric_difference(mun).area
    soma_setores = float(setores.geometry.area.sum())
    soma_distritos = float(distritos.geometry.area.sum())

    return {
        "crs_medicao": paths.crs_producao(),
        "referencia": ID_LIMITE,
        "n_setores": int(len(setores)),
        "n_distritos": int(len(distritos)),
        "setores_invalidos": int((~setores.is_valid).sum()),
        "distritos_invalidos": int((~distritos.is_valid).sum()),
        "area_municipio_m2": round(area_mun, 2),
        "area_uniao_setores_m2": round(uniao.area, 2),
        "cobertura_diferenca_simetrica_m2": round(simetrica, 2),
        "cobertura_diferenca_simetrica_pct": round(simetrica / area_mun * 100, 6),
        "cobertura_setores_fora_do_limite_m2": round(fora, 2),
        "cobertura_limite_nao_coberto_m2": round(descoberto, 2),
        "sobreposicao_entre_setores_m2": round(soma_setores - uniao.area, 2),
        "soma_areas_distritos_m2": round(soma_distritos, 2),
        "soma_distritos_menos_municipio_m2": round(soma_distritos - area_mun, 2),
        "soma_distritos_menos_municipio_pct": round((soma_distritos - area_mun) / area_mun * 100, 6),
    }


# --------------------------------------------------------------------------
# gravação idempotente + rastro
# --------------------------------------------------------------------------

def gravar(gdf: gpd.GeoDataFrame, destino: Path, camada: str) -> bool:
    """Grava o GeoPackage; devolve False se o resultado é idêntico ao existente."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        novo = Path(tmp) / destino.name
        gdf.to_file(novo, driver="GPKG", layer=camada)
        if destino.exists() and sha256_arquivo(destino) == sha256_arquivo(novo):
            return False
        novo.replace(destino)
    return True


def registrar(destino: Path, id_camada: str, descricao: str, meta_bruto: dict,
              verificacoes: dict) -> None:
    """`.json` irmão + linha no catálogo de camadas."""
    resumo = (
        f"cobertura vs {ID_LIMITE}: dif. simétrica "
        f"{verificacoes['cobertura_diferenca_simetrica_m2']:,.0f} m² "
        f"({verificacoes['cobertura_diferenca_simetrica_pct']:.4f}%); "
        f"soma distritos - município {verificacoes['soma_distritos_menos_municipio_m2']:,.0f} m²"
    )
    observacoes = (
        f"{descricao} Malha territorial de setores do IBGE ({EDICAO_SETORES}, "
        f"{meta_bruto['url_origem']}), recorte {COL_MUN}={paths.codigo_ibge()}, reprojetada para {paths.crs_producao()}. {resumo}. "
        "pode_publicar=false só até a conferência visual: a fonte autoriza "
        "(autorizacao_fonte=true); vira true na promoção. Citar: IBGE, Censo 2022. "
        "Script: scripts/processamento/limites_ibge.py."
    )
    dados = metadados.montar(
        destino, tema=TEMA, fonte_id=meta_bruto["fonte_id"], versao=EDICAO_SETORES,
        crs=paths.crs_producao(), licenca=LICENCA, autorizacao_fonte=True,
        pode_publicar=False, status_conferencia="pendente", observacoes=observacoes,
    )
    dados["edicao"] = EDICAO_SETORES
    dados["url_origem"] = meta_bruto["url_origem"]
    dados["verificacoes"] = verificacoes
    metadados.escrever(destino, dados, sobrescrever=True)

    catalogo.upsert("catalogo_camadas", "id_camada", [{
        "id_camada": id_camada,
        "tema": TEMA,
        "arquivo": paths.relativo(destino),
        "fonte_id": meta_bruto["fonte_id"],
        "versao": EDICAO_SETORES,
        "crs": paths.crs_producao(),
        "data_producao": datetime.now(timezone.utc).astimezone().date().isoformat(),
        "sha256": dados["sha256"],
        "status_conferencia": "pendente",
        "referencias_bib": "",
        "licenca": LICENCA,
        "pode_publicar": "false",
        "observacoes": observacoes,
    }])


def main() -> None:
    setores, meta_bruto, bruto = carregar_setores()
    limite, _ = carregar_limite()

    invalidos = setores[~setores.is_valid]
    if not invalidos.empty:
        raise SystemExit(
            f"{len(invalidos)} setor(es) inválido(s): {list(invalidos['CD_SETOR'])}. "
            "Nada foi gravado — a correção é decisão do responsável."
        )
    distritos = dissolver_distritos(setores)
    verificacoes = verificar(setores, distritos, limite)
    if verificacoes["distritos_invalidos"]:
        raise SystemExit("dissolução gerou distrito inválido. Nada foi gravado.")

    # GPKG determinístico: last_change fixado no Last-Modified da origem
    lm = re.search(r"Last-Modified da origem: ([^.]+GMT)", meta_bruto["observacoes"])
    if not lm:
        raise RuntimeError("Last-Modified da origem ausente no .json da malha bruta.")
    carimbo = parsedate_to_datetime(lm.group(1)).astimezone(timezone.utc)
    pyogrio.set_gdal_config_options(
        {"OGR_CURRENT_DATE": carimbo.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
    )

    ano = EDICAO_SETORES.rsplit("_", 1)[-1]
    produtos = [
        ("setores_2022", "setores", "setor-censitario", setores,
         f"Setores censitários de {paths.nome_municipio()}/{paths.uf()} com todos os "
         "atributos originais."),
        ("distritos_2022", "distritos", "distrito", distritos,
         f"Distritos de {paths.nome_municipio()}/{paths.uf()}: dissolução dos setores "
         f"por {COL_DIST}, com {COL_DIST}, {COL_NM_DIST} e N_SETORES."),
    ]
    print()
    for id_camada, tema_nome, resolucao, gdf, descricao in produtos:
        destino = paths.caminho(
            "acervo_limites", nomes.montar(tema_nome, "ibge-censo", ano, resolucao, "gpkg")
        )
        mudou = gravar(gdf, destino, id_camada)
        if mudou or not metadados.caminho_irmao(destino).exists():
            registrar(destino, id_camada, descricao, meta_bruto, verificacoes)
        print(f"{id_camada:<15} {paths.relativo(destino)} "
              f"({len(gdf)} feições; {'gravado' if mudou else 'sem mudança'})")

    v = verificacoes
    print()
    print(f"entrada ............... {paths.relativo(bruto)}")
    print(f"setores ............... {v['n_setores']} (inválidos: {v['setores_invalidos']})")
    print(f"distritos ............. {v['n_distritos']}")
    for _, d in distritos.iterrows():
        print(f"    {d[COL_DIST]}  {d[COL_NM_DIST]:<14} {d['N_SETORES']:>4} setores  "
              f"{d.geometry.area / 1e6:>10,.3f} km²")
    print(f"área do município ..... {v['area_municipio_m2'] / 1e6:,.3f} km² ({ID_LIMITE})")
    print(f"união dos setores ..... {v['area_uniao_setores_m2'] / 1e6:,.3f} km²")
    print(f"dif. simétrica ........ {v['cobertura_diferenca_simetrica_m2']:,.1f} m² "
          f"({v['cobertura_diferenca_simetrica_pct']:.4f}%)")
    print(f"  setores fora ........ {v['cobertura_setores_fora_do_limite_m2']:,.1f} m²")
    print(f"  limite descoberto ... {v['cobertura_limite_nao_coberto_m2']:,.1f} m²")
    print(f"sobreposição setores .. {v['sobreposicao_entre_setores_m2']:,.1f} m²")
    print(f"Σ distritos − município {v['soma_distritos_menos_municipio_m2']:,.1f} m² "
          f"({v['soma_distritos_menos_municipio_pct']:.4f}%)")


if __name__ == "__main__":
    main()
