"""
Importa, POR CÓPIA, os dados do setor de GeoInformação da Prefeitura de Bagé.

    https://github.com/GeoInformacao/{filesGeoJSONgeobage, GeoDataBase, geobage}

USO INTERNO EM PESQUISA. ESTES DADOS NÃO PODEM SER PUBLICADOS.
------------------------------------------------------------------------------
Não há autorização da fonte e este repositório é público. Tudo o que este
script grava vai para `data/externos/geoinformacao_bage/`, que está inteiro no
`.gitignore` (menos os `.json` de metadado) e é barrado pelo hook de
pre-commit. Todas as linhas de catálogo saem com `pode_publicar=false`.

Nada daqui vai para `data/acervo/` nem para `data/geoportal/`: promover uma
camada externa para o acervo é decisão de licença, não de pipeline.

PINAGEM
-------
Os três repositórios são lidos em COMMITS FIXOS, nunca em branch ou HEAD. Um
branch move; o resultado de hoje deixa de ser reproduzível amanhã sem que nada
acuse. Se o commit pinado não existir mais no remoto, o script ABORTA — não cai
para o HEAD.

MINIMIZAÇÃO DE DADOS PESSOAIS (LGPD)
------------------------------------
Dois arquivos trazem dado pessoal ou economicamente sensível e são minimizados
NA INGESTÃO: o original é lido do clone temporário, os campos são removidos em
memória e só o resultado é gravado. **O arquivo original nunca é gravado sob
`data/`**, em momento nenhum — por isso a cópia desses dois não é `shutil.copy`.

NOMES
-----
Cópia externa PRESERVA o nome do arquivo na origem: o nome é parte da
procedência e é o que permite reencontrar o arquivo no repositório de origem.
O padrão `{tema}_{fonte}_{periodo}_{resolucao}` vale para produtos do acervo,
não para cópias externas. Única exceção: `CONDOMINIOS.geojson`, cujo nome
descreve errado o conteúdo (é cadastro imobiliário, não condomínios); o nome
de origem fica registrado em `nome_original` no metadado.

O script é idempotente: destino com o sha256 esperado não é regravado.

Uso:
    python scripts/download/baixar_geoinformacao_bage.py
    python scripts/download/baixar_geoinformacao_bage.py --forcar
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.utils import catalogo, metadados, paths  # noqa: E402
from scripts.utils.hashes import hash_e_tamanho, sha256_arquivo  # noqa: E402

URL_BASE = "https://github.com/GeoInformacao/{repo}.git"
SUBDIR = "geoinformacao_bage"

LICENCA_INDEFINIDA = "indefinida — repositório de origem sem arquivo LICENSE"
LICENCA_GEOBAGE = "MIT License + file LICENSE (titular: Prefeitura Municipal de Bagé)"

# Nota comum a todas as linhas de catálogo: existe para quem abrir o CSV daqui
# a um ano entender por que nada disso pode ser publicado.
NOTA_PUBLICACAO = (
    "USO INTERNO EM PESQUISA — sem autorização da fonte para republicação; "
    "repositório público, por isso pode_publicar=false e o arquivo fica fora do git "
    "(data/externos/, barrado pelo .gitignore e pelo hook de pre-commit)."
)


@dataclass(frozen=True)
class Repositorio:
    """Um repositório de origem, pinado em um commit."""

    nome: str
    commit: str
    data_commit: str
    licenca: str
    instituicao: str
    descricao: str

    @property
    def url(self) -> str:
        return URL_BASE.format(repo=self.nome)

    @property
    def id_fonte(self) -> str:
        return f"geoinfo_{self.nome.lower()}"

    @property
    def commit_curto(self) -> str:
        return self.commit[:7]


REPOS: tuple[Repositorio, ...] = (
    Repositorio(
        nome="filesGeoJSONgeobage",
        commit="dec129057da35adc245f352d0dfb1633adb70560",
        data_commit="2022-07-26",
        licenca=LICENCA_INDEFINIDA,
        instituicao="Prefeitura Municipal de Bagé — setor de GeoInformação",
        descricao="Camadas GeoJSON de Bagé/RS (base do pacote R geobage).",
    ),
    Repositorio(
        nome="GeoDataBase",
        commit="125c9753dca806422b5397969eaad726519177ad",
        data_commit="2020-07-16",
        licenca=LICENCA_INDEFINIDA,
        instituicao="Prefeitura Municipal de Bagé — setor de GeoInformação",
        descricao="Base cadastral urbana de Bagé/RS (lotes, quadras, pavimentação).",
    ),
    Repositorio(
        nome="geobage",
        commit="aaec7e8e3f537f99b646669dff00898d371a573d",
        data_commit="2022-07-26",
        licenca=LICENCA_GEOBAGE,
        instituicao="Prefeitura Municipal de Bagé — setor de GeoInformação",
        descricao="Pacote R geobage — só R/ e DESCRIPTION, para procedência das funções.",
    ),
)

# ---------------------------------------------------------------------------
# minimização de dados pessoais (LGPD)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Minimizacao:
    """Campos a remover de um arquivo na ingestão, e por quê."""

    campos: tuple[str, ...]
    motivo: str
    renomear_para: str | None = None


MINIMIZACOES: dict[str, Minimizacao] = {
    "GeoDataBase/CONDOMINIOS.geojson": Minimizacao(
        campos=("proprietar", "responsave"),
        motivo=(
            "LGPD: 'proprietar' e 'responsave' nomeiam pessoas físicas identificadas e, "
            "combinados com a geometria do lote e o endereço, tornam cada feição um dado "
            "pessoal diretamente identificável. Removidos na ingestão — o arquivo original "
            "nunca foi gravado sob data/."
        ),
        renomear_para="cadastro_imobiliario.geojson",
    ),
    "GeoDataBase/LOTES_URBANOS.geojson": Minimizacao(
        campos=("valorvenal", "venal_min", "venal_max", "venal_anun"),
        motivo=(
            "Valores venais por lote: dado economicamente sensível, associável a pessoa "
            "identificada pelo endereço do lote. Removidos na ingestão — o arquivo original "
            "nunca foi gravado sob data/."
        ),
    ),
}

# ---------------------------------------------------------------------------
# temas: melhor correspondência com as pastas de data/acervo/
# ---------------------------------------------------------------------------

TEMAS: dict[str, str] = {
    # filesGeoJSONgeobage
    "AERODROMOS": "viario", "BAGE": "limites",
    "BANCOS_DE_AREIA_ARROIO_BAGE": "hidrografia", "BANHADOS": "ambiental",
    "BARRAGEM": "hidrografia", "COMPREB": "cadastro",
    "CURVAS_DE_NIVEL_BAGE_10M": "ambiental", "CURVAS_NIVEL": "ambiental",
    "DISTRITOS_DE_BAGE": "limites", "ESTRADAS_RURAIS_DE_BAGE": "viario",
    "FERROVIAS": "viario", "GEOLOGIA": "ambiental", "GEOMORFOLOGIA": "ambiental",
    "HIDROGEOLOGIA": "hidrografia", "HIDROGRAFIA": "hidrografia",
    "IMOVEIS_RURAIS_PUBLICOS": "cadastro", "LINHAS_TRANSMISSAO": "viario",
    "LOTEAMENTOS": "cadastro", "LOTES_RURAIS": "cadastro",
    "MASSA_DAGUA": "hidrografia", "NASCENTES": "hidrografia",
    "PALEONTOLOGIA": "ambiental", "PAMPA_FINAL": "ambiental",
    "PARQUE_DO_GAUCHO_BAGE": "ambiental", "PAVIMENTACAO_BAGE": "viario",
    "PEDOLOGIA": "ambiental", "PREDIOS_PUBLICOS": "cadastro",
    "PRODUCAO_LEITE": "ambiental", "RESERVA_LEGAL": "ambiental",
    "RODOVIAS_PAVIMENTADAS": "viario", "RODOVIAS_SEM_PAVIMENTO": "viario",
    "SENSIBILIDADE_AMBIENTAL": "ambiental", "SOLO": "ambiental",
    "SOLO_BAGE": "ambiental", "TIPO_SOLO": "ambiental",
    "TRECHO_DRENAGEM": "hidrografia", "TRECHO_MASSA_DAGUA": "hidrografia",
    "UNIDADE_HIDROESTRATIGRAFICA": "hidrografia", "USO_COBERTURA_SOLO": "ambiental",
    "USO_DA_TERRA": "ambiental", "VEGETACAO": "ambiental", "ZONAS_BAGE": "limites",
    # GeoDataBase
    "AREA_CONTRUIDA": "cadastro", "ASFALTO_ANTIGO": "viario",
    "ASFALTO_NOVO_DESDE_2017": "viario", "cadastro_imobiliario": "cadastro",
    "INTERTRAVADO_DE_CONCRETO": "viario", "LOGRADOUROS": "viario",
    "LOTES_URBANOS": "cadastro", "PARALELEPIPEDO": "viario",
    "QUARTEIRAO": "cadastro", "REGIOES_CENSITARIAS": "censo",
}

# temas atribuídos por aproximação — o acervo não tem pasta própria para eles
TEMA_APROXIMADO: dict[str, str] = {
    "LINHAS_TRANSMISSAO": "infraestrutura de energia; 'viario' é a pasta de redes lineares",
    "PRODUCAO_LEITE": "produção agropecuária por COREDE; sem tema próprio no acervo",
    "AERODROMOS": "infraestrutura aeroportuária; 'viario' é a pasta de transporte",
    "CURVAS_DE_NIVEL_BAGE_10M": "altimetria; sem tema de relevo no acervo",
    "CURVAS_NIVEL": "altimetria; sem tema de relevo no acervo",
}

TEMA_PROCEDENCIA = "procedencia"  # R/ e DESCRIPTION: não são camadas


@dataclass
class ArquivoCopiado:
    """Um arquivo efetivamente gravado em data/externos/."""

    repo: Repositorio
    destino: Path
    nome_original: str
    sha256: str
    tamanho: int
    crs: str = ""
    campos_removidos: list[str] = field(default_factory=list)
    motivo_remocao: str = ""
    erro_leitura: str = ""
    rebaixado: bool = True
    e_camada: bool = True

    @property
    def id_camada(self) -> str:
        return f"geoinfo_{self.repo.nome.lower()}_{self.destino.stem.lower()}"


# ---------------------------------------------------------------------------
# clone pinado
# ---------------------------------------------------------------------------

def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Roda um comando git capturando saída."""
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def clonar_pinado(repo: Repositorio, raiz_temp: Path) -> Path:
    """Clona `repo` em `raiz_temp` e faz checkout do commit pinado.

    Busca o commit diretamente por SHA (fetch raso). Se o remoto não servir
    aquele objeto, cai para clone completo e tenta o checkout — só então
    desiste. Em nenhuma hipótese usa branch ou HEAD.

    Raises:
        RuntimeError: se o repositório não puder ser clonado ou se o commit
            pinado não existir no remoto (sinal de que a origem mudou).
    """
    destino = raiz_temp / repo.nome
    destino.mkdir(parents=True)

    for passo in ("fetch-sha", "clone-completo"):
        if passo == "fetch-sha":
            _git(["init", "-q"], destino)
            _git(["remote", "add", "origin", repo.url], destino)
            if _git(["fetch", "-q", "--depth", "1", "origin", repo.commit], destino).returncode:
                continue
            alvo = "FETCH_HEAD"
        else:
            shutil.rmtree(destino)
            clone = _git(["clone", "-q", repo.url, str(destino)], raiz_temp)
            if clone.returncode:
                raise RuntimeError(
                    f"não consegui clonar {repo.url}: {clone.stderr.strip()[:300]}"
                )
            alvo = repo.commit

        if _git(["checkout", "-q", alvo], destino).returncode == 0:
            conferido = _git(["rev-parse", "HEAD"], destino).stdout.strip()
            if conferido != repo.commit:
                raise RuntimeError(
                    f"{repo.nome}: checkout resultou em {conferido}, esperado {repo.commit}"
                )
            return destino

    raise RuntimeError(
        f"{repo.nome}: o commit pinado {repo.commit} NÃO existe em {repo.url}.\n"
        "  O repositório de origem pode ter sido reescrito, tornado privado ou removido.\n"
        "  O script NÃO cai para o HEAD: isso trocaria o dado sem ninguém perceber.\n"
        "  Confira o commit na origem antes de mudar a pinagem neste arquivo."
    )


