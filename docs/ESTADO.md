# ESTADO — diário do projeto

Registro cronológico do que foi feito, do que foi conferido e do que ficou
pendente. Entrada nova no topo.

---

## 2026-09-22 — Limites: setores, distritos e área de estudo promovidos a conferido

O responsável conferiu os produtos de limites no QGIS, sobre imagem de satélite,
e aprovou. Promovidos a `status_conferencia=conferido` e `pode_publicar=true`
(a fonte autoriza, `autorizacao_fonte=true`):

| produto | onde está registrado | sha256 congelado | sha256_conteudo |
| --- | --- | --- | --- |
| `setores_2022` | `.json` irmão + `catalogo_camadas.csv` | `392674608e4c…` | `452fcc5f2426…` |
| `distritos_2022` | `.json` irmão + `catalogo_camadas.csv` | `e49445a3f970…` | `84fe4b6792d6…` |
| `config/area_estudo.geojson` | `config/area_estudo.json` (fora do catálogo) | `b0144fc34253…` | — (o `.json` não tem esse campo) |

`limite_municipal` já estava conferido desde 2026-09-20 e não foi tocado.

**Antes de gravar**, os hashes foram recalculados a partir dos arquivos: setores e
distritos batem nos dois hashes (bytes e conteúdo) com o `.json` e o catálogo; a
área de estudo bate no sha256 de bytes. O que foi conferido é o que está congelado.

**O que foi conferido no mapa:**

- cobertura do município sem vão nem sobreposição entre setores;
- limites urbanos seguindo eixos de via e quadras;
- setores de divisa são rurais: a diferença contra o limite de 2025 fica nas
  bordas externas e vem da revisão de divisa entre as edições da malha, não de
  erro de processamento.

**Números:** o responsável citou 929.471 m² contra o limite de 2025 e
1.188 m² contra o de 2022. São medidas em EPSG:31981 (plano, como mede o QGIS):
a primeira é a área dos setores fora do limite de 2025, a segunda a diferença
simétrica contra o limite de 2022. No CRS de área do acervo (ESRI:102033), as
mesmas medidas valem 927.741 m² e 1.186 m², que são os valores já gravados em
`verificacoes`. As observações registram os dois pares, cada um com seu CRS.

**Efeito no A03:** `pode_publicar_estudo("A03_expansao_adensamento")` passou de
`false` (bloqueio: `setores_2022: pode_publicar=false no catálogo`) para `true`:
as 2 camadas declaradas conferem e são publicáveis. As 10 fontes brutas também
estão ok e publicáveis. O comentário do manifesto que avisava do bloqueio foi
atualizado; os sha256 fixados não mudaram.

**Atenção:** `limites_ibge.py` e `area_estudo.py` mantêm o status conferido ao
rodar de novo, desde que o dado seja o mesmo, mas **reescrevem `observacoes`**
com o texto padrão de cada script. O registro da conferência nas observações se
perderia e ficaria só neste diário e no histórico do git.

---

## 2026-09-22 — Censo: bruto do IBGE em `data/raw/`, download direto

Dado bruto oficial pertence a `data/raw/`, não ao acervo. Os 50 arquivos de dado
do Censo (2000, 2010, 2022) e do CNEFE 2022 foram **movidos** de
`data/acervo/censo/` (sha256 conferido antes e depois de cada movimento):

| de | para |
| --- | --- |
| `data/acervo/censo/<ano>/tabelas/` | `data/raw/tabular/ibge/censo_<ano>/` |
| `data/acervo/censo/<ano>/documentacao/`, dicionários do CNEFE | `data/raw/tabular/ibge/censo_<ano>/doc/` |
| `data/acervo/censo/<ano>/malha/` | `data/raw/vetor/ibge/censo_<ano>/` |
| `data/acervo/censo/2022/malha/ftp_com_atributos/` | `data/raw/vetor/ibge/censo_2022/malha_com_atributos/` |
| `data/acervo/censo/2022/cnefe/` (zips) | `data/raw/vetor/ibge/censo_2022/cnefe/` |
| `.json` irmãos antigos, `FONTE.md`, manifestos do REVIA_BG | `docs/procedencia/revia_bg_censo/` (sem edição) |

