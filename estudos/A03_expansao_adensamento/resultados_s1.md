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
   legal. A escolha do tipo muda pouco (§ 5.1, sensibilidade). O perímetro legal **não será obtido
   nesta etapa** (§ 9).
4. **Centro** é uma definição estatística, o centro médio dos domicílios de 2010, e não o
   centro histórico. As distâncias são euclidianas, não por rede viária.
5. **Moradores:** `POP` (2010) e `TOTAL` (2022) são a população residente da célula;
   `DOM_OCU` e `TOTAL_DOM`, os domicílios ocupados. A leitura dos campos segue o d03 e o
   reconhecimento (§ 3.4).
6. **A camada de trabalho não está conferida.** Ela só vai para o acervo depois da
   conferência visual do responsável e da promoção (`scripts/utils/promover.py`).
7. **O d03 está SUPERADO** por `scripts/s1_expansao_adensamento.py` (docstring do
   `d03_grade.py`), e os números da junção por ID (573 / 5.709 / 15.385) foram
   corrigidos em 2026-09-23 no dimensionamento (§§ 3 e 5), na subordinada 1 e no
   `recorte_espacial` do manifesto e no README, com o texto antigo preservado em bloco
   de correção datado. Os equivalentes harmonizados do dimensionamento § 3.3 estão no
   § 8 abaixo. A troca de resolução é ressalva geral do acervo:
   `docs/ressalvas_censo_bage.md` § 7.

   *Texto anterior (até 2026-09-23):* "O d03 e o dimensionamento § 3.3 continuam com os
   números da junção por ID (573 / 5.709 / 15.385). Eles não foram reescritos aqui, e a
   subordinada 1 do manifesto cita esses números."

---

## 8. O dimensionamento § 3.3 na unidade harmonizada

Acrescentado em 2026-09-23, para substituir os números da junção por ID no
dimensionamento. Medido por `scripts/s1_expansao_adensamento.py` sobre as 1.707 unidades
com domicílio em algum dos dois anos, com as mesmas regras do d03. Números em
`derivados/s1_caracterizacao.json`, blocos `movimento_e_divergencia` e
`troca_de_resolucao_em_bage`.

*Até 2026-09-23 estes agregados eram medidos à mão sobre a camada de trabalho e não
estavam no JSON. Entraram no script no mesmo dia; na nova execução, todos os números
desta seção bateram com a saída, sem divergência.*

| | unidades | soma | mediana | p90 | máximo |
| --- | ---: | ---: | ---: | ---: | ---: |
| ganharam domicílios | 945 | +12.099 | 4 | 25 | 610 |
| perderam domicílios | 597 | −4.624 | 3 | 18 | 190 |
| ganharam população | 822 | +24.428 | 6,5 | 63 | 1.551 |
| perderam população | 819 | −21.361 | 10 | 66 | 779 |

Mediana, p90 e máximo das perdas são sobre o valor absoluto, como no d03.

- **Movimento bruto de domicílios:** +12.099 contra −4.624, para o mesmo saldo de
  **+7.475** — 16.723 de movimento, pouco mais de dois para um (o d03 dava 20.865, quase
  três para um).
- **Divergência de sinal:** **137 unidades (8,0 % das 1.707)** ganharam domicílios e
  perderam população, com +843 domicílios e −2.095 pessoas. O caminho inverso ocorre em
  7 unidades. O d03 dava 132 células (6,9 % de 1.925), +804 e −2.044. A subordinada 2 do
  manifesto foi corrigida para os números harmonizados em 2026-09-23.

**De onde vem a troca de resolução, medida nas duas edições como o IBGE as publica**
(leitura por `scripts/grade_estatistica.py`, cada edição recortada pelo centroide da
própria célula; bloco `troca_de_resolucao_em_bage`):
- as 41 células que o d03 contava "só em 2010" são as 41 mães de 1 km; as 1.025 "só em
  2022" são as 41 × 25 filhas de 200 m. Não havia diferença de cobertura;
- as mães tinham, em 2010, 2.380 domicílios e 7.945 pessoas (32 delas com domicílio);
- as filhas têm, em 2022, 3.892 domicílios e 10.969 pessoas (224 delas com domicílio).

---

## 9. Decisão: o perímetro urbano legal não será obtido nesta etapa

**Decidido pelo responsável em 2026-09-23.** O perímetro urbano legal de Bagé não será
obtido para a subordinada 1.