# ---------------------------------------------------------------------------
# leitura / CRS
# ---------------------------------------------------------------------------

def _normalizar_crs(nome: str) -> str:
    """Converte a URN OGC de um código EPSG para a forma `EPSG:<código>`.

    Só reescreve o identificador, para o catálogo ficar comparável com o que a
    leitura geoespacial devolve. Qualquer outra forma (CRS84, por exemplo) sai
    literal como está declarada — traduzir identificador que não é EPSG seria
    afirmar uma equivalência que a ingestão não tem como conferir.
    """
    marcador = "urn:ogc:def:crs:EPSG::"
    return f"EPSG:{nome[len(marcador):]}" if nome.startswith(marcador) else nome


def crs_declarado_bruto(caminho: Path) -> str:
    """Lê o membro `crs` do GeoJSON sem construir geometria.

    Serve de plano B quando a leitura geoespacial falha: o CRS declarado no
    cabeçalho continua sendo informação válida sobre o arquivo.
    """
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            cabecalho = arquivo.read(8192)
        inicio = cabecalho.find('"crs"')
        if inicio < 0:
            return ""
        # equilibra chaves a partir do primeiro '{' depois de "crs" — procurar
        # por "}}" quebra quando a origem escreve "} }" com espaço
        abre = cabecalho.find("{", inicio)
        profundidade = 0
        for fim in range(abre, len(cabecalho)):
            if cabecalho[fim] == "{":
                profundidade += 1
            elif cabecalho[fim] == "}":
                profundidade -= 1
                if profundidade == 0:
                    nome = json.loads(cabecalho[abre:fim + 1]).get("properties", {}).get("name", "")
                    return _normalizar_crs(str(nome))
        return ""
    except Exception:  # noqa: BLE001 — plano B não pode derrubar a ingestão
        return ""


