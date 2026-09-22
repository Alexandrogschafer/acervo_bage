# A03 — Reconhecimento dos dados do Censo (2000, 2010, 2022) e do CNEFE 2022

**Município:** Bagé/RS (`4301602`) · **Data:** 2026-09-22 · **Status do estudo:** planejado

Este documento diz **o que os dados permitem**, não analisa Bagé. Nenhuma camada
foi gerada, nada foi para `data/acervo/` nem para o geoportal, e o `manifesto.yaml`
não foi alterado. Os números abaixo foram medidos sobre o bruto do IBGE em
`data/raw/*/ibge/censo_<ano>/` (sha256 nos `.json` irmãos e em
`config/fontes_censo_ibge.yaml`).

O que já estava medido em [`docs/ressalvas_censo_bage.md`](../../docs/ressalvas_censo_bage.md)
foi consolidado, não refeito. Onde a medição de agora **revisa** uma ressalva, isso
está dito explicitamente (§ 2).

**Reprodução.** Scripts em [`scripts/`](scripts/), na ordem:

| script | faz |
| --- | --- |
| `r00_extrair.py` | extrai o município das tabelas de 2000/2010/2022, converte planilhas (XLS/XLSX/ODS) e documentação para texto |
| `variaveis.json` | mapa conceito × censo → arquivo e variáveis (montado da documentação de cada censo; base do § 1 e do § 4) |
| `r02_totais.py` | § 2 — somas × totais oficiais; busca dos setores de 2010 sem linha |
| `r03_geografia.py` | § 3 — de/para 2010→2022, hipóteses de CRS de 2000, 2000→2010 por sobreposição |
| `r04_sigilo.py` | § 4 — supressão por conceito, censo, urbano/rural |
| `r05_cnefe.py` | § 5 — CNEFE × setores 2022 |
| `r06_temas_2022.py` | § 1.4 — rendimento, entorno e favelas 2022: variáveis, cobertura, sigilo |
| `r07_aglomerados_2010.py` | § 1.4 — aglomerados subnormais 2010 × FCU 2022; cobertura do entorno nas FCU |
| `r08_entorno_universo.py` | § 1.4 — setores com entorno em 2010 e em 2022 e o universo comum, por área mínima comum |

Intermediários e saídas brutas (`r0*.json`, a lista do CNEFE, as tabelas filtradas)
ficam em `derivados/`, fora do git. As planilhas oficiais passaram a ser lidas com
`xlrd`, `openpyxl` e `odfpy` (acrescentados a `requirements.txt`) — o leitor que
faltava para as tabelas de 2000, registradas nas ressalvas como "não lidas".
Toda área foi medida no CRS de área do config (`ESRI:102033`).

---

## 1. Variáveis por censo

### 1.1 O que cada divulgação traz por setor

| censo | tabelas por setor (arquivos) | setores de Bagé | marcador de valor suprimido |
| --- | --- | ---: | --- |
| 2000 | 23 planilhas: Básico, Domicílio, Morador, Pessoa 1–7, Responsável 1–5, Instrução 1–6 + descrição dos setores e compatibilização 2000→2001 | 165 | célula em branco |
| 2010 | 26 tabelas: Básico, Domicílio 01–02, DomicílioRenda, Responsável 01–02, ResponsávelRenda, Pessoa 01–13, PessoaRenda, **Entorno 01–05** | 164 | `X` |
| 2022 | 13 temas: básico, demografia, alfabetização, cor ou raça, parentesco, óbitos, características do domicílio 1–3, e 4 temas de povos e comunidades tradicionais (indígenas, quilombolas) | 199 no básico, **198** nos demais | `X` |

O setor que só está no básico de 2022 é `430160221000001` (Palmas): população 0,
1 domicílio — o mesmo código da sede de Palmas que em 2010 não tem linha nas tabelas
(§ 2). Os códigos de setor mudam de nome de coluna entre arquivos de 2022
(`CD_SETOR`, `CD_setor`, `setor`).

### 1.2 Correspondência

"diferente" = existe com definição diferente (qual diferença, abaixo da tabela).

| conceito | 2000 | 2010 | 2022 |
| --- | --- | --- | --- |
| população total | existe · `Pessoa1 V1330` | existe · `Pessoa13 V001` (= `Domicilio02 V001`) | existe · `basico v0001` |
| população por sexo | existe · `Morador V0292, V0347` | existe · `Domicilio02 V045, V089` | existe · `demografia V01007, V01008` |
| grupos de idade | existe · quinquenais até 80+ (`Pessoa1 V1448–V1464`) e idade simples | existe · só idade simples (`Pessoa13 V022, V035–V134`) | **diferente** · quinquenais até 29, **decenais** de 30 a 69, topo **70+** (`demografia V01031–V01041`) |
| domicílios particulares permanentes | existe · `Domicilio V0003` (= `Basico Var01`) | existe · `Domicilio01 V002` (= `Basico V001`) | existe · DPPO em `caracteristicas_domicilio1 V00001` |
| moradores por domicílio | existe · `Basico Var01, Var12, Var13` | existe · `Basico V001–V003` | **diferente** · a média publicada (`basico v0005`) inclui improvisados; a comparável é `V00005 / V00001` |
| alfabetização | existe · 5+, alfabetizados e não (`Instrucao1`) | existe · 5+, só alfabetizados (`Pessoa01`; denominador em `Pessoa13`) | **diferente** · só **15+** (`alfabetizacao V00900, V00901, …`) |
| rendimento do responsável | existe · 9 classes de SM (SM = R$ 151) + totais em R$ (`Responsavel1 V0602–V0623`) | existe · as mesmas 9 classes (SM = R$ 510) + totais (`ResponsavelRenda V001–V022`) | **diferente** · publicado em 2026-05-08, em diretório próprio (`Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/`), com **6 variáveis**: responsáveis, moradores, rendimento médio, mediano e variâncias; **sem classes** — baixado em 2026-09-22 (§ 1.3) |
| cor ou raça | **não existe** (fora do universo de 2000) | existe · 5 categorias (`Pessoa03 V002–V006`) | existe · as mesmas 5 (`cor_ou_raca V01317–V01321`) |
| abastecimento de água | **diferente** · 3 formas × canalização | **diferente** · 4 formas (cisterna à parte), sem canalização | **diferente** · forma *principal* em 8 categorias + canalização + ligação à rede |
| esgotamento | existe · `Domicilio V0029–V0036` | existe · mesmas categorias (`Domicilio01 V016–V023`) | **diferente** · fossa séptica dividida em ligada / não ligada à rede |
| coleta de lixo | existe · `Domicilio V0048–V0055` | existe · mesmas categorias | **diferente** · sem subtotal "coletado" e sem "rio, lago ou mar" |
| tipo de domicílio | **diferente** · casa / apartamento / cômodo | **diferente** · casa / casa de vila ou condomínio / apartamento (sem cômodo) | **diferente** · 6 espécies de DPPO |

