# A03 — Resultados da subordinada 1: expansão ou adensamento

> *Quanto do crescimento é expansão e quanto é adensamento? Onde estão essas duas
> geografias, que densidade têm e quanta população as acompanhou?*

Medido por `scripts/s1_expansao_adensamento.py` (números em
`derivados/s1_caracterizacao.json`) e desenhado por `scripts/s1_figuras.py`. A camada de
trabalho é `saidas/s1_celulas_2010_2022.gpkg` e as figuras estão em `saidas/`. A camada e
as figuras tiveram **conferência visual do responsável em 2026-09-23** (§ 12), sem
promoção. Nada foi para `data/acervo/` nem para `data/geoportal/`. *(Até 2026-09-23:
"Nada disso está conferido no mapa".)*

Este documento **descreve**. Não tira conclusão de planejamento urbano.

> **Números adotados (decisão do responsável, 2026-09-23): setor 430160205000136 À PARTE.**
> - O setor rural de 2010 `430160205000136` fica fora dos números principais: 47
>   unidades, 968 domicílios de 2010.
>   - Ele concentra as 4 células com assinatura de desagregação da grade de 2010.
>   - Tem 31 das 232 extintas (§ 10.6).
> - **Números principais:**
>   - expansão entre **16,6 % e 25,6 %** do ganho bruto de **11.372** domicílios;
>   - **201 extintas**, com **578** domicílios;
>   - perda bruta de **4.248**.
> - Os números com **todas as unidades** ficam ao lado, como sensibilidade: 15,6–30,1 %;
>   232 extintas com 807 domicílios; perda bruta de 4.624.
> - O fechamento está no § 11.
> - As geografias do § 5 e as sete figuras do § 6 foram refeitas no cenário adotado em
>   2026-09-23.
> - O § 8 continua sobre todas as unidades, com o cenário adotado anotado.

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

*Esta tabela usa todas as unidades, porque compara a harmonização com o d03. Os números
adotados, com o setor de 2010 430160205000136 à parte, estão nos §§ 3, 4 e 11: 354
novas, 586 adensadas e 201 extintas.*

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

**Desde 2026-09-23** a camada traz também o campo booleano **`a_parte_setor_136`**,
verdadeiro nas 47 unidades do setor rural de 2010 430160205000136, declarado à parte no
cenário adotado (§ 11).
- O campo é gravado por `scripts/s1_expansao_adensamento.py`, a partir da lista de
  `derivados/s1_desagregacao_2010.json`. O `s1_desagregacao_2010.py` confere que a
  marca é igual à lista que ele calcula.
- O campo não muda classe.
- O `sha256_conteudo` passou de `78a8800b…` para `f323c4ba…`.
- A camada segue **pendente**, sem promoção.

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

**Cenário adotado: setor 430160205000136 à parte** (§§ 10.6 e 11). Números em
`derivados/s1_desagregacao_2010.json`, bloco `efeito_nos_numeros_da_subordinada_1`.

| classe | unidades | domicílios 2010 | domicílios 2022 | Δ domicílios | população 2010 | população 2022 | Δ população | moradores/dom. 2010 → 2022 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| nova | 354 | 0 | 1.883 | +1.883 | 0 | 4.602 | +4.602 | — → 2,44 |
| adensada | 586 | 19.296 | 28.785 | +9.489 | 59.119 | 74.743 | +15.624 | 3,06 → 2,60 |
| estável | 163 | 910 | 910 | 0 | 2.630 | 2.240 | −390 | 2,89 → 2,46 |
| esvaziada | 356 | 16.156 | 12.486 | −3.670 | 47.923 | 32.594 | −15.329 | 2,97 → 2,61 |
| extinta | **201** | **578** | 0 | −578 | 1.762 | 0 | −1.762 | 3,05 → — |
| **total** | **1.660** | **36.940** | **44.064** | **+7.124** | **111.434** | **114.179** | **+2.745** | 3,02 → 2,59 |

| o setor 136, à parte | unidades | domicílios 2010 | domicílios 2022 | Δ domicílios | população 2010 | população 2022 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nova / adensada / estável / esvaziada / extinta | 1 / 4 / 2 / 9 / 31 | 968 | 1.319 | +351 | 3.476 | 3.798 |

**Sensibilidade: todas as unidades.** Até 2026-09-23 esta era a tabela principal, e
continua valendo como sensibilidade.

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

**Cenário adotado (setor 430160205000136 à parte).** Ganho bruto de domicílios nas
unidades que ganharam: **11.372**.

| origem | domicílios | % do ganho bruto |
| --- | ---: | ---: |
| unidades **novas** | 1.883 | **16,6 %** |
| unidades **adensadas** | 9.489 | 83,4 % |
| · adensadas de 200 m | 8.299 | 73,0 % |
| · adensadas de 1 km | 162 | 1,4 % |
| · adensadas de 1 km **que o IBGE passou a gradear em 200 m em 2022** (18) | 1.028 | 9,0 % |

**Faixa da expansão adotada: 16,6 % a 25,6 % do ganho bruto.**
- O limite inferior conta só as unidades novas.
- O superior soma a elas o ganho das 18 adensadas harmonizadas. São células de 1 km que
  já tinham domicílio em 2010 e onde o IBGE passou a gradear em 200 m. Dentro delas
  pode haver ocupação de área nova que a resolução de 1 km de 2010 não permite separar
  do adensamento.
- As 4 adensadas do setor 136 também são mães harmonizadas, e uma delas é a célula de
  borda de 299 → 909 domicílios. Tirá-las baixa o limite superior em 4,5 pontos.

**Sensibilidade: todas as unidades.** Ganho bruto de 12.099:

| origem | domicílios | % do ganho bruto |
| --- | ---: | ---: |
| unidades **novas** | 1.884 | 15,6 % |
| unidades **adensadas** | 10.215 | 84,4 % |
| · adensadas de 200 m | 8.299 | 68,6 % |
| · adensadas de 1 km | 162 | 1,3 % |
| · adensadas de 1 km que o IBGE passou a gradear em 200 m em 2022 (22) | 1.754 | 14,5 % |

Faixa de 15,6 % a 30,1 %.

> *Corrigido em 2026-09-23. O texto anterior dava como principal a tabela de
> sensibilidade acima e "**Faixa da expansão: 15,6 % a 30,1 % do ganho bruto.**", com
> o limite superior sobre as 22 adensadas harmonizadas.*

**A comparação com o d03 é com todas as unidades,** porque mede só o efeito da troca de
resolução. Pela junção do d03, a leitura era 40 % de expansão: 5.709 domicílios em 573
células novas, com 15.385 pessoas nelas. **Harmonizada, a expansão fica entre 16 % e
30 %, e as unidades novas somam 4.604 moradores.** Da diferença:
- 3.892 domicílios e 10.969 moradores estavam nas filhas de 200 m (224 delas com
  domicílio), que o d03 tratava como novas;
- no d03, as mães correspondentes de 1 km apareciam como extintas.

---

## 5. As geografias

*Refeito em 2026-09-23 no **cenário adotado** (setor 430160205000136 à parte, § 11)
por `scripts/s1_geografias.py`, com as mesmas funções do `s1_expansao_adensamento.py`.
Números em `derivados/s1_geografias.json`: bloco `adotado`, e `todas_as_unidades` como
sensibilidade. O centro é o do § 1, sem mudança.*

- *Na sensibilidade, os números com todas as unidades são os de
  `derivados/s1_caracterizacao.json`, com uma exceção: a ordem de um empate na lista
  dos 10 maiores agrupamentos de adensadas, que o § 5 não publica.*
- *O texto anterior, com todas as unidades, está nas colunas de sensibilidade e no bloco
  de correção no fim da seção.*

### 5.1 Onde estão

| | novas (354) | adensadas (586) | extintas (201) | sensibilidade: todas as unidades (novas / adensadas / extintas) |
| --- | ---: | ---: | ---: | --- |
| peso usado | domicílios 2022 | domicílios 2022 | domicílios 2010 | — |
| distância ao centro, mediana das unidades | 18,08 km | 2,90 km | 11,06 km | 17,96 km ; 2,90 km ; 9,86 km |
| distância ao centro, mediana ponderada por domicílio | **3,47 km** | **2,50 km** | **3,89 km** | **3,47 km** ; **2,57 km** ; **4,74 km** |
| p25 – p75 (unidades) | 5,4 – 39,2 km | 1,9 – 4,1 km | 4,1 – 43,3 km | 5,4 – 39,0 km ; 1,9 – 4,1 km ; 4,2 – 40,8 km |
| **dentro** da área urbanizada 2022 (unidades / domicílios) | 25 / 968 | 442 / 26.790 | 8 / 36 | 25 / 968 ; 442 / 26.790 ; 9 / 37 |
| **fora** (unidades / domicílios) | 329 / 915 | 144 / 1.995 | 193 / 542 | 330 / 916 ; 148 / 3.193 ; 223 / 770 |
| % dos domicílios dentro | **51,4 %** | **93,1 %** | **6,2 %** | **51,4 %** ; **89,4 %** ; **4,6 %** |
| % dentro, com todos os tipos de área urbanizada | 54,0 % | 93,2 % | 6,9 % | 54,0 % ; 89,5 % ; 5,2 % |
| unidades que tocam a área urbanizada | 72 | 508 | 33 | 72 ; 512 ; 38 |
| resolução (200 m / 1 km / 1 km harmonizada) | 90 / 258 / 6 | 496 / 72 / 18 | 75 / 124 / 2 | 90 / 259 / 6 ; 496 / 72 / 22 ; 90 / 139 / 3 |

Domicílios por faixa de distância ao centro (cenário adotado; entre parênteses, com todas as unidades):

| faixa | novas | adensadas | extintas |
| --- | ---: | ---: | ---: |
| 0–1 km | 0 | 2.809 | 7 |
| 1–2 km | 195 | 7.816 | 8 |
| 2–3 km | 597 | 8.588 | 186 (188) |
| 3–4 km | 250 | 6.329 (7.238) | 106 (109) |
| 4–6 km | 365 | 2.607 (2.896) | 97 (128) |
| 6–10 km | 90 | 466 | 17 (117) |
| ≥ 10 km | 386 (387) | 170 | 157 (250) |

