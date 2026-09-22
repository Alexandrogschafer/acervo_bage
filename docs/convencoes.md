# Convenções do ACERVO_BAGE

Regras operacionais do repositório. Cada uma existe porque quebrá-la produz um
dano concreto — republicação indevida, dado irreprodutível, número que ninguém
consegue explicar seis meses depois. Onde há uma decisão discutível, o motivo
está escrito junto.

Os parâmetros citados aqui (código IBGE, CRS, caminhos) **não são repetidos em
código**: saem de [`config/config.yaml`](../config/config.yaml), lido por
[`scripts/utils/paths.py`](../scripts/utils/paths.py).

---

## 1. Arquitetura: acervo compartilhado, estudos derivados

```
data/acervo/<tema>/     A CÓPIA PRINCIPAL. Compartilhada por todos os estudos.
estudos/<id>/           Consome o acervo. NUNCA escreve nele.
data/geoportal/         Publicação: o que o portal estático serve.
```

**O estudo lê o acervo e nunca escreve nele.** Um estudo que grava direto no
acervo transforma um insumo compartilhado em subproduto de um trabalho
específico: os outros estudos passam a depender de uma decisão que não
tomaram e que não está documentada em lugar nenhum. Saídas de estudo ficam em
`estudos/<id>/saidas/`, intermediários em `estudos/<id>/derivados/`.

### Regra de promoção

Camada derivada dentro de um estudo só entra no acervo por **promoção**:

1. o responsável abre o produto **no mapa** e confere visualmente;
2. o arquivo é copiado para `data/acervo/<tema>/`;
3. ganha linha em `data/catalogo_camadas.csv` com
   `status_conferencia = conferido`;
4. ganha `.json` irmão.

A conferência visual não é formalidade. Erro de CRS, de topologia e de junção
atravessa todos os testes automáticos e aparece na primeira olhada no mapa.
`validar_catalogos.py` recusa `pode_publicar=true` em camada que ainda esteja
com `status_conferencia = pendente`.

### Camadas de outros projetos entram por CÓPIA

Camada vinda de outro repositório é **copiada** para `data/externos/` (ou,
quando é dado bruto oficial apenas transportado por outro projeto, para o tema
correspondente de `data/acervo/`), com **versão e sha256 fixados** no `.json`
irmão e no catálogo.

Nunca ler direto de `../outro_projeto/...`: isso faz o acervo depender do
estado atual de um diretório que ninguém controla e que não existe para quem
clona o repositório. A cópia é o que torna o acervo reproduzível; o sha256 é o
que permite detectar que a origem mudou.

---

## 2. CRS

| papel | CRS | onde |
| --- | --- | --- |
| **produção** | `EPSG:31981` (SIRGAS 2000 / UTM 21S) | `data/acervo/`, `data/raw/`, todo processamento |
| **publicação** | `EPSG:4326` (WGS 84) | `data/geoportal/`, `config/area_estudo.geojson` (RFC 7946) |
| **área** | `ESRI:102033` (South America Albers Equal Area Conic) | só para **medir área** — nenhum arquivo é gravado nele |

Distância, perímetro, buffer e toda operação espacial (união, diferença,
dissolve, clip) acontecem no CRS de **produção**, que é métrico. A reprojeção
para publicação é **sempre o último passo**, porque `EPSG:4326` é em graus:
medir nele produz número errado sem nenhum aviso.

**Área é medida no CRS de área, nunca no de produção.** O UTM é conforme, não
equivalente: fora do meridiano central ele infla a área, e Bagé fica na borda
leste do fuso 21 (≈54° W, a ~3° do meridiano central 57° W). Medido em
`EPSG:31981`, o município dá 4.096,533 km², 0,12 % acima dos 4.091,554 km²
oficiais do IBGE; em `ESRI:102033` dá 4.091,562 km² (resíduo de 0,008 km²).

Na prática:

