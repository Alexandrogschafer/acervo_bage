# Censo 2022 — fonte, arquivos e ressalvas

**Divulgação:** Censo Demográfico 2022 — Agregados por Setores Censitários, Resultados do universo.
**Datas do servidor:** malha divulgada em 12–13/11/2024; `basico` reeditado em 20/05/2026; `caracteristicas_domicilio2` e `3` reeditados em 17/04/2025; dicionário de dados de 12/05/2026.

**Fontes, e só elas:** `ftp.ibge.gov.br` (tabelas e documentação) e `geoftp.ibge.gov.br` (malhas). Cada arquivo foi encontrado **navegando nas listagens dos diretórios**, nunca por endereço adivinhado. Download por `scripts/censo/c01_baixar_censo.py`, que carrega as URLs exatas.

Os arquivos estão guardados **sem alteração**. `Last-Modified` é a data que o servidor informou no momento do download.

## malha (3 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `malha/ftp_com_atributos/RS_bairros_CD2022.gpkg` | 4,214,784 | Wed, 13 Nov 2024 18:23:10 GMT | 2026-09-20 | `048f32a110539366…` | malha de BAIRROS 2022 com atributos, recorte RS |
| `malha/ftp_com_atributos/RS_setores_CD2022.gpkg` | 57,962,496 | Wed, 13 Nov 2024 18:23:47 GMT | 2026-09-20 | `8d6c46bbc8d0690d…` | malha de setores 2022 COM os atributos do Censo, recorte RS |
| `malha/geoftp_malha_territorial/RS_setores_CD2022.gpkg` | 57,069,568 | Tue, 12 Nov 2024 20:08:41 GMT | 2026-09-20 | `3816950f00561620…` | malha territorial de setores 2022 (geoftp, sem os atributos do Censo), recorte RS |

URLs exatas:

- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/bairros/gpkg/UF/RS/RS_bairros_CD2022.gpkg`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/setores/gpkg/UF/RS/RS_setores_CD2022.gpkg`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/setores/gpkg/UF/RS/RS_setores_CD2022.gpkg`

## tabelas (28 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `tabelas/Agregados_por_bairros_alfabetizacao_BR.zip` | 7,903,938 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `0bbdffdb0011182c…` | agregados por BAIRRO, tema alfabetizacao (só recorte BR) |
| `tabelas/Agregados_por_bairros_basico_BR_20260520.zip` | 724,481 | Wed, 20 May 2026 13:36:44 GMT | 2026-09-20 | `c84bea0184477b8e…` | agregados por BAIRRO, tema basico (só recorte BR) |
| `tabelas/Agregados_por_bairros_caracteristicas_domicilio1_BR.zip` | 1,340,156 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `a020c3d29761cb10…` | agregados por BAIRRO, tema caracteristicas_domicilio1 (só recorte BR) |
| `tabelas/Agregados_por_bairros_caracteristicas_domicilio2_BR_20250417.zip` | 4,756,303 | Thu, 17 Apr 2025 19:59:23 GMT | 2026-09-20 | `4a4f570003df6e9b…` | agregados por BAIRRO, tema caracteristicas_domicilio2 (só recorte BR) |
| `tabelas/Agregados_por_bairros_caracteristicas_domicilio3_BR_20250417.zip` | 3,012,313 | Thu, 17 Apr 2025 19:59:23 GMT | 2026-09-20 | `f307f0ddda961db0…` | agregados por BAIRRO, tema caracteristicas_domicilio3 (só recorte BR) |
| `tabelas/Agregados_por_bairros_cor_ou_raca_BR.zip` | 2,281,866 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `f4c1589bef59f80d…` | agregados por BAIRRO, tema cor_ou_raca (só recorte BR) |
| `tabelas/Agregados_por_bairros_demografia_BR.zip` | 1,315,108 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `b2b405df497ee73e…` | agregados por BAIRRO, tema demografia (só recorte BR) |
| `tabelas/Agregados_por_bairros_domicilios_indigenas_BR.zip` | 594,091 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `b920bd257bcd425b…` | agregados por BAIRRO, tema domicilios_indigenas (só recorte BR) |
| `tabelas/Agregados_por_bairros_domicilios_quilombolas_BR.zip` | 344,717 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `d183f720781a683b…` | agregados por BAIRRO, tema domicilios_quilombolas (só recorte BR) |
| `tabelas/Agregados_por_bairros_obitos_BR.zip` | 1,119,458 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `8b38d2403b088692…` | agregados por BAIRRO, tema obitos (só recorte BR) |
| `tabelas/Agregados_por_bairros_parentesco_BR.zip` | 3,260,584 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `91919e1f6bf22e28…` | agregados por BAIRRO, tema parentesco (só recorte BR) |
| `tabelas/Agregados_por_bairros_pessoas_indigenas_BR.zip` | 905,069 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `b9d41e8c2af9394a…` | agregados por BAIRRO, tema pessoas_indigenas (só recorte BR) |
| `tabelas/Agregados_por_bairros_pessoas_quilombolas_BR.zip` | 510,748 | Tue, 12 Nov 2024 18:50:25 GMT | 2026-09-20 | `5a2d2b7fbe7ba965…` | agregados por BAIRRO, tema pessoas_quilombolas (só recorte BR) |
| `tabelas/Agregados_por_setores_alfabetizacao_BR.zip` | 142,133,036 | Tue, 12 Nov 2024 18:50:37 GMT | 2026-09-20 | `3b2de94e0099d9b6…` | agregados por setor censitário, tema alfabetizacao (só recorte BR) |
| `tabelas/Agregados_por_setores_basico_BR_20260520.zip` | 15,418,417 | Wed, 20 May 2026 13:37:23 GMT | 2026-09-20 | `ec04624286233d69…` | agregados por setor censitário, tema basico (só recorte BR) |
| `tabelas/Agregados_por_setores_caracteristicas_domicilio1_BR.zip` | 24,196,895 | Tue, 12 Nov 2024 18:50:33 GMT | 2026-09-20 | `8e0a27fc90912acb…` | agregados por setor censitário, tema caracteristicas_domicilio1 (só recorte BR) |
| `tabelas/Agregados_por_setores_caracteristicas_domicilio2_BR_20250417.zip` | 83,971,374 | Thu, 17 Apr 2025 12:52:59 GMT | 2026-09-20 | `513f8a0d9c84b132…` | agregados por setor censitário, tema caracteristicas_domicilio2 (só recorte BR) |
| `tabelas/Agregados_por_setores_caracteristicas_domicilio3_BR_20250417.zip` | 52,708,037 | Thu, 17 Apr 2025 12:52:59 GMT | 2026-09-20 | `f38010582b8329f4…` | agregados por setor censitário, tema caracteristicas_domicilio3 (só recorte BR) |
| `tabelas/Agregados_por_setores_cor_ou_raca_BR.zip` | 43,838,759 | Tue, 12 Nov 2024 18:50:39 GMT | 2026-09-20 | `cd4d628878f619b6…` | agregados por setor censitário, tema cor_ou_raca (só recorte BR) |
| `tabelas/Agregados_por_setores_demografia_BR.zip` | 22,554,090 | Tue, 12 Nov 2024 18:50:40 GMT | 2026-09-20 | `f8486233ce2f6559…` | agregados por setor censitário, tema demografia (só recorte BR) |
| `tabelas/Agregados_por_setores_domicilios_indigenas_BR.zip` | 7,603,193 | Tue, 12 Nov 2024 18:50:40 GMT | 2026-09-20 | `26e5119a3d3a3d66…` | agregados por setor censitário, tema domicilios_indigenas (só recorte BR) |
| `tabelas/Agregados_por_setores_domicilios_quilombolas_BR.zip` | 4,766,321 | Tue, 12 Nov 2024 18:50:40 GMT | 2026-09-20 | `80d275a382194216…` | agregados por setor censitário, tema domicilios_quilombolas (só recorte BR) |
| `tabelas/Agregados_por_setores_obitos_BR.zip` | 20,612,331 | Tue, 12 Nov 2024 18:50:41 GMT | 2026-09-20 | `c230b74335003f25…` | agregados por setor censitário, tema obitos (só recorte BR) |
| `tabelas/Agregados_por_setores_parentesco_BR.zip` | 62,934,980 | Tue, 12 Nov 2024 18:50:42 GMT | 2026-09-20 | `d2abcb832f1176c3…` | agregados por setor censitário, tema parentesco (só recorte BR) |
| `tabelas/Agregados_por_setores_pessoas_indigenas_BR.zip` | 18,077,907 | Tue, 12 Nov 2024 18:50:41 GMT | 2026-09-20 | `31a1e1af798966ec…` | agregados por setor censitário, tema pessoas_indigenas (só recorte BR) |
| `tabelas/Agregados_por_setores_pessoas_quilombolas_BR.zip` | 10,360,733 | Tue, 12 Nov 2024 18:50:42 GMT | 2026-09-20 | `0b6ee915a975f3eb…` | agregados por setor censitário, tema pessoas_quilombolas (só recorte BR) |
| `tabelas/Area_efetivamente_domiciliada_e_densidade_ajustada_dos_Setores_Censitarios.xlsx` | 40,038,220 | Wed, 13 Nov 2024 21:35:16 GMT | 2026-09-20 | `897caa7861bf0cca…` | área efetivamente domiciliada e densidade ajustada por setor |
| `tabelas/Populacao_residente_por_situacao_do_domicilio_municipios.xlsx` | 273,016 | Wed, 13 Nov 2024 18:53:32 GMT | 2026-09-20 | `5f8d434b2e181cb7…` | TOTAL OFICIAL por município, 2022 — usado para conferir a soma dos setores |

URLs exatas:

- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_alfabetizacao_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_basico_BR_20260520.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_caracteristicas_domicilio1_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_caracteristicas_domicilio2_BR_20250417.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_caracteristicas_domicilio3_BR_20250417.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_cor_ou_raca_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_demografia_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_domicilios_indigenas_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_domicilios_quilombolas_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_obitos_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_parentesco_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_pessoas_indigenas_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Bairro_csv/Agregados_por_bairros_pessoas_quilombolas_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_alfabetizacao_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_caracteristicas_domicilio1_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_caracteristicas_domicilio2_BR_20250417.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_caracteristicas_domicilio3_BR_20250417.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_cor_ou_raca_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_demografia_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_domicilios_indigenas_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_domicilios_quilombolas_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_obitos_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_parentesco_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_pessoas_indigenas_BR.zip`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/Agregados_por_Setor_csv/Agregados_por_setores_pessoas_quilombolas_BR.zip`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/Area_efetivamente_domiciliada_e_densidade_ajustada_dos_Setores_Censitarios.xlsx`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/tabelas_complementares/Populacao_residente_por_situacao_do_domicilio_municipios.xlsx`

## cnefe (4 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `cnefe/4301602.zip` | 356,062 | Wed, 31 Jan 2024 19:30:38 GMT | 2026-09-20 | `34d773bd6a6e6582…` | coordenadas dos endereços do Censo 2022, recorte MUNICÍPIO de Bagé |
| `cnefe/4301602_BAGE.zip` | 1,343,601 | Mon, 20 May 2024 22:54:38 GMT | 2026-09-20 | `3cb40d650571397a…` | CNEFE 2022, endereço a endereço, recorte MUNICÍPIO de Bagé |
| `cnefe/Dicionario_CNEFE_Censo_2022.xls` | 13,312 | Mon, 20 May 2024 22:50:03 GMT | 2026-09-20 | `7b3684a709cd28a5…` | dicionário do CNEFE 2022 (define ESPECIE e os demais campos) |
| `cnefe/Dicionario_Coordenadas_Censo2022.xls` | 9,216 | Wed, 31 Jan 2024 19:29:53 GMT | 2026-09-20 | `65fdf7835ba9a077…` | dicionário das coordenadas dos endereços |

URLs exatas:

- `https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Coordenadas_enderecos/Municipio/43_RS/4301602.zip`
- `https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV/Municipio/43_RS/4301602_BAGE.zip`
- `https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV/Dicionario_CNEFE_Censo_2022.xls`
- `https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Coordenadas_enderecos/Dicionario_Coordenadas_Censo2022.xls`

## documentacao (5 arquivos)

| arquivo | bytes | Last-Modified | baixado em | sha256 | o que é |
|---|---:|---|---|---|---|
| `documentacao/Dicionario_de_dados_malha_agregados.xlsx` | 18,860 | Wed, 13 Nov 2024 21:36:56 GMT | 2026-09-20 | `0dffb669ee90e1ff…` | dicionário de dados da malha com atributos |
| `documentacao/Historico_formacao_Setores_Censitarios_2010_2022.xlsx` | 83,684,271 | Wed, 13 Nov 2024 21:35:07 GMT | 2026-09-20 | `d70a9e6a46bbd73f…` | histórico de formação dos setores 2010→2022 (de/para), base da comparabilidade |
| `documentacao/Leia_me_Area_efetivamente_ocupada.pdf` | 674,327 | Wed, 13 Nov 2024 21:34:53 GMT | 2026-09-20 | `330499e9319826d8…` | leia-me da área efetivamente ocupada e densidade ajustada |
| `documentacao/Leia_me_Comparabilidade_2010_2022.pdf` | 401,284 | Wed, 13 Nov 2024 21:34:53 GMT | 2026-09-20 | `06a2783458253b10…` | RESSALVA DE COMPARABILIDADE 2010 × 2022, do próprio IBGE |
| `documentacao/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx` | 118,369 | Tue, 12 May 2026 21:29:48 GMT | 2026-09-20 | `0b8aedece57f6125…` | dicionário de dados dos agregados por setores (versão 20/05/2026, a mais recente) |

URLs exatas:

- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/Dicionario_de_dados_malha_agregados.xlsx`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/Historico_formacao_Setores_Censitarios_2010_2022.xlsx`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/Leia_me_Area_efetivamente_ocupada.pdf`
- `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/Leia_me_Comparabilidade_2010_2022.pdf`
- `https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx`

