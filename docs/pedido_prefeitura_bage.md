# Pedido à Prefeitura Municipal de Bagé

> **Rascunho — NÃO ENVIADO.** Reúne tudo o que o projeto ACERVO_BAGE precisa da
> Prefeitura. Redigido em 2026-09-24. O envio, o canal e o destinatário exato
> (Gabinete, GEPLAN, setor de GeoInformação) são decisão do responsável.

---

**A:** Prefeitura Municipal de Bagé — Secretaria de Gestão, Planejamento e Captação de
Recursos (GEPLAN) e setor de GeoInformação

**De:** Alexandro Schafer — Universidade Federal do Pampa (UNIPAMPA), Campus Bagé

**Assunto:** pedido de autorização de republicação de dados geográficos e de documentos
da legislação urbanística, para pesquisa

Prezados,

Coordeno na UNIPAMPA, Campus Bagé, o projeto de pesquisa **ACERVO_BAGE**. É um acervo
público de dados espaciais, dados não espaciais e bibliografia sobre o município de
Bagé, usado em estudos sobre a forma urbana e o crescimento da cidade. Um desses
estudos investiga onde se materializou o crescimento de domicílios entre os Censos de
2010 e 2022: se em ocupação de área nova ou em adensamento da área já ocupada.

O acervo é aberto. Por isso só republicamos o que a fonte autoriza. Os dados da
Prefeitura que usamos hoje ficam **apenas para uso interno** e não são redistribuídos,
porque os repositórios em que foram publicados não declaram licença. Para que os
resultados possam ser publicados com os dados que os sustentam, pedimos o que segue.
A finalidade é exclusivamente de pesquisa. Toda republicação citará a Prefeitura como
fonte.

### (a) Autorização de republicação das camadas do geobage e do GeoDataBase

Pedimos autorização para republicar, com citação da fonte, as camadas abaixo,
publicadas pelo setor de GeoInformação nos repositórios `GeoInformacao/GeoDataBase` e
`GeoInformacao/filesGeoJSONgeobage`, base do pacote R `geobage`. Uma licença aberta
declarada no próprio repositório resolveria o pedido de uma vez, por exemplo CC BY 4.0.

**GeoDataBase** (base cadastral urbana; versão que temos: julho de 2020):

| camada | camada | camada |
| --- | --- | --- |
| AREA_CONTRUIDA | LOTEAMENTOS | PARALELEPIPEDO |
| ASFALTO_ANTIGO | LOTES_RURAIS | QUARTEIRAO |
| ASFALTO_NOVO_DESDE_2017 | LOTES_URBANOS | REGIOES_CENSITARIAS |
| INTERTRAVADO_DE_CONCRETO | LOGRADOUROS | cadastro_imobiliario (ver a nota) |

> **Nota sobre `cadastro_imobiliario`.** A camada traz dados fiscais e de endereço do
> contribuinte: valores venais, IPTU e endereço de entrega. **Não pedimos autorização
> para republicá-la como está**, e não a republicaríamos. Se a Prefeitura puder
> autorizar só a geometria e atributos não pessoais (por exemplo, a classificação de
> uso e a área construída), isso basta para a pesquisa.

**filesGeoJSONgeobage** (camadas temáticas; versão que temos: julho de 2022):

| camada | camada | camada |
| --- | --- | --- |
| AERODROMOS | HIDROGRAFIA | PRODUCAO_LEITE |
| BAGE | IMOVEIS_RURAIS_PUBLICOS | RESERVA_LEGAL |
| BANCOS_DE_AREIA_ARROIO_BAGE | LINHAS_TRANSMISSAO | RODOVIAS_PAVIMENTADAS |
| BANHADOS | LOTEAMENTOS | RODOVIAS_SEM_PAVIMENTO |
| BARRAGEM | LOTES_RURAIS | SENSIBILIDADE_AMBIENTAL |
| COMPREB | MASSA_DAGUA | SOLO |
| CURVAS_DE_NIVEL_BAGE_10M | NASCENTES | SOLO_BAGE |
| CURVAS_NIVEL | PALEONTOLOGIA | TIPO_SOLO |
| DISTRITOS_DE_BAGE | PAMPA_FINAL | TRECHO_DRENAGEM |
| ESTRADAS_RURAIS_DE_BAGE | PARQUE_DO_GAUCHO_BAGE | TRECHO_MASSA_DAGUA |
| FERROVIAS | PAVIMENTACAO_BAGE | UNIDADE_HIDROESTRATIGRAFICA |
| GEOLOGIA | PEDOLOGIA | USO_COBERTURA_SOLO |
| GEOMORFOLOGIA | PREDIOS_PUBLICOS | USO_DA_TERRA |
| HIDROGEOLOGIA | | VEGETACAO |
| | | ZONAS_BAGE |

