# A03 — Censo

**Status:** reconhecimento · **Manifesto:** [`manifesto.yaml`](manifesto.yaml)

Reconhecimento do Censo Demográfico (2000, 2010, 2022) e do CNEFE 2022
para Bagé/RS. O dado bruto está em `data/raw/tabular/ibge/censo_<ano>/` e
`data/raw/vetor/ibge/censo_<ano>/` (obtido por `scripts/download/baixar_censo_ibge.py`);
`data/acervo/censo/` fica para as camadas curadas do censo.

**Reconhecimento dos dados: [`reconhecimento.md`](reconhecimento.md)** — o que os
dados de 2000, 2010, 2022 e do CNEFE permitem medir, o que não permitem e com que
ressalvas (variáveis por censo, totais, geografia entre censos, sigilo, CNEFE ×
setores), com os scripts que reproduzem cada número em [`scripts/`](scripts/).

**Antes de usar qualquer número, ler [`docs/ressalvas_censo_bage.md`](../../docs/ressalvas_censo_bage.md)**:
a soma dos setores fecha em 2022 e não fecha em 2010; a malha de 2000 vem com
CRS declarado errado; o geocódigo de setor não é estável entre censos.

## Como este estudo se relaciona com o acervo

Este estudo **lê** o acervo e **nunca escreve nele**. As camadas que consome
são declaradas em `manifesto.yaml`, com versão e sha256 fixados — é o
contrato que diz sobre qual estado do acervo os resultados foram produzidos.

- `scripts/`    — código próprio do estudo
- `derivados/`  — intermediários (fora do git; só os `.json` irmãos entram)
- `saidas/`     — resultados (fora do git; só os `.json` irmãos entram)

Se uma camada derivada aqui tiver valor para os demais estudos, ela entra no
acervo por **promoção**: conferência visual do responsável, depois cópia para
`data/acervo/<tema>/` com linha em `data/catalogo_camadas.csv`. Nunca por
escrita direta.

A publicação de qualquer saída herda a restrição **mais restritiva** entre as
camadas declaradas no manifesto (`scripts/utils/publicacao.py`). Enquanto o
manifesto não declarar camada nenhuma, nada daqui pode ser publicado.

## Pergunta

**A DEFINIR** — depende do reconhecimento dos dados.
