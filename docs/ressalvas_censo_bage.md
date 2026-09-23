# Ressalvas do Censo e do CNEFE para Bagé/RS

> **Origem destas ressalvas:** medições feitas no projeto **REVIA_BG**
> (`~/projetos/rede_viaria_bage`) sobre os arquivos do IBGE que ele baixou em
> 20/09/2026. Não foram refeitas aqui; valem porque os arquivos deste
> repositório têm o **mesmo sha256** dos medidos lá. Desde 22/09/2026 esses
> arquivos ficam como dado bruto em `data/raw/tabular/ibge/censo_<ano>/` e
> `data/raw/vetor/ibge/censo_<ano>/`, obtidos direto do IBGE por
> `scripts/download/baixar_censo_ibge.py` (lista fixa em
> `config/fontes_censo_ibge.yaml`). A procedência da cópia original está em
> `docs/procedencia/revia_bg_censo/`. **Exceção:** os §§ 7 a 9 (grade estatística e
> níveis de geocodificação do CNEFE) foram medidos neste repositório, no estudo A03.

Quem usar os arquivos brutos do Censo (`data/raw/*/ibge/censo_<ano>/`) neste acervo precisa ler isto antes.
São conclusões **medidas** sobre estes arquivos exatos — os mesmos sha256 que estão
no `.json` irmão de cada um e em `data/catalogo_fontes.csv` — no projeto REVIA_BG
(`~/projetos/rede_viaria_bage`), de onde os arquivos vieram por cópia em 20/09/2026.

Não são opinião nem estimativa: cada número abaixo saiu de uma contagem sobre o
arquivo. O que não foi medido está dito como não medido.

**Município:** Bagé/RS, código IBGE `4301602`.

---

## 1. A soma dos setores fecha nos três censos — comparando a mesma grandeza

