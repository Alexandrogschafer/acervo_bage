"""
Importa o Censo Demográfico (2000, 2010, 2022) e o CNEFE 2022 para o acervo,
**por cópia** a partir do projeto REVIA_BG (`rede_viaria_bage`).

Por que por cópia, e não por download novo: os arquivos já foram baixados das
fontes oficiais do IBGE em 20/09/2026, navegando as listagens de
`ftp.ibge.gov.br` e `geoftp.ibge.gov.br`, com URL exata, `Last-Modified`,
bytes e sha256 registrados nos `manifesto_censo_<ano>.json` e nos `FONTE.md`
da origem. Rebaixar 986 MiB só produziria arquivos possivelmente diferentes
(o IBGE reedita pacotes) e perderia o vínculo com as medições já feitas sobre
esses hashes. A cópia preserva o hash; é ele que amarra as ressalvas medidas
ao arquivo exato a que elas se referem.

A regra (iv) do CLAUDE.md exige cópia e proíbe leitura direta de outro
projeto. Este script é a implementação dessa regra para o Censo: nunca abre
nada da origem para escrita, e confere o sha256 da origem antes e depois da
cópia — se a origem mudou durante a execução, aborta.

O destino é `data/acervo/censo/`, e não `data/externos/`, porque estes
arquivos são **dado bruto do IBGE, como veio da fonte**, apenas transportado
pelo REVIA_BG: não são camada derivada de outro projeto, e `censo` é um dos
temas do acervo. A procedência da cópia fica registrada em cada `.json` irmão
(`origem_da_copia`) e no catálogo.

(Antes da reestruturação de 2026-09-20 o destino era `data/raw/censo/`; os
arquivos foram movidos, não rebaixados.)

Conferências (nenhuma delas dispensa as outras):

  1. sha256 de cada arquivo da origem contra o registrado no manifesto do ano
     — detecta origem já corrompida antes de copiar;
  2. sha256 da cópia contra o da origem, arquivo a arquivo;
  3. sha256 da origem de novo no fim, contra o do início — a origem tem de
     sair intocada;
  4. bytes e contagem de arquivos conferidos dos dois lados;
  5. colisão de nome de metadado (dois arquivos que gerariam o mesmo `.json`
     irmão na mesma pasta) aborta em vez de sobrescrever em silêncio.

Uso:
    python scripts/download/censo_revia_bg.py --dry-run
    python scripts/download/censo_revia_bg.py
    python scripts/download/censo_revia_bg.py --somente-metadados
    python scripts/download/censo_revia_bg.py --forcar
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROJETO))

from scripts.utils.hashes import sha256_arquivo  # noqa: E402

# Origem: projeto REVIA_BG. Não é caminho de dado deste repositório — é o
# endereço de outro projeto na máquina, e por isso é parametrizável.
ORIGEM_PADRAO = Path.home() / "projetos" / "rede_viaria_bage" / "dados" / "externos" / "censo"
ORIGEM_PROJETO = "REVIA_BG (~/projetos/rede_viaria_bage)"
ORIGEM_RELATIVA = "dados/externos/censo"

DESTINO = RAIZ_PROJETO / "data" / "acervo" / "censo"

ANOS = ("2000", "2010", "2022")

# Arquivos da origem que NÃO são mais copiados: aposentados porque o acervo já
# tem o mesmo dado (mesmo sha256) obtido direto do IBGE por um script próprio.
# caminho relativo na origem -> arquivo que o substitui neste repositório.
# O .json irmão do aposentado fica no destino como rastro (aposentado_em,
# substituido_por); este script não o regrava.
APOSENTADOS: dict[str, str] = {
    "2022/malha/geoftp_malha_territorial/RS_setores_CD2022.gpkg":
        "data/raw/vetor/ibge/censo_2022/RS_setores_CD2022.gpkg "
        "(scripts/download/baixar_malhas_ibge.py)",
}
SCRIPT_RESPONSAVEL = "scripts/download/censo_revia_bg.py"

# Licença: confirmada no próprio servidor que serviu os arquivos, e só ali.
# A página formal de termos (www.ibge.gov.br/acesso-informacao/acoes-e-programas/
# termos-de-uso.html) respondeu HTTP 403 (desafio Cloudflare) em 20/09/2026 e
# NÃO foi lida — não inventar o que ela diz.
LICENCA_DECLARADA = (
    "Dados públicos do IBGE. Declaração literal na raiz dos dois hosts que "
    "serviram os arquivos — https://ftp.ibge.gov.br/ e https://geoftp.ibge.gov.br/ "
    "(HTTP 200, conferido em 2026-09-20): \"Todos os arquivos aqui disponíveis "
    "são públicos.\""
)


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def carregar_manifestos(origem: Path) -> tuple[list[dict], dict]:
    """Lê os manifesto_censo_<ano>.json da origem. Devolve (entradas, por_caminho)."""
    entradas: list[dict] = []
    for ano in ANOS:
        caminho = origem / ano / f"manifesto_censo_{ano}.json"
        if not caminho.exists():
            raise SystemExit(f"ERRO: manifesto ausente na origem: {caminho}")
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        for item in dados.get("arquivos", []):
            item = dict(item)
            item["_manifesto"] = f"{ORIGEM_RELATIVA}/{ano}/manifesto_censo_{ano}.json"
            entradas.append(item)

    por_caminho: dict[str, dict] = {}
    for item in entradas:
        # "caminho" no manifesto é relativo à raiz do REVIA_BG
        caminho = item["caminho"]
        prefixo = ORIGEM_RELATIVA + "/"
        if not caminho.startswith(prefixo):
            raise SystemExit(f"ERRO: caminho inesperado no manifesto: {caminho}")
        relativo = caminho[len(prefixo):]
        if relativo in por_caminho:
            raise SystemExit(f"ERRO: caminho duplicado nos manifestos: {relativo}")
        por_caminho[relativo] = item
    return entradas, por_caminho


def inventariar(origem: Path) -> list[str]:
    """Arquivos da árvore de origem a copiar (menos APOSENTADOS), ordenados."""
    return sorted(
        rel for p in origem.rglob("*")
        if p.is_file() and (rel := str(p.relative_to(origem))) not in APOSENTADOS
    )


def hashear_arvore(origem: Path, relativos: list[str]) -> dict[str, str]:
    return {rel: sha256_arquivo(origem / rel) for rel in relativos}


def host_de(url: str) -> str:
    return url.split("/")[2] if "//" in url else ""


def caminho_metadado(destino_arquivo: Path) -> Path:
    return destino_arquivo.with_suffix(".json")


def montar_metadado(relativo: str, item: dict, sha_copia: str,
                    tamanho_copia: int, origem: Path) -> dict:
    ano = item["ano"]
    url = item["url"]
    return {
        "descricao": item.get("nota", ""),
        "fonte": f"IBGE — Censo Demográfico {ano} ({host_de(url)})",
        "instituicao": "IBGE — Instituto Brasileiro de Geografia e Estatística",
        "ano_censo": ano,
        "categoria": item.get("categoria", ""),
        "url": url,
        "last_modified_origem": item.get("last_modified"),
        "tamanho_bytes": tamanho_copia,
        "sha256": sha_copia,
        "licenca": LICENCA_DECLARADA,
        "data_download_original": item.get("baixado_em"),
        "data_copia": agora(),
        "transformacao_aplicada": (
            "nenhuma — arquivo guardado exatamente como veio do servidor do IBGE; "
            "a cópia preserva bytes e datas (shutil.copy2)"
        ),
        "origem_da_copia": {
            "nota": (
                "Este arquivo NÃO foi baixado por este repositório: veio por CÓPIA "
                f"do projeto {ORIGEM_PROJETO}, que o baixou da fonte oficial do IBGE "
                f"em {item.get('baixado_em', '')[:10]}. O sha256 da cópia foi conferido "
                "contra o da origem e contra o registrado no manifesto de origem."
            ),
            "projeto": ORIGEM_PROJETO,
            "caminho_no_projeto_de_origem": f"{ORIGEM_RELATIVA}/{relativo}",
            "caminho_absoluto_na_maquina_de_origem": str(origem / relativo),
            "manifesto_de_origem": item["_manifesto"],
            "fonte_md_de_origem": f"{ORIGEM_RELATIVA}/{ano}/FONTE.md",
            "sha256_no_manifesto_de_origem": item.get("sha256"),
            "bytes_no_manifesto_de_origem": item.get("bytes"),
            "reaproveitado_no_download_original": item.get("reaproveitado"),
        },
        "script_responsavel": SCRIPT_RESPONSAVEL,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Importa o Censo e o CNEFE do REVIA_BG para o acervo, por cópia."
    )
    parser.add_argument("--origem", type=Path, default=ORIGEM_PADRAO,
                        help="Árvore dados/externos/censo do projeto REVIA_BG")
    parser.add_argument("--destino", type=Path, default=DESTINO)
    parser.add_argument("--dry-run", action="store_true",
                        help="Mede e confere, sem copiar nem gravar metadado")
    parser.add_argument("--forcar", action="store_true",
                        help="Recopia mesmo que o destino já tenha o mesmo sha256")
    parser.add_argument("--somente-metadados", action="store_true",
                        help="Não copia; só regenera os .json irmãos a partir do destino")
    parser.add_argument("--limite-gb", type=float, default=2.0,
                        help="Aborta se a árvore de origem passar deste tamanho")
    args = parser.parse_args()

    origem: Path = args.origem.expanduser().resolve()
    destino: Path = args.destino.expanduser().resolve()

    if not origem.is_dir():
        raise SystemExit(f"ERRO: origem não encontrada: {origem}")
    if destino == origem or origem in destino.parents:
        raise SystemExit("ERRO: destino dentro da origem — recusado.")

    print(f"origem : {origem}")
    print(f"destino: {destino}")
    print(f"modo   : {'dry-run' if args.dry_run else 'gravando'}"
          f"{' (só metadados)' if args.somente_metadados else ''}\n")

    # ---- pré-condições ------------------------------------------------------
    entradas, por_caminho = carregar_manifestos(origem)
    relativos = inventariar(origem)
    bytes_origem = sum((origem / r).stat().st_size for r in relativos)
    print(f"[1/6] inventário da origem: {len(relativos)} arquivos, "
          f"{bytes_origem:,} bytes ({bytes_origem / 2**20:,.1f} MiB)")

    limite = args.limite_gb * 1000**3
    if bytes_origem > limite:
        raise SystemExit(
            f"ERRO: árvore de origem ({bytes_origem:,} bytes) passa do limite de "
            f"{args.limite_gb} GB. Pare e pergunte antes de copiar."
        )

    dados = [r for r in relativos if r in por_caminho]
    acompanham = [r for r in relativos if r not in por_caminho]
    print(f"      {len(dados)} arquivos de dado (com entrada em manifesto), "
          f"{len(acompanham)} arquivos de procedência que acompanham a cópia:")
    for r in acompanham:
        print(f"        · {r}")
    faltando = sorted(set(por_caminho) - set(relativos) - set(APOSENTADOS))
    if faltando:
        raise SystemExit(f"ERRO: manifesto cita arquivo ausente na origem: {faltando}")

    # colisão de metadado (dois arquivos -> mesmo .json irmão)
    vistos: dict[Path, str] = {}
    for r in dados:
        alvo = caminho_metadado(destino / r)
        if alvo in vistos:
            raise SystemExit(
                f"ERRO: colisão de metadado — '{r}' e '{vistos[alvo]}' gerariam "
                f"o mesmo arquivo {alvo}"
            )
        vistos[alvo] = r
    print(f"      sem colisão de nome de metadado ({len(vistos)} .json distintos)")

    # ---- hash da origem, antes ---------------------------------------------
    print(f"\n[2/6] sha256 da origem (antes)...")
    sha_antes = hashear_arvore(origem, relativos)

    divergentes = [
        r for r in dados if sha_antes[r] != por_caminho[r].get("sha256")
    ]
    if divergentes:
        raise SystemExit(
            "ERRO: origem diverge do próprio manifesto em "
            f"{len(divergentes)} arquivo(s): {divergentes[:5]}"
        )
    print(f"      {len(dados)}/{len(dados)} arquivos de dado conferem com o "
          "sha256 registrado no manifesto de origem")

    # ---- cópia --------------------------------------------------------------
    copiados = reaproveitados = 0
    bytes_copiados = 0
    if args.somente_metadados:
        print("\n[3/6] cópia: pulada (--somente-metadados)")
    else:
        print(f"\n[3/6] copiando (preservando datas)...")
        for r in relativos:
            alvo = destino / r
            if alvo.exists() and not args.forcar:
                if sha256_arquivo(alvo) == sha_antes[r]:
                    reaproveitados += 1
                    bytes_copiados += alvo.stat().st_size
                    continue
            if args.dry_run:
                copiados += 1
                bytes_copiados += (origem / r).stat().st_size
                continue
            alvo.parent.mkdir(parents=True, exist_ok=True)
            temporario = alvo.with_name(alvo.name + ".parcial")
            shutil.copy2(origem / r, temporario)   # copy2 == cp --preserve=timestamps
            if sha256_arquivo(temporario) != sha_antes[r]:
                temporario.unlink(missing_ok=True)
                raise SystemExit(f"ERRO: cópia de '{r}' saiu com sha256 diferente.")
            temporario.replace(alvo)
            shutil.copystat(origem / r, alvo)
            copiados += 1
            bytes_copiados += alvo.stat().st_size
        print(f"      copiados: {copiados} · já presentes e idênticos: {reaproveitados}")

    # ---- conferência da cópia ----------------------------------------------
    print(f"\n[4/6] conferindo a cópia, arquivo a arquivo...")
    if args.dry_run and not destino.exists():
        print("      dry-run: nada em disco para conferir")
        conferidos = 0
        bytes_destino = 0
    else:
        conferidos = 0
        bytes_destino = 0
        for r in relativos:
            alvo = destino / r
            if not alvo.exists():
                if args.dry_run:
                    continue
                raise SystemExit(f"ERRO: ausente no destino: {alvo}")
            sha_destino = sha256_arquivo(alvo)
            if sha_destino != sha_antes[r]:
                raise SystemExit(
                    f"ERRO: sha256 diverge em '{r}': origem {sha_antes[r][:12]}…, "
                    f"cópia {sha_destino[:12]}…"
                )
            conferidos += 1
            bytes_destino += alvo.stat().st_size
        print(f"      {conferidos}/{len(relativos)} arquivos com sha256 idêntico ao "
              f"da origem · {bytes_destino:,} bytes")
        if not args.dry_run and bytes_destino != bytes_origem:
            raise SystemExit(
                f"ERRO: bytes do destino ({bytes_destino:,}) ≠ origem ({bytes_origem:,})"
            )

    # ---- metadados ----------------------------------------------------------
    print(f"\n[5/6] metadados .json irmãos...")
    gerados = 0
    for r in dados:
        alvo = destino / r
        if not alvo.exists():
            if args.dry_run:
                gerados += 1
                continue
            raise SystemExit(f"ERRO: sem arquivo no destino para metadado: {alvo}")
        metadado = montar_metadado(r, por_caminho[r], sha256_arquivo(alvo),
                                   alvo.stat().st_size, origem)
        if not args.dry_run:
            caminho_metadado(alvo).write_text(
                json.dumps(metadado, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        gerados += 1
    print(f"      {gerados} metadados {'(simulados)' if args.dry_run else 'gravados'}")

    # manifesto da cópia: cobre TODOS os arquivos, inclusive os de procedência
    manifesto = {
        "gerado_em": agora(),
        "script": SCRIPT_RESPONSAVEL,
        "natureza": "cópia — nenhum arquivo foi baixado por este repositório",
        "origem": {
            "projeto": ORIGEM_PROJETO,
            "caminho_relativo": ORIGEM_RELATIVA,
            "caminho_absoluto_na_maquina": str(origem),
        },
        "licenca": LICENCA_DECLARADA,
        "totais": {
            "arquivos": len(relativos),
            "arquivos_de_dado": len(dados),
            "arquivos_de_procedencia": len(acompanham),
            "bytes": bytes_origem,
        },
        "aposentados": [
            {"caminho": r, "substituido_por": substituto,
             "nota": "não copiado: mesmo dado já obtido direto do IBGE"}
            for r, substituto in APOSENTADOS.items()
        ],
        "arquivos": [
            {
                "caminho": r,
                "bytes": (origem / r).stat().st_size,
                "sha256": sha_antes[r],
                "tem_metadado_irmao": r in por_caminho,
            }
            for r in relativos
        ],
    }
    if not args.dry_run:
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "manifesto_copia_censo.json").write_text(
            json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"      manifesto da cópia: {destino / 'manifesto_copia_censo.json'}")

    # ---- origem intocada ----------------------------------------------------
    print(f"\n[6/6] sha256 da origem (depois) — a origem tem de sair intocada...")
    relativos_depois = inventariar(origem)
    if relativos_depois != relativos:
        raise SystemExit("ERRO: a árvore de origem mudou de conteúdo durante a execução.")
    sha_depois = hashear_arvore(origem, relativos)
    mudaram = [r for r in relativos if sha_antes[r] != sha_depois[r]]
    if mudaram:
        raise SystemExit(f"ERRO: a origem MUDOU durante a execução: {mudaram}")
    print(f"      {len(relativos)}/{len(relativos)} arquivos da origem com o mesmo "
          "sha256 do início — REVIA_BG intocado")

    print(f"\nOK — {len(relativos)} arquivos, {bytes_origem:,} bytes "
          f"({bytes_origem / 2**20:,.1f} MiB)."
          f"{'  [DRY-RUN: nada foi gravado]' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
