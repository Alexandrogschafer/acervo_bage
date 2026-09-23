# A03 — Dimensionamento: dinâmica domiciliar de Bagé, 2010 × 2022

**Município:** Bagé/RS (`4301602`) · **Data:** 2026-09-22 · **Status do estudo:** planejado

Este documento **mede** o rumo definido pelo responsável — população estável e
domicílios crescendo, onde isso ocorre no território e com que infraestrutura urbana —
para fechar a pergunta de pesquisa com número na mão. **Nada foi gerado:** nenhuma
camada, nada em `data/acervo/`, nada no geoportal, `manifesto.yaml` intacto. Os
intermediários estão em `derivados/` (fora do git).

Os números vêm do bruto do IBGE em `data/raw/`, pelas definições do próprio IBGE,
citadas item a item. O que o acervo **não** tem está dito como ausência, não estimado.

**Reprodução.** Scripts em [`scripts/`](scripts/), depois dos do reconhecimento:

| script | faz |
| --- | --- |
| `d01_descompasso.py` | § 1 — município: população, domicílios, não ocupados, urbano × rural |
| `d02_comparacao.py` | § 2 — Bagé × RS × Brasil e a posição de Bagé entre os municípios do RS |
| `d03_grade.py` | § 3 — redistribuição na grade estatística 2010 × 2022. **SUPERADO** em 2026-09-23 por `s1_expansao_adensamento.py` (unidade harmonizada) |
| `d04_entorno.py` | § 4 — os 10 itens do entorno 2022, por domicílio e por face |

---

## 1. O descompasso no município

Medido por `scripts/d01_descompasso.py` (`derivados/d01_descompasso.json`).

### 1.1 Os números

| | 2010 | 2022 | variação |
| --- | ---: | ---: | ---: |
| população residente | 116.794 | 117.938 | **+1.144 (+0,98 %)** |
| domicílios particulares permanentes ocupados | 38.504 | 45.295 | **+6.791 (+17,64 %)** |
| moradores por domicílio ocupado | 3,021 | 2,587 | −0,434 (−14,37 %) |
| domicílios particulares (ocupados + não ocupados) | não publicado | 53.629 | — |
| domicílios não ocupados | não publicado | 8.302 (15,48 %) | — |

A população cresceu **0,98 %** e os domicílios ocupados, **17,64 %** — 18 vezes mais.
Em 12 anos Bagé ganhou 1.144 moradores e 6.791 domicílios ocupados. É o descompasso
que o artigo quer explicar, e ele é **grande**: não depende de escolha de universo nem
de arredondamento.

### 1.2 Domicílios não ocupados em 2022, e por que não há 2010

Em 2022 o básico por setor publica a decomposição (dicionário oficial
`dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx`):

| categoria (variável) | definição do IBGE | Bagé 2022 | % dos particulares |
| --- | --- | ---: | ---: |
| ocupados `v0007` (DPPO + DPIO) | domicílio com morador na data de referência | 45.327 | 84,52 |
| **vagos** `v0009` (DPPV) | "domicílio particular permanente que não tinha morador na data de referência, mesmo que, posteriormente, durante o período da coleta, tivesse sido ocupado" | **6.411** | **11,95** |
| **uso ocasional** `v0008` (DPPUO) | "servia ocasionalmente de moradia, ou seja, era o domicílio usado para descanso de fins de semana, férias ou outro fim" | **1.891** | **3,53** |
| **não ocupados (soma)** | — | **8.302** | **15,48** |

As definições citadas são as da *Metodologia do Censo Demográfico 2010* (IBGE,
Relatórios Metodológicos v. 41, **pp. 309–310**, em
`censo_2010/doc/metodologia_censo_dem_2010.pdf`) — o documento metodológico
equivalente de 2022 **não está no acervo**, e o dicionário de 2022 só expande as
siglas. Nada foi encontrado, nas fontes que temos, indicando mudança dessas duas
definições entre 2010 e 2022; **isso é ausência de evidência de mudança, não
confirmação de estabilidade.**

**Em 2010 não há não ocupados no acervo.** Os agregados por setor de 2010 só trazem
DPP **ocupados** (`Basico V001`), e as tabelas municipais do RS da própria divulgação
(`rio_grande_do_sul.zip`, tabelas 4.23.5.1 a 4.23.5.5) também só tratam de DPP
ocupados. Vagos e uso ocasional de 2010 existem na divulgação do IBGE (Sinopse /
SIDRA), **fora** do que está em `data/raw/`. Consequência direta: **a série de
domicílios não ocupados 2010 → 2022 não é medível com o acervo de hoje** — só o
estoque de 2022. Fechar essa lacuna é uma decisão de obtenção de dado, não de método.

