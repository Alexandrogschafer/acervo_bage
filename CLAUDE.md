# CLAUDE.md — regras deste repositório

Lido pelo Claude Code no início de cada sessão. As sete regras abaixo não são
preferências de estilo: cada uma existe porque quebrá-la produz um dano
concreto (republicação indevida, dado irreprodutível, mapa errado publicado).

## O que é este repositório

**acervo_bage** — acervo do município de **Bagé/RS** (código IBGE `4301602`):
dados espaciais, dados não espaciais e bibliografia, com um geoportal estático
(`index.html` + `css/` + `js/`) publicando as camadas liberadas.

Segue o padrão do repositório `uruguaiana-clima-saude` (ClimaPampa), de
Alexandro Schäfer: pipeline Python + geoportal Leaflet estático, parametrização
por código IBGE, metadados `.json` irmãos, catálogo de fontes vivo.

## Padrões técnicos

- **Linguagem:** Python. Bibliotecas: `geopandas`, `pyogrio`, `shapely`,
  `pandas`, `pyproj`, `requests`, `pyyaml`. (`rasterio` só entra quando o
  primeiro script raster existir — e então entra no `requirements.txt`.)
- **CRS padrão de trabalho:** SIRGAS 2000 / UTM 21S — `EPSG:31981`. Dado bruto
  pode vir em qualquer CRS; todo processamento reprojeta para o padrão antes de
  qualquer operação espacial (join, clip, buffer, área).
- **Área de estudo:** sempre lida de `config/area_estudo.geojson`, gerado por
  `scripts/download/vetor_ibge.py`. Nenhum script recria o polígono do
  município — importar de `scripts/utils/recorte_municipio.py`.
- **Parametrização por código IBGE:** o default é `4301602`, mas nada fica
  fixo no código a ponto de impedir rodar em outro município. A UF é deduzida
  dos dois primeiros dígitos do código.
- **Scripts de download:** idempotentes (não rebaixam o que já está em disco,
  a menos de `--forcar`) e registram fonte, URL, `Last-Modified`, tamanho e
  sha256.
- **Origem do dado:** navegar listagens/APIs documentadas. Nunca montar URL de
  download por adivinhação — se a árvore da fonte mudar, o script tem que
  falhar dizendo o que mudou, não baixar outra coisa em silêncio.
- **Nomenclatura de arquivos:** `{tema}_{fonte}_{ano-ou-periodo}_{resolucao}.{ext}`
  — ex.: `limite-municipal_ibge_2025_municipal.gpkg`.
- **Metadados:** todo arquivo de dado tem um `.json` irmão com fonte, URL,
  transformação aplicada, sha256 e data. Os `.json` são versionados mesmo
  quando o dado não é.

## As sete regras

### (i) Repositório público: licença e autorização antes de publicar
Nada vai para `data/geoportal/` sem que a fonte tenha **licença declarada** e
**autorização de republicação** registradas em `data/catalogo_fontes.csv`.
`autorizacao_para_republicar` aceita `sim` / `não` / `a confirmar` — e só `sim`
autoriza publicar. "A confirmar" significa *não publique ainda*.
`scripts/utils/validar_catalogos.py` reprova o commit que violar isso.

### (ii) PDFs nunca são versionados
Os PDFs ficam no Zotero, na biblioteca do pesquisador. `bibliografia/pdfs/`
está inteiro no `.gitignore`. O repositório é público e a maior parte do
material é protegida por direito autoral — o rastro público é o `.bib`
(metadados + DOI/URL), que basta para localizar a obra na origem.

### (iii) Produção é separada de publicação
- **Produção:** GeoPackage em `data/processed/`, no CRS de trabalho
  (`EPSG:31981`), com todos os atributos. Não versionado; rastreado por sha256
  no catálogo e no `.json` irmão.
- **Publicação:** GeoJSON em `data/geoportal/`, em `EPSG:4326` (único CRS que o
  Leaflet consome), com os atributos que o portal realmente usa. **Versionado**
  — o geoportal estático precisa dos arquivos em runtime.

O GeoJSON de publicação é sempre derivado do GeoPackage de produção por um
script de `scripts/geoportal/`. Nunca editar o GeoJSON publicado à mão: a
próxima exportação o sobrescreve.

