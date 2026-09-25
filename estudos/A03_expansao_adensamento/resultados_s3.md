# A03 — Resultados da subordinada 3: o entorno de 2022 nas áreas de crescimento

> *A infraestrutura do entorno acompanha onde a cidade cresceu? Cruzar as áreas de
> crescimento com pavimentação, bueiro, obstáculo na calçada, arborização e rampa,
> lendo 2022 como retrato transversal. Iluminação entra como controle (universal em
> Bagé) e ciclovia como ausência.* (manifesto, subordinada 3)

**Concluída em 2026-09-24.** Este documento descreve e **não tira conclusão de
planejamento urbano**. O que é interpretação está marcado como tal.
- Scripts: `scripts/s3_entorno.py` (números) e `scripts/s3_figuras.py` (figuras).
- Números: `derivados/s3_entorno.json`. A tabela por unidade está em
  `derivados/s3_unidades_setor.csv`, fora do git.
- A camada é `saidas/s1_celulas_2010_2022.gpkg`, com o `sha256_conteudo` conferido
  antes de ler.
- Os setores vêm da camada `setores_2022` do acervo (conferida). O entorno vem das
  tabelas do IBGE já declaradas no manifesto. **Nenhuma fonte nova foi declarada.**
- Nada foi promovido nem escrito em `data/acervo/` ou `data/geoportal/`.

**Recorte.**
- **A mudança** é medida na grade harmonizada, no cenário adotado: o setor de 2010
  430160205000136 fica à parte. São 1.660 unidades, nas classes do
  `resultados_s1.md`.
- **O entorno** só existe por setor censitário de 2022, e só em 168 dos 199 setores.
  - É o entorno **por domicílio** (DPPO), como no `dimensionamento.md` § 4.
  - O denominador de cada item é o próprio item (sim + não + não declarado).
- **A ligação** entre os dois é uma junção espacial célula → setor, e tudo depende
  dela. Por isso ela vem primeiro (§ 1).
- **O retrato é de 2022.** Não existe entorno de 2010 comparável para estes itens. Não
  dá para dizer se a infraestrutura chegou antes ou depois da ocupação.

**Os 10 itens.** A categoria lida em cada um e o papel dele:

| item | categoria | papel |
| --- | --- | --- |
| via pavimentada | sim | discrimina (IQR entre setores 76,6) |
| obstáculo na calçada | sim | discrimina; **mais é pior** (↓) |
| arborização | 5 ou mais árvores (e, à parte, "sem árvores", ↓) | discrimina |
| bueiro | sim | discrimina |
| rampa para cadeirante | sim | discrimina |
| ponto de ônibus | sim | contexto |
| calçada | sim | contexto |
| circulação da via | caminhão/ônibus | contexto |
| iluminação pública | sim | **controle** (universal) |
| via sinalizada para bicicleta | sim | **ausência** |

**Ponderação e referência.**
- Cada unidade recebe a proporção do setor a que foi atribuída.
- O valor de um grupo é a média **ponderada pelos domicílios de 2022** da unidade. As
  extintas não têm domicílio em 2022 e são ponderadas pelos de 2010.
- Só entram as unidades cujo setor tem entorno.
- **Referência "cidade":** o município inteiro no entorno (43.744 domicílios, 168
  setores). A diferença contra o **resto** (todas as outras unidades) também está no
  JSON e no § 2.2.

---

## 1. Incerteza da junção célula → setor

**Critério.** Cada unidade vai para o setor de 2022 com a **maior área de
interseção**; em empate, vence o menor código.
- A interseção é feita em EPSG:31981, e a área é medida no ESRI:102033.
- "Repartida" quer dizer 2 ou mais setores com pelo menos 1 % da área da unidade cada.

| grupo | unidades | peso | fração no setor: mediana | p10 | média ponderada pelo peso | repartidas (2+ setores) | < 70 % num setor (un. / peso) | em setor sem entorno (un. / peso) | setores distintos (com entorno) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| **todas** | 1.660 | 44.064 dom. 2022 | 0,937 | 0,541 | **0,725** | 908 | 413 / **19.827** | 729 / 2.455 | 170 (146) |
| novas | 354 | 1.883 | 1,000 | 0,666 | 0,773 | 104 | 43 / 732 | **287 / 544** | 52 (30) |
| adensadas | 586 | 28.785 | 0,800 | 0,525 | 0,729 | 420 | 205 / 12.470 | 94 / 993 | 149 (132) |
| estáveis | 163 | 910 | 0,990 | 0,588 | 0,736 | 65 | 33 / 405 | 126 / 162 | 44 (25) |
| esvaziadas | 356 | 12.486 | 0,820 | 0,510 | 0,708 | 249 | 117 / 6.220 | 82 / 756 | 133 (113) |
| extintas | 201 | 578 dom. 2010 | 1,000 | 0,744 | 0,953 | 70 | 15 / 25 | 140 / 266 | 41 (21) |
| células de 200 m | 986 | 40.453 | 0,835 | 0,521 | 0,739 | 692 | 317 / 17.532 | 67 / 273 | 151 (145) |
| células de 1 km | 643 | 1.015 | 1,000 | 0,644 | 0,890 | 187 | 86 / 154 | 639 / 995 | 24 (1) |
| 1 km (2022 em 200 m) | 31 | 2.596 | 0,843 | 0,482 | **0,455** | 29 | 10 / 2.141 | 23 / 1.187 | 10 (4) |