Motivo: a pergunta é onde o crescimento de domicílios se materializou no território.
- A **área urbanizada do IBGE** (2022) é **medida**: mapeamento da ocupação por imagem,
  com método publicado e o mesmo critério para todos os municípios, o que a torna
  comparável.
- O **perímetro urbano legal** é **norma**: diz onde a lei permite ou reconhece o uso
  urbano, e responde a outra pergunta (se a expansão ocorreu dentro ou fora do limite
  legal, isto é, sobre regulação, não sobre ocupação).

Consequência: "dentro/fora" continua sendo da área urbanizada (§ 1 e ressalva 3). Se uma
etapa futura perguntar pela relação entre expansão e regulação, a obtenção do perímetro
legal passa pelas regras do acervo (fonte documentada, sem URL por adivinhação).


---

## 10. Investigação: unidades extintas sem ocupação visível

Acrescentado em 2026-09-23. **Motivo:** na conferência visual, o responsável viu parte
das 232 unidades extintas sobre áreas sem ocupação visível em imagem de satélite.

**Esta seção investiga e não reclassifica.** A camada de trabalho e as classes não foram
alteradas: o script confere o `sha256_conteudo` da camada (`78a8800b…`) antes de ler.

- Script: `scripts/s1_extintas.py`.
- Números: `derivados/s1_extintas.json`.
- Apoio à conferência no mapa: `derivados/s1_extintas_unidades.gpkg`, fora do git. Tem
  as extintas e as novas, com as contagens do CNEFE e as medidas de vizinhança por
  unidade. É contagem de endereço por célula: não publicar.
- Duas fontes brutas entraram no manifesto: `ibge_cnefe2022` e
  `ibge_censo2010_malha_setores`.

### 10.1 Perfil das extintas

Domicílios ocupados de 2010. "Dentro" é a mesma regra do § 1: ≥ 50 % da área da unidade
na área urbanizada de 2022.

| grupo | unidades | domicílios 2010 | mediana | p90 | máx. | com 1 | com 2 | com 3 | ≤ 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **todas** | **232** | **807** | **1** | **7,9** | **57** | **140** | **24** | **20** | **200** |
| 200 m, dentro | 9 | 37 | 2 | 7,8 | 11 | 3 | 2 | 0 | 6 |
| 200 m, fora | 81 | 374 | 1 | 10,0 | 57 | 41 | 7 | 11 | 67 |
| 1 km, dentro | 0 | — | — | — | — | — | — | — | — |
| 1 km, fora (3 harmonizadas) | 142 | 396 | 1 | 5,9 | 19 | 96 | 15 | 9 | 127 |

- 140 das 232 extintas (60 %) tinham **um** domicílio em 2010, e 200 (86 %) tinham até
  cinco.
- Só 9 extintas estão dentro da área urbanizada, todas de 200 m.
- Moradores por domicílio em 2010: 3,24.

### 10.2 Teste de deslocamento

**Perda** é o `dom_10` da extinta. Nas vizinhas:
- **saldo** é a soma das variações de domicílios;
- **ganho bruto** é a soma só das variações positivas.

Vizinhança **rainha** é a unidade que toca a extinta (1 m). Vizinhança por **raio R** é a
unidade cujo centroide está a até R da borda da extinta.

O universo são as 5.718 unidades harmonizadas no município. Unidade sem domicílio nos
dois anos entra com variação 0. Vizinha de outro município não entra.

| vizinhança | resolução | extintas | saldo ≥ perda | 0 < saldo < perda | saldo = 0 | saldo < 0 | ganho bruto ≥ perda | com nova vizinha |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rainha | todas | 232 | 96 | 9 | 41 | 86 | 133 | 102 |
| raio 1 km | todas | 232 | 136 | 5 | 39 | 52 | 164 | 166 |
| raio 2 km | todas | 232 | 147 | 4 | 24 | 57 | 181 | 194 |
| rainha (= raio 1 km) | 1 km | 142 | 52 | 5 | 38 | 47 | 74 | 76 |
| raio 2 km | 1 km | 142 | 57 | 4 | 24 | 57 | 91 | 104 |
| rainha | 200 m | 90 | 44 | 4 | 3 | 39 | 59 | 26 |
| raio 1 km | 200 m | 90 | 84 | 0 | 1 | 5 | 90 | 90 |
| raio 2 km | 200 m | 90 | 90 | 0 | 0 | 0 | 90 | 90 |