**Leitura descritiva (cenário adotado):**
- **Novas.** Tirar o setor 136 muda uma unidade nova só.
  - Há duas populações de unidade. A maioria das novas (258 de
    354) é rural, de 1 km, com mediana de 1 domicílio, espalhada pelo município.
  - Os domicílios se dividem ao meio: 51,4 % em
    25 unidades dentro da área urbanizada, e o
    restante nas 329 de fora.
  - Entre 1 e 6 km do centro estão 1.407 dos 1.883 domicílios novos. Nenhuma unidade
    nova está a menos de 1 km do centro.
- **Adensadas.** Concentram-se na cidade:
  **93,1 %** dos domicílios dentro da
  área urbanizada (89,4 % com todas as unidades) e 88,7 % a menos de 4 km do centro.
  - A diferença vem das 4 mães harmonizadas do setor 136, fora da área urbanizada, que
    somavam 1.198 domicílios em 2022.
- **Extintas.** 93,8 % dos domicílios de 2010 estão fora da área urbanizada. Mas **não
  são só rurais**, e isso o cenário adotado mostrou (ver o quadro abaixo).
  - 106 das 201 unidades estão a 10 km ou mais do centro.
  - Sem o setor 136, a mediana ponderada cai de 4,74 para
    **3,89 km**.
  - Quase todos os 229 domicílios extintos do setor estavam a 4 km ou mais do centro:
    31 entre 4 e 6 km, 100 entre 6 e 10 km e 93 a 10 km ou mais (faixas acima).

**Parte do esvaziamento é urbano de borda, não só rural.** É uma leitura que o cenário
adotado trouxe, e o anterior escondia. Números em `derivados/s1_geografias.json`, bloco
`extintas_urbano_de_borda`.
- O setor 136 é **rural** e concentrava 229 dos 807 domicílios extintos. Com ele, as
  extintas pareciam um fenômeno do campo:
  - mediana ponderada da distância ao centro de 4,74 km;
  - maior agrupamento de 18 unidades de 1 km.
- Sem ele:
  - a mediana cai para **3,89 km**;
  - o maior agrupamento passa a ser **urbano**: 10 unidades de 200 m, 111 domicílios,
    nos setores urbanos 053 e 054 de 2010 (§ 5.2).

| extintas | cenário adotado (201; 578 dom.) | todas as unidades (232; 807 dom.) |
| --- | ---: | ---: |
| domicílios de 2010 em **setor urbano de 2010** (56 unidades de 200 m) | **344 (59,5 %)** | 344 (42,6 %) |
| domicílios de 2010 em setor rural de 2010 | 234 (40,5 %) | 463 (57,4 %) |
| domicílios em unidades dentro ou tocando a área urbanizada de 2022 | 225 | 230 |
| a até 500 m dela | 171 | 202 |
| de 500 m a 1 km | 15 | 52 |
| **até 1 km da área urbanizada, somados** | **411 (71,1 %)** | 484 (60,0 %) |
| a mais de 2 km | 163 (28,2 %) | 270 (33,5 %) |

- As 344 extintas de setor urbano de 2010 são as mesmas nos dois cenários. O que muda
  é o peso delas: **passam a ser a maioria** dos domicílios extintos.
- 26 dessas unidades, com 152 domicílios, ficam fora da área urbanizada de 2022, mas a
  menos de 1 km dela. É a borda da cidade que tinha domicílio em 2010 e não tem em
  2022.
- **Ressalva:** em 2010, o domicílio de setor urbano entrou na grade pela face de
  quadra, repartida ao longo da face, e não pelo endereço (§ 10.4). A posição fina
  dessas extintas de borda tem, portanto, a incerteza da grade de 2010.
  - Das 56, 41 não têm nenhum endereço no CNEFE 2022 (§ 10.5).
  - A leitura "urbano de borda" vale para o conjunto; célula a célula, é indício.
- **As 56 extintas urbanas são dois fenômenos** (§ 12; classes mantidas por decisão
  do responsável em 2026-09-23). Números em `derivados/s1_faces_2010.json`, bloco
  `extintas_urbanas_por_fenomeno`.

  | extintas urbanas (56; 344 dom.) | unidades | domicílios 2010 | dentro ou tocando a área urbanizada | fora dela, a menos de 1 km |
  | --- | ---: | ---: | --- | --- |
  | **esvaziamento medido:** faces que perderam os endereços | **23** | **244** | 13 un. / 150 dom. | 11 un. / 117 dom. |
  | **indício de deslocamento por repartição da face** | **29** | **95** | 16 un. / 62 dom. | 13 un. / 33 dom. |
  | outras (sem face residencial de 2010, ou com endereço de 2022 na própria unidade) | 4 | 5 | 2 un. / 3 dom. | 2 un. / 2 dom. |

  - O "urbano de borda" que é **esvaziamento medido** são os 244 domicílios. Os 95 do
    deslocamento não são perda: são indício de que a repartição de 2010 pôs na
    célula casas que estão na vizinha.
  - O agrupamento 053/054 pertence ao esvaziamento medido: 8 das 10 unidades, 105 dos
    111 domicílios (as outras 2, com 6 domicílios, são de deslocamento).

### 5.2 Contiguidade

| | novas | adensadas | extintas | sensibilidade: todas as unidades (novas / adensadas / extintas) |
| --- | ---: | ---: | ---: | --- |
| agrupamentos contíguos | 207 | 65 | 146 | 208 ; 64 ; 146 |
| unidades isoladas (agrupamento de 1) | 138 | 51 | 118 | 139 ; 51 ; 115 |
| agrupamentos de 2–4 / 5–9 / 10–49 / ≥ 50 unidades | 56 / 12 / 1 / 0 | 10 / 1 / 2 / 1 | 25 / 2 / 1 / 0 | 56 / 12 / 1 / 0 ; 9 / 1 / 2 / 1 ; 26 / 2 / 3 / 0 |
| maior agrupamento: unidades, domicílios | 12 un., 38 dom. | 475 un., 26.729 dom. | 10 un., 111 dom. | 12 un., 38 dom. ; 481 un., 28.006 dom. ; 18 un., 203 dom. |
| % dos domicílios da classe no maior agrupamento | 2,0 % | 92,9 % | 19,2 % | 2,0 % ; 93,4 % ; 25,2 % |

Os 10 maiores agrupamentos de **novas** são os mesmos nos dois cenários (unidades · domicílios · km²):

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

- As **adensadas** formam uma mancha contínua: um agrupamento de 475 unidades,
  31,5 km², com 92,9 % dos domicílios da classe.
- As **novas** e as **extintas** são fragmentadas: a maioria dos agrupamentos tem uma
  unidade só.
- Sem o setor 136, o maior agrupamento de extintas deixa de ser o bloco rural (18
  unidades, 203 domicílios).
  - Passa a ser o urbano dos setores 053 e 054: 10 unidades de 200 m, 111 domicílios,
    19,2 % dos da classe. É o esvaziamento urbano de borda do § 5.1.
  - Pelo § 12, é **esvaziamento medido**: 8 das 10 unidades (105 domicílios) estão em
    faces que perderam os endereços. A conferência visual do responsável (sem
    ocupação, ruínas de uma casa) é consistente com isso.

### 5.3 Densidade de domicílios

Densidade = domicílios da classe / área da classe (km² em ESRI:102033), separada por
resolução. Somar 200 m com 1 km mistura escalas de ocupação diferentes. Cenário
adotado; entre parênteses, os valores com todas as unidades, quando diferem.

| classe | resolução | unidades | km² | dom/km² 2010 | dom/km² 2022 | mediana dom/unidade 2010 → 2022 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| nova | 200 m | 90 | 3,60 | 0 | 388,9 | 0 → 2 |
| nova | 1 km (inclui harmonizadas) | 264 (265) | 264,0 (265,0) | 0 | 1,8 | 0 → 1 |
| adensada | 200 m | 496 | 19,84 | 918,2 | 1.336,5 | 33 → 50 |
| adensada | 1 km (inclui harmonizadas) | 90 (94) | 90,0 (94,0) | 12,0 (16,5) | 25,2 (36,9) | 2 → 4 |
| estável | 200 m | 42 (44) | 1,68 (1,76) | 448,8 (429,5) | 448,8 (429,5) | 4 → 4 (3,5 → 3,5) |
| estável | 1 km | 121 | 121,0 | 1,3 | 1,3 | 1 → 1 |
| esvaziada | 200 m | 283 | 11,32 | 1.333,0 | 1.040,8 | 52 → 39 |
| esvaziada | 1 km (inclui harmonizadas) | 73 (82) | 73,0 (82,0) | 14,6 (16,2) | 9,6 (10,0) | 3 → 2 (4 → 2) |
| extinta | 200 m | 75 (90) | 3,00 (3,60) | 131,3 (114,2) | 0 | 2 → 0 |
| extinta | 1 km (inclui harmonizadas) | 126 (142) | 126,0 (142,0) | 1,5 (2,8) | 0 | 1 → 0 |

Nas células urbanas (200 m), que o setor 136 quase não toca:
- as novas chegam a 389 dom/km² em 2022, menos de um terço da densidade das adensadas
  (1.337);
- as adensadas partem de 918 dom/km² em 2010, abaixo das esvaziadas (1.333 em 2010);
- as esvaziadas eram as unidades mais densas de 2010.

Nas de 1 km, tirar o setor 136 muda a densidade:
- a das adensadas cai de 16,5 → 36,9 para 12,0 → 25,2 dom/km²;
- a das extintas de 2010 cai de 2,8 para 1,5 dom/km².

### 5.4 Quantos moradores acompanharam cada classe

Cenário adotado (tabela do § 3); entre parênteses, com todas as unidades.

- **Novas:** +1.883 domicílios e **+4.602 moradores**, 2,44 por domicílio (+1.884 e
  +4.604).
