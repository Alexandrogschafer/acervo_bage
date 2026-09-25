# A03 — Portabilidade dos scripts para outro município

**Levantado em 2026-09-24, sem alterar código.** Objetivo: deixar barato o estudo
equivalente para Uruguaiana/RS (IBGE 4322400), previsto só como ideia (ver
`manifesto.yaml`, bloco `publicacao`). Os números antes de `:` são linhas dos
arquivos em `scripts/` na versão deste commit. Com o código mudando, os números de
linha deixam de valer; o nome do literal continua valendo para a busca.

## Resposta curta

**Nenhum script do A03 roda de ponta a ponta para outro município só trocando
`config/config.yaml`.**

- **Rodam como estão, desde que o município seja do RS:** r00, r02, r04, r06, r07,
  r08, d01, d04 e `paleta.py`.
  - Os arquivos `*_RS` são da UF inteira, e o filtro usa `paths.codigo_ibge()`.
  - Ficam só rótulos e a pasta `derivados/bage/` com nome errado.
- **Quebram por arquivo ou código de Bagé escrito no script:** `grade_estatistica.py`,
  r03, r05 e d02.
  - `grade_estatistica.py` sozinho bloqueia toda a cadeia s1/s2/s3.
- **Rodam com parâmetro, mas carregam limiares e textos calibrados em Bagé:** s1_*,
  s2_*.
- **Não se aproveitam fora de Bagé:** i01, i02, s3_entorno e s3_figuras.
  - i01 e i02 dependem de camadas de interpretação que só existem para Bagé.
  - Os textos de s3_figuras trazem a conclusão de Bagé escrita à mão.

Os utilitários de `scripts/utils/` estão limpos: nenhum código IBGE, nome de município
ou caminho de dado literal. Os `EPSG:4674` nos scripts são o CRS dos arquivos do IBGE,
não do município, e podem ficar.

## 1. Bloqueio principal: a grade estatística

`grade_estatistica.py:30` fixa `QUADRANTES = ("grade_id14.zip", "grade_id04.zip")`, e
não há conferência de cobertura.

As bboxes, lidas nos zips de 2022:

| quadrante | longitude oeste | latitude |
| --- | --- | --- |
| id14 | −56,006° | −31,5° a −26,8° |
| id04 | −55,215° | −33,9° a −31,5° |

A sede de Uruguaiana (cerca de 57,1° O) fica **fora dos dois**. O filtro devolveria
vazio ou parcial sem avisar, e o erro só apareceria adiante.

**O que fazer:** derivar os quadrantes da bbox da área de estudo, ou pô-los no config,
e parar com erro legível se a área não estiver coberta.

## 2. Script por script

