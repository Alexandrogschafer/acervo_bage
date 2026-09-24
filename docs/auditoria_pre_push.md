# Auditoria do histórico antes do primeiro push

- **Data:** 2026-09-24.
- **Alcance:** **todos os commits** (40, todas as refs, tags incluídas) e **todos os
  blobs** do histórico (775 blobs distintos, 418 caminhos que já existiram), além da
  árvore atual (463 arquivos no HEAD da época).
- **Hashes:** os hashes citados são os **atuais**, posteriores à reescrita de C1. A
  correspondência com os anteriores está em `docs/ESTADO.md`.
- **Nada foi reescrito nem apagado** nesta tarefa.

> **Contexto.** O repositório vai ser público, por exigência do GitHub Pages. Tudo o
> que estiver em qualquer commit fica público, e depois do push não há como recolher.
> Por isso a varredura cobre o histórico inteiro, não só a árvore atual.
>
> Este documento também vai ser público. Por isso ele **descreve** os achados sem
> reproduzi-los: o e-mail do autor, os números de matrícula e o caminho da home não são
> repetidos aqui.

## Método

1. **Extração.** Cada blob do histórico foi extraído, com o mapa blob → caminho →
   commits (a partir de `git ls-tree -r` em cada um dos 40 commits). Para cada achado,
   registrei o arquivo, o número de commits e se ele está no HEAD ou só no histórico.
2. **Padrões buscados em todos os blobs**, sem distinguir o tipo de arquivo:
   - CPF e CNPJ;
   - "matrícula";
   - IPTU, valor venal e `valor_m2`;
   - os campos do `cadastro_imobiliario` (inscrição, endereço de entrega, códigos de
     lote e quadra);
   - campos de pessoa (proprietário, contribuinte, titular, morador, CPF, RG,
     telefone, e-mail);
   - os campos de endereço e coordenada do CNEFE;
   - pares de coordenadas de Bagé, em graus e em UTM;
   - logradouro seguido de número;
   - uma lista de **nomes de pessoas lidos nas fontes do acervo**: prefeitos e
     secretários que assinam as leis, a equipe de preenchimento das fichas do SICG,
     os confrontantes citados nas LC 054 e 055/2015 e autores citados;
   - o nome e o e-mail do autor;
   - tokens (GitHub, AWS, Google, Slack, GitLab e chaves `sk-`), chave privada,
     atribuição de senha ou token e URL com credencial;
   - caminhos absolutos: a home do usuário no Linux, a pasta do Windows vista pelo WSL,
     `C:\Users\…` e `~/projetos`.
3. **Estrutura.** Procurei todo caminho sob `data/raw/`, `data/acervo/`,
   `data/externos/` e `estudos/*/{derivados,saidas}/` que não seja `.json`, `.gitkeep`
   ou `manifesto.yaml`. Procurei também toda extensão de dado (`pdf`, `gpkg`, `shp`,
   `zip`, `csv`, `geojson`, `xlsx`, `doc`, imagens e outras) em qualquer lugar.
4. **Conteúdo por unidade.** Procurei todo blob com ID de célula da grade
   (`200ME…N…` / `1KME…N…`) e conferi se ele liga a unidade a dado de fonte não
   redistribuível: nome de bairro ou loteamento do geobage, ou período do IPHAN.
5. **Metadados.** Li o conteúdo dos `.json` de metadado das camadas sensíveis:
   `cadastro_imobiliario`, `LOTES_URBANOS`, `COMPREB`, `LOTEAMENTOS`,
   `PREDIOS_PUBLICOS`, `IMOVEIS_RURAIS_PUBLICOS`, `LOTES_RURAIS`, CNEFE,
   `bairros_loteamentos` e `r05_cnefe`.
6. **Objetos inalcançáveis.** `git fsck --unreachable --no-reflogs` dá 0 objetos, e o
   reflog está vazio. Não sobrou nada da reescrita de 2026-09-24 fora dos commits.

## Achados

Classificação: **BLOQUEIA O PUSH** / **corrigir antes** / **apenas registrar**.

### BLOQUEIA O PUSH

| # | o quê | arquivo | commits | HEAD? |
| --- | --- | --- | --- | --- |
| B1 | **Não há `LICENSE` e não há decisão de licenciamento.** O próprio repositório proíbe publicar nesse estado: o README, em "Licença e publicação", diz "**Não publicar no GitHub Pages** enquanto esta seção estiver como pendente", e o `CLAUDE.md` repete a regra. | `README.md`, `CLAUDE.md` (a falta de `LICENSE`) | todos (nenhum commit tem `LICENSE`) | sim |

- **Não é vazamento de dado.** É uma regra do projeto que o push violaria.
- Sem licença, o código e a documentação ficam públicos sob "todos os direitos
  reservados".
