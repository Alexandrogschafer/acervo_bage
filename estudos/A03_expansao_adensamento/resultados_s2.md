# A03 — Resultados da subordinada 2: onde domicílio e população divergem

> *Onde domicílio e população andam em direções opostas? [...] Verificar se essas
> unidades formam área contígua (centro? bairros antigos?) ou estão dispersas.*
> (manifesto, subordinada 2)

**Em andamento.** Este documento traz a primeira caracterização, feita em 2026-09-23
depois da conferência visual do responsável (`resultados_s1.md` § 12.1). A subordinada
não está fechada.
- Script: `scripts/s2_divergencia.py`.
- Números: `derivados/s2_divergencia.json`.
- A camada é `saidas/s1_celulas_2010_2022.gpkg`, com o `sha256_conteudo` (`f323c4ba…`)
  conferido antes de ler.
- **Nada foi reclassificado.** Este documento descreve e não tira conclusão de
  planejamento urbano.

**Objeto.** As **137 unidades** da grade harmonizada que ganharam domicílio e perderam
população entre 2010 e 2022: +843 domicílios e −2.095 pessoas (`resultados_s1.md`
§ 8).
- O cenário é o adotado, com o setor de 2010 430160205000136 à parte. Nenhuma das 137
  está nele.
- "Urbana" e "rural" aqui são **geográficos**, nunca o rótulo de situação do setor
  (manifesto, `recorte_espacial`):
  - **urbana** é a unidade de 200 m;
  - **rural** é a de 1 km, incluídas as harmonizadas.
- O centro é o do `resultados_s1.md` § 1.

---

## 1. Dispersa ou contígua

**A conferência visual** (2026-09-23) viu a divergência **dispersa pela cidade, não
contígua**: as urbanas menores, espalhadas.

**A medida confirma a dispersão em extensão e acrescenta uma concentração:**

| | valor |
| --- | ---: |
| agrupamentos contíguos (rainha, 1 m) | 59 |
| unidades isoladas | **40** |
| agrupamentos de 2 a 4 unidades (34 unidades) | 13 |
| agrupamentos de 5 ou mais unidades | **6, com 63 das 137 unidades** |
| maior agrupamento | 21 unidades |

Os cinco maiores agrupamentos:

| unidades | domicílios 2010 | Δ domicílios | Δ população | distância ao centro (mediana) | rumo |
| ---: | ---: | ---: | ---: | ---: | --- |
| 21 | 1.134 | +146 | −261 | 1,7 km | noroeste |
| 18 | 1.115 | +106 | −348 | 1,9 km | oeste |
| 8 | 538 | +32 | −120 | 0,9 km | oeste |
| 6 | 250 | +38 | −112 | 0,5 km | sudeste |
| 5 | 273 | +32 | −92 | 4,4 km | sul |

**Contra o acaso.** Só uma adensada pode divergir, porque a nova não tem população em
2010. Por isso o acaso é a permutação do rótulo "divergente" entre as 586 adensadas
(9.999 permutações, semente fixa).
- Pares contíguos divergente–divergente: **95 observados**, contra 59,7 esperados
  (p5–p95 de 48 a 72).
- **p = 0,0001** para "mais que o acaso".

**Leitura.**
- **A divergência é difusa na cidade.** As 123 urbanas vão de 0,1 a 4,8 km do centro
  e estão em todos os oito rumos: 22 a noroeste, 20 a oeste, 18 a sudoeste, 16 ao
  sul, 16 a sudeste, 13 a nordeste, 12 ao norte e 6 a leste.
  - Não há uma mancha única. Dois terços dos agrupamentos têm uma unidade só.
  - É o que a conferência viu. **A redução do tamanho do domicílio é fenômeno difuso
    no tecido urbano**, não de um bairro.
