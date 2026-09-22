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
