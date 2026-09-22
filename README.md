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
  raw/{vetor,raster,tabular}/ dado bruto, como veio da fonte
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
  A03_censo/                    scripts/        código próprio
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

### Comandos

```bash
python scripts/utils/indice.py            # docs/indice_camadas_estudos.md
python scripts/utils/validar_catalogos.py # coerência dos catálogos
python scripts/utils/testar_validador.py  # controles do validador
python scripts/utils/verificar_publicacao.py   # barreira, fora do hook

python scripts/download/vetor_ibge.py     # limite municipal (IBGE, geoftp) — camada limite_municipal
python scripts/download/baixar_malhas_ibge.py   # malhas brutas: municipal (mais recente e 2022) + setores e distritos 2022
python scripts/processamento/area_estudo.py     # config/area_estudo.geojson a partir de limite_municipal
python scripts/processamento/limites_ibge.py    # setores_2022 e distritos_2022 em data/acervo/limites/
python scripts/geoportal/exportar_limite_municipal.py
python scripts/bibliografia/gerar_indice.py

python -m http.server 8000                # geoportal em http://localhost:8000
npm install && npx playwright install chromium
npm run test:geoportal                    # teste headless do portal
```

## Licença e publicação

> **PENDENTE.**
>
> O repositório **ainda não tem `LICENSE`** e nenhuma decisão de licenciamento
> foi tomada. Até que seja, vale o seguinte:
>
> - **Código e documentação:** sem licença declarada. Sem licença explícita,
>   o padrão legal é "todos os direitos reservados" — ou seja, terceiros não
>   têm permissão de uso garantida. Definir antes de qualquer divulgação.
> - **Dados:** a licença é sempre a da **fonte**, registrada por linha em
>   `data/catalogo_fontes.csv`. O acervo não relicencia dado de terceiro.
> - **Publicação:** só vai para o repositório público o que tiver
>   `pode_publicar=true` no catálogo e tiver passado por conferência visual.
>   A barreira de pre-commit recusa o resto.
> - **Saídas de estudo:** herdam a restrição **mais restritiva** entre as
>   camadas declaradas no manifesto. Manifesto sem camadas declaradas resolve
>   para `false` — ver [`docs/convencoes.md`](docs/convencoes.md) § 7.
>
> **Não publicar no GitHub Pages** enquanto esta seção estiver como pendente.

## Município de referência

- **Bagé, RS** — código IBGE `4301602` (em `config/config.yaml`, não em código)
- Área oficial: **4.091,554 km²** (IBGE, Áreas Territoriais 2025)
- CRS de produção `EPSG:31981` · publicação `EPSG:4326`