- **Mas não é aleatória.** Entre as adensadas, as divergentes são vizinhas umas das
  outras mais do que o acaso daria.
  - Quase metade (63) está em 6 agrupamentos de 5 ou mais unidades.
  - Os dois maiores somam 39 unidades, a oeste e a noroeste, a cerca de 2 km do
    centro.
  - A leitura "não contíguas" vale para o conjunto, não para eles.
  - **Conferência preparada** (2026-09-23), por `scripts/s2_agrupamentos.py`:

    | agrupamento | unidades | onde | domicílios 2010 → 2022 | moradores 2010 → 2022 | razão agregada |
    | --- | ---: | --- | --- | --- | --- |
    | 1 | 21 | 1,7 km ao norte do centro (a maior parte das unidades no setor noroeste) | 1.134 → 1.280 | 3.501 → 3.240 | 3,09 → 2,53 |
    | 2 | 18 | 1,9 km a oeste | 1.115 → 1.221 | 3.371 → 3.023 | 3,02 → 2,48 |

    - Todas as 39 unidades são de 200 m; 21 e 17 estão na área urbanizada densa do
      IBGE.
    - A lista por unidade (domicílios, moradores e razão nos dois anos, com o número
      usado na figura) está em `derivados/s2_agrupamentos_divergencia.json` e, em
      tabela, em `derivados/s2_agrupamentos_divergencia.csv`.
    - As figuras de detalhe são `saidas/s2_detalhe_agrupamento_1.png` e `_2.png`.
    - **Sem imagem de fundo:** o acervo não tem imagem de satélite, e trazer uma
      seria fonte nova, com licença e procedência a registrar. O fundo é vetorial:
      ruas (faces de logradouro de 2010), área urbanizada de 2022 (densa e pouco
      densa) e as demais unidades. Para ver sobre a imagem, abrir
      `saidas/s2_agrupamentos_divergencia.gpkg` no QGIS, como na conferência de
      2026-09-23.

---

## 2. As unidades rurais

A conferência contou **5 unidades rurais e 6 grandes rurais junto à borda urbana**.
Pela geografia medida (distância à área urbanizada de 2022 do IBGE):

| grupo | unidades | domicílios 2010 → 2022 | moradores 2010 → 2022 | onde |
| --- | ---: | --- | --- | --- |
| **rural (1 km) junto à borda**, a menos de 1 km da área urbanizada | **6** (5 harmonizadas + 1) | 97 → 140 | 349 → 294 | 4,2 a 6,1 km do centro; 3 ao sul, 1 a leste, 1 ao norte, 1 a noroeste |
| **rural (1 km) remota**, a 1 km ou mais | **8** | 22 → 31 | 83 → 61 | 12 a 64 km do centro; 3 a oeste, 3 a nordeste, 1 a sudoeste, 1 a sudeste |
| urbana (200 m) | 123 | 7.076 → 7.867 | 21.834 → 19.816 | 0,1 a 4,8 km; 119 dentro da área urbanizada |

- **As 6 junto à borda conferem com as "6 grandes rurais"** da conferência.
  - 5 delas são mães harmonizadas: células de 1 km de 2010 que o IBGE passou a gradear
    em 200 m em 2022, porque tocam setor urbano de 2022.
  - Três tocam a área urbanizada, e as outras estão a 43, 179 e 192 m dela.
  - A maior (1KME4988N7863, ao sul) vai de 52 para 76 domicílios e de 189 para 151
    moradores.

  | unidade | resolução | domicílios | moradores | distância ao centro | rumo | à área urbanizada |
  | --- | --- | --- | --- | ---: | --- | ---: |
  | 1KME4994N7869 | 1 km (2022 em 200 m) | 12 → 14 | 34 → 30 | 4,2 km | leste | 43 m |
  | 1KME4990N7864 | 1 km (2022 em 200 m) | 3 → 4 | 12 → 8 | 4,9 km | sul | 179 m |
  | 1KME4991N7864 | 1 km (2022 em 200 m) | 11 → 18 | 43 → 41 | 5,1 km | sul | toca |
  | 1KME4988N7874 | 1 km (2022 em 200 m) | 10 → 15 | 43 → 40 | 5,8 km | norte | toca |
  | 1KME4984N7871 | 1 km | 9 → 13 | 28 → 24 | 5,9 km | noroeste | 192 m |
  | 1KME4988N7863 | 1 km (2022 em 200 m) | 52 → 76 | 189 → 151 | 6,1 km | sul | toca |

