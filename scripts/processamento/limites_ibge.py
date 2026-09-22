"""
Produz as camadas-base de setores e distritos do Censo 2022 em data/acervo/limites/:

    setores_2022    setores_ibge-censo_2022_setor-censitario.gpkg
                    setores do município, com TODOS os atributos originais
    distritos_2022  distritos_ibge-censo_2022_distrito.gpkg
                    malha OFICIAL de distritos do IBGE, com os atributos
                    originais — desde que coincida com a dissolução dos setores
                    (ver "DISTRITOS")

Entradas: as malhas brutas baixadas por `scripts/download/baixar_malhas_ibge.py`
em data/raw/vetor/ibge/<edicao>/, cada uma conferida contra o sha256 do seu
`.json` irmão. Município, UF e CRS vêm de `config/config.yaml`.

O limite municipal NÃO é produzido aqui: a camada canônica é `limite_municipal`
(conferida, produzida por `scripts/download/vetor_ibge.py`), usada apenas como
REFERÊNCIA nas verificações.

DISTRITOS
---------
Dado oficial tem prioridade. A malha oficial de distritos 2022 é comparada à
dissolução dos setores 2022 por CD_DIST: códigos, nomes, área e diferença
simétrica de cada distrito.
  - Mesmos códigos e nomes e diferença simétrica < TOLERANCIA_DISTRITO_M2 em
    TODOS os distritos: `distritos_2022` é gravada a partir da malha OFICIAL; a
    dissolução fica só como verificação (observacoes + `.json`).
  - Qualquer outra coisa: `distritos_2022` NÃO é tocada, a comparação vai para
    docs/comparacoes/distritos_ibge_oficial_x_dissolucao.md e o script sai com
    código 2, à espera de decisão do responsável.

COBERTURA POR EDIÇÃO (relatada, nunca corrigida)
------------------------------------------------
A união dos setores é comparada ao limite do município em duas edições da
malha municipal: a do ano do Censo (municipio_2022, só em data/raw/, não vira
camada) e a canônica (`limite_municipal`, municipio_2025). Os setores NÃO são
recortados por nenhuma das duas.

Operações espaciais no CRS de produção; toda ÁREA é medida no CRS de área
(equivalente, `crs.area`) via `scripts/utils/medidas.py`, e cada bloco de
medidas registra `crs_medicao_area`.

STATUS: as camadas entram com status_conferencia=pendente e pode_publicar=false.
A fonte autoriza redistribuição (autorizacao_fonte=true), mas o acervo só
publica o que foi conferido no mapa (validar_catalogos.py). pode_publicar
vira true na promoção (metadados.promover + catalogo.promover), junto com
status_conferencia=conferido e o bloco "--- conferência ---" em observacoes.
Rodar de novo preserva os três se o CONTEÚDO é o conferido e os remove se o
dado mudou (metadados.reconciliar / catalogo.reconciliar_linha).

GeoPackage determinístico: `OGR_CURRENT_DATE` é fixado no Last-Modified da
malha de origem, então a mesma entrada gera os mesmos bytes. Se o CONTEÚDO
gerado (sha256_conteudo) e o metadado forem iguais aos existentes, nada é
regravado; o `.json` registra `sha256_conteudo` ao lado do `sha256`. Se o
CONTEÚDO é o conferido, a conferência (status, pode_publicar e a nota) é
preservada no `.json` e no catálogo; se mudou, é removida (ver STATUS acima).

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

from scripts.utils import catalogo, medidas, metadados, nomes, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

EDICAO_CENSO = "censo_2022"
ANO_CENSO = EDICAO_CENSO.rsplit("_", 1)[-1]
EDICAO_MUNICIPAL_CENSO = f"municipio_{ANO_CENSO}"
ID_LIMITE = "limite_municipal"
LICENCA = "IBGE — uso livre com citação da fonte"
TEMA = "limites"
TOLERANCIA_DISTRITO_M2 = 1.0

COL_MUN, COL_DIST, COL_NM_DIST = "CD_MUN", "CD_DIST", "NM_DIST"
CAMINHO_COMPARACAO = ("comparacoes", "distritos_ibge_oficial_x_dissolucao.md")


# --------------------------------------------------------------------------
# entrada
# --------------------------------------------------------------------------

def carregar_bruto(edicao: str, padrao: str) -> tuple[gpd.GeoDataFrame, dict, Path]:
    """Feições do município numa malha bruta, no CRS de produção.

    Args:
        edicao: subdiretório de data/raw/vetor/ibge/ (ex.: "censo_2022").
        padrao: regex do nome do arquivo; exige exatamente um.

    Returns:
        (feições do município, .json irmão da malha bruta, caminho da malha)
    """
    pasta = paths.caminho("raw_vetor", "ibge", edicao)
    candidatos = [a for a in sorted(pasta.glob("*"))
                  if re.fullmatch(padrao, a.name) and a.suffix != ".json"]
    if len(candidatos) != 1:
        raise FileNotFoundError(
            f"esperava 1 arquivo '{padrao}' em {paths.relativo(pasta)}, achei "
            f"{[c.name for c in candidatos]}. Rode: python scripts/download/baixar_malhas_ibge.py"
        )
    bruto = candidatos[0]
    meta = metadados.ler(bruto)
    if sha256_arquivo(bruto) != meta["sha256"]:
        raise RuntimeError(f"{paths.relativo(bruto)} não bate com o sha256 do seu .json.")

    gdf = gpd.read_file(f"zip://{bruto}" if bruto.suffix == ".zip" else bruto)
    if COL_MUN not in gdf.columns:
        raise RuntimeError(f"coluna {COL_MUN} ausente em {bruto.name}: {list(gdf.columns)}")
    if gdf.crs is None:
        raise RuntimeError(f"{bruto.name} não declara CRS.")
    codigo = paths.codigo_ibge()
    gdf = gdf[gdf[COL_MUN].astype(str).str.strip() == codigo].copy()
    if gdf.empty:
        raise RuntimeError(f"nenhuma feição com {COL_MUN}={codigo} em {bruto.name}")
    return gdf.to_crs(paths.crs_producao()).reset_index(drop=True), meta, bruto


def carregar_limite() -> tuple[gpd.GeoDataFrame, dict]:
    """A camada canônica `limite_municipal`, no CRS de produção (sha256 conferido)."""
    linha, arquivo = catalogo.camada_conferida(ID_LIMITE)
    limite = gpd.read_file(arquivo).to_crs(paths.crs_producao())
    if len(limite) != 1:
        raise RuntimeError(f"{linha['arquivo']}: esperava 1 feição, achei {len(limite)}")
    return limite, linha


def last_modified(meta: dict) -> datetime:
    """Last-Modified da origem, gravado nas observações do `.json` da malha bruta."""
    achado = re.search(r"Last-Modified da origem: ([^.]+GMT)", meta["observacoes"])
    if not achado:
        raise RuntimeError(f"Last-Modified ausente no .json de {meta['arquivo']}.")
    return parsedate_to_datetime(achado.group(1)).astimezone(timezone.utc)


# --------------------------------------------------------------------------
# verificações
# --------------------------------------------------------------------------

def dissolver_distritos(setores: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Setores dissolvidos por CD_DIST (um nome por código, exigido)."""
    nomes_por_codigo = setores.groupby(COL_DIST)[COL_NM_DIST].nunique()
    ambiguos = nomes_por_codigo[nomes_por_codigo > 1]
    if not ambiguos.empty:
        raise RuntimeError(f"CD_DIST com mais de um NM_DIST: {list(ambiguos.index)}")
    distritos = setores[[COL_DIST, COL_NM_DIST, "geometry"]].dissolve(
        by=[COL_DIST, COL_NM_DIST], as_index=False
    )
    contagem = setores.groupby(COL_DIST).size().rename("N_SETORES")
    distritos = distritos.merge(contagem, left_on=COL_DIST, right_index=True)
    return distritos.sort_values(COL_DIST).reset_index(drop=True)


