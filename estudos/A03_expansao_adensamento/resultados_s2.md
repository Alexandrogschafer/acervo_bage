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
  - *Proposta:* olhar esses dois agrupamentos no mapa na próxima conferência. A
    leitura "não contíguas" vale para o conjunto, não para eles.

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

- **As rurais remotas são 8, não 5.** São as 8 que a figura 7 deixa fora do recorte
  (`resultados_s1.md` § 6). Três delas ficam a 61–64 km, no extremo nordeste do
  município. A diferença para a contagem da conferência não foi resolvida aqui.
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
  - a decisão sobre olhar os dois agrupamentos maiores no mapa (§ 1).
- A diferença entre as "5 unidades rurais" da conferência e as 8 remotas medidas (§ 2).
- **Ressalva herdada da subordinada 1** (`resultados_s1.md` § 12). Em 2010, o
  domicílio urbano está na face repartida por extensão. A divergência usa domicílios e
  população de 2010, e a posição deles tem essa incerteza. O reposicionamento do § 12
  não foi aplicado à população, então o efeito dele sobre as 137 não está medido.