- **As rurais remotas: a conferência estimou 5, a medida deu 8.** Registrado em
  2026-09-23, com o critério de cada uma:

  | | quantas | critério |
  | --- | ---: | --- |
  | conferência visual do responsável | **5** | estimativa a olho, no QGIS sobre imagem de satélite, das unidades rurais divergentes afastadas da cidade |
  | medida (`scripts/s2_divergencia.py`) | **8** | unidade de 1 km divergente, fora do setor 136, a 1 km ou mais da área urbanizada de 2022 do IBGE (distância da borda da unidade, EPSG:31981) |

  - As 8 são as que a figura 7 deixa fora do recorte urbano (`resultados_s1.md` § 6).
  - Três delas ficam a 61–64 km, no extremo nordeste do município; é provável que
    tenham ficado fora da vista da conferência. Isto é hipótese, não foi conferido.
  - A diferença fica registrada, sem correção de nenhum dos dois lados.
  - Todas têm de 1 a 7 domicílios. Juntas, ganharam 9 domicílios e perderam 22
    moradores.

---

## 3. Razão moradores/domicílio: convergência ou esvaziamento

Unidades ocupadas nos dois anos. O "restante" são as ocupadas não divergentes. A razão
da cidade (cenário adotado) é **3,017 em 2010 e 2,591 em 2022**. O teste é a
permutação do rótulo entre as unidades do grupo (9.999 permutações).

| | unidades | mediana 2010 | mediana 2022 | agregada 2010 → 2022 | % acima da cidade em 2010 | queda mediana |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| **urbanas divergentes** | 123 | **3,13** | **2,52** | 3,09 → 2,52 | 68,3 % | 0,61 |
| urbanas, restante | 698 | 3,06 | 2,68 | 2,99 → 2,61 | 54,3 % | 0,40 |
| **rurais divergentes** | 14 | **4,00** | **2,00** | 3,63 → 2,08 | 78,6 % | 1,64 |
| rurais, restante | 270 | 2,50 | 2,00 | 3,10 → 2,72 | 24,8 % | 0,50 |

| diferença de medianas (divergentes − restante) | 2010 | 2022 |
| --- | --- | --- |
| urbanas | +0,07 (p = 0,043, divergentes acima) | **−0,16** (p = 0,0002, divergentes abaixo) |
| rurais | **+1,50** (p = 0,0005, divergentes acima) | 0,00 (sem diferença) |

**Leitura:**
- **Rurais: convergência.** As 14 partiam de uma razão muito acima do resto (mediana 4,0
  contra 2,5) e chegaram ao mesmo 2,0.
  - 11 das 14 partiam acima da razão da cidade, e 9 terminam mais perto dela.
  - É compatível com o domicílio rural numeroso que se divide. O ganho é de 1 a 2
    domicílios nas remotas e de 1 a 24 nas junto à borda.
- **Urbanas: as duas coisas.** As divergentes partiam só um pouco acima (3,13 contra
  3,06, no limite da significância) e **terminam abaixo** do resto (2,52 contra 2,68).
  - A queda mediana é de 0,61, contra 0,40 no resto.
  - Por unidade:
    - 58 partiam acima da cidade e terminam mais perto dela. É **convergência**.
    - 26 partiam acima e terminam mais longe dela do que partiram.
    - 39 partiam na razão da cidade ou abaixo. É **esvaziamento**: o domicílio já
      pequeno ficou menor.
  - Não há um mecanismo único: a convergência explica menos da metade das urbanas.