def comparar_distritos(oficiais: gpd.GeoDataFrame, dissolvidos: gpd.GeoDataFrame) -> dict:
    """Compara distrito a distrito a malha oficial com a dissolução dos setores."""
    of = oficiais.set_index(COL_DIST)
    di = dissolvidos.set_index(COL_DIST)
    linhas = []
    for codigo in sorted(set(of.index) | set(di.index)):
        linha = {"cd_dist": codigo,
                 "nm_oficial": of[COL_NM_DIST].get(codigo),
                 "nm_dissolucao": di[COL_NM_DIST].get(codigo)}
        if codigo in of.index and codigo in di.index:
            g_of, g_di = of.geometry[codigo], di.geometry[codigo]
            dif = medidas.area_m2(g_of.symmetric_difference(g_di))
            area_of = medidas.area_m2(g_of)
            linha.update(
                area_oficial_m2=round(area_of, 2),
                area_dissolucao_m2=round(medidas.area_m2(g_di), 2),
                n_setores=int(di["N_SETORES"][codigo]),
                dif_simetrica_m2=round(dif, 4),
                dif_simetrica_pct=round(dif / area_of * 100, 8),
            )
        linhas.append(linha)

    so_oficial = sorted(set(of.index) - set(di.index))
    so_dissolucao = sorted(set(di.index) - set(of.index))
    nomes_divergentes = [l["cd_dist"] for l in linhas
                         if l["nm_oficial"] and l["nm_dissolucao"]
                         and l["nm_oficial"] != l["nm_dissolucao"]]
    acima = [l["cd_dist"] for l in linhas
             if l.get("dif_simetrica_m2", float("inf")) >= TOLERANCIA_DISTRITO_M2]
    return {
        "n_oficial": int(len(of)),
        "n_dissolucao": int(len(di)),
        "so_na_oficial": so_oficial,
        "so_na_dissolucao": so_dissolucao,
        "nomes_divergentes": nomes_divergentes,
        "tolerancia_m2": TOLERANCIA_DISTRITO_M2,
        "crs_medicao_area": medidas.crs_medicao_area(),
        "acima_da_tolerancia": acima,
        "coincidem": not (so_oficial or so_dissolucao or nomes_divergentes or acima),
        "distritos": linhas,
    }