### (iv) Camada de outro projeto entra por cópia, nunca por leitura direta
Camada vinda de outro repositório (ex.: `rede_viaria_bage`,
`uruguaiana-clima-saude`) é **copiada** para `data/externos/`, com a versão e o
sha256 do original fixados no `.json` irmão e no catálogo de fontes.

Nunca ler o arquivo direto do outro projeto (`../outro_projeto/...`): isso faz
o acervo depender do estado atual de um diretório que ninguém controla e que
não existe para quem clona este repositório. A cópia é o que torna o acervo
reproduzível; o sha256 é o que permite detectar que a origem mudou.

### (v) Toda fonte no catálogo de fontes, toda camada no catálogo de camadas
- Fonte nova → uma linha em `data/catalogo_fontes.csv`.
- Camada publicável nova → uma linha em `data/catalogo_camadas.csv`.
- Rodar `python scripts/utils/validar_catalogos.py` **antes de cada commit**.

Os catálogos não são documentação acessória: são o índice do acervo e a única
coisa que permite saber, de fora, o que existe e sob qual licença.

### (vi) Produto derivado só é congelado depois da conferência no mapa
Um produto geográfico derivado (recorte, buffer, cruzamento, agregação) só
recebe versão e sha256 no `data/catalogo_camadas.csv` **depois** de o
responsável abrir o geoportal e conferir visualmente o resultado.

Erro de CRS, de topologia ou de junção costuma passar por todos os testes
automáticos e aparecer na primeira olhada no mapa. Por isso o validador
confere o sha256 do arquivo publicado contra o registrado: se o arquivo mudou
depois de congelado, o congelamento caducou e a conferência tem que ser
refeita — o validador falha até o catálogo ser atualizado.

### (vii) O `bage.bib` é gerado pelo Zotero, nunca editado à mão
`bibliografia/bage.bib` é a exportação automática da coleção "Bagé" do Zotero
via Better BibTeX (`Keep updated` ligado). Editar o arquivo à mão é perder a
edição no próximo salvamento do Zotero — a correção se faz no item do Zotero.
O mesmo vale para `bibliografia/indice.md`, gerado por
`scripts/bibliografia/gerar_indice.py`. Ver `bibliografia/README.md`.

## Estrutura de pastas

```
config/                    area_estudo.geojson — referência única de recorte
data/raw/{vetor,raster,tabular}   dado bruto, como veio da fonte
data/processed/            produção (GeoPackage), CRS de trabalho
data/externos/             cópias de camadas de outros projetos (regra iv)
data/geoportal/            publicação (GeoJSON 4326) + catalogo.json — VERSIONADO
data/catalogo_fontes.csv   catálogo de fontes
data/catalogo_camadas.csv  catálogo de camadas publicáveis
scripts/download/          um script por fonte
scripts/processamento/     limpeza, recorte, cruzamento
scripts/geoportal/         produção -> publicação + teste headless
scripts/bibliografia/      leitura do .bib e geração do índice
scripts/utils/             funções reutilizáveis e validadores
bibliografia/              bage.bib (do Zotero), indice.md (gerado), pdfs/ (ignorado)
css/ js/ index.html        geoportal estático
docs/                      ESTADO.md — diário do projeto
notebooks/                 exploração, não produção
```

## Comandos úteis

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/download/vetor_ibge.py --codigo-ibge 4301602
python scripts/geoportal/exportar_limite_municipal.py
python scripts/geoportal/exportar_catalogo.py
python scripts/utils/validar_catalogos.py      # antes de todo commit
python scripts/utils/testar_validador.py       # controles do validador
python scripts/bibliografia/gerar_indice.py

python -m http.server 8000                     # geoportal em http://localhost:8000
npm install && npx playwright install chromium
npm run test:geoportal                         # teste headless do portal
```

## O que NÃO fazer

- Não montar URL de download por adivinhação (ver "Origem do dado").
- Não hardcodear o polígono ou o código do município em scripts de
  processamento — importar de `scripts/utils/recorte_municipio.py`.
- Não commitar dado bruto pesado; ele é rastreado por catálogo + sha256.
- Não misturar CRS sem reprojetar explicitamente antes da operação espacial.
- Não editar à mão nada que seja gerado: `bage.bib`, `indice.md`,
  `data/geoportal/*.geojson`, `data/geoportal/catalogo.json`.
