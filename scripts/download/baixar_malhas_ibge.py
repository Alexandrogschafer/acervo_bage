"""
Baixa as malhas-base do IBGE para a UF do acervo:

    a) malha municipal, na edição MAIS RECENTE listada no geoftp;
    b) malha de setores censitários do Censo 2022 (malha territorial, sem os
       atributos do Censo).

Destino: data/raw/vetor/ibge/<edicao>/<arquivo>, onde <edicao> é o nome do
diretório da edição no geoftp (`municipio_2025`, `censo_2022`). Cada edição tem
seu diretório, então uma edição nova nunca cai por cima da anterior. Nada é
descompactado: o GDAL lê o shapefile de dentro do ZIP (`zip://`).

UF e CRS vêm de `config/config.yaml`, via `scripts/utils/paths.py`.

REGRA DE ORIGEM DO DADO
-----------------------
Nenhuma URL é montada por adivinhação. O script parte da raiz do geoftp e
desce pelas listagens de diretório, exigindo em cada nível que o nome esperado
esteja listado, e escolhe o arquivo final pelo padrão do nome, exigindo
exatamente um candidato. Se o IBGE reorganizar a árvore, o script falha
dizendo qual nível sumiu, em vez de baixar outra coisa sem avisar.

IDEMPOTÊNCIA
------------
- Arquivo já baixado, com tamanho e Last-Modified iguais aos da origem: não é
  baixado de novo e o `.json` irmão não é reescrito.
- Arquivo já baixado, mas a origem mudou (o IBGE republicou a MESMA edição):
  o script PARA. Substituir exige `--forcar`, porque o sha256 antigo pode já
  estar fixado em catálogo ou em manifesto de estudo.
- O download vai para `<arquivo>.part` e só é renomeado depois de conferido o
  tamanho, para que um download interrompido não pareça um arquivo completo.

CATÁLOGO DE FONTES
------------------
Cada produto tem um `id_fonte`. Se a linha não existe, é criada. Se existe com
o mesmo sha256, fica intacta. Se existe com OUTRO sha256 (edição nova), o
script avisa e não mexe nela: trocar a fonte de uma camada conferida é decisão
do responsável, não efeito colateral de download.

Uso:
    python scripts/download/baixar_malhas_ibge.py
    python scripts/download/baixar_malhas_ibge.py --edicao-municipal 2024
    python scripts/download/baixar_malhas_ibge.py --forcar
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pyogrio
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import catalogo, metadados, paths  # noqa: E402
from scripts.utils.hashes import hash_e_tamanho  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("baixar_malhas_ibge")

HOST_GEOFTP = "https://geoftp.ibge.gov.br/"
# Só estes níveis são nomeados; cada um é conferido contra a listagem do pai.
NIVEIS_MALHAS = ["organizacao_do_territorio/", "malhas_territoriais/"]
DIR_MUNICIPAIS = "malhas_municipais/"
DIR_SETORES = "malhas_de_setores_censitarios__divisoes_intramunicipais/"
EDICAO_SETORES = "censo_2022"

LICENCA = "IBGE — uso livre com citação da fonte"
TIMEOUT = 120


@dataclass(frozen=True)
class Produto:
    """Um arquivo a baixar, já resolvido pela navegação."""

    id_fonte: str
    nome: str
    edicao: str
    url: str
    arquivo: str

    @property
    def destino(self) -> Path:
        return paths.caminho("raw_vetor", "ibge", self.edicao, self.arquivo)


# --------------------------------------------------------------------------
# navegação pelas listagens do geoftp
# --------------------------------------------------------------------------

def listar(url: str) -> list[str]:
    """Entradas filhas de uma listagem Apache do geoftp.

    Descarta ordenação (`?C=`), links absolutos (pai, redes sociais) e âncoras.
    """
    if not url.startswith(HOST_GEOFTP):
        raise RuntimeError(f"URL fora do host autorizado ({HOST_GEOFTP}): {url}")
    resposta = requests.get(url, timeout=TIMEOUT)
    resposta.raise_for_status()
    return [
        href for href in re.findall(r'href="([^"]+)"', resposta.text)
        if not href.startswith(("?", "/", "http://", "https://", "#"))
    ]


def entrar(url: str, nome: str) -> str:
    """Desce um nível, exigindo que `nome` esteja listado em `url`."""
    entradas = listar(url)
    if nome not in entradas:
        raise RuntimeError(
            f"'{nome}' não está listado em {url}. Entradas: {sorted(entradas)[:30]}"
        )
    return url + nome


def unico(url: str, padrao: str) -> str:
    """O único arquivo da listagem que casa com `padrao` (regex, nome inteiro)."""
    candidatos = [e for e in listar(url) if re.fullmatch(padrao, e)]
    if len(candidatos) != 1:
        raise RuntimeError(
            f"esperava exatamente 1 arquivo casando '{padrao}' em {url}, achei {candidatos}"
        )
    return candidatos[0]


def raiz_malhas() -> str:
    url = HOST_GEOFTP
    for nivel in NIVEIS_MALHAS:
        url = entrar(url, nivel)
    return url


def resolver_municipal(uf: str, ano: str | None) -> Produto:
    """Malha municipal da UF, na edição pedida ou na mais recente listada."""
    url = entrar(raiz_malhas(), DIR_MUNICIPAIS)
    edicoes = sorted(
        e.rstrip("/") for e in listar(url) if re.fullmatch(r"municipio_\d{4}/", e)
    )
    if not edicoes:
        raise RuntimeError(f"nenhuma edição 'municipio_AAAA/' listada em {url}")
    edicao = f"municipio_{ano}" if ano else edicoes[-1]
    if edicao not in edicoes:
        raise RuntimeError(f"edição {edicao} não listada. Disponíveis: {edicoes}")
    logger.info("malha municipal: edição %s (disponíveis: %s … %s)",
                edicao, edicoes[0], edicoes[-1])

    url = entrar(url, f"{edicao}/")
    url = entrar(url, "UFs/")
    url = entrar(url, f"{uf}/")
    arquivo = unico(url, rf"{uf}_Municipios_\d{{4}}\.zip")
    return Produto(
        id_fonte="ibge_malhas_municipais",
        nome=f"Malhas Territoriais — malhas municipais ({arquivo})",
        edicao=edicao, url=url + arquivo, arquivo=arquivo,
    )


def resolver_setores(uf: str, edicao: str) -> Produto:
    """Malha territorial de setores censitários da UF (GeoPackage)."""
    url = entrar(raiz_malhas(), DIR_SETORES)
    url = entrar(url, f"{edicao}/")
    for nivel in ("setores/", "gpkg/", "UF/", f"{uf}/"):
        url = entrar(url, nivel)
    ano = edicao.rsplit("_", 1)[-1]
    arquivo = unico(url, rf"{uf}_setores_CD{ano}\.gpkg")
    return Produto(
        id_fonte=f"ibge_malha_setores_{ano}",
        nome=f"Malhas de setores censitários — {edicao.replace('_', ' ')} "
             f"(malha territorial, sem atributos do Censo) ({arquivo})",
        edicao=edicao, url=url + arquivo, arquivo=arquivo,
    )


# --------------------------------------------------------------------------
# download idempotente
# --------------------------------------------------------------------------

def baixar(produto: Produto, forcar: bool) -> bool:
    """Baixa o produto se preciso. Devolve True se baixou.

    Raises:
        RuntimeError: se a origem mudou e `forcar` não foi pedido, ou se o
            download veio com tamanho diferente do anunciado.
    """
    destino = produto.destino
    cabecalho = requests.head(produto.url, timeout=TIMEOUT)
    cabecalho.raise_for_status()
    last_modified = cabecalho.headers.get("Last-Modified", "")
    tamanho_origem = int(cabecalho.headers.get("Content-Length") or -1)

    if destino.exists() and not forcar:
        registrado = _last_modified_registrado(destino)
        if destino.stat().st_size == tamanho_origem and registrado == last_modified:
            logger.info("já baixado e igual à origem: %s", paths.relativo(destino))
            return False
        raise RuntimeError(
            f"{paths.relativo(destino)} já existe, mas a origem mudou "
            f"(tamanho local {destino.stat().st_size} x origem {tamanho_origem}; "
            f"Last-Modified registrado {registrado!r} x origem {last_modified!r}). "
            "O IBGE republicou a mesma edição. Confira quem fixou o sha256 antigo "
            "e rode com --forcar para substituir."
        )

    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".part")
    logger.info("baixando %s (%s bytes)", produto.url, tamanho_origem)
    with requests.get(produto.url, stream=True, timeout=TIMEOUT) as resposta:
        resposta.raise_for_status()
        with open(parcial, "wb") as saida:
            for bloco in resposta.iter_content(chunk_size=1024 * 1024):
                saida.write(bloco)
    if tamanho_origem >= 0 and parcial.stat().st_size != tamanho_origem:
        raise RuntimeError(
            f"download incompleto de {produto.url}: origem anuncia {tamanho_origem} "
            f"bytes, chegaram {parcial.stat().st_size}. Arquivo parcial em {parcial}."
        )
    parcial.replace(destino)

    dados = metadados.montar(
        destino,
        tema="limites",
        fonte_id=produto.id_fonte,
        versao=produto.edicao,
        crs=_crs(destino),
        licenca=LICENCA,
        autorizacao_fonte=True,
        pode_publicar=True,
        status_conferencia="pendente",
        url_origem=produto.url,
        observacoes=(
            f"Arquivo bruto, como veio do geoftp do IBGE (UF inteira). "
            f"Last-Modified da origem: {last_modified}. "
            "Obtido navegando as listagens a partir de organizacao_do_territorio/ "
            "(scripts/download/baixar_malhas_ibge.py)."
        ),
        data_producao=datetime.now(timezone.utc),
    )
    dados["edicao"] = produto.edicao
    metadados.escrever(destino, dados, sobrescrever=True)
    return True


def _last_modified_registrado(destino: Path) -> str:
    """Last-Modified gravado nas observações do `.json` irmão ('' se não houver)."""
    try:
        obs = metadados.ler(destino).get("observacoes", "")
    except FileNotFoundError:
        return ""
    achado = re.search(r"Last-Modified da origem: ([^.]+GMT)", obs)
    return achado.group(1) if achado else ""


def _crs(arquivo: Path) -> str:
    """CRS declarado no arquivo, como 'EPSG:xxxx' quando possível."""
    alvo = f"zip://{arquivo}" if arquivo.suffix == ".zip" else str(arquivo)
    return str(pyogrio.read_info(alvo).get("crs") or "")


# --------------------------------------------------------------------------
# catálogo de fontes
# --------------------------------------------------------------------------

def registrar_fonte(produto: Produto) -> str:
    """Cria a linha da fonte se não existir; nunca troca o sha256 de uma existente."""
    sha256, tamanho = hash_e_tamanho(produto.destino)
    existentes = {l["id_fonte"]: l for l in catalogo.ler("catalogo_fontes")}
    atual = existentes.get(produto.id_fonte)
    if atual is not None:
        if atual["sha256"].strip().lower() == sha256:
            return "inalterada (mesmo sha256)"
        logger.warning(
            "fonte '%s' está no catálogo com OUTRO sha256 (%s…) — o arquivo baixado "
            "(%s…) é outra edição ou republicação. Linha NÃO alterada: atualizar é "
            "decisão do responsável.", produto.id_fonte, atual["sha256"][:12], sha256[:12],
        )
        return "DIVERGENTE — não alterada"

    catalogo.upsert("catalogo_fontes", "id_fonte", [{
        "id_fonte": produto.id_fonte,
        "nome": produto.nome,
        "instituicao": "IBGE",
        "url": produto.url,
        "data_acesso": datetime.now(timezone.utc).date().isoformat(),
        "formato": produto.destino.suffix.lstrip("."),
        "tamanho_bytes": str(tamanho),
        "sha256": sha256,
        "licenca": LICENCA,
        "autorizacao_fonte": "true",
        "pode_publicar": "true",
        "observacoes": (
            f"[edição: {produto.edicao} | recorte: UF {paths.uf()} | "
            "script: scripts/download/baixar_malhas_ibge.py] Baixado navegando as "
            "listagens do geoftp a partir de organizacao_do_territorio/ — nenhuma URL "
            f"montada por adivinhação. Cópia bruta em {paths.relativo(produto.destino)}. "
            "Citar: IBGE, Malhas Territoriais."
        ),
    }])
    return "acrescentada"


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa as malhas-base do IBGE (geoftp).")
    parser.add_argument("--edicao-municipal", default=None,
                        help="ano da malha municipal (default: a mais recente listada)")
    parser.add_argument("--edicao-setores", default=EDICAO_SETORES,
                        help=f"diretório da edição de setores (default: {EDICAO_SETORES})")
    parser.add_argument("--forcar", action="store_true",
                        help="rebaixa mesmo se já existir, inclusive quando a origem mudou")
    args = parser.parse_args()

    uf = paths.uf()
    produtos = [
        resolver_municipal(uf, args.edicao_municipal),
        resolver_setores(uf, args.edicao_setores),
    ]

    print()
    for produto in produtos:
        baixou = baixar(produto, args.forcar)
        situacao_fonte = registrar_fonte(produto)
        sha256, tamanho = hash_e_tamanho(produto.destino)
        print(f"{produto.id_fonte}")
        print(f"  edição ..... {produto.edicao}")
        print(f"  url ........ {produto.url}")
        print(f"  arquivo .... {paths.relativo(produto.destino)} "
              f"({'baixado agora' if baixou else 'já existia'})")
        print(f"  tamanho .... {tamanho:,} bytes")
        print(f"  sha256 ..... {sha256}")
        print(f"  catálogo ... {situacao_fonte}")


if __name__ == "__main__":
    main()
