# Censo 2010 — fonte, arquivos e ressalvas

**Divulgação:** Censo Demográfico 2010 — Resultados do Universo, Agregados por Setores Censitários.
**Datas do servidor:** recorte RS reeditado em 15/06/2026 (os CSV do pacote têm essa data; os XLS são de 2012); documentação de 30/10/2023; malha de setores de 29/02/2012.

**Fontes, e só elas:** `ftp.ibge.gov.br` (tabelas e documentação) e `geoftp.ibge.gov.br` (malhas). Cada arquivo foi encontrado **navegando nas listagens dos diretórios**, nunca por endereço adivinhado. Download por `scripts/censo/c01_baixar_censo.py`, que carrega as URLs exatas.

Os arquivos estão guardados **sem alteração**. `Last-Modified` é a data que o servidor informou no momento do download.

## malha (1 arquivo)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `malha/rs_setores_censitarios.zip` | 12,729,964 | Tue, 14 Jun 2016 19:42:44 GMT | 2026-09-20 | `c7f65e26bf0813a0…` | malha de setores censitários 2010 (urbanos e rurais), recorte RS |

URLs exatas:

- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2010/setores_censitarios_shp/rs/rs_setores_censitarios.zip`

## tabelas (2 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `tabelas/RS_20260615.zip` | 137,504,353 | Mon, 15 Jun 2026 11:37:18 GMT | 2026-09-20 | `952d751b5441416b…` | agregados por setores 2010, recorte RS, versão 15/06/2026 (inclui entorno dos domicílios) |
| `tabelas/rio_grande_do_sul.zip` | 7,252,014 | Wed, 17 Aug 2016 14:02:12 GMT | 2026-09-20 | `3079fe5e337da680…` | TOTAL OFICIAL por município, 2010 (Resultados do Universo, ODS) — confere a soma dos setores |

URLs exatas:

- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/RS_20260615.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/ods/Municipios/rio_grande_do_sul.zip`

## documentacao (1 arquivo)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `documentacao/Documentacao_Agregado_dos_Setores_2010_20231030.zip` | 34,133,643 | Mon, 30 Oct 2023 20:16:16 GMT | 2026-09-20 | `eccb3896d19c4e29…` | documentação e dicionário dos agregados por setores 2010 |

URLs exatas:

- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/Documentacao_Agregado_dos_Setores_2010_20231030.zip`

## Notas metodológicas e dicionários baixados

- `Documentacao_Agregado_dos_Setores_2010_20231030.zip` — documentação e dicionário dos agregados por setores 2010

## Ressalvas de comparabilidade

A documentação (`Documentacao_Agregado_dos_Setores_2010_20231030.zip`) traz o PDF
*BASE DE INFORMAÇÕES POR SETOR CENSITÁRIO Censo 2010 - Universo* e uma planilha `Descrição_RS.xls`
por UF. O dicionário das variáveis (`V001`, `V002`, …) está nesse PDF.

**Ressalva medida nesta sessão, não documental:** a tabela de Bagé tem **164 setores** e a malha
tem **168** — **4 setores da malha não têm linha na tabela**. A soma de `V002` (moradores) dá
**116.318** contra **116.794** do total oficial do município: **−476 pessoas, −0,408 %**. Os 4
setores sem linha são a explicação a investigar antes de usar a soma dos setores como total
municipal.

## Inventário de Bagé (4301602) medido sobre estes arquivos

Ver `trabalho/censo/inventario_bage_censos.json` e `trabalho/censo/dicionario_variaveis_rascunho.csv`. Resumo:

- **164 setores na tabela, 168 na malha** — 4 da malha sem linha na tabela;
- malha: 132 urbanos e 36 rurais (`TIPO`), **EPSG:4674**, 0 inválida;
- população `V002` = **116.318** × oficial **116.794** → **−476, −0,408 %**;
- domicílios `V001` = 38.504.