*Corrigido em 2026-09-22 (texto anterior preservado na seção
[Corrigido em 2026-09-22](#corrigido-em-2026-09-22)). Medição:
`estudos/A03_expansao_adensamento/reconhecimento.md` § 2, script `estudos/A03_expansao_adensamento/scripts/r02_totais.py`.*

Cada soma de setores confrontada com o total oficial **da mesma grandeza**:

| censo | grandeza | soma dos setores (urbana / rural) | total oficial | diferença |
| --- | --- | --- | --- | ---: |
| 2022 | população (`v0001`) | 117.938 (114.883 / 3.055) | 117.938 (114.883 / 3.055) | **0** |
| 2010 | população (`Domicilio02 V001`) | 116.794 (97.765 / 19.029) | 116.794 (97.765 / 19.029) | **0** |
| 2010 | DPP (`Basico V001`) | 38.504 (32.642 / 5.862) | 38.504 | **0** |
| 2010 | moradores em DPP (`Basico V002`) | 116.318 (97.304 / 19.014) | 116.318 | **0** |
| 2000 | população (`Pessoa1 V1330`) | 118.767 (97.290 / 21.477) | 118.767 (97.290 / 21.477) | **0** |
| 2000 | DPP (`Basico Var01`) | 35.119 | 35.119 | **0** |

Em 2010 a igualdade vale também **distrito a distrito**, nas três grandezas.

**A soma dos setores serve como total municipal nos três censos.** O que não se pode é
comparar grandezas diferentes: `V002` de 2010 e `Var12` de 2000 são **moradores em
domicílios particulares permanentes**, e ficam abaixo da população total porque ela
inclui domicílios improvisados e coletivos (2010: 116.318 × 116.794; 2000: 117.893 ×
118.767). Era essa a origem das diferenças de −476 (2010) e −874 (2000) registradas
antes.

## 2. 2010: quatro setores sem linha na tabela — contribuem zero

A malha de 2010 tem **168 setores** em Bagé; as tabelas, **164**. Os 4 sem linha:
`430160205000142` (rural, entre a Estrada dos Vieiras, o rio Negro e a BR-153) e as
sedes das vilas de Joca Tavares (`430160217000001`), José Otávio (`430160220000001`) e
Palmas (`430160221000001`), desenhadas como quadrados de ~100 m em torno de escola ou
subprefeitura.

Procurados em **todos** os arquivos de dados da divulgação de 2010 (26 CSV e 26 XLS), na
documentação, nas 21 tabelas por município/distrito e no de/para 2010→2022: aparecem
**só** na descrição dos setores (`Descrição_RS.xls`) e no de/para, **em nenhum arquivo
de dados**.

Como os totais fecham exatamente sem eles — no município e em cada distrito (§ 1) —, os
4 **contribuem zero pessoas e zero domicílios**. A razão da omissão não está escrita na
divulgação; "setor sem domicílio não tem linha" é inferência coerente com os totais, não
afirmação do IBGE. O setor `430160221000001` reaparece em 2022 só na tabela básica, com
população 0.

## 3. 2000: o território não é o de hoje; CRS da malha decidido, uso só agregado

**Território.** A própria divulgação de 2000 traz `Compatibilização_2000-2001_RS.xls`:
**11 setores** de Bagé (distritos `…10` e `…12`) passaram a **Aceguá**, instalado em
2001 — **3.927 pessoas** e 1.147 DPP. Bagé de 2000 no território de 2001 = **114.840**
habitantes, o mesmo número da planilha oficial "Municípios instalados em 2001". Na
geometria, 1.545 km² desses setores estão hoje em Aceguá. Comparação 2000 × 2010/2022
do município inteiro tem de descontar esses setores.

Lado espacial:

- a malha urbana de Bagé (`data/raw/vetor/ibge/censo_2000/4301602.zip`, 127 setores) vem
  declarada em **EPSG:32621 — UTM 21 NORTE**, hemisfério errado para Bagé (58,8° N).
  **CRS DECIDIDO pelo responsável em 2026-09-22: SAD69 / UTM 21S (`EPSG:29191`)** —
  registrado no `.json` irmão do arquivo (campo `crs`) e em
  `config/fontes_censo_ibge.yaml`; o arquivo não foi alterado nem reprojetado.
  **Limitação conhecida:** lida em `EPSG:29191`, a malha tem **deslocamento residual de
  ~90–105 m** em relação à malha de 2010 e IoU por setor de ~0,5 (medido em
  `estudos/A03_expansao_adensamento/reconhecimento.md` § 3.2). **7 das 127 geometrias são inválidas**;
- a malha rural (`rs_setores_censitarios.zip`, 44 códigos em Bagé) vem **sem CRS
  declarado**, em graus; 6 dos seus polígonos são envoltórias de faixas de setores
  urbanos (ex.: `…001-0114`), e não setores. **CRS DECIDIDO pelo responsável em
  2026-09-22: SAD69 geográfico (`EPSG:4618`)** — registrado no `.json` irmão do arquivo
  (campo `crs`) e em `config/fontes_censo_ibge.yaml`; o arquivo não foi alterado nem
  reprojetado. Vale a mesma regra de uso abaixo;
- **REGRA DE USO: dados de 2000 só por município e por distrito, nunca por setor.** O
  resíduo de ~100 m e a ausência de de/para oficial 2000→2010 não sustentam comparação
  nem mapeamento setor a setor;
- as tabelas de 2000 (XLS BIFF8) **foram lidas** em 2026-09-22 com `xlrd`
  (`requirements.txt`); 127 setores urbanos + 38 rurais = 165, exatamente as linhas da
  tabela.

## 4. Comparabilidade 2010 → 2022: o geocódigo não é identificador estável

Só **141 dos 199 setores de 2022 (70,9 %)** têm correspondência **1:1** com 2010.
**21 setores de 2010 foram divididos**, chegando a **6 destinos**.

> **O geocódigo de setor NÃO é identificador estável entre censos.** Qualquer série
> temporal por setor tem de passar pelo de/para do IBGE —
> `data/raw/tabular/ibge/censo_2022/doc/Historico_formacao_Setores_Censitarios_2010_2022.xlsx`
> — ou usar um recorte estável (bairros, município).

O próprio IBGE publica a ressalva em
`data/raw/tabular/ibge/censo_2022/doc/Leia_me_Comparabilidade_2010_2022.pdf`.

Juntar 2010 com 2022 por igualdade de geocódigo **não gera erro**: gera número plausível
e falso, porque parte dos códigos casa por coincidência de recorte parcial.

## 5. Bagé não tem bairros na divulgação do Censo 2022

Medido nos 199 setores de Bagé por `CD_MUN`, `NM_MUN` e `NM_BAIRRO`: **Bagé não tem
bairro na divulgação do IBGE de 2022**. Dos 497 municípios do RS, 162 têm; Bagé não é
um deles, e os 199 setores têm `NM_BAIRRO` vazio.

**Controle negativo:** a mesma medição em **Porto Alegre** devolve **99 bairros** — ou
seja, a contagem zero em Bagé é ausência real na fonte, não filtro quebrado.

Consequência: `data/raw/vetor/ibge/censo_2022/malha_com_atributos/RS_bairros_CD2022.gpkg` está guardado pelo
RS e como controle, **não** como fonte de bairros de Bagé. Para bairros de Bagé existe a
camada própria do REVIA_BG (decisão DN-B1), com dois recortes — administrativo e
recortado pela mancha urbana —, e todo cruzamento "por bairro" tem de declarar qual usa.

## 6. CNEFE 2022 de Bagé

**62.782 endereços, 34 campos, 100 % com coordenada.** **93,84 %** caem dentro da mancha
urbana v2.3 do REVIA_BG.

| espécie | endereços |
| --- | ---: |
| domicílio particular | 53.629 |
| domicílio coletivo | 87 |
| estabelecimento agropecuário | 1.427 |
| estabelecimento de ensino | 122 |
| estabelecimento de saúde | 238 |
| estabelecimento de outras finalidades | 6.092 |
| edificação em construção | 931 |
| estabelecimento religioso | 256 |

**Conferência independente entre dois produtos do mesmo Censo:** as espécies 1 e 2 do
CNEFE (53.629 e 87) coincidem **exatamente** com `v0003` e `v0004` do agregado por
setores. São arquivos diferentes, diretórios diferentes e datas de divulgação diferentes
— é uma medida que tinha de bater e bateu.

**Dado de endereço.** Publicar qualquer derivado do CNEFE no geoportal exige decidir
antes o nível de agregação; o arquivo bruto não vai para `data/geoportal/`.

## 7. Grade estatística 2010 → 2022: a resolução mudou em 41 lugares

*Acrescentado em 2026-09-23. Diferente dos §§ 1–6, esta ressalva foi **medida neste
repositório**, não no REVIA_BG. Medição: `estudos/A03_expansao_adensamento/resultados_s1.md`
§§ 1, 4 e 8, script `estudos/A03_expansao_adensamento/scripts/s1_expansao_adensamento.py`,
sobre a grade bruta em `data/raw/vetor/ibge/censo_<ano>/grade_estatistica/`
(quadrantes `grade_id14` e `grade_id04`).*

A grade estatística do IBGE é aninhada (200 m no urbano, 1 km no rural), mas **não é a
mesma nas duas edições**. Em **41 lugares de Bagé** (centroide no município), o IBGE
refinou a resolução entre 2010 e 2022: a célula de 1 km de 2010 aparece em 2022 como as
**25 células de 200 m** que a compõem.

| medida | valor |
| --- | ---: |
| células de mesmo `ID_UNICO` nas duas edições | 5.677 |
| nelas: distância máxima entre centroides / diferença máxima de área | 4,9 × 10⁻⁵ m / 0,14 m² |
| células de 1 km de 2010 subdivididas em 2022 (mães) | **41** |
| células de 200 m de 2022 que as substituem (filhas, 41 × 25) | **1.025** |
| desvio máximo de área, soma das filhas × mãe (ESRI:102033) | 0,1 m² |
| mães com domicílio em 2010 (domicílios / pessoas) | 32 (2.380 / 7.945) |
| filhas com domicílio em 2022 (domicílios / pessoas) | 224 (3.892 / 10.969) |

No recorte lido pelos dois quadrantes (caixa envolvente do município, além da borda) há
62 mães e 1.550 filhas; as 41 e 1.025 acima são as de Bagé.

**Por que importa.** Juntar as edições por `ID_UNICO` e tratar o ausente como zero **não
gera erro**: as filhas entram como ocupação nova e a mãe como área abandonada.
- Em Bagé isso fez 224 células "novas" e 32 "extintas" que eram só troca de resolução,
  e levou a expansão a **40 %** do ganho bruto de domicílios.
- Na unidade harmonizada, a expansão fica entre **16,6 % e 25,6 %**. É o número adotado
  do A03, com o setor de 2010 430160205000136 à parte, por causa do § 8.
- Com todas as unidades, a sensibilidade é de 15,6 % a 30,1 %. É esta a comparação que
  mede o efeito da troca de resolução, porque só ela muda a junção.
- As células só numa edição parecem diferença de cobertura, mas são exatamente as mães
  e as filhas.

> *Corrigido em 2026-09-23. O texto anterior terminava com: "[...] e levou a expansão a
> **40 %** do ganho bruto de domicílios, quando na unidade harmonizada ela fica entre
> **15,6 % e 30,1 %**." Esse número continua válido como sensibilidade com todas as
> unidades.*

> **REGRA DE USO: comparar a grade de 2010 com a de 2022 só na unidade harmonizada** —
> onde 2010 tem uma célula de 1 km e 2022 tem as suas 25 filhas de 200 m, comparar a
> mãe com a soma das filhas. **Juntar por `ID_UNICO` trata refinamento como ocupação
> nova.** Conferir antes de medir: cada célula que só existe numa edição tem de estar
> contida numa célula da outra, e as filhas têm de cobrir a mãe; se sobrar alguma
> coisa, parar.

Mesmo na unidade harmonizada fica uma incerteza: numa mãe de 1 km que já tinha domicílio
em 2010, a resolução de 2010 não separa ocupação de área nova de adensamento.
- No cenário adotado, são 18 unidades adensadas com 1.028 domicílios ganhos, e é essa a
  largura da faixa de 16,6 % a 25,6 %.
- Com todas as unidades, são 22 com 1.754, e a faixa vai de 15,6 % a 30,1 %.

*Corrigido em 2026-09-23. Antes, o parágrafo dava só "22 unidades adensadas com 1.754
domicílios ganhos [...] a faixa de 15,6 % a 30,1 %".*

**No A03, é achado de método.** A seção de método prevista do artigo
(`estudos/A03_expansao_adensamento/manifesto.yaml`, `metodo_previsto`) tem **dois
achados metodológicos**:
1. a **reclassificação de 13 setores rurais de 2010 em urbanos de 2022**, que faz a série
   urbano × rural pelo rótulo de situação do setor produzir um falso êxodo rural (67 % do
   ganho urbano de população);
2. a **troca de resolução da grade entre 2010 e 2022**, desta seção, que faz a junção por
   identificador produzir uma falsa expansão.

Os dois têm a mesma forma: uma mudança de recorte do IBGE que, lida como se o recorte
fosse fixo, vira mudança no território.

*Desde 2026-09-23 são três achados: o terceiro é a grade de 2010 híbrida (§ 8).*

---

## 8. Grade estatística de 2010: híbrida por método, sem a variável de abordagem

*Acrescentado em 2026-09-23. Lido na documentação do IBGE e medido neste repositório.*
- Documentação: `data/raw/tabular/ibge/censo_2010/doc/grade_estatistica.pdf` (IBGE,
  *Grade Estatística*, 2016) e
  `data/raw/tabular/ibge/censo_2022/doc/Notas_metodologicas_grade_estatistica_2022.pdf`.
- Medição: `estudos/A03_expansao_adensamento/resultados_s1.md` § 10.4 e § 10.6, script
  `scripts/s1_desagregacao_2010.py`.

**A grade de 2010 não é observação direta em toda parte.** Pelo método do próprio IBGE
(p. 16–22), ela é **híbrida**:

| ausência de localização no setor | abordagem | como a célula recebe domicílios e população |
| --- | --- | --- |
| < 50 % | agregação | rural: pontos das coordenadas. Urbano: **quadra/face**, repartida pela extensão da face quando ela cruza células. |
| > 50 % | desagregação | dasimétrico com vias; ou dasimétrico binário com uso e cobertura; ou ponderação zonal simples. População = domicílios × moradores por domicílio **do setor**. |

- A metodologia descreve uma **variável de abordagem por célula** (agregação,
  desagregação ou misto, p. 21). **Ela não acompanha o produto distribuído no geoftp:**
  - os arquivos `grade_idNN.zip` de 2010 têm só `ID_UNICO`, `nome_*`, `QUADRANTE`,
    `MASC`, `FEM`, `POP` e `DOM_OCU`;
  - a listagem não traz outro produto.
- **A regra também não se reconstrói por setor:** a "ausência de localização" de cada
  setor não é publicada.

**A grade de 2022 é observada** (notas 01/2025, p. 7): totalização direta dos
microdados pela coordenada do endereço no CNEFE (níveis 1 a 4), com os níveis 5 e 6
excluídos. Não há equivalente da desagregação.

**Consequência.** Comparar 2010 com 2022 sem separar a abordagem **mistura dado modelado
com dado observado**. Onde 2010 foi desagregado, a presença de domicílio numa célula e o
zero da vizinha vêm da distribuição do setor, não do endereço. A diferença para 2022
pode aparecer como "extinta", "nova" ou "esvaziada" sem que nada tenha mudado no
lugar.

**O que se detecta sem a variável** (indício, não a variável):
- **Razão moradores/domicílio igual à do setor.** Não discrimina, e foi descartada:
  - 26,3 % das células de 2010 são compatíveis, contra 21,7 % em 2022, que não tem
    desagregação;
  - as células com a marca mais clara nem seguem a razão publicada do setor.
- **Pares (domicílios, população) idênticos em células vizinhas inteiras do mesmo setor.**
  Discrimina: 4 células em 2010, 0 em 2022. Mas só enxerga ponderação zonal ou
  dasimétrico binário em blocos homogêneos.
  - Em Bagé, marca um setor: o rural `430160205000136`.
  - As unidades desse setor têm **968 domicílios de 2010** e respondem por **31 das 232
    extintas** da subordinada 1 do A03.
- **O número de células desagregadas detectado é um PISO, não uma estimativa.**
  - Só deixam rastro a ponderação zonal e o dasimétrico binário, e só num bloco
    homogêneo: células inteiras com a mesma área povoada no mesmo setor.
  - Não deixam **nenhum** rastro:
    - a desagregação num setor heterogêneo;
    - a desagregação por vias;
    - a célula mista.
  - Nesses casos a célula desagregada não se distingue da agregada.
- **O teste da razão do setor foi descartado pelo controle de 2022, e o descarte é
  parte do método.**
  - Ele parte da fórmula do IBGE: população = domicílios × moradores por domicílio do
    setor.
  - Mas acusa 21,7 % de compatíveis em 2022, que não tem desagregação, contra 26,3 %
    em 2010.
  - Quem repetir o teste em outro município precisa do mesmo controle antes de ler
    qualquer resultado.
- **O tamanho do viés no município inteiro não se mede sem a variável oficial.** O
  pedido ao IBGE está em `docs/pedido_ibge_grade_2010_abordagem.md`, pronto para
  envio e não enviado.
- **No A03,** o setor 136 é declarado à parte nos resultados da subordinada 1 por
  decisão do responsável (2026-09-23; `resultados_s1.md` § 11).

> **REGRA DE USO: toda comparação 2010 × 2022 na grade declara que 2010 é parcialmente
> modelado.**
> - Resultado que dependa da posição fina de poucos domicílios em 2010 (célula que
>   "surge" ou "some", sobretudo no rural e em setores urbanos isolados) é indício, não
>   medida.
> - Quando a variável de abordagem for obtida, separar as células desagregadas antes de
>   medir.

**No A03, é o terceiro achado metodológico** (`metodo_previsto` do manifesto), ao lado
da reclassificação dos 13 setores e da troca de resolução (§ 7).
- Os três têm a mesma forma: um procedimento do IBGE que, lido como se o dado fosse
  homogêneo, vira mudança no território.
- **A regra do upgrade** de 1 km para 200 m (notas 2022, p. 6: célula de 1 km de 2010
  que passa a intersectar setor urbano de 2022) **confirma** a medição do § 7. As 41
  mães de Bagé são exatamente as células previstas pela regra, 41 de 41.

---

## 9. CNEFE 2022: as duas listas de nível de geocodificação não coincidem

*Acrescentado em 2026-09-23. Medido neste repositório: `estudos/A03_expansao_adensamento/scripts/s1_desagregacao_2010.py`,
bloco `niveis_de_geocodificacao_cnefe_2022`.*

O campo `NV_GEO_COORD` do CNEFE 2022 tem duas descrições diferentes nos níveis 2, 3 e
5. Os dois textos, literais:

| nível | *Notas metodológicas 01/2025 — Grade Estatística*, p. 7 | dicionário do CNEFE (`Dicionario_CNEFE_Censo_2022.xls`) |
| --- | --- | --- |
| 2 | "Coordenada modificada pela mediana das coordenadas coletadas em um mesmo logradouro" | "Endereço - coordenada modificada (apartamentos em um mesmo número no logradouro)" |
| 3 | "Coordenada estimada a partir da coordenada registrada em operação anterior para o endereço atual" | "Endereço - coordenada estimada (endereços originalmente sem coordenadas ou coordenadas inválidas)" |
| 5 | "Mediana das coordenadas de endereços em mesmo logradouro, CEP e localidade" | "Localidade" |

Os níveis 1, 4 e 6 coincidem: coordenada original, ponto médio da face de quadra e
centroide do setor.

**Em Bagé, o dado confere com o dicionário no nível 2:**
- 3.925 dos 4.273 endereços de nível 2 (92 %) são apartamentos;
- todos compartilham logradouro e número com outro registro;
- nos 81 logradouros com mais de um número em nível 2, **cada número tem a sua
  coordenada**, e nenhum tem coordenada única de logradouro.

Os níveis 3 (262 endereços) e 5 (2) não se decidem pelo dado.

**O que depende da lista:**
- **Nenhuma contagem.** O código é o mesmo nas duas listas.
- A exclusão dos níveis 5 e 6 da grade de 2022 vale em qualquer das duas; em Bagé são
  3 endereços.
- **Dependem só os rótulos:** o do nível 3 no reconhecimento do A03 (§ 5, 262
  endereços) segue o dicionário e é incerto.
- **Uma afirmação foi corrigida:** "o nível 4 é a única posição que não é do endereço"
  (A03, `resultados_s1.md` § 10.4). Nas duas listas, os níveis 2 a 4 não são a
  coordenada original: em Bagé são **4.621 endereços (7,4 %)**, 4.487 deles domicílios.

> **REGRA DE USO:** ao citar um nível de geocodificação do CNEFE 2022, dizer de qual
> lista vem o rótulo. Em Bagé, para o nível 2, usar o do dicionário, que o dado
> confirma.

---

## 10. Grade estatística de 2010: no urbano, o domicílio está na face, repartida pela extensão

*Acrescentado em 2026-09-23. Medido neste repositório:
`estudos/A03_expansao_adensamento/scripts/s1_faces_2010.py` → `derivados/s1_faces_2010.json`,
com a Base de Faces de Logradouros do Censo 2010 (fonte `ibge_censo2010_faces_logradouros`).*

A metodologia da grade de 2010 (p. 18–19) agrega o setor urbano por face de quadra e,
quando a face cruza células, reparte os domicílios pela extensão dela, supondo
distribuição uniforme. Em Bagé isso está **confirmado no dado**: repartir o `TOT_RES`
de cada face pelo comprimento reproduz o `DOM_OCU` das 1.053 células de 200 m de setor
urbano com correlação de **0,989**.

- **57,8 %** dos endereços residenciais urbanos de 2010 (20.330 de 35.174) estão em
  face que cruza células.
- Reposicionar o 2010 pelos endereços do CNEFE 2022 ao longo da mesma face muda de
  célula cerca de **2,1 mil domicílios (6,5 %)**. É um limite superior, porque inclui
  crescimento e demolição ao longo da face.
- A repartição cria **extintas e novas de borda** que o endereço de 2022 não sustenta.
  No A03, das 56 extintas urbanas, 29 (95 domicílios) têm indício de deslocamento por
  repartição e somem com o reposicionamento; outras 23 (244 domicílios) estão em faces
  que perderam os endereços, e são esvaziamento medido (`resultados_s1.md` § 12).

**Consequência, geral:** no urbano, a grade de 2010 e a de 2022 **não são comparáveis
célula a célula**, porque o posicionamento mudou de método — face repartida em 2010,
endereço em 2022. Isso vale para **qualquer município**, não só Bagé: a regra de 2010 é
nacional (Grade Estatística, 2016, p. 18–19), e a de 2022 também (Notas metodológicas
01/2025, p. 6–7). O tamanho do efeito (57,8 % e 6,5 % aqui) é de Bagé; o de outro
município depende do comprimento das faces diante da célula de 200 m.

No A03 é o **quarto achado de método** (manifesto, `metodo_previsto`). Decisão do
responsável (2026-09-23): as classes ficam como a grade publica, e o reposicionamento
pela face é sensibilidade declarada, não classificação.

> **REGRA DE USO:** ao comparar célula a célula a grade de 2010 com a de 2022 no
> urbano, a posição de 2010 é a da face e não a do endereço. Mudança numa célula de
> borda de face (extinta ou nova com poucos domicílios) é indício, não fato, até
> conferir as faces que a atravessam.

---

## Corrigido em 2026-09-22

Texto anterior dos §§ 1 a 3, mantido como registro. Foi substituído porque comparava
moradores em domicílios particulares permanentes com população total (diferenças de
−476 em 2010 e −874 em 2000, que desaparecem quando se compara a mesma grandeza), não
considerava a transferência de 11 setores de 2000 para Aceguá e deixava em aberto o
efeito dos 4 setores de 2010 sem linha. Medição que motivou a correção:
`estudos/A03_expansao_adensamento/reconhecimento.md` § 2.

<details>
<summary>Texto anterior (até 2026-09-22)</summary>

> ## 1. A soma dos setores fecha em 2022, e não fecha em 2010
>
> | censo | soma dos setores | total oficial do município | diferença | serve como total municipal? |
> | --- | ---: | ---: | ---: | --- |
> | 2022 | **117.938** | 117.938 | **0** | **sim** |
> | 2010 | 116.318 (`V002`) | 116.794 | **−476** (−0,408 %) | **não** |
> | 2000 | 117.893 (`Var12`) | 118.767 | −874 | não, mas por outro motivo (§ 4) |
>
> Em 2022 a soma dos **199 setores** de Bagé fecha **exatamente** com o total oficial
> (urbana 114.883 + rural 3.055). A tabela e a malha têm os mesmos 199 códigos:
> 0 só na tabela, 0 só na malha.
>
> ## 2. 2010: quatro setores sem linha na tabela — causa em aberto
>
> A malha de 2010 tem **168 setores** em Bagé; a tabela de agregados tem **164**.
> **Quatro setores existem na malha e não têm linha na tabela** — três sedes de distrito
> e um rural — e **não aparecem em nenhuma das 26 planilhas** do pacote.
>
> A causa **não foi determinada**; fica declarada em aberto. A consequência é operacional
> e não depende de descobrir a causa:
>
> > **A soma dos setores de 2010 NÃO serve como total municipal.** Para o total de 2010,
> > usar a tabela oficial por município (`2010/tabelas/rio_grande_do_sul.zip`), não a soma.
>
> ## 3. 2000: a diferença é de recorte, não erro
>
> `Var12` (moradores em domicílios particulares permanentes) soma **117.893** contra
> **118.767** oficiais, −874. **Não é erro de soma nem de junção:** as duas quantidades
> medem coisas diferentes — o total oficial inclui **domicílios improvisados e coletivos**,
> que `Var12` por definição não conta. Comparar as duas como se fossem a mesma grandeza
> produz uma discrepância que não existe.
>
> Ressalva adicional de 2000, do lado espacial:
>
> - a malha urbana de Bagé (`2000/malha/4301602.zip`, 127 setores) vem declarada em
>   **EPSG:32621 — UTM 21 NORTE**, hemisfério errado para Bagé: é erro de declaração no
>   `.prj`, não dado do sul projetado. **7 das 127 geometrias são inválidas**;
> - a malha rural (`rs_setores_censitarios.zip`, 47 setores em Bagé) vem **sem CRS declarado**;
> - o CRS tem de ser decidido e registrado **antes** de qualquer medição métrica;
> - as **tabelas de 2000 não foram lidas** no REVIA_BG: vêm só em `.XLS` legado (BIFF8) e
>   aquele ambiente não tinha leitor. Os arquivos estão guardados intactos; falta o leitor.
>

</details>

---

## Licença, e o que não foi possível confirmar

A licença registrada em `data/catalogo_fontes.csv` é a **declaração dos próprios
servidores que serviram estes arquivos**, conferida em 20/09/2026 (HTTP 200):

> "Todos os arquivos aqui disponíveis são públicos."
> — raiz de `https://ftp.ibge.gov.br/` e de `https://geoftp.ibge.gov.br/`

**O que não foi lido:** a página formal de termos de uso do IBGE
(`www.ibge.gov.br/acesso-informacao/acoes-e-programas/termos-de-uso.html`) respondeu
**HTTP 403** (desafio Cloudflare, com e sem cabeçalhos de navegador) em 20/09/2026.
A licença citada acima é a do servidor de download, **não** a dessa página, e nada foi
transcrito dela. Se a página formal declarar condição adicional — atribuição em formato
específico, restrição de uso comercial —, ela **ainda não foi conferida**, e
`autorizacao_fonte = true` nas nove linhas se apoia na declaração do FTP e na
prática já adotada para as demais fontes IBGE do acervo.

## Procedência

Os arquivos chegaram primeiro por **cópia** de
`~/projetos/rede_viaria_bage/dados/externos/censo/` (projeto REVIA_BG), que os baixou das
fontes oficiais do IBGE em 20/09/2026 navegando as listagens do FTP — nenhuma URL montada
por adivinhação. A cópia foi conferida arquivo a arquivo (sha256 origem = sha256 cópia) e
a origem saiu inalterada.

Em 22/09/2026 os 50 arquivos de dado foram movidos (sha256 conferido antes e depois) para
`data/raw/tabular/ibge/censo_<ano>/` (tabelas; documentação em `doc/`) e
`data/raw/vetor/ibge/censo_<ano>/` (malhas; `malha_com_atributos/` e `cnefe/` em 2022).
A malha territorial de setores 2022 do geoftp, que também veio na cópia, é hoje obtida por
`scripts/download/baixar_malhas_ibge.py`. Cada arquivo tem `.json` irmão com URL exata,
`Last-Modified` do servidor, data do download original e sha256; a lista fixa está em
`config/fontes_censo_ibge.yaml`, e `scripts/download/baixar_censo_ibge.py --verificar`
confere a origem sem baixar.

O registro da cópia original — `.json` irmãos antigos (com `origem_da_copia`),
`manifesto_copia_censo.json`, `FONTE.md` e `manifesto_censo_<ano>.json` do REVIA_BG — está,
sem edição, em `docs/procedencia/revia_bg_censo/`.

Script: `scripts/download/baixar_censo_ibge.py` (substitui `scripts/download/censo_revia_bg.py`).
