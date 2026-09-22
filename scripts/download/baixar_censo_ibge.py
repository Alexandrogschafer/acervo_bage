"""
Baixa DIRETO do IBGE os arquivos do Censo (2000, 2010, 2022) e do CNEFE 2022,
como dado bruto em data/raw/:

    tabelas              data/raw/tabular/ibge/censo_<ano>/
    documentação         data/raw/tabular/ibge/censo_<ano>/doc/
    malhas e geometrias  data/raw/vetor/ibge/censo_<ano>/
                         (…/malha_com_atributos/ para as malhas do FTP de agregados,
                          …/cnefe/ para os endereços georreferenciados)

A lista de arquivos é FIXA, em `config/fontes_censo_ibge.yaml` (caminho em
`paths.fontes_censo_ibge`): URL exata, bytes, Last-Modified e sha256
esperados. Ela foi gerada uma vez a partir dos manifestos do REVIA_BG, que
baixou esses arquivos do IBGE em 2026-09-20 navegando as listagens; este
script não depende mais do REVIA_BG. Substitui `censo_revia_bg.py`.

Por que lista fixa e não navegação: estes arquivos já têm sha256 medido e
ressalvas medidas sobre eles (docs/ressalvas_censo_bage.md). O que importa é
obter EXATAMENTE aqueles bytes. Se o IBGE republicar um arquivo, o sha256 não
bate e o script recusa instalar — a troca de versão é decisão do responsável.

MODOS
-----
(padrão)     para cada arquivo: se já está no destino com o sha256 esperado,
             nada a fazer; senão baixa para `<arquivo>.part`, confere tamanho e
             sha256 e só então instala. sha256 diferente do esperado: NÃO
             instala, relata e segue para o próximo.
--semear DIR move os arquivos de uma cópia local (ex.: a antiga
             data/acervo/censo/, pelo `caminho_revia_bg` de cada item) para os
             destinos, conferindo o sha256 antes e depois do movimento. Evita
             rebaixar ~976 MB.
--verificar  só HEAD na origem: compara Last-Modified e tamanho com a lista.
             Não baixa, não grava, não aborta — relata o que mudou.

Em todos os modos que gravam, cada arquivo ganha `.json` irmão
(`scripts/utils/metadados.py`) e a fonte é conferida em
data/catalogo_fontes.csv pelo mesmo padrão de `baixar_malhas_ibge.py`: linha
ausente é criada; existente com o mesmo sha256 fica intacta; com outro
sha256, só aviso.

Uso:
    python scripts/download/baixar_censo_ibge.py --semear data/acervo/censo
    python scripts/download/baixar_censo_ibge.py
    python scripts/download/baixar_censo_ibge.py --verificar
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pyogrio
import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import catalogo, metadados, paths  # noqa: E402
from scripts.utils.hashes import sha256_arquivo  # noqa: E402

HOSTS_AUTORIZADOS = ("https://ftp.ibge.gov.br/", "https://geoftp.ibge.gov.br/")
TIMEOUT = 300
TEMA = "censo"


@dataclass(frozen=True)
class Item:
    ano: str
    categoria: str
    fonte_id: str
    url: str
    arquivo: str
    base: str
    subdir: str
    bytes: int
    sha256: str
    last_modified: str
    baixado_em: str
    descricao: str
    caminho_revia_bg: str

    @property
    def destino(self) -> Path:
        return paths.caminho(self.base, *self.subdir.split("/"), self.arquivo)


def carregar_lista() -> list[Item]:
    dados = yaml.safe_load(paths.caminho("fontes_censo_ibge").read_text(encoding="utf-8"))
    itens = []
    for bruto in dados["arquivos"]:
        destino = bruto.pop("destino")
        item = Item(base=destino["base"], subdir=destino["subdir"],
                    **{k: (str(v) if k != "bytes" else int(v)) for k, v in bruto.items()})
        if not item.url.startswith(HOSTS_AUTORIZADOS):
            raise RuntimeError(f"URL fora dos hosts do IBGE: {item.url}")
        itens.append(item)
    destinos = [i.destino for i in itens]
    if len(set(destinos)) != len(destinos):
        raise RuntimeError("dois itens da lista apontam para o mesmo destino.")
    return itens


# --------------------------------------------------------------------------
# obtenção: semeadura e download
# --------------------------------------------------------------------------

def ja_instalado(item: Item) -> bool:
    return item.destino.is_file() and sha256_arquivo(item.destino) == item.sha256


def semear(item: Item, origem: Path) -> str:
    """Move o arquivo de uma cópia local, conferindo o sha256 antes e depois."""
    if ja_instalado(item):
        return "já no destino"
    fonte = origem / item.caminho_revia_bg
    if not fonte.is_file():
        return "AUSENTE na cópia local"
    if sha256_arquivo(fonte) != item.sha256:
        return "sha256 da cópia local DIVERGE do esperado — não movido"
    if item.destino.exists():
        return "destino ocupado por arquivo com outro sha256 — não movido"
    item.destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(fonte), str(item.destino))
    if sha256_arquivo(item.destino) != item.sha256:
        shutil.move(str(item.destino), str(fonte))
        raise RuntimeError(f"sha256 mudou no movimento de {fonte} — desfeito.")
    return "movido"


def baixar(item: Item) -> str:
    """Baixa se preciso; instala só com o sha256 esperado."""
    if ja_instalado(item):
        return "já no destino"
    if item.destino.exists():
        return "destino ocupado por arquivo com outro sha256 — não baixado"
    item.destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = item.destino.with_name(item.destino.name + ".part")
    with requests.get(item.url, stream=True, timeout=TIMEOUT) as resposta:
        resposta.raise_for_status()
        with open(parcial, "wb") as saida:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                saida.write(bloco)
    sha = sha256_arquivo(parcial)
    if sha != item.sha256:
        parcial.unlink()
        return (f"ORIGEM MUDOU: baixado sha256 {sha[:12]}…, esperado {item.sha256[:12]}… "
                "— não instalado")
    parcial.replace(item.destino)
    return "baixado"


def verificar(item: Item) -> tuple[bool, str]:
    """HEAD na origem; devolve (mudou, descrição)."""
    try:
        resposta = requests.head(item.url, timeout=60, allow_redirects=True)
    except requests.RequestException as erro:
        return True, f"ERRO de rede: {erro}"
    if resposta.status_code != 200:
        return True, f"HTTP {resposta.status_code}"
    lm = resposta.headers.get("Last-Modified", "")
    tamanho = int(resposta.headers.get("Content-Length") or -1)
    diferencas = []
    if lm != item.last_modified:
        diferencas.append(f"Last-Modified {item.last_modified!r} -> {lm!r}")
    if tamanho != item.bytes:
        diferencas.append(f"tamanho {item.bytes:,} -> {tamanho:,}")
    return bool(diferencas), "; ".join(diferencas) or "igual"


# --------------------------------------------------------------------------
# rastro
# --------------------------------------------------------------------------

def _crs(arquivo: Path) -> str:
    """CRS declarado, quando o arquivo é vetor legível pelo GDAL ('' caso contrário)."""
    if paths.caminho("raw_vetor") not in arquivo.parents:
        return ""
    alvo = f"zip://{arquivo}" if arquivo.suffix == ".zip" else str(arquivo)
    try:
        return str(pyogrio.read_info(alvo).get("crs") or "")
    except Exception:  # noqa: BLE001 — CSV em zip, zip com várias camadas etc.
        return ""


def escrever_metadado(item: Item, fontes: dict[str, dict]) -> bool:
    """`.json` irmão; devolve True se gravou (só grava se o conteúdo mudou)."""
    fonte = fontes[item.fonte_id]
    verdadeiro = lambda c: fonte[c].strip().lower() == "true"  # noqa: E731
    dados = metadados.montar(
        item.destino,
        tema=TEMA,
        fonte_id=item.fonte_id,
        versao=f"censo_{item.ano}",
        crs=_crs(item.destino),
        licenca=fonte["licenca"],
        autorizacao_fonte=verdadeiro("autorizacao_fonte"),
        pode_publicar=verdadeiro("pode_publicar"),
        status_conferencia="pendente",
        url_origem=item.url,
        observacoes=(
            f"{item.descricao}. Arquivo bruto, exatamente como veio do IBGE. "
            f"Last-Modified da origem: {item.last_modified}. "
            f"Baixado em {item.baixado_em} (pelo REVIA_BG, cópia aposentada; procedência "
            "em docs/procedencia/revia_bg_censo/). Lista fixa em config/fontes_censo_ibge.yaml; "
            "rebaixável por scripts/download/baixar_censo_ibge.py."
        ),
        data_producao=datetime.fromisoformat(item.baixado_em),
    )
    dados["edicao"] = f"censo_{item.ano}"
    caminho_json = metadados.caminho_irmao(item.destino)
    if caminho_json.exists() and metadados.ler(item.destino) == dados:
        return False
    metadados.escrever(item.destino, dados, sobrescrever=True)
    return True


def conferir_fontes(itens: list[Item], fontes: dict[str, dict]) -> list[str]:
    """Mesmo padrão de baixar_malhas_ibge.py: nunca troca o sha256 de uma fonte."""
    relatos = []
    for id_fonte in sorted({i.fonte_id for i in itens}):
        linha = fontes.get(id_fonte)
        if linha is None:
            relatos.append(f"{id_fonte}: AUSENTE no catálogo — criar a linha à mão, "
                           "com licença e ressalvas")
            continue
        principal = next((i for i in itens if i.url == linha["url"]), None)
        if principal is None:
            relatos.append(f"{id_fonte}: url do catálogo não está na lista fixa")
        elif linha["sha256"].strip().lower() != principal.sha256:
            relatos.append(f"{id_fonte}: sha256 DIVERGENTE do catálogo — linha não alterada")
        else:
            relatos.append(f"{id_fonte}: inalterada (mesmo sha256)")
    return relatos


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa o Censo direto do IBGE (lista fixa).")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--semear", type=Path, metavar="DIR",
                       help="move os arquivos de uma cópia local em vez de baixar")
    grupo.add_argument("--verificar", action="store_true",
                       help="só HEAD na origem; relata mudanças, não baixa nem grava")
    args = parser.parse_args()

    itens = carregar_lista()

    if args.verificar:
        mudaram = 0
        for item in itens:
            mudou, texto = verificar(item)
            mudaram += mudou
            print(f"{'MUDOU' if mudou else 'igual':<5}  censo_{item.ano}  {item.arquivo:<70} {texto if mudou else ''}")
        print(f"\n{len(itens)} arquivos verificados na origem; {mudaram} com diferença.")
        return

    fontes = {l["id_fonte"]: l for l in catalogo.ler("catalogo_fontes")}
    origem = args.semear.resolve() if args.semear else None
    contagem: dict[str, int] = {}
    for item in itens:
        situacao = semear(item, origem) if origem else baixar(item)
        contagem[situacao] = contagem.get(situacao, 0) + 1
        gravou = escrever_metadado(item, fontes) if ja_instalado(item) else False
        print(f"{situacao:<16} {'json' if gravou else '    '}  "
              f"{paths.relativo(item.destino)}")

    print()
    for situacao, n in sorted(contagem.items()):
        print(f"{n:>3}  {situacao}")
    print()
    for relato in conferir_fontes(itens, fontes):
        print(f"fonte {relato}")


if __name__ == "__main__":
    main()