- `scripts/download/baixar_censo_ibge.py` baixa direto do IBGE a partir da lista
  fixa `config/fontes_censo_ibge.yaml` (gerada uma vez dos manifestos do REVIA_BG);
  `--verificar` confere a origem por HEAD. Em 22/09: 50/50 iguais à origem.
- `scripts/download/censo_revia_bg.py` está SUBSTITUÍDO e não grava mais.
- `data/acervo/censo/` ficou vazia (`.gitkeep`): é para as camadas curadas do
  censo (setores com agregados, harmonização), não para o bruto.
- As entradas de 2026-09-20 abaixo descrevem o estado daquele dia; os caminhos
  nelas são os da época e não foram reescritos.

---

## 2026-09-20 — Reestruturação: acervo compartilhado + estudos derivados

Substitui a estrutura anterior. **Nada foi apagado: tudo que existia foi
movido ou migrado de esquema**, e o que mudou de lugar está listado abaixo.

### O que foi movido

| de | para | volume |
| --- | --- | --- |
| `data/raw/censo/` | `data/acervo/censo/` | 110 arquivos, 987 MB |
| `data/processed/` | `data/acervo/limites/` | GeoPackage + `.json` |
| `js/layers.js`, `js/map-init.js` | `estudos/A02_portal/scripts/` | portal anterior |
| `css/style.css` | `css/estilo.css` | renomeado |

O Censo foi para `data/acervo/censo/` porque `censo` é um dos temas nomeados
do acervo: deixá-lo em `data/raw/` ao lado de um `data/acervo/censo/` vazio
recriaria a duplicação que a reestruturação existe para eliminar. As 9
referências de caminho (script de cópia, catálogo, `ressalvas_censo_bage.md`,
este diário) foram atualizadas junto.

`data/processed/` deixou de existir: a "produção" virou o próprio acervo.

### Catálogos migrados de esquema

As colunas mudaram por inteiro. As 11 fontes e 1 camada foram **convertidas,
não recriadas**:

- `catalogo_fontes.csv`: `id`→`id_fonte`, `autorizacao_para_republicar` (sim/não)
  → `autorizacao_fonte` (bool), mais `formato`, `tamanho_bytes` e
  `pode_publicar`. `tamanho_bytes` foi recuperado dos `.json` irmãos por
  casamento de sha256 (10 das 11 fontes; a 11ª é fonte de conferência sem
  cópia local).
- `catalogo_camadas.csv`: `id`→`id_camada`, e as colunas
  `arquivo_producao`/`arquivo_publicacao` colapsaram em **um só** `arquivo`,
  apontando para a cópia do acervo.

As colunas do esquema antigo que o novo não tem (`tema` da fonte,
`resolucao_ou_escala`, `periodo`, `script_responsavel`, `nome` da camada, o
caminho de publicação) foram **preservadas dentro de `observacoes`**, entre
colchetes — nenhum conteúdo foi descartado.

### Novo: `config/config.yaml` e `scripts/utils/`

Município, CRS e os 32 caminhos passaram a sair de `config/config.yaml`. Os
scripts existentes (`vetor_ibge.py`, `common.py`, `recorte_municipio.py`,
`exportar_*.py`, `validar_catalogos.py`) foram reescritos para lê-los de lá —
não há mais `"EPSG:31981"` nem `"4301602"` literal fora do YAML.

Módulos novos: `paths.py`, `nomes.py`, `metadados.py`, `manifesto.py`,
`publicacao.py`, `indice.py`, `verificar_publicacao.py`. `hashes.py` ganhou
tamanho em bytes e conferência.

### Barreira de publicação

`.githooks/pre-commit` + `git config core.hooksPath .githooks`. Testado com
arquivo de prova sob `data/acervo/`: **commit recusado, rc=1, HEAD inalterado**.
As três regras foram exercitadas isoladamente — (a) camada com
`pode_publicar=false`, (b) dado não-`.json` em área de acervo, (c) saída de
estudo cujo manifesto resolve para `false`. O `.json` irmão na mesma pasta
passa, como deve.

