# ESTADO — diário do projeto

Registro cronológico do que foi feito, do que foi conferido e do que ficou
pendente. Entrada nova no topo.

---

## 2026-09-23 — A03: conferência visual; deslocamento por face em 2010; caracteriza a divergência

- **Conferência visual do responsável** (QGIS, imagem de satélite) sobre a camada de
  trabalho e as sete figuras.
  - Resultado: extintas de 053/054 sem ocupação visível (ruína de uma casa); novas,
    todas com residência; a divergência dispersa, com 5 rurais e 6 grandes rurais
    junto à borda, e poucas no miolo.
  - Registrada em `resultados_s1.md` § 12.1 e no `.json` da camada, em
    `verificacoes.conferencias_visuais_do_responsavel`.
  - **Não** no bloco `--- conferência ---`: por decisão do responsável, a camada não
    foi promovida. O `s1_expansao_adensamento.py` passa a preservar o campo.
  - A camada segue pendente; o `sha256_conteudo` não mudou (`f323c4ba…`).
- **Faces de logradouro de 2010 baixadas pela lista fixa** (7ª leva de
  `config/fontes_censo_ibge.yaml`): os 5 distritos de Bagé e o leia-me, com URLs lidas
  nas listagens do geoftp e sha256 fixados. A fonte nova é
  `ibge_censo2010_faces_logradouros`, no catálogo e no manifesto.
- **`scripts/s1_faces_2010.py`** → `derivados/s1_faces_2010.json` (`resultados_s1.md`
  §§ 12.2–12.4).
  - A repartição uniforme pela face reproduz a grade de 2010 no urbano (correlação
    0,989).
  - Das 56 extintas urbanas, 47 são atravessadas por face cuja maior parte cai em
    outra célula. Das 608 casas do CNEFE 2022 nessas faces, 607 estão fora da
    extinta, com mediana de 138 m.
  - Pelo mecanismo: 29 somem com o reposicionamento (95 domicílios), e 23 estão em
    face que perdeu os endereços (244), entre elas 8 das 10 de 053/054.
  - 57,8 % dos endereços urbanos de 2010 estão em face que cruza células, e cerca de
    2,1 mil domicílios (6,5 %) mudam de célula.
  - Efeito na faixa da expansão: 16,6–25,6 % → 17,1–26,6 % (17,3–26,6 % na variante
    conservadora).
  - **Proposta pendente de decisão** (§ 12.4): manter as classes e declarar a
    repartição como quarto achado de método. Ressalva geral em
    `docs/ressalvas_censo_bage.md` § 10.
- **`scripts/s2_divergencia.py`** → `derivados/s2_divergencia.json`, e o novo
  `resultados_s2.md` (subordinada 2, em andamento).
  - Contiguidade: 40 isoladas, mas 63 em 6 agrupamentos de 5 ou mais, e pares acima
    do acaso (95 contra 59,7).
  - Rurais: 6 junto à borda (5 harmonizadas) e 8 remotas.
  - Razão: as rurais convergem (4,0 → 2,0); nas urbanas há as duas coisas (3,13 →
    2,52, contra 3,06 → 2,68).
  - As divergentes estão acima do esperado no miolo, 22 contra 10,2 esperadas a até
    1 km do centro. A unidade a leste é o núcleo rural de Quebrachinho.
- **Nada reclassificado.**

---

## 2026-09-23 — A03: unidades à parte marcadas na camada; subordinada 2 no cenário adotado

- **Camada de trabalho:** ganhou o campo booleano `a_parte_setor_136` (47 unidades).
  - Ele é gravado por `s1_expansao_adensamento.py`, a partir da lista de
    `s1_desagregacao_2010.json`. O `s1_desagregacao_2010.py` PARA se a marca divergir
    da lista.
  - O `sha256_conteudo` passou de `78a8800b…` para **`f323c4ba…`**, com o `.json`
    irmão atualizado. A camada segue pendente, sem promoção.
  - A cadeia foi rodada de novo: s1 → s1_extintas → s1_desagregacao_2010 →
    s1_geografias → s1_figuras. O `s1_caracterizacao.json` ficou byte a byte igual, e
    nos demais JSONs só mudaram o sha da camada e as datas.
- **Manifesto:**
  - chave nova `saidas_de_trabalho`, com o `sha256_conteudo` da camada e o anterior em
    comentário;
  - subordinada 2: "8,3 % das 1.660 (cenário adotado); 8,0 % das 1.707 com todas as
    unidades", com o texto anterior em comentário datado. As 137 unidades e o
    +843 / −2.095 não mudam.
- **`resultados_s1.md` §§ 5.1, 5.2 e 11.1:** parte do esvaziamento é **urbano de borda,
  não só rural**.
  - No cenário adotado, 59,5 % dos domicílios extintos estavam em setores urbanos de
    2010 (42,6 % com todas as unidades).
  - 71,1 % estão a até 1 km da área urbanizada de 2022.
  - O maior agrupamento passa a ser o urbano dos setores 053 e 054, e a mediana cai de
    4,74 para 3,89 km.
  - **Ressalva:** a posição de 2010 no urbano vem da face de quadra.
  - Os números saem do bloco `extintas_urbano_de_borda` do `s1_geografias.json`.

---

## 2026-09-23 — A03: textos no cenário adotado; geografias e figuras refeitas

- **Textos remetidos ao cenário adotado** (setor 136 à parte primeiro, todas as
  unidades como sensibilidade, texto anterior em correção datada):
  - `dimensionamento.md` §§ 3.3 e 5.2;
  - `docs/ressalvas_censo_bage.md` § 7;
  - `metodo_previsto` item 2 do manifesto;
  - README;
  - `resultados_s1.md` §§ 1 (nota), 3, 4 e 8, reordenados para o adotado vir primeiro.
  - **Grep final** por 15,6 / 30,1 / 12.099 / 4.624 / 232 / 807: o que sobra é
    sensibilidade rotulada, bloco de correção, o conjunto investigado no § 10 ou este
    diário.
- **Geografias do § 5 refeitas** por `scripts/s1_geografias.py`, com
  `derivados/s1_geografias.json` nos dois cenários.
  - Adensadas: 93,1 % dos domicílios dentro da área urbanizada (89,4 % com todas).
  - Extintas: mediana ponderada de 3,89 km (4,74 km); o maior agrupamento passa a ser
    o urbano dos setores 053 e 054.
  - O cenário "todas as unidades" reproduz o `s1_caracterizacao.json`, salvo a ordem de
    um empate num top-10 não publicado.
