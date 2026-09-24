# Licença da documentação e dos produtos próprios do acervo

Copyright (c) 2026 Alexandro Schafer / UNIPAMPA

A documentação e os produtos próprios do ACERVO_BAGE estão licenciados sob a
**Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)**. O texto legal da
licença está em <https://creativecommons.org/licenses/by/4.0/legalcode.pt>.

## O que está sob CC BY 4.0

- a documentação: `README.md`, `docs/`, `CLAUDE.md`, os `README.md` dos estudos e os
  textos de `bibliografia/` escritos aqui;
- os **catálogos**: `data/catalogo_*.csv`;
- os **metadados**: os `.json` irmãos, os manifestos e os registros de procedência;
- os **textos dos estudos**: `estudos/*/*.md`;
- as **figuras produzidas aqui**, quando a publicação delas é permitida (ver abaixo).

O **código** (scripts, geoportal e testes) está sob a licença **MIT**, no arquivo
[`LICENSE`](LICENSE).

## O que NÃO está sob CC BY 4.0: os dados

- **Os dados seguem a licença de cada fonte.** Ela está registrada camada a camada em
  `data/catalogo_fontes.csv` e `data/catalogo_camadas.csv` e no `.json` irmão de cada
  arquivo.
  - O acervo **não relicencia** dado de terceiro.
  - Esta licença não se aplica a nenhum dado de terceiro, mesmo quando ele está
    citado, tabulado ou desenhado num produto daqui.
- **Nenhuma saída é mais permissiva que a fonte dela.** Uma figura, uma tabela ou uma
  camada derivada herda a restrição mais restritiva entre as suas entradas
  (`scripts/utils/publicacao.py`; `docs/convencoes.md` § 7). Onde a fonte é mais
  restritiva que a CC BY 4.0, vale a restrição da fonte.
- **As camadas sem autorização de republicação continuam sem ela.** São as do geobage
  e do GeoDataBase, a camada de bairros e loteamentos revisada e a evolução urbana do
  IPHAN, entre outras: `pode_publicar=false` e fora do repositório. Esta licença não
  muda isso.

## Como atribuir

> Schafer, A. / UNIPAMPA. *ACERVO_BAGE — acervo de dados e estudos sobre Bagé/RS*,
> 2026. Licença CC BY 4.0 (documentação) e MIT (código).

Cite também a fonte de cada dado usado, como registrada no catálogo.
