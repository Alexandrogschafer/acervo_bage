# A03 — Revisão bibliográfica para a RA'E GA

**Data:** 2026-09-25 · **Periódico alvo:** RA'E GA (ver [`submissao_raega.md`](submissao_raega.md))
· **Entradas:** [`bibliografia_a03.bib`](bibliografia_a03.bib)

Este documento prepara a revisão bibliográfica do artigo ACERVO_BAGE-A03. Ele traz:
- o protocolo e o registro da busca;
- o mapa da literatura;
- a posição dos quatro achados de método;
- a conta da regra dos 80 % de referências em periódico.

O `.bib` é **material para o responsável importar no Zotero**. O
`bibliografia/bage.bib` não foi tocado, e `referencias_bib` do manifesto continua
vazio até a importação fixar as chaves.

**Regra de conferência.** Cada entrada do `.bib` foi conferida na fonte em 2026-09-25:
- DOI resolvido na API do Crossref;
- ou página do OJS e PDF da revista ou dos anais;
- ou PDF do IBGE guardado em `data/raw/`.

Quando um campo não foi confirmado, ele ficou fora do `.bib`. Quando a referência
inteira não foi confirmada, ela ficou fora e está no § 7.

---

## 0. A lacuna, na forma declarada

**Formulação para o artigo.** A busca sistemática registrada no § 2 foi feita em
2026-09-25, com protocolo, bases, expressões e contagens anotados. Ela **não localizou
trabalho que meça o efeito dos artefatos de produção da Grade Estatística na
comparação entre as edições de 2010 e 2022**. As bases que não puderam ser consultadas
(§ 2.3) ficam declaradas como limitação da busca. A afirmação é sobre o que foi
buscado, não sobre toda a literatura existente.

*Redação anterior (até 2026-09-25): "a lacuna existe", sob o título "ninguém publicou
a comparação entre as grades de 2010 e 2022". Trocada pela forma declarada por decisão
do responsável.*

- **O que não foi encontrado.** A busca teve 38 estratos (§ 2.2). Não apareceu artigo,
  anais, tese ou preprint que:
  - compare a Grade Estatística de 2010 com a de 2022 célula a célula;
  - meça a variação de população ou de domicílios por célula;
  - discuta a comparabilidade entre as duas edições.
- **O único candidato foi descartado.** A tese de Prates (Unicamp, 2025) apareceu num
  estrato da grade e foi lida pelo responsável em 2026-09-25. Não ocupa a lacuna
  (§ 7).
- **O que o IBGE já documenta, e o artigo tem de citar.**
  - **A troca de resolução.** A nota metodológica da grade de 2022 (IBGE, 2025) dá a
    regra: a célula de 1 km de 2010 que passou a tocar setor urbano em 2022 foi
    dividida em células de 200 m ("upgrade"), e não houve "downgrade". A nota traz
    também a contagem de células das duas edições (Quadro 01). É a única comparação
    entre as edições, e é só de geometria.
  - **O método híbrido de 2010.** O IBGE (2016, p. 16–22) descreve a agregação e a
    desagregação e diz que "foi incluída uma variável para explicitar a abordagem
    utilizada para a obtenção dos dados em cada célula". Salgado et al. (2025, p. 5–6)
    repetem essa informação. O **precedente publicado** do método é D'Antona, Bueno e
    Dagnino (2013), na Rebep: uma grade regular construída sobre a Contagem 2007 pela
    agregação dos domicílios pelas coordenadas e pela desagregação dos dados por setor
    com proporcionalidade de área.
  - **A face de logradouro em 2010** (IBGE, 2016, p. 18–19) e **os níveis de
    geocodificação do CNEFE em 2022** (IBGE, 2025). O nível 4 é o "ponto médio da face
    de quadra", e os níveis 5 e 6 foram excluídos da grade.
  - **A mudança da tipologia urbano-rural de 2022.** Souza et al. (2024), autores do
    IBGE, descrevem a mudança sem medir o efeito dela na série.

**Consequência para o texto.** O artigo **não** pode dizer que a troca de resolução e o
método híbrido são desconhecidos. A lacuna defensável é **empírica**: medir quanto
esses artefatos contaminam a variação de 2010 a 2022 lida na grade. São quatro
artefatos: o refinamento de 1 km para 200 m, a desagregação de 2010, o posicionamento
pela face contra o posicionamento pela coordenada e a reclassificação dos setores.

Há um ponto a acrescentar nos achados 3 e 4, conferido no PDF da nota guardado no
acervo. O dicionário de 2022 (Quadro 04) não tem campo de método por célula. A nota de
2025 **não avisa sobre a comparabilidade com 2010**: ela lista a "Estabilidade
espaço-temporal" entre as vantagens da grade.

**Limitação declarada da busca.** As bases do § 2.3 não foram consultadas por
bloqueio ou falta de indexação. A lacuna fica sustentada pelo que foi buscado. Ficam
como **pendência menor**, que não impede a redação:
- anais da ABEP 2024 (Galoá);
- SBSR 2025 (proceedings.science bloqueou).

---

## 1. As referências de partida, conferidas

