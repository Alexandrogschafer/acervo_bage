codigo_projeto: ACERVO_BAGE

# CLAUDE.md — contexto do ACERVO_BAGE

Lido pelo Claude Code no início de cada sessão.

**As regras operacionais completas estão em [`docs/convencoes.md`](docs/convencoes.md).**
Este arquivo é o resumo do que muda a forma de trabalhar aqui.

## O que é

Acervo do município de **Bagé/RS** (IBGE `4301602`): dados espaciais, dados
não espaciais e bibliografia, com geoportal estático. Repositório **público**.

Arquitetura: **acervo compartilhado + estudos derivados**.

- `data/acervo/<tema>/` é a **cópia principal**, catalogada e com hash.
- `estudos/<id>/` **consome** o acervo e **nunca escreve nele**, declarando em
  `manifesto.yaml` quais camadas usa, em que versão e sha256.

## Parâmetros: só em `config/config.yaml`

Município, CRS e caminhos saem de `config/config.yaml`, lido por
`scripts/utils/paths.py`. **Se aparecer um `"EPSG:31981"`, um `"4301602"` ou um
caminho literal fora do YAML, é bug.**

- CRS de produção `EPSG:31981` (métrico — operações, distância e perímetro)
- CRS de publicação `EPSG:4326` (só o Leaflet consome; reprojetar por último)
- CRS de área `ESRI:102033` (equivalente): **toda área** é medida nele, via
  `scripts/utils/medidas.py`, com `crs_medicao_area` registrado junto

## Módulos de `scripts/utils/` (usar, não reimplementar)

| módulo | papel |
| --- | --- |
| `paths.py` | config, raiz, caminhos; erro legível se faltar chave; `carregar_area_estudo()` já no CRS de produção |
| `catalogo.py` | lê/atualiza os catálogos; `camada_conferida()` confere o sha256 antes de derivar |
| `medidas.py` | área no CRS equivalente (`area_m2`, `areas_m2`) |
| `hashes.py` | sha256 em blocos + tamanho |
| `conteudo.py` | `sha256_conteudo`: hash do DADO (geometria + atributos + CRS), não dos bytes |
| `nomes.py` | `{tema}_{fonte}_{ano-ou-periodo}_{resolucao}.{ext}` |
| `metadados.py` | o `.json` irmão de todo produto |
| `manifesto.py` | resolve o contrato do estudo contra o acervo |
| `publicacao.py` | propagação de `pode_publicar` (mais restritivo vence) |
| `indice.py` | gera `docs/indice_camadas_estudos.md` |
| `validar_catalogos.py` | coerência dos catálogos |
| `verificar_publicacao.py` | barreira de pre-commit |

## As regras que mais pegam

1. **Estudo nunca escreve no acervo.** Camada derivada entra por **promoção**:
   conferência visual no mapa → cópia para `data/acervo/<tema>/` → linha no
   catálogo com `status_conferencia=conferido`.
2. **`pode_publicar` propaga pelo mais restritivo.** Uma camada `false` torna
   a saída inteira `false`. Manifesto sem camadas declaradas resolve para
   `false` — o vácuo é "não sei", e "não sei" não autoriza publicar.
3. **Dado não é versionado; o rastro é.** `.json` irmão + linha no catálogo +
   sha256. A barreira de pre-commit recusa arquivo de dado estagiado.
4. **Camada de outro projeto entra por CÓPIA**, com versão e sha256 fixados —
   nunca por leitura direta de `../outro_projeto/`.
5. **Divergência de manifesto é aviso, não correção.** Nada atualiza o sha256
   fixado sozinho: isso apagaria a evidência de que o resultado veio de outro
   dado.
6. **Nunca montar URL de download por adivinhação.** Navegar as listagens/APIs
   documentadas, para que mudança na fonte **falhe** em vez de baixar outra
   coisa em silêncio.
7. **Arquivos gerados não se editam à mão:** `bibliografia/bage.bib` (Zotero),
   `bibliografia/indice.md`, `docs/indice_camadas_estudos.md`,
   `data/geoportal/*.geojson`, `data/geoportal/catalogo.json`.

## Depois de clonar

```bash
git config core.hooksPath .githooks   # hooks não são clonados; sem isso, sem barreira
```

## Antes de commitar

```bash
python scripts/utils/validar_catalogos.py
python scripts/utils/indice.py
```

## Pendências conhecidas

- **Sem `LICENSE`** e sem decisão de licenciamento — ver a seção "Licença e
  publicação" do README. Não publicar no GitHub Pages até resolver.
- `bibliografia/bage.bib` ainda é um exemplo de uma entrada; será substituído
  pela exportação do Zotero.
- Os três estudos estão em `reconhecimento`, com `camadas: []`.