| script | lê do config? | o que tem de Bagé embutido | classificação |
| --- | --- | --- | --- |
| `grade_estatistica.py` | parcial | quadrantes fixos :30 (§ 1) | com parâmetro; **bloqueia** |
| `paleta.py` | não precisa | nada | sem alteração |
| `r00_extrair.py` | sim | pasta `derivados/bage/` :95, 117, 141, 152; `RS_20260615.zip` :111; `Agregado_de_setores_2000_RS.zip` :127; `PopMun_43_31/33.zip` :161; `rio_grande_do_sul.zip` :170; `_RS.xls` :181 | sem alteração no RS |
| `r02_totais.py` | sim | `derivados/bage` :34; tabelas `4.23.*` (23 = posição do RS) :77, 117–118, 126–127; nome literal `"Bagé"` :94 | sem alteração no RS |
| `r03_geografia.py` | parcial | **`'4301602.zip'`** :117, 210; **distrito-sede `05` fixo** :206; hipóteses de CRS de 2000 só no fuso 21 :55–60; `CRS_RURAL_2000 = "EPSG:4618"` :65 (decisão para o arquivo de Bagé); `RS_setores_CD2022.gpkg` :105; `IOU_LIMPO = 0.90` :51 | com parâmetro |
| `r04_sigilo.py` | não usa `paths` | `derivados/bage` :28; `Basico_RS` :32–33 | sem alteração no RS |
| `r05_cnefe.py` | parcial | **`"4301602_BAGE.zip"`** :52; `RS_setores_CD2022.gpkg` :60 | com parâmetro |
| `r06_temas_2022.py` | sim | regex `Bag[ée]` :116; `/199` num print :146 | sem alteração (só rótulos) |
| `r07_aglomerados_2010.py` | sim | `"Rio Grande do Sul"` :57 e `"Centro-Oeste"` :60, para achar o bloco da UF | sem alteração no RS |
| `r08_entorno_universo.py` | sim | `Entorno0{i}_RS.csv` :43, 48; `derivados/bage` | sem alteração no RS |
| `d01_descompasso.py` | não usa `paths` | código do município **deduzido da 1ª linha do CSV** :116–117; `Basico_RS`/`Domicilio02_RS` | sem alteração no RS |
| `d02_comparacao.py` | parcial | **`UF_RS = "43"`** :52; **`PORTE = (50_000, 200_000)`**, escolhido em torno de Bagé :54–55; chaves `bage`, `posicao_de_bage` :153, 186 | com parâmetro |
| `d03_grade.py` | — | superado | não portar |
| `d04_entorno.py` | não usa `paths` | `derivados/bage/c2022` :38 | sem alteração |
| `s1_expansao_adensamento.py` | sim | campo `a_parte_setor_136` :98; `LIMIAR_DENTRO = 0.5` :92; `FAIXAS_KM` :94; para se a troca de resolução não for 1 km → 200 m :130–134; textos "199 setores" :525, setor 136 e "41 células" :579–582 | com parâmetro |
| `s1_desagregacao_2010.py` | sim | a lista de setores à parte é **calculada** (teste B); fixos: `rs_setores_censitarios.zip` :66, `PARTE_INTEIRA = 0.9` e `DOM_MIN_B = 3` :68–69, texto do setor 136 :310 | com parâmetro |
| `s1_extintas.py` | sim (CNEFE por glob `{codigo}_*.zip`) | `rs_setores_censitarios.zip` :66; raios de 1 e 2 km :68–69 | com parâmetro |
| `s1_faces_2010.py` | sim (faces por glob) | **`RAIO_FACE_M = 40`** (p90 medido em Bagé) :75; chave `agrupamento_053_054` :304, 482; textos "distrito-sede (05)" e setor 136 | com parâmetro |
| `s1_geografias.py` | sim | `FAIXAS_BORDA_M` :61 | sem alteração (depende da cadeia s1) |
| `s1_figuras.py` | sim (extensão calculada) | títulos "Bagé —" :217, 239, 270; `FONTE` com "41 células", setor 136 e "UTM 21S (EPSG:31981)" :77–82; faixas das coropletas :67–76; margens :102, 105 | com parâmetro |
| `s2_divergencia.py` | sim | `DIST_BORDA_M = 1000`, `RAIOS_MIOLO_KM` :64–65; item "unidade rural a leste" é pergunta de Bagé e dá erro com grupo vazio :277–279; chaves `centro_EPSG31981`, `no_setor_136` | com parâmetro |
| `s2_agrupamentos.py` | sim | `QUANTOS = 2`, `MARGEM_M = 300` :52–53; título "Bagé —" :159; rótulo do CRS :58–62 | com parâmetro |
| `s3_entorno.py` | sim | lê o CSV do **i02** :60, 321–326; períodos REVIA_BG (`FIRMES_ANTIGOS = {"1938","1960"}`, "até 2001") :82–84, 250; iluminação como "controle (universal)" :78; `LIMIAR_SENS = 0.70` :61, com "70pct" escrito à mão :145–146 | **específico de Bagé** |
| `s3_figuras.py` | sim | **conclusão escrita à mão** ("INCONCLUSIVO", "nenhuma diferença tem p < 0,05") :305–311; números de Bagé ("31 dos 199", "IQR 76,6", "71 % a 90 %"); `RAMPA_FAIXAS` calibrada em Bagé :74–79 | **específico de Bagé** |
| `i01_bairros_loteamentos.py` | parcial | camada `externos/bairros_loteamentos_bage/` :56; prefixos LOTEAMENTO/BAIRRO/VILA :80; colunas `id`/`nome` :90 | **específico de Bagé** |
| `i02_evolucao_urbana.py` | parcial | `externos/revia_bg/evolucao_urbana` :65; shapefiles por período :70–78; regra da borda de 1938/1960 :81–85 | **específico de Bagé** |
| `variaveis.json` | n/a | nomes `*_RS.csv`; nota com número de Bagé :752 | sem alteração no RS |