- a operação continua no CRS de produção; a **geometria resultante** é
  reprojetada para o CRS de área só para ser medida — usar
  `scripts/utils/medidas.py` (`area_m2`, `areas_m2`), nunca `.area` direto;
- todo número de área gravado em metadado leva, no mesmo bloco, o campo
  **`crs_medicao_area`**; perímetro e distância levam `crs_medicao_distancia`;
- o CRS de área vem de `crs.area` no config (`paths.crs_area()`), como os
  demais.

Dado bruto pode chegar em qualquer CRS; reprojetar é obrigatório **antes** de
qualquer operação espacial (join, clip, buffer), nunca depois.

---

## 3. Nomes de arquivo

```
{tema}_{fonte}_{ano-ou-periodo}_{resolucao}.{ext}
```

Exemplos:

```
limite-municipal_ibge_2025_municipal.gpkg
setores_ibge-censo_2022_setor-censitario.gpkg
precipitacao_inmet_2010-2025_mensal.csv
```

`_` separa os quatro componentes, então **`_` não pode aparecer dentro de um
componente** — dentro use `-`. É isso que torna o nome decomponível de volta
sem ambiguidade. Implementado e validado em
[`scripts/utils/nomes.py`](../scripts/utils/nomes.py) (`montar`, `decompor`,
`valido`).

**Exceção, no geoportal:** o GeoJSON publicado leva o nome do **id da camada**
(`limite_municipal.geojson`), não o nome longo do acervo. No portal o que
identifica é o id do catálogo, e é por ele que
`scripts/geoportal/exportar_catalogo.py` resolve o arquivo.

---

## 4. O `.json` irmão

Todo arquivo de dado tem, ao lado, um `.json` com o mesmo nome base. Como o
dado pesado não é versionado e o `.json` é, **ele é o único rastro público do
produto**. Gerado por
[`scripts/utils/metadados.py`](../scripts/utils/metadados.py).

| campo | conteúdo |
| --- | --- |
| `arquivo` | caminho relativo à raiz do repositório |
| `tema` | tema do acervo |
| `fonte_id` | id em `data/catalogo_fontes.csv` |
| `versao` | versão do produto |
| `crs` | CRS do arquivo (vazio para tabular) |
| `data_producao` | ISO 8601 com fuso |
| `sha256` | hash do arquivo |
| `sha256_conteudo` | camadas vetoriais do acervo: hash do **conteúdo** (ver abaixo) |
| `tamanho_bytes` | tamanho do arquivo |
| `licenca` | texto da licença da fonte |
| `autorizacao_fonte` | bool — a fonte autoriza redistribuição? |
| `pode_publicar` | bool — este produto pode ir para o repositório público? |
| `referencias_bib` | lista de chaves de `bibliografia/bage.bib` |
| `campos_removidos` | lista de campos suprimidos (ex.: dado pessoal) |
| `status_conferencia` | `pendente` \| `conferido` |
| `observacoes` | texto livre |

Formato: **UTF-8, `indent=2`, chaves ordenadas**. `escrever()` **não
sobrescreve** um `.json` existente sem `sobrescrever=True` — metadado apagado
por engano é rastro perdido.

### `sha256` × `sha256_conteudo`

O `sha256` do arquivo muda sem que o dado mude: um GeoPackage é um banco
SQLite, e a ordem das páginas, o contador de alterações do cabeçalho e o
carimbo `last_change` dependem de como e quando ele foi escrito. Por isso
toda camada vetorial do acervo registra também `sha256_conteudo`
([`scripts/utils/conteudo.py`](../scripts/utils/conteudo.py)): CRS + nomes
de colunas + cada feição como atributos em JSON canônico e WKB da geometria
normalizada, com as feições ordenadas pelo próprio hash (independe do fid).
Nenhuma coordenada é arredondada: é igualdade exata de dado.