| # | referência | tipo | situação |
| --- | --- | --- | --- |
| 1 | Lobo, M. A. A. (2009). *urbe* 1(1): 71–84. Setores urbanos 1991–2000, RM de Belém | **PERIÓDICO** | conferida; **sem DOI**. As páginas divergem: 71–84 (revista) × 71–83 (Redalyc). Usado 71–84 |
| 2 | Hirye, M. C. M.; Amaral, S.; Monteiro, A. M. V.; Alves, D. S. (2016). *Revista Brasileira de Cartografia* 68(8): 1585–1599. Altamira 2000 e 2010 | **PERIÓDICO** | conferida. **Corrigido:** a primeira autora é **Mayumi** Cursino de Moura Hirye. Não há versão em anais |
| 3 | Salgado, G. P. L.; Dal'Asta, A. P.; Adorno, B. V.; Amaral, S. (2025). *Revista Brasileira de Cartografia* 77: 1–23 | **PERIÓDICO** | conferida. **Ressalva:** o artigo não cria código de método por célula. Ele **descreve** o da Grade Estatística de 2010 (IBGE, 2016) e avalia grades globais contra o Censo 2022 |
| 4 | Mendonça, P. H. R. et al. (11 autores, 2024). *e-metropolis* 15: 1–20. Expansão com desadensamento na RMSP, 2010–2022 | **PERIÓDICO** | conferida; seção especial; **sem DOI e sem número de fascículo** |
| 5 | Reis, I. A. (2013). *Anais do XVI SBSR*, p. 952–959 | **ANAIS** | conferida; ISBN não confirmado |
| 6 | Mendonça, P. H. R.; Kon, F. (2025). *Anais do IX CoUrb* (SBC), p. 29–42 | **ANAIS** | conferida. É o mesmo primeiro autor do item 4, com **um** coautor só |
| 7a | Ehrl, P. (2017). *Estudos Econômicos* 47(1): 215–229. AMC 1872–2010 | **PERIÓDICO** | conferida. **É esta a AMC a citar:** é periódico e cobre até 2010 |
| 7b | Reis, E. J.; Pimentel, M.; Alvarenga, A. I.; Santos, M. C. H. *Áreas mínimas comparáveis… 1872 a 2000*. Anais do I Simpósio Brasileiro de Cartografia Histórica | **ANAIS** | **a conferir** (§ 7): o ano (2011) e o local vêm só da citação de Ehrl |
| 7c | Reis, E.; Pimentel, M.; Alvarenga, A. I. *Áreas mínimas comparáveis… 1872 a 2000*. IPEA/DIMAC, documento no Ipeadata | **RELATÓRIO** | **a conferir** (§ 7): arquivo .doc sem série nem número. Não é Texto para Discussão |

Das sete, **quatro contam como periódico** (1, 2, 3 e 4) e mais a AMC de Ehrl (7a). As
de anais (5, 6 e 7b) e o documento do IPEA (7c) **não contam**.

---

## 2. Busca sistemática

### 2.1 Protocolo

- **Data de todas as buscas:** 2026-09-25.
- **Termos pedidos:**
  - compatibilização de setores censitários;
  - áreas mínimas comparáveis;
  - grade estatística IBGE;
  - interpolação areal dados censitários;
  - desagregação populacional;
  - dasimétrico população Brasil;
  - dinâmica domiciliar intraurbana;
  - densidade domiciliar cidade média;
  - expansão urbana adensamento censo 2010 2022.
- **Bases:** Google Scholar, Crossref (API), SciELO e o OJS de cada revista (RA'E GA,
  Revista Brasileira de Cartografia, Rebep, Boletim de Ciências Geodésicas, RBEUR e
  urbe). SciELO e Cadernos Metrópole foram cobertos pela Crossref, com filtro de
  prefixo ou de ISSN, porque o acesso direto foi recusado (§ 2.3).
- **Como ler as contagens:**
  - a do **Google Scholar** é o "Aproximadamente N resultados";
  - a da **Crossref** é o `total-results` da busca por relevância. Ela vem inflada,
    porque a Crossref não faz busca por frase, e só as 20 primeiras foram lidas;
  - a do **OJS** exige todas as palavras, o que explica os zeros nas expressões
    longas. Por isso houve uma segunda rodada, com expressões curtas.
- **Retidos:** itens do estrato que entraram na lista final, sem descontar
  duplicatas entre estratos.

### 2.2 Registro

**A. Estratos da lacuna (comparação entre as grades de 2010 e 2022)**

