# ACERVO_BAGE

Acervo do município de **Bagé/RS** (código IBGE `4301602`): dados espaciais,
dados não espaciais e bibliografia, com geoportal estático.

## Objetivo

Manter **uma cópia principal** dos dados de Bagé, catalogada, com licença
conhecida e hash conferido — e permitir que vários estudos a consumam sem
duplicá-la e sem alterá-la.

A separação é a ideia central do repositório:

- **acervo** (`data/acervo/`) — a base compartilhada. Cada arquivo tem fonte,
  licença, sha256 e `.json` irmão. É de onde todo mundo lê.
- **estudos** (`estudos/<id>/`) — trabalhos que consomem o acervo. Cada um
  declara em `manifesto.yaml` exatamente quais camadas usa e em que versão e
  sha256. **Um estudo nunca escreve no acervo**; camada derivada só entra lá
  por promoção, depois de conferência visual do responsável.

Assim, meses depois ainda se sabe sobre qual estado do acervo cada resultado
foi produzido — e se o acervo mudou desde então, a conferência acusa em vez de
corrigir em silêncio.

As regras completas estão em **[`docs/convencoes.md`](docs/convencoes.md)**.

## Estrutura

```
config/
  config.yaml                 TODOS os parâmetros (município, CRS, caminhos).
                              Nada disso se repete em código.
  area_estudo.geojson         recorte de referência do acervo

data/
  raw/{vetor,raster,tabular}/ dado bruto, como veio da fonte (ex.: Censo em ibge/censo_<ano>/)
  acervo/                     A CÓPIA PRINCIPAL, por tema:
    limites/ censo/ hidrografia/ viario/
    cadastro/ educacao/ saude/ ambiental/
  externos/                   cópias de outros projetos, versão e sha256 fixados
  geoportal/                  publicação: o que o portal serve (VERSIONADO)
  catalogo_fontes.csv         de onde veio, sob qual licença
  catalogo_camadas.csv        o que existe, em que versão, se pode publicar

scripts/
  download/                   um script por fonte
  processamento/              limpeza, recorte, cruzamento
  acervo/                     entrada e promoção de camadas no acervo
  geoportal/                  acervo -> publicação + teste headless
  bibliografia/               leitura do .bib e geração do índice
  utils/                      config, hashes, nomes, metadados, manifesto,
                              publicação, índice, barreira de publicação

estudos/
  A01_base-cartografica/      cada estudo com:
  A02_portal/                   manifesto.yaml  contrato com o acervo
  A03_expansao_adensamento/                    scripts/        código próprio
                                derivados/      intermediários (fora do git)
                                saidas/         resultados (fora do git)
                                README.md

bibliografia/                 bage.bib (do Zotero), indice.md (gerado)
docs/                         convencoes.md, ESTADO.md, índices gerados
notebooks/                    exploração, não produção
css/ js/ index.html           geoportal estático
.githooks/pre-commit          barreira de publicação
```

## Ambiente

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # ou requirements.lock.txt, para o ambiente exato

# OBRIGATÓRIO depois de clonar — hooks não são clonados pelo Git:
git config core.hooksPath .githooks
```

Sem esse `git config`, o repositório funciona **sem a barreira de publicação**
— e é nesse estado que o commit distraído passa. Conferir com
`git config --get core.hooksPath`.

### Promoção (depois da conferência no mapa)

Um produto só passa a `conferido` pelo comando de promoção, depois que o
responsável o conferiu **no mapa**:

```bash
python scripts/utils/promover.py --id setores_2022 --nota "Conferido no QGIS sobre imagem de satélite em AAAA-MM-DD: ..."
python scripts/utils/promover.py --id config/area_estudo.geojson --nota "..."
```

O comando confere o arquivo em disco contra o `sha256_conteudo` registrado.
Depois grava `status_conferencia=conferido`, `pode_publicar` (nunca mais
permissivo que a fonte) e a nota no bloco `--- conferência ---`, no `.json` e
no catálogo. Ele recusa, sem gravar nada, nestes casos: produto inexistente,
hash divergente, fonte com `autorizacao_fonte=false`. Regras completas em
[`docs/convencoes.md`](docs/convencoes.md) § 1.

### Comandos

```bash
python scripts/utils/indice.py            # docs/indice_camadas_estudos.md
python scripts/utils/validar_catalogos.py # coerência dos catálogos
python scripts/utils/testar_validador.py  # controles do validador
python scripts/utils/verificar_publicacao.py   # barreira, fora do hook
python scripts/utils/promover.py --id <id_camada|caminho> --nota "<conferência>"   # promoção

python scripts/download/vetor_ibge.py     # limite municipal (IBGE, geoftp) — camada limite_municipal
python scripts/download/vetor_ibge.py --local   # idem, sem rede: usa o ZIP já em data/raw/
python scripts/download/baixar_malhas_ibge.py   # malhas brutas: municipal (mais recente e 2022) + setores e distritos 2022
python scripts/processamento/area_estudo.py     # config/area_estudo.geojson a partir de limite_municipal
python scripts/processamento/limites_ibge.py    # setores_2022 e distritos_2022 em data/acervo/limites/
python scripts/download/baixar_censo_ibge.py    # Censo 2000/2010/2022 + CNEFE, direto do IBGE -> data/raw/
python scripts/download/baixar_censo_ibge.py --verificar   # só HEAD: algo mudou na origem?
# scripts/download/censo_revia_bg.py está SUBSTITUÍDO por baixar_censo_ibge.py (não grava mais)
python scripts/geoportal/exportar_limite_municipal.py
python scripts/bibliografia/gerar_indice.py

python -m http.server 8000                # geoportal em http://localhost:8000
npm install && npx playwright install chromium
npm run test:geoportal                    # teste headless do portal
```

## Licença e publicação

Decidido pelo responsável em 2026-09-24. São três regras:

1. **Código: [MIT](LICENSE).** Titular: Alexandro Schafer / UNIPAMPA, 2026.
2. **Documentação e produtos próprios do acervo: [CC BY 4.0](LICENSE-DOCS.md).** Isso
   inclui:
   - os catálogos e os metadados (`.json` irmãos, manifestos, procedência);
   - os textos dos estudos;
   - as figuras produzidas aqui.
3. **Dados: a licença de cada fonte.** Ela está registrada camada a camada em
   `data/catalogo_fontes.csv` e `data/catalogo_camadas.csv`.
   - O acervo não relicencia dado de terceiro.
   - **Nenhuma saída é mais permissiva que a fonte dela.** Uma saída de estudo herda
     a restrição **mais restritiva** entre as entradas do manifesto, camadas e fontes
     brutas. Manifesto sem nenhuma entrada resolve para `false` (ver
     [`docs/convencoes.md`](docs/convencoes.md) § 7).
   - Nada muda no regime das camadas sem autorização de republicação (geobage,
     GeoDataBase, bairros e loteamentos revisados, evolução urbana do IPHAN). Elas
     seguem `pode_publicar=false` e fora do repositório.

**Publicar no GitHub Pages continua condicionado ao `pode_publicar` de cada camada.**
- Só vai para o repositório público, e portanto para o portal, o que tiver
  `pode_publicar=true` no catálogo e tiver passado por conferência visual.
- A barreira de pre-commit recusa o resto.
- A licença do repositório não autoriza publicar nenhuma camada que a fonte não
  autorize.

## Município de referência

- **Bagé, RS** — código IBGE `4301602` (em `config/config.yaml`, não em código)
- Área oficial: **4.091,554 km²** (IBGE, Áreas Territoriais 2025)
- CRS de produção `EPSG:31981` · publicação `EPSG:4326`
