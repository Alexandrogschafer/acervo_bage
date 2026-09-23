# A03 — Resultados da subordinada 1: expansão ou adensamento

> *Quanto do crescimento é expansão e quanto é adensamento? Onde estão essas duas
> geografias, que densidade têm e quanta população as acompanhou?*

Medido por `scripts/s1_expansao_adensamento.py` (números em
`derivados/s1_caracterizacao.json`) e desenhado por `scripts/s1_figuras.py`. A camada de
trabalho é `saidas/s1_celulas_2010_2022.gpkg` e as figuras estão em `saidas/`. Nada disso
está conferido no mapa, e nada foi para `data/acervo/` nem para `data/geoportal/`.

Este documento **descreve**. Não tira conclusão de planejamento urbano.

---

## 1. O que foi medido, e como

**Unidade.** A unidade é a célula da grade estatística do IBGE (200 m no urbano, 1 km no
rural). Uma célula é de Bagé quando o **centroide** dela cai no município. É a mesma
regra do d03.

**Correção em relação ao d03: a grade não é a mesma nas duas edições.** Em 41 lugares
do município, uma célula de 1 km de 2010 aparece em 2022 como as **25 células de
200 m** que a compõem. A grade é aninhada, e o IBGE passou a gradear esses lugares na
resolução urbana. O d03 juntou as edições por `ID_UNICO` e tratou o que faltava como
zero. Com isso, a troca de resolução virou mudança no território:
- as filhas de 200 m entraram como "novas";
- a mãe de 1 km entrou como "extinta".

A conferência de geografia do d03 olhou só as 5.677 células de mesmo ID e por isso não
viu o aninhamento. Aqui, a comparação usa a **unidade harmonizada**: nos 41 lugares, a
célula de 1 km de 2010 é comparada com a soma das suas 25 filhas de 2022. O script
exige que:
- cada célula presente numa edição só esteja contida numa célula da outra;
- as filhas cubram a mãe (desvio máximo de área de 0,1 m², medido em ESRI:102033).

Se alguma dessas condições falhar, o script para.

| classe | d03 (junção por `ID_UNICO`) | das quais eram troca de resolução | **unidade harmonizada** |
| --- | ---: | ---: | ---: |
| nova | 573 | 224 | **355** |
| adensada | 568 | 0 | **590** |
| estável | 164 | 0 | **165** |
| esvaziada | 359 | 0 | **365** |
| extinta | 261 | 32 | **232** |

As 590 adensadas incluem 22 unidades harmonizadas. As 355 novas incluem 6.

**Classes**, sobre domicílios ocupados (2010: `DOM_OCU`; 2022: `TOTAL_DOM`):

| classe | regra |
| --- | --- |
| nova | sem domicílio em 2010, com domicílio em 2022 |
| adensada | tinha domicílio e ganhou |
| estável | tinha domicílio, variação nula |
| esvaziada | tinha domicílio e perdeu, mas ainda tem |
| extinta | tinha domicílio em 2010 e não tem em 2022 |

A camada de trabalho traz, por unidade: domicílios e moradores nos dois anos, variação
absoluta e relativa (a relativa é nula quando 2010 = 0), classe, resolução, área, distância
ao centro e fração da unidade dentro da área urbanizada de 2022.

**Referências declaradas**

| referência | definição |
| --- | --- |
| centro | Centro médio dos domicílios de 2010: centroides das unidades ponderados por domicílios de 2010 (EPSG:31981: x 776.002, y 6.530.803). Fica num setor urbano do distrito-sede (`430160205000033`). O `NM_BAIRRO` está vazio nos 199 setores de 2022, então não há nome de bairro. Sensibilidade: usando só as unidades de 200 m, o centro se desloca 0,50 km. |
| área urbanizada 2022 | IBGE, *Áreas Urbanizadas do Brasil 2022* (baixada nesta tarefa, pela lista fixa). Polígonos de Bagé com Tipo = "Área urbanizada", densa e pouco densa: 40 polígonos, 34,34 km². A unidade está **dentro** quando ≥ 50 % da sua área cai na área urbanizada. Sensibilidade: todos os tipos (inclui loteamento vazio e outros equipamentos urbanos), 67 polígonos, 36,83 km². |
| contiguidade | Critério rainha: unidades que compartilham aresta ou vértice, com tolerância de 1 m. |
| medidas | Distâncias em EPSG:31981; áreas em ESRI:102033. |