---

## 4. A área consolidada mais densa

A conferência notou **poucas divergentes no miolo central mais denso**. A medida é
feita em quatro recortes, sobre as 123 urbanas. O esperado é o que as divergentes
teriam na zona se estivessem nela na mesma proporção das adensadas de 200 m.

| recorte | divergentes na zona | % das divergentes | % das adensadas | esperado |
| --- | ---: | ---: | ---: | ---: |
| área urbanizada **densa** do IBGE (≥ 50 % da unidade) | 112 | 91,1 % | 77,8 % | 95,7 |
| quartil superior de domicílios em 2010 (≥ 59 por unidade) | 57 | 46,3 % | 21,8 % | 26,8 |
| **miolo:** até 1 km do centro | **22** | 17,9 % | 8,3 % | 10,2 |
| até 1,5 km do centro | 37 | 30,1 % | 18,8 % | 23,1 |

**Leitura.** Em número absoluto, são poucas no miolo: 22 das 123 a até 1 km do centro.
**Em proporção, estão acima do esperado em todos os recortes.**
- No miolo, 22 contra 10,2 esperadas.
- Nas unidades mais densas de 2010, 57 contra 26,8.
- A impressão visual de "poucas" vem do tamanho pequeno do miolo, não da ausência. Das
  82 unidades de 200 m ocupadas em 2010 a até 1 km do centro, 22 são divergentes.
- Isso é coerente com o § 3: a divergência urbana está na área consolidada e densa de
  2010, onde a razão partia um pouco mais alta.

---

## 5. A unidade rural grande isolada a leste

É **1KME4994N7869**, a divergente de 1 km junto à borda mais a leste do centro: a
4,2 km, a leste, e a 43 m da área urbanizada de 2022, sem parte dentro dela. Não toca
nenhuma outra divergente.

| | 2010 | 2022 |
| --- | ---: | ---: |
| domicílios ocupados | 12 | 14 |
| moradores | 34 | 30 |
| moradores por domicílio | 2,83 | 2,14 |

- É **mãe harmonizada**. Em 2022 o IBGE a gradeou em 200 m, porque ela toca um setor
  urbano de 2022.

**O que há nela segundo o CNEFE 2022:** 36 endereços, todos no nível 1 de
geocodificação (a coordenada original).

| espécie | endereços |
| --- | ---: |
| domicílio particular (todos "casa") | 21 |
| estabelecimento agropecuário | 11 |
| estabelecimento de outras finalidades | 3 |
| edificação em construção | 1 |

- **Localidades:** Quebrachinho (33 endereços) e Prado Velho (3).
- **Setores de 2022:** 430160205000160 (rural, 34 endereços) e 430160205000162
  (urbano, 2). O setor urbano é o que fez o IBGE subdividir a célula.
- A grade de 2022 conta 14 domicílios ocupados para 21 domicílios no CNEFE. O CNEFE
  lista também o vago e o de uso ocasional (`resultados_s1.md` § 10.3).
- **Leitura.** É um núcleo rural de casas e estabelecimentos agropecuários encostado
  na borda leste da cidade: 11 estabelecimentos para 21 domicílios. Ganhou 2
  domicílios e perdeu 4 moradores.

---

## 6. O que fica em aberto

- A resposta da subordinada ainda não está escrita. Faltam:
  - o fechamento da pergunta "centro? bairros antigos?", com o que os §§ 1 e 4 mediram;
  - a conferência visual dos dois agrupamentos maiores, já preparada (§ 1).
- A diferença entre as 5 rurais remotas da conferência e as 8 medidas fica registrada
  (§ 2), sem correção.
- **Ressalva herdada da subordinada 1** (`resultados_s1.md` § 12). Em 2010, o
  domicílio urbano está na face repartida por extensão. A divergência usa domicílios e
  população de 2010, e a posição deles tem essa incerteza. O reposicionamento do § 12
  não foi aplicado à população, então o efeito dele sobre as 137 não está medido.