**Leitura da incerteza (antes dos resultados).**
- **Pela unidade, a junção parece boa**: metade das unidades tem 94 % ou mais da área
  num único setor.
- **Pelo domicílio, não.** Em média, só **72,5 %** da área da unidade (pesada pelos
  domicílios) está no setor atribuído.
  - **45 % dos domicílios de 2022** (19.827 de 44.064) estão em unidades com menos de
    70 % da área num único setor.
  - As células urbanas de 200 m, onde está quase todo domicílio, **atravessam o limite
    de setor**. Setor urbano é pequeno.
  - Com a junção por maior área, o setor atribuído a elas é o dominante, mas não o
    único.
- **Setor sem entorno.** 729 unidades (2.455 domicílios) caem nos 31 setores sem
  entorno. São sobretudo as células de 1 km, no campo: só 1 dos 24 setores atribuídos
  a elas tem entorno.
  - Das **354 novas, 287 (544 domicílios) estão em setor sem entorno.** O entorno das
    novas se lê, na prática, só nas 67 que têm entorno (1.339 domicílios).
- **O número efetivo de observações é o de setores, não o de unidades.** Todas as
  unidades de um setor recebem o mesmo valor.
  - As novas somam 30 setores com entorno, as extintas 21 e as estáveis 25.
  - Nos grupos pequenos, **3 setores levam de 30 % a 60 % do peso** (§ 2).
- **Sensibilidade.** Todos os cruzamentos foram repetidos só com as unidades com
  **70 % ou mais da área num único setor**: 1.247 unidades, cerca de 55 % dos
  domicílios. O resultado principal só é afirmado quando **vale nas duas leituras**.
- A tabela por unidade (setor atribuído, fração, repartição) está em
  `derivados/s3_unidades_setor.csv`, fora do git. É dado do IBGE; só não é versionada
  por ser lista por unidade que também leva a datação do i02.

---

## 2. O entorno das classes de mudança

### 2.1 Principal (todas as unidades com entorno)

% de domicílios com o item. Entre parênteses, a diferença em pontos contra a cidade.

| item | cidade | novas | adensadas | estáveis | esvaziadas | extintas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| via pavimentada | 45,8 | 57,2 (+11,4) | 40,3 (−5,6) | 51,0 (+5,1) | 49,5 (+3,7) | 28,5 (−17,3) |
| obstáculo na calçada ↓ | 64,4 | 42,8 (−21,5) | 66,6 (+2,2) | 53,7 (−10,7) | 65,7 (+1,3) | 71,8 (+7,5) |
| arborização (5+ árvores) | 48,9 | 36,5 (−12,4) | 50,4 (+1,6) | 55,0 (+6,1) | 53,7 (+4,8) | 45,0 (−3,9) |
| bueiro | 65,1 | 41,0 (−24,1) | 64,8 (−0,3) | 66,7 (+1,6) | 69,1 (+4,0) | 65,3 (+0,3) |
| rampa para cadeirante | 17,6 | 16,0 (−1,6) | 15,5 (−2,1) | 18,4 (+0,8) | 19,5 (+1,9) | 6,4 (−11,2) |
| ponto de ônibus | 12,5 | 37,8 (+25,3) | 11,6 (−0,9) | 9,5 (−3,0) | 11,2 (−1,3) | 8,2 (−4,4) |
| calçada | 89,3 | 78,3 (−11,1) | 87,8 (−1,5) | 85,5 (−3,9) | 90,0 (+0,6) | 87,2 (−2,1) |
| circulação: caminhão/ônibus | 93,1 | 86,4 (−6,7) | 92,8 (−0,3) | 93,8 (+0,6) | 94,3 (+1,2) | 85,5 (−7,6) |
| iluminação pública (controle) | 99,3 | 99,7 (+0,4) | 99,3 (0,0) | 99,3 (0,0) | 99,4 (+0,1) | 99,3 (−0,1) |
| via para bicicleta (ausência) | 1,4 | 12,8 (+11,4) | 1,4 (0,0) | 0,4 (−1,0) | 0,8 (−0,5) | 1,3 (−0,1) |
| sem árvores ↓ | 20,8 | 51,0 (+30,2) | 17,4 (−3,4) | 15,3 (−5,5) | 16,8 (−4,1) | 21,0 (+0,2) |
| *com entorno: unidades / peso / setores* | | 67 / 1.339 / 30 | 492 / 27.792 / 132 | 37 / 748 / 25 | 274 / 11.730 / 113 | 61 / 312 / 21 |
| *peso nos 3 maiores setores* | | 45,7 % | 8,3 % | 30,3 % | 7,2 % | 59,9 % |

### 2.2 Contra o resto da cidade (pontos)

É a mesma leitura, com a referência "todas as outras unidades" no lugar do município.
Ela importa para as adensadas, que somam 63 % dos domicílios e pesam sobre a média da
cidade.

