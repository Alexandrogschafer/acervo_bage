# acervo_bage

Acervo do município de **Bagé/RS** (código IBGE `4301602`): **dados
espaciais**, **dados não espaciais** e **bibliografia**, com um **geoportal
estático** publicando as camadas liberadas.

O repositório reúne três blocos: os **scripts** que baixam, padronizam e
catalogam os dados; o **geoportal** (`index.html` + `css/` + `js/`), um mapa
Leaflet que publica as camadas; e a **bibliografia** (`bibliografia/`),
mantida no Zotero e exportada para cá.

Segue o padrão do repositório [`uruguaiana-clima-saude`](../uruguaiana-clima-saude)
(ClimaPampa) — pipeline Python + geoportal Leaflet estático, parametrização por
código IBGE, metadados `.json` irmãos e catálogo de fontes vivo.

## Camadas disponíveis

O painel lateral organiza as camadas em grupos colapsáveis. Os grupos são
montados em tempo de execução a partir de `data/geoportal/catalogo.json`
(projeção dos catálogos CSV), então **publicar camada nova não exige editar o
HTML**.

- **Mapa base:** alternância entre mapa (OpenStreetMap) e imagem de satélite
  (Esri World Imagery).
- **Território:** limite municipal de Bagé (IBGE, malhas municipais 2025).
- **Urbano**, **Mobilidade**, **Saúde**, **Educação**, **Ambiente**,
  **Dados não espaciais:** grupos preparados, **ainda sem camada publicada** —
  aparecem no painel marcados como vazios.
- **Fontes e licenças:** uma entrada por camada publicada, com instituição,
  fonte, licença, versão e data, lida do catálogo.

Este é o estado inicial do acervo: **uma camada publicada**. O inventário
técnico completo (toda fonte, com licença, autorização de republicação,
resolução/escala, período, script responsável e sha256) está em
`data/catalogo_fontes.csv`, e o de camadas publicáveis em
`data/catalogo_camadas.csv`.

## Dados não espaciais

Séries tabulares sem geometria própria (demografia, saúde, economia,
educação) entram em `data/raw/tabular/`, com `.json` irmão, e são registradas
no catálogo de fontes com `tema` adequado. No geoportal aparecem no grupo
"Dados não espaciais" como referência, não como camada de mapa.

**Nenhuma série tabular foi coletada ainda** — a estrutura está pronta e
vazia.

## Bibliografia

- `bibliografia/bage.bib` — exportação automática da coleção **"Bagé"** do
  Zotero (plugin Better BibTeX, `Keep updated`). **Arquivo gerado: nunca
  editar à mão.**
- `bibliografia/indice.md` — índice legível gerado do `.bib`
  (`python scripts/bibliografia/gerar_indice.py`), com chave, autores, ano,
  título, veículo, tema, DOI/URL e as camadas do geoportal que citam cada
  referência, mais a data de geração e o sha256 do `.bib` de origem.
- `bibliografia/pdfs/` — ponto de montagem local, **inteiramente ignorado pelo
  git**: os PDFs ficam no Zotero (repositório público + material protegido por
  direito autoral).

O `bage.bib` atual é um **exemplo mínimo de uma entrada**, criado só para o
pipeline ter o que validar; será substituído pela primeira exportação do
Zotero. Ver `bibliografia/README.md`.

## Padrões técnicos

- **Linguagem:** Python. Bibliotecas: `geopandas`, `pyogrio`, `shapely`,
  `pandas`, `pyproj`, `requests`, `pyyaml`.
- **CRS padrão:** SIRGAS 2000 / UTM 21S — `EPSG:31981`. Dado bruto pode vir em
  outro CRS; todo processamento reprojeta para o padrão. A publicação no
  geoportal é em `EPSG:4326` (exigência do Leaflet).
- **Área de estudo:** referenciada sempre a partir de
  `config/area_estudo.geojson`.
- **Parametrização por código IBGE:** default `4301602` (Bagé/RS), nada fixo no
  código — a UF sai dos dois primeiros dígitos.
- **Origem do dado:** navegar listagens/APIs documentadas; nunca montar URL de
  download por adivinhação.
- **Scripts de download:** idempotentes, registrando URL, `Last-Modified`,
  tamanho e sha256.