**Uma diferença de definição que existe e importa.** Em 2010 os domicílios
**fechados** (com morador, sem entrevista) foram **imputados** e entraram no total de
DPP ocupados (documentação dos agregados de 2010, "Tratamento dos domicílios
fechados"); a quantidade imputada não é publicada por setor. Em 2022 há imputação
equivalente, e ela é publicada: em Bagé, `v0006` dá **0,03 %** dos domicílios
particulares ocupados (≈ 14 domicílios). Os dois totais são, portanto, "ocupados com
imputação" nos dois censos, mas só em 2022 se sabe o tamanho da imputação.

### 1.3 Urbano e rural: o corte existe, mas não é comparável direto

| | 2010 | 2022 | variação |
| --- | ---: | ---: | ---: |
| população urbana | 97.765 | 114.883 | +17.118 (+17,51 %) |
| população rural | 19.029 | 3.055 | −15.974 (−83,95 %) |
| DPP ocupados urbanos | 32.642 | 44.018 | +11.376 (+34,85 %) |
| DPP ocupados rurais | 5.862 | 1.277 | −4.585 (−78,22 %) |
| não ocupados 2022, urbano | — | 7.271 | 14,17 % dos particulares |
| não ocupados 2022, rural | — | 1.031 | **44,54 %** dos particulares |

**Esse salto urbano é, em boa parte, reclassificação da Base Territorial, não
migração.** Medido pelo de/para oficial: **13 setores rurais de 2010, com 11.476
pessoas e 3.427 DPP, correspondem a áreas que em 2022 são só setores urbanos**. Isso
responde por **67 % do ganho urbano** de população (11.476 de 17.118) e por **72 % da
perda rural** (11.476 de 15.974). Qualquer leitura urbano × rural entre os dois censos
tem que descontar isso; o corte confiável para série é a **área mínima comum**
(§ 3.1 do reconhecimento), não o rótulo de situação.

O dado rural de 2022, isolado, é legítimo e diz algo forte: **44,5 % dos domicílios
particulares rurais de Bagé não são ocupados** — quase metade —, contra 14,2 % no
urbano.

### 1.4 Ressalvas de medição

- O DPPO puro (`caracteristicas_domicilio1 V00001`) é **suprimido em 4 setores** e
  falta em 1; pelo `v0007` desses mesmos setores, o que falta é **no máximo 4
  domicílios**. O total alternativo sem supressão (`v0007`, DPPO + improvisados) é
  45.327 — 32 a mais que os 45.295, entre improvisados e supressão.
- Em 2010, dois setores especiais (`…205000047` e `…205000079`) vêm com DPP em branco;
  não há supressão (`X`) no `Basico V001`.
- Toda comparação usa **DPP ocupados**, o único universo que existe nos dois censos.

---

## 2. Bagé é caso comum ou fora da curva?

Medido por `scripts/d02_comparacao.py` (`derivados/d02_comparacao.json`), somando os
setores por município: 2022 no recorte BR (todos os 5.570 municípios), 2010 no recorte
RS (único que existe no acervo).

**Conferência antes de comparar:** a soma dos setores bate com a tabela oficial de
população por município da própria divulgação de 2022
(`Populacao_residente_por_situacao_do_domicilio_municipios.xlsx`) em **5.570 de 5.570
municípios, diferença zero**. O RS de 2010 soma 10.693.929 pessoas, o total oficial do
estado.

### 2.1 Os três recortes

| | população 2010 → 2022 | ocupados 2010 → 2022 | diferença | pessoas por domicílio 2010 → 2022 | não ocupados 2022 |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Bagé** | +0,98 % | +17,72 % | **+16,74 pp** | 3,033 → 2,602 | **15,48 %** |
| **RS** | +1,77 % | +18,31 % | **+16,54 pp** | 2,971 → 2,556 | 19,97 % |
| **Brasil** | *ausente* | *ausente* | — | — → 2,800 | 19,95 % |

(Aqui "ocupados" é `v0007` em 2022 e `Basico V001` em 2010, e "pessoas por domicílio" é
população ÷ ocupados — a razão que existe nos três recortes. Em Bagé ela dá 2,602,
contra 2,587 pelo par exato do 2022, "moradores em DPPO ÷ DPPO" do § 1.)

**Brasil 2010 não está no acervo:** os agregados por setor de 2010 só existem no
recorte RS, e não há tabela municipal do Brasil em `data/raw/`. A comparação com o
Brasil fica restrita ao retrato de 2022.

### 2.2 A posição de Bagé entre os municípios do RS

O ranking usa a **diferença em pontos percentuais** entre o crescimento dos domicílios
e o da população, e não a razão entre os dois: onde a população quase não muda — o caso
de Bagé — a razão explode (18,08 em Bagé, 10,34 no RS) e não ordena nada.

| grupo | municípios | diferença de Bagé | percentil de Bagé | mediana do grupo | municípios acima de Bagé |
| --- | ---: | ---: | ---: | ---: | ---: |
| todo o RS | 496 | +16,74 pp | **62,3** | +15,87 pp | 186 |
| RS, 50 mil a 200 mil hab. (2022) | 33 | +16,74 pp | **60,6** | +16,31 pp | 12 |

| grupo | não ocupados em Bagé | percentil | mediana do grupo | municípios acima |
| --- | ---: | ---: | ---: | ---: |
| todo o RS | 15,48 % | **34,7** | 17,53 % | 323 |
| RS, 50 mil a 200 mil hab. | 15,48 % | **69,7** | 14,33 % | 9 |

A faixa de porte é **50.000 a 200.000 habitantes em 2022** (Bagé tem 117.938): são
**33 municípios** do RS. Um município do RS ficou fora de todo o pareamento — **Pinto
Bandeira**, emancipado depois de 2010, sem setores próprios naquele censo: 496 dos 497.

### 2.3 O que esses números dizem

**O descompasso de Bagé não é excepcional — é o padrão do Rio Grande do Sul.**

- **258 dos 496 municípios do RS (52 %) ganharam domicílios ocupados perdendo
  população** entre 2010 e 2022. Bagé nem chega a esse grupo: ganhou domicílios e
  ganhou população (pouca).
- 464 dos 496 (94 %) ganharam domicílios; 290 (58 %) perderam população.
- A diferença de Bagé, +16,74 pp, está no **percentil 62** do estado e perto da
  mediana do próprio grupo de porte (+16,31 pp). O RS inteiro tem +16,54 pp.
- Em vacância Bagé é **discreto no estado** (15,48 % contra mediana 17,53 %), mas
  **alto entre os municípios do seu porte** (mediana 14,33 %) — porque a vacância alta
  do RS se concentra em municípios pequenos e de veraneio.

Isso desloca a pergunta do artigo: o interessante não é *que* Bagé teve descompasso —
quase todo o estado teve —, e sim **onde** ele se materializou no território e **com
que infraestrutura**. É o que os blocos 3 e 4 dimensionam.

---

## 3. Redistribuição: a grade estatística 2010 × 2022

> **Corrigido em 2026-09-23.** Os §§ 3.1 e 3.3 foram reescritos com a unidade
> harmonizada de [`resultados_s1.md`](resultados_s1.md): a grade **não** é a mesma
> geografia nos dois anos, e a junção por `ID_UNICO` do d03 contava a troca de resolução
> como ocupação nova. O d03 está SUPERADO. O texto anterior está preservado em
> [Corrigido em 2026-09-23](#corrigido-em-2026-09-23), no fim deste documento. Regra
> geral: [`docs/ressalvas_censo_bage.md`](../../docs/ressalvas_censo_bage.md) § 7.

Medido por `scripts/d03_grade.py` (`derivados/d03_grade.json`). Células de 200 m no
urbano e 1 km no rural, quadrantes ID_14 e ID_04. Uma célula é de Bagé quando seu
**centroide** cai no município — regra única para os dois anos.

### 3.1 Conferência exigida: a grade NÃO é a mesma geografia nos dois anos

*Corrigido em 2026-09-23 (texto anterior no fim do documento). Medição:
[`resultados_s1.md`](resultados_s1.md) §§ 1 e 8, script `scripts/s1_expansao_adensamento.py`.*

**Não é, em toda parte.** A grade é aninhada, e nas 5.677 células de Bagé com o mesmo
`ID_UNICO` nas duas edições a geometria coincide (distância máxima entre centroides de
4,9 × 10⁻⁵ m, diferença máxima de área de 0,14 m²). Mas em **41 lugares do município o
IBGE refinou a resolução entre 2010 e 2022**: a célula de 1 km de 2010 aparece em 2022
como as **25 células de 200 m** que a compõem. As "41 células só em 2010 e 1.025 só em
2022" que o d03 lia como diferença de cobertura são exatamente essas 41 mães e as suas
41 × 25 filhas.

A conferência do d03 olhou só as células de mesmo ID e por isso não viu o aninhamento.
**Regra:** comparar 2010 com 2022 na **unidade harmonizada** — a mãe de 1 km contra a
soma das suas 25 filhas. O `s1_expansao_adensamento.py` faz isso e **para** se alguma
célula de uma edição não couber numa da outra ou se as filhas não cobrirem a mãe (desvio
máximo medido: 0,1 m², em ESRI:102033).

### 3.2 Ressalva: a grade de 2010 não fecha com o município

| | população | domicílios |
| --- | ---: | ---: |
| grade 2010 (centroide no município) | 114.910 | 37.908 |
| grade 2010 (qualquer célula que toca o município) | 115.191 | 38.008 |
| **município 2010 (§ 1)** | **116.794** | **38.504** |
| grade 2022 (centroide no município) | 117.977 | 45.383 |
| grade 2022 (qualquer célula que toca) | 118.198 | 45.486 |
| **município 2022 (§ 1)** | **117.938** | **45.327** |

Em 2022 a grade fecha (diferença de +0,03 % na população, explicada pela borda). Em
2010 falta **1,4 % da população e 1,3 % dos domicílios**, e isso **não é efeito de
borda** — nem incluindo toda célula que toca o município o total fecha. É coerente com
o registrado no reconhecimento (§ 3.4): em 2010 os valores por célula vêm de
agregação/desagregação do IBGE, não de contagem direta. **Uso seguro:** a grade serve
para a *geografia da mudança*; os *totais* vêm do setor e do município.

### 3.3 O que a grade mostra

*Corrigido em 2026-09-23, duas vezes; os textos anteriores estão no fim do documento.
Números da unidade harmonizada, no **cenário adotado**: o setor rural de 2010
430160205000136 fica à parte, porque a grade de 2010 foi desagregada ali
([`resultados_s1.md`](resultados_s1.md) §§ 3, 4, 10.6 e 11). A sensibilidade com todas
as unidades fica ao lado. Fonte: `derivados/s1_desagregacao_2010.json`, bloco
`efeito_nos_numeros_da_subordinada_1`.*

Das unidades harmonizadas de Bagé, **1.660 têm domicílio em algum dos dois anos**, fora
as 47 do setor 136. Com elas, são 1.707.

| | unidades | soma | mediana | p90 | máximo | sensibilidade: unidades / soma |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ganharam domicílios | 940 | **+11.372** | 4 | 25 | 579 | 945 / +12.099 |
| perderam domicílios | 557 | **−4.248** | 3 | 18 | 190 | 597 / −4.624 |
| ganharam população | 817 | +22.639 | 6 | 62,4 | 1.453 | 822 / +24.428 |
| perderam população | 777 | −19.894 | 10 | 65 | 779 | 819 / −21.361 |

**O município quase parado esconde um território em movimento.**
- Para um saldo líquido de **+7.124** domicílios, houve +11.372 de ganho bruto contra
  −4.248 de perda. São **15.620 domicílios de movimento para 7.124 de saldo, pouco mais
  de dois para um**.
- Com todas as unidades: 16.723 de movimento para +7.475 de saldo.
- Na população o contraste é maior: +22.639 contra −19.894, para um saldo de +2.745
  (+3.067 com todas as unidades).

**De onde vem o ganho de domicílios:**

| origem | unidades | domicílios | sensibilidade |
| --- | ---: | ---: | --- |
| unidades **novas** (sem domicílio em 2010) | 354 | **+1.883** | 355 / +1.884 |
| unidades que **já tinham** domicílio e cresceram | 586 | **+9.489** | 590 / +10.215 |

**A expansão fica entre 16,6 % e 25,6 % do ganho bruto**, e o restante é adensamento de
área já ocupada. Com todas as unidades, a sensibilidade é de 15,6 % a 30,1 %.
- O limite superior soma às novas o ganho de 18 unidades de 1 km (22 com todas) em que
  o IBGE passou a gradear em 200 m em 2022. Nelas, a resolução de 2010 não separa
  ocupação nova de adensamento (resultados_s1.md § 4).
- As unidades novas trouxeram **4.602 moradores** (4.604).
- Há **201 unidades** que tinham domicílio em 2010 e não têm mais, com 578 domicílios.
  Com todas as unidades são 232, com 807.

**Divergência de sinal:** **137 unidades ganharam domicílios e perderam população**,
+843 domicílios e −2.095 pessoas. São 8,3 % das 1.660 ocupadas, ou 8,0 % das 1.707. O
setor 136 não tem nenhuma delas. O caminho inverso, perder domicílio e ganhar
população, ocorre em só 7 unidades. A divergência existe, é localizada e tem direção
clara.

---

## 4. Infraestrutura: o entorno de 2022

Medido por `scripts/d04_entorno.py` (`derivados/d04_entorno.json`), nos 168 setores com
entorno por domicílio (43.744 DPPO) e nos 171 com entorno por face (7.573 faces). O
denominador de cada item é o próprio item (sim + não + não declarado), para que "não
declarado" não vire "não". A dispersão é entre setores, **cada setor com peso 1**.

| item (categoria) | % dos domicílios no município | mediana entre setores | q1 | q3 | **IQR** | % por face no município |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **via pavimentada** (sim) | 45,8 | 34,7 | 13,6 | 90,2 | **76,6** | 35,1 |
| **obstáculo na calçada** (sim) | 64,4 | 72,0 | 38,7 | 91,8 | **53,2** | 54,8 |
| **arborização** (5+ árvores) | 48,9 | 50,7 | 28,3 | 73,6 | **45,3** | 38,8 |
| **bueiro** (sim) | 65,1 | 69,1 | 51,3 | 86,9 | **35,6** | 56,9 |
| **arborização** (sem árvores) | 20,8 | 13,5 | 4,7 | 29,3 | 24,6 | 27,5 |
| **rampa para cadeirante** (sim) | 17,6 | 4,8 | 0,0 | 22,8 | 22,8 | 11,9 |
| **ponto de ônibus** (sim) | 12,5 | 9,1 | 2,9 | 14,9 | 12,0 | 7,9 |
| **calçada** (sim) | 89,3 | 97,8 | 88,8 | 100,0 | 11,2 | 78,2 |
| circulação da via (caminhão/ônibus) | 93,1 | 100,0 | 96,6 | 100,0 | 3,4 | 91,1 |
| **iluminação pública** (sim) | 99,3 | 100,0 | 99,7 | 100,0 | **0,3** | 96,2 |
| via sinalizada para bicicleta (sim) | 1,4 | 0,0 | 0,0 | 0,0 | 0,0 | 1,2 |

**A variação entre setores é grande o bastante — para alguns itens, e muito.**

- **Pavimentação separa o território como nenhum outro item:** metade dos setores está
  entre 13,6 % e 90,2 % de domicílios em face pavimentada, com p10 de 1,2 % e p90 de
  100 %. Há setores praticamente sem rua pavimentada e setores inteiramente
  pavimentados, na mesma cidade.
- **Obstáculo na calçada, arborização (5+), bueiro e rampa** também discriminam bem
  (IQR de 22,8 a 53,2).
- **Iluminação pública não discrimina nada**: 99,3 % no município, IQR de 0,3 ponto —
  é universal em Bagé. Serve como controle, não como variável de diferenciação.
- **Ciclovia e aquavia são nulos** (1,4 % e 0,0 %): não sustentam análise.
- **Calçada é quase universal por domicílio (89,3 %) mas cai para 78,2 % por face** —
  as faces sem calçada têm menos domicílios, o que já é um resultado.

**Detalhe que confirma o desenho de 2022:** "não declarado" é **0,0 %** em quase todos
os itens, mas **10,7 % em obstáculo na calçada e rampa para cadeirante** — exatamente a
fatia de domicílios em face **sem** calçada (100 − 89,3). Confirma, no dado, o que a
publicação do IBGE diz no texto: em 2022 esses dois itens só foram perguntados onde
havia calçada (§ 1.4 do reconhecimento, restrição A2 da rampa).

---

## 5. Fechamento

### 5.1 O descompasso é excepcional ou comum?

**Comum, e é isso que muda o artigo.** Bagé cresceu 17,64 % em domicílios ocupados com
0,98 % de população: diferença de **+16,74 pp**. Duas medidas diferentes situam Bagé, e
elas **não são a mesma coisa nem se somam**:

- **Posição de Bagé na distribuição da diferença.** +16,74 pp é o **percentil 62** dos
  496 municípios do RS (mediana estadual +15,87 pp; o RS inteiro, +16,54 pp) e o
  percentil 60,6 entre os 33 do seu porte. Ou seja, **186 municípios (38 %) têm
  diferença maior que a de Bagé** — 12, entre os do mesmo porte.
- **Quantos municípios estão no caso mais extremo.** **258 dos 496 (52 %) ganharam
  domicílios ocupados *perdendo* população.** Esse é **outro conjunto**, não "os que
  fizeram mais que Bagé": um município entra nele por perder população, mesmo com
  diferença menor que a de Bagé. **Bagé não está nesse grupo** — ganhou domicílios e
  ganhou população.

O que **não** é comum em Bagé é a combinação: a maioria dos municípios do estado perdeu
população (290 de 496), e Bagé ficou estável. E a vacância de Bagé (15,48 %) é baixa
para o estado (percentil 35) mas **alta para o seu porte** (percentil 70).

Conclusão para a redação do artigo: **tratar o descompasso como contexto regional
medido, não como anomalia local**. A pergunta que sobra é sobre território e
infraestrutura, não sobre a existência do fenômeno.

### 5.2 Qual das três partes tem o sinal mais forte

**A redistribuição no território (§ 3).** Em ordem:

1. **Redistribuição — sinal forte.** *(Corrigido em 2026-09-23, com os números de
   [`resultados_s1.md`](resultados_s1.md); texto anterior no fim do documento.)*
   No cenário adotado, com o setor 136 à parte (§ 3.3), são 11.372 domicílios ganhos
   contra 4.248 perdidos para um saldo de 7.124.
   - 354 unidades novas, com **16,6 % a 25,6 %** do ganho bruto.
   - 137 unidades ganham domicílio e perdem população.
   - 201 unidades se esvaziaram por completo.
   - Sensibilidade com todas as unidades: 12.099 × 4.624; 355 novas; 15,6–30,1 %; 232.

   O município parado é média de movimentos grandes e de direções opostas. Eles são
   medidos na unidade harmonizada, porque a grade **não** é a mesma geografia nos dois
   anos (§ 3.1). O setor 136 fica fora porque a grade de 2010 é modelada ali.
   *(Corrigido de novo em 2026-09-23; texto anterior no fim do documento.)*
2. **Infraestrutura — sinal forte, mas transversal.** A pavimentação varia de ~0 a
   100 % entre setores (IQR de 76,6 pontos), e mais quatro itens discriminam bem. Só
   que **o entorno só existe em 2022**: é um retrato, não uma série (§ 1.4 do
   reconhecimento — só iluminação e bueiro seriam comparáveis com 2010, e iluminação é
   universal, logo inútil para diferenciar).
3. **Descompasso no município — sinal grande, mas não distintivo.** Ele dimensiona o
   fenômeno e situa Bagé, e é o que o § 2 mostrou ser regra no RS.

### 5.3 Redação proposta da pergunta (PROPOSTA — não decidida)

> **Decidida pelo responsável em 2026-09-22.** A pergunta, as três subordinadas (com
> a 3 reescrita: iluminação entra como controle e ciclovia como ausência), o recorte
> espacial e o que fica fora estão em [`manifesto.yaml`](manifesto.yaml), que é o
> registro válido. O texto abaixo é a proposta como foi feita, mantida como está.
>
> **Nota de 2026-09-23.** Os números da subordinada 1 abaixo (5.709 / 573 / 8.461 / 568
> / 15.385) vêm da junção por ID do d03 e estão **superados**: na unidade harmonizada
> são 1.884 domicílios em 355 unidades novas, 10.215 em 590 que já tinham domicílio e
> 4.604 moradores nas novas ([`resultados_s1.md`](resultados_s1.md) §§ 3–4). O
> manifesto já traz os números corrigidos. Os da subordinada 2 (132 / +804 / −2.044)
> também estão superados: harmonizados, são 137 unidades (8,0 % de 1.707), +843
> domicílios e −2.095 pessoas (resultados_s1.md § 8). O manifesto foi corrigido em
> 2026-09-23.

**Pergunta de pesquisa.**

> Bagé ganhou 6.791 domicílios ocupados (+17,6 %) com a população praticamente estável
> (+1,0 %) entre 2010 e 2022. **Onde**, no território do município, esse crescimento de
> domicílios se materializou — em ocupação de área nova ou em adensamento da área já
> ocupada —, e **que infraestrutura urbana** existe em 2022 nas áreas que cresceram,
> comparada à do restante da cidade?

**Perguntas subordinadas.**

1. **Quanto do crescimento é expansão e quanto é adensamento?** Pela grade estatística,
   já se sabe o tamanho: 5.709 domicílios em 573 células novas e 8.461 em 568 células
   que já tinham domicílio. Falta caracterizar essas duas geografias — onde estão, que
   densidade têm e quanto de população acompanhou (15.385 pessoas nas células novas).
2. **Onde domicílio e população andam em direções opostas?** As 132 células que ganham
   domicílio e perdem população (+804 domicílios, −2.044 pessoas) são o retrato do
   encolhimento domiciliar no território — moradores por domicílio caiu de 3,02 para
   2,59 no município. Verificar se essas células formam área contígua (centro? bairros
   antigos?) ou estão dispersas.
3. **A infraestrutura do entorno acompanha onde a cidade cresceu?** Cruzar os setores
   das áreas de crescimento com os itens que discriminam — pavimentação (IQR 76,6),
   bueiro, obstáculo na calçada, arborização e rampa —, lendo 2022 como retrato
   transversal, sem série com 2010.

**Deliberadamente fora da pergunta,** com o motivo:

- **série de vagos e uso ocasional** — 2010 não está no acervo (§ 1.2); com o dado de
  2022 sozinho dá para descrever o estoque (8.302 domicílios, 44,5 % dos particulares
  no rural), não a mudança;
- **série de entorno 2010 → 2022** — só iluminação e bueiro são comparáveis pelo IBGE,
  e iluminação é universal em Bagé;
- **leitura urbano × rural entre censos** — 67 % do salto urbano é reclassificação de
  13 setores (§ 1.3).

### 5.4 O que falta decidir (do responsável) — RESOLVIDO em 2026-09-22

> Os quatro pontos abaixo foram decididos e estão no `manifesto.yaml`: o
> enquadramento regional foi aceito; as três subordinadas entraram juntas; **os não
> ocupados de 2010 NÃO serão obtidos** (a vacância não é eixo do artigo e o dado de
> 2010 só existe por município); e o recorte é grade + setor de 2022, com junção
> célula → setor e incerteza declarada.

1. Aceitar ou não o enquadramento do § 5.1 (descompasso como contexto regional).
2. Escolher entre as três subordinadas ou pedir outro recorte.
3. Decidir se vale obter os não ocupados de 2010 (fora de `data/raw/` hoje) para
   transformar o estoque de 2022 em série — é decisão de obtenção de dado, e a
   obtenção passa pelas regras do acervo.
4. Definir o recorte espacial de trabalho: grade (célula), setor 2022, ou área mínima
   comum. A grade é a única que compara território direto entre os dois anos; o setor é
   a única com entorno; a AMC é a única com série de atributo do censo.

---

## Corrigido em 2026-09-23

Texto anterior dos §§ 3.1, 3.3 e 5.2 (item 1), mantido como registro. Foi substituído
porque a conferência de geografia do d03 olhou só as células de mesmo `ID_UNICO` e não
viu que, em 41 lugares do município, a célula de 1 km de 2010 aparece em 2022 como as 25
células de 200 m que a compõem. A junção por ID com ausente = 0 contou essa troca de
resolução como 224 células "novas" (as filhas com domicílio) e 32 "extintas" (as mães),
levando a expansão a 40 % do ganho bruto. Medição que motivou a correção:
[`resultados_s1.md`](resultados_s1.md) §§ 1, 4 e 8.

<details>
<summary>Texto anterior (até 2026-09-23)</summary>

> ### 3.1 Conferência exigida: as duas edições são a mesma geografia
>
> **São.** Entre as células de Bagé, 5.677 têm o mesmo `ID_UNICO` nas duas edições, e
> nelas a **distância máxima entre centroides é 4,9 × 10⁻⁵ m** e a **diferença máxima de
> área, 0,14 m²** (tamanhos: 40.000 m² e 1.000.002 m²). As diferenças de contagem são de
> cobertura, não de malha: 41 células só na edição de 2010 e 1.025 só na de 2022 — a
> grade de 2022 cobre mais território. Como a geografia confere, a comparação célula a
> célula é legítima e o script seguiu.
>
> ### 3.3 O que a grade mostra
>
> Das 6.743 células de Bagé, **1.925 têm domicílio em algum dos dois anos**.
>
> | | células | soma | mediana | p90 | máximo |
> | --- | ---: | ---: | ---: | ---: | ---: |
> | ganharam domicílios | 1.141 | +14.170 | 4 | 27 | 293 |
> | perderam domicílios | 620 | −6.695 | 3 | 19 | 700 |
> | ganharam população | 1.023 | +31.050 | 7 | 67 | 727 |
> | perderam população | 837 | −27.983 | 10 | 70 | 2.270 |
>
> **O município quase parado esconde um território em movimento intenso.** Para um saldo
> líquido de +7.475 domicílios na grade, houve +14.170 de ganho bruto contra −6.695 de
> perda — **20.865 domicílios de movimento para 7.475 de saldo, quase três para um**. Na
> população o contraste é maior ainda: +31.050 contra −27.983 para um saldo perto de
> zero.
>
> **De onde vem o ganho de domicílios:**
>
> | origem | células | domicílios |
> | --- | ---: | ---: |
> | células **novas** (sem domicílio em 2010) | 573 | **+5.709** |
> | células que **já tinham** domicílio e cresceram | 568 | **+8.461** |
>
> Ou seja: **60 % do ganho bruto é adensamento** de área já ocupada e **40 % é ocupação
> de área nova** — e as células novas trouxeram 15.385 pessoas. Também há 261 células que
> tinham domicílio em 2010 e não têm mais.
>
> **Divergência de sinal:** **132 células (6,9 % das ocupadas) ganharam domicílios e
> perderam população** — +804 domicílios e −2.044 pessoas. O caminho inverso (perder
> domicílio e ganhar população) ocorre em só 7 células (0,4 %). A divergência existe, é
> localizada e tem direção clara.
>
> ### 5.2 (item 1)
>
> 1. **Redistribuição — sinal forte.** Movimento bruto de 14.170 domicílios ganhos contra
>    6.695 perdidos para um saldo de 7.475; 573 células novas; 132 células que ganham
>    domicílio e perdem população; 261 células esvaziadas. O município parado é média de
>    movimentos grandes e de direções opostas — e a grade está conferida como a mesma
>    geografia nos dois anos.

</details>

## Corrigido em 2026-09-23 (segunda correção): cenário adotado, setor 136 à parte

O responsável decidiu, em 2026-09-23, declarar à parte o setor rural de 2010
430160205000136, onde a grade de 2010 foi desagregada ([`resultados_s1.md`](resultados_s1.md)
§§ 10.6 e 11). Os §§ 3.3 e 5.2 (item 1) passaram a dar primeiro os números adotados. O
texto que eles tinham, com todas as unidades e ainda válido como sensibilidade, fica
abaixo.

<details>
<summary>Texto anterior (da primeira correção, até a segunda, ambas em 2026-09-23)</summary>

> ### 3.3 O que a grade mostra
>
> *Corrigido em 2026-09-23 (texto anterior no fim do documento). Números da unidade
> harmonizada, de [`resultados_s1.md`](resultados_s1.md) §§ 3, 4 e 8.*
>
> Das unidades harmonizadas de Bagé, **1.707 têm domicílio em algum dos dois anos**.
>
> | | unidades | soma | mediana | p90 | máximo |
> | --- | ---: | ---: | ---: | ---: | ---: |
> | ganharam domicílios | 945 | +12.099 | 4 | 25 | 610 |
> | perderam domicílios | 597 | −4.624 | 3 | 18 | 190 |
> | ganharam população | 822 | +24.428 | 6,5 | 63 | 1.551 |
> | perderam população | 819 | −21.361 | 10 | 66 | 779 |
>
> **O município quase parado esconde um território em movimento.** Para um saldo líquido
> de +7.475 domicílios na grade, houve +12.099 de ganho bruto contra −4.624 de perda —
> **16.723 domicílios de movimento para 7.475 de saldo, pouco mais de dois para um**. Na
> população o contraste é maior: +24.428 contra −21.361 para um saldo de +3.067.
>
> **De onde vem o ganho de domicílios:**
>
> | origem | unidades | domicílios |
> | --- | ---: | ---: |
> | unidades **novas** (sem domicílio em 2010) | 355 | **+1.884** |
> | unidades que **já tinham** domicílio e cresceram | 590 | **+10.215** |
>
> Ou seja: a **expansão fica entre 15,6 % e 30,1 % do ganho bruto** e o restante é
> adensamento de área já ocupada. O limite superior soma às novas o ganho de 22 unidades
> de 1 km em que o IBGE passou a gradear em 200 m em 2022, onde a resolução de 2010 não
> separa ocupação nova de adensamento (resultados_s1.md § 4). As unidades novas trouxeram
> **4.604 moradores**. Há **232 unidades** que tinham domicílio em 2010 e não têm mais.
>
> **Divergência de sinal:** **137 unidades (8,0 % das ocupadas) ganharam domicílios e
> perderam população** — +843 domicílios e −2.095 pessoas. O caminho inverso (perder
> domicílio e ganhar população) ocorre em só 7 unidades. A divergência existe, é
> localizada e tem direção clara.
>
> **(§ 5.2, item 1)** Movimento bruto de 12.099 domicílios ganhos contra 4.624 perdidos
> para um saldo de 7.475; 355 unidades novas, com 15,6 % a 30,1 % do ganho bruto; 137
> unidades que ganham domicílio e perdem população; 232 unidades esvaziadas por
> completo. O município parado é média de movimentos grandes e de direções opostas —
> medidos na unidade harmonizada, porque a grade **não** é a mesma geografia nos dois
> anos (§ 3.1).

</details>
