# ESTADO — diário do projeto

Registro cronológico do que foi feito, do que foi conferido e do que ficou
pendente. Entrada nova no topo.

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