**Desvio deliberado do especificado:** a regra (b) isenta `.gitkeep` e
`manifesto.yaml`. Sem a isenção, a regra (b) e o `.gitignore` se
contradiriam — o `.gitignore` exige versionar esses dois, o hook os barraria,
e nenhum commit passaria. Estão isentos por não carregarem dado.

### Estudos

`A01_base-cartografica`, `A02_portal`, `A03_expansao_adensamento`, cada um com
`manifesto.yaml` (esquema comentado, `camadas: []`), `scripts/`, `derivados/`,
`saidas/` e `README.md`. Todos em `status: reconhecimento`.

Consequência da regra do mais restritivo: com `camadas: []`, os três resolvem
para `pode_publicar=false`. É intencional — quem não declarou entradas não
provou que pode publicar.

### Geoportal

Voltou a ser **esqueleto sem camadas**, conforme pedido: `index.html` +
`css/estilo.css` + `js/mapa.js`, Leaflet centrado em Bagé. O portal anterior
(que carregava o limite municipal e montava rodapé de fontes a partir do
catálogo) foi preservado em `estudos/A02_portal/scripts/` como ponto de
partida para reconstruí-lo na nova arquitetura.

Teste headless adaptado: 7/7 checagens, incluindo a de que **nenhuma** camada
é carregada — um teste que não checasse isso deixaria passar camada entrando
sem catálogo.

### Pendências

1. **Sem `LICENSE` e sem decisão de licenciamento.** Registrado como PENDENTE
   no README. Não publicar no Pages até resolver.
2. `bage.bib` continua sendo o exemplo de uma entrada, a ser substituído pela
   exportação do Zotero.
3. O sha256 do GeoPackage no catálogo muda a cada reexecução do
   `vetor_ibge.py` (o formato grava `last_change` em `gpkg_contents`); foi
   atualizado nesta sessão. Se precisar de hash estável, avaliar
   `OGR_CURRENT_DATE`.
4. `data/geoportal/limite_municipal.geojson` continua publicado e catalogado,
   mas o esqueleto do portal não o carrega — isso é trabalho de A02.

---

## 2026-09-20 — Censo 2000/2010/2022 e CNEFE 2022 importados do REVIA_BG (tag `censo_v1`)

Importação **por cópia**, a partir de `~/projetos/rede_viaria_bage/dados/externos/censo/`
(projeto REVIA_BG), que baixou os arquivos das fontes oficiais do IBGE em 20/09/2026.
**Nada foi baixado por este repositório** e **nada foi escrito no REVIA_BG**: a origem foi
aberta só para leitura.

Script: `scripts/download/censo_revia_bg.py` (com `--dry-run`, idempotente, `--forcar` para
recopiar, `--somente-metadados` para regerar os `.json`).

### Cópia e conferência

| item | valor |
| --- | ---: |
| arquivos copiados | **58** |
| bytes copiados | **1.033.715.032** (985,8 MiB) |
| arquivos de dado (com entrada em manifesto) | 51 |
| arquivos de procedência que vieram junto (`FONTE.md`, `manifesto_censo*.json`) | 7 |
| metadados `.json` irmãos gerados | 51 |

Tamanho medido **antes** de copiar, como pedido: as tabelas de 2022 (recorte BR, por setor e
por bairro) somam **577.556.141 bytes** — setores 509.176.073, bairros 28.068.832, mais dois
`.xlsx`. Abaixo do limite de 2 GB, então a cópia seguiu sem parada.

Quatro conferências, nenhuma dispensando as outras:

1. **origem × manifesto de origem** — 51/51 arquivos de dado com o sha256 registrado nos
   `manifesto_censo_<ano>.json` do REVIA_BG. Detecta origem já corrompida antes de copiar;
2. **cópia × origem** — **58/58** com sha256 idêntico, e 1.033.715.032 bytes dos dois lados;
3. **origem intocada** — 58/58 com o mesmo sha256 do início. Conferido também **fora do
   script**, por `sha256sum` do shell contra uma linha de base tirada antes de qualquer
   escrita: o digest do conjunto das 58 linhas é `3af2752609d82d54…` no início e no fim;