---

## 2. Conferência contra o total do município

| | grade (centroide no município) | município (d01) | diferença | % |
| --- | ---: | ---: | ---: | ---: |
| população 2010 | 114.910 | 116.794 | −1.884 | **−1,61 %** |
| domicílios 2010 | 37.908 | 38.504 | −596 | **−1,55 %** |
| população 2022 | 117.977 | 117.938 | +39 | +0,03 % |
| domicílios 2022 | 45.383 | 45.327 | +56 | +0,12 % |

A grade de 2010 fica abaixo do município. **Isso fica registrado, não corrigido.**

- Com a regra do centroide usada aqui, a diferença é de 1,6 % da população e dos
  domicílios.
- O "1,4 %" citado no dimensionamento (§ 3.2) é o da regra "qualquer célula que toca o
  município" (115.191 pessoas).
- Nas duas regras, a diferença é do dado de 2010 (agregação/desagregação do IBGE), não
  da borda.

Consequência: nas classes, os domicílios de 2010 estão subcontados em cerca de 1,5 %. As
variações de 2010 para 2022 herdam essa diferença.

A harmonização não muda os totais: 2010 e 2022 somam o mesmo que no d03, com saldo de
**+7.475 domicílios** e **+3.067 pessoas** na grade.

---

## 3. Tabela por classe

| classe | unidades | domicílios 2010 | domicílios 2022 | Δ domicílios | população 2010 | população 2022 | Δ população | moradores/dom. 2010 → 2022 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| nova | 355 | 0 | 1.884 | +1.884 | 0 | 4.604 | +4.604 | — → 2,44 |
| adensada | 590 | 19.768 | 29.983 | +10.215 | 60.806 | 78.217 | +17.411 | 3,08 → 2,61 |
| estável | 165 | 912 | 912 | 0 | 2.637 | 2.245 | −392 | 2,89 → 2,46 |
| esvaziada | 365 | 16.421 | 12.604 | −3.817 | 48.849 | 32.911 | −15.938 | 2,97 → 2,61 |
| extinta | 232 | 807 | 0 | −807 | 2.618 | 0 | −2.618 | 3,24 → — |
| **total** | **1.707** | **37.908** | **45.383** | **+7.475** | **114.910** | **117.977** | **+3.067** | 3,03 → 2,60 |

---

## 4. A resposta: quanto é expansão, quanto é adensamento

Ganho bruto de domicílios nas unidades que ganharam: **12.099**.

| origem | domicílios | % do ganho bruto |
| --- | ---: | ---: |
| unidades **novas** | 1.884 | **15,6 %** |
| unidades **adensadas** | 10.215 | 84,4 % |
| · adensadas de 200 m | 8.299 | 68,6 % |
| · adensadas de 1 km | 162 | 1,3 % |
| · adensadas de 1 km **que o IBGE passou a gradear em 200 m em 2022** | 1.754 | 14,5 % |

**Faixa da expansão: 15,6 % a 30,1 % do ganho bruto.**
- O limite inferior conta só as unidades novas.
- O superior soma a elas o ganho das 22 adensadas harmonizadas.
- Essas 22 são células de 1 km que já tinham domicílio em 2010 e onde o IBGE passou a
  gradear em 200 m. Dentro delas pode haver ocupação de área nova que a resolução de
  1 km de 2010 não permite separar do adensamento.

Pela junção do d03, a leitura era 40 % de expansão (5.709 domicílios em 573 células
novas), com 15.385 pessoas nas novas. **Harmonizada, a expansão fica entre 16 % e 30 %,
e as unidades novas somam 4.604 moradores.** Da diferença:
- 3.892 domicílios e 10.969 moradores estavam nas filhas de 200 m (224 delas com
  domicílio), que o d03 tratava como novas;
- no d03, as mães correspondentes de 1 km apareciam como extintas.

---

## 5. As geografias

### 5.1 Onde estão