| item | novas | adensadas | estáveis | esvaziadas | extintas |
| --- | ---: | ---: | ---: | ---: | ---: |
| via pavimentada | +14,1 | **−10,0** | +7,5 | +8,2 | −15,1 |
| obstáculo na calçada ↓ | −23,3 | +3,8 | −11,9 | +0,5 | +6,4 |
| arborização (5+ árvores) | −15,0 | −1,7 | +4,1 | +3,8 | −6,0 |
| bueiro | −25,1 | −1,4 | +1,5 | +5,3 | 0,0 |
| rampa para cadeirante | −0,7 | −3,6 | +1,7 | +3,9 | −10,3 |
| calçada | −10,1 | −0,8 | −2,6 | +2,6 | −0,9 |
| iluminação pública (controle) | +0,4 | −0,1 | −0,1 | +0,1 | −0,1 |

### 2.3 Sensibilidade: só unidades com ≥ 70 % da área num setor

| item | cidade | novas | adensadas | estáveis | esvaziadas | extintas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| via pavimentada | 45,8 | 47,2 (+1,3) | 40,0 (−5,8) | 43,9 (−2,0) | 46,6 (+0,8) | 28,9 (−16,9) |
| obstáculo na calçada ↓ | 64,4 | 72,3 (+7,9) | 69,2 (+4,9) | 58,4 (−6,0) | 67,1 (+2,8) | 71,0 (+6,6) |
| arborização (5+ árvores) | 48,9 | 37,4 (−11,5) | 52,1 (+3,2) | 63,2 (+14,4) | 51,6 (+2,8) | 44,4 (−4,4) |
| bueiro | 65,1 | 50,2 (−14,9) | 65,1 (0,0) | 67,8 (+2,7) | 68,2 (+3,1) | 64,4 (−0,7) |
| rampa para cadeirante | 17,6 | 8,0 (−9,5) | 13,9 (−3,7) | 16,8 (−0,8) | 19,9 (+2,4) | 6,6 (−11,0) |
| ponto de ônibus | 12,5 | 11,0 (−1,5) | 10,9 (−1,6) | 9,7 (−2,9) | 10,8 (−1,7) | 8,2 (−4,4) |
| calçada | 89,3 | 79,3 (−10,0) | 88,1 (−1,2) | 84,4 (−5,0) | 91,2 (+1,9) | 86,8 (−2,5) |
| circulação: caminhão/ônibus | 93,1 | 76,9 (−16,2) | 91,6 (−1,5) | 90,4 (−2,7) | 93,0 (−0,1) | 85,3 (−7,8) |
| iluminação pública (controle) | 99,3 | 99,6 (+0,3) | 99,3 (0,0) | 99,1 (−0,3) | 99,3 (0,0) | 99,3 (−0,1) |
| via para bicicleta (ausência) | 1,4 | 2,0 (+0,6) | 1,1 (−0,3) | 0,8 (−0,6) | 0,7 (−0,7) | 1,3 (−0,1) |
| sem árvores ↓ | 20,8 | 41,8 (+20,9) | 15,9 (−4,9) | 8,0 (−12,8) | 17,8 (−3,1) | 21,5 (+0,7) |
| *com entorno: unidades / peso / setores* | | 58 / 684 / 26 | 307 / 15.748 / 108 | 28 / 378 / 18 | 169 / 6.054 / 80 | 55 / 301 / 21 |

### 2.4 O que se sustenta

**Critério declarado.** Uma diferença contra a cidade só é dada como resultado quando
atende às três condições:
- (a) tem o mesmo sinal no principal e na sensibilidade;
- (b) no principal, tirando **um setor de cada vez**, o valor do grupo nunca cruza o da
  cidade;
- (c) tem 5 pontos ou mais nas duas leituras.

| classe | diferenças que se sustentam (principal / sensibilidade, em pontos) |
| --- | --- |
| **novas** | **bueiro −24,1 / −14,9**; **arborização 5+ −12,4 / −11,5** (sem árvores +30,2 / +20,9); **calçada −11,1 / −10,0** |
| adensadas | via pavimentada −5,6 / −5,8 (contra o resto: −10,0) |
| estáveis | obstáculo na calçada −10,7 / −6,0 (melhor que a cidade); arborização 5+ +6,1 / +14,4 |
| esvaziadas | **nenhuma**: acompanham a cidade em todos os itens |
| **extintas** | **via pavimentada −17,3 / −16,9**; **rampa −11,2 / −11,0**; obstáculo na calçada +7,5 / +6,6 (pior); circulação de caminhão/ônibus −7,6 / −7,8 |

**Controles.**
- **Iluminação pública é universal** em todas as classes (99,3–99,7 %) e nas duas
  leituras: o controle funciona.
  - A **exceção está nas favelas e comunidades urbanas**, com 90,9 % (§ 4.2). O dado
    de universalidade vale para a cidade, não para cada ponta dela.
- **A via sinalizada para bicicleta é ausente**, de 0,4 % a 2,0 %, em todas as classes
  na sensibilidade. O 12,8 % das novas no principal vem de um setor.

**As extintas urbanas por fenômeno** (`resultados_s1.md` § 12.4; peso: domicílios de
2010):

