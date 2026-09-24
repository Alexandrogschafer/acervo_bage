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

### Nota de conferência

A conferência é registrada em `observacoes`, no `.json` irmão e na linha do
catálogo, num **bloco delimitado** gravado na promoção (ver "Comando de
promoção", abaixo):

```
<texto do script produtor> --- conferência --- <nota do responsável> --- fim da conferência ---
```

O texto fora do bloco pertence ao script produtor e é reescrito a cada
execução. O bloco pertence ao responsável. Todo script que regrava metadado ou
linha de catálogo passa pela mesma regra (`metadados.reconciliar()`,
`catalogo.reconciliar_linha()`, aplicadas por `metadados.escrever()`,
`catalogo.upsert()` e `catalogo.registrar_regravacao()`):

| antes | dado regravado | resultado |
| --- | --- | --- |
| conferido | mesmo `sha256_conteudo` (ou mesmo `sha256`, se um lado não tem conteúdo) | status, `pode_publicar` e bloco **preservados** |
| conferido | conteúdo mudou | bloco **removido**, `status_conferencia=pendente`, `pode_publicar=false` |
| pendente | qualquer | continua pendente: **regravação nunca promove** |

`validar_catalogos.py` recusa bloco de conferência em produto pendente
(conferência 8). `testar_validador.py` tem os controles (C1–C8).

### Comando de promoção

A promoção se faz **só** pelo comando
[`scripts/utils/promover.py`](../scripts/utils/promover.py), depois da
conferência visual:

```bash
python scripts/utils/promover.py --id setores_2022 --nota "Conferido no QGIS sobre imagem de satélite em AAAA-MM-DD: ..."
python scripts/utils/promover.py --id config/area_estudo.geojson --nota "..."
```

`--id` é o `id_camada` do catálogo ou o caminho de um produto fora do catálogo
(com `.json` irmão). Antes de gravar qualquer coisa, o comando confere:

| conferência | se falhar |
| --- | --- |
| produto existe (catálogo ou disco) e tem `.json` irmão | recusa: produto inexistente |
| `sha256_conteudo` registrado bate com o arquivo em disco; `sha256` dos bytes também | recusa: hash divergente |
| linha do catálogo registra o mesmo `sha256` do `.json` | recusa: hash divergente |
| toda fonte (`fonte_id`) tem `autorizacao_fonte=true` no catálogo de fontes | recusa: fonte não autoriza |
| produto derivado (`camada_origem`): a camada de origem está conferida | recusa |
| produto já conferido | recusa, salvo `--substituir-nota` |

Grava `status_conferencia=conferido`, `pode_publicar` e a nota no bloco, no
`.json` e (se há) na linha do catálogo. **`pode_publicar` sai da fonte e nunca
é mais permissivo que ela**: `true` só se todas as fontes, e a camada de origem
quando há, têm `pode_publicar=true`. Recusa sai com rc=1 e nada gravado.
Controles em `testar_validador.py` (PR1–PR5).

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
| `observacoes` | texto livre (com o bloco de conferência, quando conferido) |

Opcionais, gravados só quando existem: procedência (`repo_origem`, `commit`,
`url_origem`, `data_commit`, `nome_original`), derivação e medida (`edicao`,
`camada_origem`, `medidas`, `verificacoes`, `sha256_conteudo`) e
**`complementos`**: campos que um `.json` anterior tinha e que o produtor atual
não gera (anotação à mão, esquema antigo). O produtor os **preserva** ali, em
vez de descartá-los.

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
- `manifesto.py` (contrato dos estudos) segue o mesmo critério, tanto para
  `camadas:` quanto para `fontes_brutas:` (§ 5).

`pode_publicar` é separado de `autorizacao_fonte` de propósito: a fonte pode
autorizar redistribuição e mesmo assim o produto não poder ser publicado (um
derivado que reidentifica endereço, por exemplo). Um nunca se deduz do outro.

---

## 5. O `manifesto.yaml` do estudo

```yaml
estudo: ACERVO_BAGE-A03_expansao_adensamento
pergunta: "A DEFINIR — depende do reconhecimento dos dados"
camadas: []        # - {id:, versao:, sha256:}
fontes_brutas: []  # - {fonte_id:, arquivo:, versao:, sha256:}
referencias_bib: []
status: "reconhecimento"
```

`status`: `planejado` | `reconhecimento` | `em-andamento` | `concluido`.

### Os dois blocos: `camadas:` e `fontes_brutas:`

Um estudo consome coisas de duas naturezas, e o manifesto não as mistura:

| bloco | o que é | catálogo | chave |
| --- | --- | --- | --- |
| `camadas:` | **produto curado do acervo** — passou por conferência e tem linha própria | `data/catalogo_camadas.csv` | `id` |
| `fontes_brutas:` | **dado bruto em `data/raw/`**, exatamente como veio da origem | `data/catalogo_fontes.csv` | `fonte_id` + `arquivo` |

A fonte bruta precisa de `arquivo` além do `fonte_id` porque uma fonte serve
muitos arquivos: uma divulgação do IBGE tem dezenas, cada um com seu `.json`
irmão e seu sha256. O rastro conferido de uma fonte bruta é esse `.json`
irmão, e o arquivo tem de estar sob `data/raw/` — **bruto que saiu de lá não é
mais bruto**; se virou produto curado, é camada.

**Decisão (2026-09-22): dado bruto NÃO é promovido a camada.** Copiar o bruto
do IBGE para `data/acervo/` só para caber em `camadas:` criaria uma segunda
cópia do mesmo dado, sem nada acrescentado, e duas verdades sobre o mesmo
arquivo. O bruto fica em `data/raw/`, declarado em `fontes_brutas:`. **O que
virará camada é o PRODUTO do A03** — setores com os agregados anexados, grade
recortada ao município, junção célula → setor —, e só depois de conferido,
pela promoção descrita no § 3.

O manifesto é um **contrato**: diz sobre qual estado do acervo aquele
resultado foi produzido. [`scripts/utils/manifesto.py`](../scripts/utils/manifesto.py)
resolve cada camada contra `data/catalogo_camadas.csv`, e cada fonte bruta
contra `data/catalogo_fontes.csv` e o `.json` irmão do arquivo, devolvendo:

| situação | significado |
| --- | --- |
| `ok` | o dado fixado é o dado atual do acervo (critério abaixo) |
| `divergente` | a entrada existe, mas mudou desde que o estudo a fixou (ou não fixou sha256, ou a fonte bruta está fora de `data/raw/`) |
| `ausente` | o id não está no catálogo, ou o arquivo sumiu do disco, ou a fonte bruta está sem `.json` irmão |

Cada camada do manifesto pode fixar `sha256` (do arquivo) e, opcionalmente,
`sha256_conteudo` (§ 4). O critério é o mesmo do validador, **conteúdo antes de bytes**:
se `sha256_conteudo` foi fixado, ele decide; senão, vale o `sha256` do arquivo; e um
arquivo regravado com outros bytes continua `ok` quando o manifesto fixou o sha256 do
catálogo e o `sha256_conteudo` do `.json` irmão confere com o recalculado. Controles em
`scripts/utils/testar_validador.py` (M1–M5).

Para `fontes_brutas:` vale o mesmo critério, com o `.json` irmão no lugar da
linha do catálogo: `sha256_conteudo` decide quando fixado (e o arquivo que não
for dado legível por conteúdo — um zip tabular, um xlsx — é acusado em vez de
passar em silêncio); senão vale o `sha256` dos bytes; a `versao` fixada tem de
bater com a do `.json`. Controles: `testar_validador.py` (B1–B5).

[`scripts/utils/indice.py`](../scripts/utils/indice.py) publica as duas listas
separadas em `docs/indice_camadas_estudos.md`, com os dois índices reversos:
camada → estudos e fonte bruta → estudos.

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

**Uma saída de estudo herda a restrição MAIS RESTRITIVA entre todas as
entradas declaradas no manifesto: as camadas (`camadas:`) E as fontes brutas
(`fontes_brutas:`).** Basta uma camada ou uma fonte bruta com
`pode_publicar=false` para a saída inteira ser `false`. O `pode_publicar` da
camada vem de `data/catalogo_camadas.csv`; o da fonte bruta, de
`data/catalogo_fontes.csv`. (Regra ampliada às fontes brutas em 2026-09-22;
antes só as camadas contavam.)

Restrição **não se dilui em processamento**: se uma entrada não pode ser
redistribuída, o produto que a incorpora também não pode, por mais
transformado que esteja.

Dois pontos deliberados em
[`scripts/utils/publicacao.py`](../scripts/utils/publicacao.py):

1. **Manifesto sem nenhuma entrada devolve `false`**, não `true`. Vazio é
   `camadas:` E `fontes_brutas:` vazios ao mesmo tempo. Quem não declarou
   entradas não provou que pode publicar; o vácuo é "não sei", e "não sei" não
   autoriza publicação em repositório público. Manifesto só com fontes brutas,
   todas publicáveis, resolve para `true` (regra ajustada em 2026-09-22; antes,
   faltar `camadas:` bastava para `false`).
2. **Entrada `divergente` ou `ausente` também bloqueia**, seja camada ou
   fonte bruta. Se o acervo mudou desde que o estudo fixou o sha256, não dá
   para afirmar sob qual licença a saída foi produzida.

### Licença do repositório × licença do dado

Decidido pelo responsável em 2026-09-24. Substitui a regra anterior, que proibia
publicar no GitHub Pages enquanto não houvesse licença.

| o quê | licença | arquivo |
| --- | --- | --- |
| código (scripts, geoportal, testes) | MIT | `LICENSE` |
| documentação e produtos próprios (catálogos, metadados, textos dos estudos, figuras produzidas aqui) | CC BY 4.0 | `LICENSE-DOCS.md` |
| **dados** | **a de cada fonte**, registrada camada a camada no catálogo | `data/catalogo_fontes.csv`, `data/catalogo_camadas.csv`, `.json` irmão |

- A licença do repositório **não relicencia** dado de terceiro.
- **Nenhuma saída é mais permissiva que a fonte dela**: vale a propagação desta seção.
  Uma figura ou tabela que incorpora dado de fonte restrita herda a restrição.
- **Publicar no GitHub Pages está permitido**, mas condicionado ao `pode_publicar` de
  cada camada, pela barreira do § 8.
  - As camadas sem autorização de republicação seguem `pode_publicar=false` e fora
    do repositório.

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

## 10. Legislação

Leis, leis complementares e decretos municipais, com os documentos que chegam
junto (anexos, material de processo legislativo, fichas do SICG/IPHAN).

```
data/raw/legislacao/bage/       os arquivos, como vieram, com o NOME ORIGINAL
data/catalogo_legislacao.csv    uma linha por norma
data/catalogo_fontes.csv        o conjunto como fonte (legislacao_municipal_bage)
```

- **Onde fica.** Em `data/raw/legislacao/bage/` (`paths.raw_legislacao`),
  registrado por [`scripts/acervo/registrar_legislacao.py`](../scripts/acervo/registrar_legislacao.py).
  O nome do arquivo **não** é reescrito na convenção do § 3: ele é procedência.
  Todo arquivo tem `.json` irmão (§ 4) com `sha256`; `sha256_conteudo` não se
  aplica a documento. Quando dois formatos do mesmo documento teriam o mesmo
  `.json` irmão, o segundo vai para uma subpasta (`formato_doc/`), com o nome
  intacto.
- **Catálogo próprio.** `data/catalogo_legislacao.csv`:

  ```
  id_norma, tipo, numero, ano, data, ementa, assunto, arquivo, sha256,
  situacao, observacoes
  ```

  Preenchido **lendo o cabeçalho do documento**, não o nome do arquivo (que às
  vezes engana: `lei_altera_paragrafo_2015.pdf` é a LC 054/2015, que altera
  uso rural para urbano). O que não se lê com segurança fica **em branco** e é
  explicado em `observacoes`; nada é inferido. `situacao` (`vigente`,
  `revogada`, `alterada`) só quando um texto do acervo a declara, citando qual.
  Documento que não é norma (relatório, ficha, mapa) não tem linha: fica só com
  o `.json`. `validar_catalogos.py` confere o catálogo contra os `.json`
  irmãos e o disco (conferência 9; controles L1–L2).
- **Texto de lei × anexo cartográfico — dois regimes.**

  | o quê | regime | `pode_publicar` |
  | --- | --- | --- |
  | texto de lei municipal | não é objeto de proteção autoral (Lei 9.610/1998, art. 8º, IV) | `true`, licença "legislação municipal — texto de lei, domínio público" |
  | anexo cartográfico extraído como camada | **base de dados**: geometria redesenhada, com base cartográfica de terceiros | decidido **caso a caso**, na linha própria do catálogo de camadas |
  | documento que não é lei (relatório de consultoria, material do IPHAN) | licença **não se presume** pela vizinhança com a lei | `false` enquanto a licença não for declarada |

  O `pode_publicar=true` do PDF de uma lei vale para o **documento**. Extrair
  um mapa anexo como camada é outra decisão, tomada depois, e a camada entra
  pela promoção do § 1, com conferência visual.
- **Não versionado, como todo dado.** `*.pdf` e `data/raw/**` continuam fora
  do git (o texto de lei *poderia* ser versionado, mas os arquivos somam
  ~200 MB e um passa de 60 MB); o rastro público é o `.json` e o catálogo.

---

## 11. O que NÃO fazer

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