Diferenças que decidem comparação:

- **Universo de domicílio.** 2000 e 2010 contam DPP ocupados (o número é igual ao de
  responsáveis); 2010 imputou moradores a domicílios fechados, 2000 não. 2022 diz
  DPPO explicitamente — mas `basico v0007` é DPPO + improvisados, `v0003` inclui vagos
  e de uso ocasional, `v0002` inclui coletivos. O DPPO puro está em
  `caracteristicas_domicilio1 V00001`.
- **Idade.** O único esquema comum aos três censos é o de 2022 (topo 70+, decenal a
  partir de 30).
- **Alfabetização.** A taxa comparável nos três é a de **15 anos ou mais**.
- **Rendimento.** 2000 × 2010: mesmas classes em salários mínimos (nominais, sem
  deflação). 2022: só média e mediana — não há distribuição por classe. Em 2010,
  `ResponsavelRenda` **não** tem universo DPP (explicação abaixo).

**Universo do rendimento do responsável em 2010 (os +9).** `ResponsavelRenda V020`
("pessoas responsáveis com ou sem rendimento") soma 38.513 contra 38.504 DPP
(`Basico V001`). A documentação de 2010 define a pessoa responsável "pela unidade
domiciliar (**domicílio particular ou unidade de habitação em domicílio coletivo**)", e o
arquivo fala em "pessoas responsáveis", sem "por DPP". Medido setor a setor:

| parcela | responsáveis |
| --- | ---: |
| DPP (`Basico V001`) | 38.504 |
| − DPP dos 2 setores de Piraí com `V020` suprimido (`X`): `430160222000001` (1) e `430160222000003` (18) | −19 |
| + domicílios particulares improvisados (`DomicilioRenda V001`), um responsável cada | +18 |
| + unidades de habitação em domicílios coletivos, em 5 setores sem improvisado (`…002`, `…010`, `…033`, `…049`, `…076`) | +10 |
| **= `V020`** | **38.513** |

Conferências: `V020` é idêntico, setor a setor, a `Responsavel02 V001` ("Pessoas
Responsáveis", 38.532 = 38.513 + os 19 suprimidos em `ResponsavelRenda`); a tabela
oficial 4.23.1.3 dá 38.522 responsáveis em domicílios particulares = 38.504 DPP + 18
improvisados. Consequência: para rendimento **por DPP**, usar `Basico V005–V008`
(explicitamente DPP); as classes de `ResponsavelRenda` cobrem DPP + improvisados +
unidades em coletivos (diferença de 0,07 % em Bagé).
- **Água.** Só "rede geral" é comparável nos três; canalização só entre 2000 e 2022.
- **Esgoto.** Para 2010 × 2022, somar as duas fossas sépticas de 2022; "rede geral +
  fossa ligada" de 2022 **não** equivale à "rede geral" de 2010.
- **Tipo.** Recortes comuns: apartamento; casa (em 2010/2022, somar casa + casa de vila).

Detalhe variável a variável: `scripts/variaveis.json`.

### 1.3 Censo 2022: o que o IBGE já divulgou por setor, e o que não

Levantado nas listagens de `ftp.ibge.gov.br` e `geoftp.ibge.gov.br` em 2026-09-22,
sem baixar dados:

- **Divulgados e presentes na cópia local:** os 13 temas da tabela 1.1, nas mesmas
  versões (básico `20260520`; características do domicílio 2 e 3 `20250417`).
- **Divulgados e baixados em 2026-09-22** (depois do reconhecimento; não processados):
  - **rendimento do responsável** por setor (2026-05-08; ver tabela 1.2):
    `data/raw/tabular/ibge/censo_2022/Agregados_por_setores_renda_responsavel_BR_20260508_csv.zip`
    (9.370.011 B) e o dicionário em `…/censo_2022/doc/` (10.197 B); fonte
    `ibge_censo2022_renda_responsavel_setores`;
  - **entorno urbanístico** por setor (2025-04-17): domicílios, faces e moradores
    (`Agregados_por_setores_entorno_{domicílios,faces,moradores}_BR.zip`, 35,2 MB) e
    `doc/dicionarios_de_dados_entorno.zip`; fonte `ibge_censo2022_entorno_setores`;
  - **favelas e comunidades urbanas** por setor (2025-04-17):
    `FavelaseComunidadesUrbanas2022Setores_20250417.xlsx` e a apresentação da divulgação
    em `doc/` (não há dicionário próprio); fonte `ibge_censo2022_favelas_setores`.
- **Divulgados e deixados de fora por decisão:** **registro de nascimento** por setor
  (2026-02-04); a versão percentual do entorno com geometria
  (`br_setores_entorno_cd2022.gpkg`, 363 MB, nacional); os polígonos das favelas
  (`arquivos_vetoriais/`).
- **Não existem por setor** (constatação de ausência): educação além de alfabetização,
  trabalho, migração, deslocamento, fecundidade, deficiência.
- **O que ainda falta publicar: o servidor não diz.** Não há leia-me, nota ou
  diretório anunciando temas futuros; nenhuma lista de pendências foi assumida.

### 1.4 Temas de 2022 baixados depois: rendimento, entorno, favelas

Medido em 2026-09-22 por `scripts/r06_temas_2022.py` (intermediários em `derivados/`).

| tema | variáveis (dicionário) | setores de Bagé com linha (de 199) | supressão |
| --- | --- | ---: | --- |
| rendimento do responsável | 6 | 198 | 4 setores (2 u / 2 r), todas as 6 variáveis; 2,0 % das células |
| entorno — domicílios | 35 | 168 (167 de 173 urbanos; 1 de 26 rurais) | nenhuma |
| entorno — moradores | 35 | 168 (idem) | nenhuma |
| entorno — faces de quadra | 35 | 171 (169 urbanos; 2 rurais) | nenhuma |
| favelas e comunidades urbanas | planilha setor → FCU | 7 setores citados | não se aplica |

O setor sem linha no rendimento é `430160221000001` (população 0).

**Rendimento do responsável 2022.** Por setor: pessoas responsáveis em DPPO (`V06001`),
moradores em DPPO (`V06002`) e variância (`V06003`), rendimento nominal **médio**
(`V06004`), variância (`V06005`) e **mediano** (`V06006`) mensal dos responsáveis **com
rendimento**. Universo exatamente DPPO: a soma de `V06001` é 45.295 = DPPO
(`caracteristicas_domicilio1 V00001`) — diferente do universo de 2010 (§ 1.2).
Comparável com 2010: a média só dos que têm rendimento, `Basico V007` de 2010 (DPP) ×
`V06004` (DPPO), em valores nominais (deflacionar). **Não** comparável: as classes de
salário mínimo de 2000/2010 (2022 não tem distribuição) e a mediana (2010 não publica
mediana por setor).

**Entorno urbanístico 2022.** Levantado nos setores "escolhidos para aplicação do
entorno": em Bagé, 43.742 dos 44.018 DPPO urbanos (99,4 %) e 2 dos 1.277 rurais — é um
tema **urbano**. Sem linha, entre os urbanos: `…205000047` (tipo 6, sem DPPO),
`…205000079` (tipo 7), `…205000197`, `…220000011` (sede de José Otávio), `…221000001`
(população 0) e **`…205000195` — a favela Passo das Pedras**. O mesmo conjunto de itens
vem em três unidades — domicílios (DPPO), moradores e **faces de quadra** (7.573 faces) —,
cada item em sim / não / não declarado:

- circulação da via (caminhão/ônibus; carros; só pedestres, bicicletas e motos; aquavia);
- via pavimentada; bueiro; iluminação pública; ponto de ônibus;
- via sinalizada para bicicleta; calçada; obstáculo na calçada; rampa para cadeirante;
- arborização (sem árvores; 1–2; 3–4; 5 ou mais).

**Há entorno em 2010?** Sim, em `Entorno01`–`Entorno05`: DPP e moradores por existência
de identificação do logradouro, iluminação pública, pavimentação, calçada, meio-fio/guia,
bueiro/boca de lobo, rampa para cadeirante, arborização, esgoto a céu aberto e lixo
acumulado, cruzados com a condição de ocupação. Em Bagé, respondido para 32.482 dos 32.641
DPP urbanos (99,5 %) e 3.220 dos 5.844 rurais — 35.702 DPP com resposta, em 139 setores
que somam 36.068 DPP: os 366 restantes não entram porque as tabelas do entorno só cruzam
três condições de ocupação (próprio, alugado, cedido).

#### Comparabilidade 2010 × 2022: a classificação do próprio IBGE

**Fontes.** 2022: *Censo Demográfico 2022: Características urbanísticas do entorno dos
domicílios* (IBGE, 2025), `data/raw/tabular/ibge/censo_2022/doc/liv102168.pdf`, obtido
manualmente pelo responsável (a biblioteca do IBGE bloqueia acesso automatizado; item
manual da lista fixa, fonte `ibge_censo2022_entorno_publicacao`). Seção "Comparabilidade
com a pesquisa urbanística do entorno de 2010" e **Tabela 2**, **pp. 50–52** (numeração
impressa = página do PDF). 2010: *Metodologia do Censo Demográfico 2010* (IBGE, Relatórios
Metodológicos v. 41), `censo_2010/doc/metodologia_censo_dem_2010.pdf`, seção 7.2.3
(**pp. 305–307**) e 10.5 (**pp. 432–433**). A classificação abaixo é a **do IBGE**. Ela
substitui a tabela anterior deste parágrafo, que marcava os seis itens comuns como
"não decidíveis" por falta da metodologia de 2022.