| fenômeno | unidades (com entorno) | dom. 2010 (com entorno) | setores | 3 maiores setores | via pavimentada | rampa | obstáculo ↓ | bueiro |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| **esvaziamento medido** | 23 (21) | 244 (218) | 12 | 80,3 % | 31,5 (−14,3) | 8,1 (−9,5) | 74,1 (+9,8) | 63,6 (−1,5) |
| deslocamento por repartição da face | 29 (25) | 95 (77) | 13 | 42,9 % | 25,1 (−20,7) | 2,6 (−15,0) | 63,2 (−1,1) | 66,2 (+1,1) |
| outras | 4 (4) | 5 (5) | 4 | 80,0 % | 17,6 (−28,3) | 8,4 (−9,2) | 74,0 (+9,6) | 77,1 (+12,1) |

- **Esvaziamento medido:** pavimentação, rampa e obstáculo passam no critério desta
  seção.
  - Tirando um setor de cada vez, a pavimentação fica em 25,2–43,2 %, a rampa em
    5,4–15,6 % e o obstáculo em 72,4–74,8 %. Nenhum cruza a cidade.
  - Todas as 23 unidades têm 70 % ou mais da área num setor, então a sensibilidade é
    idêntica ao principal.
- **O deslocamento por repartição**, que é efeito de medida, também está em setores
  pouco pavimentados e sem rampa. Mas não tem mais obstáculo.
- **O resultado das extintas, portanto, não é um artefato do deslocamento:** o
  esvaziamento **medido** tem o mesmo entorno pior.

**Resultados da subordinada 3 (o que se sustenta).** Todo resultado é "a unidade está
em setor com…", nunca "a unidade tem…".
- **As novas, onde há entorno, estão em setores com menos bueiro, menos arborização e
  menos calçada** que a cidade:
  - bueiro −24,1 / −14,9 pontos;
  - árvores −12,4 / −11,5;
  - calçada −11,1 / −10,0.
  - Vale nas duas leituras e sem depender de um setor.
  - A pavimentação das novas **não** separa de forma estável.
- **As extintas estão em setores com menos pavimentação e menos rampa, e com mais
  obstáculo na calçada:** pavimentação −17,3 / −16,9; rampa −11,2 / −11,0; obstáculo
  +7,5 / +6,6.
  - **O esvaziamento urbano acontece onde a infraestrutura é pior.** Vale para o
    esvaziamento **medido**, e não só para o deslocamento por repartição.
- **As esvaziadas são iguais à cidade** em todos os itens.
  - **Perder domicílio não se associa a entorno ruim; a extinção, sim.** A unidade que
    perde parte dos domicílios está no tecido comum da cidade. A que perde todos está
    no tecido de pior infraestrutura.
- **O adensamento se deu em tecido um pouco menos pavimentado:** −5,6 pontos contra a
  cidade, −10,0 contra o resto. Nos demais itens, ele acompanha a cidade.
- **As favelas e comunidades urbanas são o contraste extremo** (§ 4.2):
  - via pavimentada ≈ 1 %, rampa ≈ 1 % e calçada 62,8 %;
  - a **iluminação pública cai para 90,9 %**, a **única quebra da universalidade**
    medida em toda a cidade (99,3 %; 99,3–99,7 % em todas as classes).

**O que não se sustenta, e por quê.** Em todos os casos abaixo, poucos setores levam o
peso: 3 setores fazem 46 % do peso das novas.
- **Novas "mais pavimentadas" que a cidade:** +11,4 no principal, +1,3 na
  sensibilidade.
- **Novas "com menos obstáculo":** −21,5 no principal, **+7,9** na sensibilidade. O
  sinal se inverte.
- **Novas "com mais ponto de ônibus e ciclovia":** +25,3 e +11,4 no principal, −1,5 e
  +0,6 na sensibilidade.
- **O item 3 inteiro** (§ 3): 3 setores fazem de 71 % a 90 % do peso de cada grupo.
- Esses valores sobem ou descem com a presença de 2 ou 3 setores grandes, e não com a
  classe. Por isso não entram como resultado.

---

## 3. A pergunta da datação: expansão recente × preenchimento de vazio interno (interpretação)

> **Interpretação.** Os grupos vêm da datação pela evolução urbana do IPHAN
> (`resultados_s1.md` § 14.1.1; `derivados/i02_evolucao_urbana_unidades.csv`), que é
> **fonte não redistribuível**. Aqui saem só agregados por grupo. A figura do item está
> marcada com a restrição da fonte.

**Grupos, dentro das 90 novas urbanas de 200 m:**

| grupo | unidades | domicílios 2022 | com entorno (un. / dom.) | setores | peso no maior setor | peso nos 3 maiores |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| ocupação posterior a 2001 | 55 | 675 | 37 / 615 | 18 | 28,5 % | 70,7 % |
| vazio interno do tecido de 1938–1960 | 27 | 643 | 21 / 637 | 14 | 41,8 % | 85,6 % |
| *borda sem data firme (à parte)* | 4 | 50 | 4 / 50 | 3 | — | — |
| *incrementos de 1970 e 2001 (à parte)* | 4 | 32 | 3 / 31 | 2 | — | — |

- Os dois grupos principais têm **4 setores em comum**.

**Principal:**