A autorização cobriria também os **derivados** que o projeto faz a partir dessas
camadas. O principal é um mosaico revisado de bairros e loteamentos, com 114 polígonos,
feito a partir do material do geobage.

### (b) Versão mais recente das mesmas camadas

As versões publicadas nos repositórios são de **2020 (GeoDataBase) e 2022
(filesGeoJSONgeobage)**. O estudo compara 2010 com 2022, e a cidade mudou desde então:
loteamentos novos, pavimentação e alterações do perímetro urbano. Pedimos, se
existirem, as versões atuais das mesmas camadas, com a **data de referência** de cada
uma. Interessam sobretudo LOTEAMENTOS, LOTES_URBANOS, QUARTEIRAO, LOGRADOUROS e as de
pavimentação.

Se houver **data de aprovação dos loteamentos**, ela é especialmente valiosa: é o que
permite datar a expansão urbana.

### (c) Documentos da legislação urbanística que não localizamos

O projeto reuniu o Plano Diretor (LC 025/2007), o PlanMob (LC 069/2018) e as leis
complementares que os alteram. Faltam os documentos abaixo, citados nesses textos:

| documento | onde é citado | para que serve |
| --- | --- | --- |
| Lei Municipal nº **2.099/1980** (cria a ZRC-2 e reajusta o zoneamento) | texto compilado da Lei 1.762/1973, art. 41 | datar o zoneamento de 1980 |
| Lei Municipal nº **2.171/1981** (faixa urbana ao longo do Anel Rodoviário) | idem, art. 16 | idem |
| Lei Municipal nº **2.645-A/1989** (nova redação do art. 7º, as zonas) | idem, art. 7º | idem |
| Lei Municipal nº **2.723/1991** (ZR-1 no prolongamento da Av. Líbio Vinhas) | idem, art. 41 | idem |
| **ato do Poder Executivo do art. 180 da LC 025/2007**, que detalha os limites das macrozonas, das zonas e do perímetro urbano com os vértices georreferenciados | LC 025/2007, art. 180 | perímetro urbano legal com coordenadas |
| **anexos I-A e III-A a III-D da LC 069/2018** (mapa da classificação hierárquica das vias e redes preferenciais: motorizada, transporte público, cicloviária, pedestres) | LC 069/2018, art. 2º | a lei que temos não traz esses anexos |
| **plantas nº 27 e nº 28 da Lei 1.762/1973** (sistema viário e zoneamento do primeiro Plano Diretor) | Lei 1.762/1973, arts. 3º e 6º | zoneamento de 1973 |

### (d) Anexos cartográficos do PDDUA em formato vetorial, se existirem

Os anexos 01 a 11 da LC 025/2007 estão no PDF do Plano Diretor como **imagem**, com
mapas datados de agosto de 2007: modelo espacial, macrozoneamento rural e urbano,
zoneamento, perímetro urbano e sistema viário, instrumentos e regiões de planejamento.

Se a Prefeitura tiver esses mapas em formato **vetorial** (DWG, SHP, GeoPackage ou
similar), pedimos uma cópia. Pedimos também a versão atualizada, se houver, que inclua
as alterações de perímetro das LC 054 e 055/2015. Isso evitaria redesenhar os limites a
partir da imagem, que é um processo sujeito a erro.

---

Agradecemos a atenção. Estamos à disposição para esclarecer a finalidade e o uso dos
dados, e para enviar os resultados do estudo quando concluídos.

Atenciosamente,

**Alexandro Schafer**
Universidade Federal do Pampa — Campus Bagé
Projeto ACERVO_BAGE (pesquisa)

---

<!-- Notas internas (não fazem parte do texto a enviar):
- Versões que temos: GeoDataBase no commit 125c9753 (2020-07-16); filesGeoJSONgeobage
  no commit dec12905 (2022-07-26). Catálogo: data/catalogo_fontes.csv
  (geoinfo_geodatabase, geoinfo_filesgeojsongeobage).
- Se a autorização vier: atualizar autorizacao_fonte/pode_publicar das fontes e das
  camadas (54 linhas geoinfo_* em data/catalogo_camadas.csv) e de
  bairros_loteamentos_revisado; nunca cadastro_imobiliario com atributos pessoais.
- Documentos que chegarem: registrar por scripts/acervo/registrar_legislacao.py
  (classificar cada arquivo) e acrescentar linha em data/catalogo_legislacao.csv.
-->
