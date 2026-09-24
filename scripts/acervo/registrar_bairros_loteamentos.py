"""
Registra o arquivo de bairros e loteamentos de Bagé REVISADO pelo responsável.

    data/externos/bairros_loteamentos_bage/bairros_loteamentos_bage.gpkg

USO INTERNO EM PESQUISA. ESTE ARQUIVO NÃO PODE SER PUBLICADO.
------------------------------------------------------------------------------
É trabalho próprio do responsável, a partir de material do geobage (Prefeitura
de Bagé), que não autoriza republicação. Por isso sai com autorizacao_fonte=false
e pode_publicar=false, como as demais camadas derivadas do geobage, e o arquivo
fica fora do git (data/externos/, barrado pelo .gitignore e pelo hook de
pre-commit). Só o `.json` irmão entra no git.

CAMADA DE INTERPRETAÇÃO, FORA DO MANIFESTO
------------------------------------------
Serve para NOMEAR e interpretar no texto dos estudos (em que bairro ou
loteamento cai uma unidade), não para derivar camada nem mapa. Por isso NÃO é
declarada no manifesto de nenhum estudo: declarada, ela tornaria a saída inteira
pode_publicar=false pela regra do mais restritivo (scripts/utils/publicacao.py).
Nome de bairro ou loteamento entra como texto; figura nenhuma usa esta camada.

O script não altera o arquivo (não corrige geometria: o material é do
responsável). Só lê, mede e registra. É idempotente.

Uso:
    python scripts/acervo/registrar_bairros_loteamentos.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import geopandas as gpd  # noqa: E402
import pyogrio  # noqa: E402
import shapely  # noqa: E402

from scripts.utils import catalogo, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402

ID_FONTE = "bairros_loteamentos_revisado"
ARQUIVO = paths.caminho("externos", "bairros_loteamentos_bage", "bairros_loteamentos_bage.gpkg")
PROCEDENCIA = ("arquivo revisado pelo responsável, a partir de material do geobage "
               "(Prefeitura de Bagé, sem autorização de republicação)")
LICENCA = "sem licença de republicação — trabalho do responsável sobre material do geobage"
NOTA = (
    f"Procedência: {PROCEDENCIA}. Nunca versionado neste repositório antes de 2026-09-24. "
    "USO INTERNO EM PESQUISA — sem autorização da fonte para republicação; repositório "
    "público, por isso pode_publicar=false e o arquivo fica fora do git (data/externos/, "
    "barrado pelo .gitignore e pelo hook de pre-commit). CAMADA DE INTERPRETAÇÃO: serve para "
    "nomear bairro e loteamento no texto dos estudos, não para publicar camada nem mapa. NÃO "
    "é declarada no manifesto do A03 (nem de outro estudo): declarada, bloquearia a "
    "publicação do estudo pela regra do mais restritivo. Geometria não corrigida: o material "
    "é do responsável. Uma camada só, mosaico de bairros e loteamentos sem campo de tipo nem "
    "de data de aprovação."
)
TOLERANCIA_SOBREPOSICAO_M2 = 1.0


def inspecionar(arquivo: Path) -> dict:
    """Camadas, campos, CRS, feições, geometrias inválidas e sobreposição entre polígonos."""
    camadas = []
    for nome, tipo in pyogrio.list_layers(arquivo):
        g = gpd.read_file(arquivo, layer=nome)
        invalidas = g[~g.is_valid]
        pares = []
        for i, j in zip(*g.sindex.query(g.geometry, predicate="intersects")):
            if i < j:
                area = g.geometry.iloc[i].intersection(g.geometry.iloc[j]).area
                if area > TOLERANCIA_SOBREPOSICAO_M2:
                    pares.append({"a": g["nome"].iloc[i], "b": g["nome"].iloc[j],
                                  "m2_crs_producao": round(float(area), 1)})
        uniao = g.union_all()
        partes = getattr(uniao, "geoms", [uniao])
        camadas.append({
            "nome": str(nome), "geometria": str(tipo), "feicoes": int(len(g)),
            "crs": ":".join(g.crs.to_authority()) if g.crs else "",
            "campos": [c for c in g.columns if c != g.geometry.name],
            "geometrias_invalidas": int(len(invalidas)),
            "motivos_invalidas": [shapely.is_valid_reason(x) for x in invalidas.geometry],
            "geometrias_vazias_ou_nulas": int((g.geometry.isna() | g.geometry.is_empty).sum()),
            "multipartes": int((g.geometry.apply(lambda x: len(getattr(x, "geoms", [x]))) > 1).sum()),
            "partes_separadas_da_uniao": int(len(partes)),
            "buracos_internos_da_uniao": int(sum(len(p.interiors) for p in partes)),
            "sobreposicao_entre_poligonos": {
                "criterio": f"interseção de área > {TOLERANCIA_SOBREPOSICAO_M2} m² entre dois "
                            "polígonos, medida no CRS do arquivo (ordem de grandeza, não medida "
                            "de área publicada)",
                "pares": pares,
            },
        })
    return {"camadas": camadas}


def main() -> None:
    if not ARQUIVO.is_file():
        raise SystemExit(f"PARADO — arquivo não encontrado: {paths.relativo(ARQUIVO)}")
    inspecao = inspecionar(ARQUIVO)
    inspecao["data_do_arquivo_recebido"] = datetime.fromtimestamp(
        ARQUIVO.stat().st_mtime).astimezone().isoformat(timespec="seconds")
    crs = inspecao["camadas"][0]["crs"]
    meta = metadados.montar(
        ARQUIVO, tema="cadastro", fonte_id=ID_FONTE, versao="revisao_2026-09-24",
        licenca=LICENCA, autorizacao_fonte=False, pode_publicar=False, crs=crs,
        observacoes=NOTA,
    )
    meta["sha256_conteudo"] = sha256_conteudo(ARQUIVO)
    meta["verificacoes"] = inspecao
    irmao = metadados.caminho_irmao(ARQUIVO)
    metadados.escrever(ARQUIVO, meta, sobrescrever=irmao.exists())

    resumo = "; ".join(f"camada {c['nome']}: {c['feicoes']} feições ({c['geometria']}, {c['crs']})"
                       for c in inspecao["camadas"])
    linha = {
        "id_fonte": ID_FONTE,
        "nome": "Bairros e loteamentos de Bagé — arquivo revisado pelo responsável "
                "(bairros_loteamentos_bage.gpkg)",
        "instituicao": "responsável pelo acervo, a partir de material do geobage "
                       "(Prefeitura Municipal de Bagé — setor de GeoInformação)",
        "url": "",
        "data_acesso": "2026-09-24",
        "formato": "gpkg",
        "tamanho_bytes": str(meta["tamanho_bytes"]),
        "sha256": meta["sha256"],
        "licenca": LICENCA,
        "autorizacao_fonte": "false",
        "pode_publicar": "false",
        "observacoes": f"[{resumo}; cópia em {paths.relativo(ARQUIVO)}; "
                       f"script: scripts/acervo/registrar_bairros_loteamentos.py] {NOTA}",
    }
    catalogo.upsert("catalogo_fontes", "id_fonte", [linha])
    print(f"registrado: {paths.relativo(irmao)} ({meta['sha256'][:12]}…, conteúdo "
          f"{meta['sha256_conteudo'][:12]}…); {resumo}")


if __name__ == "__main__":
    main()