| item | cidade | posterior a 2001 | vazio interno 1938–1960 | diferença (pp) | tirando um setor: faixa | sinal estável? | p (permutação) |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| via pavimentada | 45,8 | 56,6 | 61,4 | −4,8 | −22,1 a +22,8 | não | 0,88 |
| obstáculo na calçada ↓ | 64,4 | 46,2 | 39,0 | +7,2 | −20,8 a +23,7 | não | 0,84 |
| arborização (5+ árvores) | 48,9 | 46,8 | 25,4 | +21,4 | +0,3 a +35,0 | sim | 0,50 |
| bueiro | 65,1 | 45,3 | 32,0 | +13,3 | −9,7 a +29,3 | não | 0,71 |
| rampa para cadeirante | 17,6 | 29,5 | 2,5 | +27,0 | +0,9 a +35,5 | sim | 0,27 |
| ponto de ônibus | 12,5 | 29,9 | 48,2 | −18,4 | −44,3 a +18,8 | não | 0,75 |
| calçada | 89,3 | 74,5 | 85,3 | −10,8 | −21,5 a +7,6 | não | 0,73 |
| circulação: caminhão/ônibus | 93,1 | 73,6 | 97,5 | −23,9 | −34,4 a −2,6 | sim | 0,29 |
| iluminação pública (controle) | 99,3 | 99,8 | 99,6 | +0,2 | 0,0 a +0,5 | não | 0,60 |
| via para bicicleta (ausência) | 1,4 | 27,1 | 0,8 | +26,4 | −0,7 a +34,2 | não | 0,28 |
| sem árvores ↓ | 20,8 | 47,2 | 57,7 | −10,4 | −25,7 a +19,9 | não | 0,78 |

**Sensibilidade (≥ 70 % num setor):** com entorno, 32 unidades e 229 domicílios
posteriores a 2001, contra 18 unidades e 369 domicílios de vazio interno.

| item | posterior a 2001 | vazio interno | diferença (pp) | tirando um setor: faixa | sinal estável? | p |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| via pavimentada | 74,3 | 33,9 | **+40,4** | +1,5 a +61,5 | sim | 0,27 |
| obstáculo na calçada ↓ | 90,1 | 67,0 | +23,1 | +8,1 a +28,3 | sim | 0,35 |
| arborização (5+ árvores) | 25,0 | 43,5 | −18,6 | −24,3 a +19,3 | não | 0,56 |
| bueiro | 32,5 | 55,0 | −22,5 | −39,1 a +26,9 | não | 0,58 |
| rampa para cadeirante | 9,9 | 4,3 | +5,6 | +0,8 a +20,7 | sim | 0,37 |
| calçada | 96,8 | 74,6 | +22,2 | +6,2 a +29,1 | sim | 0,32 |
| circulação: caminhão/ônibus | 39,5 | 95,7 | −56,2 | −64,2 a +3,8 | não | 0,12 |
| sem árvores ↓ | 69,4 | 27,4 | +42,0 | −4,4 a +48,8 | não | 0,09 |

- Nas 22 comparações (11 itens × 2 leituras), **nenhum p fica abaixo de 0,05**.
- O p da permutação ainda é **otimista**: ele trata como independentes unidades que
  dividem o mesmo setor.

**Resultado: a hipótese não é confirmada, e também não é negada.** O dado **não
separa** os dois grupos.

A hipótese dizia que a expansão recente foi para onde falta infraestrutura, e que o
preenchimento se deu em tecido já servido. Nenhum dos itens que testariam isso muda do
jeito previsto nas duas leituras:
- **Pavimentação:** no principal, a expansão recente tem **menos** (−4,8, com sinal
  instável). Na sensibilidade, tem **muito mais** (+40,4).
- **Bueiro:** +13,3 no principal e −22,5 na sensibilidade, com sinal instável nas
  duas.
- **Arborização:** +21,4 e −18,6. **Calçada:** −10,8 e +22,2.
- **Os itens mudam de sinal** entre as duas leituras.
  - Nos dois grupos, **3 setores levam de 71 % a 90 % do peso**.
  - O resultado depende de **quais três setores** entram, não da idade da ocupação.
- **O único contraste de mesmo sentido nas duas leituras** é descritivo e não testa a
  hipótese: a expansão recente está em faces com **menos circulação de caminhão e
  ônibus** (−23,9 e −56,2 pontos), ou seja, em ruas locais.
  - No principal, o sinal é estável tirando um setor de cada vez.
  - Na sensibilidade, a faixa toca o zero.

**Com o § 4.1 (interpretação):** as novas posteriores a 2001 **fora** da área
urbanizada do IBGE têm, onde há entorno, pouca pavimentação (23,2 %) e pouca rampa
(10,1 %), contra 61,9 % e 32,6 % das que estão **dentro**.
- É o contraste que a hipótese imaginava: a expansão recente fora da mancha urbana
  aparece menos servida em pavimentação.
- Mas ele se apoia em 23 unidades com entorno e **84 domicílios**. É uma indicação,
  não um resultado.

### 3.1 Decisão: o item 3 não será refeito com outra junção por setor

*Decisão do responsável, 2026-09-24.*
- Qualquer junção por setor (maior área, fração da área, ponderação por domicílio da
  face) atribui às unidades **o mesmo valor do setor**.
- Com 14 a 18 setores por grupo, e 3 deles levando de 71 % a 90 % do peso, o resultado
  continuaria dependendo de quais setores entram.
- **A limitação é da unidade de agregação do entorno (o setor), não do método de
  junção.**

### 3.2 Teste: o entorno por FACE resolveria o item 3? Não liga

*Testado em 2026-09-24, navegando as listagens do FTP do IBGE.*

