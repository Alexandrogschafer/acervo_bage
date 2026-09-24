"""
Importa por CÓPIA os shapefiles de evolução urbana do REVIA_BG.

    <REVIA_BG>/dados/externos/evolucao_urbana/*   ->  data/externos/revia_bg/evolucao_urbana/

Versão fixada: `evolucao_urbana_evo_v1` do `config/base.yml` do REVIA_BG, que
registra o sha256 de cada um dos 48 arquivos. A origem é conferida contra esse
registro ANTES de copiar, a cópia contra a origem, e a origem de novo no fim.
Qualquer divergência aborta sem gravar metadado: se o REVIA_BG mudou, a versão
fixada não é mais a que está lá, e decidir o que fazer é do responsável.

REGIME: NÃO REDISTRIBUIR
------------------------
Os polígonos foram convertidos (CAD -> shapefile, ArcGIS 10.3, 2017) da prancha
03/18 "Condicionantes – Evolução Urbana" do dossiê de tombamento do IPHAN
(SICG, 2009), que não tem licença registrada. O docs/LICENCAS.md do REVIA_BG diz
"não redistribuir os polígonos". Por isso: autorizacao_fonte=false,
pode_publicar=false, arquivos fora do git (data/externos/, .gitignore e hook).

CAMADA DE INTERPRETAÇÃO, FORA DO MANIFESTO
------------------------------------------
Como bairros_loteamentos: serve para DATAR e interpretar no texto dos estudos
(em que período de ocupação cai uma unidade), não para derivar camada nem mapa.
NÃO é declarada no manifesto do A03: declarada, tornaria a saída inteira
pode_publicar=false pela regra do mais restritivo (scripts/utils/publicacao.py).

ferrovia.shp chega SEM .prj. É copiada (o conjunto fica íntegro) e registrada
com a anomalia, mas NÃO deve ser usada: o CRS dela não está declarado.

Os anos nos nomes dos arquivos (1825, 1850, …) foram atribuídos na conversão
CAD e NÃO constam do mapa, que rotula os períodos por descrição; a
correspondência vai no `.json` de cada período.

Uso (só lê o REVIA_BG):
    python scripts/acervo/importar_evolucao_urbana_revia.py --revia ~/projetos/rede_viaria_bage
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pyogrio  # noqa: E402
import shapely  # noqa: E402
import yaml  # noqa: E402

from scripts.utils import catalogo, metadados, paths  # noqa: E402
from scripts.utils.conteudo import sha256_conteudo  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

ID_FONTE = "revia_bg_evolucao_urbana"
VERSAO = "evolucao_urbana_evo_v1"
DATA_COPIA = "2026-09-24"
SUBDIR_ORIGEM = Path("dados") / "externos" / "evolucao_urbana"
DESTINO = paths.caminho("externos", "revia_bg", "evolucao_urbana")
LICENCA = ("sem licença registrada — polígonos convertidos da prancha 03/18 do dossiê de "
           "tombamento do IPHAN (SICG, 2009); o REVIA_BG registra 'não redistribuir os polígonos'")

# rótulo da legenda do mapa (forma do REVIA_BG, estudos/A03_morfometria_rede_urbana/
# scripts/rotulos_evo.py); os anos do nome do arquivo são da conversão CAD
PERIODOS = {
    "urbano_1825": ("p1_1820", "primeiro loteamento (década de 1820)"),
    "urbano_1850": ("p2_xix", "traçado na metade do século XIX"),
    "urbano_1900": ("p3_xx", "traçado do início do século XX"),
    "urbano_1938": ("p4_1938", "traçado em 1938"),
    "urbano_1960": ("p5_1960", "traçado em 1960"),
    "urbano_1961_1970": ("p6_1970", "traçado em 1970"),
    "urbano_1970_2001": ("p7_2001", "traçado em 2001"),
}
EXTRAS = {
    "urbano_acampamentos": "acampamento (1811) — no mapa é símbolo de ponto; não é período",
    "charqueadas_evolucao": "charqueadas — áreas nomeadas no desenho; não é período",
    "ferrovia": "ferrovia — SEM .prj: CRS não declarado; NÃO USAR",
}

NOTA = (
    "Cópia do REVIA_BG (dados/externos/evolucao_urbana/, versão evolucao_urbana_evo_v1 do "
    "config/base.yml de lá), com sha256 de cada componente conferido contra aquele registro. "
    "Origem: prancha 03/18 'Condicionantes – Evolução Urbana', dossiê de tombamento do IPHAN "
    "(SICG, out/2009, SNA Arquitetura, 1:25.000), convertida de CAD para shapefile pelo "
    "responsável (ArcGIS 10.3, 2017). NÃO REDISTRIBUIR: o docs/LICENCAS.md do REVIA_BG diz 'não "
    "redistribuir os polígonos'; por isso autorizacao_fonte=false, pode_publicar=false e fora do "
    "git. CAMADA DE INTERPRETAÇÃO: serve para DATAR e interpretar no texto (período de ocupação), "
    "não para publicar camada nem mapa. NÃO é declarada no manifesto do A03: declarada, "
    "bloquearia a publicação do estudo pela regra do mais restritivo. Os polígonos até 1960 são "
    "cumulativos (1825 ⊂ 1850 ⊂ 1900 ⊂ 1938, e 1960 cobre 74,5 % de 1938) e os dois últimos são "
    "manchas destacadas: quem usa deriva o INCREMENTO de cada período (polígono menos a união dos "
    "anteriores), como no REVIA_BG."
)


def git(revia: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(revia), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def registro(revia: Path) -> dict[str, dict]:
    """Os arquivos fixados em evolucao_urbana_evo_v1, por nome."""
    base = yaml.safe_load((revia / "config" / "base.yml").read_text(encoding="utf-8"))
    return {Path(a["caminho"]).name: a for a in base[VERSAO]["arquivos"]}


def conferir_origem(origem: Path, fixados: dict[str, dict]) -> None:
    presentes = {p.name for p in origem.iterdir() if p.is_file()}
    if presentes != set(fixados):
        raise SystemExit(f"PARADO — origem difere do registro {VERSAO}: "
                         f"sobrando {sorted(presentes - set(fixados))}, "
                         f"faltando {sorted(set(fixados) - presentes)}")
    for nome, a in fixados.items():
        if sha256_arquivo(origem / nome) != a["sha256"]:
            raise SystemExit(f"PARADO — {nome}: sha256 da origem difere do fixado em {VERSAO}")


def inspecionar(shp: Path) -> dict:
    info = pyogrio.read_info(shp)
    geoms = pyogrio.read_dataframe(shp).geometry
    return {"feicoes": int(info["features"]), "geometria": str(info["geometry_type"]),
            "crs_declarado": info["crs"] or "SEM .prj",
            "campos": [str(c) for c in info["fields"]],
            "geometrias_invalidas": int((~shapely.is_valid(geoms.values)).sum())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--revia", type=Path, required=True, help="raiz do REVIA_BG (só leitura)")
    args = parser.parse_args()
    revia = args.revia.expanduser().resolve()
    origem = revia / SUBDIR_ORIGEM

    fixados = registro(revia)
    conferir_origem(origem, fixados)
    commit = git(revia, "rev-parse", "HEAD")
    data_commit = git(revia, "log", "-1", "--format=%cI")
    if git(revia, "status", "--porcelain", "--", "config/base.yml"):
        raise SystemExit("PARADO — config/base.yml do REVIA_BG tem alteração não commitada")

    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome in fixados:
        alvo = DESTINO / nome
        if alvo.exists() and sha256_arquivo(alvo) != fixados[nome]["sha256"]:
            raise SystemExit(f"PARADO — {paths.relativo(alvo)} existe com outro conteúdo")
        if not alvo.exists():
            shutil.copy2(origem / nome, alvo)
        if sha256_arquivo(alvo) != fixados[nome]["sha256"]:
            raise SystemExit(f"PARADO — cópia de {nome} diverge do fixado")
    conferir_origem(origem, fixados)  # a origem tem de sair intocada

    total = 0
    for base in [*PERIODOS, *EXTRAS]:
        shp = DESTINO / f"{base}.shp"
        componentes = {n: {"sha256": a["sha256"], "bytes": int(a["bytes"])}
                       for n, a in sorted(fixados.items()) if n.split(".")[0] == base}
        total += sum(c["bytes"] for c in componentes.values())
        inspecao = inspecionar(shp)
        if base in PERIODOS:
            codigo, rotulo = PERIODOS[base]
            papel = f"período '{rotulo}' (código {codigo}); o ano do nome do arquivo não consta do mapa"
        else:
            papel = EXTRAS[base]
        meta = metadados.montar(
            shp, tema="cadastro", fonte_id=ID_FONTE, versao=VERSAO, licenca=LICENCA,
            autorizacao_fonte=False, pode_publicar=False,
            crs=inspecao["crs_declarado"] if inspecao["crs_declarado"] != "SEM .prj" else "",
            observacoes=f"{papel}. {NOTA}",
            data_producao=datetime.fromtimestamp((origem / f"{base}.shp").stat().st_mtime).astimezone(),
            repo_origem="REVIA_BG (rede_viaria_bage)", commit=commit, data_commit=data_commit,
        )
        meta["sha256_conteudo"] = sha256_conteudo(shp)
        meta["verificacoes"] = {**inspecao, "componentes_do_shapefile": componentes,
                                "caminho_na_origem": str(SUBDIR_ORIGEM / f"{base}.shp")}
        metadados.escrever(shp, meta, sobrescrever=metadados.caminho_irmao(shp).exists())
        print(f"{paths.relativo(shp)}: {inspecao['feicoes']} feições, {inspecao['crs_declarado']}")

    linha = {
        "id_fonte": ID_FONTE,
        "nome": "Evolução urbana de Bagé — polígonos por período (cópia do REVIA_BG, "
                f"{VERSAO}), da prancha 03/18 do dossiê de tombamento do IPHAN",
        "instituicao": "REVIA_BG (conversão CAD do responsável) sobre IPHAN / SICG 2009 "
                       "(SNA Arquitetura)",
        "url": "",
        "data_acesso": DATA_COPIA,
        "formato": "shp",
        "tamanho_bytes": str(total),
        "sha256": "",
        "licenca": LICENCA,
        "autorizacao_fonte": "false",
        "pode_publicar": "false",
        "observacoes": f"[{len(fixados)} arquivos, {len(PERIODOS) + len(EXTRAS)} shapefiles, em {paths.relativo(DESTINO)}; "
                       f"sha256 por componente no .json de cada .shp; REVIA_BG commit {commit[:7]}; "
                       "script: scripts/acervo/importar_evolucao_urbana_revia.py; ferrovia.shp sem "
                       f".prj, não usar] {NOTA}",
    }
    catalogo.upsert("catalogo_fontes", "id_fonte", [linha])
    print(f"fonte {ID_FONTE}: {len(fixados)} arquivos, {total} bytes, REVIA_BG {commit[:7]}")


if __name__ == "__main__":
    main()