| | novas (355) | adensadas (590) | extintas (232) |
| --- | ---: | ---: | ---: |
| peso usado | domicílios 2022 | domicílios 2022 | domicílios 2010 |
| distância ao centro, mediana das unidades | 17,96 km | 2,90 km | 9,86 km |
| distância ao centro, mediana ponderada por domicílio | **3,47 km** | **2,57 km** | **4,74 km** |
| p25 – p75 (unidades) | 5,4 – 39,0 km | 1,9 – 4,1 km | 4,2 – 40,8 km |
| **dentro** da área urbanizada 2022 (unidades / domicílios) | 25 / 968 | 442 / 26.790 | 9 / 37 |
| **fora** (unidades / domicílios) | 330 / 916 | 148 / 3.193 | 223 / 770 |
| % dos domicílios dentro | **51,4 %** | **89,4 %** | **4,6 %** |
| % dentro, com todos os tipos de área urbanizada | 54,0 % | 89,5 % | 5,2 % |
| unidades que tocam a área urbanizada | 72 | 512 | 38 |
| resolução (200 m / 1 km / 1 km harmonizada) | 90 / 259 / 6 | 496 / 72 / 22 | 90 / 139 / 3 |

Domicílios por faixa de distância ao centro:

| faixa | novas | adensadas | extintas |
| --- | ---: | ---: | ---: |
| 0–1 km | 0 | 2.809 | 7 |
| 1–2 km | 195 | 7.816 | 8 |
| 2–3 km | 597 | 8.588 | 188 |
| 3–4 km | 250 | 7.238 | 109 |
| 4–6 km | 365 | 2.896 | 128 |
| 6–10 km | 90 | 466 | 117 |
| ≥ 10 km | 387 | 170 | 250 |

**Leitura descritiva:**
- **Novas.** Duas populações de unidade. A maioria das unidades novas (259 de 355) é
  rural, de 1 km, com mediana de 1 domicílio, espalhada pelo município. Os domicílios,
  porém, se dividem ao meio:
  - 51 % em 25 unidades dentro da área urbanizada;
  - o restante nas 330 unidades de fora.
  Entre 1 e 6 km do centro estão 1.407 dos 1.884 domicílios novos.
  Nenhuma unidade nova está a menos de 1 km do centro.
- **Adensadas.** Concentram-se na cidade: 89 % dos domicílios dentro da área
  urbanizada, 88 % a menos de 4 km do centro.
- **Extintas.** São rurais: 95 % dos domicílios de 2010 fora da área urbanizada.
  115 das 232 unidades estão a 10 km ou mais do centro.

### 5.2 Contiguidade

| | novas | adensadas | extintas |
| --- | ---: | ---: | ---: |
| agrupamentos contíguos | 208 | 64 | 146 |
| unidades isoladas (agrupamento de 1) | 139 | 51 | 115 |
| agrupamentos de 2–4 / 5–9 / 10–49 / ≥ 50 unidades | 56 / 12 / 1 / 0 | 9 / 1 / 2 / 1 | 26 / 2 / 3 / 0 |
| maior agrupamento: unidades, domicílios | 12 un., 38 dom. | **481 un., 28.006 dom.** | 18 un., 203 dom. |
| % dos domicílios da classe no maior agrupamento | 2,0 % | **93,4 %** | 25,2 % |

Os 10 maiores agrupamentos de **novas** (unidades · domicílios · km²):

| unidades | domicílios | km² |
| ---: | ---: | ---: |
| 12 | 38 | 12,0 |
| 7 | 67 | 7,0 |
| 6 | 73 | 0,24 |
| 6 | 10 | 6,0 |
| 5 | 276 | 0,2 |
| 5 | 129 | 0,2 |
| 5 | 54 | 0,2 |
| 5 | 18 | 5,0 |
| 5 | 13 | 0,2 |
| 5 | 8 | 5,0 |

Os agrupamentos de 1 km (5–12 km²) têm poucos domicílios. Os de 200 m (0,2 km²)
concentram a maior parte: um só deles tem 276 domicílios.

- As **adensadas** formam uma mancha contínua: um agrupamento de 481 unidades, 37,5 km²,
  com 93 % dos domicílios da classe.
- As **novas** e as **extintas** são fragmentadas: a maioria dos agrupamentos tem uma
  unidade só.

### 5.3 Densidade de domicílios

Densidade = domicílios da classe / área da classe (km² em ESRI:102033), separada por
resolução. Somar 200 m com 1 km mistura escalas de ocupação diferentes.