**A tabela de entorno "por faces"** (`Agregados_por_setores_entorno_faces_BR.zip`,
declarada no manifesto) é **agregada por setor**.
- Tem uma linha por setor (`COD_SETOR_M22FINAL`; 171 setores em Bagé) e
  `V05400` = faces no setor, com contagens de faces por item.
- **Não há identificador de face.** As 7.573 faces são uma soma, não uma lista.

**A geometria das faces de 2022 existe** no IBGE.
- Caminho: `geoftp.ibge.gov.br/recortes_para_fins_estatisticos/malha_de_setores_censitarios/`
  `censo_2022/base_de_faces_de_logradouros_versao_2022_censo_demografico/`.
- Um arquivo por UF. O do RS tem 41,6 MB, com Last-Modified de 07/06/2024.
  - Baixei só esse, para inspeção, fora do acervo (sha256 `f1b38ad7…0fec`).
  - Nenhum recorte nacional foi baixado.
- Em Bagé são 7.631 faces (LineString, EPSG:4674).
- Campos: `CD_SETOR`, `CD_QUADRA`, `CD_FACE`, `NM_TIP_LOG`, `NM_TIT_LOG`, `NM_LOG`,
  `TOT_RES` e `TOT_GERAL`.
- **Nenhum atributo de entorno.**

**O entorno não é publicado abaixo do setor.**
- A pasta `Agregados_por_Setores_Censitarios_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/`
  vai de setor a município.
- A pasta `Dados_percentuais_das_Caracteristicas_urbanisticas_do_entorno_dos_domicilios/`
  também é por setor (`br_setores_entorno_cd2022`).

**Conclusão: não liga.**
- Há geometria de face com identificador, mas não há entorno por face publicado.
- Há entorno, mas só agregado por setor, sem identificador de face.
- **O item 3 fica sem resposta**, e isso entra como **limitação declarada do artigo**.
  - Com o dado público do Censo 2022, não é possível dizer se a expansão posterior a
    2001 está em faces mais ou menos servidas que o preenchimento de vazio interno.
  - Responder exigiria o entorno por face, que o IBGE não publica.
  - Resta um pedido de tabulação especial ao IBGE, se o responsável quiser fazê-lo.
- O arquivo de faces **não entrou no acervo**: não é usado.

---

## 4. As pontas

### 4.1 Área urbanizada do IBGE, dentro × fora

Uma unidade está "dentro" quando tem 50 % ou mais da área na área urbanizada de 2022,
o mesmo limiar do s1. Os valores são % de domicílios, só nas unidades com entorno.

| classe | lado | unidades | peso | com entorno (un. / peso) | via pavimentada | bueiro | arborização 5+ | calçada | rampa | obstáculo ↓ |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| novas | dentro | 25 | 968 | 22 / 958 | 63,9 | 29,0 | 31,8 | 85,7 | 18,6 | 38,5 |
| novas | fora | 329 | 915 | 45 / 381 | 40,6 | 71,2 | 48,1 | 59,6 | 9,4 | 53,8 |
| adensadas | dentro | 442 | 26.790 | 439 / 26.772 | 41,3 | 65,4 | 50,6 | 88,8 | 15,9 | 67,3 |
| adensadas | fora | 144 | 1.995 | 53 / 1.020 | **13,8** | 48,3 | 46,3 | 63,7 | 5,7 | 48,5 |
| estáveis | dentro | 25 | 710 | 24 / 708 | 52,0 | 66,6 | 55,3 | 85,4 | 18,9 | 52,7 |
| estáveis | fora | 138 | 200 | 13 / 40 | 32,8 | 67,5 | 50,0 | 86,6 | 8,4 | 70,6 |
| esvaziadas | dentro | 227 | 11.491 | 227 / 11.491 | 50,1 | 69,3 | 54,0 | 90,1 | 19,8 | 65,8 |
| esvaziadas | fora | 129 | 995 | 47 / 239 | 21,6 | 56,8 | 38,4 | 84,2 | 4,8 | 61,8 |
| extintas | dentro | 8 | 36 (2010) | 7 / 25 | 54,6 | 68,0 | 60,1 | 92,7 | 17,0 | 77,3 |
| extintas | fora | 193 | 542 (2010) | 54 / 287 | 26,2 | 65,1 | 43,7 | 86,7 | 5,5 | 71,4 |
| novas 200 m posteriores a 2001 | dentro | 17 | 541 | 14 / 531 | 61,9 | 41,7 | 45,7 | 76,2 | 32,6 | 44,6 |
| novas 200 m posteriores a 2001 | fora | 38 | 134 | 23 / 84 | 23,2 | 68,0 | 54,1 | 63,4 | 10,1 | 56,3 |

*Correção de 2026-09-24:* a primeira versão desta tabela (commit `1730e1b`) trazia, na
coluna "peso", o peso **só das unidades com entorno**, por defeito do script. A soma
com entorno sobrescrevia o total. As proporções não mudam.

- **Fora da área urbanizada, pavimentação e rampa caem em todas as classes.**
  - Pavimentação: de 41–64 % para 14–41 %.
  - Rampa: de 16–33 % para 5–10 %.
  - A calçada cai nas novas e nas adensadas.
  - É a ponta periférica, descrita pelo dado.
  - O contraste é de **setor**: os setores de fora são grandes e mistos, e uma unidade
    fora da mancha recebe o valor de um setor que também tem parte urbana.