## 3. O que precisaria virar parâmetro

Os nomes de chave são sugestões.

### Identificação do município

- `municipio.slug`, no lugar da pasta `derivados/bage/`: r00, r02, r03, r04, r06, r08,
  d01, d04, s1_desagregacao e s1_extintas.
- `paths.nome_municipio()`, no lugar do literal "Bagé" em r02:94, r06:116 e nos títulos
  das figuras.
- `paths.codigo_ibge()` em d01, que hoje deduz o código do CSV.
- `municipio.uf_codigo` e `municipio.uf_nome` para d02:52 e r07:57/60. Uruguaiana não
  precisa, por ser do RS.
- `municipio.distrito_sede` para o `05` fixo em r03:206.

### Arquivos brutos

Nome ou glob por `{codigo}`/`{uf}`, como s1_extintas e s2 já fazem para o CNEFE:

- `ibge.grade.quadrantes`, ou derivar da bbox (§ 1);
- `ibge.censo_2010.agregados_uf` (`RS_20260615.zip`);
- `ibge.censo_2010.malha_setores_uf`;
- `ibge.censo_2010.tabelas_uf` e o prefixo `4.23`;
- `ibge.censo_2000.*` (agregados, PopMun, malha rural e malha urbana `{codigo}.zip`);
- o CNEFE de r05:52 passa a usar `{codigo}_*.zip`;
- `RS_setores_CD2022.gpkg` (r03, r05) passa a vir da camada `setores_2022` do acervo,
  como no s1.

### Códigos de setor e de agrupamento

- O setor `430160205000136` aparece só em **texto e em nome de campo**; a lista é
  calculada.
  - Renomear o campo `a_parte_setor_136` para algo como `a_parte`.
  - Montar os textos a partir de `setores_com_assinatura`.
- A chave `agrupamento_053_054` aparece em s1_faces, i01 e i02. Ela deve virar um nome
  neutro, como `maior_agrupamento_extintas`.

### Limiares calibrados

Bloco `a03.limiares`. Cada um precisa de decisão do responsável: manter o valor de Bagé
ou recalibrar para o outro município.

| limiar | valor em Bagé | onde |
| --- | --- | --- |
| dentro da área urbanizada | 0,5 | s1_expansao:92 |
| tolerância de contiguidade | 1 m | s1_expansao:93 |
| faixas de distância | `FAIXAS_KM` | s1_expansao:94 |
| teste B da desagregação | parte inteira 0,9; mínimo de 3 domicílios | s1_desagregacao:68–69 |
| raio da face (p90 medido) | 40 m | s1_faces:75 |
| borda e miolo | 1000 m; 1 e 1,5 km | s2_divergencia:64–65 |
| agrupamentos detalhados | 2, margem de 300 m | s2_agrupamentos:52–53 |
| sensibilidade da junção por setor | 0,70 | s3_entorno:61 |
| repartida mínima | 0,01 | s3_entorno:62 |
| porte do grupo de comparação | 50 mil a 200 mil | d02:55 |
| IoU e grade de calibração | 0,9 | r03:51, 285 |
| faixas de borda | `FAIXAS_BORDA_M` | s1_geografias:61 |
| proximidade | 500 m | i01:65 |

