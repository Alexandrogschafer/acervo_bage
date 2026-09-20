# A01 — Base cartográfica

**Status:** reconhecimento · **Manifesto:** [`manifesto.yaml`](manifesto.yaml)

Reconhecimento e consolidação da base cartográfica de referência de
Bagé/RS: limite municipal, malhas e divisões territoriais que servem de
recorte para todos os demais estudos.

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