def cobertura(setores: gpd.GeoDataFrame, limite, rotulo: str) -> dict:
    """União dos setores x um limite municipal: diferença simétrica e suas partes."""
    uniao = setores.geometry.union_all()
    area = medidas.area_m2(limite)
    simetrica = medidas.area_m2(uniao.symmetric_difference(limite))
    return {
        "referencia": rotulo,
        "crs_medicao_area": medidas.crs_medicao_area(),
        "area_municipio_m2": round(area, 2),
        "area_uniao_setores_m2": round(medidas.area_m2(uniao), 2),
        "diferenca_simetrica_m2": round(simetrica, 2),
        "diferenca_simetrica_pct": round(simetrica / area * 100, 6),
        "setores_fora_do_limite_m2": round(medidas.area_m2(uniao.difference(limite)), 2),
        "limite_nao_coberto_m2": round(medidas.area_m2(limite.difference(uniao)), 2),
    }


def escrever_comparacao(comp: dict) -> Path:
    """Relatório markdown da comparação, para decisão do responsável."""
    destino = paths.caminho("docs", *CAMINHO_COMPARACAO)
    destino.parent.mkdir(parents=True, exist_ok=True)
    linhas = [
        "# Distritos 2022 — malha oficial do IBGE × dissolução dos setores",
        "",
        f"Gerado por `scripts/processamento/limites_ibge.py` em "
        f"{datetime.now().astimezone().isoformat(timespec='seconds')}. Município "
        f"{paths.nome_municipio()}/{paths.uf()} ({paths.codigo_ibge()}); áreas medidas em "
        f"{paths.crs_area()} (equivalente).",
        "",
        f"**As camadas NÃO coincidem** (tolerância: < {TOLERANCIA_DISTRITO_M2} m² de "
        "diferença simétrica por distrito). `distritos_2022` não foi alterada; a "
        "escolha da camada canônica fica com o responsável.",
        "",
        f"- distritos na oficial: {comp['n_oficial']}; na dissolução: {comp['n_dissolucao']}",
        f"- só na oficial: {comp['so_na_oficial'] or '—'}",
        f"- só na dissolução: {comp['so_na_dissolucao'] or '—'}",
        f"- nomes divergentes: {comp['nomes_divergentes'] or '—'}",
        f"- acima da tolerância: {comp['acima_da_tolerancia'] or '—'}",
        "",
        "| CD_DIST | nome (oficial) | nome (dissolução) | área oficial (km²) | "
        "área dissolução (km²) | dif. simétrica (m²) | dif. (%) |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for l in comp["distritos"]:
        km2 = lambda c: f"{l[c] / 1e6:,.4f}" if c in l else "—"  # noqa: E731
        linhas.append(
            f"| {l['cd_dist']} | {l['nm_oficial'] or '—'} | {l['nm_dissolucao'] or '—'} | "
            f"{km2('area_oficial_m2')} | {km2('area_dissolucao_m2')} | "
            f"{l.get('dif_simetrica_m2', '—')} | {l.get('dif_simetrica_pct', '—')} |"
        )
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return destino


# --------------------------------------------------------------------------
# gravação idempotente + rastro
# --------------------------------------------------------------------------

def gravar(gdf: gpd.GeoDataFrame, destino: Path, camada: str, carimbo: datetime) -> bool:
    """Grava o GeoPackage; devolve False se o existente já tem o mesmo CONTEÚDO.

    Critério de conteúdo (sha256_conteudo), não de bytes: um arquivo com o
    mesmo dado não é substituído, e o sha256 conferido continua valendo.
    """
    pyogrio.set_gdal_config_options(
        {"OGR_CURRENT_DATE": carimbo.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        novo = Path(tmp) / destino.name
        gdf.to_file(novo, driver="GPKG", layer=camada)
        if destino.exists() and sha256_conteudo(destino) == sha256_conteudo(novo):
            return False
        novo.replace(destino)
    return True


def registrar(destino: Path, id_camada: str, meta_bruto: dict, observacoes: str,
              verificacoes: dict) -> bool:
    """`.json` irmão + linha no catálogo. Devolve False se nada mudou."""
    observacoes += (
        " A fonte autoriza (autorizacao_fonte=true); pode_publicar só vira true na "
        "promoção, depois da conferência visual. Citar: IBGE, Censo 2022. "
        "Script: scripts/processamento/limites_ibge.py."
    )
    # nota de conferência (metadados.reconciliar): preservada se o CONTEÚDO é
    # o conferido; despromovida se mudou. O script nunca promove.
    antigo = (metadados.ler(destino) if metadados.caminho_irmao(destino).exists() else None)
    dados = metadados.montar(
        destino, tema=TEMA, fonte_id=meta_bruto["fonte_id"], versao=EDICAO_CENSO,
        crs=paths.crs_producao(), licenca=LICENCA, autorizacao_fonte=True,
        pode_publicar=False, status_conferencia="pendente", observacoes=observacoes,
    )
    dados["edicao"] = EDICAO_CENSO
    dados["url_origem"] = meta_bruto["url_origem"]
    dados["verificacoes"] = verificacoes
    dados["sha256_conteudo"] = sha256_conteudo(destino)
    dados = metadados.reconciliar(antigo, dados)
    mesmo = bool(antigo) and metadados.mesmo_conteudo(antigo, dados)

    if antigo is not None and \
            {k: v for k, v in antigo.items() if k != "data_producao"} == \
            {k: v for k, v in dados.items() if k != "data_producao"}:
        return False
    metadados.escrever(destino, dados, sobrescrever=True)

    catalogo.upsert("catalogo_camadas", "id_camada", [{
        "id_camada": id_camada,
        "tema": TEMA,
        "arquivo": paths.relativo(destino),
        "fonte_id": meta_bruto["fonte_id"],
        "versao": EDICAO_CENSO,
        "crs": paths.crs_producao(),
        "data_producao": datetime.now(timezone.utc).astimezone().date().isoformat(),
        "sha256": dados["sha256"],
        "status_conferencia": dados["status_conferencia"],
        "referencias_bib": "",
        "licenca": LICENCA,
        "pode_publicar": "true" if dados["pode_publicar"] else "false",
        "observacoes": observacoes,
    }], mesmo_conteudo={id_camada: mesmo})
    return True


def destino_de(tema_nome: str, resolucao: str) -> Path:
    return paths.caminho(
        "acervo_limites", nomes.montar(tema_nome, "ibge-censo", ANO_CENSO, resolucao, "gpkg")
    )


def _cob_texto(c: dict) -> str:
    return (f"{c['referencia']}: {c['diferenca_simetrica_m2']:,.0f} m² "
            f"({c['diferenca_simetrica_pct']:.4f}%; setores fora "
            f"{c['setores_fora_do_limite_m2']:,.0f} m², limite descoberto "
            f"{c['limite_nao_coberto_m2']:,.0f} m²)")


def main() -> None:
    uf = paths.uf()
    setores, meta_setores, bruto_setores = carregar_bruto(
        EDICAO_CENSO, rf"{uf}_setores_CD{ANO_CENSO}\.gpkg")
    oficiais, meta_distritos, bruto_distritos = carregar_bruto(
        EDICAO_CENSO, rf"{uf}_distritos_CD{ANO_CENSO}\.gpkg")
    mun_censo, meta_mun_censo, _ = carregar_bruto(
        EDICAO_MUNICIPAL_CENSO, rf"{uf}_Municipios_{ANO_CENSO}\.zip")
    limite, linha_limite = carregar_limite()
    if len(mun_censo) != 1:
        raise RuntimeError(f"malha {EDICAO_MUNICIPAL_CENSO}: esperava 1 feição, achei {len(mun_censo)}")

    invalidos = setores[~setores.is_valid]
    if not invalidos.empty:
        raise SystemExit(
            f"{len(invalidos)} setor(es) inválido(s): {list(invalidos['CD_SETOR'])}. "
            "Nada foi gravado — a correção é decisão do responsável."
        )
    if not oficiais.is_valid.all():
        raise SystemExit("malha oficial de distritos tem geometria inválida. Nada foi gravado.")

    # ---- setores: cobertura por edição -------------------------------------
    edicao_limite = re.search(r"/(municipio_\d{4})/", metadados.ler(
        paths.RAIZ / linha_limite["arquivo"]).get("url_origem", ""))
    rotulo_limite = f"{edicao_limite.group(1) if edicao_limite else '?'} ({ID_LIMITE})"
    coberturas = [
        cobertura(setores, mun_censo.geometry.iloc[0], f"{EDICAO_MUNICIPAL_CENSO} (data/raw)"),
        cobertura(setores, limite.geometry.iloc[0], rotulo_limite),
    ]
    uniao = setores.geometry.union_all()
    verif_setores = {
        "crs_medicao_area": medidas.crs_medicao_area(),
        "n_setores": int(len(setores)),
        "setores_invalidos": 0,
        "sobreposicao_entre_setores_m2": round(
            float(medidas.areas_m2(setores).sum()) - medidas.area_m2(uniao), 2),
        "cobertura_por_edicao": coberturas,
        "recorte_aplicado": "nenhum — setores não são recortados por limite algum",
    }
    obs_setores = (
        f"Setores censitários de {paths.nome_municipio()}/{uf} com todos os atributos "
        f"originais. Malha territorial de setores do IBGE ({EDICAO_CENSO}, "
        f"{meta_setores['url_origem']}), recorte {COL_MUN}={paths.codigo_ibge()}, "
        f"reprojetada para {paths.crs_producao()}. Cobertura da união dos setores "
        f"(diferença simétrica, sem recorte; áreas em {paths.crs_area()}) — "
        f"{_cob_texto(coberturas[0])}; "
        f"{_cob_texto(coberturas[1])}."
    )
    destino_setores = destino_de("setores", "setor-censitario")
    gravou_setores = gravar(setores, destino_setores, "setores_2022", last_modified(meta_setores))
    registrou_setores = registrar(destino_setores, "setores_2022", meta_setores,
                                  obs_setores, verif_setores)

    # ---- distritos: oficial x dissolução -----------------------------------
    dissolvidos = dissolver_distritos(setores)
    comp = comparar_distritos(oficiais, dissolvidos)

    print()
    print(f"setores_2022    {paths.relativo(destino_setores)} ({len(setores)} feições; "
          f"{_situacao(gravou_setores, registrou_setores)})")

    destino_distritos = destino_de("distritos", "distrito")
    if not comp["coincidem"]:
        relatorio = escrever_comparacao(comp)
        _imprimir(comp, coberturas)
        raise SystemExit(
            f"\nDISTRITOS: malha oficial e dissolução NÃO coincidem. distritos_2022 não "
            f"foi alterada. Comparação em {paths.relativo(relatorio)} — decisão do responsável."
        )

    oficiais = oficiais.sort_values(COL_DIST).reset_index(drop=True)
    soma = float(medidas.areas_m2(oficiais).sum())
    area_limite = medidas.area_m2(limite.geometry.iloc[0])
    verif_distritos = {
        "crs_medicao_area": medidas.crs_medicao_area(),
        "n_distritos": int(len(oficiais)),
        "origem": "malha oficial de distritos do IBGE",
        "comparacao_com_dissolucao_dos_setores": comp,
        "soma_areas_distritos_m2": round(soma, 2),
        "soma_distritos_menos_limite_municipal_m2": round(soma - area_limite, 2),
        "soma_distritos_menos_limite_municipal_pct": round((soma - area_limite) / area_limite * 100, 6),
    }
    max_dif = max(l["dif_simetrica_m2"] for l in comp["distritos"])
    obs_distritos = (
        f"Distritos de {paths.nome_municipio()}/{uf}: malha OFICIAL de distritos do IBGE "
        f"({EDICAO_CENSO}, {meta_distritos['url_origem']}), recorte "
        f"{COL_MUN}={paths.codigo_ibge()}, atributos originais, reprojetada para "
        f"{paths.crs_producao()}. Verificação: a dissolução dos setores 2022 por "
        f"{COL_DIST} tem os mesmos {comp['n_oficial']} códigos e nomes e diferença "
        f"simétrica máxima de {max_dif:.4f} m² por distrito (tolerância "
        f"< {TOLERANCIA_DISTRITO_M2} m²). Soma das áreas − {ID_LIMITE}: "
        f"{soma - area_limite:,.0f} m² (áreas em {paths.crs_area()})."
    )
    gravou_distritos = gravar(oficiais, destino_distritos, "distritos_2022",
                              last_modified(meta_distritos))
    registrou_distritos = registrar(destino_distritos, "distritos_2022", meta_distritos,
                                    obs_distritos, verif_distritos)
    print(f"distritos_2022  {paths.relativo(destino_distritos)} ({len(oficiais)} feições, "
          f"OFICIAL; {_situacao(gravou_distritos, registrou_distritos)})")
    print(f"\nentradas: {paths.relativo(bruto_setores)}, {paths.relativo(bruto_distritos)}, "
          f"{meta_mun_censo['arquivo']}")
    _imprimir(comp, coberturas)


def _situacao(gravou: bool, registrou: bool) -> str:
    if gravou:
        return "GeoPackage gravado"
    return "GeoPackage inalterado, metadado atualizado" if registrou else "sem mudança"


def _imprimir(comp: dict, coberturas: list[dict]) -> None:
    print("\nDistritos — oficial × dissolução dos setores")
    print(f"  {'CD_DIST':<10} {'nome oficial':<14} {'nome dissol.':<14} {'setores':>7} "
          f"{'km² oficial':>12} {'km² dissol.':>12} {'dif. m²':>9} {'dif. %':>10}")
    for l in comp["distritos"]:
        print(f"  {l['cd_dist']:<10} {str(l['nm_oficial']):<14} {str(l['nm_dissolucao']):<14} "
              f"{l.get('n_setores', '—'):>7} "
              f"{l.get('area_oficial_m2', float('nan')) / 1e6:>12,.4f} "
              f"{l.get('area_dissolucao_m2', float('nan')) / 1e6:>12,.4f} "
              f"{l.get('dif_simetrica_m2', float('nan')):>9,.4f} "
              f"{l.get('dif_simetrica_pct', float('nan')):>10.6f}")
    print(f"  coincidem: {comp['coincidem']}")
    print("\nCobertura da união dos setores (sem recorte)")
    for c in coberturas:
        print(f"  {c['referencia']:<34} área mun. {c['area_municipio_m2'] / 1e6:>10,.3f} km²  "
              f"dif. simétrica {c['diferenca_simetrica_m2']:>13,.1f} m² "
              f"({c['diferenca_simetrica_pct']:.4f}%)  fora {c['setores_fora_do_limite_m2']:>12,.1f}  "
              f"descoberto {c['limite_nao_coberto_m2']:>12,.1f}")


if __name__ == "__main__":
    main()
