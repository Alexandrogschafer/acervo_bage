# Índice — camadas do acervo × estudos

> **ARQUIVO GERADO. Não edite à mão.**
> Regere com `python scripts/utils/indice.py`; qualquer edição manual
> é perdida na próxima execução. A fonte são os
> `estudos/*/manifesto.yaml`, resolvidos contra `data/catalogo_camadas.csv`
> (bloco `camadas:`) e `data/catalogo_fontes.csv` + o `.json` irmão de cada
> arquivo (bloco `fontes_brutas:`).

- **Gerado em:** 2026-09-22 23:10:35 -0300
- **Estudos encontrados:** 3

`camadas:` é produto curado do acervo (`data/catalogo_camadas.csv`);
`fontes_brutas:` é dado bruto em `data/raw/` (`data/catalogo_fontes.csv`).
A diferença está em `docs/convencoes.md`.

## Camada → estudos que a consomem

| Camada | Estudos | Situação |
| --- | --- | --- |
| `limite_municipal` | `ACERVO_BAGE-A03_expansao_adensamento` | ok |
| `setores_2022` | `ACERVO_BAGE-A03_expansao_adensamento` | ok |

## Fonte bruta → estudos que a consomem

| Fonte | Arquivos | Estudos | Situação |
| --- | ---: | --- | --- |
| `ibge_censo2010_agregados_setores` | 1 | `ACERVO_BAGE-A03_expansao_adensamento` | ok |
| `ibge_censo2022_agregados_setores` | 3 | `ACERVO_BAGE-A03_expansao_adensamento` | ok |
| `ibge_censo2022_entorno_setores` | 2 | `ACERVO_BAGE-A03_expansao_adensamento` | ok |
| `ibge_grade_estatistica_2010` | 2 | `ACERVO_BAGE-A03_expansao_adensamento` | ok |
| `ibge_grade_estatistica_2022` | 2 | `ACERVO_BAGE-A03_expansao_adensamento` | ok |

## Estudo → camadas e fontes brutas que consome

### `ACERVO_BAGE-A01_base-cartografica`

- **Manifesto:** `estudos/A01_base-cartografica/manifesto.yaml`
- **Status:** reconhecimento
- **Pergunta:** A DEFINIR — depende do reconhecimento dos dados
- **Referências:** —

**Camadas do acervo**

Nenhuma camada declarada ainda.

**Fontes brutas (`data/raw/`)**

Nenhuma fonte bruta declarada.

### `ACERVO_BAGE-A02_portal`

- **Manifesto:** `estudos/A02_portal/manifesto.yaml`
- **Status:** reconhecimento
- **Pergunta:** A DEFINIR — depende do reconhecimento dos dados
- **Referências:** —

**Camadas do acervo**

Nenhuma camada declarada ainda.

**Fontes brutas (`data/raw/`)**

Nenhuma fonte bruta declarada.

### `ACERVO_BAGE-A03_expansao_adensamento`

- **Manifesto:** `estudos/A03_expansao_adensamento/manifesto.yaml`
- **Status:** planejado
- **Pergunta:** Bagé ganhou 6.791 domicílios ocupados (+17,6 %) com a população praticamente estável (+1,0 %) entre 2010 e 2022. ONDE, no território do município, esse crescimento de domicílios se materializou — em ocupação de área nova ou em adensamento da área já ocupada —, e QUE INFRAESTRUTURA URBANA existe em 2022 nas áreas que cresceram, comparada à do restante da cidade?
- **Referências:** —

**Camadas do acervo**

| Camada | Versão (manifesto) | Situação | Detalhe |
| --- | --- | --- | --- |
| `limite_municipal` | 1.0 | ok | confere (por sha256 do arquivo) |
| `setores_2022` | censo_2022 | ok | confere (por sha256 do arquivo) |

**Fontes brutas (`data/raw/`)**

| Fonte | Arquivo | Versão (manifesto) | Situação | Detalhe |
| --- | --- | --- | --- | --- |
| `ibge_grade_estatistica_2010` | `data/raw/vetor/ibge/censo_2010/grade_estatistica/grade_id14.zip` | censo_2010 | ok | confere (por sha256 do arquivo) |
| `ibge_grade_estatistica_2010` | `data/raw/vetor/ibge/censo_2010/grade_estatistica/grade_id04.zip` | censo_2010 | ok | confere (por sha256 do arquivo) |
| `ibge_grade_estatistica_2022` | `data/raw/vetor/ibge/censo_2022/grade_estatistica/grade_id14.zip` | censo_2022 | ok | confere (por sha256 do arquivo) |
| `ibge_grade_estatistica_2022` | `data/raw/vetor/ibge/censo_2022/grade_estatistica/grade_id04.zip` | censo_2022 | ok | confere (por sha256 do arquivo) |
| `ibge_censo2010_agregados_setores` | `data/raw/tabular/ibge/censo_2010/RS_20260615.zip` | censo_2010 | ok | confere (por sha256 do arquivo) |
| `ibge_censo2022_agregados_setores` | `data/raw/tabular/ibge/censo_2022/Agregados_por_setores_basico_BR_20260520.zip` | censo_2022 | ok | confere (por sha256 do arquivo) |
| `ibge_censo2022_agregados_setores` | `data/raw/tabular/ibge/censo_2022/Agregados_por_setores_caracteristicas_domicilio1_BR.zip` | censo_2022 | ok | confere (por sha256 do arquivo) |
| `ibge_censo2022_entorno_setores` | `data/raw/tabular/ibge/censo_2022/Agregados_por_setores_entorno_domicílios_BR.zip` | censo_2022 | ok | confere (por sha256 do arquivo) |
| `ibge_censo2022_entorno_setores` | `data/raw/tabular/ibge/censo_2022/Agregados_por_setores_entorno_faces_BR.zip` | censo_2022 | ok | confere (por sha256 do arquivo) |
| `ibge_censo2022_agregados_setores` | `data/raw/tabular/ibge/censo_2022/doc/Historico_formacao_Setores_Censitarios_2010_2022.xlsx` | censo_2022 | ok | confere (por sha256 do arquivo) |