- **`s1_desagregacao_2010.py`** grava a lista das 47 unidades à parte, o sha da camada
  e o `movimento_e_divergencia` de cada recorte.
- **Sete figuras refeitas** (`s1-v2`):
  - setor 136 hachurado e contornado em todas, explicado na legenda;
  - contagens da legenda no cenário adotado;
  - **figura 7 nova:** as 137 unidades da divergência de sinal (subordinada 2), recorte
    urbano. As 8 rurais fora do recorte estão declaradas no próprio mapa.
- **Conferência por imagem de ~2010** (setores 136, 053 e 054): **encerrada como
  dispensada**. O setor 136 já está à parte, e a conferência não mudaria decisão.
- **Pedido ao IBGE:** segue sem envio.

---

## 2026-09-23 — A03: subordinada 1 fechada, com o setor 136 à parte

- **Decisão do responsável:** o setor rural de 2010 430160205000136 fica à parte na
  subordinada 1.
  - **Números adotados:** expansão de 16,6–25,6 % do ganho bruto de 11.372; 201
    extintas com 578 domicílios; perda bruta de 4.248.
  - **Sensibilidade com todas as unidades:** 15,6–30,1 %; 232 extintas com 807; perda
    bruta de 4.624.
  - A subordinada 2 não muda: as mesmas 137 unidades de divergência.
  - `s1_desagregacao_2010.py` passou a gravar a tabela por classe dos três recortes.
- **`resultados_s1.md`:**
  - aviso no topo;
  - §§ 3, 4, 7 e 8 com o cenário adotado, com o texto anterior em correção datada;
  - § 10 com o **piso** e o descarte do teste A como parte do método;
  - **§ 11 novo, de conclusão.**
- **Manifesto:** a subordinada 1 está **CONCLUÍDA**, com o texto anterior em comentário.
  O status do estudo continua `planejado`. O README foi atualizado.
- **Ressalvas:**
  - § 8: o piso e o descarte;
  - **§ 9 novo:** as listas de nível de geocodificação (notas 2022 × dicionário do
    CNEFE) divergem nos níveis 2, 3 e 5.
    - O dado de Bagé confirma o dicionário no nível 2.
    - Nenhuma contagem depende da lista.
    - Uma frase do § 10.4 estava errada e foi corrigida: os níveis 2 a 4 somam 4.621
      endereços, não 86.
- **Pedido ao IBGE:** completado com o remetente (Alexandro Schafer, UNIPAMPA, Campus
  Bagé, projeto ACERVO_BAGE) e a finalidade. O e-mail fica fora do repositório. **Não
  enviado.**

---

## 2026-09-23 — A03: grade de 2010 híbrida; detecção indireta da desagregação

- **Documentação da grade baixada** pela lista fixa (commit `de4a7de`):
  `grade_estatistica.pdf` (2010) e `Notas_metodologicas_grade_estatistica_2022.pdf`.
- **Grade de 2010.** É híbrida por método: setor com mais de 50 % de ausência de
  localização entra por desagregação. A variável de abordagem por célula (p. 21) **não
  vem nos arquivos do geoftp**, e a regra não se reconstrói (a ausência por setor não é
  publicada).
- **Grade de 2022.** É contagem de pontos do CNEFE (níveis 1 a 4). A regra do upgrade
  1 km → 200 m confere com as 41 mães medidas (41/41).
- **`scripts/s1_desagregacao_2010.py`** gera `derivados/s1_desagregacao_2010.json`,
  que é versionado:
  - **Teste A** (a razão da célula é a do setor): 26,3 % de compatíveis em 2010 contra
    21,7 % em 2022. Não discrimina, **descartado**.
  - **Teste B** (pares idênticos contíguos): 4 células em 2010 e 0 em 2022, todas no
    setor rural 430160205000136. Esse setor tem 968 domicílios de 2010, 31 das 232
    extintas e 27 das 147 sem endereço.
  - Tratar o setor à parte deixa a faixa da expansão em 16,6–25,6 %.
  - Nada reclassificado.
- **Registrado:**
  - `resultados_s1.md` § 10 reescrito (§§ 10.4, 10.6 e 10.7);
  - `docs/ressalvas_censo_bage.md` § 8 novo;
  - o terceiro achado no `metodo_previsto` do manifesto e no README;
  - a documentação da grade entrou no manifesto como fonte bruta.
- **Pendente:** o pedido ao IBGE está redigido em
  `docs/pedido_ibge_grade_2010_abordagem.md` e **não foi enviado**. Falta decidir o
  canal e quem assina.

---

## 2026-09-23 — A03: investigação das unidades extintas sem ocupação visível

- **Motivo.** Na conferência visual, o responsável viu parte das 232 extintas sobre área
  sem ocupação visível em imagem. **Investigado, sem reclassificar:** a camada de
  trabalho e as classes ficaram como estavam, e o script confere o `sha256_conteudo`
  (`78a8800b…`) antes de ler.
- **`scripts/s1_extintas.py`** gera `derivados/s1_extintas.json`, que é versionado, e
  `derivados/s1_extintas_unidades.gpkg`, fora do git, para a conferência no mapa.
  Resultado em `resultados_s1.md` § 10.
- **Manifesto:** entraram duas fontes brutas, `ibge_cnefe2022` e
  `ibge_censo2010_malha_setores`.
- **Achados:**
  - 140 das 232 extintas tinham 1 domicílio em 2010.
  - Extintas e novas são vizinhas **menos** que o acaso (105 contra 158 pares na
    rainha), então o deslocamento entre vizinhas não se sustenta.
  - A grade não tem supressão de célula pequena.
  - 62 extintas têm domicílio no CNEFE 2022, o que indica desocupação real com a
    construção de pé.
  - 147 extintas não têm nenhum endereço (634 dos 807 domicílios). Nelas é compatível,
    mas não comprovado, que a posição de 2010 estivesse fora do lugar. O maior bloco
    fica no setor rural 430160205000136 de 2010.
- **Pendente (decisão do responsável):**
  - conferência por imagem de ~2010;
  - obter `grade_estatistica.pdf` (2010) e as notas da grade de 2022;
  - declarar a faixa de expansão de sensibilidade 11,6–26,1 %.

---

## 2026-09-23 — A03: subordinada 2 harmonizada; agregados do § 8 no script

- **Subordinada 2 do manifesto.** 132 células / +804 / −2.044 (junção por ID do d03) →
  137 unidades (8,0 % de 1.707) / +843 / −2.095, citando `resultados_s1.md` § 8; texto
  antigo em comentário datado. Resolve a pendência da entrada anterior. A nota do
  dimensionamento § 5.3 foi atualizada; a proposta ficou como foi feita.