def ler_crs(caminho: Path) -> tuple[str, str]:
    """Abre o arquivo como camada e devolve `(crs, erro_de_leitura)`.

    A leitura geoespacial é também o teste de sanidade do arquivo: um GeoJSON
    sintaticamente válido pode ter anel não fechado e quebrar na construção da
    geometria. Quando isso acontece, o erro é REGISTRADO e o arquivo é copiado
    assim mesmo — corrigir geometria de terceiro não é papel da ingestão.
    """
    import geopandas as gpd

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            gdf = gpd.read_file(caminho)
            return (str(gdf.crs) if gdf.crs else ""), ""
        except Exception as erro:  # noqa: BLE001
            return crs_declarado_bruto(caminho), f"{type(erro).__name__}: {str(erro)[:200]}"


# ---------------------------------------------------------------------------
# cópia
# ---------------------------------------------------------------------------

def _gravar_se_mudou(destino: Path, conteudo: bytes, forcar: bool) -> bool:
    """Grava `conteudo` só se o destino não tiver esse sha256. Devolve se gravou."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and not forcar:
        import hashlib
        if sha256_arquivo(destino) == hashlib.sha256(conteudo).hexdigest():
            return False
    destino.write_bytes(conteudo)
    return True


def copiar_simples(origem: Path, destino: Path, forcar: bool) -> bool:
    """Cópia byte a byte, idempotente pelo sha256. Devolve se gravou."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and not forcar and sha256_arquivo(destino) == sha256_arquivo(origem):
        return False
    shutil.copy2(origem, destino)
    return True