4. **catálogo × disco** — os 9 `sha256` das linhas novas do catálogo conferidos contra o
   arquivo correspondente em `data/acervo/censo/`, 9/9.

**Controle negativo** (uma comparação que dá zero só vale se o comparador detecta diferença):
1 bit trocado no último byte de uma cópia descartável de `2000/malha/4301602.zip`, mesmo
tamanho em bytes — sha256 passou de `39480d0035683aff…` para `d14f56b0be61aaa4…`,
**detectado**. E um sha256 inexistente (`ffff…`) não casou com nenhum arquivo do manifesto,
como tinha de ser.

Datas preservadas (`shutil.copy2`, equivalente a `cp --preserve=timestamps`): conferido por
amostra, `stat` da origem igual ao da cópia.

Idempotência: a segunda execução registrou `copiados: 0 · já presentes e idênticos: 58`.

### Catálogo de fontes

**9 linhas novas**, uma por divulgação (não por arquivo), de `ibge_censo2000_agregado_setores`
a `ibge_cnefe2022_coordenadas`. As 2 linhas pré-existentes ficaram **byte a byte iguais**.
`python scripts/utils/validar_catalogos.py` → **rc=0** (1 aviso antigo, sobre
`ibge_areas_territoriais` não ter script responsável). `testar_validador.py` → **4/4**.

### Licença — o que foi confirmado e o que não foi

Confirmada **na raiz dos dois hosts que serviram os arquivos**, `https://ftp.ibge.gov.br/` e
`https://geoftp.ibge.gov.br/` (HTTP 200, 20/09/2026), com a frase literal:

> "Todos os arquivos aqui disponíveis são públicos."

**Não foi lida** a página formal de termos de uso do IBGE
(`www.ibge.gov.br/acesso-informacao/acoes-e-programas/termos-de-uso.html`): respondeu
**HTTP 403** — desafio Cloudflare —, com e sem cabeçalhos de navegador. Nada foi transcrito
dela. O `autorizacao_para_republicar = sim` das nove linhas se apoia na declaração do FTP e
na prática já adotada para as outras fontes IBGE do acervo; **se a página formal trouxer
condição adicional, isso ainda não foi conferido.** Registrado também em
`docs/ressalvas_censo_bage.md`.

### Ressalvas registradas

`docs/ressalvas_censo_bage.md` (novo) e o campo `observacoes` de cada linha do catálogo:
soma dos setores fechando em 2022 (117.938, diferença 0) e não fechando em 2010 (−476, com
4 setores da malha sem linha na tabela e **causa declarada em aberto**); a diferença de 2000
(−874) sendo **de recorte, não erro**; o geocódigo **não** sendo identificador estável entre
2010 e 2022 (só 141 dos 199 setores em 1:1); **Bagé não ter bairros** na divulgação de 2022,
com controle negativo em Porto Alegre (99); e o CNEFE de Bagé (62.782 endereços, todos com
coordenada, espécies 1 e 2 coincidindo exatamente com `v0003`/`v0004` do agregado por setores).

### Decisões desta sessão, para revisão

1. **Destino `data/acervo/censo/`, não `data/externos/`.** A regra (iv) manda copiar camada *de
   outro projeto* para `data/externos/`. Estes arquivos são **dado bruto do IBGE, como veio da
   fonte**, apenas transportado pelo REVIA_BG — não são camada derivada dele —, então foram
   para `data/raw/`, conforme pedido na especificação da sessão. A procedência da cópia está
   registrada assim mesmo, em `origem_da_copia` de cada `.json` irmão, no
   `manifesto_copia_censo.json` e nas 9 linhas do catálogo. **Se a leitura correta da regra
   (iv) for `data/externos/`, a mudança é um `git mv` mais uma reexecução do script.**
2. **Os 3 `FONTE.md` copiados não são versionados.** A regra do `.gitignore`
   (`data/raw/**` com exceção só para `*.json` e `.gitkeep`) os ignora. Não mexi no
   `.gitignore`, que é contrato declarado do repositório. A perda é pequena — o conteúdo
   deles está em `docs/ressalvas_censo_bage.md` e os dados de procedência estão nos
   manifestos versionados —, mas **é uma decisão do responsável** acrescentar
   `!data/raw/**/FONTE.md` ou deixar como está.