- **Adensadas:** +9.489 domicílios e **+15.624 moradores** (+10.215 e +17.411).
  Moradores por domicílio caíram de 3,06 para 2,60.
- **Esvaziadas:** −3.670 domicílios e **−15.329 moradores** (−3.817 e −15.938). A perda
  de moradores é proporcionalmente maior que a de domicílios (−32 % contra −23 %).
- **Extintas:** −578 domicílios e −1.762 moradores (−807 e −2.618).
- **Estáveis:** sem variação de domicílios, e mesmo assim −390 moradores (−392).

> *Corrigido em 2026-09-23.* Até esta data o § 5 era medido só sobre todas as unidades.
> Os números antigos estão nas colunas de sensibilidade acima e em
> `derivados/s1_caracterizacao.json`, e seguem válidos como sensibilidade. As
> leituras antigas que mudaram:
> - adensadas "89 % dos domicílios dentro da área urbanizada" e agrupamento de
>   "481 unidades, 37,5 km², 93 %";
> - extintas "95 % fora", "115 das 232 unidades a 10 km ou mais" e maior agrupamento de
>   "18 un., 203 dom.";
> - moradores por classe com todas as unidades (§ 5.4 anterior).

---

## 6. Figuras

*Refeitas em 2026-09-23 no cenário adotado (versão `s1-v2` no `.json` irmão), por
`scripts/s1_figuras.py`.*

Todas estão em `saidas/`, fora do git, cada uma com `.json` irmão (pendente, não
publicável). Mapas em EPSG:31981, com escala, norte da quadrícula e fonte. A base é o
limite municipal e o **contorno da área urbanizada de 2022 do IBGE**.

**O setor 136 em todas as figuras:**
- As 47 unidades do setor de 2010 430160205000136 aparecem **hachuradas e contornadas**,
  na cor da sua classe ou faixa.
- A legenda explica o que isso significa: à parte, porque a grade de 2010 foi
  desagregada ali, e fora das contagens.
- As contagens da legenda são as do cenário adotado.

| figura | área urbana | município inteiro |
| --- | --- | --- |
| classes | `s1_mapa_classes_urbano.png` | `s1_mapa_classes_municipio.png` |
| variação de domicílios | `s1_mapa_var_domicilios_urbano.png` | `s1_mapa_var_domicilios_municipio.png` |
| variação de população | `s1_mapa_var_populacao_urbano.png` | `s1_mapa_var_populacao_municipio.png` |
| **divergência de sinal (subordinada 2)** | `s1_mapa_divergencia_urbano.png` | — |

**A sétima figura, nova em 2026-09-23,** é o primeiro mapa da subordinada 2: as 137
unidades que ganharam domicílios e perderam moradores (+843 / −2.095).
- Recorte urbano, com as demais unidades ocupadas em cinza de contexto.
- 8 unidades rurais ficam fora do recorte (+9 domicílios, −22 moradores), e o próprio
  mapa diz isso.
- Nenhuma das 137 está no setor 136.

O que os mapas mostram, sem interpretar:
- a mancha azul (adensada) contínua na cidade, entremeada de esvaziadas no núcleo;
- as novas de 200 m na franja da área urbanizada;
- as novas e extintas de 1 km espalhadas pelo rural;
- um bloco de unidades de 1 km a leste da cidade que perderam domicílios (esvaziadas e
  extintas). É o setor 136, hachurado.
- na figura 7, as unidades da divergência de sinal se espalham pelo tecido urbano,
  sem formar mancha.
  - *Isto é descrição do mapa. Se elas formam área contígua é pergunta da subordinada
    2, ainda não medida.* Medido em 2026-09-23, em [`resultados_s2.md`](resultados_s2.md).
    Há 40 isoladas, mas também 6 agrupamentos de 5 ou mais unidades, e mais pares
    contíguos que o acaso.

---

## 7. Ressalvas

1. **A grade de 2010 fica 1,6 % abaixo do município** (§ 2). Isso foi registrado e não
   corrigido.
2. **Resolução de 1 km:** numa unidade rural, "adensada" e "nova" dizem respeito a
   1 km². A faixa de 16,6–25,6 % (§ 4, cenário adotado; 15,6–30,1 % com todas as
   unidades) é a medida dessa incerteza onde ela mais pesa.
3. **Não há perímetro urbano legal no acervo.** "Dentro/fora" e o contorno nos mapas são
   da *área urbanizada* do IBGE (2022), que é um mapeamento por imagem e não um limite
   legal. A escolha do tipo muda pouco (§ 5.1, sensibilidade). O perímetro legal **não será obtido
   nesta etapa** (§ 9).
4. **Centro** é uma definição estatística, o centro médio dos domicílios de 2010, e não o
   centro histórico. As distâncias são euclidianas, não por rede viária.
5. **Moradores:** `POP` (2010) e `TOTAL` (2022) são a população residente da célula;
   `DOM_OCU` e `TOTAL_DOM`, os domicílios ocupados. A leitura dos campos segue o d03 e o
   reconhecimento (§ 3.4).
6. **A camada de trabalho não está promovida.** A conferência visual do responsável foi
   feita em 2026-09-23 (§ 12.1) e está registrada fora do bloco de conferência. A camada
   só vai para o acervo depois da promoção (`scripts/utils/promover.py`). *(Até
   2026-09-23: "não está conferida".)*
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

**Cenário adotado (setor 136 à parte, § 11).** Números em
`derivados/s1_desagregacao_2010.json`, `efeito_nos_numeros_da_subordinada_1`,
calculados pela mesma função `movimento_e_divergencia`. Na coluna da direita, a
sensibilidade com todas as unidades.

| | unidades | soma | mediana | p90 | máximo | sensibilidade: unidades / soma / mediana / p90 / máximo |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ganharam domicílios | 940 | **+11.372** | 4 | 25 | 579 | 945 / +12.099 / 4 / 25 / 610 |
| perderam domicílios | 557 | **−4.248** | 3 | 18 | 190 | 597 / −4.624 / 3 / 18 / 190 |
| ganharam população | 817 | +22.639 | 6 | 62,4 | 1.453 | 822 / +24.428 / 6,5 / 63 / 1.551 |
| perderam população | 777 | −19.894 | 10 | 65 | 779 | 819 / −21.361 / 10 / 66 / 779 |

Mediana, p90 e máximo das perdas são sobre o valor absoluto, como no d03.

- **Movimento bruto de domicílios:** +11.372 contra −4.248, para um saldo de
  **+7.124**. São 15.620 de movimento, pouco mais de dois para um.
  - Com todas as unidades: 16.723 para +7.475.
  - O d03 dava 20.865, quase três para um.
- **Divergência de sinal:** **137 unidades** ganharam domicílios e perderam população,
  com +843 domicílios e −2.095 pessoas.
  - São 8,3 % das 1.660, ou 8,0 % das 1.707. Nenhuma delas está no setor 136.
  - O caminho inverso ocorre em 7 unidades.
  - O d03 dava 132 células (6,9 % de 1.925), +804 e −2.044. A subordinada 2 do
    manifesto foi corrigida para os números harmonizados em 2026-09-23.

> *Corrigido em 2026-09-23 (cenário adotado). Antes, a tabela desta seção tinha só
> todas as unidades (hoje a coluna de sensibilidade), com "Movimento bruto de
> domicílios: +12.099 contra −4.624, para o mesmo saldo de +7.475 — 16.723 de
> movimento" e a divergência em "8,0 % das 1.707".*

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
*(Desde 2026-09-23 a camada tem o campo `a_parte_setor_136`, e o `sha256_conteudo` passou
a `f323c4ba…`. As classes e os números são os mesmos, e os scripts do § 10 foram rodados
de novo sobre ela.)*

- Script: `scripts/s1_extintas.py`.
- Números: `derivados/s1_extintas.json`.
- Apoio à conferência no mapa: `derivados/s1_extintas_unidades.gpkg`, fora do git. Tem
  as extintas e as novas, com as contagens do CNEFE e as medidas de vizinhança por
  unidade. É contagem de endereço por célula: não publicar.
- Duas fontes brutas entraram no manifesto: `ibge_cnefe2022` e
  `ibge_censo2010_malha_setores`.
- **Reescrito em 2026-09-23, depois do download da documentação da grade:**
  - § 10.4 refeito: a grade de 2010 é híbrida por método;
  - § 10.6 novo: detecção indireta da desagregação, por `scripts/s1_desagregacao_2010.py`;
  - conclusão (§ 10.7) atualizada.
  - Nenhuma classe mudou.

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

### 10.4 A documentação da grade: método, sigilo e posição do endereço

*Reescrito em 2026-09-23, depois de baixar a documentação da própria grade.*

A documentação está em `data/raw/tabular/ibge/censo_<ano>/doc/`:
- 2010: `grade_estatistica.pdf` (IBGE, *Grade Estatística*, 2016, 28 p.);
- 2022: `Notas_metodologicas_grade_estatistica_2022.pdf` (*Notas metodológicas
  01/2025*).

Ela entrou pela lista fixa em 2026-09-23, commit `de4a7de`.

Continuam valendo os documentos do Censo já consultados:
- `metodologia_censo_dem_2010.pdf`;
- `liv102168.pdf`;
- os dicionários do CNEFE.

**A grade de 2010 é híbrida por método do próprio IBGE** (metodologia de 2010, p. 16–22):

- **Por que é híbrida.** Havia "uma quantidade significativa de registros sem dados de
  localização" (p. 16).
  - No urbano, as causas eram malha viária incompleta ou sem codificação.
  - No rural, "nem todas as edificações tiveram as suas coordenadas geográficas
    registradas".
- **A regra, por setor censitário** (p. 17–18):
  - "ausência de localização" é a diferença entre os domicílios do setor nos
    microdados e os que puderam ser localizados;
  - abaixo de **50 %**, o setor entra por **agregação**;
  - acima de 50 %, entra por **desagregação**;
  - o texto não diz o que acontece com exatamente 50 %.