def copiar_minimizado(
    origem: Path, destino: Path, minimizacao: Minimizacao, forcar: bool
) -> tuple[bool, list[str]]:
    """Lê o GeoJSON, remove os campos e grava SÓ o resultado.

    O original é lido do clone temporário e nunca chega ao disco do projeto.

    Returns:
        `(gravou, campos_efetivamente_removidos)`.
    """
    documento: dict[str, Any] = json.loads(origem.read_text(encoding="utf-8"))
    removidos: set[str] = set()

    for feicao in documento.get("features", []):
        propriedades = feicao.get("properties")
        if not isinstance(propriedades, dict):
            continue
        for campo in minimizacao.campos:
            if campo in propriedades:
                del propriedades[campo]
                removidos.add(campo)

    # geometria e membro `crs` saem intactos: minimizar não é reprojetar nem
    # consertar — só apagar coluna
    conteudo = json.dumps(documento, ensure_ascii=False).encode("utf-8")
    return _gravar_se_mudou(destino, conteudo, forcar), sorted(removidos)


def arquivos_do_repo(repo: Repositorio, clone: Path) -> list[Path]:
    """Lista os arquivos a copiar de um clone, segundo a regra do repositório."""
    if repo.nome == "geobage":
        # só procedência das funções: R/ e DESCRIPTION. Sem PDF, sem imagens.
        return sorted(clone.glob("R/*.R")) + [clone / "DESCRIPTION"]
    alvos = sorted(clone.glob("*.geojson"))
    zip_curvas = clone / "CURVAS_DE_NIVEL_BAGE_10M.zip"
    if zip_curvas.exists():
        alvos.append(zip_curvas)
    return alvos