---

## 7. Bairros e loteamentos dos dois agrupamentos (interpretação)

> **Origem dos nomes.** `data/externos/bairros_loteamentos_bage/bairros_loteamentos_bage.gpkg`
> é material **revisado pelo responsável a partir do geobage** (Prefeitura de Bagé),
> **sem autorização de republicação** (`pode_publicar=false`, fora do git). Serve para
> **nomear e interpretar no texto**, não para publicar camada nem mapa. Não está no
> manifesto: se estivesse, a regra do mais restritivo bloquearia a publicação do estudo.

*Feito em 2026-09-24 por `scripts/i01_bairros_loteamentos.py`. Números em
`derivados/i01_bairros_loteamentos.json`, bloco `s2_agrupamentos_divergencia`. A lista
por unidade está em `derivados/i01_bairros_loteamentos_unidades.csv`, fora do git.*

- **A camada.** Uma camada só, com 114 polígonos (EPSG:31981). Bairros, vilas e
  loteamentos estão lado a lado, num mosaico sem hierarquia.
  - Não há campo de tipo nem data de aprovação. Por isso não há período de loteamento
    a relatar.
  - O "tipo" das tabelas é só o que o nome declara (prefixo LOTEAMENTO, BAIRRO ou
    VILA).
- **Critério.** Cada unidade vai para o polígono com a **maior área de interseção**. A
  parte da unidade fora de todos os polígonos concorre como "(fora da camada)".
  - A interseção é feita no CRS de produção, e a área é medida no ESRI:102033.
- **As figuras não mudam.** Seguem com a grade, a área urbanizada do IBGE e o fundo
  vetorial. Bairro e loteamento entram como texto, não como camada.

**Agrupamento 1** (21 unidades, 1.134 domicílios em 2010):

| bairro ou loteamento | tipo pelo nome | unidades | % das unidades | domicílios 2010 | % dos domicílios |
| --- | --- | ---: | ---: | ---: | ---: |
| SÃO JOÃO | sem tipo no nome | 5 | 23,8 % | 302 | 26,6 % |
| VILA SANTA TECLA | vila | 4 | 19,0 % | 278 | 24,5 % |
| SÃO JORGE | sem tipo no nome | 3 | 14,3 % | 177 | 15,6 % |
| VILA SÃO BERNARDO | vila | 3 | 14,3 % | 127 | 11,2 % |
| BAIRRO LARANJEIRAS | bairro | 3 | 14,3 % | 110 | 9,7 % |
| SÃO SEBASTIÃO | sem tipo no nome | 1 | 4,8 % | 66 | 5,8 % |
| VILA PETRÓPOLIS 1 | vila | 1 | 4,8 % | 46 | 4,1 % |
| (fora da camada; toca VILA SANTA TECLA) | — | 1 | 4,8 % | 28 | 2,5 % |

**Agrupamento 2** (18 unidades, 1.115 domicílios em 2010):

| bairro ou loteamento | tipo pelo nome | unidades | % das unidades | domicílios 2010 | % dos domicílios |
| --- | --- | ---: | ---: | ---: | ---: |
| CENTRO | sem tipo no nome | 8 | 44,4 % | 565 | 50,7 % |
| VILA ALCIDES ALMEIDA | vila | 3 | 16,7 % | 190 | 17,0 % |
| VILA OPERÁRIA | vila | 2 | 11,1 % | 125 | 11,2 % |
| VILA MINGOTE PAIVA | vila | 2 | 11,1 % | 75 | 6,7 % |
| LOTEAMENTO VICENTE DE PAULO/VILA BRASIL | loteamento | 1 | 5,6 % | 67 | 6,0 % |
| VILA ALMEIDA | vila | 1 | 5,6 % | 66 | 5,9 % |
| (fora da camada; toca VILA OPERÁRIA) | — | 1 | 5,6 % | 27 | 2,4 % |