- **Agregação:**
  - no rural, os pontos das coordenadas (p. 18);
  - no urbano, **quadra/face**, não ponto. Quando a face cruza células, os domicílios
    são repartidos pela extensão dela, supondo distribuição uniforme (p. 18–19).
  - O setor pequeno diante da célula é incorporado inteiro, com tolerância de 90 %
    (p. 20).
- **Desagregação** (p. 18 e 20–21), do setor (origem) para a célula (destino), nesta
  ordem de preferência:
  1. dasimétrico com **vias**;
  2. dasimétrico **binário** com uso e cobertura (povoada / não povoada);
  3. **ponderação zonal simples**, por área.
  - Nos três, **a população da célula é o número de domicílios × moradores por
    domicílio do setor**.
- **Arredondamento** só no fim. Os "dados espúrios" gerados pelo método foram
  suprimidos (p. 22).
- **A variável de abordagem por célula existe no método:** "foi incluída uma variável
  para explicitar a abordagem utilizada para a obtenção dos dados em cada célula:
  agregação, desagregação ou misto" (p. 21).
  - **Ela NÃO acompanha o produto distribuído no geoftp.** Os quatro arquivos em
    `data/raw/` têm só `ID_UNICO`, `nome_1KM` … `nome_500KM`, `QUADRANTE`, `MASC`, `FEM`,
    `POP`, `DOM_OCU`, `Shape_Leng` e `Shape_Area`.
  - A listagem de `.../grade_estatistica/censo_2010/` não tem outro produto além dos
    56 quadrantes.
- **Por que a regra não se reconstrói:** ela depende da ausência de localização de cada
  setor, e esse número **não é publicado**.

**Grade de 2022** (notas 01/2025, p. 6–7):
- **Vínculo:** "a partir das coordenadas geográficas dos domicílios [...] incorporadas
  ao registro de endereços do CNEFE".
  - Níveis de qualidade posicional 1 a 4: **totalização direta**.
  - Níveis 5 e 6: excluídos. São 0,028 % da população e 0,019 % dos domicílios do
    Brasil; no RS, 0,021 % e 0,018 %.
  - **Não há equivalente da desagregação:** 2022 é contagem de pontos.
  - Os níveis 2, 3 e 4 entram na grade de 2022 sem ser a coordenada original do
    endereço.
    - Em Bagé são **4.621 endereços (7,4 %)**, dos quais **4.487** são domicílios
      (particulares ou coletivos).
    - O nível 2, que é a maior parte, fica no mesmo número do endereço (ver a
      divergência abaixo).
  - *Corrigido em 2026-09-23. O texto anterior era: "O nível 4 (ponto médio da face de
    quadra) é a única posição que não é do endereço. Em Bagé ele tem 86 endereços." Ele
    estava errado nas duas listas: os níveis 2 e 3 também não são a coordenada
    original.*
- **Upgrade de resolução:**
  - a célula de 1 km de 2010 "que passou a interseccionar setores censitários urbanos em
    2022" foi dividida em células de 200 m;
  - **não houve o inverso** (sem *downgrade*);
  - o resto das células de 1 km foi mantido.
- **A regra confirma a nossa medição** (`derivados/s1_desagregacao_2010.json`, bloco
  `upgrade_2022`):
  - as células de 1 km de 2010, com centroide em Bagé, que intersectam setor urbano de
    2022 são **41, exatamente as 41 mães** medidas no § 1;
  - nenhuma prevista fica de fora, e nenhuma observada sobra;
  - nenhuma célula de 200 m virou 1 km.
  - Uma das 41 toca o setor urbano em só 0,2 m². Isso mostra que o IBGE aplicou a
    interseção sem tolerância.