- **Resolve-se sem reescrever o histórico:** basta escolher a licença do código e da
  documentação, acrescentar o `LICENSE` e atualizar o README.

### Corrigir antes (decisão do responsável; depois do push não há volta)

| # | o quê | arquivo | commits | HEAD? |
| --- | --- | --- | --- | --- |
| C1 | **E-mail pessoal do autor nos metadados de todos os commits** (autor e committer, 40 de 40). Não está em arquivo; está no cabeçalho do commit. | metadados de commit | 40 | — |
| C2 | **Três números de matrícula de imóvel** no Registro de Imóveis, com a área e o logradouro confrontante. Estão nas observações das linhas das LC 054/2015 e 055/2015. Não há nome de proprietário. | `data/catalogo_legislacao.csv` | 4 (de `2d36fce` ao HEAD) | sim |

- **C1.** Não é um problema do conteúdo, mas é irreversível depois do push. Se o
  responsável preferir não expor o e-mail pessoal, há dois caminhos:
  - antes do primeiro push: reescrever autor e committer com um `.mailmap` e
    `git filter-repo --mailmap`, trocando o e-mail pelo endereço `noreply` do GitHub;
  - daí em diante: configurar `user.email` com esse `noreply`.
  - Se o e-mail pode ser público, basta registrar.
- **C2.** Os números vêm do **texto das próprias leis**, que é público e cujo PDF
  está com `pode_publicar=true`. Mesmo assim, o critério desta auditoria lista
  "matrícula de imóvel" como dado pessoal, e a análise não precisa dos números.
  - Opção leve: aceitar, porque é texto de lei publicado.
  - Opção estrita: generalizar para "três glebas, pelo Registro de Imóveis" e
    **reescrever o histórico** a partir de `2d36fce`. Só corrigir o HEAD deixaria os
    números nos commits anteriores.

### Apenas registrar

| # | o quê | arquivo(s) | commits | HEAD? |
| --- | --- | --- | --- | --- |
| R1 | **Caminho absoluto da home do usuário** no campo `caminho_absoluto_na_maquina_de_origem` dos registros de procedência da cópia do Censo feita a partir do REVIA_BG. | `docs/procedencia/revia_bg_censo/**` (52 arquivos) | 33 | sim |
| R2 | O mesmo campo nos `.json` antigos do Censo, quando moravam em `data/raw/censo/` e depois em `data/acervo/censo/`. | 104 caminhos que já não existem | 1 a 5 | **não** (só histórico) |
| R3 | `~/projetos/rede_viaria_bage` citado na documentação e em textos de uso. Não é absoluto, mas supõe uma pasta local. | `docs/ESTADO.md`, `docs/ressalvas_censo_bage.md`, `scripts/acervo/importar_evolucao_urbana_revia.py` (docstring), `scripts/download/censo_revia_bg.py` (`ORIGEM_PROJETO`) | vários | sim |
| R4 | **Agregados por nome de polígono** da camada de bairros e loteamentos revisada (fonte sem autorização): 188 linhas de contagem por polígono no i01, e as tabelas por bairro dos `resultados_s1.md` § 13 e `resultados_s2.md` § 7. **Não há unidade individual** (a lista por unidade foi removida do histórico em 2026-09-24) nem geometria. | `estudos/A03_expansao_adensamento/derivados/i01_bairros_loteamentos.json`, `resultados_s1.md`, `resultados_s2.md` | a partir de `4e779c4` | sim |
| R5 | **Agregados por período** da evolução urbana do IPHAN (fonte sem autorização), sem unidade individual e sem geometria. | `derivados/i02_evolucao_urbana.json`, `resultados_s1.md` § 14, `resultados_s2.md` § 8 | a partir de `2a3f803` | sim |
| R6 | **Metadados das camadas não redistribuíveis:** nomes de campo, contagens, áreas e 3 pares de polígonos com nome, na sobreposição da camada de bairros. Não há valor de feição. | `.json` de `data/externos/**` | vários | sim |
| R7 | **IDs de célula da grade com dado do IBGE** (domicílios, moradores, rumo, distância), inclusive células de 1 km com poucos domicílios. A fonte é a grade estatística publicada pelo IBGE, que já aplica o sigilo dela. **Não** há vínculo com bairro, loteamento ou período. | `derivados/s1_desagregacao_2010.json`, `s2_divergencia.json`, `s1_faces_2010.json`, `s2_agrupamentos_divergencia.json`, `resultados_s2.md` | 6 a 9 | sim |
| R8 | **CNEFE, cadastro e LOTES_URBANOS: só nomes de coluna** no código e contagens agregadas (`r05_cnefe.json`: totais por espécie, faixa e setor). **Nenhum** endereço, número ou coordenada individual. Os `.json` do `cadastro_imobiliario` e do `LOTES_URBANOS` registram a remoção, na ingestão, dos campos de proprietário e responsável e dos valores venais. | scripts, `r05_cnefe.json`, `.json` de `data/externos/` | vários | sim |
| R9 | **Endereços de bens tombados** (prédios e clubes), na ementa das leis de patrimônio. São imóveis de interesse público e endereço de lei publicada. | `data/catalogo_legislacao.csv` | 4 | sim |
| R10 | **Coordenadas agregadas:** o centro inicial do mapa e os centroides da malha urbana. Nenhuma é de endereço. | `js/mapa.js`, `estudos/A02_portal/scripts/map-init.js`, `r03_geografia.json`, `s2_divergencia.json` | vários | sim |
| R11 | **Nomes de pessoa:** o crédito profissional da equipe que elaborou o material do IPHAN (escritório de arquitetura), o nome do remetente no rascunho de pedido à Prefeitura e o nome do autor no `CLAUDE.md` antigo. Os nomes lidos nas fontes (prefeitos, equipe do SICG, confrontantes) **não aparecem** em nenhum blob. "Ney Azambuja" aparece só como nome de lugar (Núcleo Ney Azambuja). | `data/catalogo_fontes.csv`, `.json` do IPHAN, `scripts/acervo/*.py`, `docs/pedido_prefeitura_bage.md`, `CLAUDE.md` (histórico) | vários | sim |
| R12 | Mensagens de commit citam hashes anteriores à reescrita de 2026-09-24 (por exemplo, `d312258`). A correspondência está em `docs/ESTADO.md`. | mensagens | 2 | — |
| R13 | A **cópia de segurança** da reescrita, em `~/backups/acervo_bage_2026-09-24_pre-reescrita/` e fora do repositório, **contém a lista removida**. Nunca fazer push a partir dela, nem usá-la como remoto. | fora do repositório | — | — |