**Distribuição do saldo nas extintas de 1 km, rainha** (p10 / p25 / mediana / p75 /
p90): −30,9 / −1 / 0 / 1,8 / 3.

**Nas extintas de 200 m, o raio não discrimina.** O raio de 1 km alcança em mediana
89,5 unidades, e o de 2 km, 236. A extinta fica então cercada pelo crescimento da
cidade, e o saldo ≥ perda sai quase sempre verdadeiro.

**Linha de base (1 km).** O "ganho ≥ perda" sozinho não diz nada: a perda típica é de 1
domicílio. A tabela compara as medidas que não dependem da perda em torno de três grupos
de unidades:

| unidades de 1 km | n | saldo das vizinhas ≥ 1 (rainha / 2 km) | com nova vizinha (rainha / 2 km) |
| --- | ---: | --- | --- |
| extintas | 142 | 40,1 % / 43,0 % | 53,5 % / 73,2 % |
| outras ocupadas (adensada, estável, esvaziada) | 297 | 48,5 % / 58,9 % | 53,9 % / 79,5 % |
| sem domicílio nos dois anos | 3.341 | 30,2 % / 46,1 % | 32,1 % / 57,2 % |

**Pares por permutação.** Se a extinção fosse o mesmo domicílio posto numa célula
vizinha, pares extinta–nova apareceriam **mais** que o acaso.

- Unidades: as 704 de 1 km com domicílio em algum ano.
- Acaso: 9.999 permutações das classes entre essas mesmas unidades, com semente fixa.

| par | vizinhança | observados | esperado (média) | p5–p95 | p (menos que o acaso) | p (mais que o acaso) |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| **extinta–nova** | rainha | **105** | 157,5 | 137–178 | **0,0001** | 1,0 |
| **extinta–nova** | centroides ≤ 2 km | **123** | 193,5 | 170–218 | **0,0001** | 1,0 |
| **extinta–nova** | centroides ≤ 5 km | **727** | 1.101,1 | 1.010–1.196 | **0,0001** | 1,0 |
| extinta–extinta | rainha | 64 | 42,0 | 31–54 | 0,997 | **0,003** |
| extinta–esvaziada | rainha | 67 | 48,7 | 37–61 | 0,993 | **0,010** |
| extinta–esvaziada | centroides ≤ 2 km | 85 | 59,9 | 47–74 | 0,998 | **0,003** |
| nova–nova | rainha | 122 | 146,4 | 125–168 | 0,032 | 0,97 |

**Leitura:**
- Extintas e novas são vizinhas **menos** do que o acaso, em todas as escalas testadas
  (1, 2 e 5 km).
- As extintas se agrupam com outras extintas e com esvaziadas. A perda é regional, não
  espelhada em ganho ao lado.
- Em torno das extintas de 1 km, a vizinhança ganha **menos** que em torno das outras
  unidades ocupadas.

### 10.3 CNEFE 2022 dentro das extintas

Os 228 endereços do CNEFE que caem nas 232 extintas:
- **domicílio particular:** 106;
- domicílio coletivo: 3;
- **estabelecimento agropecuário:** 82;
- outros: 37 (outras finalidades 33, edificação em construção 3, ensino 1).

Todos têm nível de geocodificação 1, isto é, a coordenada original do Censo 2022.

| extintas | 200 m | 1 km | total |
| --- | ---: | ---: | ---: |
| **com domicílio (particular ou coletivo) no CNEFE** | 6 | 56 | **62** |
| só com agropecuário ou outros | 15 | 8 | 23 |
| **sem nenhum endereço** | 69 | 78 | **147** |

- **62 extintas têm domicílio no CNEFE.** Em 50 delas, o CNEFE tem tantos domicílios
  quanto a grade tinha ocupados em 2010, ou mais.
- **Isso contradiz "sem domicílio", mas não "sem domicílio ocupado"**, que é a regra da
  classe (§ 1):
  - o CNEFE lista o domicílio particular ocupado ou não (vago, de uso ocasional);
  - a grade de 2022 conta só os ocupados.
  - Nas unidades de 1 km, a grade tem 79,0 % dos domicílios do CNEFE (4.928 de 6.240);
    nas de 200 m, 85,3 %.
  - Uma unidade rural com 1 domicílio no CNEFE e nenhum ocupado é, portanto, esperável.