- **Comparar camadas** (`--verificar`, idempotência dos produtores, "posso
  derivar desta camada?") é sempre por `sha256_conteudo`, nunca pelo sha256 do
  arquivo. Produtor que gera o mesmo conteúdo **não substitui** o arquivo, e o
  sha256 conferido continua valendo.
- **Validador:** arquivo com sha256 diferente do catálogo é aceito (com aviso)
  se o `sha256_conteudo` recalculado bate com o do `.json`; se não bate, é
  erro — o dado mudou e a conferência caducou. Quando o `.json` registra
  `sha256_conteudo`, ele é sempre recalculado e tem de bater.
- Produtores gravam GeoPackage com `last_change` fixo (Last-Modified da origem,
  via `OGR_CURRENT_DATE`), para que a mesma entrada dê os mesmos bytes.
- `manifesto.py` (contrato dos estudos) ainda compara o sha256 do arquivo.

`pode_publicar` é separado de `autorizacao_fonte` de propósito: a fonte pode
autorizar redistribuição e mesmo assim o produto não poder ser publicado (um
derivado que reidentifica endereço, por exemplo). Um nunca se deduz do outro.

---

## 5. O `manifesto.yaml` do estudo

```yaml
estudo: ACERVO_BAGE-A03_expansao_adensamento
pergunta: "A DEFINIR — depende do reconhecimento dos dados"
camadas: []        # - {id:, versao:, sha256:}
referencias_bib: []
status: "reconhecimento"
```

`status`: `reconhecimento` | `em-andamento` | `concluido`.

O manifesto é um **contrato**: diz sobre qual estado do acervo aquele
resultado foi produzido. [`scripts/utils/manifesto.py`](../scripts/utils/manifesto.py)
resolve cada camada contra `data/catalogo_camadas.csv` e contra o arquivo em
disco, devolvendo:

| situação | significado |
| --- | --- |
| `ok` | o dado fixado é o dado atual do acervo (critério abaixo) |
| `divergente` | a camada existe, mas mudou desde que o estudo a fixou |
| `ausente` | o id não está no catálogo, ou o arquivo sumiu do disco |

Cada camada do manifesto pode fixar `sha256` (do arquivo) e, opcionalmente,
`sha256_conteudo` (§ 4). O critério é o mesmo do validador, **conteúdo antes de bytes**:
se `sha256_conteudo` foi fixado, ele decide; senão, vale o `sha256` do arquivo; e um
arquivo regravado com outros bytes continua `ok` quando o manifesto fixou o sha256 do
catálogo e o `sha256_conteudo` do `.json` irmão confere com o recalculado. Controles em
`scripts/utils/testar_validador.py` (M1–M5).

**A resolução nunca atualiza o manifesto sozinha.** Divergência é aviso, não
correção: se o acervo mudou, quem decide se o estudo continua válido é o
responsável. Reescrever o sha256 automaticamente apagaria justamente a
evidência de que o resultado foi produzido sobre outro dado.

---

## 6. Catálogos

### `data/catalogo_fontes.csv`

```
id_fonte, nome, instituicao, url, data_acesso, formato, tamanho_bytes,
sha256, licenca, autorizacao_fonte, pode_publicar, observacoes
```

### `data/catalogo_camadas.csv`

```
id_camada, tema, arquivo, fonte_id, versao, crs, data_producao, sha256,
status_conferencia, referencias_bib, licenca, pode_publicar, observacoes
```

`tema` usa o vocabulário dos diretórios de `data/acervo/`: `limites`, `censo`,
`hidrografia`, `viario`, `cadastro`, `educacao`, `saude`, `ambiental`.

Conferir com `python scripts/utils/validar_catalogos.py` **antes de cada
commit**; os controles do próprio validador estão em
`scripts/utils/testar_validador.py`.

---

## 7. Propagação de `pode_publicar`

**Uma saída de estudo herda a restrição MAIS RESTRITIVA entre todas as camadas
declaradas no manifesto.** Basta uma camada com `pode_publicar=false` para a
saída inteira ser `false`.

Restrição **não se dilui em processamento**: se uma entrada não pode ser
redistribuída, o produto que a incorpora também não pode, por mais
transformado que esteja.

Dois pontos deliberados em
[`scripts/utils/publicacao.py`](../scripts/utils/publicacao.py):

1. **Manifesto sem camadas devolve `false`**, não `true`. Quem não declarou
   entradas não provou que pode publicar; o vácuo é "não sei", e "não sei" não
   autoriza publicação em repositório público.
2. **Camada `divergente` ou `ausente` também bloqueia.** Se o acervo mudou
   desde que o estudo fixou o sha256, não dá para afirmar sob qual licença a
   saída foi produzida.

---

## 8. Barreira de publicação (hook de pre-commit)

[`scripts/utils/verificar_publicacao.py`](../scripts/utils/verificar_publicacao.py)
percorre os arquivos **estagiados** e recusa o commit, nomeando o arquivo,
quando ele:

- **(a)** consta em `data/catalogo_camadas.csv` com `pode_publicar=false`;
- **(b)** está sob `data/acervo/`, `data/externos/` ou `estudos/*/derivados/`
  **sem ser `.json`**;
- **(c)** está sob `estudos/*/saidas/` e o manifesto do estudo resolve para
  `pode_publicar=false`.

Exceções da regra (b): **`.gitkeep` e `manifesto.yaml`**. São exigidos pelo
contrato do `.gitignore` (o primeiro mantém o diretório vazio na árvore, o
segundo é o contrato do estudo) e não carregam dado. Sem a exceção, a regra
(b) e o `.gitignore` se contradiriam e nenhum commit passaria.

O `.gitignore` já barra esses arquivos; o hook é a **segunda** barreira, para o
caso de `git add -f` ou de uma regra de ignore alterada por engano.

### Reinstalar o hook depois de um clone

Hooks **não são clonados pelo Git**. Depois de `git clone`, rode uma vez:

```bash
git config core.hooksPath .githooks
```

Conferir: `git config --get core.hooksPath` deve imprimir `.githooks`.
Sem isso o repositório funciona, mas **sem a barreira** — e é exatamente nesse
estado que o commit distraído passa.

Emergência documentada: `git commit --no-verify`. Se for preciso usar, diga no
corpo do commit por quê.

---

## 9. Bibliografia

`bibliografia/bage.bib` é a **exportação automática** da coleção "Bagé" do
Zotero (plugin Better BibTeX, `Keep updated` ligado). **Nunca editar à mão:**
a edição se perde no próximo salvamento do Zotero — a correção se faz no item
do Zotero.

O mesmo vale para os arquivos gerados: `bibliografia/indice.md`
(`scripts/bibliografia/gerar_indice.py`) e
`docs/indice_camadas_estudos.md` (`scripts/utils/indice.py`).

PDFs ficam no Zotero, **nunca no git**: `*.pdf` está ignorado em todo o
repositório. O acervo é público e quase todo PDF de referência é protegido por
direito autoral; o rastro público é o `.bib` (metadados + DOI/URL), suficiente
para localizar a obra na origem.

---

## 10. O que NÃO fazer

- Não montar URL de download por adivinhação — navegar as listagens/APIs
  documentadas, de modo que uma mudança na fonte **falhe** em vez de baixar
  outra coisa em silêncio.
- Não repetir código IBGE, CRS ou caminho em script: vem de `config.yaml`.
- Não escrever em `data/acervo/` a partir de um estudo.
- Não editar à mão nada gerado: `bage.bib`, `indice.md`,
  `docs/indice_camadas_estudos.md`, `data/geoportal/*.geojson`,
  `data/geoportal/catalogo.json`.
- Não commitar dado: ele é rastreado por catálogo + `.json` irmão + sha256.
- Não misturar CRS sem reprojetar explicitamente antes da operação espacial.