## Notas metodológicas e dicionários baixados

- `dicionario_de_dados_agregados_por_setores_censitarios_20260520.xlsx` — dicionário de dados dos agregados por setores (versão 20/05/2026, a mais recente)
- `Dicionario_de_dados_malha_agregados.xlsx` — dicionário de dados da malha com atributos
- `Leia_me_Comparabilidade_2010_2022.pdf` — RESSALVA DE COMPARABILIDADE 2010 × 2022, do próprio IBGE
- `Leia_me_Area_efetivamente_ocupada.pdf` — leia-me da área efetivamente ocupada e densidade ajustada
- `Historico_formacao_Setores_Censitarios_2010_2022.xlsx` — histórico de formação dos setores 2010→2022 (de/para), base da comparabilidade

**A nota metodológica n. 06 NÃO está no FTP nem no geoftp.** Esta sessão navegou `Censos/Censo_Demografico_2022/` inteiro e as subpastas de `Agregados_por_Setores_Censitarios`: não existe pasta de notas metodológicas nesses dois hosts. A nota é publicada na biblioteca do IBGE (`biblioteca.ibge.gov.br`), fora dos dois hosts autorizados — por isso não foi baixada. Falta autorização para esse host.

## Ressalvas de comparabilidade

O IBGE publica, junto da malha de 2022, duas peças que tratam de comparabilidade — e as
duas estão baixadas em `documentacao/`:

- **`Leia_me_Comparabilidade_2010_2022.pdf`** — a ressalva do próprio IBGE sobre comparar 2010 com
  2022. É o documento a ler antes de qualquer série temporal por setor.
- **`Historico_formacao_Setores_Censitarios_2010_2022.xlsx`** (83,7 MB) — o de/para de formação dos
  setores entre 2010 e 2022. Sem ele, comparar setor a setor entre os dois censos não se sustenta:
  os setores foram redesenhados.

Medido nesta sessão: **Bagé tem 199 setores em 2022 e 164 na tabela de 2010** (168 na malha de
2010). Os códigos de setor **não são os mesmos entre censos** — a comparação tem de passar pelo
de/para, ou ser feita por agregação a um recorte estável (município, ou os polígonos do estudo).

**Recorte disponível:** os agregados por setor e por bairro de 2022 existem **só para o Brasil
inteiro** (`_BR.zip`) — não há corte por UF nem por município. A malha, sim, tem corte por UF.

## Inventário de Bagé (4301602) medido sobre estes arquivos

Ver `trabalho/censo/inventario_bage_censos.json` e `trabalho/censo/dicionario_variaveis_rascunho.csv`. Resumo:

- **199 setores**, {'Urbana': 173, 'Rural': 26}; a tabela e a malha têm **exatamente os mesmos 199 códigos** (0 só na tabela, 0 só na malha);
- **população `v0001` = 117.938**, igual ao total oficial (urbana 114.883 + rural 3.055) — **diferença 0**;
- domicílios: `v0002` total 53.716 · `v0003` particulares 53.629 · `v0004` coletivos 87 · `v0007` particulares ocupados 45.327;
- malha em **EPSG:4674 (SIRGAS 2000)**, 0 geometria inválida, 0 nula;
- os dois pacotes de malha do IBGE (com atributos e territorial) têm, em Bagé, **geometria idêntica** (diferença simétrica 0) e diferem só em colunas (37 × 30);
- **CNEFE 2022 de Bagé: 62.782 endereços, 34 campos, 100 % com coordenada.** As espécies 1 e 2 do CNEFE (53.629 domicílios particulares e 87 coletivos) coincidem **exatamente** com `v0003` e `v0004` do agregado por setores — conferência independente entre dois produtos diferentes do mesmo Censo;
- **Bagé NÃO tem bairro na divulgação do IBGE 2022**: 162 dos 497 municípios do RS têm, e Bagé não é um deles (0 por `CD_MUN`, 0 por `NM_MUN`, e os 199 setores com `NM_BAIRRO` vazio; controle negativo em Porto Alegre, 99 bairros).