| base | expressão | resultados | aproveitados |
| --- | --- | ---: | ---: |
| Google Scholar | `"grade estatística" 2010 2022` | ~164 | 3 (Salgado; Silva, D. M.; Oliveira et al.) — nenhum compara as edições |
| Google Scholar | `"grade estatística" "censo 2022"` (desde 2024) | ~14 | 1 (Salgado) |
| Google Scholar | `"grade estatística" 2010 2022 comparação células` | ~67 | 0 novos |
| Google Scholar | `"statistical grid" IBGE 2022 2010` | ~57 | 0 |
| Google Scholar | `"grade estatística" 2010 2022 "variação" população célula` (desde 2024) | ~12 | 0 |
| Google Scholar | `"grade estatística" "2010 e 2022"` | 10 | 0 |
| Google Scholar | `"grade estatística" "desagregação" "agregação" 2022` (desde 2023) | 4 | 1 (Salgado) |
| Google Scholar | `"grade estatística" CNEFE 2022 coordenadas domicílios` (desde 2023) | 7 | 0 |
| Google Scholar | `"statistical grid" Brazil "2022 census" population` (desde 2023) | 4 | 0 |
| Google Scholar | `Bueno D'Antona "grade estatística"` | ~56 | 1 (Bueno, 2014, tese) |
| Google Scholar | `"grade estatística" "setores censitários" reclassificação urbano rural 2022` (desde 2023) | 3 | 0 |
| Google Scholar | `"grade estatística" comparabilidade 2010 2022` | ~96 | 1 lido e descartado (Prates, 2025, tese; § 7). *Corrigido em 2026-09-25: a primeira passagem registrou 0 aproveitados, sem anotar o item; ele foi reencontrado ao refazer o estrato* |
| Google Scholar | `"grade populacional" 2022 IBGE` (desde 2023) | 2 | 0 |
| Google Scholar | `IBGE "statistical grid" 2010 2022 "population change" OR "population growth" cells` (desde 2024) | 2 | 0 |
| Crossref | `"grade estatística" censo 2022` | 9.434.099 | 1 (DOI da tese de Bueno) |
| Crossref | `grade estatistica IBGE 2010 2022` | 13.147.255 | 0 |
| RBC (OJS) | `"grade estatística"` | 2 | 1 (Pedro; Queiroz Filho, 2017) |
| RBC (OJS) | `grade estatística 2022` | 7 | 0 novos |
| RA'E GA (OJS) | `"grade estatística"` | 1 | 0 (artigo sobre dengue) |
| Rebep (OJS) | `"grade estatística"` | 1 | 1 (D'Antona et al., 2015) |
| e-metropolis (OJS) | `"grade estatística"` | 0 | 0 |
| arXiv (API) | `all:IBGE AND all:grid AND all:census` | 0 | 0 |
| arXiv (API) | `all:Brazil AND all:census AND all:2022 AND all:grid` | 0 | 0 |
| busca web geral (15 expressões) | ex.: `"Grade Estatística 2010" "Grade Estatística 2022"`; `site:scielo.br "grade estatística" IBGE 2022`; `"Boletim de Ciências Geodésicas" "grade estatística"`; `SBSR 2025 anais "grade estatística" censo 2022`; `GeoInfo 2024 OR 2025 "grade estatística"` | não informado (9–10 links cada) | 4 (IBGE 2025; errata do IBGE; nota de coordenadas do IBGE, 2024; Souza et al., 2024) |

**B. Estratos temáticos: Google Scholar**

| # | expressão | resultados | aproveitados |
| --- | --- | ---: | ---: |
| 1 | `"compatibilização de setores censitários"` | 33 | 3 (Lobo, 2009; Libório et al.; Mendonça; Kon) |
| 2 | `"áreas mínimas comparáveis"` | 557 | 2 (Reis et al., AMC; Silva; Bacha) |
| 3 | `"grade estatística" IBGE` | 347 | 3 (Bueno, tese; Pedro; Queiroz Filho; Anazawa et al.) |
| 4 | `"interpolação areal" dados censitários` | 3 | 1 (Morais Junior; Silva) |
| 5 | `"desagregação populacional"` | 17 | 0 |
| 6 | `dasimétrico população Brasil` | 205 | 3 (Silva, A. P. et al.; Strauch et al.; Castro et al.) |
| 7 | `"dinâmica domiciliar" intraurbana` | 2 | 0 |
| 8 | `"densidade domiciliar" "cidade média"` | 25 | 1 (Silva, J. C. T. P. et al.) |
| 9 | `"expansão urbana" adensamento censo 2010 2022` | 2.360 | 0 (dissertações e TCCs) |
| s1 | `"moradores por domicílio" redução censo 2022` | 485 | 1 (Moura, 2026) |
| s2 | `"tamanho médio dos domicílios" Brasil` | 102 | 1 (Becceneri et al.) |
| s3 | `CNEFE endereços geocodificação censo` | 70 | 1 (Silva, L. Y. W., 2025) |
| s4 | `"Censo 2022" urbano rural classificação setores` | 1.440 | 2 (Souza et al., 2024; Rodriguez, 2024) |
| s5 | `"cidades médias" "Censo 2022" população domicílios` | 171 | 2 (Miyazaki; Silva; Lisbôa et al.) |
| s6 | `Bagé expansão urbana` | 5.870 | 0 de periódico (TCC, anais, patrimônio) |
| s7 | `"grade estatística" "Censo 2022"` | 25 | 0 novos |
| s8 | `"setores censitários" 2010 2022 comparação` | 2.880 | 0 novos |

**C. Estratos temáticos: Crossref** (`query.bibliographic`, 20 primeiros lidos)

| # | expressão | total | aproveitados |
| --- | --- | ---: | ---: |
| 1 | compatibilização de setores censitários | 10.267.667 | 2 (França et al.; Mendonça; Kon) |
| 2 | áreas mínimas comparáveis | 16.992 | 1 (Silva; Bacha) |
| 3 | grade estatística IBGE | 181.693 | 1 (Bueno, tese) |
| 4 | interpolação areal dados censitários | 32.680 | 3 (Hirye et al.; Morais Junior; Silva; Bueno; D'Antona) |
| 5 | desagregação populacional | 3.363 | 0 |
| 6 | dasimétrico população Brasil | 215.595 | 1 (Silva, A. P. et al.) |
| 7 | dinâmica domiciliar intraurbana | 13.979 | 0 |
| 8 | densidade domiciliar cidade média | 45.028 | 0 |
| 9 | expansão urbana adensamento censo 2010 2022 | 13.019.406 | 0 (dissertações e anais) |

**D. SciELO pela Crossref** (filtro `prefix:10.1590`, `type:journal-article`)

| # | expressão | total | aproveitados |
| --- | --- | ---: | ---: |
| 1 | compatibilização de setores censitários | 324.621 | 0 |
| 2 | áreas mínimas comparáveis | 1.204 | 1 (Silva; Bacha) |
| 3 | grade estatística IBGE | 509 | 0 |
| 4 | interpolação areal dados censitários | 2.750 | 0 |
| 5 | desagregação populacional | 886 | 0 |
| 6 | dasimétrico população Brasil | 30.663 | 1 (D'Antona et al., 2015) |
| 7 | dinâmica domiciliar intraurbana | 1.653 | 0 |
| 8 | densidade domiciliar cidade média | 3.350 | 1 (Lacerda, 2024) |
| 9 | expansão urbana adensamento censo 2010 2022 | 44.469 | 1 (Souza; Frutuozo, 2018) |

**E. Crossref filtrada por ISSN** (para as revistas com OJS inacessível ou busca fraca)

| revista | expressão | total | aproveitados |
| --- | --- | ---: | ---: |
| Cadernos Metrópole | setores censitários censo | 10 | 1 (Moura, 2026) |
| Cadernos Metrópole | densidade domicílios adensamento | 1 | 1 (Rios et al., 2022) |
| Cadernos Metrópole | cidades médias expansão urbana | 113 | 0 |
| Cadernos Metrópole | Censo 2022 | 68 | 0 novos |
| RBEUR | setores censitários censo | 2 | 1 (Lobo, C. et al., 2015) |
| RBEUR | densidade domicílios adensamento | 0 | 0 |
| RBEUR | cidades médias expansão urbana | 118 | 1 (Maia; Leonelli, 2025) |
| RBEUR | Censo 2022 | 65 | 0 |
| e-metropolis | as quatro expressões acima | 0 | 0 (a revista não deposita DOI) |
| Rebep | arranjos domiciliares tamanho do domicílio unipessoais | 88 | 1 (Becceneri et al.) |
| Rebep | Censo 2022 domicílios população crescimento | 380 | 1 (Silva, J. C. T. P. et al.) |
| Rebep | grade estatística população | 380 | 0 |

**F. OJS das revistas.** Na 1ª rodada foram os 9 termos, na ordem do § 2.1, alguns entre
aspas: `"compatibilização" "setores censitários"`, `"áreas mínimas comparáveis"`,
`"grade estatística"`, `"interpolação areal"`, `"desagregação populacional"` e os
demais sem aspas.

| revista | resultados por termo (1…9) | aproveitados |
| --- | --- | ---: |
| RA'E GA | 0, 0, 1, 0, 0, 0, 0, 0, 0 | 0 |
| Revista Brasileira de Cartografia | 0, 0, 2, 0, 0, 3, 0, 0, 0 | 5 (Pedro; Queiroz Filho; Alves; D'Antona; Castro et al.; Nowatzki et al.; Strauch et al.) |
| Rebep | 0, 2, 1, 0, 0, 0, 1, 0, 0 | 3 (Silva; Bacha; Nadalin et al.; D'Antona et al.) |
| Boletim de Ciências Geodésicas | todos 0 | 0 |
| RBEUR | todos 0 (índice de busca aparentemente incompleto: "censo" dá só 8 resultados) | 0 |
| urbe | 0, 0, 1, 0, 0, 0, 0, 0, 0 | 0 |

Na 2ª rodada foram expressões curtas: `"setores censitários" compatibilização`,
`dasimétrico`, `"moradores por domicílio"`, `"cidade média" "expansão urbana"`,
`adensamento domicílios censo` e `"Censo 2022" domicílios`.

| revista | resultados (1…6) | aproveitados |
| --- | --- | ---: |
| RA'E GA | 0, 0, 0, 1, 0, 0 | 0 |
| Revista Brasileira de Cartografia | 0, 3, 0, 0, 0, 2 | 1 novo (Salgado et al.) |
| Rebep | 0, 1, 0, 0, 0, 13 | 1 novo (Umbelino; Davis Jr.) |
| Boletim de Ciências Geodésicas | todos 0 | 0 |
| urbe | 0, 0, 0, 0, 0, 1 | 0 |
| urbe, conferência | `compatibilizar setores censitários` | 1 (Lobo, 2009) |
| RA'E GA, sondagem | `"setores censitários"` | 1 (Dias et al., 2025) |

**G. Clássicos internacionais.** Não houve busca por termo. Eles foram localizados pelo
nome e conferidos no Crossref: Goodchild; Lam (1980, sem DOI, conferido em bases
bibliográficas), Tobler, Openshaw, Flowerdew et al., Fotheringham; Wong, Fisher;
Langford, Eicher; Brewer, Mennis, Mennis; Hultgren, Langford, Schroeder, Schroeder;
Van Riper, Logan et al. (2014, 2016), Batista e Silva et al., Liu et al. e Bradbury
et al.

### 2.3 Bases que não puderam ser consultadas: o responsável completa à mão

| base | motivo | o que rodar |
| --- | --- | --- |
| **SciELO Search** (search.scielo.org) | HTTP 403, desafio anti-robô | os 9 termos. A Crossref com prefixo 10.1590 cobre o SciELO Brasil, mas não a contagem nem a busca por frase |
| **Boletim de Ciências Geodésicas** pelo SciELO | depende do SciELO Search | os 9 termos. O OJS da revista deu 0 em tudo, o que pode ser limitação da busca |
| **BDTD / Oasisbr** | tela de verificação de navegador | teses e dissertações: grade estatística; compatibilização de setores; Bagé |
| **Lume UFRGS** | captcha | Bagé; cidades médias gaúchas; expansão urbana na fronteira |
| **e-metropolis** (site) | conexão recusada; a revista não tem DOI no Crossref | os 9 termos |
| **OJS de Cadernos Metrópole** | tempo esgotado (substituído pela Crossref com ISSN) | os 9 termos, para ter a contagem da própria revista |
| **SBSR** (proceedings.science) | HTTP 403 | grade estatística; interpolação; dasimétrico (2015–2025) |
| **repositórios da FGV e da Unicamp** | bloqueio anti-robô | a tese de Bueno (2014), para conferir título e nível. *Prates (Unicamp, 2025) está encerrado: o responsável leu a tese em 2026-09-25 (§ 7)* |
| **anais da ABEP 2024** (Galoá) e **GeoInfo** | a busca não indexa | grade estatística 2022; comparação 2010 2022 |
| **não rodado** | fora do alcance desta sessão | Geosul, Boletim Gaúcho de Geografia, GEOUSP, Sociedade & Natureza, Mercator; Scholar em inglês; Unipampa e Urcamp (literatura local sobre Bagé) |

**Termo que faltou no protocolo.** A subordinada 3 (o entorno de 2022) não tem estrato
próprio: nenhum dos nove termos cobre "características urbanísticas do entorno" nem
"infraestrutura urbana setor censitário". Convém acrescentar esse estrato antes de
fechar a revisão.

---

## 3. Mapa da literatura: o que está resolvido e o que está em aberto

| frente | o que está resolvido (e por quem) | o que está em aberto |
| --- | --- | --- |
| **Compatibilizar recortes censitários entre censos** | Métodos para setores: Lobo (2009), Reis (2013, anais), Hirye et al. (2016), Mendonça e Kon (2025, anais, por grafos). Para municípios, a AMC: Ehrl (2017), com o Voronoi como alternativa em Silva e Bacha (2011). Mudança de suporte: Libório et al. (2020). No exterior, a harmonização temporal de setores: Schroeder (2007), Logan, Xu e Stults (2014) | Tudo isso compatibiliza **setores**. A **grade**, criada para dispensar a compatibilização, não tem estudo de comparabilidade entre edições |
| **Interpolação areal e dasimetria** | Consolidada. Internacionais: Goodchild e Lam (1980), Flowerdew, Green e Kehris (1991), Eicher e Brewer (2001), Mennis (2003). Nacionais, quase todos na Revista Brasileira de Cartografia: Strauch et al. (2014), Castro et al. (2019), Nowatzki et al. (2023), Silva, Morato e Kawakubo (2013), Amaral et al. (2012) | O erro da desagregação é estudado **no ato de estimar**. Não se estudou o que acontece quando a estimativa (2010) é subtraída de uma contagem (2022) |
| **Grade estatística e grades populacionais** | O produto e o método: IBGE (2016, 2025). Potencial e limites: Bueno e D'Antona (2017). Revisão: Silva, D. M. et al. (2024). Precedente do método híbrido: D'Antona, Bueno e Dagnino (2013), grade sobre a Contagem 2007. Usos da grade de 2010: D'Antona, Dagnino e Bueno (2015), Alves e D'Antona (2020). Adequação da célula de 200 m: Pedro e Queiroz Filho (2017). Grades globais contra o Censo 2022: Salgado et al. (2025) | **Comparação 2010 × 2022**; efeito da troca de resolução; efeito do método híbrido; o código de método por célula, que o IBGE (2016) declara e que não vem no produto distribuído (ver `resultados_s1.md` § 10.6) |
| **Base territorial e tipologia urbano-rural de 2022** | Souza et al. (2024) descrevem o novo critério. Dias et al. (2025), na RA'E GA, ligam a variação de 2010 a 2022 ao aprimoramento da base territorial | **Quanto** a reclassificação distorce a série urbano × rural de um município |
| **Domicílios × população: desadensamento** | RMSP 2010–2022: Mendonça et al. (2024). RMs paulistas: Lisbôa et al. (2024). Leitura geral do Censo 2022: Moura (2026). Arranjos domiciliares: Becceneri et al. (2021). No exterior: Liu et al. (2003), Bradbury et al. (2014) | **Cidade média fora de região metropolitana**, e **na escala intraurbana**, com separação entre expansão e adensamento. Não apareceu estudo equivalente |
| **Expansão urbana em cidade média** | Silva, Sathler e Macedo (2022), Peres e Saboya (2024), Maia e Leonelli (2025), Miyazaki e Silva (2023), Lacerda (2024) | São estudos de morfologia e segregação. Nenhum mede **quanto do crescimento de domicílios é área nova e quanto é adensamento** |
| **Adensamento** | Por quadra: Umbelino e Davis Jr. (2015). Verticalização: Lobo, C. et al. (2015), Rios et al. (2022). Centros antigos: Nadalin et al. (2018) | O adensamento **sem verticalização**, típico de cidade média, não aparece |
| **Bagé** | Não apareceu artigo de periódico sobre a expansão urbana de Bagé (Scholar, s6) | Literatura local: Unipampa, Urcamp, Lume (§ 2.3) |

**Leitura de conjunto.** A literatura brasileira sabe compatibilizar setores e
desagregar população. Ela trata a grade estatística como a unidade estável que dispensa
esse trabalho. O A03 mostra que, **entre 2010 e 2022, a grade não é estável**: mudam a
resolução, a origem do dado (modelado × contado) e o posicionamento do domicílio
(face × coordenada). Na mesma década, o rótulo urbano-rural dos setores também muda.
São problemas conhecidos da compatibilização de setores que reaparecem dentro do
produto feito para evitá-los.

---

## 4. Onde cada achado de método se insere

Os quatro achados são os de `manifesto.yaml`, `metodo_previsto`.

**1. Reclassificação de 13 setores rurais em urbanos: o falso êxodo rural.**
- **Dialoga com:** Souza et al. (2024), que dão o critério novo; Dias et al. (2025),
  base territorial 2010–2022 na RA'E GA; Bueno e D'Antona (2017), limites do setor
  como unidade. No quadro conceitual, é o efeito de zoneamento do MAUP (Fotheringham
  e Wong, 1991), aplicado ao atributo de situação e não ao limite.
- **Contribuição:** a literatura descreve a mudança de critério. O A03 **mede** o
  efeito dela numa série municipal: 67 % do ganho urbano de população e 72 % da perda
  rural. A consequência é de uso geral: a série urbano × rural pelo rótulo não serve
  entre 2010 e 2022.

**2. Troca de resolução da grade: a falsa expansão.**
- **Dialoga com:** IBGE (2025), que dá a regra de "upgrade" sem "downgrade"; a
  harmonização temporal (Schroeder, 2007; Logan, Xu e Stults, 2014); a compatibilização
  por agregação até a unidade comum (Lobo, 2009; Ehrl, 2017; Mendonça e Kon, 2025).
- **Contribuição:** a regra está documentada, mas a consequência não. Juntar as edições
  pelo `ID_UNICO` gera 40 % de expansão, contra 16,6–25,6 % na unidade harmonizada. A
  unidade harmonizada (a mãe de 1 km contra a soma das 25 filhas) é a AMC da grade:
  uma solução conhecida, aplicada a um lugar onde ninguém supunha precisar dela.

**3. Grade de 2010 híbrida, sem a variável de abordagem.**
- **Dialoga com:** IBGE (2016), fonte primária; D'Antona, Bueno e Dagnino (2013),
  precedente publicado do método (agregação pela coordenada mais desagregação por
  proporcionalidade de área, sobre a Contagem 2007); Salgado et al. (2025), que repetem
  que cada célula tem o código do método; a literatura de dasimetria sobre o erro de
  estimativa (Mennis, 2003; Eicher e Brewer, 2001; Strauch et al., 2014; Castro et al.,
  2019; Silva, D. M. et al., 2024).
- **Contribuição:** a variação de 2010 a 2022 mistura estimativa com contagem. O
  código de método que o IBGE e Salgado et al. dão como existente **não acompanha o
  produto distribuído**. Sem ele, a detecção é indireta (teste de pares idênticos
  contíguos). O pedido ao IBGE está redigido em `docs/pedido_ibge_grade_2010_abordagem.md`.
  **Atenção:** antes de o texto afirmar a ausência do campo, confirmar com o IBGE ou
  com o arquivo de outra origem. Hoje a ausência é a do produto do geoftp.

**4. Posicionamento pela face de logradouro (2010) × endereço do CNEFE (2022).**
- **Dialoga com:** IBGE (2016, p. 18–19), a repartição pela extensão da face; IBGE
  (2025), os níveis de geocodificação; Pedro e Queiroz Filho (2017), a adequação da
  célula de 200 m; Umbelino e Davis Jr. (2015), a quadra como unidade.
- **Contribuição:** é mudança de suporte do dado de entrada (Libório et al., 2020, em
  português; o MAUP em Fotheringham e Wong, 1991). Mede-se a correlação de 0,989 na
  reconstrução, 57,8 % dos endereços em face que cruza célula e 6,5 % dos domicílios
  que mudam de célula.
- **Nuance a incluir:** em 2022 o posicionamento também não é todo pela coordenada
  original. Pelos Quadros 02 e 03 da nota de 2025, conferidos no PDF do acervo, o RS
  tem:
  - 12 900 pessoas e 5 080 domicílios no nível 4, o **ponto médio da face de quadra**;
  - 617 060 pessoas no nível 2 (mediana do logradouro) e 60 057 no nível 3
    (coordenada de operação anterior), num total de 10 882 259.
  Medir a parte de Bagé nos níveis 2 a 4 fortaleceria o achado.

---

## 5. Contagem: periódico × outros

### 5.1 A lista proposta para o artigo (núcleo)

O `.bib` tem 56 entradas: 51 de periódico, 2 de anais, 2 relatórios e 1 livro. O
artigo não usará todas. O limite de 20 páginas diagramadas comporta cerca de 40
referências. O núcleo proposto é este:

| grupo | referências | n |
| --- | --- | ---: |
| periódico, nacional ou de autoria brasileira | Lobo (2009); Hirye et al. (2016); Salgado et al. (2025); Mendonça et al. (2024); Ehrl (2017); Silva e Bacha (2011); Libório et al. (2020); Dias et al. (2025); Bueno e D'Antona (2017); D'Antona, Bueno e Dagnino (2013); D'Antona, Dagnino e Bueno (2015); Pedro e Queiroz Filho (2017); Alves e D'Antona (2020); Silva, D. M. et al. (2024); Castro et al. (2019); Strauch et al. (2014); Amaral et al. (2012); Souza et al. (2024); Silva, Sathler e Macedo (2022); Peres e Saboya (2024); Maia e Leonelli (2025); Becceneri et al. (2021); Nadalin et al. (2018); Lisbôa et al. (2024); Moura (2026) | 25 |
| periódico, internacional indispensável (§ 6) | Goodchild e Lam (1980); Flowerdew, Green e Kehris (1991); Fotheringham e Wong (1991); Mennis (2003); Schroeder (2007); Logan, Xu e Stults (2014); Liu et al. (2003) | 7 |
| **total de periódicos** | | **32** |
| anais | Reis (2013); Mendonça e Kon (2025) | 2 |
| relatório do IBGE (no `.bib`) | IBGE (2016), grade; IBGE (2025), nota da grade 2022 | 2 |
| relatório do IBGE (**fora do `.bib`**, que o texto quase certamente cita) | *Metodologia do Censo Demográfico 2010* (Relatórios Metodológicos v. 41), já citada em `dimensionamento.md`; *Leia-me: comparabilidade entre as malhas de setores censitários 2010 e 2022*; *Características urbanísticas do entorno dos domicílios* (Censo 2022, subordinada 3); *Coordenadas geográficas dos endereços* (nota metodológica 01/2024) | 4 |
| **total de outros** | | **8** |

### 5.2 A conta

*Recontada em 2026-09-25, com D'Antona, Bueno e Dagnino (2013) no núcleo. Antes: 31
periódicos contra 8 outros, 79,5 %.*

| cenário | periódicos | outros | total | % periódico | 80 %? |
| --- | ---: | ---: | ---: | ---: | --- |
| núcleo como está | 32 | 8 | 40 | **80,0 %** | **sim, no limite**: qualquer "outro" a mais derruba |
| + 2 periódicos da reserva | 34 | 8 | 42 | 81,0 % | sim, mas ainda não absorve 1 "outro" a mais (34/43 = 79,1 %) |
| **+ 4 periódicos da reserva (recomendado)** | 36 | 8 | 44 | **81,8 %** | sim; absorve **1** "outro" a mais (36/45 = 80,0 %) |
| + tese de Bueno (2014) e AMC do IPEA, se entrarem | 32 | 10 | 42 | 76,2 % | não; faltariam 8 periódicos (40 / 50) |

**Regra de bolso:** a cada referência que não é de periódico, entram **4 de
periódico**, porque P ≥ 4 × O.

**A regra está atendida sem margem.** Com as 8 de fora, faltam **0 referências de
periódico para empatar** e **4 para absorver um "outro" imprevisto**, como uma nota do
IBGE que um avaliador peça. Estas estão prontas no `.bib`, na ordem de pertinência:

1. Umbelino e Davis Jr. (2015), Rebep: domicílios por quadra;
2. Rios et al. (2022), Cadernos Metrópole: adensamento;
3. Miyazaki e Silva (2023), Brazilian Geographical Journal: cidade média e setor;
4. Nowatzki et al. (2023), Revista Brasileira de Cartografia: interpolação por área ×
   dasimetria;
5. depois, se necessário: Lobo, C. et al. (2015), Eicher e Brewer (2001).

**Outras formas de ganhar folga:**
- Citar a AMC só por Ehrl (2017), que é periódico, e **não** pelo IPEA.
- Citar a grade de 2010 pelo IBGE (2016), por D'Antona, Bueno e Dagnino (2013) e por
  Bueno e D'Antona (2017), e **não** pela tese de Bueno.
- Citar o MAUP por Fotheringham e Wong (1991), que é periódico, e **não** por Openshaw
  (1984), que é livro.
- Juntar as duas notas metodológicas do CNEFE e da grade de 2022 numa citação só, se
  o texto permitir.

---

## 6. Referências internacionais: indispensáveis e dispensáveis

A RA'E GA publica em português e valoriza o diálogo com a literatura nacional. Para
quase todos os temas há equivalente brasileiro. As internacionais entram só onde o
conceito é de origem internacional e o avaliador vai procurá-lo.

| referência | decisão | motivo |
| --- | --- | --- |
| Goodchild e Lam (1980) | **indispensável** | origem da interpolação areal; qualquer seção de método sobre mudança de recorte a cita |
| Flowerdew, Green e Kehris (1991) | **indispensável** | interpolação areal em SIG, versão em periódico |
| Fotheringham e Wong (1991) | **indispensável** | o MAUP em periódico; substitui Openshaw (1984) na conta dos 80 % |
| Mennis (2003) | **indispensável** | referência da dasimetria de população; é o método que o IBGE usou para desagregar a grade de 2010 |
| Schroeder (2007) | **indispensável** | harmonização temporal de dados censitários, que é a pergunta dos achados 2 e 3 |
| Logan, Xu e Stults (2014) | **indispensável** | o caso de referência de série harmonizada de setores; contraponto direto |
| Liu et al. (2003) | **indispensável** | enquadra o descompasso: domicílios crescem mais que a população, como fenômeno geral |
| Openshaw (1984) | dispensável | clássico do MAUP, mas é **livro** e custa na conta. Só se o avaliador pedir |
| Eicher e Brewer (2001) | reserva | avaliação de métodos dasimétricos; os nacionais (Strauch; Castro) cobrem |
| Tobler (1979) | dispensável | interpolação picnofilática, método que o A03 não usa |
| Fisher e Langford (1995) | dispensável | erro da interpolação por Monte Carlo; útil só se o texto quantificar o erro de 2010 |
| Mennis e Hultgren (2006); Langford (2006) | dispensáveis | variantes da dasimetria; Strauch et al. (2014) já as trazem em português |
| Schroeder e Van Riper (2013); Logan, Stults e Xu (2016) | dispensáveis | aprofundam Schroeder (2007) e Logan et al. (2014) |
| Batista e Silva et al. (2013) | dispensável | grade europeia; Salgado et al. (2025) e Silva, D. M. et al. (2024) cobrem grades em português |
| Bradbury et al. (2014) | dispensável | repete Liu et al. (2003) em série longa |
| Amaral et al. (2012) | **manter** | revista internacional, mas autoria e caso brasileiros; conta como diálogo nacional |

---

## 7. A conferir: ficaram fora do `.bib`

| referência | o que falta |
| --- | --- |
| Reis, E. J.; Pimentel, M.; Alvarenga, A. I.; Santos, M. C. H. *Áreas mínimas comparáveis para os períodos intercensitários de 1872 a 2000*. Anais do I Simpósio Brasileiro de Cartografia Histórica | ano (2011 só pela citação de Ehrl) e local. O PDF (ufmg.br/rededemuseus/crch/simposio/) não traz |
| Reis, E.; Pimentel, M.; Alvarenga, A. I. Mesmo título. IPEA/DIMAC, .doc no Ipeadata | série, número e ano formal. Só há a data de gravação do arquivo (2007). O "IPEA 2008" que circula no Scholar não foi confirmado |
| Bueno, M. C. D. *Grade estatística…* Tese, IFCH/Unicamp, 2014. DOI 10.47749/t/unicamp.2014.937903 | título completo e nível. O Crossref traz só "Grade estatística", e o repositório da Unicamp bloqueou |
| IBGE. *Censo Demográfico 2022: coordenadas geográficas dos endereços*. Nota metodológica 01, 2024 | não está no acervo; conferir em biblioteca.ibge.gov.br (liv102063) |
| IBGE. *Leia-me: comparabilidade entre as malhas de setores censitários 2010 e 2022* | está no acervo (`data/raw/tabular/ibge/censo_2022/doc/`), mas o PDF não traz ano nem responsável; definir a forma ABNT |
| IBGE. *Metodologia do Censo Demográfico 2010* e *Características urbanísticas do entorno dos domicílios* (Censo 2022) | estão no acervo; montar as entradas no Zotero a partir dos PDFs (ano, série, ISBN) |
| França, C. J. et al. Compatibilização dos bairros… *Geografares*, n. 6. DOI 10.7147/geo6.1014 | ano: a revista diz 2008 e o Crossref, 2020. Pertinência baixa |
| Anazawa, T. M. et al. (2020). *Revista Espinhaço* 9(2): 98–110 | só vista pelo agente de busca (DOI Zenodo); não reconferida |
| Silva, L. Y. W. (2025). *Estudos Geográficos* 23(4): 1–20. CNEFE 2022 em Petrolina–Juazeiro | sem DOI; não reconferida na página da revista |
| Oliveira, G. E. T.; Körting, T. S.; Amaral, S. (2025). *Revista Brasileira de Cartografia* 77. DOI 10.14393/rbcv77n0a-69156 | não reconferida no Crossref; pertinência baixa (usa só a grade de 2010) |
| Flowerdew e Green (1989, 1994); Wong (2004): capítulos de livro | organizadores e ano dos livros não confirmados. Dispensáveis (§ 6) |

**Encerrado em 2026-09-25: Prates (2025).**
- **Referência, conforme a leitura do responsável:** PRATES, Talita de Oliveira
  Bracher. *Indicador de Vulnerabilidade Social a Inundações na Região Metropolitana
  de Campinas: Análise Crítica da Subnotificação de Eventos Hidrológicos e Impactos na
  Gestão de Riscos*. Tese (Doutorado em Geografia, Análise Ambiental e Dinâmica
  Territorial), Instituto de Geociências, Unicamp, 2025. 180 p.
- **Não ocupa a lacuna.**
  - A grade estatística é citada uma única vez, como suporte cartográfico e
    interpretativo.
  - O próprio texto declara que só as variáveis censitárias entraram na formulação do
    IVS. A unidade de análise é o setor censitário.
  - Não há nenhuma ocorrência de "célula", "200 m", "1 km", "compatibilização" nem
    "áreas mínimas".
  - A "harmonização" do trecho do Scholar é a seleção de variáveis conceitualmente
    equivalentes entre 2010 e 2022 e a coerência cartográfica dos setores. Não se
    refere às grades.
- **Decisão do responsável: não citar**, por ser tese e pela regra dos 80 %. Reavaliar
  se sair artigo derivado.
- **Registro:** foi encontrada no estrato `"grade estatística" comparabilidade 2010
  2022` do Google Scholar (§ 2.2, quadro A, corrigido).
- **Correção:** até esta data, a revisão dizia "dissertação ou tese" e "pode tocar a
  lacuna". As duas coisas eram inferência, não dado da busca.

Um item foi **descartado**: Mendes, Barja e Ferreira (2022), na RA'E GA 55, que um dos
estratos marcou como "usa a grade de 2010". O Crossref confirma que o artigo trata da
incidência de dengue em Campinas. Sem pertinência.

---

## 8. Decisões pendentes (do responsável)

1. **Importar** `bibliografia_a03.bib` no Zotero, fixar as chaves e, depois da
   exportação, preencher `referencias_bib` no `manifesto.yaml`.
2. **Pendência menor:** consultar ABEP 2024 e SBSR 2025 quando for possível. A
   lacuna já está redigida na forma declarada (§ 0), com as bases bloqueadas como
   limitação. *Prates (Unicamp, 2025) foi encerrado em 2026-09-25 (§ 7).*
3. **Escolher as 4 referências de reserva** do § 5.2, ou outras. O núcleo atende os
   80 % no limite (80,0 %), sem margem.
4. **AMC:** citar só Ehrl (2017), como recomendado, ou também a versão IPEA/anais,
   que custa um "outro" e está a conferir.
5. **Lobo (2009):** p. 71–84 (a revista, adotado) ou 71–83 (o Redalyc).
6. **Lisbôa et al. (2024):** é o único artigo de periódico sobre "domicílios ×
   população", mas a revista é de administração. Manter ou trocar.
7. **Estrato do entorno** (subordinada 3): acrescentar a busca por "características
   urbanísticas do entorno" e "infraestrutura urbana setor censitário".