| classe | resolução | unidades | km² | dom/km² 2010 | dom/km² 2022 | mediana dom/unidade 2010 → 2022 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| nova | 200 m | 90 | 3,60 | 0 | 388,9 | 0 → 2 |
| nova | 1 km (inclui harmonizadas) | 265 | 265,0 | 0 | 1,8 | 0 → 1 |
| adensada | 200 m | 496 | 19,84 | 918,2 | 1.336,5 | 33 → 50 |
| adensada | 1 km (inclui harmonizadas) | 94 | 94,0 | 16,5 | 36,9 | 2 → 4 |
| estável | 200 m | 44 | 1,76 | 429,5 | 429,5 | 3,5 → 3,5 |
| estável | 1 km | 121 | 121,0 | 1,3 | 1,3 | 1 → 1 |
| esvaziada | 200 m | 283 | 11,32 | 1.333,0 | 1.040,8 | 52 → 39 |
| esvaziada | 1 km (inclui harmonizadas) | 82 | 82,0 | 16,2 | 10,0 | 4 → 2 |
| extinta | 200 m | 90 | 3,60 | 114,2 | 0 | 2 → 0 |
| extinta | 1 km (inclui harmonizadas) | 142 | 142,0 | 2,8 | 0 | 1 → 0 |

Nas células urbanas (200 m):
- as novas chegam a 389 dom/km² em 2022, menos de um terço da densidade das adensadas
  (1.337);
- as adensadas partem de 918 dom/km² em 2010, abaixo das esvaziadas (1.333 em 2010);
- as esvaziadas eram as unidades mais densas de 2010.

### 5.4 Quantos moradores acompanharam cada classe

- **Novas:** +1.884 domicílios e **+4.604 moradores** (2,44 por domicílio).
- **Adensadas:** +10.215 domicílios e **+17.411 moradores**. Moradores por domicílio
  caíram de 3,08 para 2,61.
- **Esvaziadas:** −3.817 domicílios e **−15.938 moradores**. A perda de moradores é
  proporcionalmente maior que a de domicílios (−33 % contra −23 %).
- **Extintas:** −807 domicílios e −2.618 moradores.
- **Estáveis:** sem variação de domicílios, e mesmo assim −392 moradores.

---

## 6. Figuras

Todas em `saidas/`, fora do git, cada uma com `.json` irmão (pendente, não publicável).
Mapas em EPSG:31981, com escala, norte da quadrícula e fonte. A base é o limite municipal
e o **contorno da área urbanizada de 2022 do IBGE**.

| figura | área urbana | município inteiro |
| --- | --- | --- |
| classes | `s1_mapa_classes_urbano.png` | `s1_mapa_classes_municipio.png` |
| variação de domicílios | `s1_mapa_var_domicilios_urbano.png` | `s1_mapa_var_domicilios_municipio.png` |
| variação de população | `s1_mapa_var_populacao_urbano.png` | `s1_mapa_var_populacao_municipio.png` |

O que os mapas mostram, sem interpretar:
- a mancha azul (adensada) contínua na cidade, entremeada de esvaziadas no núcleo;
- as novas de 200 m na franja da área urbanizada;
- as novas e extintas de 1 km espalhadas pelo rural;
- um bloco de unidades de 1 km a leste da cidade que perderam domicílios (esvaziadas e
  extintas).

---

## 7. Ressalvas

1. **A grade de 2010 fica 1,6 % abaixo do município** (§ 2). Isso foi registrado e não
   corrigido.
2. **Resolução de 1 km:** numa unidade rural, "adensada" e "nova" dizem respeito a
   1 km². A faixa de 15,6–30,1 % (§ 4) é a medida dessa incerteza onde ela mais pesa.
3. **Não há perímetro urbano legal no acervo.** "Dentro/fora" e o contorno nos mapas são
   da *área urbanizada* do IBGE (2022), que é um mapeamento por imagem e não um limite
   legal. A escolha do tipo muda pouco (§ 5.1, sensibilidade).
4. **Centro** é uma definição estatística, o centro médio dos domicílios de 2010, e não o
   centro histórico. As distâncias são euclidianas, não por rede viária.
5. **Moradores:** `POP` (2010) e `TOTAL` (2022) são a população residente da célula;
   `DOM_OCU` e `TOTAL_DOM`, os domicílios ocupados. A leitura dos campos segue o d03 e o
   reconhecimento (§ 3.4).
6. **A camada de trabalho não está conferida.** Ela só vai para o acervo depois da
   conferência visual do responsável e da promoção (`scripts/utils/promover.py`).
7. **O d03 e o dimensionamento § 3.3 continuam com os números da junção por ID**
   (573 / 5.709 / 15.385). Eles não foram reescritos aqui, e a subordinada 1 do
   manifesto cita esses números.
