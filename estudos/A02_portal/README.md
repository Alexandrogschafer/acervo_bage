# A02 — Portal

**Status:** reconhecimento · **Manifesto:** [`manifesto.yaml`](manifesto.yaml)

Geoportal do acervo: publicação das camadas liberadas em mapa Leaflet
estático, consumindo `data/geoportal/`.

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

## Situação herdada da estrutura anterior

`scripts/` recebeu, na reestruturação, o portal da execução anterior:

- `map-init.js` — inicialização do mapa e do painel lateral;
- `layers.js` — montagem das camadas a partir de um `catalogo.json`.

Aquele portal carregava o limite municipal e montava painel, rodapé de fontes
e licenças a partir do catálogo, com teste headless passando. Ele **não** é o
portal vigente: o `index.html` na raiz voltou a ser um esqueleto sem camadas,
conforme a reestruturação. Estes dois arquivos ficam aqui como ponto de
partida para reconstruir a publicação dentro da nova arquitetura.