def ingerir(repo: Repositorio, clone: Path, forcar: bool) -> list[ArquivoCopiado]:
    """Copia os arquivos de um repositório e devolve o que foi gravado."""
    dir_destino = paths.caminho("externos", SUBDIR, repo.nome)
    copiados: list[ArquivoCopiado] = []

    for origem in arquivos_do_repo(repo, clone):
        if not origem.exists():
            print(f"    ! ausente no clone, pulado: {origem.name}")
            continue

        chave = f"{repo.nome}/{origem.name}"
        minimizacao = MINIMIZACOES.get(chave)
        e_r = origem.suffix == ".R" or origem.name == "DESCRIPTION"

        if minimizacao:
            nome_destino = minimizacao.renomear_para or origem.name
            destino = dir_destino / nome_destino
            gravou, removidos = copiar_minimizado(origem, destino, minimizacao, forcar)
            motivo = minimizacao.motivo
        else:
            subcaminho = "R" if origem.suffix == ".R" else ""
            destino = dir_destino / subcaminho / origem.name
            gravou = copiar_simples(origem, destino, forcar)
            removidos, motivo = [], ""

        sha, tamanho = hash_e_tamanho(destino)
        crs, erro = ("", "")
        if destino.suffix == ".geojson":
            crs, erro = ler_crs(destino)

        copiados.append(ArquivoCopiado(
            repo=repo, destino=destino, nome_original=origem.name,
            sha256=sha, tamanho=tamanho, crs=crs,
            campos_removidos=removidos, motivo_remocao=motivo,
            erro_leitura=erro, rebaixado=gravou, e_camada=not e_r,
        ))

    return copiados


# ---------------------------------------------------------------------------
# metadados e catálogos
# ---------------------------------------------------------------------------

def escrever_metadado(arquivo: ArquivoCopiado) -> None:
    """Grava o `.json` irmão do arquivo copiado."""
    repo = arquivo.repo
    observacoes = [NOTA_PUBLICACAO]
    if arquivo.motivo_remocao:
        observacoes.append(arquivo.motivo_remocao)
    if arquivo.erro_leitura:
        observacoes.append(
            f"FALHA NA LEITURA GEOESPACIAL: {arquivo.erro_leitura}. O arquivo foi copiado "
            "byte a byte assim mesmo; a geometria NÃO foi corrigida (isso é decisão de "
            "quem for usar a camada, não da ingestão). O CRS registrado é o declarado no "
            "cabeçalho do arquivo."
        )
    if arquivo.destino.suffix == ".zip":
        observacoes.append("Arquivo compactado: CRS não inspecionado (não foi descompactado).")
    aproximado = TEMA_APROXIMADO.get(arquivo.destino.stem)
    if aproximado:
        observacoes.append(f"Tema aproximado — {aproximado}.")

    tema = (TEMA_PROCEDENCIA if not arquivo.e_camada
            else TEMAS.get(arquivo.destino.stem, "cadastro"))

    metadados.escrever(
        arquivo.destino,
        metadados.montar(
            arquivo.destino,
            tema=tema,
            fonte_id=repo.id_fonte,
            versao=repo.commit_curto,
            crs=arquivo.crs,
            licenca=repo.licenca,
            autorizacao_fonte=False,
            pode_publicar=False,
            campos_removidos=arquivo.campos_removidos,
            status_conferencia="pendente",
            observacoes=" ".join(observacoes),
            repo_origem=repo.nome,
            commit=repo.commit,
            url_origem=repo.url,
            data_commit=repo.data_commit,
            nome_original=(arquivo.nome_original
                           if arquivo.nome_original != arquivo.destino.name else None),
        ),
        sobrescrever=True,
    )