| item | classe do IBGE (Tabela 2, p. 51; notas, p. 52) | por quê (p. 50–51) | viés esperado em 2010 → 2022 |
| --- | --- | --- | --- |
| iluminação pública | **A1 — comparação direta** | mesmo conceito e mesmo método; nos dois censos conta a face e a confrontante (2010: p. 306; 2022: p. 14) | nenhum de método |
| bueiro / boca de lobo | **A1 — comparação direta** | idem | nenhum de método |
| rampa para cadeirante | **A2 — comparável com restrição** | em 2010 o quesito valia para todas as faces; em 2022, só para faces com calçada assinalada. Restrição do IBGE: "considerar apenas as faces de 2010 que continham rampas para cadeirantes e calçada simultaneamente" (p. 52) | sem a restrição, 2010 e 2022 têm denominadores diferentes |
| calçada / passeio | **B — não comparável** | conceito ampliado: 2010 contava "caminho calçado ou pavimentado" para pedestres; 2022 conta calçada/passeio **com ou sem pavimentação** (p. 50) | **tende a subir** por efeito de método, não por mais calçada |
| pavimentação | **B — não comparável** | critério mudou: 2010 contava qualquer pavimentação, "mesmo que em uma pequena parte da via"; 2022, só pavimentação em **mais de 50 %** do trecho percorrido (p. 50) | **tende a cair** por efeito de método, não por menos pavimento |
| arborização | **B — não comparável** | área de observação menor: 2010 contava face, confrontante e canteiro central; 2022, só face e canteiro central (pp. 50–51; 2022: p. 14); 2022 publica ainda 4 classes de quantidade | **tende a cair** por efeito de método (o IBGE fala em "comparação […] impossibilitada", p. 51) |
| identificação do logradouro, meio-fio/guia, esgoto a céu aberto, lixo acumulado | **C2 — só em 2010** | não pesquisados em 2022 | — |
| ponto de ônibus/van, via sinalizada para bicicleta, obstáculo na calçada, capacidade da via | **C1 — só em 2022** | quesitos novos | — |

Para o grupo B, a nota da p. 52 admite só uma checagem indireta: comparar a
discrepância com a dos itens A e, se for "significativamente maior", tomá-la como efeito
da nova metodologia. Isso não reconstrói a série. O IBGE conclui: "o usuário só
encontrará uma comparabilidade direta para os itens Iluminação Pública e Bueiro/Boca de
lobo" (p. 51).

**A restrição da rampa (A2) não é aplicável com os agregados por setor.** O IBGE manda
comparar só as faces de 2010 que tinham rampa **e** calçada ao mesmo tempo (p. 52). As
tabelas `Entorno01`–`Entorno05` de 2010 cruzam cada item com a condição de ocupação, a
água, o esgoto e o lixo — **nunca rampa × calçada**. O cruzamento exigiria dado por face,
que não existe na divulgação por setor de 2010 e não está no acervo. Portanto, com o dado
que temos, **rampa fica sem série na prática**: entra na série só se aparecer o dado de
2010 por face. Isso não contradiz o IBGE — ele classifica a rampa como comparável com
restrição, e é a restrição que não se implementa aqui.

**A lista da p. 49 é de crítica interna, não de comparabilidade para análise.** Ao
descrever a crítica da base, o IBGE diz ter comparado com 2010 "os quesitos que eram
comparáveis entre as pesquisas, a saber, iluminação, bueiro, calçada e capacidade da
via". É a descrição de um **procedimento interno de detecção de erro de coleta** — usado
para achar valores suspeitos, não para sustentar análise —, e por isso inclui capacidade
da via, que não existia em 2010, e calçada, classificada como não comparável na p. 50.
Para uso analítico vale a seção de comparabilidade e a Tabela 2 (**pp. 50–52**), não essa
frase.