### Figuras e textos

- Rótulo "SIRGAS 2000 / UTM 21S (EPSG:31981)" gerado a partir de `crs.producao`
  (s1_figuras, s2_agrupamentos, s3_figuras). Uruguaiana também está no fuso 21S, mas o
  rótulo não deve depender disso.
- Números de resultado escritos à mão ("41 células", "199", "168", "31 dos 199",
  "7 setores", "IQR 76,6", "INCONCLUSIVO / p < 0,05") calculados a partir dos JSON.
- Faixas das coropletas e margens em `a03.figuras.*`.

### Camadas de interpretação e leitura do entorno

- `a03.interpretacao.bairros` (caminho, prefixos, colunas).
- `a03.interpretacao.evolucao_urbana` (caminho, períodos, recortes "firmes").
  - Sem a camada, s3 deveria rodar **sem** a datação, em vez de parar.
- `a03.entorno.itens`: o papel de cada item do entorno. "Iluminação universal" é
  leitura de Bagé.

## 4. O que falha em outro município com qualquer config

1. **Grade estatística fora dos quadrantes** (§ 1).
2. **Dado bruto do município.** CNEFE, faces de 2010 por distrito e malha urbana de
   2000 são arquivos municipais.
   - Em `config/fontes_censo_ibge.yaml` só estão os de Bagé.
   - Os scripts exigem o `.json` irmão com sha256, gerado pelo download.
   - Pela regra 6, as entradas novas vêm navegando as listagens do IBGE, nunca
     montando URL.
3. **Acervo.** `limite_municipal` e `setores_2022` do outro município precisam estar
   catalogados e conferidos, e `config/area_estudo.geojson` precisa ser regenerado.
4. **Malha de 2000.** Os CRS decididos (EPSG:29191 e EPSG:4618) valem para os arquivos
   de Bagé. As hipóteses de r03 cobrem só o fuso 21.
5. **i01 e i02** só existem para Bagé. s3_entorno para sem o CSV do i02.
6. **Saídas não separadas por município.** `derivados/` e `saidas/` são do estudo.
   - Rodar para outro município **sobrescreve** as de Bagé.
   - Mais grave: `conferencias_visuais_anteriores()` (s1_expansao:407–421,
     s3_figuras:104–115) copia do `.json` anterior a conferência visual do responsável
     sem olhar o conteúdo.
   - O registro de Bagé iria parar na camada do outro município.
   - **O estudo de Uruguaiana deve ser um estudo próprio** (`estudos/<id>/` com manifesto
     próprio, provavelmente em outro repositório com config próprio), não uma
     reexecução deste diretório.
7. **Premissas do dado de Bagé que viram parada:**
   - s1_expansao:130–134, troca de resolução diferente de 1 km → 200 m;
   - s2_divergencia:279, grupo vazio;
   - a ordem da cadeia, que depende de `d01_descompasso.json`.
8. **Outra UF:** `*_RS`, `43`, `4.23` e "Rio Grande do Sul" também quebram. Uruguaiana
   não é afetada, por ser do RS.

## 5. Ordem sugerida, quando o estudo de Uruguaiana chegar

1. Grade: quadrantes pela bbox e erro legível sem cobertura.
2. Literais de arquivo em r03, r05 e d02, e `municipio.slug`.
3. Campos e chaves com nome de Bagé (`a_parte_setor_136`, `agrupamento_053_054`) e
   textos de figura calculados.
4. Limiares em bloco de parâmetros, com decisão do responsável sobre cada um.
5. s3 tolerante à ausência das camadas de interpretação.
6. Separar saídas por município ou, melhor, estudo próprio (§ 4, item 6).
