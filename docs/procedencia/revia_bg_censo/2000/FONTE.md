# Censo 2000 — fonte, arquivos e ressalvas

**Divulgação:** Censo Demográfico 2000 — Dados do Universo, Agregado por Setores Censitários.
**Datas do servidor:** arquivos de 2003, republicados no FTP em 17/08/2016; malha urbana por município de 2012 (republicada 02/06/2016) e malha rural (e500) de 2003.

**Fontes, e só elas:** `ftp.ibge.gov.br` (tabelas e documentação) e `geoftp.ibge.gov.br` (malhas). Cada arquivo foi encontrado **navegando nas listagens dos diretórios**, nunca por endereço adivinhado. Download por `scripts/censo/c01_baixar_censo.py`, que carrega as URLs exatas.

Os arquivos estão guardados **sem alteração**. `Last-Modified` é a data que o servidor informou no momento do download.

## malha (2 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `malha/4301602.zip` | 13,126 | Thu, 02 Jun 2016 20:59:09 GMT | 2026-09-20 | `39480d0035683aff…` | malha de setores URBANOS 2000, recorte MUNICÍPIO de Bagé (4301602) |
| `malha/rs_setores_censitarios.zip` | 4,466,420 | Tue, 14 Jun 2016 19:44:01 GMT | 2026-09-20 | `d9f491a2dddf3e20…` | malha de setores RURAIS 2000 (projeção geográfica, e500), recorte RS |

URLs exatas:

- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2000/setor_urbano/rs/4301602/4301602.zip`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2000/setor_rural/projecao_geografica/censo_2000/e500_arcview_shp/uf/rs/rs_setores_censitarios.zip`

## tabelas (3 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `tabelas/Agregado_de_setores_2000_RS.zip` | 53,869,085 | Wed, 17 Aug 2016 14:09:08 GMT | 2026-09-20 | `5c0d655a1dc8c87f…` | agregado por setores censitários 2000, recorte RS |
| `tabelas/PopMun_43_31.zip` | 54,484 | Wed, 17 Aug 2016 14:09:20 GMT | 2026-09-20 | `fa8e27ffe6fff91c…` | TOTAL OFICIAL por município, RS, 2000 (tabela 1.31) — confere a soma dos setores |
| `tabelas/PopMun_43_33.zip` | 46,844 | Wed, 17 Aug 2016 14:09:20 GMT | 2026-09-20 | `a79b81a3d49bfe5d…` | população por situação do domicílio, municípios do RS, 2000 (tabela 1.33) |

URLs exatas:

- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2000/Dados_do_Universo/Agregado_por_Setores_Censitarios/Agregado_de_setores_2000_RS.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2000/Dados_do_Universo/Municipios/PopMun_43_31.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2000/Dados_do_Universo/Municipios/PopMun_43_33.zip`

## documentacao (2 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `documentacao/Arquivo_AgreSetores_Completo_V2.doc` | 86,016 | Wed, 17 Aug 2016 14:09:03 GMT | 2026-09-20 | `0e3ccba3a96095ab…` | documentação do agregado por setores 2000 (layout dos arquivos) |
| `documentacao/referencias_metodologicas.zip` | 34,191 | Thu, 02 Jun 2016 19:37:06 GMT | 2026-09-20 | `6c9a5b8db5a034c2…` | referências metodológicas da malha de 2000 |

URLs exatas:

- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2000/Dados_do_Universo/Agregado_por_Setores_Censitarios/Arquivo_AgreSetores_Completo_V2.doc`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2000/setor_rural/documentacao/referencias_metodologicas.zip`

## Notas metodológicas e dicionários baixados

- `Arquivo_AgreSetores_Completo_V2.doc` — documentação do agregado por setores 2000 (layout dos arquivos)
- `referencias_metodologicas.zip` — referências metodológicas da malha de 2000

## Ressalvas de comparabilidade

A documentação vem em `Arquivo_AgreSetores_Completo_V2.doc` (layout dos arquivos) e, no
geoftp, em `referencias_metodologicas.zip`.

**Ressalvas medidas nesta sessão:**

- **As tabelas de 2000 não foram lidas.** O Censo 2000 distribui os agregados só em **.XLS legado
  (BIFF8)**. Este ambiente não tem `xlrd`, e o LibreOffice instalado **não tem o módulo Calc** (só
  `writer`, `math`, `base-core`), de modo que `soffice --convert-to csv` responde *source file could
  not be loaded*. Os arquivos estão guardados intactos; falta um leitor.
- **A malha de 2000 é dividida em urbana e rural, e não cobre Bagé de forma homogênea.** O recorte
  urbano existe **por município** (`4301602.zip`, 127 setores) — é o menor recorte de todos os três
  censos. O rural vem só por UF (`43SE500G.shp`, 6.679 setores no RS, 47 em Bagé).
- **CRS:** a malha urbana de Bagé de 2000 vem em **EPSG:32621 (UTM 21N, WGS 84)** — hemisfério
  NORTE, o que para Bagé é um erro de declaração no `.prj`, não um dado do sul projetado. A malha
  rural vem **sem CRS declarado**. Nos dois casos o CRS tem de ser decidido e registrado antes de
  qualquer medição métrica. **7 das 127 geometrias urbanas são inválidas.**

## Inventário de Bagé (4301602) medido sobre estes arquivos

Ver `trabalho/censo/inventario_bage_censos.json` e `trabalho/censo/dicionario_variaveis_rascunho.csv`. Resumo:

- **malha urbana por município: 127 setores** (EPSG:32621 declarado, 7 inválidas);
- **malha rural: 47 setores em Bagé** (RS inteiro 6.679, sem CRS declarado);
- **tabelas não lidas** — .XLS legado sem leitor neste ambiente.