def _upsert_csv(caminho: Path, chave: str, novas: list[dict[str, str]]) -> tuple[int, int]:
    """Acrescenta ou atualiza linhas por `chave`, preservando cabeçalho e ordem.

    Nunca reescreve o arquivo descartando linhas: as existentes que não estão em
    `novas` seguem intactas, na ordem original.

    Returns:
        `(acrescentadas, atualizadas)`.
    """
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        campos = list(leitor.fieldnames or [])
        existentes = list(leitor)

    por_chave = {linha[chave]: i for i, linha in enumerate(existentes)}
    acrescentadas = atualizadas = 0

    for nova in novas:
        completa = {c: str(nova.get(c, "")) for c in campos}
        indice = por_chave.get(completa[chave])
        if indice is None:
            existentes.append(completa)
            por_chave[completa[chave]] = len(existentes) - 1
            acrescentadas += 1
        else:
            existentes[indice] = completa
            atualizadas += 1

    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(existentes)

    return acrescentadas, atualizadas


def registrar_catalogos(
    copiados: list[ArquivoCopiado], hoje: str
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Registra fontes e camadas nos dois catálogos."""
    por_repo: dict[str, list[ArquivoCopiado]] = {}
    for arquivo in copiados:
        por_repo.setdefault(arquivo.repo.nome, []).append(arquivo)

    linhas_fontes = []
    for repo in REPOS:
        arquivos = por_repo.get(repo.nome, [])
        total = sum(a.tamanho for a in arquivos)
        nao_camada = [a for a in arquivos if not a.e_camada]
        extra = (f" {len(nao_camada)} arquivos de código (R/ e DESCRIPTION) entram como "
                 "procedência das funções e NÃO recebem linha em catalogo_camadas.csv: "
                 "não são camadas." if nao_camada else "")
        linhas_fontes.append({
            "id_fonte": repo.id_fonte,
            "nome": f"{repo.nome} — {repo.descricao}",
            "instituicao": repo.instituicao,
            "url": repo.url,
            "data_acesso": hoje,
            "formato": "geojson + zip" if any(a.e_camada for a in arquivos) else "R",
            "tamanho_bytes": str(total),
            "sha256": "",
            "licenca": repo.licenca,
            "autorizacao_fonte": "false",
            "pode_publicar": "false",
            "observacoes": (
                f"[commit pinado {repo.commit} ({repo.data_commit}); "
                f"{len(arquivos)} arquivos copiados para "
                f"data/externos/{SUBDIR}/{repo.nome}/] {NOTA_PUBLICACAO}"
                " sha256 por arquivo está no .json irmão de cada um (o repositório "
                "inteiro não tem um hash único)." + extra
            ),
        })

    linhas_camadas = []
    for arquivo in copiados:
        if not arquivo.e_camada:
            continue
        observacoes = [NOTA_PUBLICACAO]
        if arquivo.campos_removidos:
            observacoes.append(
                f"LGPD: campos removidos na ingestão ({', '.join(arquivo.campos_removidos)}). "
                f"{arquivo.motivo_remocao}"
            )
        if arquivo.nome_original != arquivo.destino.name:
            observacoes.append(f"Renomeado na ingestão; nome_original={arquivo.nome_original}.")
        if arquivo.erro_leitura:
            observacoes.append(
                f"FALHA NA LEITURA GEOESPACIAL: {arquivo.erro_leitura}. Copiado assim mesmo, "
                "sem correção de geometria; CRS lido do cabeçalho do arquivo."
            )
        aproximado = TEMA_APROXIMADO.get(arquivo.destino.stem)
        if aproximado:
            observacoes.append(f"Tema aproximado — {aproximado}.")

        linhas_camadas.append({
            "id_camada": arquivo.id_camada,
            "tema": TEMAS.get(arquivo.destino.stem, "cadastro"),
            "arquivo": paths.relativo(arquivo.destino),
            "fonte_id": arquivo.repo.id_fonte,
            "versao": arquivo.repo.commit_curto,
            "crs": arquivo.crs,
            "data_producao": hoje,
            "sha256": arquivo.sha256,
            "status_conferencia": "pendente",
            "referencias_bib": "",
            "licenca": arquivo.repo.licenca,
            "pode_publicar": "false",
            "observacoes": " ".join(observacoes),
        })

    return (
        _upsert_csv(paths.caminho("catalogo_fontes"), "id_fonte", linhas_fontes),
        # catalogo.upsert aplica a regra da nota de conferência: linha conferida
        # com o mesmo sha256 mantém a conferência; arquivo novo a despromove
        catalogo.upsert("catalogo_camadas", "id_camada", linhas_camadas),
    )


# ---------------------------------------------------------------------------

def relatar(copiados: list[ArquivoCopiado], fontes: tuple[int, int],
            camadas: tuple[int, int]) -> None:
    """Imprime o relatório final."""
    print()
    print("=" * 78)
    print("RELATÓRIO — importação GeoInformação/Bagé (uso interno, sem publicação)")
    print("=" * 78)

    total_bytes = 0
    for repo in REPOS:
        arquivos = [a for a in copiados if a.repo.nome == repo.nome]
        soma = sum(a.tamanho for a in arquivos)
        total_bytes += soma
        novos = sum(1 for a in arquivos if a.rebaixado)
        print(f"\n  {repo.nome} @ {repo.commit_curto} ({repo.data_commit})")
        print(f"    arquivos ....... {len(arquivos)} "
              f"({novos} gravados agora, {len(arquivos) - novos} já conferiam o sha256)")
        print(f"    bytes .......... {soma:,}")
        print(f"    licença ........ {repo.licenca}")

    print(f"\n  TOTAL: {len(copiados)} arquivos, {total_bytes:,} bytes "
          f"({total_bytes / 1048576:.1f} MB)")

    print("\n  Minimização LGPD (campos removidos na ingestão):")
    minimizados = [a for a in copiados if a.campos_removidos]
    if not minimizados:
        print("    (nenhum)")
    for arquivo in minimizados:
        print(f"    {arquivo.repo.nome}/{arquivo.destino.name}"
              + (f"  (era {arquivo.nome_original})"
                 if arquivo.nome_original != arquivo.destino.name else ""))
        print(f"      removidos: {', '.join(arquivo.campos_removidos)}")

    print("\n  Arquivos que falharam na leitura geoespacial:")
    falhos = [a for a in copiados if a.erro_leitura]
    if not falhos:
        print("    (nenhum)")
    for arquivo in falhos:
        print(f"    {arquivo.repo.nome}/{arquivo.destino.name}: {arquivo.erro_leitura}")
        print("      -> copiado assim mesmo, sem correção; registrado em observacoes.")

    print(f"\n  Catálogos: fontes +{fontes[0]} / ~{fontes[1]} | "
          f"camadas +{camadas[0]} / ~{camadas[1]}")
    print("\n  pode_publicar=false em TODAS as linhas. Nada foi copiado para "
          "data/acervo/ nem data/geoportal/.")
    print("=" * 78)


def main() -> None:
    """Executa a ingestão completa."""
    parser = argparse.ArgumentParser(
        description="Importa por cópia os dados da GeoInformação/Bagé (uso interno)."
    )
    parser.add_argument("--forcar", action="store_true",
                        help="Regrava mesmo quando o sha256 do destino já confere")
    args = parser.parse_args()

    hoje = datetime.now(timezone.utc).astimezone().date().isoformat()
    raiz_temp = Path(tempfile.mkdtemp(prefix="geoinformacao-bage-"))
    copiados: list[ArquivoCopiado] = []

    print(f"clone temporário em {raiz_temp} (fora da árvore do projeto)")
    try:
        for repo in REPOS:
            print(f"\n=== {repo.nome} @ {repo.commit} ===")
            clone = clonar_pinado(repo, raiz_temp)
            print(f"  checkout confirmado em {repo.commit}")
            do_repo = ingerir(repo, clone, args.forcar)
            print(f"  {len(do_repo)} arquivo(s) em data/externos/{SUBDIR}/{repo.nome}/")
            for arquivo in do_repo:
                escrever_metadado(arquivo)
            copiados.extend(do_repo)
    finally:
        shutil.rmtree(raiz_temp, ignore_errors=True)
        print(f"\ntemporário removido: {not raiz_temp.exists()}")

    fontes, camadas = registrar_catalogos(copiados, hoje)
    relatar(copiados, fontes, camadas)


if __name__ == "__main__":
    main()
