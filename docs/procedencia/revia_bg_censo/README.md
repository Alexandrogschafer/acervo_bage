# Procedência — cópia do Censo vinda do REVIA_BG (registro histórico)

Estes arquivos **não são editados**. São o rastro de como os arquivos do Censo
(2000, 2010, 2022) e do CNEFE 2022 chegaram a este repositório:

- em **2026-09-20** o projeto REVIA_BG (`~/projetos/rede_viaria_bage`) baixou os
  arquivos do IBGE (`ftp.ibge.gov.br`, `geoftp.ibge.gov.br`) navegando as
  listagens, e registrou URL, `Last-Modified`, bytes e sha256 em
  `manifesto_censo_<ano>.json` e `FONTE.md`;
- no mesmo dia, `scripts/download/censo_revia_bg.py` os **copiou** para
  `data/acervo/censo/`, gerando os `.json` irmãos (com `origem_da_copia`) e
  `manifesto_copia_censo.json`;
- em **2026-09-22** os 50 arquivos de dado foram **movidos** (sha256 conferido
  antes e depois) para `data/raw/tabular/ibge/censo_<ano>/` e
  `data/raw/vetor/ibge/censo_<ano>/`, com `.json` irmãos novos, e passaram a
  ser obtidos direto do IBGE por `scripts/download/baixar_censo_ibge.py`, a
  partir da lista fixa `config/fontes_censo_ibge.yaml`. A malha territorial de
  setores 2022 do geoftp já tinha sido aposentada antes (ver o `.json` em
  `2022/malha/geoftp_malha_territorial/`).

A árvore aqui reproduz a de `data/acervo/censo/` no momento da mudança. Os
caminhos citados DENTRO destes arquivos são os da época (no REVIA_BG ou em
`data/acervo/censo/`) e não foram atualizados de propósito.