- **Proporção com domicílio no CNEFE, pelo tamanho em 2010:**
  - extintas que tinham 1 domicílio: 38 de 140;
  - que tinham 2: 13 de 24;
  - que tinham 3: 5 de 20;
  - que tinham 4: 4 de 9;
  - que tinham 5: 0 de 7;
  - que tinham 6 ou mais: **2 de 32**.
  Quanto maior a extinta, mais raro é haver domicílio lá em 2022.
- **Limite do município.** 12 extintas tocam o limite, e 9 delas estão sem endereço.
  O CNEFE lido é só o de Bagé, então nessas 9 a conferência é incompleta.

### 10.4 A documentação da grade: sigilo e posicionamento do endereço rural

**Os documentos da grade não estão no repositório.** As notas metodológicas de 2022
(`Notas_metodologicas_grade_estatistica_2022.pdf`) e a metodologia de 2010
(`grade_estatistica.pdf`) foram lidas só no reconhecimento dos servidores. O resumo delas
está em `derivados/r_ftp_ibge.md`, Q2. Os arquivos da grade trazem só o histórico de
geoprocessamento (`.shp.xml`) e nada sobre sigilo ou posicionamento.

Documentos consultados, todos em `data/raw/`:
- `metodologia_censo_dem_2010.pdf`;
- `notas_tecnicas.pdf` (2010);
- `liv102168.pdf` (2022, *Características urbanísticas do entorno*);
- os dicionários do CNEFE e das coordenadas de 2022;
- `Leia_me_Comparabilidade_2010_2022.pdf`;
- o `.shp.xml` das duas grades.

| tema | 2010 | 2022 |
| --- | --- | --- |
| **supressão por sigilo na grade** | **Regra não encontrada nos documentos que temos.** A metodologia de 2010 (§ 1.4.3) diz que as tabelas não são desidentificadas, salvo as de Terras Indígenas. A regra "< 5 DPP" é da base por setor, não da grade. | **Regra não encontrada nos documentos que temos.** O resumo das notas (r_ftp_ibge.md) não menciona sigilo. |
| supressão, pelo dado | Nenhuma: 0 nulos; 234 células de 1 km e 86 de 200 m com **1** domicílio publicadas. | Nenhuma: 0 nulos; 296 células de 1 km e 141 de 200 m com **1** domicílio publicadas. |
| **posição do endereço rural** | O recenseador coletava a coordenada por GPS no PDA **nos setores rurais**. Sem sinal depois de duas tentativas, a entrevista seguia **sem coordenada** (metodologia 2010, cap. 4, "Preparo dos arquivos para a coleta"). O próprio IBGE registra "falhas de obtenção" de coordenadas sem indicador de controle (§ 11.5.2.2.1). O CNEFE 2010 tinha coordenada **só na área rural** (§ 1.4.3.6). | Coordenada coletada **"o mais próximo possível do acesso à unidade"**. A inválida é trocada pelo melhor dado disponível: coleta anterior, coordenada do questionário, outro endereço da edificação ou ponto médio da face (liv102168, "Coordenadas geográficas", p. 39–40). O CNEFE registra isso em `NV_GEO_COORD`, de 1 a 6 (dicionário). |
| como a grade usa a posição | **Não está nos documentos que temos.** O resumo em r_ftp_ibge.md diz que 2010 foi feita por agregação e desagregação (dasimetria, ponderação zonal), com um campo de método por célula. **Esse campo não existe nos arquivos baixados**, cujos campos são `ID_UNICO`, `nome_*`, `QUADRANTE`, `MASC`, `FEM`, `POP` e `DOM_OCU` (`.shp.xml`). Não sabemos onde a grade de 2010 pôs o domicílio rural sem coordenada, nem o domicílio de setor urbano, que não tinha coordenada. | Pelo resumo das notas: totalização direta dos microdados geocodificados pelo CNEFE, nos níveis 1 a 4, com os níveis 5 e 6 **excluídos**. |

Verificações no dado que complementam a documentação:
- **CNEFE 2022 de Bagé por nível de geocodificação:**
  - 58.158 no nível 1;
  - 4.273 no 2;
  - 262 no 3;
  - 86 no 4;
  - **só 3 nos níveis 5 e 6** (2 e 1).
  A exclusão dos níveis 5 e 6 não pesa em Bagé.