### Sem achados

| verificação | resultado |
| --- | --- |
| CPF / CNPJ | 0 em todos os blobs |
| campos de pessoa (proprietário, contribuinte, titular, morador, RG, telefone, e-mail) como chave de dado | 0 |
| campos do `cadastro_imobiliario` como dado (inscrição, endereço de entrega, códigos de lote) | 0 |
| valores de IPTU ou valor venal | 0: só os nomes dos campos removidos, nos metadados e no script de ingestão |
| **arquivo de dado versionado** fora do permitido (item 3) | **0 em todo o histórico**: só `.json`, `.gitkeep` e `manifesto.yaml` nas áreas de dado. Os `.csv` e `.geojson` versionados são os catálogos, `config/area_estudo.geojson` e `data/geoportal/limite_municipal.geojson` (IBGE), todos por decisão registrada |
| PDF, DOC, GPKG, SHP, ZIP e similares em qualquer commit | 0 |
| **lista por unidade de fonte não redistribuível** (item 2) | **0 em todo o histórico**, depois da reescrita de 2026-09-24. O i02 nunca teve lista |
| geometria do geobage, do GeoDataBase, da camada de bairros ou do IPHAN | 0: o único GeoJSON de feição é o limite municipal do IBGE |
| produtos restritos do REVIA_BG (`bairros_v1` e polígonos do IPHAN, segundo o `LICENCAS.md` de lá) | 0. Do REVIA_BG só entraram os registros de procedência do Censo (IBGE, público) e os metadados da cópia da evolução urbana |
| **segredos** (tokens, chave privada, senha, URL com credencial, `.env`, `.pem`, `.key`) | **0** |
| `C:\Users\…` ou a pasta do Windows vista pelo WSL | 0 |
| objetos inalcançáveis ou reflog | 0 / vazio |

## Parecer da primeira passada

**O repositório NÃO deve ir a público como está, por um único motivo: B1.** Falta a
decisão de licença, e o próprio projeto proíbe publicar no GitHub Pages nesse estado.

**Quanto ao conteúdo, o histórico está limpo:**
- nenhum dado pessoal individual;
- nenhuma lista por unidade de fonte sem autorização;
- nenhum arquivo de dado;
- nenhum segredo.

Isso vale para os 40 commits, não só para a árvore atual.

Antes do primeiro push:

1. **Resolver B1:** escolher a licença do código e da documentação (a dos dados
   continua sendo a de cada fonte), acrescentar `LICENSE` e tirar o "PENDENTE" do
   README. Não exige reescrever o histórico.
2. **Decidir C1 e C2**, porque só dá para resolvê-los antes do push:
   - C1: expor ou não o e-mail pessoal nos commits;
   - C2: manter ou não os números de matrícula, que são texto de lei.
   - Se qualquer um deles for corrigido, a reescrita deve ser feita **de uma só vez**,
     com uma nova cópia de segurança antes e esta mesma auditoria repetida depois.