- **As células de 200 m cortam os polígonos.** 11 das 21 unidades do agrupamento 1 e 7
  das 18 do agrupamento 2 tocam mais de um polígono. Em 1 e 3 delas, respectivamente, o
  polígono atribuído tem menos da metade da área da unidade.
  - O nome vale para o conjunto, não para a célula.
- **Leitura, só para nomear:**
  - o **agrupamento 1** está no arco São João – São Jorge – Laranjeiras – São
    Sebastião, com as vilas Santa Tecla, São Bernardo e Petrópolis 1;
  - o **agrupamento 2** está na borda oeste do polígono CENTRO, que é grande (548 ha),
    e nas vilas Alcides Almeida, Operária, Mingote Paiva e Almeida.
  - São **bairros e vilas antigos**, não loteamentos recentes. Só uma das 39 unidades
    cai num polígono chamado de loteamento.
  - Isso dá nome à pergunta do manifesto ("centro? bairros antigos?"), mas não a fecha:
    a camada não tem data e não mede idade.
- **Rumo.** O campo `orientacao` da camada, que é do responsável, põe os polígonos do
  agrupamento 1 a NORTE e NORDESTE. O § 1 diz noroeste, pelo rumo das unidades a partir
  do centro médio dos domicílios de 2010. As duas referências são diferentes, e a
  diferença fica registrada, sem correção.

---

## 8. Período de ocupação dos dois agrupamentos (interpretação)

> **Origem não redistribuível.** `data/externos/revia_bg/evolucao_urbana/` é a cópia
> (REVIA_BG, versão `evolucao_urbana_evo_v1`, sha256 fixado por componente) dos
> polígonos convertidos da prancha 03/18 "Condicionantes – Evolução Urbana" do dossiê
> de tombamento do **IPHAN** (SICG, 2009). A licença não está registrada, e o REVIA_BG
> diz **"não redistribuir os polígonos"** (`pode_publicar=false`, fora do git).
> - Serve para **DATAR e interpretar no texto**, não para publicar camada nem mapa.
> - Não está no manifesto, como a camada de bairros do § 7.
> - As figuras não mudam.
> - **Tudo o que este parágrafo afirma é interpretação.**

*Feito em 2026-09-24 por `scripts/i02_evolucao_urbana.py`. Números em
`derivados/i02_evolucao_urbana.json`, bloco `s2_agrupamentos_divergencia`. A lista por
unidade está em `derivados/i02_evolucao_urbana_unidades.csv`, fora do git.*

- **Incrementos.** Os polígonos do mapa são cumulativos até 1960, e os dois últimos são
  manchas destacadas. O incremento de cada período é o polígono dele menos a união dos
  anteriores. É o critério do REVIA_BG.
  - Incrementos, em hectares: déc. 1820, 23,6; metade do séc. XIX, 188,7; início do
    séc. XX, 266,2; 1938, 1.682,2; 1960, 1.188,0; 1970, 433,1; 2001, 389,0.
- **Critério.** Cada unidade vai para o incremento com a **maior área de interseção**.
  A parte fora de todos concorre como "fora do traçado mapeado até 2001". Em empate,
  vence o período mais antigo.
  - A interseção é feita em EPSG:31981, e a área é medida no ESRI:102033.
- **Borda sem data firme — decisão do responsável, 2026-09-24.**
  - O REVIA_BG registra que o polígono de 1938 é **generalizado**. Ele tem 551,9 ha que
    o polígono de 1960 não cobre.
  - A unidade atribuída a 1938 que tem metade ou mais da própria área nessa parte **não
    é datada "até 1938"**. Ela vai para **borda sem data firme**, uma categoria
    separada das datações firmes.
  - O período pela maior área continua na lista por unidade.

