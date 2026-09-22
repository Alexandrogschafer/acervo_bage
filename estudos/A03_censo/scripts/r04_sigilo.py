"""
A03 — reconhecimento, item 4: supressão de valores (sigilo) por setor.

Para cada conceito × censo do mapa de variáveis (scripts/variaveis.json, montado
a partir da documentação de cada censo), conta os setores com ao menos uma
célula suprimida nas variáveis do conceito, separando urbano e rural.

Marcadores contados como supressão: "X" (sigilo declarado em 2010 e 2022),
célula vazia/nula (a forma de 2000) e "." — cada um contado à parte. Setor
que existe na tabela básica e não tem linha no arquivo do tema conta como
"sem linha".

Escreve derivados/r04_sigilo.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

ESTUDO = Path(__file__).resolve().parents[1]
BAGE = ESTUDO / "derivados" / "bage"
MAPA = json.loads((ESTUDO / "scripts" / "variaveis.json").read_text(encoding="utf-8"))

BASICO = {  # arquivo, coluna do código, coluna da situação
    "2000": ("Basico_RS__BASICO_RS.csv", "Cod_setor", "Situacao"),
    "2010": ("Basico_RS.csv", "Cod_setor", "Situacao_setor"),
    "2022": ("Agregados_por_setores_basico.csv", "CD_SETOR", "SITUACAO"),
}


def ler(ano: str, arquivo: str) -> pd.DataFrame:
    return pd.read_csv(BAGE / f"c{ano}" / arquivo, sep=";", dtype=str, keep_default_na=False)


def coluna_setor(df: pd.DataFrame) -> str:
    return next(c for c in df.columns if c.lower() in ("cod_setor", "cd_setor", "setor"))


def urbano(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    return s.isin(["1", "2", "3"]) | s.str.lower().str.startswith("urb")


def main() -> None:
    universo = {}
    for ano, (arq, cod, sit) in BASICO.items():
        b = ler(ano, arq)
        universo[ano] = pd.Series(urbano(b[sit]).values, index=b[cod].str.strip())

    resultado = {}
    for conceito, anos in MAPA.items():
        resultado[conceito] = {}
        for ano, info in anos.items():
            if not info.get("arquivo") or not info.get("variaveis"):
                resultado[conceito][ano] = {"status": info.get("status"), "avaliado": False}
                continue
            df = ler(ano, info["arquivo"])
            df = df.set_index(df[coluna_setor(df)].str.strip())
            u = universo[ano]
            sem_linha = sorted(set(u.index) - set(df.index))
            v = df.reindex(u.index)[info["variaveis"]].fillna("<sem linha>").apply(lambda c: c.str.strip())
            marcas = {"X": v.eq("X"), "vazio": v.eq(""), ".": v.eq(".")}
            qualquer = marcas["X"] | marcas["vazio"] | marcas["."]
            setor_supr = qualquer.any(axis=1)
            setor_todo = qualquer.all(axis=1)
            resultado[conceito][ano] = {
                "status": info["status"], "avaliado": True, "arquivo": info["arquivo"],
                "n_variaveis": len(info["variaveis"]), "setores": int(len(u)),
                "setores_sem_linha_no_tema": sem_linha,
                "setores_com_supressao": int(setor_supr.sum()),
                "urbanos_com_supressao": f"{int(setor_supr[u].sum())}/{int(u.sum())}",
                "rurais_com_supressao": f"{int(setor_supr[~u].sum())}/{int((~u).sum())}",
                "setores_com_todas_suprimidas": int(setor_todo.sum()),
                "celulas_suprimidas_pct": round(100 * float(qualquer.values.mean()), 2),
                "por_marcador": {k: int(m.values.sum()) for k, m in marcas.items()},
            }
    (ESTUDO / "derivados" / "r04_sigilo.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    for conceito, anos in resultado.items():
        for ano, r in anos.items():
            if r.get("avaliado"):
                print(f"{conceito:<24} {ano}  setores c/ supressão {r['setores_com_supressao']:>3}/{r['setores']}"
                      f"  urb {r['urbanos_com_supressao']:>7}  rur {r['rurais_com_supressao']:>6}"
                      f"  todas {r['setores_com_todas_suprimidas']:>3}  células {r['celulas_suprimidas_pct']:>5}%"
                      f"  {r['por_marcador']}  sem linha {len(r['setores_sem_linha_no_tema'])}")
            else:
                print(f"{conceito:<24} {ano}  — {r['status']}")


if __name__ == "__main__":
    main()