3. **Fazer o push a partir deste repositório**, nunca da cópia de segurança (R13).

Os itens "apenas registrar" (R1 a R12) não impedem a publicação:
- R1 a R3 afetam só a reprodutibilidade;
- R4 a R6 são agregados e metadados, sem unidade nem geometria;
- R7 a R11 são dado público ou referência profissional.

---

## Decisões do responsável (2026-09-24)

| achado | decisão | como foi resolvido |
| --- | --- | --- |
| **B1** — sem licença | **RESOLVIDO.** Código sob **MIT**; documentação e produtos próprios sob **CC BY 4.0**; dados sob a licença de cada fonte, sem saída mais permissiva que a fonte. | `LICENSE` (MIT; Alexandro Schafer / UNIPAMPA, 2026) e `LICENSE-DOCS.md` (CC BY 4.0). O README perdeu o "PENDENTE" e ganhou as três regras. O `CLAUDE.md` e o `docs/convencoes.md` § 7 perderam a regra que proibia publicar. Publicar no Pages segue condicionado ao `pode_publicar` de cada camada. |
| **C1** — e-mail pessoal nos commits | **TROCAR** pelo endereço `noreply` do GitHub. | `git filter-repo --mailmap`, com o `.mailmap` fora do repositório, sobre os 40 commits e as 2 tags anotadas (autor, committer e tagger). `user.email` do repositório configurado com o mesmo `noreply`. |
| **C2** — números de matrícula no catálogo de legislação | **MANTER.** São texto de lei publicada, e a correção não compensa uma reescrita. | Nada foi alterado. O item passa a "apenas registrar". |

A cópia de segurança anterior à reescrita de C1 está em
`~/backups/acervo_bage_2026-09-24_pre-mailmap/`, com um mirror e um tar da pasta.
**Ela contém o e-mail antigo** e, como a cópia anterior, não pode ser publicada nem
usada como remoto.

## Reauditoria depois da reescrita (C1)

Mesmos critérios e mesmos padrões da primeira passada, sobre o histórico reescrito: 40
commits, 775 blobs e 601 pares caminho-commit distintos. Foram varridos também os
metadados de commit e de tag e os arquivos novos desta etapa (`LICENSE`,
`LICENSE-DOCS.md` e as edições de `README.md`, `CLAUDE.md`, `docs/convencoes.md` e
`docs/ESTADO.md`).

| verificação | resultado |
| --- | --- |
| árvores dos 40 commits, antes × depois | **idênticas**, commit a commit |
| sha256 dos 463 arquivos rastreados, antes × depois da reescrita | **idênticos** |
| nome, datas de autoria e de commit, assunto e **mensagem completa** | **idênticos** (`diff` do `git log` e comparação byte a byte das mensagens) |
| conjunto de blobs | **idêntico** ao da primeira passada (775): a reescrita só tocou metadados |
| e-mail antigo em **qualquer objeto** (commits, tags, árvores, blobs) | **0** |
| autor, committer e tagger | os 40 commits e as 2 tags com o endereço `noreply` |
| objetos inalcançáveis / reflog | 0 / vazio |
| CPF, CNPJ, campos de pessoa, campos do cadastro, IPTU ou venal como dado | 0 (iguais à primeira passada) |
| ID de unidade ligado a fonte não redistribuível | 0. Os 5 arquivos com ID de unidade são os do IBGE (R7) |
| arquivo de dado fora do permitido | 0 |
| segredos | 0 |
| caminho absoluto da home | os mesmos de R1 e R2 (52 no HEAD, só em `docs/procedencia/`), nenhum novo |
| matrícula | o mesmo C2, mantido por decisão |
| arquivos novos desta etapa | nenhum dado pessoal, segredo ou caminho absoluto |

**Nada novo apareceu.** Os achados "apenas registrar" (R1 a R13) seguem como estavam.
Soma-se a eles:
- **R14:** a cópia de segurança `pre-mailmap`, que contém o e-mail antigo. Fica fora
  do repositório, como R13.

## Parecer final

**O único achado que bloqueava o push (B1) está resolvido.** C1 foi corrigido, e C2
foi mantido por decisão registrada.

**O repositório pode ir a público como está**, do ponto de vista desta auditoria:
- nenhum dado pessoal individual;
- nenhuma lista por unidade de fonte sem autorização;
- nenhum arquivo de dado;
- nenhum segredo;
- licença declarada.

Isso vale para o histórico inteiro.

- **O push não foi feito.** A publicação continua sendo decisão do responsável.
- Se for publicar, fazer o push **deste** repositório, nunca de uma das duas cópias de
  segurança.