- **Nomenclatura:** `{tema}_{fonte}_{ano-ou-periodo}_{resolucao}.{ext}` —
  ex.: `limite-municipal_ibge_2025_municipal.gpkg`.
- **Metadados:** todo arquivo de dado tem um `.json` irmão (fonte, URL,
  transformação, sha256, data). Versionados mesmo quando o dado não é.
- **Produção × publicação:** GeoPackage em `data/processed/` (produção, não
  versionado, rastreado por hash) × GeoJSON em `data/geoportal/` (publicação,
  versionado — o portal estático precisa dele).

As regras completas do repositório estão em [`CLAUDE.md`](CLAUDE.md).

## Estrutura de pastas

```
acervo_bage/
├── README.md · CLAUDE.md · requirements.txt · requirements.lock.txt
├── config/
│   └── area_estudo.geojson          # limite municipal (referência única)
├── data/
│   ├── raw/{vetor,raster,tabular}/  # dado bruto (ignorado; .json irmão versionado)
│   ├── processed/                   # produção: GeoPackage, EPSG:31981
│   ├── externos/                    # cópias de camadas de outros projetos
│   ├── geoportal/                   # publicação: GeoJSON 4326 + catalogo.json
│   ├── catalogo_fontes.csv
│   └── catalogo_camadas.csv
├── scripts/
│   ├── download/                    # um script por fonte
│   ├── processamento/
│   ├── geoportal/                   # produção -> publicação + teste headless
│   ├── bibliografia/
│   └── utils/                       # recorte, hashes, validadores
├── bibliografia/                    # bage.bib, indice.md, pdfs/ (ignorado)
├── css/ · js/ · index.html          # geoportal estático
├── docs/ESTADO.md                   # diário do projeto
└── notebooks/                       # exploração, não produção
```

## Como começar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # ou requirements.lock.txt, para o ambiente exato

python scripts/download/vetor_ibge.py --codigo-ibge 4301602
```

Isso baixa a malha municipal do IBGE (navegando as listagens do
`geoftp.ibge.gov.br`), recorta Bagé e gera:

- `config/area_estudo.geojson` (EPSG:31981) — referência única de recorte;
- `data/processed/limite-municipal_ibge_2025_municipal.gpkg` — arquivo de
  produção;
- os `.json` irmãos de ambos, com URL, `Last-Modified`, sha256 e as áreas
  calculada e oficial.

Em seguida, para publicar no portal:

```bash
python scripts/geoportal/exportar_limite_municipal.py   # GeoJSON EPSG:4326
python scripts/geoportal/exportar_catalogo.py           # catalogo.json do portal
python scripts/utils/validar_catalogos.py               # antes de qualquer commit
```

## Como testar o portal

O geoportal usa `fetch()` para carregar as camadas, então precisa ser servido
por HTTP — abrir `index.html` via `file://` não funciona.

```bash
python -m http.server 8000
# abrir http://localhost:8000
```

### Teste automatizado (Playwright headless)

Mesmo esquema do ClimaPampa:

```bash
npm install
npx playwright install chromium     # baixa o browser headless, uma vez
npm run test:geoportal
```

`scripts/geoportal/test_headless.js` sobe um servidor local, abre o portal em
Chromium headless e valida: inicialização do Leaflet, presença dos 7 grupos
temáticos, carregamento da camada do limite municipal a partir do catálogo,
enquadramento caindo sobre Bagé, alternância mapa/satélite, liga/desliga pelo
checkbox, marcação dos grupos ainda vazios, rodapé de fontes/licenças
preenchido, e ausência de erros de console/JS. Gera
`scripts/geoportal/geoportal-headless.png` (não versionado).

### Validação dos catálogos

```bash
python scripts/utils/validar_catalogos.py   # rc=0 se consistente
python scripts/utils/testar_validador.py    # controles positivo + 3 negativos
```

O segundo monta catálogos deliberadamente quebrados (id de fonte inexistente,
chave bibliográfica inexistente, camada publicada com fonte sem licença) e
exige que o validador reprove cada um — um validador que nunca reprova nada
não valida nada.

## Município de referência (default)

- **Bagé, RS** — código IBGE `4301602`
- Área oficial: **4.091,554 km²** (IBGE, Áreas Territoriais 2025)
- Todos os scripts aceitam o código IBGE como argumento; o default é Bagé, mas
  nada está fixo a ponto de impedir reuso em outro município.