**Universo de 2022: por que 168 setores (documentado).** O universo foi de setores
urbanos da Base Territorial, mais setores com áreas urbanizadas mapeadas e setores com
concentração de estruturas, domicílios e sistema viário, "independentemente de serem
classificados como urbanos ou rurais". Nos setores rurais incluídos, o entorno cobriu só
a parte com faces de quadra definidas (p. 13). Depois, "com a revisão da Base Territorial
para divulgação foram retirados da base de divulgação […] setores censitários que não
faziam parte do escopo da pesquisa, ou seja, aqueles que não possuíam morfologia urbana"
(p. 50). Isso explica o recorte medido em Bagé: **168 setores com entorno** (167 de 173
urbanos; 1 de 26 rurais). O critério geral agora está documentado. O documento **não
lista setor por setor**, então não diz por que cada um dos 6 setores urbanos de Bagé sem
linha foi retirado (tipos especiais 6 e 7, a sede de Palmas com população 0, a sede de
José Otávio, `…205000197` e a favela Passo das Pedras, que a planilha do IBGE de
cobertura nas FCU registra com 0 %).

**Ressalva: o universo de 2022 é maior que o de 2010.** O IBGE avisa que os universos não
são os mesmos. As cidades se expandiram, e 2022 coletou mais em áreas urbanizadas de
setores rurais e em favelas e comunidades urbanas. Por isso "a quantidade de setores
censitários e faces coletadas, geralmente, foi maior" (p. 52). A Tabela 3 (p. 53) dá
223.666 → 340.965 setores no Brasil e **15.932 → 18.653 no RS**.

**Quantos setores de Bagé têm entorno, e qual é o universo da série** (medido por
`scripts/r08_entorno_universo.py`):

| ano | critério | setores com entorno |
| --- | --- | --- |
| 2010 | alguma variável de `Entorno01`–`Entorno05` diferente de zero, excluídos os dois totais do setor (`V001` do Entorno01, DPP; `V422` do Entorno03, moradores) — é o critério do próprio IBGE: "os setores onde não houve coleta […] apresentam valor zero para todas as informações" | **139** de 164 (126 de 129 urbanos; 13 de 35 rurais, todos de situação 4, "aglomerado rural de extensão urbana"), com 36.068 DPP |
| 2022 | setor com linha na tabela do entorno por domicílios | **168** de 199 (167 de 173 urbanos; 1 de 26 rurais), com 43.744 DPPO |

Os dois totais precisam ficar fora do critério de 2010: com eles, 21 setores rurais de
situação 8 entrariam como "com entorno" tendo só o total de moradores preenchido.

**O universo de qualquer série é o comum aos dois anos.** Como o geocódigo não é estável
entre censos (§ 3.1), a interseção é por **área mínima comum** — os componentes conexos
do de/para oficial. Das 165 AMCs de Bagé:

| classe | AMCs | setores de 2010 | setores de 2022 |
| --- | ---: | ---: | ---: |
| **entorno nos dois anos — universo da série** | **139** | 139 (todos com entorno) | 155 (todos com entorno) |
| só 2022 (área sem entorno em 2010) | 5 | 5 | 21, dos quais 13 com entorno |
| sem entorno em nenhum dos dois anos | 21 | 24 | 23 |

Nenhuma AMC tem entorno só em 2010. Ou seja: **139 AMCs sustentam a série** de
iluminação e bueiro, e **13 setores de 2022 com entorno ficam fora dela** — área que em
2010 não tinha coleta, coerente com o universo maior de 2022. Os universos também diferem
por conceito (DPP com imputação dos fechados em 2010; DPPO em 2022, com "não declarado"),
então a série deve comparar **proporções** dentro das 139 AMCs, nunca contagens por
setor.

**Favelas e comunidades urbanas (FCU) 2022.** **Bagé tem FCU registradas: 6
comunidades, em 7 setores** — exatamente os 7 setores de tipo 1 (`CD_TIPO = 1`) da malha,
todos urbanos, no distrito-sede.

| FCU (código) | setores | moradores | domicílios particulares ocupados |
| --- | ---: | ---: | ---: |
| Passo das Pedras (`43016020001`) | 1 | 149 | 52 |
| Stand (`43016020002`) | 2 | 190 | 67 |
| Vila Miséria (`43016020003`) | 1 | 301 | 104 |
| Balança Municipal (`43016020004`) | 1 | 74 | 22 |
| Beco do Juruna (`43016020005`) | 1 | 289 | 97 |
| Beco dos Coqueiros (`43016020007`) | 1 | 129 | 42 |
| **total** | **7** | **1.132** | **384** |

Nomes e códigos como na planilha oficial `FavelaseComunidadesUrbanas2022Setores_20250417`;
moradores = `basico v0001`, domicílios = `basico v0007`, somados pelos setores (a FCU é
composta por setores inteiros). Não há o código `…0006` em Bagé. Das 7, só Passo das
Pedras fica sem dado de entorno (0 % de cobertura na planilha do IBGE
`FCU_Entorno_Cobertura_das_FCUs_moradores_em_DPPO.xlsx`; as outras 5 FCU, 100 %).

**Aglomerados subnormais 2010 — Bagé não tinha nenhum.** Medido por
`scripts/r07_aglomerados_2010.py`:

- a tabela oficial de setores de aglomerado subnormal de 2010 (`AGSN2010Setores.xls`,
  15.868 setores no país) **não tem nenhum setor de Bagé**;
- conferência independente na tabela municipal das *Informações territoriais* (tab01):
  o RS tinha **448 aglomerados em 23 municípios** (Porto Alegre, Pelotas, Rio Grande,
  Caxias do Sul, …) — Bagé **não** está entre eles;
- portanto **zero aglomerados, zero setores, zero moradores** em 2010.

**Correspondência dos 7 setores de FCU de 2022 com 2010**, pelo de/para oficial:

| setor 2022 (FCU) | setor de 2010 de origem | formação na divulgação 2022 | era aglomerado em 2010? |
| --- | --- | --- | --- |
| `…184` Balança Municipal | `…125` | 241 (divisão) | não |
| `…186` Beco dos Coqueiros | `…051` | 241 | não |
| `…188` Vila Miséria | `…049` | 241 | não |
| `…190` Stand | `…045` | 241 | não |
| `…192` Stand | `…114` | 241 | não |
| `…195` Passo das Pedras | `…138` (via intermediário `…163`) | 242 (divisão, situação alterada) | não |
| `…199` Beco do Juruna | `…087` | 241 | não |