- **O bueiro inverte nas novas:** 29 % dentro, 71 % fora. É um caso em que o setor
  atribuído pesa mais que a posição da unidade. Não é lido como achado.
- **Quase todo o peso das novas está dentro** da área urbanizada (958 de 1.339
  domicílios com entorno). As novas de fora são muitas (329), mas pequenas, e quase
  todas sem entorno (45 com entorno, 381 domicílios).

### 4.2 Favelas e comunidades urbanas de 2022

Os 7 setores de FCU vêm da coluna `CD_FCU` da camada `setores_2022` e são idênticos
aos da planilha oficial do IBGE. Por isso nenhuma fonte nova foi necessária. Seis deles
têm entorno.

| | FCU (média simples dos 6 setores) | cidade |
| --- | ---: | ---: |
| via pavimentada | **1,0** | 45,8 |
| rampa para cadeirante | 1,0 | 17,6 |
| calçada | 62,8 | 89,3 |
| bueiro | 57,4 | 65,1 |
| arborização 5+ | 37,6 | 48,9 |
| obstáculo na calçada ↓ | 58,6 | 64,4 |
| ponto de ônibus | 0,0 | 12,5 |
| circulação: caminhão/ônibus | 61,6 | 93,1 |
| **iluminação pública** | **90,9** | 99,3 |

- **As FCU são a ponta de menor infraestrutura.** Não há via pavimentada nem rampa;
  em um setor, só 5,9 % dos domicílios estão em face pavimentada.
  - **A iluminação pública, universal no resto da cidade, falha ali.**
- **O crescimento nas FCU é adensamento, não expansão.**
  - Nenhuma nova toca setor de FCU.
  - Nenhuma das novas datadas toca setor de FCU.
  - 21 adensadas têm 1 % ou mais da área em setor de FCU, com cerca de 252 domicílios
    de 2022 na parte de FCU. Há também 6 esvaziadas (cerca de 49 domicílios).
  - Pela maior área, só 4 unidades são atribuídas a setor de FCU: 3 adensadas e 1
    esvaziada. Os setores de FCU são pequenos e as células de 200 m os atravessam.
  - Por isso a leitura é pela fração da área, não pela atribuição.

---

## 5. Figuras

Todas estão em `saidas/`, cada uma com `.json` irmão (pendente, `pode_publicar=false`):
- **`s3_mapa_entorno_itens_urbano.png`:** os 5 itens que discriminam, % de domicílios
  por setor, com as novas e as adensadas de 200 m sobrepostas em contorno.
- **`s3_mapa_pavimentacao_urbano.png`:** a pavimentação, o item de maior dispersão, em
  tamanho de leitura.
- **`s3_datacao_novas_200m.png`:** item 3, os dois grupos nos 10 itens, com a cidade
  como referência. O principal e a sensibilidade ficam lado a lado.
  - Esta figura leva a restrição da fonte da datação: `autorizacao_fonte=false`.

**Cor** (`scripts/paleta.py`):
- **Coropleta:** uma rampa **violeta** de 5 degraus, fora do eixo azul/laranja, porque
  é magnitude e não ganho ou perda. Validada com `validate_palette.js --ordinal`:
  degrau claro com 2,08:1.
- **Setor sem entorno:** cinza claro com hachura esparsa, para não se confundir com
  "perto de zero" (mais leve desde a conferência, § 5.1).
- **Áreas de crescimento:** em **contorno de tinta**. As novas vão em traço cheio com
  halo claro; as adensadas, em tracejado.
  - O azul da classe "nova" sumiria sobre o violeta escuro: o validador mediu ΔE 1,6
    em deuteranopia.
- **Os dois grupos do item 3:** dois tons do azul das novas, com forma diferente
  (círculo e quadrado) e o valor escrito em cada marcador. O azul claro tem contraste
  de 2,61:1, e é o rótulo que o compensa.
- **As unidades de 1 km não são desenhadas nos mapas.** Estão no campo e quase todas em
  setor sem entorno.

### 5.1 Conferência visual do responsável (2026-09-24)

As três figuras foram **aprovadas com três ajustes de leitura**, feitos na versão
`s3-v2` de `scripts/s3_figuras.py`:

| figura | ajuste pedido | como ficou |
| --- | --- | --- |
| `s3_datacao_novas_200m.png` | marcar os itens em que principal e sensibilidade divergem em sinal; dizer que o resultado é inconclusivo | hachura cinza na faixa dos **4 itens** em que a diferença posterior − vazio troca de sinal (via pavimentada, arborização, bueiro, calçada), explicada na legenda; título "resultado INCONCLUSIVO" e subtítulo: "não concluir a partir de um painel só" |
| `s3_mapa_entorno_itens_urbano.png` | rampa com escala própria, adaptada à distribuição do item | faixas 0–5, 5–10, 10–20, 20–40, 40–100 % (84 / 19 / 18 / 17 / 30 setores; antes, 121 dos 168 caíam em 0–20 %); o título e a legenda do painel dizem que a escala é diferente das demais |
| `s3_mapa_entorno_itens_urbano.png` e `s3_mapa_pavimentacao_urbano.png` | fundo dos setores sem entorno mais leve | `COR_SEM_ENTORNO` (`#efeeea`, `paleta.py`) com hachura esparsa |

