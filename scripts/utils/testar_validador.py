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


def rodar(fontes: Path, camadas: Path) -> tuple[int, str]:
    processo = subprocess.run(
        [sys.executable, str(VALIDADOR), "--fontes", str(fontes),
         "--camadas", str(camadas), "--bib", str(CAMINHO_BIB), "--raiz", str(RAIZ_PROJETO)],
        capture_output=True, text=True,
    )
    return processo.returncode, processo.stdout + processo.stderr


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

    print("=" * 78)
    print("CONTROLES DO VALIDADOR DE CATÁLOGOS")
    print("=" * 78)
    for nome, esperado, ok, rc, saida in resultados:
        print(f"\n[{'OK' if ok else 'FALHOU'}] {nome}")
        print(f"        esperado: {esperado} | obtido: rc={rc}")
        for linha in saida.strip().splitlines():
            if linha.startswith(("ERRO", "FALHOU", "OK —")):
                print(f"        {linha}")

    total_ok = sum(1 for _, _, ok, _, _ in resultados if ok)
    print("\n" + "=" * 78)
    print(f"{total_ok}/{len(resultados)} controles no resultado esperado")
    if total_ok != len(resultados):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