Cada favela de 2022 foi **isolada como setor próprio na última etapa**, por divisão de um
setor maior (segundo dígito 4 = "subdivisão por critério de limite de estrutura
territorial"); os códigos anteriores à divisão são os mesmos que o CNEFE ainda usa (§ 5).
**Nenhuma tem antecedente em aglomerado de 2010.**

**Mudança de conceito.** 2010: aglomerado subnormal = conjunto de **no mínimo 51 unidades
habitacionais** carentes de serviços públicos essenciais, em terreno de propriedade
alheia (atual ou recente) e com urbanização fora dos padrões ou precariedade de serviços
(*Aglomerados subnormais — informações territoriais*, notas técnicas, **p. 8**, em
`censo_2010/doc/notas_tecnicas.pdf`). 2022: FCU = territórios populares
autoproduzidos, com **predominância de insegurança jurídica da posse** e ao menos um de:
serviços públicos ausentes ou precários; edificações/arruamento autoproduzidos fora dos
parâmetros oficiais; localização em área com restrição legal ou de risco (apresentação
da divulgação, **pp. 10–11**, em `censo_2022/doc/`); o critério de 51 unidades não
aparece nesses slides.

**Nota Metodológica de 2024: pendência encerrada, não se aplica a Bagé.** A *Nota
Metodológica sobre a mudança de Aglomerados Subnormais para Favelas e Comunidades Urbanas*
(IBGE, 2024), citada na apresentação (p. 12), serve para ligar aglomerados de 2010 a
favelas de 2022. Bagé não tinha nenhum aglomerado subnormal em 2010, e nenhum dos 7
setores de FCU de 2022 descende de setor de aglomerado. Não há o que ligar, e a série
"favela" de Bagé começa em 2022, lida só pelo conceito de 2022. A nota não foi e não
precisa ser obtida para este estudo (decisão registrada em 2026-09-22). Fica fora do
alcance, e não como pendência, **por que** Bagé tinha zero em 2010 (limite de 51
unidades, critério de 2010 ou território). O zero de 2010 continua **não** podendo ser
lido como "não havia favela" (§ 6).

---

## 2. Totais: soma dos setores × total oficial

Cada soma foi confrontada com o total oficial **da mesma grandeza**.

| censo | grandeza | soma dos setores (urbana / rural) | total oficial (urbana / rural) | diferença |
| --- | --- | --- | --- | ---: |
| 2022 | população | 117.938 (114.883 / 3.055) | 117.938 (114.883 / 3.055) | **0** |
| 2010 | população (`Domicilio02 V001`) | 116.794 (97.765 / 19.029) | 116.794 (97.765 / 19.029) | **0** |
| 2010 | DPP (`Basico V001`) | 38.504 (32.642 / 5.862) | 38.504 (32.642 / 5.862) | **0** |
| 2010 | moradores em DPP (`Basico V002`) | 116.318 (97.304 / 19.014) | 116.318 (97.304 / 19.014) | **0** |
| 2000 | população (`Pessoa1 V1330`) | 118.767 (97.290 / 21.477) | 118.767 (97.290 / 21.477) | **0** |
| 2000 | DPP (`Basico Var01`) | 35.119 | 35.119 | **0** |

Fontes oficiais: 2022 `Populacao_residente_por_situacao_do_domicilio_municipios.xlsx`;
2010 tabelas 4.23.1.1 e 4.23.5.1 (`rio_grande_do_sul.zip`); 2000 tabelas 3.1.2.23 e
3.3.1.23 (`PopMun_43_31/33.zip`). Em 2010 a igualdade vale também **distrito a
distrito** (Bagé, Joca Tavares, José Otávio, Palmas, Piraí), nas três grandezas.

**Domicílios em 2022:** o total oficial de domicílios por município não está na cópia
local; não há contra o que comparar. Somas: DPO (`v0007`) 45.327 (44.043 / 1.284);
DPPO (`V00001`) 45.295, com 4 setores suprimidos; total de domicílios (`v0002`) 53.716.
A conferência independente que existe é a das ressalvas (§ 6: espécies 1 e 2 do CNEFE
= `v0003` e `v0004`).

### Revisão das ressalvas (§ 1 a § 3)

As ressalvas registram a soma de 2010 como −476 e "não serve como total municipal". A
diferença vinha de comparar **moradores em DPP** (`V002`, 116.318) com a **população
total** (116.794) — a mesma confusão de grandezas que as ressalvas já tinham
identificado em 2000. Comparando grandezas iguais, **a soma dos setores fecha
exatamente nos três censos.** Proposta (não aplicada aqui): atualizar
`docs/ressalvas_censo_bage.md` § 1–§ 3.

### 2000: o território não é o de hoje

A própria divulgação de 2000 traz `Compatibilização_2000-2001_RS.xls`: **11 setores**
de Bagé (distritos `…10` e `…12`) passaram para **Aceguá**, instalado em 2001 —
**3.927 pessoas** e 1.147 DPP. Bagé de 2000 **no território de 2001 = 114.840**
habitantes, o mesmo número da planilha oficial "Municípios instalados em 2001". Na
geometria, 1.545 km² desses setores estão hoje em Aceguá. Qualquer comparação 2000 ×
2010/2022 do município inteiro tem de descontar esses setores.

### A lacuna de 2010: os 4 setores sem linha

A malha tem 168 setores; as tabelas, 164. Os 4 ausentes:

| setor | tipo | distrito | descrição oficial do perímetro |
| --- | --- | --- | --- |
| `430160205000142` | rural | Bagé | entre a Estrada dos Vieiras, o rio Negro e a BR-153 |
| `430160217000001` | urbano | Joca Tavares | quadrado de ~100 m em torno da escola rural Alfredo da Silva |
| `430160220000001` | urbano | José Otávio | quadrado de ~100 m em torno da subprefeitura |
| `430160221000001` | urbano | Palmas | quadrado de ~100 m em torno da escola Ivo Miranda Colares |

Onde foram procurados: **todos** os membros do pacote de agregados de 2010 (os 26 CSV
e as 26 planilhas XLS), a documentação (PDF e `Descrição_RS.xls`), as 21 tabelas por
município/distrito (ODS) e o de/para 2010→2022. **Aparecem só em dois lugares:** a
descrição dos setores (`Descrição_RS.xls`, que dá os perímetros acima) e o de/para
2010→2022. **Em nenhum arquivo de dados.**

Como os totais fecham exatamente sem eles — no município e em cada distrito —, os 4
contribuíram **zero pessoas e zero DPP**. Os três urbanos são as sedes formais das vilas
distritais, desenhadas como pequenos quadrados. A razão da omissão não está escrita em
nenhum arquivo da divulgação; "setor sem domicílio não tem linha" é **inferência**,
coerente com os totais, não afirmação do IBGE.

---

## 3. Geografia entre censos

### 3.1 2010 → 2022, pelo de/para oficial

`Historico_formacao_Setores_Censitarios_2010_2022.xlsx`: 202 linhas para Bagé, cadeia
completa de código de formação (FRM) de cada setor de 2022 até 2010. Cobre os 168
setores de 2010 e os 199 de 2022; nenhum código de fora do município.

| classe | componentes | setores 2010 | setores 2022 |
| --- | ---: | ---: | ---: |
| 1:1 | 141 | 141 | 141 |
| divisão (1 → n) | 21 | 21 | 55 |
| fusão (n → 1) | 3 | 6 | 3 |
| redesenho (n → m) | 0 | 0 | 0 |

Dos 141 pares 1:1:

- **99 com série limpa** — toda a cadeia é `111` (manutenção plena, mesmo município,
  distrito e situação);
- 39 com ajuste vetorial (segundo dígito `6`);
- 3 com mudança de situação ou distrito.

**Série limpa: 99 dos 199 setores de 2022 (49,7 %).** Como não há redesenho, **todos**
os setores são comparáveis em alguma área mínima comum: **165 AMCs 2010–2022**
(141 pares + 21 setores de 2010 divididos + 3 setores de 2022 fundidos).

**A sobreposição geométrica não substitui o de/para.** Mesmo nos 99 limpos, a malha de
2010 publicada e a de 2022 diferem no traçado: IoU mediano 0,85, mínimo 0,16. Nos
urbanos, os centróides ficam a ~25 m, sem deslocamento sistemático. Cinco pequenos
aglomerados rurais (0,06–0,14 km²) têm o mesmo código e o de/para os liga 1:1, mas o
traçado de 2010 está deslocado 220–330 m (IoU < 0,1); suas cadeias registram ajuste
vetorial e mudança de situação.

### 3.2 A malha urbana de 2000: hipóteses de CRS

O `.prj` declara EPSG:32621 (UTM 21 **Norte**). Mesmas coordenadas, lidas em quatro
CRS, comparadas com a malha de 2010 e com a envoltória urbana que a própria malha rural
de 2000 traz:

| hipótese | centróide | dentro da malha 2010 | dentro da envoltória rural 2000 | IoU mediano (melhor par em 2010) | deslocamento médio até 2010 (dx, dy) |
| --- | --- | ---: | ---: | ---: | --- |
| EPSG:32621 (declarado) | 52,2° O, **58,8° N** | 0 % | 0 % | 0 | — |
| EPSG:32721 (WGS 84 / UTM 21S) | 54,106° O, 31,327° S | 100 % | 91,7 % | 0,487 | −95 m, +44 m |
| EPSG:29191 (SAD69 / UTM 21S) | 54,107° O, 31,328° S | 100 % | 93,0 % | 0,504 | −41 m, +83 m |
| EPSG:31981 (SIRGAS 2000 / UTM 21S) | idem 32721 | 100 % | 91,7 % | 0,487 | −95 m, +44 m |

O declarado põe Bagé no hemisfério norte; qualquer leitura de UTM 21 **Sul** a põe
inteira sobre a cidade. Entre as leituras sul, SAD69 sobrepõe um pouco mais, mas nenhuma
elimina um deslocamento residual de ~90–105 m, e o IoU por setor fica em ~0,5 —
diferença de traçado, de base cartográfica ou de desenho, que esta medição não separa.

**Decisão do responsável (2026-09-22): SAD69 / UTM 21S (`EPSG:29191`).** Registrada no
`.json` irmão de `4301602.zip` e em `docs/ressalvas_censo_bage.md` § 3, com o resíduo
de ~90–105 m como limitação conhecida e a **regra de uso: dados de 2000 só por município
e distrito, nunca por setor**. Nada foi reprojetado nem gravado como camada.

A malha **rural** de 2000 vem sem `.prj`, em graus. **Decisão do responsável
(2026-09-22): SAD69 geográfico (`EPSG:4618`)** — a mesma leitura usada nas medições
acima (que eram feitas com ela como suposição de trabalho), registrada no `.json`
irmão de `rs_setores_censitarios.zip` e nas ressalvas § 3, com a mesma regra de uso.

### 3.3 2000 → 2010, por sobreposição de áreas

Não há de/para oficial. A relação foi feita por geometria: há vínculo entre dois setores
se a interseção cobre ≥ L da área de um deles. O método foi **calibrado no par
2010→2022**, onde o de/para é o gabarito: de 12 combinações (L de 5 % a 50 %, erosão de
borda de 0 a 40 m), a melhor — **L = 50 %, sem erosão** — reproduz a classe oficial de
**84,9 %** dos setores. Esse é o erro esperado do método em 2000→2010. Limiares baixos
(5–10 %) ligam tudo por sobras de borda e concordam só 22–39 %.

Resultado (malha urbana de 2000 lida como SAD69 / UTM 21S; rural como SAD69 geográfico):

| classe | setores 2000 | setores 2010 |
| --- | ---: | ---: |
| 1:1 | 118 | 118 |
| divisão | 12 | 24 |
| fusão | 2 | 1 |
| redesenho | 11 | 10 |
| sem par majoritário | 22 (11 = Aceguá) | 15 |

Os 1:1 daqui **não são série limpa**: a correspondência é majoritária, não de
identidade, e o IoU dos melhores pares urbanos fica em ~0,5. Para 2000 × 2010 por
setor, o dado sustenta no máximo agregação em áreas maiores que o setor.

### 3.4 Grade estatística do IBGE

Existe para **2010 e 2022**, em
`geoftp.ibge.gov.br/recortes_para_fins_estatisticos/grade_estatistica/`:

- células de **200 m** no urbano e **1 km** no rural, em shapefile, Albers equivalente
  (SIRGAS 2000);
- recortada em **56 quadrantes** (`grade_idNN.zip`), iguais nas duas edições, sem
  recorte por UF;
- variáveis: população total e domicílios ocupados (notas de 2022); 2022 tem também
  grades agregadas nacionais de 1 a 500 km;
- a documentação de 2010 não lista os campos da grade daquele ano.

Arquivos que cobrem Bagé — **baixados em 2026-09-22** (não processados), em
`data/raw/vetor/ibge/censo_<ano>/grade_estatistica/`, fontes
`ibge_grade_estatistica_2010` e `ibge_grade_estatistica_2022`:

| arquivo | bytes | Last-Modified | feições |
| --- | ---: | --- | ---: |
| `censo_2022/grade_estatistica/grade_id14.zip` | 26.890.770 | 2025-06-12 | 582.324 |
| `censo_2022/grade_estatistica/grade_id04.zip` | 3.031.479 | 2025-06-12 | 68.071 |
| `censo_2010/grade_id14.zip` | 32.648.454 | 2016-10-06 | 537.732 |
| `censo_2010/grade_id04.zip` | 3.830.448 | 2016-10-06 | 66.031 |

Total: 66.401.151 B. `ID_14` cobre ~94,5 % do município (a cidade e 198 dos 199
setores); `ID_04`, uma faixa rural no extremo sul (~224 km²). A atribuição foi
**inferida** (blocos de 500 km na Albers do IBGE, conferida em 7 pontos do mapa oficial)
e **conferida antes do download** contra `config/area_estudo.geojson`: só ID_14
(3.867 km²) e ID_04 (224 km²) tocam o município. **Depois do download**, só pelos
metadados: os quatro arquivos têm o campo `QUADRANTE` e a extensão do ID_14 contém
94,5 % de Bagé. Correção à documentação: os shapefiles vêm em **EPSG:4674 (SIRGAS 2000
geográfico)**, não em Albers.

---

## 4. Sigilo

**Regras declaradas.** 2000 e 2010: setor com **menos de 5 DPP** tem quase todas as
variáveis omitidas (em branco em 2000, `X` em 2010); ficam as estruturais (domicílios,
população por sexo). Em 2000, além disso, **células de rendimento e anos de estudo com
menos de 4 informantes** também são omitidas. **2022: a regra não está documentada** em
nenhum arquivo consultado (cópia local e notas do servidor); o padrão medido — `X`
célula a célula em categorias raras — indica supressão **por célula**, não por setor.

Setores com ao menos uma célula suprimida nas variáveis do conceito (urbanos / rurais):

| conceito | 2000 (120 u / 45 r) | 2010 (129 u / 35 r) | 2022 (173 u / 26 r) |
| --- | --- | --- | --- |
| população total | 0 | 0 | 0 |
| sexo | 0 | 0 | 4 (2 / 2) |
| grupos de idade | 8 (6 / 2) | 2 (1 / 1) | 24 (7 / **17**) |
| DPP | 0 | 0 | 4 (2 / 2) |
| moradores por domicílio | 7 (6 / 1) | 2 (2 / 0) | 4 (2 / 2) |
| alfabetização | 8 (6 / 2) | 2 (1 / 1) | 49 (28 / **21**) |
| rendimento do responsável | **131 (95 / 36)** | 2 (1 / 1) | 4 (2 / 2) — tema de 2026-05-08 (§ 1.4) |
| cor ou raça | — | 2 (1 / 1) | 65 (58 / 7) |
| água | 8 (6 / 2) | 2 (1 / 1) | **146 (123 / 23)** |
| esgoto | 8 (6 / 2) | 2 (1 / 1) | **148 (127 / 21)** |
| lixo | 8 (6 / 2) | 2 (1 / 1) | 71 (54 / 17) |
| tipo de domicílio | 8 (6 / 2) | 2 (1 / 1) | 54 (48 / 6) |
| entorno (domicílios, moradores, faces) | — | ver § 1.4 | **0** (em 168–171 setores com linha) |

Leitura:

- **2000 e 2010:** a supressão é de **setor inteiro** e atinge poucos setores (8 e 2) —
  exceto o rendimento de 2000, suprimido por célula em 131 dos 165 setores.
- **2022:** a supressão é **por célula** e pesa nas distribuições com categorias
  raras: água e esgoto têm alguma célula suprimida em ~3 de cada 4 setores. Nos
  rurais, é quase a regra (idade 17/26, alfabetização 21/26, água 23/26). Somar
  categorias antes de analisar **não** recupera o valor suprimido.
- Em 2022, 4 setores têm todas as variáveis suprimidas em cada um dos conceitos
  avaliados; mais 1 (`430160221000001`) não tem linha nos temas.

Contagem completa por marcador e percentual de células: `derivados/r04_sigilo.json`.

---

## 5. CNEFE 2022 × setores 2022

62.782 endereços. Todos os `COD_SETOR` do CNEFE têm 16 caracteres, terminando em `P`
(o sufixo não é explicado no dicionário do CNEFE).

**4.024 endereços (6,4 %) apontam para 10 códigos que não existem na malha de
divulgação.** Estão no de/para como setores da malha **intermediária/preliminar** de
2022, divididos na etapa final em 2 ou 3 setores (formação `241`, `221`, `242`). O CNEFE
ficou com o código anterior à divisão. Por isso o resultado vem em duas leituras:

| leitura | dentro do setor indicado | % |
| --- | ---: | ---: |
| estrita (código como está) | 56.466 | 89,94 % |
| **por sucessão** (código resolvido pelo de/para para os setores de divulgação) | **60.345** | **96,12 %** |

Os **2.437** que caem fora do setor indicado (leitura por sucessão):

| distância até o setor indicado | endereços |
| --- | ---: |
| < 10 m | 1.794 |
| 10–50 m | 469 |
| 50–100 m | 95 |
| 100–500 m | 74 |
| 500 m – 1 km | 3 |
| 1–5 km | 2 |

- Mediana 3,9 m, máximo 1.045 m. 2.351 caem em outro setor **do mesmo distrito**;
  59 caem fora da malha do município.
- Por espécie: 1.835 domicílios particulares, 431 estabelecimentos de outras
  finalidades, 82 agropecuários, 37 edificações em construção, 31 de saúde, 8 de ensino,
  7 religiosos, 6 domicílios coletivos.
- Por nível de geocodificação (% dentro): coordenada original do Censo 96,4 %
  (58.158 end.); modificada para apartamentos no mesmo número 92,4 % (4.273); estimada
  85,5 % (262); níveis 4–6: 100 % (89).

Três quartos dos que caem fora estão a menos de 10 m: é o ponto de endereço sobre a linha
de fronteira do setor (fachada, meio da rua), não endereço trocado de setor. **A lista
endereço a endereço está em `derivados/r05_cnefe_fora.csv`, fora do git:** é dado de
endereço, e este documento, que é versionado, só publica agregados.

Pontos lidos como SIRGAS 2000 (`EPSG:4674`); o CSV não declara datum.

---

## 6. O que o dado sustenta

### Dá para medir

- Totais de **população** por setor, com urbano e rural, nos três censos — as somas
  fecham exatamente com os oficiais (2000 no território de 2000; ver Aceguá).
- **Série 2010–2022 por setor** em 99 setores (série limpa) e por **área mínima comum**
  em todo o município (165 AMCs), pelo de/para oficial.
- **Sexo**, **DPP** e **população total** por setor em 2000 e 2010, sem supressão
  relevante.
- **Cor ou raça** 2010 × 2022, nas mesmas 5 categorias.
- **Idade** nos três censos no esquema comum (0–4 … 25–29, decenais, 70+).
- **Alfabetização de 15 anos ou mais** nos três censos.
- **Rendimento do responsável 2000 × 2010** em classes de salário mínimo.
- **Endereços do CNEFE georreferenciados**, com 96 % no setor indicado (lido por
  sucessão).
- **Rendimento médio e mediano do responsável por setor em 2022**, universo DPPO, com
  supressão em só 4 setores.
- **Entorno urbanístico em 2022** nos setores urbanos (99,4 % dos DPPO urbanos), sem
  supressão, em três unidades (domicílios, moradores, faces).
- **Favelas e comunidades urbanas em 2022**: 6 FCU, 7 setores, 1.132 moradores.

### Não dá

- **Soma dos setores de 2000 como "Bagé de hoje"**: 11 setores (3.927 pessoas) são hoje
  de Aceguá.
- **Distribuição de rendimento em 2022** (só média e mediana foram publicadas).
- **Entorno rural em 2022** (2 domicílios rurais levantados em Bagé).
- **Série de favelas/aglomerados 2010 → 2022** (zero aglomerados em 2010; a mudança de
  conceito impede tratar a ausência de 2010 como "não havia favela").
- **Meio-fio, identificação do logradouro, esgoto a céu aberto e lixo acumulado em
  2022** (existiam no entorno de 2010, não no de 2022).
- **Calçada, pavimentação e arborização 2010 → 2022**: não comparáveis segundo o IBGE
  (grupo B, pp. 50–52). Por efeito de método, calçada tende a subir e pavimentação e
  arborização a cair.
- **Cor ou raça em 2000** (não está no universo).
- **Série 2000–2010 por setor**: sem de/para oficial, CRS de 2000 não resolvido, IoU ~0,5.
- **Água e esgoto por setor em 2022 com todas as categorias**: supressão em ~75 % dos
  setores.
- **Bairros de Bagé pelo Censo 2022** (já registrado nas ressalvas: Bagé não tem bairros
  na divulgação).
- **Educação, trabalho, migração, deficiência por setor em 2022**: não foram divulgados
  nesse nível.

### Dá com ressalva

- **Série 2000 → 2010**: só em áreas maiores que o setor, e condicionada à hipótese de
  CRS da malha urbana de 2000 (erro de classificação esperado ~15 %).
- **Saneamento 2000 × 2010 × 2022**: só "rede geral" (água) e categorias agregadas
  (esgoto: somar as fossas sépticas de 2022; lixo: somar coleta + caçamba), e em 2022
  preferir agregar setores antes de usar categorias raras.
- **Moradores por domicílio 2022**: calcular `V00005 / V00001`; a média publicada
  inclui improvisados.
- **Domicílios em 2022**: definir o universo (DPPO, DPO ou total) antes de somar; não há
  total municipal oficial local para conferir.
- **Rendimento 2010**: as classes de `ResponsavelRenda` incluem responsáveis de
  improvisados e de unidades em coletivos (+28 sobre DPP, −19 por supressão; § 1.2); para
  universo DPP estrito, usar as médias do `Basico`.
- **Setores rurais de 2022**: a supressão por célula é quase regra; resultados rurais
  por setor saem com lacunas grandes.
- **Rendimento do responsável 2010 × 2022**: só a média dos que têm rendimento
  (`Basico V007` × `V06004`), nominal — deflacionar; universos DPP × DPPO.
- **Entorno 2010 × 2022**: pela classificação do IBGE (2025, pp. 50–52; § 1.4), só
  **iluminação pública** e **bueiro/boca de lobo** têm comparação direta. **Rampa** é
  comparável com restrição (2010 só nas faces com calçada e rampa), mas a restrição exige
  dado por face e não se aplica aos agregados por setor. O universo da série são as
  **139 AMCs com entorno nos dois anos** (139 setores de 2010 e 155 dos 168 de 2022);
  comparar sempre proporções dentro delas, porque o universo de 2022 é maior.
- **Favelas 2022**: 6 FCU em 7 setores; Passo das Pedras sem entorno (0 % de
  cobertura). **Sem série com 2010**: Bagé não tinha aglomerado subnormal, e nenhum dos 7
  setores de 2022 descende de setor de aglomerado — a série "favela" começa em 2022.
- **Grade estatística 2010/2022**: baixada (quadrantes 14 e 04, conferidos contra a área
  de estudo), mas só com população e domicílios; em 2010 os valores por célula vêm de
  agregação/desagregação do IBGE, não de contagem direta.
- **CNEFE × setores**: usar o de/para para os 10 códigos da malha intermediária; 3,9 %
  dos pontos caem fora do setor indicado, quase todos na fronteira.

### Perguntas de pesquisa — SUGESTÕES para o responsável

Nenhuma foi escolhida; todas são sustentadas pelo dado dentro das ressalvas acima.
Atualizadas em 2026-09-22 com os temas do § 1.4 (limite de cinco).

1. **SUGESTÃO** (mantida) — Como a população e o número de domicílios se redistribuíram
   no território de Bagé entre 2010 e 2022, nas 165 áreas mínimas comuns do de/para
   oficial?
2. **SUGESTÃO** (mantida) — O envelhecimento entre 2010 e 2022 é homogêneo no município
   ou se concentra em áreas específicas (esquema etário comum, 70+)?
3. **SUGESTÃO** (reescrita em 2026-09-22 com a metodologia do IBGE, § 1.4; em duas
   partes):
   - **(a) 2010 → 2022, restrita**: como mudou a proporção de domicílios urbanos com
     **iluminação pública** e com **bueiro/boca de lobo**, por área mínima comum?
     **Rampa** só entra se aparecer o dado de 2010 por face, para aplicar a restrição
     do IBGE. **Calçada, pavimentação e arborização ficam fora da série.** O recorte
     são as 139 AMCs com entorno nos dois anos.
   - **(b) 2022, retrato transversal completo**: como se distribuem no território
     urbano de 2022 todos os itens do entorno (pavimentação, calçada, obstáculo, rampa,
     arborização em classes, iluminação, bueiro, ponto de ônibus, via para bicicleta,
     capacidade da via), por setor e por face? Sem comparação com 2010.
4. **SUGESTÃO** (nova) — Como o rendimento médio do responsável (com rendimento,
   deflacionado) variou entre 2010 e 2022 por área mínima comum, e em que medida
   acompanha as mudanças de iluminação e bueiro (os únicos itens do entorno com série)?
5. **SUGESTÃO** (nova) — Como as 6 favelas e comunidades urbanas de 2022 se diferenciam
   do restante da área urbana em rendimento, características do domicílio e entorno
   (Passo das Pedras sem entorno)?

Saíram da lista, só pelo limite de cinco, e continuam sustentadas: composição por cor ou
raça 2010–2022 por área mínima comum; usos não residenciais do CNEFE × densidade de
domicílios; variação de domicílios ocupados urbano × rural com a população quase
estável.