- **Divergência de documentos.** A lista de níveis das notas não é a do dicionário do
  CNEFE (§ 10.3):

  | nível | notas da grade | dicionário do CNEFE |
  | --- | --- | --- |
  | 2 | mediana das coordenadas coletadas no mesmo logradouro | apartamentos no mesmo número |
  | 3 | coordenada de operação anterior | coordenada estimada |
  | 5 | mediana por logradouro, CEP e localidade | localidade |

  Os dois textos, citados:
  - **Notas da grade 2022**, p. 7: "2. Coordenada modificada pela mediana das
    coordenadas coletadas em um mesmo logradouro; 3. Coordenada estimada a partir da
    coordenada registrada em operação anterior para o endereço atual; [...]
    5. Mediana das coordenadas de endereços em mesmo logradouro, CEP e localidade".
  - **Dicionário do CNEFE 2022** (`Dicionario_CNEFE_Censo_2022.xls`): "2=Endereço -
    coordenada modificada (apartamentos em um mesmo número no logradouro); 3=Endereço -
    coordenada estimada (endereços originalmente sem coordenadas ou coordenadas
    inválidas); [...] 5=Localidade".

  **O dado de Bagé confere com o dicionário no nível 2** (`scripts/s1_desagregacao_2010.py`,
  bloco `niveis_de_geocodificacao_cnefe_2022` de `derivados/s1_desagregacao_2010.json`):
  - dos 4.273 endereços de nível 2, **3.925 (92 %)** são apartamentos (`COD_TIPO_ESPECIE`
    103);
  - todos compartilham logradouro e número com outro registro;
  - 99,1 % têm a mesma coordenada de outro nível 2;
  - nos 81 logradouros com mais de um número em nível 2, **cada número tem a sua
    coordenada**. Nenhum logradouro tem uma coordenada só, como teria uma "mediana do
    logradouro".

  Os níveis 3 (262 endereços) e 5 (2) não se decidem pelo dado.

  **O que depende da lista, entre os números já medidos:**
  - **Contagens por código** (§ 10.3: 228 endereços no nível 1 nas extintas; § 10.5:
    2.587 / 322 / 12 / 1 nas novas; § 10.4: 3 endereços nos níveis 5 e 6):
    **não dependem**. O código é o mesmo nas duas listas, e os níveis 5 e 6 são
    excluídos da grade em qualquer das duas.
  - **Rótulos do reconhecimento § 5** ("modificada para apartamentos no mesmo número
    92,4 %", "estimada 85,5 %"): vêm do dicionário. O de nível 2 está confirmado pelo
    dado. O de nível 3 é incerto e afeta 262 endereços.
  - **Uma frase deste § 10.4** ("o nível 4 é a única posição que não é do endereço"):
    estava errada e foi corrigida acima (4.621 endereços, não 86).
  - Nenhum número da grade, das classes ou dos testes do § 10 muda.

  A ressalva geral está em `docs/ressalvas_censo_bage.md` § 9.

**Sigilo:**
- A metodologia de 2010 trata a confidencialidade como desafio e cita limiares
  europeus de supressão de 3 e 10 indivíduos (p. 9).
- **Não declara regra de supressão para a grade brasileira.**
- As notas de 2022 não tratam de sigilo.
- No dado não há supressão: 0 nulos, e 234 e 296 células de 1 km com 1 domicílio (2010 e
  2022).

**Posição do endereço, no Censo** (sem mudança):
- **2010:** GPS no PDA nos setores rurais; sem sinal depois de duas tentativas, a
  entrevista seguia sem coordenada (metodologia do Censo 2010, cap. 4). O CNEFE 2010
  tinha coordenada só no rural (§ 1.4.3.6).
- **2022:** coordenada "o mais próximo possível do acesso à unidade" (liv102168,
  p. 39–40).

Verificações no dado (sem mudança):
- Em Bagé, só 3 endereços do CNEFE estão nos níveis 5 e 6.
- Nenhum centroide dos 36 setores rurais de 2010 cai numa extinta.

> **Corrigido em 2026-09-23.** A versão anterior desta subseção dizia que a
> documentação da grade "não está no repositório" e que "não sabemos onde a grade de
> 2010 pôs o domicílio rural sem coordenada, nem o domicílio de setor urbano". Com a
> metodologia de 2010 baixada, isso foi respondido acima:
> - o domicílio de setor com ausência de localização acima de 50 % foi distribuído por
>   desagregação;
> - o domicílio urbano de setor agregado foi posto na face de quadra.

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
  - *Nota de 2026-09-23:* a alocação é a face de quadra repartida pela extensão
    (§ 12). As 56 se separam em **23 de esvaziamento medido** (faces que perderam os
    endereços; 244 domicílios), **29 com indício de deslocamento por repartição** (95)
    e 4 outras (5).
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
  - *Nota de 2026-09-23:* esvaziamento medido (§ 12): 8 das 10 estão em faces que
    perderam os endereços; a conferência visual não viu ocupação.

### 10.6 Detecção indireta da desagregação na grade de 2010

*Acrescentado em 2026-09-23.*
- Script: `scripts/s1_desagregacao_2010.py`.
- Números: `derivados/s1_desagregacao_2010.json`.

**Tudo aqui é INDÍCIO.** Não é a variável oficial de abordagem, que não acompanha o
produto (§ 10.4). Nenhuma classe foi alterada.

**Setor de cada célula.** É o setor com a maior área de interseção, medida em
ESRI:102033. A célula é "inteira" quando esse setor cobre ≥ 90 % dela, a tolerância da
p. 20.

**Teste A — a razão do setor (o teste pedido).**
- **A ideia.** Na desagregação, a população da célula = domicílios × r, sendo r a razão
  moradores/domicílio do setor. Com o arredondamento só no fim, uma célula desagregada
  tem de satisfazer:

  (DOM_OCU − 0,5)·r − 0,5 ≤ POP ≤ (DOM_OCU + 0,5)·r + 0,5

- **Tolerância.** Essa desigualdade **é** a tolerância: o erro máximo que o
  arredondamento de domicílios e de população permite.
- **A razão r de cada setor:**
  - 2010: `Domicilio02 V001 / Domicilio01 V001`, moradores e domicílios particulares e
    coletivos;
  - 2022: `basico v0001 / v0007`.
- **Controles:**
  - a grade de 2022, que é contagem de pontos;
  - a própria grade de 2010, comparada com a razão de um setor sorteado.

| células inteiras com domicílios ≥ 5 | células | compatíveis com a razão do próprio setor | compatíveis com a razão de um setor sorteado |
| --- | ---: | ---: | ---: |
| 2010 | 315 | **26,3 %** | 13,3 % |
| 2022 (controle) | 345 | **21,7 %** | — |

| por setor, com ≥ 3 células informativas | 2010 | 2022 |
| --- | ---: | ---: |
| setores | 40 | 44 |
| mediana da fração compatível | 0,25 | 0,20 |
| setores com fração compatível ≥ 0,8 | **0** | 0 |
| mediana do coeficiente de variação da razão entre células | 0,098 | 0,106 |
| setores com CV < 0,05 | 10 | 3 |

**Veredito: o teste A NÃO discrimina e está DESCARTADO pelo controle de 2022.**

O descarte **é parte do método** e fica registrado com o motivo: o teste parte da
fórmula do próprio IBGE (p. 20–21), mas acusa em 2022, que não tem desagregação, quase
o mesmo que em 2010.
- 2010 fica a 4,6 pontos de 2022. Em 2022 não há desagregação, e ainda assim o dado dá
  21,7 % de compatíveis.
- Em nenhum setor de 2010 a maioria das células acompanha a razão do setor.
- O excesso sobre o setor sorteado aparece nas duas edições: é a semelhança natural
  entre a célula e a média do seu setor, não uma assinatura de método.
- Na faixa de 1 a 2 domicílios, o intervalo de tolerância cobre quase qualquer valor
  plausível: 82 % das células de 1 km com 1 domicílio são compatíveis em 2010, e 86 %
  em 2022.
- O motivo mais forte vem do teste B. As células com a assinatura mais clara de
  desagregação têm razão **3,84** (73 pessoas / 19 domicílios), e a razão publicada do
  setor é **3,61**. Se elas são desagregadas, o IBGE usou totais de setor diferentes
  dos agregados publicados.
  - Por exemplo, só os domicílios não localizados. Isto é inferência.
  - Com isso, a razão publicada não serve de gabarito.

**Teste B — pares idênticos contíguos (achado na exploração).**
- **A ideia.** A ponderação zonal e o dasimétrico binário dão o **mesmo** par
  (domicílios, população) a células inteiras com a mesma área povoada no mesmo setor.
  A contagem de pontos só repete pares por coincidência.
- **Critério:**
  - DOM_OCU ≥ 3;
  - célula inteira num setor;
  - o par (DOM_OCU, POP) se repete numa vizinha rainha, também inteira, do mesmo setor.

| | células com assinatura | setores | par |
| --- | ---: | --- | --- |
| 2010 | **4** (1 km) | 430160205000136 | 19 domicílios / 73 pessoas |
| 2022 (controle) | **0** | — | — |

**O teste B discrimina, mas enxerga pouco.**
- Só marca desagregação onde ela deixou marca inequívoca: um bloco de células de 1 km
  inteiras e iguais num setor rural.
- A desagregação por **vias** dá valores diferentes em cada célula, pela extensão de via
  de cada uma. A **mista** soma pontos e área. Nenhuma das duas repete pares.
- Por isso a ausência de assinatura **não** indica agregação.

**Classificação das 1.352 células de 2010 com domicílio:**

| classe | células | domicílios | população |
| --- | ---: | ---: | ---: |
| assinatura de desagregação | 4 | 76 | 292 |
| assinatura de agregação | **0** | — | — |
| indeterminada | 1.348 | 37.832 | 114.618 |

- **Nenhuma célula recebe "assinatura de agregação".** Nenhum teste separa a agregação
  do resto: o controle de 2022, todo agregado, parece com tudo o mais.
- **No setor.** A regra do IBGE é por setor, então as células inteiras de um setor
  desagregado são todas desagregadas. Estendendo a assinatura ao setor 136, as unidades
  cujo setor de maior área é o 136 somam 46 células com domicílio, **968 domicílios e
  3.476 pessoas** (2,6 % dos 37.908 da grade de 2010).
  - Não são todas desagregadas. O setor tem 494 DPP no agregado, e células de borda,
    como a de 299 domicílios com 87 % no setor, trazem domicílios de setores urbanos
    vizinhos.

**Cruzamento com as classes da subordinada 1** (unidade harmonizada = célula de 2010):

| classe | unidades | com assinatura | no setor 136 | domicílios 2010 no setor 136 |
| --- | ---: | ---: | ---: | ---: |
| nova | 355 | 0 | 1 | 0 |
| adensada | 590 | 0 | 4 | 472 |
| estável | 165 | 0 | 2 | 2 |
| esvaziada | 365 | 2 | 9 | 265 |
| **extinta** | **232** | **2** | **31** | **229** |
| · extintas sem nenhum endereço no CNEFE | 147 | 2 | **27** | 209 |
| · extintas com domicílio no CNEFE | 62 | 0 | 2 | 13 |

**Efeito nos números da subordinada 1** se essas unidades forem tratadas à parte (só
medido, nada aplicado):

| | todas | sem as 4 células com assinatura | sem as unidades do setor 136 |
| --- | ---: | ---: | ---: |
| unidades | 1.707 | 1.703 | 1.660 |
| ganho bruto de domicílios | 12.099 | 12.099 | 11.372 |
| perda bruta | 4.624 | 4.555 | 4.248 |
| extintas (domicílios 2010) | 232 (807) | 230 (769) | **201 (578)** |
| novas (domicílios 2022) | 355 (1.884) | 355 (1.884) | 354 (1.883) |
| ganho das adensadas | 10.215 | 10.215 | 9.489 |
| **faixa da expansão** | **15,6–30,1 %** | 15,6–30,1 % | **16,6–25,6 %** |

**Leitura:**
- A assinatura estrita muda pouco: 2 extintas, 38 domicílios.
- O setor 136 inteiro responde por **31 das 232 extintas e 229 dos 807 domicílios
  extintos (28 %)**. Entre as 147 sem endereço, são 27.
- Tratá-lo à parte estreita a faixa da expansão. O limite superior cai porque as 4
  adensadas do setor são mães harmonizadas e somam +726 domicílios. Entre elas está a
  célula de borda com 299 domicílios em 2010 e 909 em 2022.
- **O que foi medido é um PISO, não uma estimativa.** As 4 células e o setor 136 (968
  domicílios) são o **mínimo** de desagregação em Bagé, não o tamanho dela.
- **Só dois métodos deixam rastro detectável:** a ponderação zonal e o dasimétrico
  binário, e só num **bloco homogêneo**, isto é, células inteiras com a mesma área
  povoada no mesmo setor.
- **Os demais não deixam nenhum rastro:**
  - a desagregação num setor heterogêneo, com células de área povoada diferente;
  - a desagregação por vias, que dá a cada célula a sua extensão de via;
  - a célula mista, que soma pontos e área.
  - Nesses casos a célula desagregada não se distingue de uma agregada, com nenhum dos
    dois testes.
- **O tamanho do viés no município inteiro não se mede** sem a variável oficial (§ 10.4
  e `docs/pedido_ibge_grade_2010_abordagem.md`).

### 10.7 Conclusão: o que os números sustentam

| causa candidata | sustentada? | por quê |
| --- | --- | --- |
| **deslocamento para a vizinha** (o mesmo domicílio posto em célula ao lado numa das edições) | **não** | Pares extinta–nova ficam **abaixo** do acaso a 1, 2 e 5 km (105 contra 158 esperados na rainha; p = 0,0001 para "menos"). A vizinhança das extintas ganha menos que a das outras unidades ocupadas. |
| **supressão por sigilo** na grade | **não** | Nenhuma edição tem nulo, e as duas publicam centenas de células com 1 domicílio. Nenhum documento que temos traz regra de sigilo para a grade. |
| **posicionamento por setor ou localidade** | **não** | Todos os 228 endereços nas extintas estão no nível 1, e o município tem só 3 endereços nos níveis 5 e 6. Nenhum centroide de setor rural de 2010 cai numa extinta. |
| **desocupação real, com a construção de pé** (vaga ou de uso ocasional em 2022) | **sim, em 62 unidades** | 106 domicílios particulares e 3 coletivos no CNEFE, com nenhum ocupado na grade de 2022. Em 1 km, a grade tem 79 % do CNEFE. Nessas unidades a imagem deveria mostrar construção. |
| **posição de 2010 modelada, não observada** (domicílio real, contado no setor, mas distribuído por desagregação ou pela face de quadra) | **o mecanismo está confirmado pelo método do IBGE** (§ 10.4). A marca no dado aparece num setor: **setor 136, 31 extintas e 229 domicílios**, 27 delas sem endereço. No resto, não se mede. | A grade de 2010 é híbrida: acima de 50 % de ausência de localização, o setor é desagregado. A variável por célula não acompanha o produto. O teste B acha no setor 136 um bloco de células iguais (19 / 73), que é a marca da ponderação zonal ou do dasimétrico binário (§ 10.6). |
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
  - A grade de 2010 é híbrida por método (§ 10.4). O bloco do setor 136 tem a marca
    da desagregação (§ 10.6). Os 344 domicílios de setor urbano de 2010 estão, no
    melhor caso, na face de quadra e não no endereço.
    - *Nota de 2026-09-23 (§ 12):* nas 56 extintas urbanas, 23 (244 domicílios) são
      esvaziamento medido, em faces que perderam os endereços, e 29 (95) são indício
      de deslocamento pela repartição da face.
  - Sem a variável de abordagem por célula, o dado só mostra um piso do viés: um
    setor, 229 domicílios extintos.
  - O teste que decidiria unidade a unidade é **imagem de ~2010**: se houve construção
    onde a grade de 2010 pôs domicílios. Ele foi dispensado (item 1 abaixo).

**Tratamento.** Como o teste de deslocamento deu negativo, não há proposta de tratamento
de deslocamento. Proposta para decisão do responsável, sem nada aplicado:
1. **Conferência por imagem de ~2010:** ENCERRADA COMO DISPENSADA em 2026-09-23, por
   decisão do responsável.
   - **O motivo:** o setor 136 já está à parte, e a conferência não mudaria decisão
     nenhuma.
     - Nenhuma classe é reclassificada por imagem.
     - O setor 136 já foi retirado dos números adotados.
     - Nos setores 053 e 054 (10 unidades de 200 m, 111 domicílios), a imagem só
       diria se havia construção em 2010. Isso não altera a regra das classes nem o
       cenário adotado.
   - *O texto anterior propunha: começar pelos dois maiores agrupamentos (setor rural
     136; setores urbanos 053 e 054), que somam 314 dos 807 domicílios; depois, uma
     amostra das 147 sem endereço.*
2. **Pedir ao IBGE a variável de abordagem por célula** da grade de 2010 (p. 21). O
   rascunho está em `docs/pedido_ibge_grade_2010_abordagem.md` e não foi enviado. Com a
   variável, o cruzamento do § 10.6 deixa de ser indício.
   - *Até 2026-09-23 este item era: "obter a documentação da grade que falta". Ela foi
     obtida no commit `de4a7de`, e a variável não vem no produto.*
3. **Sensibilidade, a registrar, sem mudar a classe.** As extintas afetam só o lado da
   perda: as 147 sem endereço somam 634 dos 4.624 domicílios de perda bruta (13,7 %).
   A faixa da expansão (§ 4) usa só ganhos, mas depende do zero de 2010 nas novas. Se
   a posição de 2010 é frágil no rural, as novas de 1 km (484 domicílios) também são:
   sem elas, a faixa iria de 15,6–30,1 % para **11,6–26,1 %**. É a faixa a declarar
   até o teste por imagem.
   - *Nota de 2026-09-23: essa conta é sobre todas as unidades. O cenário adotado é o
     do item 4.*
4. **Declarar à parte o setor 136**, sem mudar classe: 31 extintas e 229 domicílios. A
   faixa da expansão fica em 16,6–25,6 %, o que o § 10.6 mede.
   **ADOTADO pelo responsável em 2026-09-23** (§ 11).

**Ressalvas desta seção:**
- O CNEFE não distingue ocupado de vago.
- A imagem de satélite não foi usada aqui: é a conferência do responsável.
- A atribuição unidade → setor de 2010 é pelo centroide da unidade.
- A conferência do CNEFE é incompleta nas unidades que cruzam o limite.

---

## 11. Conclusão da subordinada 1

*Fechada em 2026-09-23. A subordinada 1 está **concluída** no manifesto, e o estudo
continua `planejado`. Nenhuma classe foi reclassificada: o setor 136 é declarado à
parte, e as unidades dele mantêm as suas classes.*

> *Quanto do crescimento é expansão e quanto é adensamento? Onde estão essas duas
> geografias, que densidade têm e quanta população as acompanhou?*

### 11.1 Números adotados

**Decisão do responsável:** o setor rural de 2010 `430160205000136` fica **à parte**.
- **Motivo:** ele concentra as 4 células com assinatura de desagregação da grade de
  2010 e 31 das 232 extintas (§ 10.6).
- **O que sai:** as unidades cujo setor de 2010 de maior área é o 136. São 47 unidades,
  com 968 domicílios de 2010 e 1.319 de 2022.
- **Fonte:** `derivados/s1_desagregacao_2010.json`, bloco
  `efeito_nos_numeros_da_subordinada_1`.

| | **adotado: setor 136 à parte** | sensibilidade: todas as unidades |
| --- | ---: | ---: |
| unidades com domicílio em algum ano | **1.660** | 1.707 |
| domicílios 2010 → 2022 | **36.940 → 44.064** | 37.908 → 45.383 |
| saldo de domicílios | **+7.124** | +7.475 |
| ganho bruto / perda bruta | **11.372 / 4.248** | 12.099 / 4.624 |
| novas (domicílios 2022) | **354 (1.883)** | 355 (1.884) |
| adensadas (ganho) | **586 (+9.489)** | 590 (+10.215) |
| extintas (domicílios 2010) | **201 (578)** | 232 (807) |
| **expansão, % do ganho bruto** | **16,6 % a 25,6 %** | 15,6 % a 30,1 % |
| adensamento, % do ganho bruto | **74,4 % a 83,4 %** | 69,9 % a 84,4 % |
| moradores que acompanharam as novas | **4.602** | 4.604 |
| divergência de sinal (subordinada 2) | 137 unidades, +843 / −2.095 | igual |

**A resposta:**
- **A maior parte do crescimento de domicílios de Bagé entre 2010 e 2022 é adensamento
  da área já ocupada**, entre três quartos e cinco sextos do ganho bruto.
- **A expansão sobre área sem domicílio em 2010 é de um sexto a um quarto.**
- **A incerteza da faixa** vem das 18 unidades de 1 km que o IBGE passou a gradear em
  200 m. Nelas, a resolução de 2010 não separa ocupação nova de adensamento (§ 4).

**As geografias** (§ 5, cenário adotado; com todas as unidades entre parênteses):
- **Adensadas:** uma mancha contínua. O maior agrupamento tem 475 unidades e 92,9 % dos
  domicílios da classe (481; 93,4 %). 93,1 % dos domicílios estão dentro da área
  urbanizada de 2022 (89,4 %).
- **Novas:** duas populações.
  - Unidades rurais de 1 km, dispersas, com mediana de 1 domicílio.
  - Unidades de 200 m na franja da área urbanizada, que concentram os domicílios.
  - Metade dos domicílios novos fica dentro da área urbanizada.
- **Extintas:** 93,8 % dos domicílios de 2010 estão fora da área urbanizada (95,4 %),
  mas **parte do esvaziamento é urbano de borda, não só rural**. É leitura que o
  cenário adotado trouxe e que o anterior escondia (§ 5.1).
  - O maior agrupamento passa a ser urbano: 10 unidades de 200 m, 111 domicílios, nos
    setores 053 e 054. Antes eram as 18 unidades de 1 km do setor rural 136. É
    esvaziamento medido (8 das 10 em faces que perderam os endereços, § 12), e a
    conferência visual, sem ocupação e com ruínas, é consistente com ele.
  - A mediana ponderada da distância ao centro cai de 4,74 para 3,89 km.
  - 59,5 % dos domicílios extintos estavam em setores urbanos de 2010 (42,6 % com todas
    as unidades).
  - 71,1 % estão em unidades a até 1 km da área urbanizada de 2022.
  - A posição fina dessas extintas urbanas tem a incerteza da grade de 2010 (face de
    quadra, § 10.4). Pelo § 12 elas são dois fenômenos: **23 unidades (244
    domicílios) de esvaziamento medido**, em faces que perderam os endereços, e **29
    (95) com indício de deslocamento por repartição** — estas não são perda.
  - Pelo § 10, 62 são desocupação com a construção de pé.
  - As demais não se separam da posição modelada da grade de 2010.
- **Densidade** (§ 5.3): as novas de 200 m chegam a 389 domicílios/km², menos de um
  terço das adensadas (1.337), nos dois cenários.

### 11.2 As quatro ressalvas metodológicas

São as quatro do `metodo_previsto` do manifesto (a quarta entrou em 2026-09-23; até
então eram três). As quatro têm a mesma forma: um
procedimento do IBGE que, lido como se o dado fosse homogêneo, vira mudança no
território.

1. **Reclassificação de 13 setores rurais de 2010 em urbanos de 2022**
   (dimensionamento § 1.3).
   - Pelo rótulo de situação do setor, 67 % do ganho urbano de população é
     reclassificação.
   - **Tratamento:** urbano e rural definidos geograficamente, pela área urbanizada e
     pela própria grade.
2. **Troca de resolução da grade** (§ 1; `docs/ressalvas_censo_bage.md` § 7).
   - Em 41 lugares, a célula de 1 km de 2010 virou as suas 25 de 200 m, pela regra das
     notas de 2022 conferida 41 de 41 (§ 10.4).
   - **Tratamento:** unidade harmonizada. A junção por `ID_UNICO` dava 40 % de expansão.
3. **Grade de 2010 híbrida** (§§ 10.4 e 10.6; `docs/ressalvas_censo_bage.md` § 8).
   - Parte de 2010 é desagregada do setor, não observada.
   - A variável de abordagem por célula não acompanha o produto.
   - **Tratamento:**
     - o setor 136 à parte;
     - declarar que o medido é um **piso**, porque só a ponderação zonal ou o
       dasimétrico binário em bloco homogêneo deixam rastro;
     - o teste pela razão do setor, descartado pelo controle de 2022, fica registrado
       como parte do método.
4. **Repartição do domicílio urbano pela face de logradouro em 2010** (§ 12;
   `docs/ressalvas_censo_bage.md` § 10). *Acrescentado em 2026-09-23, por decisão do
   responsável.*
   - Em 2010, o domicílio urbano está na face de quadra, repartida pela extensão; em
     2022, no endereço. A reconstrução pela face reproduz a grade de 2010 com
     correlação de **0,989**; **57,8 %** dos endereços urbanos de 2010 estão em face
     que cruza célula; cerca de **2,1 mil domicílios (6,5 %)** mudam de célula quando
     a posição vem do endereço.
   - **Consequência:** no urbano, a grade de 2010 e a de 2022 **não são comparáveis
     célula a célula**, porque o posicionamento mudou de método. Vale para qualquer
     município, não só para Bagé.
   - **Tratamento:** classes mantidas; reposicionamento como sensibilidade declarada
     (17,1–26,6 % contra 16,6–25,6 %); nas extintas urbanas, esvaziamento medido (23;
     244) separado do indício de deslocamento (29; 95).

Além delas, entram na seção de ressalvas do artigo:
- a grade de 2010 fica 1,6 % abaixo do município (§ 2);
- "dentro/fora" é a área urbanizada do IBGE, não o perímetro legal (§§ 7 e 9);
- a divergência entre as listas de níveis de geocodificação (§ 10.4;
  `docs/ressalvas_censo_bage.md` § 9). Ela não muda nenhum número.

### 11.3 O que fica para o texto do artigo

- **Resultado:**
  - a faixa de 16,6–25,6 % de expansão, com a sensibilidade de 15,6–30,1 % ao lado;
  - a tabela por classe do cenário adotado (§ 3);
  - as geografias do § 5, no cenário adotado, com a sensibilidade ao lado;
  - as sete figuras do § 6, com o setor 136 hachurado. A figura 7 é o primeiro mapa
    da subordinada 2.
- **Seção de método:** os quatro achados do § 11.2, com os números que os medem.
  - Troca de resolução: 40 % pela junção por ID, 15,6–30,1 % na unidade harmonizada
    com todas as unidades. É essa a comparação que mede o achado. O número adotado do
    resultado é 16,6–25,6 %, com o setor 136 à parte.
  - Grade híbrida: setor 136, 968 domicílios, 31 extintas, piso.
  - Repartição pela face: correlação de 0,989, 57,8 % dos endereços urbanos em face
    que cruza célula, ~2,1 mil domicílios (6,5 %) que mudam de célula.
- **O que o artigo NÃO afirma:**
  - o tamanho total da desagregação em Bagé, que não se mede sem a variável do IBGE;
  - a causa de cada uma das 170 extintas sem domicílio no CNEFE;
  - qualquer leitura de planejamento urbano. Este documento descreve.

**Pendências que não reabrem a subordinada 1:**
- **Pedido ao IBGE da variável de abordagem.** O texto está pronto para envio em
  `docs/pedido_ibge_grade_2010_abordagem.md` e não foi enviado. Se a variável chegar,
  o § 10.6 é refeito com ela, e o cenário adotado pode mudar. Isso reabre só a
  sensibilidade, não o método.
- ~~Conferência por imagem de ~2010~~: **encerrada como dispensada** em 2026-09-23
  (§ 10.7, item 1).
- ~~Marcar o setor 136 nas figuras~~: **feito** em 2026-09-23 (§ 6). As sete figuras
  foram refeitas com os números adotados.
- **A camada de trabalho** teve a conferência visual em 2026-09-23 (§ 12.1) e segue
  pendente de promoção. Nada foi para o acervo.
- ~~Deslocamento por face em 2010~~: **decidido** em 2026-09-23 (§ 12.4): classes
  mantidas, reposicionamento como sensibilidade, quarto achado de método.

---

## 12. Conferência visual de 2026-09-23 e deslocamento por face na grade de 2010

*Acrescentado em 2026-09-23. **Nada foi reclassificado.** A camada de trabalho segue
pendente, sem promoção e sem cópia para o acervo. O `sha256_conteudo` dela
(`f323c4ba…`) é conferido pelos dois scripts novos antes de ler.*

### 12.1 A conferência

**Feita pelo responsável em 2026-09-23**, no QGIS, sobre imagem de satélite. Objeto:
`saidas/s1_celulas_2010_2022.gpkg` e as sete figuras (`s1-v2`).

| o que foi olhado | resultado da conferência |
| --- | --- |
| extintas urbanas do agrupamento dos setores de 2010 053/054 (§ 5.2) | **sem ocupação visível** nas células; ruínas de uma casa entre dois quadrados que caem parcialmente no setor |
| unidades novas | **todas com residência visível** |
| as 137 da divergência de sinal (figura 7) | dispersas pela cidade, não contíguas; 5 unidades rurais e 6 grandes rurais junto à borda urbana; as urbanas, menores, espalhadas; poucas no miolo central mais denso |

**Onde fica registrada:**
- aqui;
- no `.json` irmão da camada, em `verificacoes.conferencias_visuais_do_responsavel`,
  com a data.
  - **Não** fica no bloco `--- conferência ---` de `observacoes`. Esse bloco só é
    gravado por `scripts/utils/promover.py`, que promoveria a camada a `conferido` e
    recalcularia `pode_publicar`. Decisão do responsável em 2026-09-23: campo à parte,
    status pendente.
  - O `s1_expansao_adensamento.py` preserva esse campo quando regrava o `.json`.

O que a conferência pediu, e onde está:
- o teste de deslocamento por face (§§ 12.2–12.4);
- a caracterização da divergência de sinal, em
  [`resultados_s2.md`](resultados_s2.md), que é o documento da subordinada 2.

### 12.2 A hipótese e o método

**Hipótese.** No urbano, a grade de 2010 agrega por face de quadra. Quando a face
cruza células, os domicílios são repartidos pela extensão da face, supondo
distribuição uniforme (Grade Estatística, 2016, p. 18–19; § 10.4). Isso desloca
domicílio entre células mesmo sem desagregação. A grade de 2022 posiciona pelo endereço
do CNEFE.
- Uma célula atravessada só pela "cauda" de uma face recebe parte dos domicílios dela
  em 2010. Se as casas estão na outra ponta da face, a célula fica sem domicílio em 2022
  e vira **extinta**.
- A vizinha pode ter o inverso e virar **nova**.

**Faces de 2010.** A *Base de Faces de Logradouros do Censo 2010* não estava em
`data/raw/`. Ela entrou pela lista fixa em 2026-09-23 (7ª leva de
`config/fontes_censo_ibge.yaml`, fonte nova `ibge_censo2010_faces_logradouros`).
- Os arquivos são os 5 distritos de Bagé (`4301602{05,17,20,21,22}00.zip`) e o
  leia-me, com URLs lidas nas listagens do geoftp.
- Só o distrito-sede (05) tem atributos. Os outros 4 trazem só a geometria.
- **`TOT_RES` = total de espécies residenciais da face**: endereços do CNEFE 2010,
  ocupados ou não. São 5.073 faces com residência, com 35.174 endereços.

**Script:** `scripts/s1_faces_2010.py`. **Números:** `derivados/s1_faces_2010.json`.
1. **Recorte face × unidade.** Para cada face, a fração do comprimento em cada célula.
   A célula **maior** da face é a que tem a maior fração. Um trecho **de fora** é o
   trecho de face cuja maior parte cai em outra célula.
2. **Modelo uniforme** (o do IBGE): cada célula recebe `TOT_RES` × fração do
   comprimento.
3. **Modelo pelos pontos de 2022.** Cada domicílio do CNEFE 2022 (espécie 1 ou 2) é
   ligado à face residencial de 2010 mais próxima, até 40 m. É o p90 da distância
   medida nas células de 200 m de setor urbano: p50 9,9 m, p75 18,3 m, p90 37,0 m.
   - Cada célula recebe `TOT_RES` × a fração dos pontos de 2022 da face que cai
     nela.
   - Face sem nenhum ponto de 2022 fica com a repartição uniforme.
   - É o 2010 "reposicionado pelos endereços de 2022".
4. **Escala k = 0,929**, domicílios ocupados de 2010 por endereço residencial, nas
   células de 200 m de setor urbano.
5. **Extintas urbanas** = extintas de 200 m com centroide em setor urbano de 2010, fora
   do setor 136: são as **56** unidades com **344** domicílios do § 5.1.
   - O critério é o do setor porque a regra do IBGE é por setor, e só o setor urbano
     tem face.
   - As 19 extintas de 200 m em setor rural de 2010 (50 domicílios) quase não têm
     face: 3 são atravessadas, com 1,7 endereço.

**Validação do modelo uniforme.** Ele **reproduz a grade de 2010** nas células de
200 m de setor urbano.

| células de 200 m | células | DOM_OCU 2010 | `TOT_RES` repartido | correlação | com domicílio e modelo < 0,5 | sem domicílio e modelo ≥ 1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| setor urbano de 2010 | 1.053 | 32.600 | 35.106 | **0,989** | 10 | **0** |
| setor rural de 2010 | 620 | 1.875 | 68 | 0,123 | 97 | 0 |

- A repartição pela face é, portanto, o mecanismo da grade de 2010 no urbano de Bagé.
- Nenhuma célula a que o modelo dá 1 endereço ou mais ficou sem domicílio na grade.
- No setor rural de 2010 a face não explica nada. Ali é a coordenada ou a
  desagregação (§ 10.4).

**Limite do teste, declarado.** O modelo pelos pontos supõe que os endereços da face
ficaram no mesmo lugar entre 2010 e 2022. Duas situações dão o mesmo resultado, e o
dado não as separa:
- a casa demolida numa ponta da face;
- a repartição uniforme que pôs a casa na ponta errada.

Pelo mesmo motivo, uma face que **ganhou** endereços puxa o 2010 para onde houve
crescimento. Por isso há uma **variante conservadora**: só são reposicionadas as faces
com domicílios do CNEFE 2022 ≤ `TOT_RES` de 2010. As demais ficam uniformes.

### 12.3 O que o teste mostra

**Extintas urbanas (56 unidades, 344 domicílios).**

| medida | extintas urbanas | adensadas | esvaziadas | estáveis |
| --- | ---: | ---: | ---: | ---: |
| unidades | 56 | 447 | 265 | 32 |
| atravessadas por face residencial de 2010 | 53 | — | — | — |
| **atravessadas por face cuja maior parte cai em outra célula** | **47** | 424 | 257 | 29 |
| · com a célula maior vizinha rainha, em todas essas faces | 33 | — | — | — |
| **todo o domicílio de 2010 vem de cauda de face** | **25** | 30 | 12 | 7 |
| % do repartido que vem de cauda de face | **33,8 %** | 17,4 % | 15,1 % | 23,0 % |

- A cauda de face pesa o **dobro** nas extintas urbanas do que nas adensadas e nas
  esvaziadas.
- Em 25 das 56, todo o domicílio de 2010 veio de trecho de face cuja maior parte está
  em outra célula.

**CNEFE 2022 em volta das extintas urbanas:**
- **Nas faces de 2010 que atravessam as 56:** 608 domicílios do CNEFE 2022.
  - **1 cai dentro de uma extinta; 607 caem fora.**
  - Distância à extinta: p10 25 m, p25 63 m, **mediana 138 m**, p75 313 m, p90 488 m.
  - 61 estão a até 25 m, 66 entre 25 e 50 m, 102 entre 50 e 100 m, 139 entre 100 e
    200 m, e 239 a mais de 200 m.
- **Nas vizinhas rainha:** 7.219 domicílios, mediana de 85 por extinta. Só 2 extintas
  não têm nenhum.
  - Distância: mediana de 172 m; 146 estão a até 25 m da extinta e 374 a até 50 m.
- **Balanço das faces:** as 139 faces que atravessam as extintas tinham 828 endereços
  residenciais em 2010 e têm 460 domicílios ligados no CNEFE 2022.
  - **74 faces não têm nenhum domicílio em 2022.** Elas somavam 321 endereços em 2010.
  - Só 27 faces têm em 2022 tantos domicílios quanto em 2010, ou mais.

**As 56, por mecanismo** (modelo pelos pontos, escala k):

| mecanismo | unidades | domicílios 2010 |
| --- | ---: | ---: |
| **some com o reposicionamento:** os endereços de 2022 da face estão em outra célula | **29** | **95** |
| **a face perdeu os endereços:** a maior parte vem de face sem nenhum domicílio no CNEFE 2022 | **23** | **244** |
| sem face residencial de 2010 | 3 | 3 |
| permanece: há ponto de 2022 da face na própria unidade | 1 | 2 |

Quantas das 56 ficariam **sem domicílio em 2010** com o reposicionamento, pelos quatro
estimadores:

| estimador | todas as faces | variante conservadora |
| --- | ---: | ---: |
| substituição: k × modelo pelos pontos < 0,5 | 32 | 21 |
| aditivo: DOM_OCU + k × (pontos − uniforme), arredondado | 18 | 13 |

**O agrupamento dos setores 053/054** (10 unidades, 111 domicílios; a conferência
não viu ocupação):
- 33 faces o atravessam, 32 do setor 054. Elas tinham **143** endereços residenciais
  em 2010 e têm **46** domicílios ligados no CNEFE 2022.
- **23 dessas faces não têm nenhum domicílio em 2022.** Elas somavam 91 endereços em
  2010.
- Dos 46 domicílios de 2022 nessas faces, só 1 cai dentro do agrupamento.
- Pelo mecanismo: **8 das 10 unidades** estão em "a face perdeu os endereços", e 2 em
  "some com o reposicionamento".
- Não é, portanto, a repartição pela face. **É a face inteira que perdeu os
  endereços.** Isso é compatível com o que a conferência viu (nenhuma ocupação, ruína
  de uma casa), e não se separa da remoção sem imagem de ~2010.

**Novas urbanas (47 unidades, 751 domicílios de 2022)** — o outro lado:

| mecanismo | unidades | domicílios 2022 |
| --- | ---: | ---: |
| **sem face residencial de 2010 ligada:** rua ou ocupação nova | **29** | **423** |
| cauda de face de 2010, sem endereço de 2022 ligado: continua nova | 7 | 188 |
| **teria domicílio em 2010 com o reposicionamento:** há endereço de 2022 em face de 2010 | **11** | **140** |

- Na variante conservadora, só 3 das 47 teriam domicílio em 2010.
- 13 novas são atravessadas por face de 2010, todas só pela cauda (4,1 endereços
  repartidos, que o arredondamento zera). Nas faces que as atravessam há 181
  domicílios de 2022; 16 caem na própria nova e 165 fora, com mediana de 89 m.
- A conferência viu residência em **todas** as novas. É o que os dois lados dizem:
  - a maioria das novas urbanas está onde não havia face residencial em 2010;
  - 11, com 140 domicílios, podem ser domicílio de 2010 que a repartição pôs na
    vizinha.

**A escala no urbano de Bagé.** O teste confirma o mecanismo, e a medida é esta:

| medida (células de 200 m de setor urbano de 2010) | valor |
| --- | ---: |
| endereços residenciais de 2010 em face que cruza células | **20.330 de 35.174 (57,8 %)** |
| repartido que cai em cauda de face | 5.859 (16,7 %) |
| **domicílios de 2010 que mudam de célula com o reposicionamento** (k) | **≈ 2.108 de 32.600 (6,5 %)** |
| células com mudança ≥ 0,5 domicílio e ≥ 10 % do DOM_OCU | 421, com 13.772 domicílios de 2010 |
| células com qualquer mudança ≥ 0,5 | 711, com 30.410 domicílios de 2010 |

- **Mais da metade dos endereços urbanos de 2010 está em face que cruza células.** A
  posição deles na grade depende da repartição.
- O que efetivamente muda de célula quando a posição vem do endereço é da ordem de
  **2,1 mil domicílios**, 6,5 % do urbano. É o limite superior desse efeito, porque
  inclui crescimento real ao longo da face.

### 12.4 Tratamento das extintas urbanas: DECIDIDO

> **Decisão do responsável (2026-09-23): MANTER as classes como estão.** O
> reposicionamento pela face fica como **sensibilidade declarada**, não como
> classificação.
> - Os números adotados continuam os do § 11: faixa da expansão de **16,6–25,6 %**,
>   201 extintas com 578 domicílios, perda bruta de 4.248.
> - Ao lado, como sensibilidade: 17,1–26,6 % (todas as faces) e 17,3–26,6 %
>   (variante conservadora).
> - Nas 56 extintas urbanas o texto separa, em toda parte, os dois fenômenos:
>   - **23 unidades (244 domicílios) de esvaziamento medido**: faces que perderam os
>     endereços. O agrupamento 053/054 pertence a este grupo (8 das 10 unidades, 105
>     domicílios), e a conferência visual do responsável (ruínas, sem ocupação) é
>     consistente com ele;
>   - **29 unidades (95 domicílios) com indício de deslocamento por repartição** da
>     face, que não são tratadas como perda no texto, embora continuem na classe
>     extinta;
>   - 4 outras (5 domicílios).
> - A repartição pela face entra como **quarto achado de método** (manifesto,
>   `metodo_previsto`; `docs/ressalvas_censo_bage.md` § 10).
> - Foi o caminho 1 abaixo. O texto da proposta fica como estava.

*Proposta, como foi apresentada (para decisão do responsável; nada aplicado):*

**Efeito medido** nos números adotados, pela sensibilidade do reposicionamento (bloco
`sensibilidade_reposicionado` e variante conservadora; cenário adotado, população não
reposicionada):

| | adotado (§ 11) | reposicionado, todas as faces | reposicionado, variante conservadora |
| --- | ---: | ---: | ---: |
| unidades com domicílio em algum ano | 1.660 | 1.641 | 1.647 |
| novas (domicílios 2022) | 354 (1.883) | 357 (1.850) | 361 (1.908) |
| extintas (domicílios 2010) | 201 (578) | 182 (462) | 188 (480) |
| ganho bruto | 11.372 | 10.809 | 11.028 |
| perda bruta | 4.248 | 3.719 | 3.916 |
| **faixa da expansão** | **16,6–25,6 %** | **17,1–26,6 %** | **17,3–26,6 %** |

- **O efeito na faixa da expansão é pequeno: +0,5 a +1,0 ponto.**
  - A repartição desloca domicílio para os dois lados. O ganho bruto e a perda bruta
    encolhem juntos (−563 e −529, com todas as faces).
  - As novas quase não mudam: 12 deixam de ser novas e 15 passam a ser, com todas
    as faces.
- O que muda é o **movimento bruto**, 15.620 → 14.528 (14.944 na variante conservadora), e a contagem de extintas:
  - 19 das 201 extintas deixam de ter domicílio em 2010 (13 na variante
    conservadora);
  - 139 transições entre adensada, estável e esvaziada, com todas as faces.

**Três caminhos:**
1. **Manter as classes como a grade publica e declarar a repartição pela face como
   ressalva de método** (recomendado).
   - A faixa de 16,6–25,6 % fica, com o reposicionamento ao lado como sensibilidade:
     17,1–26,6 %.
   - Das 56 extintas urbanas, o texto separa:
     - as **23 unidades (244 domicílios) em que a face perdeu os endereços**. É
       esvaziamento real até prova em contrário, e é o que a conferência viu em
       053/054;
     - as **29 (95 domicílios) que somem com o reposicionamento**, registradas como
       **indício** de deslocamento por face, não como perda.
   - A leitura "urbano de borda" do § 5.1 continua, com peso menor. Os domicílios
     extintos de setor urbano em que ela se apoia caem de 344 para 249 sem as 29 de
     cauda de face, ou para 244 contando só as de face que perdeu os endereços.
2. **Pôr à parte as 29 extintas de cauda de face**, como o setor 136.
   - É coerente com o § 11, mas pede o simétrico: as 11 novas que teriam domicílio em
     2010.
   - A marca é por estimador. O número vai de 13 a 32 conforme o estimador (§ 12.3),
     e o "à parte" ficaria menos firme que o do setor 136, que tem assinatura no dado.
3. **Adotar o 2010 reposicionado como número principal.** Não recomendado.
   - O modelo pelos pontos mistura crescimento e demolição ao longo da face com a
     repartição, e desloca 6,5 % do urbano com uma suposição que não se testa.
   - Ele serve de sensibilidade, não de dado.

**Em qualquer dos três**, entra na seção de método um **quarto achado**, da mesma forma
que os outros três (§ 11.2):
- em 2010, a posição do domicílio urbano é a face repartida por extensão;
- em 2022, é o endereço;
- 57,8 % dos endereços urbanos de 2010 estão em face que cruza células.
- A repartição cria extintas e novas de borda que o dado de 2022 não sustenta. Em Bagé
  o efeito na faixa da expansão é de +0,5 a +1,0 ponto, e no movimento bruto de
  cerca de 1,1 mil domicílios.

> *A conferência visual (§ 12.1) também alcança dois pontos anteriores:*
> - *o cabeçalho deste documento dizia "Nada disso está conferido no mapa";*
> - *a ressalva 6 do § 7 e o fim do § 11.3 diziam que a camada "segue pendente de
>   conferência visual".*
>
> *Desde 2026-09-23 a conferência visual foi feita e registrada. A camada continua
> **pendente de promoção**, e nada foi para o acervo.*