- **`s1_expansao_adensamento.py`** ganhou os blocos `movimento_e_divergencia` e
  `troca_de_resolucao_em_bage` em `derivados/s1_caracterizacao.json` (antes medidos à
  mão). Rodado de novo: os 11 grupos de números do § 8 bateram com a saída, sem
  divergência. O JSON só ganhou linhas. A camada de trabalho foi regravada com o mesmo
  `sha256_conteudo` (`78a8800b…`); mudaram só o sha256 dos bytes e a `data_producao`
  do `.json` irmão. As figuras não foram refeitas (o conteúdo da camada é o mesmo).
- **README do A03.** Corrigida a frase que dava `setores_2022` como não publicável: ela
  está conferida e publicável desde 2026-09-22, e o estudo resolve para
  `pode_publicar=true` (13 entradas conferem). As saídas da subordinada 1 seguem
  pendentes e não publicáveis.

---

## 2026-09-23 — A03: números superados pela harmonização corrigidos; ressalva geral

- **Correção.** Os números da junção por `ID_UNICO` (573 células novas / 5.709
  domicílios / 15.385 pessoas; 568 / 8.461; 261 extintas; 14.170 × 6.695) foram
  trocados pelos da unidade harmonizada (`resultados_s1.md`) no dimensionamento §§ 3.1,
  3.3 e 5.2, na subordinada 1 e no `recorte_espacial` do manifesto e no README do A03.
  O texto antigo ficou em bloco de correção datado (dimensionamento: seção "Corrigido em
  2026-09-23"; manifesto: comentário acima de cada item). A afirmação de que a grade é
  "a mesma geografia" nos dois anos foi substituída pela regra da unidade harmonizada.
  - A nota da proposta em § 5.3 do dimensionamento foi acrescentada; a proposta ficou
    como foi feita.
- **Achado da conferência.** As "41 células só em 2010 e 1.025 só em 2022" que o d03
  lia como diferença de cobertura são exatamente as 41 mães de 1 km e as 41 × 25 filhas.
- **Ressalva geral.** `docs/ressalvas_censo_bage.md` § 7: troca de resolução da grade,
  com os números medidos e a regra de uso. `metodo_previsto` do manifesto ganhou o
  segundo achado de método (troca de resolução, ao lado da reclassificação dos 13
  setores).
- **d03 SUPERADO** por `s1_expansao_adensamento.py` (docstring e README), sem apagar.
  A leitura da grade (`ler_grade`) foi para `scripts/grade_estatistica.py`, usado pelo
  s1 e pelo d03; o d03 rodou de novo e `d03_grade.json` saiu idêntico.
- **`resultados_s1.md`.** § 8 com os equivalentes harmonizados do dimensionamento § 3.3
  (movimento bruto 12.099 × 4.624; divergência de sinal em 137 unidades, +843 / −2.095),
  medidos sobre a camada de trabalho. § 9: perímetro urbano legal **não** será obtido
  nesta etapa, por decisão do responsável.
- **Pendente (decisão do responsável):** a subordinada 2 do manifesto ainda cita
  132 células / +804 / −2.044 do d03; harmonizado é 137 / +843 / −2.095.

---

## 2026-09-22 — A03, subordinada 1: expansão e adensamento na grade

- **Limpeza.** Removidos o bruto legado `data/raw/vetor/RS_Municipios_2025.zip` e o
  `.json` dele. O sha256 (`d70d47cc…`) era idêntico ao canônico em
  `ibge/municipio_2025/`, conferido antes de apagar. O `CLAUDE.md` foi atualizado com a
  situação real dos estudos.
- **Área urbanizada 2022.** Baixada pela lista fixa, 5ª leva de
  `config/fontes_censo_ibge.yaml`. A URL foi obtida navegando o geoftp até
  `…/areas_urbanizadas_do_brasil/2022/Shapefile/`. sha256 `5e41d6c7…`, 54,5 MB. A fonte
  `ibge_areas_urbanizadas_2022` entrou no catálogo e nas `fontes_brutas` do manifesto
  do A03.
- **Achado de método: a grade de 2022 não é a de 2010 em toda parte.** 41 células de
  1 km de 2010, no município, aparecem em 2022 como 25 células de 200 m cada. O d03 as
  juntou por `ID_UNICO` com ausente = 0: 224 das 573 "novas" e 32 das 261 "extintas"
  eram troca de resolução. `scripts/s1_expansao_adensamento.py` compara na **unidade
  harmonizada** e para se a grade não fechar.
- **Resultado harmonizado.** 355 novas (+1.884 domicílios, +4.604 moradores), 590
  adensadas (+10.215), 165 estáveis, 365 esvaziadas, 232 extintas. A expansão fica
  entre **15,6 % e 30,1 %** do ganho bruto de domicílios; o d03 dava 40 %.
  - As adensadas formam um agrupamento contíguo de 481 unidades, com 93 % dos
    domicílios da classe; 89 % dos domicílios estão dentro da área urbanizada.
  - As novas são fragmentadas (208 agrupamentos) e têm 51 % dos domicílios dentro da
    área urbanizada.
  - As extintas são rurais: 95 % dos domicílios fora da área urbanizada.
  Detalhes em `estudos/A03_expansao_adensamento/resultados_s1.md`.
- **Conferência.** A grade de 2010 fica 1,61 % abaixo do município na população e
  1,55 % nos domicílios (regra do centroide), registrado sem correção. A de 2022 fecha
  (+0,03 % e +0,12 %).
- **Saídas** (fora do git, cada uma com `.json` pendente): camada de trabalho
  `saidas/s1_celulas_2010_2022.gpkg` e 6 mapas `saidas/s1_mapa_*.png`. Nada foi para o
  acervo nem para o geoportal.
- **Ambiente.** matplotlib acrescentado a `requirements.txt` e ao lock.
- **Não reescritos:** `d03_grade.json`, o dimensionamento § 3.3 e o texto da
  subordinada 1 no manifesto. Eles citam 573 / 5.709 / 15.385; a correção é decisão
  do responsável.

---

## 2026-09-22 — Promoção por linha de comando; vetor_ibge no esquema atual; vácuo

- **`limite_municipal`, nota.** A frase "Conferido visualmente no mapa em
  2026-09-20." foi movida para o bloco `--- conferência ---` da linha do
  catálogo, com o texto inalterado.
- **`vetor_ibge.py`, esquema atual.** Grava o `.json` por `metadados.montar`
  (status, pode_publicar, observacoes, sha256_conteudo, medidas, verificacoes).
  Campos antigos que ele não gera vão para `complementos`
  (`area_km2_geometrica_recalculada_em`, `data_acesso` e `data_processamento`
  de 2026-09-20). Mudanças no modo de rodar:
  - `--local` não usa a rede: lê o ZIP já em `data/raw/vetor/ibge/municipio_<ano>/`
    e aborta se o conteúdo divergir do registrado;
  - o modo online delega a navegação e o download a `baixar_malhas_ibge.py`.
- **`limite_municipal`, regravação.** O `.json` foi regravado com `--local`,
  sem rede. O `sha256_conteudo` (`33770372a09e…`) bate no arquivo em disco e no
  gerado do ZIP, e o GeoPackage não foi regravado (sha256 `a5618d27fbe6…`
  mantido). Continua conferido e publicável, com a nota no bloco do `.json` e
  do catálogo. Uma segunda execução não mudou nada.
- **Vácuo.** Só conta como vazio o manifesto sem `camadas:` E sem
  `fontes_brutas:`. Manifesto só com fontes brutas publicáveis agora resolve
  para true (`convencoes.md` § 7).
- **`scripts/utils/promover.py`.** Promove por `--id` (`id_camada` ou caminho) e
  `--nota`. Confere o hash e a fonte antes de gravar, e `pode_publicar` nunca
  sai mais permissivo que a fonte. Documentado em `convencoes.md` § 1 e no
  README.
- **Controles.** `testar_validador.py`: 38/38, sendo 8 novos (V1–V2, PR1–PR5, VI1).
- **Estado final.** Os quatro produtos de limites estão conferidos, com a nota
  no bloco: setores, distritos, área de estudo e limite municipal.
- **Não mexido:** o bruto legado `data/raw/vetor/RS_Municipios_2025.zip` e o
  `.json` dele, do layout anterior, idênticos em sha256 ao canônico em
  `ibge/municipio_2025/`. Nenhum script lê mais esse caminho.

---

## 2026-09-22 — Nota de conferência preservada; fontes brutas na regra de publicação

Resolve o "Atenção" da entrada abaixo.

- **Nota de conferência.** Agora fica num bloco `--- conferência --- … --- fim da
  conferência ---` dentro de `observacoes`, gravado por `metadados.promover()` +
  `catalogo.promover()`. Ao regravar: o mesmo conteúdo preserva status,
  `pode_publicar` e bloco; conteúdo novo despromove (pendente, `false`, sem
  bloco). Regravação nunca promove. A regra está em `metadados.escrever()`,
  `catalogo.upsert()` e `catalogo.registrar_regravacao()`, e com isso vale para
  `limites_ibge.py`, `area_estudo.py`, `vetor_ibge.py` (linha de
  `limite_municipal`) e os três scripts de download. O validador recusa bloco em
  produto pendente. A regra está descrita em `convencoes.md` § 1.
- **Migração.** As notas de setores, distritos e área de estudo foram movidas
  para o bloco, sem mudar o texto. Depois disso `limites_ibge.py` e
  `area_estudo.py` rodaram de novo: os três seguem conferidos e publicáveis, com
  o bloco intacto no `.json` e no catálogo. Uma segunda execução não mudou
  nenhum byte.
- **Área de estudo.** `config/area_estudo.json` ganhou `sha256_conteudo`
  (`53c4eee1c72e…`). O GeoJSON só é substituído se o conteúdo mudar.
- **Publicação.** `pode_publicar_estudo` aplica o mais restritivo a camadas E
  fontes brutas (`convencoes.md` § 7). A03 segue publicável: 2 camadas e 10
  fontes brutas, nenhum bloqueio.
- `testar_validador.py`: 30/30, sendo 10 controles novos (C1–C8 conferência,
  P1–P2 publicação).
- `limite_municipal` continua conferido, mas a nota dele (de 2026-09-20) está
  solta no texto, fora do bloco, e não foi tocada.

---

## 2026-09-22 — Limites: setores, distritos e área de estudo promovidos a conferido

O responsável conferiu os produtos de limites no QGIS, sobre imagem de satélite,
e aprovou. Promovidos a `status_conferencia=conferido` e `pode_publicar=true`
(a fonte autoriza, `autorizacao_fonte=true`):

| produto | onde está registrado | sha256 congelado | sha256_conteudo |
| --- | --- | --- | --- |
| `setores_2022` | `.json` irmão + `catalogo_camadas.csv` | `392674608e4c…` | `452fcc5f2426…` |
| `distritos_2022` | `.json` irmão + `catalogo_camadas.csv` | `e49445a3f970…` | `84fe4b6792d6…` |
| `config/area_estudo.geojson` | `config/area_estudo.json` (fora do catálogo) | `b0144fc34253…` | — (o `.json` não tem esse campo) |

`limite_municipal` já estava conferido desde 2026-09-20 e não foi tocado.

**Antes de gravar**, os hashes foram recalculados a partir dos arquivos: setores e
distritos batem nos dois hashes (bytes e conteúdo) com o `.json` e o catálogo; a
área de estudo bate no sha256 de bytes. O que foi conferido é o que está congelado.

**O que foi conferido no mapa:**

- cobertura do município sem vão nem sobreposição entre setores;
- limites urbanos seguindo eixos de via e quadras;
- setores de divisa são rurais: a diferença contra o limite de 2025 fica nas
  bordas externas e vem da revisão de divisa entre as edições da malha, não de
  erro de processamento.

**Números:** o responsável citou 929.471 m² contra o limite de 2025 e
1.188 m² contra o de 2022. São medidas em EPSG:31981 (plano, como mede o QGIS):
a primeira é a área dos setores fora do limite de 2025, a segunda a diferença
simétrica contra o limite de 2022. No CRS de área do acervo (ESRI:102033), as
mesmas medidas valem 927.741 m² e 1.186 m², que são os valores já gravados em
`verificacoes`. As observações registram os dois pares, cada um com seu CRS.

**Efeito no A03:** `pode_publicar_estudo("A03_expansao_adensamento")` passou de
`false` (bloqueio: `setores_2022: pode_publicar=false no catálogo`) para `true`:
as 2 camadas declaradas conferem e são publicáveis. As 10 fontes brutas também
estão ok e publicáveis. O comentário do manifesto que avisava do bloqueio foi
atualizado; os sha256 fixados não mudaram.

**Atenção:** `limites_ibge.py` e `area_estudo.py` mantêm o status conferido ao
rodar de novo, desde que o dado seja o mesmo, mas **reescrevem `observacoes`**
com o texto padrão de cada script. O registro da conferência nas observações se
perderia e ficaria só neste diário e no histórico do git.

---

## 2026-09-22 — Censo: bruto do IBGE em `data/raw/`, download direto

Dado bruto oficial pertence a `data/raw/`, não ao acervo. Os 50 arquivos de dado
do Censo (2000, 2010, 2022) e do CNEFE 2022 foram **movidos** de
`data/acervo/censo/` (sha256 conferido antes e depois de cada movimento):

| de | para |
| --- | --- |
| `data/acervo/censo/<ano>/tabelas/` | `data/raw/tabular/ibge/censo_<ano>/` |
| `data/acervo/censo/<ano>/documentacao/`, dicionários do CNEFE | `data/raw/tabular/ibge/censo_<ano>/doc/` |
| `data/acervo/censo/<ano>/malha/` | `data/raw/vetor/ibge/censo_<ano>/` |
| `data/acervo/censo/2022/malha/ftp_com_atributos/` | `data/raw/vetor/ibge/censo_2022/malha_com_atributos/` |
| `data/acervo/censo/2022/cnefe/` (zips) | `data/raw/vetor/ibge/censo_2022/cnefe/` |
| `.json` irmãos antigos, `FONTE.md`, manifestos do REVIA_BG | `docs/procedencia/revia_bg_censo/` (sem edição) |

- `scripts/download/baixar_censo_ibge.py` baixa direto do IBGE a partir da lista
  fixa `config/fontes_censo_ibge.yaml` (gerada uma vez dos manifestos do REVIA_BG);
  `--verificar` confere a origem por HEAD. Em 22/09: 50/50 iguais à origem.
- `scripts/download/censo_revia_bg.py` está SUBSTITUÍDO e não grava mais.
- `data/acervo/censo/` ficou vazia (`.gitkeep`): é para as camadas curadas do
  censo (setores com agregados, harmonização), não para o bruto.
- As entradas de 2026-09-20 abaixo descrevem o estado daquele dia; os caminhos
  nelas são os da época e não foram reescritos.

---

## 2026-09-20 — Reestruturação: acervo compartilhado + estudos derivados

Substitui a estrutura anterior. **Nada foi apagado: tudo que existia foi
movido ou migrado de esquema**, e o que mudou de lugar está listado abaixo.

### O que foi movido

| de | para | volume |
| --- | --- | --- |
| `data/raw/censo/` | `data/acervo/censo/` | 110 arquivos, 987 MB |
| `data/processed/` | `data/acervo/limites/` | GeoPackage + `.json` |
| `js/layers.js`, `js/map-init.js` | `estudos/A02_portal/scripts/` | portal anterior |
| `css/style.css` | `css/estilo.css` | renomeado |

O Censo foi para `data/acervo/censo/` porque `censo` é um dos temas nomeados
do acervo: deixá-lo em `data/raw/` ao lado de um `data/acervo/censo/` vazio
recriaria a duplicação que a reestruturação existe para eliminar. As 9
referências de caminho (script de cópia, catálogo, `ressalvas_censo_bage.md`,
este diário) foram atualizadas junto.

`data/processed/` deixou de existir: a "produção" virou o próprio acervo.

### Catálogos migrados de esquema

As colunas mudaram por inteiro. As 11 fontes e 1 camada foram **convertidas,
não recriadas**:

- `catalogo_fontes.csv`: `id`→`id_fonte`, `autorizacao_para_republicar` (sim/não)
  → `autorizacao_fonte` (bool), mais `formato`, `tamanho_bytes` e
  `pode_publicar`. `tamanho_bytes` foi recuperado dos `.json` irmãos por
  casamento de sha256 (10 das 11 fontes; a 11ª é fonte de conferência sem
  cópia local).
- `catalogo_camadas.csv`: `id`→`id_camada`, e as colunas
  `arquivo_producao`/`arquivo_publicacao` colapsaram em **um só** `arquivo`,
  apontando para a cópia do acervo.

As colunas do esquema antigo que o novo não tem (`tema` da fonte,
`resolucao_ou_escala`, `periodo`, `script_responsavel`, `nome` da camada, o
caminho de publicação) foram **preservadas dentro de `observacoes`**, entre
colchetes — nenhum conteúdo foi descartado.

### Novo: `config/config.yaml` e `scripts/utils/`

Município, CRS e os 32 caminhos passaram a sair de `config/config.yaml`. Os
scripts existentes (`vetor_ibge.py`, `common.py`, `recorte_municipio.py`,
`exportar_*.py`, `validar_catalogos.py`) foram reescritos para lê-los de lá —
não há mais `"EPSG:31981"` nem `"4301602"` literal fora do YAML.

Módulos novos: `paths.py`, `nomes.py`, `metadados.py`, `manifesto.py`,
`publicacao.py`, `indice.py`, `verificar_publicacao.py`. `hashes.py` ganhou
tamanho em bytes e conferência.

### Barreira de publicação

`.githooks/pre-commit` + `git config core.hooksPath .githooks`. Testado com
arquivo de prova sob `data/acervo/`: **commit recusado, rc=1, HEAD inalterado**.
As três regras foram exercitadas isoladamente — (a) camada com
`pode_publicar=false`, (b) dado não-`.json` em área de acervo, (c) saída de
estudo cujo manifesto resolve para `false`. O `.json` irmão na mesma pasta
passa, como deve.

**Desvio deliberado do especificado:** a regra (b) isenta `.gitkeep` e
`manifesto.yaml`. Sem a isenção, a regra (b) e o `.gitignore` se
contradiriam — o `.gitignore` exige versionar esses dois, o hook os barraria,
e nenhum commit passaria. Estão isentos por não carregarem dado.

### Estudos

`A01_base-cartografica`, `A02_portal`, `A03_expansao_adensamento`, cada um com
`manifesto.yaml` (esquema comentado, `camadas: []`), `scripts/`, `derivados/`,
`saidas/` e `README.md`. Todos em `status: reconhecimento`.

Consequência da regra do mais restritivo: com `camadas: []`, os três resolvem
para `pode_publicar=false`. É intencional — quem não declarou entradas não
provou que pode publicar.

### Geoportal

Voltou a ser **esqueleto sem camadas**, conforme pedido: `index.html` +
`css/estilo.css` + `js/mapa.js`, Leaflet centrado em Bagé. O portal anterior
(que carregava o limite municipal e montava rodapé de fontes a partir do
catálogo) foi preservado em `estudos/A02_portal/scripts/` como ponto de
partida para reconstruí-lo na nova arquitetura.

Teste headless adaptado: 7/7 checagens, incluindo a de que **nenhuma** camada
é carregada — um teste que não checasse isso deixaria passar camada entrando
sem catálogo.

### Pendências

1. **Sem `LICENSE` e sem decisão de licenciamento.** Registrado como PENDENTE
   no README. Não publicar no Pages até resolver.
2. `bage.bib` continua sendo o exemplo de uma entrada, a ser substituído pela
   exportação do Zotero.
3. O sha256 do GeoPackage no catálogo muda a cada reexecução do
   `vetor_ibge.py` (o formato grava `last_change` em `gpkg_contents`); foi
   atualizado nesta sessão. Se precisar de hash estável, avaliar
   `OGR_CURRENT_DATE`.
4. `data/geoportal/limite_municipal.geojson` continua publicado e catalogado,
   mas o esqueleto do portal não o carrega — isso é trabalho de A02.

---

## 2026-09-20 — Censo 2000/2010/2022 e CNEFE 2022 importados do REVIA_BG (tag `censo_v1`)

Importação **por cópia**, a partir de `~/projetos/rede_viaria_bage/dados/externos/censo/`
(projeto REVIA_BG), que baixou os arquivos das fontes oficiais do IBGE em 20/09/2026.
**Nada foi baixado por este repositório** e **nada foi escrito no REVIA_BG**: a origem foi
aberta só para leitura.

Script: `scripts/download/censo_revia_bg.py` (com `--dry-run`, idempotente, `--forcar` para
recopiar, `--somente-metadados` para regerar os `.json`).

### Cópia e conferência

| item | valor |
| --- | ---: |
| arquivos copiados | **58** |
| bytes copiados | **1.033.715.032** (985,8 MiB) |
| arquivos de dado (com entrada em manifesto) | 51 |
| arquivos de procedência que vieram junto (`FONTE.md`, `manifesto_censo*.json`) | 7 |
| metadados `.json` irmãos gerados | 51 |

Tamanho medido **antes** de copiar, como pedido: as tabelas de 2022 (recorte BR, por setor e
por bairro) somam **577.556.141 bytes** — setores 509.176.073, bairros 28.068.832, mais dois
`.xlsx`. Abaixo do limite de 2 GB, então a cópia seguiu sem parada.

Quatro conferências, nenhuma dispensando as outras:

1. **origem × manifesto de origem** — 51/51 arquivos de dado com o sha256 registrado nos
   `manifesto_censo_<ano>.json` do REVIA_BG. Detecta origem já corrompida antes de copiar;
2. **cópia × origem** — **58/58** com sha256 idêntico, e 1.033.715.032 bytes dos dois lados;
3. **origem intocada** — 58/58 com o mesmo sha256 do início. Conferido também **fora do
   script**, por `sha256sum` do shell contra uma linha de base tirada antes de qualquer
   escrita: o digest do conjunto das 58 linhas é `3af2752609d82d54…` no início e no fim;
4. **catálogo × disco** — os 9 `sha256` das linhas novas do catálogo conferidos contra o
   arquivo correspondente em `data/acervo/censo/`, 9/9.

**Controle negativo** (uma comparação que dá zero só vale se o comparador detecta diferença):
1 bit trocado no último byte de uma cópia descartável de `2000/malha/4301602.zip`, mesmo
tamanho em bytes — sha256 passou de `39480d0035683aff…` para `d14f56b0be61aaa4…`,
**detectado**. E um sha256 inexistente (`ffff…`) não casou com nenhum arquivo do manifesto,
como tinha de ser.

Datas preservadas (`shutil.copy2`, equivalente a `cp --preserve=timestamps`): conferido por
amostra, `stat` da origem igual ao da cópia.

Idempotência: a segunda execução registrou `copiados: 0 · já presentes e idênticos: 58`.

### Catálogo de fontes

**9 linhas novas**, uma por divulgação (não por arquivo), de `ibge_censo2000_agregado_setores`
a `ibge_cnefe2022_coordenadas`. As 2 linhas pré-existentes ficaram **byte a byte iguais**.
`python scripts/utils/validar_catalogos.py` → **rc=0** (1 aviso antigo, sobre
`ibge_areas_territoriais` não ter script responsável). `testar_validador.py` → **4/4**.

### Licença — o que foi confirmado e o que não foi

Confirmada **na raiz dos dois hosts que serviram os arquivos**, `https://ftp.ibge.gov.br/` e
`https://geoftp.ibge.gov.br/` (HTTP 200, 20/09/2026), com a frase literal:

> "Todos os arquivos aqui disponíveis são públicos."

**Não foi lida** a página formal de termos de uso do IBGE
(`www.ibge.gov.br/acesso-informacao/acoes-e-programas/termos-de-uso.html`): respondeu
**HTTP 403** — desafio Cloudflare —, com e sem cabeçalhos de navegador. Nada foi transcrito
dela. O `autorizacao_para_republicar = sim` das nove linhas se apoia na declaração do FTP e
na prática já adotada para as outras fontes IBGE do acervo; **se a página formal trouxer
condição adicional, isso ainda não foi conferido.** Registrado também em
`docs/ressalvas_censo_bage.md`.

### Ressalvas registradas

`docs/ressalvas_censo_bage.md` (novo) e o campo `observacoes` de cada linha do catálogo:
soma dos setores fechando em 2022 (117.938, diferença 0) e não fechando em 2010 (−476, com
4 setores da malha sem linha na tabela e **causa declarada em aberto**); a diferença de 2000
(−874) sendo **de recorte, não erro**; o geocódigo **não** sendo identificador estável entre
2010 e 2022 (só 141 dos 199 setores em 1:1); **Bagé não ter bairros** na divulgação de 2022,
com controle negativo em Porto Alegre (99); e o CNEFE de Bagé (62.782 endereços, todos com
coordenada, espécies 1 e 2 coincidindo exatamente com `v0003`/`v0004` do agregado por setores).

### Decisões desta sessão, para revisão

1. **Destino `data/acervo/censo/`, não `data/externos/`.** A regra (iv) manda copiar camada *de
   outro projeto* para `data/externos/`. Estes arquivos são **dado bruto do IBGE, como veio da
   fonte**, apenas transportado pelo REVIA_BG — não são camada derivada dele —, então foram
   para `data/raw/`, conforme pedido na especificação da sessão. A procedência da cópia está
   registrada assim mesmo, em `origem_da_copia` de cada `.json` irmão, no
   `manifesto_copia_censo.json` e nas 9 linhas do catálogo. **Se a leitura correta da regra
   (iv) for `data/externos/`, a mudança é um `git mv` mais uma reexecução do script.**
2. **Os 3 `FONTE.md` copiados não são versionados.** A regra do `.gitignore`
   (`data/raw/**` com exceção só para `*.json` e `.gitkeep`) os ignora. Não mexi no
   `.gitignore`, que é contrato declarado do repositório. A perda é pequena — o conteúdo
   deles está em `docs/ressalvas_censo_bage.md` e os dados de procedência estão nos
   manifestos versionados —, mas **é uma decisão do responsável** acrescentar
   `!data/raw/**/FONTE.md` ou deixar como está.
3. **Nada do Censo foi publicado no geoportal.** `data/geoportal/` não mudou, e nenhuma linha
   foi acrescentada a `catalogo_camadas.csv`: não há camada derivada ainda, e a regra (vi)
   exige conferência no mapa antes de congelar qualquer uma.

### Pendências novas

7. **Tabelas do Censo 2000 ainda não lidas** — `.XLS` legado (BIFF8), sem leitor no ambiente
   do REVIA_BG. Aqui o `requirements.txt` também não tem `xlrd`. Os arquivos estão intactos.
8. **CRS da malha de 2000 por decidir** — a urbana vem declarada em EPSG:32621 (UTM 21
   **norte**, hemisfério errado) e a rural sem CRS. Decidir e registrar antes de qualquer
   medição métrica; 7 das 127 geometrias urbanas são inválidas.
9. **Causa dos 4 setores de 2010 sem linha na tabela** — em aberto. Até lá, a soma dos
   setores de 2010 não serve como total municipal.
10. **Termos de uso formais do IBGE não conferidos** — página atrás de Cloudflare.

---

## 2026-09-20 — Criação do repositório (tag `estrutura_v1`)

Criação do acervo do zero, em diretório vazio. Nenhum outro diretório foi
tocado, exceto leitura do repositório de referência.

### Comparação com o repositório de referência (ClimaPampa)

`~/projetos/uruguaiana-clima-saude` estava acessível localmente e **foi lido
integralmente** antes de qualquer decisão. Foram comparados: `README.md`,
`CLAUDE.md`, `.gitignore`, `index.html`, `css/style.css`,
`js/map-init.js`, `js/layers.js`, `scripts/download/vetor_ibge.py`,
`scripts/geoportal/common.py`, `scripts/utils/recorte_municipio.py`,
`scripts/geoportal/test_headless.js`, `package.json`, `requirements.txt`,
`data/catalogo_fontes.csv` e a estrutura de `data/geoportal/`.

**Herdado sem mudança:**

- CRS de trabalho `EPSG:31981`, publicação em `EPSG:4326`;
- `config/area_estudo.geojson` como referência única de recorte, com
  `scripts/utils/recorte_municipio.py` como único ponto de leitura;
- `scripts/geoportal/common.py` (`salvar_geojson_wgs84`), com a mesma regra de
  só reprojetar para 4326 no último passo;
- convenção de nome `{tema}_{fonte}_{periodo}_{resolucao}.{ext}`;
- metadado `.json` irmão de todo arquivo de dado;
- `data/catalogo_fontes.csv` como catálogo vivo;
- idempotência dos downloads (`--forcar` para rebaixar);
- parametrização por código IBGE, sem hardcode do município;
- layout do geoportal: painel lateral à direita, grupos colapsáveis, gaveta no
  mobile, alternância mapa/satélite (OSM + Esri World Imagery), namespace
  global `window.App`, Leaflet 1.9.4 via unpkg com SRI;
- teste headless Playwright no mesmo esquema (`npm run test:geoportal`,
  servidor HTTP efêmero + Chromium headless + screenshot não versionado).

**Divergências deliberadas em relação ao ClimaPampa** (e o motivo):

1. **Download pelo geoftp, não pela API de malhas.** O ClimaPampa usa
   `servicodados.ibge.gov.br/api/v3/malhas`. Aqui a exigência é o geoftp, com
   navegação pelas listagens. Ganho concreto: o produto do geoftp traz o
   atributo `AREA_KM2` (das Áreas Territoriais), que o GeoJSON da API não
   traz — é ele que permitiu conferir a área do município contra o valor
   oficial. Nenhuma URL é montada por adivinhação: o script desce de
   `organizacao_do_territorio/` até o ZIP, exigindo em cada nível que o nome
   esperado esteja listado.
2. **`limite_municipal.geojson` com underscore**, enquanto o ClimaPampa usa
   `limite-municipal.geojson` com hífen. O nome com underscore foi pedido
   explicitamente na especificação deste repositório. Os arquivos de
   *produção* seguem o hífen da convenção herdada
   (`limite-municipal_ibge_2025_municipal.gpkg`), então a divergência está só
   na camada de publicação.
3. **Camadas montadas a partir do catálogo, não escritas no JS.** No
   ClimaPampa, `js/layers.js` lista as camadas em código. Aqui o portal lê
   `data/geoportal/catalogo.json` (projeção dos dois CSV) e monta os grupos
   sozinho. Motivo: o acervo exige rodapé com fonte e licença por camada
   ligadas ao catálogo — deixar a lista em duas fontes de verdade garantiria
   divergência com o tempo.
4. **Catálogo de fontes com colunas novas:** `id`,
   `autorizacao_para_republicar` e `sha256`, que o ClimaPampa não tem. São o
   que sustenta a regra (i) e a rastreabilidade sem versionar o dado.
5. **Segundo catálogo (`catalogo_camadas.csv`) e validador**, inexistentes no
   ClimaPampa.
6. **`.gitignore` com exceções por negação.** O ClimaPampa ignora
   `data/raw/` e `data/processed/` inteiros. Aqui os `.json` irmãos precisam
   ser versionados, o que exige a forma `data/raw/**` + `!data/raw/**/` +
   `!data/raw/**/*.json` — com `data/raw/` (diretório) o Git não desceria na
   árvore e nenhuma negação funcionaria.
7. **`rasterio` fora do `requirements.txt`**, porque nenhum script raster
   existe ainda.

### Área de estudo

`scripts/download/vetor_ibge.py` navegou o geoftp e baixou
`municipio_2025/UFs/RS/RS_Municipios_2025.zip`
(10.139.778 bytes, `Last-Modified: 2026-02-26`,
sha256 `d70d47cc…28513`), recortou `CD_MUN = 4301602` e gravou a área de
estudo em `EPSG:31981`.

Conferência:

| item | valor |
| --- | --- |
| município | Bagé (4301602) |
| feições | 1 |
| CRS | EPSG:31981 |
| área geométrica (calculada em 31981) | 4.096,533 km² |
| área oficial (atributo `AREA_KM2` da malha) | 4.091,554 km² |
| diferença | 4,979 km² (**0,122 %**) |

O valor oficial foi conferido **por uma segunda fonte, independente da
malha**: a planilha `AR_BR_RG_UF_RGINT_RGI_MUN_2025.ods` da publicação
*Áreas Territoriais 2025* do IBGE
(`geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/areas_territoriais/2025/`)
traz para Bagé exatamente **4.091,554 km²** — idêntico ao atributo da malha.

A diferença de 0,122 % é esperada e não indica erro: a área oficial do IBGE é
calculada sobre a superfície do elipsoide, enquanto 4.096,533 km² é a área do
polígono projetado em UTM 21S, e a projeção UTM distorce área ao se afastar do
meridiano central. Bagé (≈54,1° W) está a cerca de 3° do meridiano central do
fuso 21 (57° W), magnitude compatível com a distorção observada.

> **Atualização 2026-09-22:** a regra mudou. Área passou a ser medida no CRS
> equivalente `crs.area` do config (`ESRI:102033`, South America Albers Equal
> Area Conic), via `scripts/utils/medidas.py`: Bagé = **4.091,562 km²**, resíduo
> de **+0,008 km²** (0,0002 %) em relação ao oficial. Os 4.096,533 km² acima
> ficam como registro da medição em UTM. Ver `docs/convencoes.md`, seção 2.

Idempotência conferida: a segunda execução registrou
`já existe, não rebaixando: RS_Municipios_2025.zip` e reproduziu as mesmas
saídas.

### Catálogos e validador

`data/catalogo_fontes.csv` (2 fontes) e `data/catalogo_camadas.csv`
(1 camada publicada). `scripts/utils/validar_catalogos.py` passou (rc=0, 1
aviso: a fonte de conferência `ibge_areas_territoriais` não tem script
responsável, o que é aceitável para consulta pontual).

**Controles negativos** (`scripts/utils/testar_validador.py`) — 4/4 no
resultado esperado:

| controle | esperado | obtido |
| --- | --- | --- |
| positivo: catálogos reais | rc=0 | rc=0 |
| A: id de fonte inexistente | rc=1 | rc=1 — *fonte 'fonte_que_nao_existe' não existe em catalogo_fontes.csv* |
| B: chave bibliográfica inexistente | rc=1 | rc=1 — *chave bibliográfica 'chave2099inexistente' não existe em bage.bib* |
| C: camada publicada com fonte sem licença | rc=1 | rc=1 — *está PUBLICADA mas a fonte 'ibge_malhas_municipais' não tem licença declarada* |

O validador também confere o sha256 do arquivo publicado contra o registrado
no catálogo, o que operacionaliza a regra (vi): se o GeoJSON mudou depois de
congelado, a validação falha até que a conferência no mapa seja refeita.

### Geoportal

`index.html` + `css/style.css` + `js/map-init.js` + `js/layers.js`. Sete
grupos temáticos no painel (Território, Urbano, Mobilidade, Saúde, Educação,
Ambiente, Dados não espaciais); só Território tem camada — os outros seis
aparecem marcados como "Nenhuma camada publicada ainda".

Conferido:

- `python -m http.server`: `index.html`, CSS, os dois JS, `catalogo.json` e
  `limite_municipal.geojson` servidos com HTTP 200;
- teste headless Playwright: **15/15 checagens**, **0 erro de console**,
  **0 exceção de JS**. Entre elas: Leaflet inicializado, os 7 grupos
  presentes, camada carregada do catálogo e ativa no mapa com 1 feição,
  `fitBounds` caindo dentro do bounding box de Bagé (centro resultante
  −31,2462 / −54,0655), alternância mapa/satélite trocando a camada base de
  fato, checkbox desligando e religando a camada, grupos vazios marcados e
  rodapé de fontes com a licença preenchida a partir do catálogo;
- inspeção visual do screenshot: o contorno tracejado coincide com o limite
  municipal de Bagé sobre o basemap OSM, com a sede municipal dentro do
  polígono.

### Bibliografia

`bibliografia/bage.bib` é um **exemplo mínimo de uma entrada**
(`silva2021geobage`), criado só para o pipeline ter o que validar, e **será
substituído inteiro pela exportação do Zotero** (coleção "Bagé", Better
BibTeX com `Keep updated`). O fluxo está descrito em
`bibliografia/README.md`. `bibliografia/indice.md` foi gerado por
`scripts/bibliografia/gerar_indice.py`, com data de geração e sha256 do `.bib`
no cabeçalho.

Não há dependência de biblioteca BibTeX: `scripts/bibliografia/bibtex.py` é um
leitor mínimo, suficiente para o que o Better BibTeX emite.

### Pendências

1. **Substituir `bage.bib` pela exportação real do Zotero.** Enquanto isso não
   acontece, a coluna `referencias_bibliograficas` de
   `catalogo_camadas.csv` está **vazia de propósito**: nenhuma referência real
   cita o limite municipal ainda, e preencher com a entrada de exemplo seria
   inventar um vínculo. A checagem de chaves é exercitada pelo controle
   negativo B.
2. **`sha256` do GeoPackage de produção não é estável entre execuções** — o
   formato grava `last_change` em `gpkg_contents`, então regerar o arquivo
   muda o hash mesmo sem mudança de geometria. Por isso o `sha256` de
   `catalogo_camadas.csv` refere-se ao **arquivo de publicação** (GeoJSON,
   determinístico). A identidade do produto de produção fica ancorada no
   sha256 da fonte + edição da malha, registrados no `.json` irmão. Se for
   preciso hash estável do GPKG, avaliar exportação com timestamp fixo
   (`OGR_CURRENT_DATE`).
3. **Grupos temáticos vazios**: Urbano, Mobilidade, Saúde, Educação, Ambiente
   e Dados não espaciais aguardam a primeira camada.
4. **Nenhum dado não espacial coletado ainda** — `data/raw/tabular/` vazio.
5. **`data/externos/` vazio** — nenhuma camada importada de outro projeto
   (`rede_viaria_bage`, `SIG_bage` e `bage` existem em `~/projetos/` e são
   candidatos naturais, sempre por cópia, conforme a regra (iv)).
6. **Sem repositório remoto e sem push**, conforme pedido.