- **Centro dos setores rurais de 2010.** Se a grade de 2010 pusesse o domicílio sem
  coordenada no centro do setor, as extintas concentrariam esses pontos. Não
  concentram:
  - dos 36 setores rurais, **nenhum** tem o centroide numa extinta;
  - só 1 tem nela o ponto representativo.

### 10.5 Contraste: as novas

| novas | unidades | domicílios 2022 | mediana | p90 | máx. | com 1 | com 2 | com 3 | ≤ 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| todas | 355 | 1.884 | 1 | 5,0 | 266 | 212 | 67 | 26 | 320 |
| 200 m, dentro | 25 | 968 | 7 | 131,6 | 266 | 4 | 4 | 2 | 11 |
| 200 m, fora | 65 | 432 | 1 | 10,6 | 170 | 37 | 8 | 3 | 51 |
| 1 km, fora (6 harmonizadas) | 265 | 484 | 1 | 3,0 | 45 | 171 | 55 | 21 | 258 |

**O perfil das novas rurais é o espelho do das extintas:** mediana de 1 domicílio, e
171 das 265 unidades de 1 km com um só.

**A diferença está no ancoramento:**
- 351 das 355 novas têm domicílio no CNEFE 2022, com níveis de geocodificação 1 a 4
  (2.587 / 322 / 12 / 1).
- Em 221 delas, a grade tem exatamente o número de domicílios do CNEFE.
- As 4 novas sem nenhum endereço **tocam o limite do município**. O domicílio delas
  deve estar no CNEFE do município vizinho, que não foi lido.
- **Do lado de 2022, portanto, a nova rural corresponde a pontos do CNEFE.** "Nova sem
  ocupação visível" significaria que o próprio ponto do CNEFE está fora da construção.
  A regra de 2022 permite isso: coordenada "no acesso à unidade", e numa propriedade
  rural o acesso pode ficar longe da casa.
- **Isso não se mede aqui:** só a imagem responde. A camada de apoio traz as 265 novas
  de 1 km para essa conferência.

**Onde as extintas caíam em 2010**, pela situação do setor de 2010 que contém o
centroide da unidade:

| | setor rural 2010 | setor urbano 2010 |
| --- | --- | --- |
| extintas de 1 km | 142 unidades (78 sem endereço), 396 dom. | — |
| extintas de 200 m | 34 (28 sem endereço), 67 dom. | **56 (41 sem endereço), 344 dom.** |
| novas de 1 km | 265 (4 sem endereço) | — |
| novas de 200 m | 43 (0 sem endereço) | 47 (0 sem endereço) |

- **Extintas de 200 m em setor urbano de 2010.** São 56 unidades e 344 domicílios,
  43 % dos 807. O domicílio de setor urbano **não tinha coordenada** em 2010 (§ 10.4),
  então a posição dele na grade de 2010 veio de alguma alocação que não conhecemos.
- **Maior agrupamento de extintas** (18 unidades de 1 km, 203 domicílios):
  - 15 das 18 unidades estão sem nenhum endereço no CNEFE 2022;
  - o agrupamento cai quase todo no **setor rural 430160205000136** de 2010 (situação 8);
  - 11 das 18 unidades tinham de 10 a 19 domicílios em 2010, todas com 3,6 a 3,9
    moradores por domicílio. A média do setor em 2010 era de 3,61.
- **O setor 136 inteiro:**
  - 31 extintas, com 229 domicílios em 2010, 27 delas sem endereço;
  - no agregado de 2010, o setor tinha **494 DPP**;
  - a grade de 2010 põe **968** domicílios em unidades com centroide nele. A atribuição
    por centroide mistura setores vizinhos na borda, então esse número indica, não
    prova.
- **Segundo maior agrupamento:** 10 unidades de 200 m e 111 domicílios nos setores
  urbanos 053 e 054; 9 dessas unidades estão sem endereço.

### 10.6 Conclusão: o que os números sustentam