**Agrupamento 1** (21 unidades, 1.134 domicílios em 2010):

| período de ocupação | unidades | % das unidades | domicílios 2010 | % dos domicílios |
| --- | ---: | ---: | ---: | ---: |
| *datação firme* | | | | |
| 1938 | 2 | 9,5 % | 88 | 7,8 % |
| 1960 | 7 | 33,3 % | 457 | 40,3 % |
| 1970 | 10 | 47,6 % | 489 | 43,1 % |
| *sem datação firme* | | | | |
| borda sem data firme | 0 | — | 0 | — |
| fora do traçado mapeado até 2001 | 2 | 9,5 % | 100 | 8,8 % |

**Agrupamento 2** (18 unidades, 1.115 domicílios em 2010):

| período de ocupação | unidades | % das unidades | domicílios 2010 | % dos domicílios |
| --- | ---: | ---: | ---: | ---: |
| *datação firme* | | | | |
| metade do séc. XIX | 2 | 11,1 % | 168 | 15,1 % |
| início do séc. XX | 2 | 11,1 % | 160 | 14,3 % |
| 1938 | 11 | 61,1 % | 580 | 52,0 % |
| *sem datação firme* | | | | |
| borda sem data firme | 3 | 16,7 % | 207 | 18,6 % |
| fora do traçado mapeado até 2001 | 0 | — | 0 | — |

- **Qualidade da atribuição.**
  - Agrupamento 1: 6 unidades tocam mais de um período, e nenhuma foi atribuída com
    menos da metade da área.
  - Agrupamento 2: 7 tocam mais de um período, e 1 foi atribuída com menos da metade.
  - Nenhuma unidade dos dois agrupamentos está inteiramente fora dos polígonos.

### 8.1 Resultado (interpretação): o encolhimento do domicílio não depende da idade do bairro

**Os dois agrupamentos da divergência são de épocas diferentes.**
- O **agrupamento 1** é **periferia de 1960–1970**. Tem 17 das 21 unidades nesses dois
  incrementos, com **83 % dos domicílios de 2010** (946 de 1.134). Nada nele é anterior
  a 1938.
- O **agrupamento 2** é **cidade de até 1938**. Tem 15 das 18 unidades datadas
  firmemente até 1938, com **81 % dos domicílios** (908 de 1.115):
  - 52 % no incremento de 1938;
  - 29 % no traçado do séc. XIX e do início do séc. XX.
  - As outras 3 unidades (19 %) são borda sem data firme. **Nenhuma** é posterior a
    1938.
  - Antes da decisão sobre a borda, o incremento de 1938 somava 70 % (§ 8, versão
    anterior). Os 18 pontos de diferença são as 3 unidades da borda.

**E ainda assim convergem para a mesma razão moradores/domicílio.** Pelo § 1:
- o agrupamento 1 vai de **3,09 a 2,53**;
- o agrupamento 2 vai de **3,02 a 2,48**;
- os dois terminam em cerca de **2,5 moradores por domicílio**, abaixo da cidade (2,59
  em 2022).

**Leitura: o encolhimento domiciliar é transversal à idade do tecido urbano.** Ele não
é efeito de uma geração de bairros.
- Um tecido anterior a 1938, no centro e nas vilas antigas, e uma periferia de
  1960–1970 chegam ao mesmo domicílio pequeno em 2022.
- Isso é compatível com uma mudança na composição do domicílio que atravessa a cidade.
  Não é compatível com um ciclo de vida próprio de um conjunto de bairros da mesma
  época.
- Com o § 7: "bairros antigos" vale para o agrupamento 2. Para o agrupamento 1, o
  "antigo" é de meio século, não do núcleo histórico.

**Ressalvas.**
- É **interpretação**: a datação vem de fonte **não redistribuível** e entra só no
  texto.
- São dois agrupamentos. O resultado mostra que a idade do tecido não separa os dois;
  não mostra que ela nunca importe.
