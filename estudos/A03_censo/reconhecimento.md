# A03 — Reconhecimento dos dados do Censo (2000, 2010, 2022) e do CNEFE 2022

**Município:** Bagé/RS (`4301602`) · **Data:** 2026-09-22 · **Status do estudo:** reconhecimento

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
| rendimento do responsável | existe · 9 classes de SM (SM = R$ 151) + totais em R$ (`Responsavel1 V0602–V0623`) | existe · as mesmas 9 classes (SM = R$ 510) + totais (`ResponsavelRenda V001–V022`) | **diferente — e fora da cópia local** · publicado em 2026-05-08, em diretório próprio (`Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/`), com **6 variáveis**: responsáveis, moradores, rendimento médio, mediano e variâncias; **sem classes** |
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
  `ResponsavelRenda V020` soma 38.513 contra 38.504 DPP (17 setores com V020 > V001):
  universo não exatamente DPP, **a confirmar**.
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
- **Divulgados e ausentes da cópia local:**
  - **rendimento do responsável** (2026-05-08; ver tabela 1.2);
  - **entorno urbanístico** (2025-04-17: domicílios, faces, moradores; e uma versão em
    percentual já com geometria, `br_setores_entorno_cd2022.gpkg`, 2025-12-12);
  - **registro de nascimento** por setor (2026-02-04);
  - anexo de **favelas e comunidades urbanas** por setor.
- **Não existem por setor** (constatação de ausência): educação além de alfabetização,
  trabalho, migração, deslocamento, fecundidade, deficiência.
- **O que ainda falta publicar: o servidor não diz.** Não há leia-me, nota ou
  diretório anunciando temas futuros; nenhuma lista de pendências foi assumida.

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
**Relatado, não decidido.** A malha rural de 2000 vem sem `.prj`, em graus; foi lida
como SAD69 geográfico (`EPSG:4618`) — **suposição**.

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

Arquivos que cobrem Bagé (não baixados):

| arquivo | bytes | Last-Modified |
| --- | ---: | --- |
| `censo_2022/grade_estatistica/grade_id14.zip` | 26.890.770 | 2025-06-12 |
| `censo_2022/grade_estatistica/grade_id04.zip` | 3.031.479 | 2025-06-12 |
| `censo_2010/grade_id14.zip` | 32.648.454 | 2016-10-06 |
| `censo_2010/grade_id04.zip` | 3.830.448 | 2016-10-06 |

`ID_14` cobre ~94,5 % do município (a cidade e 198 dos 199 setores); `ID_04`, uma faixa
rural no extremo sul (~224 km²). A atribuição é **inferida**: nenhum documento dá as
coordenadas dos quadrantes; a regra (blocos de 500 km a partir da origem da projeção)
foi deduzida e conferida em 7 pontos do mapa oficial. Confirma-se pelo campo
`QUADRANTE` depois de baixar.

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
| rendimento do responsável | **131 (95 / 36)** | 2 (1 / 1) | — (fora da cópia local) |
| cor ou raça | — | 2 (1 / 1) | 65 (58 / 7) |
| água | 8 (6 / 2) | 2 (1 / 1) | **146 (123 / 23)** |
| esgoto | 8 (6 / 2) | 2 (1 / 1) | **148 (127 / 21)** |
| lixo | 8 (6 / 2) | 2 (1 / 1) | 71 (54 / 17) |
| tipo de domicílio | 8 (6 / 2) | 2 (1 / 1) | 54 (48 / 6) |

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

### Não dá

- **Soma dos setores de 2000 como "Bagé de hoje"**: 11 setores (3.927 pessoas) são hoje
  de Aceguá.
- **Distribuição de rendimento em 2022** (só média e mediana foram publicadas — e fora
  da cópia local).
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
- **Rendimento 2010**: o universo de `ResponsavelRenda` não é exatamente DPP (38.513 ×
  38.504); a confirmar.
- **Setores rurais de 2022**: a supressão por célula é quase regra; resultados rurais
  por setor saem com lacunas grandes.
- **Grade estatística 2010/2022**: disponível (quadrantes 14 e 04), mas só com população e
  domicílios, e a atribuição dos quadrantes é inferida até o download.
- **CNEFE × setores**: usar o de/para para os 10 códigos da malha intermediária; 3,9 %
  dos pontos caem fora do setor indicado, quase todos na fronteira.

### Perguntas de pesquisa — SUGESTÕES para o responsável

Nenhuma foi escolhida; todas são sustentadas pelo dado dentro das ressalvas acima.

1. **SUGESTÃO** — Como a população e o número de domicílios se redistribuíram no
   território de Bagé entre 2010 e 2022, nas 165 áreas mínimas comuns do de/para oficial?
2. **SUGESTÃO** — O envelhecimento entre 2010 e 2022 é homogêneo no município ou se
   concentra em áreas específicas (esquema etário comum, 70+)?
3. **SUGESTÃO** — Como mudou a composição por cor ou raça entre 2010 e 2022, por área
   mínima comum?
4. **SUGESTÃO** — Onde o CNEFE 2022 mostra usos não residenciais (estabelecimentos por
   espécie) e como isso se relaciona com a densidade de domicílios por setor?
5. **SUGESTÃO** — Com a população quase estável (116.794 em 2010, 117.938 em 2022),
   onde — em áreas urbanas × rurais — está a variação no número de domicílios
   ocupados, definido o mesmo universo de domicílio nos dois censos?