3. **Nada do Censo foi publicado no geoportal.** `data/geoportal/` não mudou, e nenhuma linha
   foi acrescentada a `catalogo_camadas.csv`: não há camada derivada ainda, e a regra (vi)
   exige conferência no mapa antes de congelar qualquer uma.

### Pendências novas

7. **Tabelas do Censo 2000 ainda não lidas** — `.XLS` legado (BIFF8), sem leitor no ambiente
   do REVIA_BG. Aqui o `requirements.txt` também não tem `xlrd`. Os arquivos estão intactos.
8. **CRS da malha de 2000 por decidir** — a urbana vem declarada em EPSG:32621 (UTM 21
   **norte**, hemisfério errado) e a rural sem CRS. Decidir e registrar antes de qualquer
   medição métrica; 7 das 127 geometrias urbanas são inválidas.
9. **Causa dos 4 setores de 2010 sem linha na tabela** — em aberto. Até lá, a soma dos
   setores de 2010 não serve como total municipal.
10. **Termos de uso formais do IBGE não conferidos** — página atrás de Cloudflare.

---

## 2026-09-20 — Criação do repositório (tag `estrutura_v1`)

Criação do acervo do zero, em diretório vazio. Nenhum outro diretório foi
tocado, exceto leitura do repositório de referência.

### Comparação com o repositório de referência (ClimaPampa)

`~/projetos/uruguaiana-clima-saude` estava acessível localmente e **foi lido
integralmente** antes de qualquer decisão. Foram comparados: `README.md`,
`CLAUDE.md`, `.gitignore`, `index.html`, `css/style.css`,
`js/map-init.js`, `js/layers.js`, `scripts/download/vetor_ibge.py`,
`scripts/geoportal/common.py`, `scripts/utils/recorte_municipio.py`,
`scripts/geoportal/test_headless.js`, `package.json`, `requirements.txt`,
`data/catalogo_fontes.csv` e a estrutura de `data/geoportal/`.

**Herdado sem mudança:**

- CRS de trabalho `EPSG:31981`, publicação em `EPSG:4326`;
- `config/area_estudo.geojson` como referência única de recorte, com
  `scripts/utils/recorte_municipio.py` como único ponto de leitura;
- `scripts/geoportal/common.py` (`salvar_geojson_wgs84`), com a mesma regra de
  só reprojetar para 4326 no último passo;
- convenção de nome `{tema}_{fonte}_{periodo}_{resolucao}.{ext}`;
- metadado `.json` irmão de todo arquivo de dado;
- `data/catalogo_fontes.csv` como catálogo vivo;
- idempotência dos downloads (`--forcar` para rebaixar);
- parametrização por código IBGE, sem hardcode do município;
- layout do geoportal: painel lateral à direita, grupos colapsáveis, gaveta no
  mobile, alternância mapa/satélite (OSM + Esri World Imagery), namespace
  global `window.App`, Leaflet 1.9.4 via unpkg com SRI;
- teste headless Playwright no mesmo esquema (`npm run test:geoportal`,
  servidor HTTP efêmero + Chromium headless + screenshot não versionado).

**Divergências deliberadas em relação ao ClimaPampa** (e o motivo):

1. **Download pelo geoftp, não pela API de malhas.** O ClimaPampa usa
   `servicodados.ibge.gov.br/api/v3/malhas`. Aqui a exigência é o geoftp, com
   navegação pelas listagens. Ganho concreto: o produto do geoftp traz o
   atributo `AREA_KM2` (das Áreas Territoriais), que o GeoJSON da API não
   traz — é ele que permitiu conferir a área do município contra o valor
   oficial. Nenhuma URL é montada por adivinhação: o script desce de
   `organizacao_do_territorio/` até o ZIP, exigindo em cada nível que o nome
   esperado esteja listado.
2. **`limite_municipal.geojson` com underscore**, enquanto o ClimaPampa usa
   `limite-municipal.geojson` com hífen. O nome com underscore foi pedido
   explicitamente na especificação deste repositório. Os arquivos de
   *produção* seguem o hífen da convenção herdada
   (`limite-municipal_ibge_2025_municipal.gpkg`), então a divergência está só
   na camada de publicação.