- **Onde está o registro:** no `.json` de cada figura, em
  `verificacoes.conferencias_visuais_do_responsavel`, como foi feito na camada de
  trabalho. O objeto conferido foi a versão `s3-v1`, identificada pelo sha256 do PNG.
  O script preserva esse campo entre execuções.
- **O que NÃO foi feito:** promoção. O bloco `--- conferência ---` de `observacoes` não
  foi gravado, e `promover.py` não foi usado. As figuras seguem **pendentes**, com
  `pode_publicar=false`. A de datação mantém `autorizacao_fonte=false`.
- Os números não mudaram: só a leitura das figuras.

---

## 6. Ressalvas

1. **Retrato de 2022, não série.** O entorno mede como estão as faces em 2022. Não diz
   se a infraestrutura precedeu, acompanhou ou seguiu a ocupação.
2. **Falácia ecológica.** A unidade recebe a proporção do **setor**.
   - Um setor com 50 % de faces pavimentadas não diz quais faces, nem se as da unidade
     estão entre elas.
   - Todo resultado é "a unidade está num setor com…", nunca "a unidade tem…".
3. **Junção repartida** (§ 1): 45 % dos domicílios estão em unidades com menos de 70 %
   da área num único setor. A sensibilidade mitiga, mas não elimina: ela troca a
   incerteza por uma amostra menor.
4. **Poucos setores nos grupos pequenos.**
   - Novas: 30 setores; extintas: 21; grupos da datação: 18 e 14.
   - Nesses grupos, 3 setores levam de 30 % a 90 % do peso.
   - A retirada de um setor (§ 2.4) é o teste de fragilidade adotado.
5. **As extintas são ponderadas pelos domicílios de 2010**, porque não há domicílio em
   2022. O entorno de 2022 é o do lugar de onde os domicílios saíram, não o de onde
   eles estão.
6. **Obstáculo na calçada e rampa** só foram perguntados onde havia calçada
   (`dimensionamento.md` § 4: 10,7 % de não declarado). Setor com pouca calçada tem
   esses dois itens medidos sobre menos faces.
7. **A datação do item 3** vem de fonte não redistribuível e do mapa de 2009, com o
   polígono de 1938 generalizado (`resultados_s1.md` § 14). Os grupos herdam essa
   precisão.

## 7. O que o dado NÃO sustenta

- **Que a cidade cresceu "para onde não há infraestrutura".** As novas, onde há
  entorno, estão em setores com menos bueiro, calçada e árvore. Mas a pavimentação
  delas não se distingue da cidade de forma estável, e 287 das 354 novas nem têm
  entorno medido.
- **Que a expansão posterior a 2001 está em tecido pior servido que o preenchimento
  de vazio interno** (§ 3). O dado não separa os dois grupos, e o entorno por face não
  é publicado (§ 3.2). A pergunta fica **sem resposta**, como limitação declarada.
- **Qualquer relação de causa** entre infraestrutura e ocupação, em qualquer sentido.
- **Que a infraestrutura "chegou" ou "não chegou"** às áreas novas: não há entorno de
  2010.
- **Que as extintas saíram POR CAUSA da infraestrutura.** A associação é de setor e
  transversal: o esvaziamento medido está em setores de pior entorno. Mas o dado não
  diz que o entorno causou a saída, nem que ele já era assim em 2010.
- **Um valor de entorno para uma unidade individual.**
- **Recomendação de política urbana.** Este documento descreve.

## 8. Fecho da subordinada 3

**Resultados** (descrição, no nível do setor; § 2.4):
1. **As novas**, onde há entorno, estão em setores com **menos bueiro, menos
   arborização e menos calçada** que a cidade. A pavimentação delas não se distingue
   de forma estável.
2. **As extintas** estão em setores com **menos pavimentação e menos rampa e mais
   obstáculo na calçada**.
   - **O esvaziamento urbano acontece onde a infraestrutura é pior.** Vale para o
     esvaziamento medido, não só para o deslocamento por repartição.
3. **As esvaziadas são iguais à cidade.** **Perder domicílio não se associa a entorno
   ruim; a extinção, sim.**
4. **O adensamento**, 95 % do peso das áreas de crescimento com entorno, acompanha a
   cidade, com pavimentação um pouco menor.
5. **As favelas e comunidades urbanas são o contraste extremo:** via pavimentada ≈ 1 %,
   rampa ≈ 1 %, e a **iluminação pública cai para 90,9 %**, a única quebra da
   universalidade medida. Ali cresce o adensamento, não a expansão.

**O que não se sustenta:** as novas mais pavimentadas, com menos obstáculo, ou com mais
ônibus e ciclovia. Em todos esses casos, poucos setores levam o peso, e os valores
mudam quando eles saem.

**Limitação declarada.** A pergunta aberta pela datação — se a expansão posterior a
2001 foi para onde falta infraestrutura, enquanto o preenchimento de vazio interno se
deu em tecido já servido — **fica sem resposta**.
- Por decisão, ela não será refeita com outra junção por setor.
- O entorno por face, que a responderia, **não é publicado** pelo IBGE (§ 3.2).
- A limitação é da unidade de agregação, não do método.