| causa candidata | sustentada? | por quê |
| --- | --- | --- |
| **deslocamento para a vizinha** (o mesmo domicílio posto em célula ao lado numa das edições) | **não** | Pares extinta–nova ficam **abaixo** do acaso a 1, 2 e 5 km (105 contra 158 esperados na rainha; p = 0,0001 para "menos"). A vizinhança das extintas ganha menos que a das outras unidades ocupadas. |
| **supressão por sigilo** na grade | **não** | Nenhuma edição tem nulo, e as duas publicam centenas de células com 1 domicílio. Nenhum documento que temos traz regra de sigilo para a grade. |
| **posicionamento por setor ou localidade** | **não** | Todos os 228 endereços nas extintas estão no nível 1, e o município tem só 3 endereços nos níveis 5 e 6. Nenhum centroide de setor rural de 2010 cai numa extinta. |
| **desocupação real, com a construção de pé** (vaga ou de uso ocasional em 2022) | **sim, em 62 unidades** | 106 domicílios particulares e 3 coletivos no CNEFE, com nenhum ocupado na grade de 2022. Em 1 km, a grade tem 79 % do CNEFE. Nessas unidades a imagem deveria mostrar construção. |
| **posição de 2010 fora do lugar** (domicílio real, contado no setor, mas posto em célula onde não estava) | **compatível, não comprovado**, nas 170 extintas sem domicílio no CNEFE (147 sem nenhum endereço e 23 só com agropecuário ou outros) | Em 2022 não há domicílio nessas unidades, o que bate com a imagem. O lado frágil é 2010: o domicílio urbano não tinha coordenada, e o rural podia ficar sem ela, com alocação não documentada nos arquivos que temos. O maior bloco (setor 136) tem 11 de 18 unidades com 10 a 19 domicílios, razão moradores/domicílio próxima da média do setor e 15 de 18 unidades sem endereço em 2022. |
| **desaparecimento real** (construção demolida ou abandonada até sumir) | **compatível, não comprovado**, nas mesmas 170 | O agrupamento de extintas com esvaziadas acima do acaso é o que a despovoação rural produz. Os números de 2022 não separam isto da posição errada de 2010. |

**Em resumo:**
- **Não é deslocamento entre vizinhas.**
- **62 extintas são desocupação real:** a construção existe e o domicílio estava vago ou
  era de uso ocasional em 2022. A classe está certa nelas. Se a imagem não mostra
  construção nessas 62, o que falha é a posição do ponto do CNEFE.
- **As outras 170 concentram 634 dos 807 domicílios** (as 147 sem nenhum endereço).
  Nelas, os números separam a pergunta mas não a respondem:
  - 2022 confirma a ausência;
  - a dúvida é se 2010 estava certo.
  - Os indícios de alocação de 2010 são o bloco do setor 136 e os 344
    domicílios de setor urbano de 2010, que não tinham coordenada.
  - O teste que decide é **imagem de ~2010**: se houve construção onde a grade de 2010
    pôs domicílios.

**Tratamento.** Como o teste de deslocamento deu negativo, não há proposta de tratamento
de deslocamento. Proposta para decisão do responsável, sem nada aplicado:
1. **Conferência por imagem de ~2010** (histórico do Google Earth ou mosaico da época):
   - começar pelos dois maiores agrupamentos (setor rural 136; setores urbanos 053 e
     054), que somam 314 dos 807 domicílios;
   - depois, uma amostra das 147 sem endereço.
   - Pelo resultado, a causa de cada extinta fica documentada unidade a unidade.
2. **Obter a documentação da grade** que falta (`grade_estatistica.pdf` de 2010 e as
   notas de 2022), pela listagem do servidor. A regra de alocação de 2010 decide a
   leitura das 170. Os arquivos não foram baixados nesta tarefa.
3. **Sensibilidade, a registrar, sem mudar a classe.** As extintas afetam só o lado da
   perda: as 147 sem endereço somam 634 dos 4.624 domicílios de perda bruta (13,7 %).
   A faixa da expansão (§ 4) usa só ganhos, mas depende do zero de 2010 nas novas. Se
   a posição de 2010 é frágil no rural, as novas de 1 km (484 domicílios) também são:
   sem elas, a faixa iria de 15,6–30,1 % para **11,6–26,1 %**. É a faixa a declarar
   até o teste por imagem.

**Ressalvas desta seção:**
- O CNEFE não distingue ocupado de vago.
- A imagem de satélite não foi usada aqui: é a conferência do responsável.
- A atribuição unidade → setor de 2010 é pelo centroide da unidade.
- A conferência do CNEFE é incompleta nas unidades que cruzam o limite.