3. **Camadas montadas a partir do catálogo, não escritas no JS.** No
   ClimaPampa, `js/layers.js` lista as camadas em código. Aqui o portal lê
   `data/geoportal/catalogo.json` (projeção dos dois CSV) e monta os grupos
   sozinho. Motivo: o acervo exige rodapé com fonte e licença por camada
   ligadas ao catálogo — deixar a lista em duas fontes de verdade garantiria
   divergência com o tempo.
4. **Catálogo de fontes com colunas novas:** `id`,
   `autorizacao_para_republicar` e `sha256`, que o ClimaPampa não tem. São o
   que sustenta a regra (i) e a rastreabilidade sem versionar o dado.
5. **Segundo catálogo (`catalogo_camadas.csv`) e validador**, inexistentes no
   ClimaPampa.
6. **`.gitignore` com exceções por negação.** O ClimaPampa ignora
   `data/raw/` e `data/processed/` inteiros. Aqui os `.json` irmãos precisam
   ser versionados, o que exige a forma `data/raw/**` + `!data/raw/**/` +
   `!data/raw/**/*.json` — com `data/raw/` (diretório) o Git não desceria na
   árvore e nenhuma negação funcionaria.
7. **`rasterio` fora do `requirements.txt`**, porque nenhum script raster
   existe ainda.

### Área de estudo

`scripts/download/vetor_ibge.py` navegou o geoftp e baixou
`municipio_2025/UFs/RS/RS_Municipios_2025.zip`
(10.139.778 bytes, `Last-Modified: 2026-02-26`,
sha256 `d70d47cc…28513`), recortou `CD_MUN = 4301602` e gravou a área de
estudo em `EPSG:31981`.

Conferência:

| item | valor |
| --- | --- |
| município | Bagé (4301602) |
| feições | 1 |
| CRS | EPSG:31981 |
| área geométrica (calculada em 31981) | 4.096,533 km² |
| área oficial (atributo `AREA_KM2` da malha) | 4.091,554 km² |
| diferença | 4,979 km² (**0,122 %**) |

O valor oficial foi conferido **por uma segunda fonte, independente da
malha**: a planilha `AR_BR_RG_UF_RGINT_RGI_MUN_2025.ods` da publicação
*Áreas Territoriais 2025* do IBGE
(`geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/areas_territoriais/2025/`)
traz para Bagé exatamente **4.091,554 km²** — idêntico ao atributo da malha.

A diferença de 0,122 % é esperada e não indica erro: a área oficial do IBGE é
calculada sobre a superfície do elipsoide, enquanto 4.096,533 km² é a área do
polígono projetado em UTM 21S, e a projeção UTM distorce área ao se afastar do
meridiano central. Bagé (≈54,1° W) está a cerca de 3° do meridiano central do
fuso 21 (57° W), magnitude compatível com a distorção observada.

> **Atualização 2026-09-22:** a regra mudou. Área passou a ser medida no CRS
> equivalente `crs.area` do config (`ESRI:102033`, South America Albers Equal
> Area Conic), via `scripts/utils/medidas.py`: Bagé = **4.091,562 km²**, resíduo
> de **+0,008 km²** (0,0002 %) em relação ao oficial. Os 4.096,533 km² acima
> ficam como registro da medição em UTM. Ver `docs/convencoes.md`, seção 2.

Idempotência conferida: a segunda execução registrou
`já existe, não rebaixando: RS_Municipios_2025.zip` e reproduziu as mesmas
saídas.

### Catálogos e validador

`data/catalogo_fontes.csv` (2 fontes) e `data/catalogo_camadas.csv`
(1 camada publicada). `scripts/utils/validar_catalogos.py` passou (rc=0, 1
aviso: a fonte de conferência `ibge_areas_territoriais` não tem script
responsável, o que é aceitável para consulta pontual).

**Controles negativos** (`scripts/utils/testar_validador.py`) — 4/4 no
resultado esperado:

| controle | esperado | obtido |
| --- | --- | --- |
| positivo: catálogos reais | rc=0 | rc=0 |
| A: id de fonte inexistente | rc=1 | rc=1 — *fonte 'fonte_que_nao_existe' não existe em catalogo_fontes.csv* |
| B: chave bibliográfica inexistente | rc=1 | rc=1 — *chave bibliográfica 'chave2099inexistente' não existe em bage.bib* |
| C: camada publicada com fonte sem licença | rc=1 | rc=1 — *está PUBLICADA mas a fonte 'ibge_malhas_municipais' não tem licença declarada* |

O validador também confere o sha256 do arquivo publicado contra o registrado
no catálogo, o que operacionaliza a regra (vi): se o GeoJSON mudou depois de
congelado, a validação falha até que a conferência no mapa seja refeita.

### Geoportal

`index.html` + `css/style.css` + `js/map-init.js` + `js/layers.js`. Sete
grupos temáticos no painel (Território, Urbano, Mobilidade, Saúde, Educação,
Ambiente, Dados não espaciais); só Território tem camada — os outros seis
aparecem marcados como "Nenhuma camada publicada ainda".

Conferido:

- `python -m http.server`: `index.html`, CSS, os dois JS, `catalogo.json` e
  `limite_municipal.geojson` servidos com HTTP 200;
- teste headless Playwright: **15/15 checagens**, **0 erro de console**,
  **0 exceção de JS**. Entre elas: Leaflet inicializado, os 7 grupos
  presentes, camada carregada do catálogo e ativa no mapa com 1 feição,
  `fitBounds` caindo dentro do bounding box de Bagé (centro resultante
  −31,2462 / −54,0655), alternância mapa/satélite trocando a camada base de
  fato, checkbox desligando e religando a camada, grupos vazios marcados e
  rodapé de fontes com a licença preenchida a partir do catálogo;
- inspeção visual do screenshot: o contorno tracejado coincide com o limite
  municipal de Bagé sobre o basemap OSM, com a sede municipal dentro do
  polígono.

### Bibliografia

`bibliografia/bage.bib` é um **exemplo mínimo de uma entrada**
(`silva2021geobage`), criado só para o pipeline ter o que validar, e **será
substituído inteiro pela exportação do Zotero** (coleção "Bagé", Better
BibTeX com `Keep updated`). O fluxo está descrito em
`bibliografia/README.md`. `bibliografia/indice.md` foi gerado por
`scripts/bibliografia/gerar_indice.py`, com data de geração e sha256 do `.bib`
no cabeçalho.

Não há dependência de biblioteca BibTeX: `scripts/bibliografia/bibtex.py` é um
leitor mínimo, suficiente para o que o Better BibTeX emite.

### Pendências

1. **Substituir `bage.bib` pela exportação real do Zotero.** Enquanto isso não
   acontece, a coluna `referencias_bibliograficas` de
   `catalogo_camadas.csv` está **vazia de propósito**: nenhuma referência real
   cita o limite municipal ainda, e preencher com a entrada de exemplo seria
   inventar um vínculo. A checagem de chaves é exercitada pelo controle
   negativo B.
2. **`sha256` do GeoPackage de produção não é estável entre execuções** — o
   formato grava `last_change` em `gpkg_contents`, então regerar o arquivo
   muda o hash mesmo sem mudança de geometria. Por isso o `sha256` de
   `catalogo_camadas.csv` refere-se ao **arquivo de publicação** (GeoJSON,
   determinístico). A identidade do produto de produção fica ancorada no
   sha256 da fonte + edição da malha, registrados no `.json` irmão. Se for
   preciso hash estável do GPKG, avaliar exportação com timestamp fixo
   (`OGR_CURRENT_DATE`).
3. **Grupos temáticos vazios**: Urbano, Mobilidade, Saúde, Educação, Ambiente
   e Dados não espaciais aguardam a primeira camada.
4. **Nenhum dado não espacial coletado ainda** — `data/raw/tabular/` vazio.
5. **`data/externos/` vazio** — nenhuma camada importada de outro projeto
   (`rede_viaria_bage`, `SIG_bage` e `bage` existem em `~/projetos/` e são
   candidatos naturais, sempre por cópia, conforme a regra (iv)).
6. **Sem repositório remoto e sem push**, conforme pedido.
