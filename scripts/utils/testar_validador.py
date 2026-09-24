"""
Controles negativos de scripts/utils/validar_catalogos.py.

Um validador que nunca reprovou nada não é um validador — é decoração. Este
script monta, num diretório temporário, catálogos deliberadamente quebrados e
exige que o validador FALHE em cada um, com a mensagem certa. Também roda o
controle positivo (os catálogos reais do repositório), que tem de passar.

Os arquivos de dado nunca são tocados: as cópias quebradas só mudam o CSV, e
o validador é chamado com --raiz apontando para o repositório real, para que
as conferências de existência de arquivo continuem valendo.

Uso:
    python scripts/utils/testar_validador.py
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_FONTES = RAIZ_PROJETO / "data" / "catalogo_fontes.csv"
CAMINHO_CAMADAS = RAIZ_PROJETO / "data" / "catalogo_camadas.csv"
CAMINHO_BIB = RAIZ_PROJETO / "bibliografia" / "bage.bib"
VALIDADOR = RAIZ_PROJETO / "scripts" / "utils" / "validar_catalogos.py"


def ler(caminho: Path) -> tuple[list[str], list[dict]]:
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor.fieldnames or []), list(leitor)


def escrever(caminho: Path, campos: list[str], linhas: list[dict]) -> Path:
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def rodar(fontes: Path, camadas: Path, area_estudo: Path | None = None,
          raiz: Path = RAIZ_PROJETO) -> tuple[int, str]:
    comando = [sys.executable, str(VALIDADOR), "--fontes", str(fontes),
               "--camadas", str(camadas), "--bib", str(CAMINHO_BIB), "--raiz", str(raiz)]
    if area_estudo is not None:
        comando += ["--area-estudo", str(area_estudo)]
    if raiz != RAIZ_PROJETO:
        # raiz temporária só com a camada do controle: o catálogo de legislação
        # real não se resolve nela (os controles L1–L2 cuidam dele)
        comando += ["--legislacao", str(raiz / "sem_catalogo_legislacao.csv")]
    processo = subprocess.run(comando, capture_output=True, text=True)
    return processo.returncode, processo.stdout + processo.stderr


def controles_de_conteudo(tmp: Path, campos: list[str], camadas: list[dict]) -> list[tuple]:
    """sha256 do arquivo x sha256_conteudo, sobre cópias de `limite_municipal`.

    Cada controle monta uma raiz temporária com o GeoPackage (e o .json irmão)
    no mesmo caminho relativo do catálogo, e um catálogo só com essa camada.
    """
    import geopandas as gpd
    import pyogrio

    linha = next(c for c in camadas if c["id_camada"] == "limite_municipal")
    original = RAIZ_PROJETO / linha["arquivo"]
    meta = json.loads(original.with_suffix(".json").read_text(encoding="utf-8"))
    gdf = gpd.read_file(original)

    def montar(nome: str, gravar, sha_conteudo: str) -> tuple[Path, Path]:
        raiz = tmp / nome
        destino = raiz / linha["arquivo"]
        destino.parent.mkdir(parents=True)
        gravar(destino)
        destino.with_suffix(".json").write_text(
            json.dumps({**meta, "sha256_conteudo": sha_conteudo}), encoding="utf-8")
        return raiz, escrever(tmp / f"{nome}.csv", campos, [linha])

    def regravar(g):
        def _gravar(destino: Path) -> None:
            pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": "2000-01-01T00:00:00.000Z"})
            try:
                g.to_file(destino, driver="GPKG", layer="limite_municipal")
            finally:
                pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": None})
        return _gravar

    resultados = []
    sha_conteudo = meta["sha256_conteudo"]

    # (P2) regravado: outros bytes, mesmo dado -> aceito
    raiz, csv_p = montar("conteudo_igual", regravar(gdf), sha_conteudo)
    rc, saida = rodar(CAMINHO_FONTES, csv_p, raiz=raiz)
    resultados.append(("POSITIVO 2: arquivo regravado, mesmo conteúdo", "passar (rc=0)",
                       rc == 0 and "sha256_conteudo confere" in saida, rc, saida))

    # (E) regravado com um atributo alterado -> recusado
    alterado = gdf.copy()
    alterado.loc[0, "NM_MUN"] = "Outro"
    raiz, csv_e = montar("conteudo_alterado", regravar(alterado), sha_conteudo)
    rc, saida = rodar(CAMINHO_FONTES, csv_e, raiz=raiz)
    resultados.append(("NEGATIVO E: arquivo com o dado alterado", "falhar (rc=1)",
                       rc == 1 and "o DADO mudou" in saida, rc, saida))

    # (F) arquivo idêntico, mas sha256_conteudo do .json adulterado -> recusado
    raiz, csv_f = montar("json_adulterado", lambda d: shutil.copy2(original, d), "0" * 64)
    rc, saida = rodar(CAMINHO_FONTES, csv_f, raiz=raiz)
    resultados.append(("NEGATIVO F: sha256_conteudo do .json não confere", "falhar (rc=1)",
                       rc == 1 and "sha256_conteudo do .json irmão não" in saida, rc, saida))
    return resultados


def controles_de_manifesto(tmp: Path, campos: list[str], camadas: list[dict]) -> list[tuple]:
    """manifesto.resolver() com a mesma lógica do validador (conteúdo antes de bytes).

    Roda em processo, sobre cópias de `limite_municipal` numa raiz temporária
    e um catálogo só com essa camada. Nenhum manifesto real é tocado.
    """
    import geopandas as gpd
    import pyogrio
    import yaml

    sys.path.insert(0, str(RAIZ_PROJETO))
    from scripts.utils import manifesto

    linha = next(c for c in camadas if c["id_camada"] == "limite_municipal")
    original = RAIZ_PROJETO / linha["arquivo"]
    meta = json.loads(original.with_suffix(".json").read_text(encoding="utf-8"))
    gdf = gpd.read_file(original)

    def raiz_com(nome: str, gravar) -> tuple[Path, Path]:
        raiz = tmp / f"man_{nome}"
        destino = raiz / linha["arquivo"]
        destino.parent.mkdir(parents=True)
        gravar(destino)
        destino.with_suffix(".json").write_text(json.dumps(meta), encoding="utf-8")
        return raiz, escrever(tmp / f"man_{nome}.csv", campos, [linha])

    def regravar(g):
        def _gravar(destino: Path) -> None:
            pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": "2001-01-01T00:00:00.000Z"})
            try:
                g.to_file(destino, driver="GPKG", layer="limite_municipal")
            finally:
                pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": None})
        return _gravar

    def resolver(nome: str, raiz: Path, cat: Path, entrada: dict) -> str:
        m = tmp / f"man_{nome}.yaml"
        m.write_text(yaml.safe_dump({"estudo": "teste", "pergunta": "-", "status": "reconhecimento",
                                     "camadas": [{"id": "limite_municipal", **entrada}]}),
                     encoding="utf-8")
        c = manifesto.resolver(m, caminho_catalogo=cat, raiz=raiz).camadas[0]
        return f"{c.situacao}: {c.detalhe}"

    alterado = gdf.copy()
    alterado.loc[0, "NM_MUN"] = "Outro"
    copia = lambda d: shutil.copy2(original, d)  # noqa: E731
    sha, conteudo = linha["sha256"], meta["sha256_conteudo"]
    casos = [
        ("POSITIVO M1: mesmo arquivo, sha256 fixado", copia, {"sha256": sha}, "ok"),
        ("POSITIVO M2: regravado, mesmo conteúdo, sha256 do catálogo fixado",
         regravar(gdf), {"sha256": sha}, "ok"),
        ("NEGATIVO M3: regravado com o dado alterado", regravar(alterado), {"sha256": sha}, "divergente"),
        ("POSITIVO M4: sha256_conteudo fixado, arquivo regravado",
         regravar(gdf), {"sha256_conteudo": conteudo}, "ok"),
        ("NEGATIVO M5: sha256_conteudo fixado não confere", copia, {"sha256_conteudo": "0" * 64},
         "divergente"),
    ]
    resultados = []
    for i, (rotulo, gravar, entrada, esperado) in enumerate(casos):
        raiz, cat = raiz_com(str(i), gravar)
        saida = resolver(str(i), raiz, cat, entrada)
        resultados.append((rotulo, esperado, saida.startswith(esperado + ":"), 0, saida))
    return resultados


def controles_de_fontes_brutas(tmp: Path) -> list[tuple]:
    """`fontes_brutas:` — o bloco novo do manifesto (§ 5 das convenções).

    Roda em processo, contra o catálogo de fontes REAL e a raiz real (para o
    controle positivo) ou uma raiz temporária vazia (para o arquivo ausente).
    Nenhum manifesto real é tocado.
    """
    import yaml

    sys.path.insert(0, str(RAIZ_PROJETO))
    from scripts.utils import manifesto

    # um arquivo bruto real, com o sha256 que o .json irmão registrou
    arquivo = "data/raw/vetor/ibge/censo_2022/grade_estatistica/grade_id04.zip"
    rastro = json.loads((RAIZ_PROJETO / arquivo).with_suffix(".json").read_text(encoding="utf-8"))
    boa = {"fonte_id": rastro["fonte_id"], "arquivo": arquivo,
           "versao": rastro["versao"], "sha256": rastro["sha256"]}

    def resolver(nome: str, entradas: list[dict], raiz: Path = RAIZ_PROJETO):
        m = tmp / f"bruta_{nome}.yaml"
        m.write_text(yaml.safe_dump({"estudo": "teste", "pergunta": "-", "status": "planejado",
                                     "camadas": [], "fontes_brutas": entradas}),
                     encoding="utf-8")
        return manifesto.resolver(m, raiz=raiz)

    vazio = tmp / "raiz_vazia"
    vazio.mkdir()
    casos = [
        ("POSITIVO B1: fonte bruta real, sha256 do .json irmão", [boa], RAIZ_PROJETO, "ok"),
        ("NEGATIVO B2: fonte bruta com id fora do catálogo de fontes",
         [{**boa, "fonte_id": "fonte_que_nao_existe"}], RAIZ_PROJETO, "ausente"),
        ("NEGATIVO B3: fonte bruta com sha256 divergente",
         [{**boa, "sha256": "0" * 64}], RAIZ_PROJETO, "divergente"),
        ("NEGATIVO B4: arquivo bruto fora do disco", [boa], vazio, "ausente"),
        ("NEGATIVO B5: fonte bruta sem sha256 fixado",
         [{k: v for k, v in boa.items() if k != "sha256"}], RAIZ_PROJETO, "divergente"),
    ]
    resultados = []
    for i, (rotulo, entradas, raiz, esperado) in enumerate(casos):
        fonte = resolver(str(i), entradas, raiz).fontes_brutas[0]
        obtido = f"{fonte.situacao}: {fonte.detalhe}"
        resultados.append((rotulo, esperado, fonte.situacao == esperado, 0, obtido))

    # bloco vazio e bloco ausente: legítimos, resolvem sem erro e sem entrada
    relatorio = resolver("vazio", [])
    resultados.append(("POSITIVO B6: fontes_brutas vazio é legítimo", "0 entradas, relatório ok",
                       relatorio.fontes_brutas == [] and relatorio.ok, 0,
                       f"entradas={len(relatorio.fontes_brutas)} ok={relatorio.ok}"))
    sem_bloco = tmp / "bruta_sem_bloco.yaml"
    sem_bloco.write_text(yaml.safe_dump({"estudo": "teste", "pergunta": "-",
                                         "status": "planejado", "camadas": []}),
                         encoding="utf-8")
    r = manifesto.resolver(sem_bloco, raiz=RAIZ_PROJETO)
    resultados.append(("POSITIVO B7: manifesto sem o bloco continua válido",
                       "0 entradas, relatório ok", r.fontes_brutas == [] and r.ok, 0,
                       f"entradas={len(r.fontes_brutas)} ok={r.ok}"))
    return resultados


def controles_de_conferencia(tmp: Path, campos: list[str], camadas: list[dict]) -> list[tuple]:
    """Nota de conferência (metadados.reconciliar / catalogo.reconciliar_linha).

    Regrava, numa raiz temporária, uma cópia conferida de `setores_2022` (o
    GeoPackage e o `.json` com o bloco "--- conferência ---") do jeito que os
    scripts de produção regravam: `metadados.montar()` com status pendente e o
    texto do script, e `metadados.escrever()`. Para o catálogo, o `upsert()` e o
    `registrar_regravacao()` rodam sobre uma cópia do CSV. Nada real é tocado.
    """
    from unittest import mock

    import geopandas as gpd
    import pyogrio

    sys.path.insert(0, str(RAIZ_PROJETO))
    from scripts.utils import catalogo, metadados, paths
    from scripts.utils.conteudo import sha256_conteudo

    linha = next(c for c in camadas if c["id_camada"] == "setores_2022")
    original = RAIZ_PROJETO / linha["arquivo"]
    meta = metadados.ler(original)
    bloco = metadados.bloco_conferencia(meta["observacoes"])
    if meta["status_conferencia"] != "conferido" or not bloco:
        return [("PRÉ-CONDIÇÃO: setores_2022 conferido e com nota", "conferido + bloco",
                 False, 1, "setores_2022 não está conferido com bloco — controles sem base")]

    def copia(nome: str, alterar: bool) -> Path:
        destino = tmp / f"conf_{nome}" / original.name
        destino.parent.mkdir(parents=True)
        if alterar:
            gdf = gpd.read_file(original)
            gdf.loc[0, "NM_MUN"] = "Outro"
            pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": "2002-01-01T00:00:00.000Z"})
            try:
                gdf.to_file(destino, driver="GPKG")
            finally:
                pyogrio.set_gdal_config_options({"OGR_CURRENT_DATE": None})
        else:
            shutil.copy2(original, destino)
        # o .json de antes da regravação: o conferido, com a nota
        metadados.caminho_irmao(destino).write_text(json.dumps(meta), encoding="utf-8")
        return destino

    def regravar(destino: Path, status: str = "pendente") -> dict:
        dados = metadados.montar(
            destino, tema="limites", fonte_id=meta["fonte_id"], versao=meta["versao"],
            crs=meta["crs"], licenca=meta["licenca"], autorizacao_fonte=True,
            pode_publicar=False, status_conferencia=status, observacoes="texto do script.")
        dados["sha256_conteudo"] = sha256_conteudo(destino)
        metadados.escrever(destino, dados, sobrescrever=True)
        return metadados.ler(destino)

    def resumo(d: dict) -> str:
        return (f"status={d['status_conferencia']} pode_publicar={d['pode_publicar']} "
                f"bloco={'sim' if metadados.bloco_conferencia(d['observacoes']) else 'não'}")

    resultados = []

    # (C1) .json: mesmo conteúdo -> preserva status, pode_publicar e a nota
    d = regravar(copia("igual", alterar=False))
    ok = (d["status_conferencia"] == "conferido" and d["pode_publicar"] is True
          and metadados.bloco_conferencia(d["observacoes"]) == bloco
          and d["observacoes"].startswith("texto do script."))
    resultados.append(("POSITIVO C1: .json regravado sem mudança preserva a nota",
                       "conferido, true, bloco intacto", ok, 0, resumo(d)))

    # (C2) .json: dado alterado -> despromove e remove a nota
    d = regravar(copia("alterado", alterar=True))
    ok = (d["status_conferencia"] == "pendente" and d["pode_publicar"] is False
          and metadados.bloco_conferencia(d["observacoes"]) is None)
    resultados.append(("NEGATIVO C2: .json regravado com o dado alterado despromove",
                       "pendente, false, sem bloco", ok, 0, resumo(d)))

    # (C3) regravação nunca promove: .json pendente + dicionário dizendo conferido
    destino = copia("sem_promocao", alterar=False)
    metadados.caminho_irmao(destino).write_text(
        json.dumps({**meta, "status_conferencia": "pendente", "pode_publicar": False,
                    "observacoes": metadados.sem_bloco(meta["observacoes"])}),
        encoding="utf-8")
    d = regravar(destino, status="conferido")
    resultados.append(("NEGATIVO C3: regravação não promove", "pendente, false",
                       d["status_conferencia"] == "pendente" and d["pode_publicar"] is False,
                       0, resumo(d)))

    # catálogo: cópia do CSV real, apontada por paths.caminho durante o controle
    def catalogo_tmp(nome: str) -> Path:
        return escrever(tmp / f"conf_cat_{nome}.csv", campos, [dict(c) for c in camadas])

    def com_catalogo(csv_tmp: Path, funcao):
        real = paths.caminho
        def caminho(nome, *extras):
            return csv_tmp if nome == "catalogo_camadas" else real(nome, *extras)
        with mock.patch.object(paths, "caminho", caminho):
            funcao()
        return next(l for l in ler(csv_tmp)[1] if l["id_camada"] == "setores_2022")

    def resumo_linha(l: dict) -> str:
        return (f"status={l['status_conferencia']} pode_publicar={l['pode_publicar']} "
                f"bloco={'sim' if metadados.bloco_conferencia(l['observacoes']) else 'não'}")

    nova = {**linha, "status_conferencia": "pendente", "pode_publicar": "false",
            "observacoes": "texto do script."}

    # (C4) catálogo: upsert com o mesmo conteúdo -> preserva
    l = com_catalogo(catalogo_tmp("igual"), lambda: catalogo.upsert(
        "catalogo_camadas", "id_camada", [nova], mesmo_conteudo={"setores_2022": True}))
    ok = (l["status_conferencia"] == "conferido" and l["pode_publicar"] == "true"
          and metadados.bloco_conferencia(l["observacoes"]) == bloco)
    resultados.append(("POSITIVO C4: catálogo regravado sem mudança preserva a nota",
                       "conferido, true, bloco intacto", ok, 0, resumo_linha(l)))

    # (C5) catálogo: upsert com dado novo -> despromove
    l = com_catalogo(catalogo_tmp("alterado"), lambda: catalogo.upsert(
        "catalogo_camadas", "id_camada", [{**nova, "sha256": "0" * 64}],
        mesmo_conteudo={"setores_2022": False}))
    ok = (l["status_conferencia"] == "pendente" and l["pode_publicar"] == "false"
          and metadados.bloco_conferencia(l["observacoes"]) is None)
    resultados.append(("NEGATIVO C5: catálogo regravado com o dado alterado despromove",
                       "pendente, false, sem bloco", ok, 0, resumo_linha(l)))

    # (C6) catálogo: sem decisão de conteúdo, sha256 novo -> despromove (fallback)
    l = com_catalogo(catalogo_tmp("sem_decisao"), lambda: catalogo.upsert(
        "catalogo_camadas", "id_camada", [{**nova, "sha256": "0" * 64}]))
    resultados.append(("NEGATIVO C6: catálogo com sha256 novo e sem decisão despromove",
                       "pendente, false", l["status_conferencia"] == "pendente"
                       and l["pode_publicar"] == "false", 0, resumo_linha(l)))

    # (C7) registrar_regravacao (produtor que não monta a linha, ex. vetor_ibge)
    csv_c7 = catalogo_tmp("regravacao")
    l = com_catalogo(csv_c7, lambda: catalogo.registrar_regravacao(
        RAIZ_PROJETO / linha["arquivo"], "0" * 64, mesmo_conteudo=False))
    ok = (l["status_conferencia"] == "pendente" and l["sha256"] == "0" * 64
          and metadados.bloco_conferencia(l["observacoes"]) is None)
    resultados.append(("NEGATIVO C7: registrar_regravacao com dado novo despromove",
                       "pendente, sha256 novo, sem bloco", ok, 0, resumo_linha(l)))

    # (C8) validador: nota de conferência em linha pendente é erro
    quebrada = [dict(c) for c in camadas]
    for c in quebrada:
        if c["id_camada"] == "setores_2022":
            c.update(status_conferencia="pendente", pode_publicar="false")
    rc, saida = rodar(CAMINHO_FONTES, escrever(tmp / "conf_bloco_pendente.csv", campos, quebrada))
    resultados.append(("NEGATIVO C8: nota de conferência em camada pendente", "falhar (rc=1)",
                       rc == 1 and "a despromoção tem de remover a nota" in saida, rc, saida))
    return resultados


def controles_de_publicacao(tmp: Path, campos_fontes: list[str], fontes: list[dict]) -> list[tuple]:
    """publicacao.pode_publicar_estudo: o mais restritivo vale para camadas E fontes brutas.

    Manifesto temporário com `limite_municipal` e uma fonte bruta real; o
    negativo usa uma cópia do catálogo de fontes com essa fonte em
    pode_publicar=false. Nenhum manifesto nem catálogo real é tocado.
    """
    import yaml

    sys.path.insert(0, str(RAIZ_PROJETO))
    from scripts.utils import metadados, publicacao

    _, camadas = ler(CAMINHO_CAMADAS)
    limite = next(c for c in camadas if c["id_camada"] == "limite_municipal")
    arquivo = "data/raw/vetor/ibge/censo_2022/grade_estatistica/grade_id04.zip"
    rastro = metadados.ler(RAIZ_PROJETO / arquivo)
    fonte_id = rastro["fonte_id"]
    manifesto_tmp = tmp / "pub_manifesto.yaml"
    manifesto_tmp.write_text(yaml.safe_dump({
        "estudo": "teste", "pergunta": "-", "status": "planejado",
        "camadas": [{"id": "limite_municipal", "versao": limite["versao"],
                     "sha256": limite["sha256"]}],
        "fontes_brutas": [{"fonte_id": fonte_id, "arquivo": arquivo,
                           "versao": rastro["versao"], "sha256": rastro["sha256"]}],
    }), encoding="utf-8")

    restrita = [dict(f) for f in fontes]
    for f in restrita:
        if f["id_fonte"] == fonte_id:
            f["pode_publicar"] = "false"
    fontes_restritas = escrever(tmp / "pub_fontes_restritas.csv", campos_fontes, restrita)

    base = next(f for f in fontes if f["id_fonte"] == fonte_id)
    resultados = []
    if str(base.get("pode_publicar", "")).strip().lower() == "true" and \
            str(limite.get("pode_publicar", "")).strip().lower() == "true":
        d = publicacao.pode_publicar_estudo("teste", caminho=manifesto_tmp)
        resultados.append(("POSITIVO P1: camada e fonte bruta publicáveis", "pode_publicar=true",
                           d.pode_publicar, 0, d.motivo))
    d = publicacao.pode_publicar_estudo("teste", caminho=manifesto_tmp,
                                        caminho_catalogo_fontes=fontes_restritas)
    ok = (not d.pode_publicar and any(b.startswith(f"fonte bruta {fonte_id}")
                                      and "pode_publicar=false" in b for b in d.bloqueios))
    resultados.append(("NEGATIVO P2: fonte bruta com pode_publicar=false bloqueia o estudo",
                       "pode_publicar=false, bloqueio na fonte", ok, 0,
                       f"{d.motivo} | {d.bloqueios}"))

    # regra do vácuo: vazio é camadas E fontes_brutas vazios
    def so_fontes(nome: str, entradas: list[dict]) -> Path:
        m = tmp / f"pub_{nome}.yaml"
        m.write_text(yaml.safe_dump({"estudo": "teste", "pergunta": "-", "status": "planejado",
                                     "camadas": [], "fontes_brutas": entradas}),
                     encoding="utf-8")
        return m
    entrada = {"fonte_id": fonte_id, "arquivo": arquivo, "versao": rastro["versao"],
               "sha256": rastro["sha256"]}
    if str(base.get("pode_publicar", "")).strip().lower() == "true":
        d = publicacao.pode_publicar_estudo("teste", caminho=so_fontes("so_fontes", [entrada]))
        resultados.append(("POSITIVO V1: só fontes brutas, todas publicáveis", "pode_publicar=true",
                           d.pode_publicar, 0, d.motivo))
    d = publicacao.pode_publicar_estudo("teste", caminho=so_fontes("vazio", []))
    resultados.append(("NEGATIVO V2: camadas E fontes_brutas vazios (vácuo)", "pode_publicar=false",
                       not d.pode_publicar and "nenhuma entrada" in d.motivo, 0, d.motivo))
    return resultados


def controles_de_promocao(tmp: Path) -> list[tuple]:
    """scripts/utils/promover.py por linha de comando, num repositório temporário.

    Copia scripts/, config/, os dois catálogos e os produtos usados (distritos
    e área de estudo) para uma raiz temporária — `paths.RAIZ` sai da posição
    do código, então o comando roda contra a cópia. Nada real é tocado.
    """
    sys.path.insert(0, str(RAIZ_PROJETO))
    from scripts.utils import metadados

    distritos = "data/acervo/limites/distritos_ibge-censo_2022_distrito.gpkg"
    area = "config/area_estudo.geojson"

    def repo(nome: str) -> Path:
        raiz = tmp / f"prom_{nome}"
        shutil.copytree(RAIZ_PROJETO / "scripts", raiz / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(RAIZ_PROJETO / "config", raiz / "config")
        for rel in ("data/catalogo_camadas.csv", "data/catalogo_fontes.csv", distritos,
                    str(Path(distritos).with_suffix(".json"))):
            (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ_PROJETO / rel, raiz / rel)
        # despromove as cópias: é o estado de quem vai ser promovido
        for rel in (distritos, area):
            j = (raiz / rel).with_suffix(".json")
            m = json.loads(j.read_text(encoding="utf-8"))
            m.update(status_conferencia="pendente", pode_publicar=False,
                     observacoes=metadados.sem_bloco(m["observacoes"]))
            j.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        caminho = raiz / "data/catalogo_camadas.csv"
        campos, linhas = ler(caminho)
        for l in linhas:
            if l["id_camada"] == "distritos_2022":
                l.update(status_conferencia="pendente", pode_publicar="false",
                         observacoes=metadados.sem_bloco(l["observacoes"]))
        escrever(caminho, campos, linhas)
        return raiz

    def promover(raiz: Path, ident: str, nota: str = "nota de teste") -> tuple[int, str]:
        p = subprocess.run([sys.executable, str(raiz / "scripts/utils/promover.py"),
                            "--id", ident, "--nota", nota], capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def estado(raiz: Path, rel: str, id_camada: str | None) -> tuple:
        m = json.loads((raiz / rel).with_suffix(".json").read_text(encoding="utf-8"))
        linha = None
        if id_camada:
            linha = next(l for l in ler(raiz / "data/catalogo_camadas.csv")[1]
                         if l["id_camada"] == id_camada)
        return (m["status_conferencia"], m["pode_publicar"],
                metadados.bloco_conferencia(m["observacoes"]),
                linha and (linha["status_conferencia"], linha["pode_publicar"],
                           metadados.bloco_conferencia(linha["observacoes"])))

    resultados = []
    bloco = metadados.montar_bloco("nota de teste")

    # (PR1) promoção válida de camada do catálogo
    raiz = repo("valida")
    rc, saida = promover(raiz, "distritos_2022")
    obtido = estado(raiz, distritos, "distritos_2022")
    resultados.append(("POSITIVO PR1: promoção válida (camada do catálogo)",
                       "rc=0; .json e catálogo conferidos, true, com a nota",
                       rc == 0 and obtido == ("conferido", True, bloco, ("conferido", "true", bloco)),
                       rc, f"{saida.strip()} | {obtido[:2]} cat={obtido[3] and obtido[3][:2]}"))

    # (PR2) promoção válida de produto fora do catálogo, por caminho
    rc, saida = promover(raiz, area)
    obtido = estado(raiz, area, None)
    resultados.append(("POSITIVO PR2: promoção válida (config/area_estudo.geojson)",
                       "rc=0; .json conferido, true, com a nota",
                       rc == 0 and obtido[:3] == ("conferido", True, bloco), rc,
                       f"{saida.strip()} | {obtido[:2]}"))

    # (PR3) hash divergente: sha256_conteudo do .json adulterado
    raiz = repo("hash")
    j = (raiz / distritos).with_suffix(".json")
    m = json.loads(j.read_text(encoding="utf-8"))
    m["sha256_conteudo"] = "0" * 64
    j.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    antes = estado(raiz, distritos, "distritos_2022")
    rc, saida = promover(raiz, "distritos_2022")
    resultados.append(("NEGATIVO PR3: hash divergente", "rc=1, 'hash divergente', nada gravado",
                       rc == 1 and "hash divergente" in saida
                       and estado(raiz, distritos, "distritos_2022") == antes, rc, saida))

    # (PR4) fonte com autorizacao_fonte=false
    raiz = repo("fonte")
    caminho = raiz / "data/catalogo_fontes.csv"
    campos, linhas = ler(caminho)
    for l in linhas:
        if l["id_fonte"] == "ibge_malha_distritos_2022":
            l["autorizacao_fonte"] = "false"
    escrever(caminho, campos, linhas)
    antes = estado(raiz, distritos, "distritos_2022")
    rc, saida = promover(raiz, "distritos_2022")
    resultados.append(("NEGATIVO PR4: fonte com autorizacao_fonte=false",
                       "rc=1, 'autorizacao_fonte=false', nada gravado",
                       rc == 1 and "autorizacao_fonte=false" in saida
                       and estado(raiz, distritos, "distritos_2022") == antes, rc, saida))

    # (PR5) produto inexistente
    rc, saida = promover(raiz, "camada_que_nao_existe")
    resultados.append(("NEGATIVO PR5: produto inexistente", "rc=1, 'produto inexistente'",
                       rc == 1 and "produto inexistente" in saida, rc, saida))
    return resultados


def controles_de_vetor_ibge(tmp: Path) -> list[tuple]:
    """vetor_ibge.py --local: conteúdo divergente do registrado ABORTA sem gravar."""
    sys.path.insert(0, str(RAIZ_PROJETO))
    from scripts.download import vetor_ibge
    from scripts.utils import paths
    from scripts.utils.hashes import sha256_arquivo

    caminho_zip, meta_zip, _ = vetor_ibge.zip_local(vetor_ibge.uf_de(paths.codigo_ibge()), None)
    municipio = vetor_ibge.recortar_municipio(caminho_zip, paths.codigo_ibge())
    destino = tmp / "vetor_ibge" / "limite.gpkg"
    destino.parent.mkdir()
    vetor_ibge._gravar(municipio, destino, "2003-01-01T00:00:00.000Z")
    sha_antes = sha256_arquivo(destino)
    try:
        vetor_ibge.gravar_gpkg(municipio, destino,
                               vetor_ibge.carimbo_gpkg(vetor_ibge.last_modified_de(meta_zip)),
                               exigir_conteudo="0" * 64)
        abortou, msg = False, "não abortou"
    except vetor_ibge.ConteudoDivergente as erro:
        abortou, msg = True, str(erro)
    return [("NEGATIVO VI1: vetor_ibge --local com conteúdo divergente", "aborta, nada gravado",
             abortou and sha256_arquivo(destino) == sha_antes, 0, msg)]


def controles_de_legislacao(tmp: Path) -> list[tuple]:
    """(L1) sha256 da linha diverge do .json/arquivo; (L2) situação fora do domínio."""
    from scripts.utils import paths

    caminho = paths.caminho("catalogo_legislacao")
    if not caminho.exists():
        return []
    campos, linhas = ler(caminho)

    def rodar_leg(csv_tmp: Path) -> tuple[int, str]:
        comando = [sys.executable, str(VALIDADOR), "--bib", str(CAMINHO_BIB),
                   "--legislacao", str(csv_tmp)]
        processo = subprocess.run(comando, capture_output=True, text=True)
        return processo.returncode, processo.stdout + processo.stderr

    resultados = []
    l1 = [dict(l) for l in linhas]
    l1[0]["sha256"] = "0" * 64
    rc, saida = rodar_leg(escrever(tmp / "legislacao_sha.csv", campos, l1))
    resultados.append(("NEGATIVO L1: norma com sha256 que não é o do arquivo", "falhar (rc=1)",
                       rc == 1 and "sha256 da linha difere do .json irmão" in saida, rc, saida))
    l2 = [dict(l) for l in linhas]
    l2[0]["situacao"] = "provavelmente vigente"
    rc, saida = rodar_leg(escrever(tmp / "legislacao_situacao.csv", campos, l2))
    resultados.append(("NEGATIVO L2: situação fora do domínio", "falhar (rc=1)",
                       rc == 1 and "situacao" in saida and "fora do domínio" in saida, rc, saida))
    return resultados


def main() -> None:
    campos_fontes, fontes = ler(CAMINHO_FONTES)
    campos_camadas, camadas = ler(CAMINHO_CAMADAS)
    if not camadas:
        raise SystemExit("catalogo_camadas.csv está vazio — nada a testar.")

    resultados = []

    with tempfile.TemporaryDirectory(prefix="validador-controles-") as tmp:
        tmp = Path(tmp)

        # controle positivo: os catálogos reais têm de passar
        rc, saida = rodar(CAMINHO_FONTES, CAMINHO_CAMADAS)
        resultados.append(("POSITIVO: catálogos reais do repositório",
                           "passar (rc=0)", rc == 0, rc, saida))

        # (A) camada aponta para um id de fonte que não existe
        camadas_a = [dict(c) for c in camadas]
        camadas_a[0]["fonte_id"] = "fonte_que_nao_existe"
        arquivo_a = escrever(tmp / "camadas_fonte_inexistente.csv", campos_camadas, camadas_a)
        rc, saida = rodar(CAMINHO_FONTES, arquivo_a)
        resultados.append(("NEGATIVO A: id de fonte inexistente", "falhar (rc=1)",
                           rc == 1 and "não existe em catalogo_fontes.csv" in saida, rc, saida))

        # (B) camada cita uma chave bibliográfica que não está no .bib
        camadas_b = [dict(c) for c in camadas]
        camadas_b[0]["referencias_bib"] = "chave2099inexistente"
        arquivo_b = escrever(tmp / "camadas_bib_inexistente.csv", campos_camadas, camadas_b)
        rc, saida = rodar(CAMINHO_FONTES, arquivo_b)
        resultados.append(("NEGATIVO B: chave bibliográfica inexistente", "falhar (rc=1)",
                           rc == 1 and "chave bibliográfica" in saida, rc, saida))

        # (C) camada publicada cuja fonte está sem licença
        fontes_c = [dict(f) for f in fontes]
        id_fonte_da_camada = (camadas[0]["fonte_id"] or "").split(";")[0].strip()
        for fonte in fontes_c:
            if fonte["id_fonte"] == id_fonte_da_camada:
                fonte["licenca"] = ""
        arquivo_c = escrever(tmp / "fontes_sem_licenca.csv", campos_fontes, fontes_c)
        rc, saida = rodar(arquivo_c, CAMINHO_CAMADAS)
        resultados.append(("NEGATIVO C: camada publicada com fonte sem licença", "falhar (rc=1)",
                           rc == 1 and "não tem licença declarada" in saida, rc, saida))

        # (D) área de estudo marcada publicável sem ter sido conferida
        area = RAIZ_PROJETO / "config" / "area_estudo.geojson"
        area_d = tmp / "area_estudo.geojson"
        shutil.copy2(area, area_d)
        meta_d = json.loads(area.with_suffix(".json").read_text(encoding="utf-8"))
        meta_d.update(pode_publicar=True, status_conferencia="pendente")
        area_d.with_suffix(".json").write_text(json.dumps(meta_d), encoding="utf-8")
        rc, saida = rodar(CAMINHO_FONTES, CAMINHO_CAMADAS, area_d)
        resultados.append(("NEGATIVO D: área de estudo publicável e pendente", "falhar (rc=1)",
                           rc == 1 and "área de estudo" in saida and "pode_publicar=true" in saida,
                           rc, saida))

        resultados += controles_de_conteudo(tmp, campos_camadas, camadas)
        resultados += controles_de_manifesto(tmp, campos_camadas, camadas)
        resultados += controles_de_fontes_brutas(tmp)
        resultados += controles_de_conferencia(tmp, campos_camadas, camadas)
        resultados += controles_de_publicacao(tmp, campos_fontes, fontes)
        resultados += controles_de_promocao(tmp)
        resultados += controles_de_vetor_ibge(tmp)
        resultados += controles_de_legislacao(tmp)

    print("=" * 78)
    print("CONTROLES DO VALIDADOR DE CATÁLOGOS")
    print("=" * 78)
    for nome, esperado, ok, rc, saida in resultados:
        print(f"\n[{'OK' if ok else 'FALHOU'}] {nome}")
        print(f"        esperado: {esperado} | obtido: rc={rc}")
        for linha in saida.strip().splitlines():
            if linha.startswith(("ERRO", "FALHOU", "OK —", "ok:", "divergente:")):
                print(f"        {linha}")

    total_ok = sum(1 for _, _, ok, _, _ in resultados if ok)
    print("\n" + "=" * 78)
    print(f"{total_ok}/{len(resultados)} controles no resultado esperado")
    if total_ok != len(resultados):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
