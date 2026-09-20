# Ressalvas do Censo e do CNEFE para Bagé/RS

Quem usar os arquivos de `data/acervo/censo/` neste acervo precisa ler isto antes.
São conclusões **medidas** sobre estes arquivos exatos — os mesmos sha256 que estão
no `.json` irmão de cada um e em `data/catalogo_fontes.csv` — no projeto REVIA_BG
(`~/projetos/rede_viaria_bage`), de onde os arquivos vieram por cópia em 20/09/2026.

Não são opinião nem estimativa: cada número abaixo saiu de uma contagem sobre o
arquivo. O que não foi medido está dito como não medido.

**Município:** Bagé/RS, código IBGE `4301602`.

---

## 1. A soma dos setores fecha em 2022, e não fecha em 2010

| censo | soma dos setores | total oficial do município | diferença | serve como total municipal? |
| --- | ---: | ---: | ---: | --- |
| 2022 | **117.938** | 117.938 | **0** | **sim** |
| 2010 | 116.318 (`V002`) | 116.794 | **−476** (−0,408 %) | **não** |
| 2000 | 117.893 (`Var12`) | 118.767 | −874 | não, mas por outro motivo (§ 4) |

Em 2022 a soma dos **199 setores** de Bagé fecha **exatamente** com o total oficial
(urbana 114.883 + rural 3.055). A tabela e a malha têm os mesmos 199 códigos:
0 só na tabela, 0 só na malha.

## 2. 2010: quatro setores sem linha na tabela — causa em aberto

A malha de 2010 tem **168 setores** em Bagé; a tabela de agregados tem **164**.
**Quatro setores existem na malha e não têm linha na tabela** — três sedes de distrito
e um rural — e **não aparecem em nenhuma das 26 planilhas** do pacote.

A causa **não foi determinada**; fica declarada em aberto. A consequência é operacional
e não depende de descobrir a causa:

> **A soma dos setores de 2010 NÃO serve como total municipal.** Para o total de 2010,
> usar a tabela oficial por município (`2010/tabelas/rio_grande_do_sul.zip`), não a soma.

## 3. 2000: a diferença é de recorte, não erro

`Var12` (moradores em domicílios particulares permanentes) soma **117.893** contra
**118.767** oficiais, −874. **Não é erro de soma nem de junção:** as duas quantidades
medem coisas diferentes — o total oficial inclui **domicílios improvisados e coletivos**,
que `Var12` por definição não conta. Comparar as duas como se fossem a mesma grandeza
produz uma discrepância que não existe.

Ressalva adicional de 2000, do lado espacial:

- a malha urbana de Bagé (`2000/malha/4301602.zip`, 127 setores) vem declarada em
  **EPSG:32621 — UTM 21 NORTE**, hemisfério errado para Bagé: é erro de declaração no
  `.prj`, não dado do sul projetado. **7 das 127 geometrias são inválidas**;
- a malha rural (`rs_setores_censitarios.zip`, 47 setores em Bagé) vem **sem CRS declarado**;
- o CRS tem de ser decidido e registrado **antes** de qualquer medição métrica;
- as **tabelas de 2000 não foram lidas** no REVIA_BG: vêm só em `.XLS` legado (BIFF8) e
  aquele ambiente não tinha leitor. Os arquivos estão guardados intactos; falta o leitor.

## 4. Comparabilidade 2010 → 2022: o geocódigo não é identificador estável

Só **141 dos 199 setores de 2022 (70,9 %)** têm correspondência **1:1** com 2010.
**21 setores de 2010 foram divididos**, chegando a **6 destinos**.

> **O geocódigo de setor NÃO é identificador estável entre censos.** Qualquer série
> temporal por setor tem de passar pelo de/para do IBGE —
> `data/acervo/censo/2022/documentacao/Historico_formacao_Setores_Censitarios_2010_2022.xlsx`
> — ou usar um recorte estável (bairros, município).

O próprio IBGE publica a ressalva em
`data/acervo/censo/2022/documentacao/Leia_me_Comparabilidade_2010_2022.pdf`.

Juntar 2010 com 2022 por igualdade de geocódigo **não gera erro**: gera número plausível
e falso, porque parte dos códigos casa por coincidência de recorte parcial.

## 5. Bagé não tem bairros na divulgação do Censo 2022

Medido nos 199 setores de Bagé por `CD_MUN`, `NM_MUN` e `NM_BAIRRO`: **Bagé não tem
bairro na divulgação do IBGE de 2022**. Dos 497 municípios do RS, 162 têm; Bagé não é
um deles, e os 199 setores têm `NM_BAIRRO` vazio.

**Controle negativo:** a mesma medição em **Porto Alegre** devolve **99 bairros** — ou
seja, a contagem zero em Bagé é ausência real na fonte, não filtro quebrado.

Consequência: `2022/malha/ftp_com_atributos/RS_bairros_CD2022.gpkg` está no acervo pelo
RS e como controle, **não** como fonte de bairros de Bagé. Para bairros de Bagé existe a
camada própria do REVIA_BG (decisão DN-B1), com dois recortes — administrativo e
recortado pela mancha urbana —, e todo cruzamento "por bairro" tem de declarar qual usa.

## 6. CNEFE 2022 de Bagé

**62.782 endereços, 34 campos, 100 % com coordenada.** **93,84 %** caem dentro da mancha
urbana v2.3 do REVIA_BG.

| espécie | endereços |
| --- | ---: |
| domicílio particular | 53.629 |
| domicílio coletivo | 87 |
| estabelecimento agropecuário | 1.427 |
| estabelecimento de ensino | 122 |
| estabelecimento de saúde | 238 |
| estabelecimento de outras finalidades | 6.092 |
| edificação em construção | 931 |
| estabelecimento religioso | 256 |

**Conferência independente entre dois produtos do mesmo Censo:** as espécies 1 e 2 do
CNEFE (53.629 e 87) coincidem **exatamente** com `v0003` e `v0004` do agregado por
setores. São arquivos diferentes, diretórios diferentes e datas de divulgação diferentes
— é uma medida que tinha de bater e bateu.

**Dado de endereço.** Publicar qualquer derivado do CNEFE no geoportal exige decidir
antes o nível de agregação; o arquivo bruto não vai para `data/geoportal/`.

---

## Licença, e o que não foi possível confirmar

A licença registrada em `data/catalogo_fontes.csv` é a **declaração dos próprios
servidores que serviram estes arquivos**, conferida em 20/09/2026 (HTTP 200):

> "Todos os arquivos aqui disponíveis são públicos."
> — raiz de `https://ftp.ibge.gov.br/` e de `https://geoftp.ibge.gov.br/`

**O que não foi lido:** a página formal de termos de uso do IBGE
(`www.ibge.gov.br/acesso-informacao/acoes-e-programas/termos-de-uso.html`) respondeu
**HTTP 403** (desafio Cloudflare, com e sem cabeçalhos de navegador) em 20/09/2026.
A licença citada acima é a do servidor de download, **não** a dessa página, e nada foi
transcrito dela. Se a página formal declarar condição adicional — atribuição em formato
específico, restrição de uso comercial —, ela **ainda não foi conferida**, e
`autorizacao_fonte = true` nas nove linhas se apoia na declaração do FTP e na
prática já adotada para as demais fontes IBGE do acervo.

## Procedência

Nenhum destes arquivos foi baixado por este repositório. Todos vieram por **cópia** de
`~/projetos/rede_viaria_bage/dados/externos/censo/` (projeto REVIA_BG), que os baixou das
fontes oficiais do IBGE em 20/09/2026 navegando as listagens do FTP — nenhuma URL montada
por adivinhação. A cópia foi conferida arquivo a arquivo (sha256 origem = sha256 cópia) e
a origem saiu inalterada.

Cada arquivo tem seu `.json` irmão com URL exata, `Last-Modified` do servidor, data do
download original, data da cópia, sha256 e o caminho de origem.
`data/acervo/censo/manifesto_copia_censo.json` cobre a árvore inteira, inclusive os
`FONTE.md` e os `manifesto_censo_<ano>.json` do REVIA_BG, que vieram junto.

Script: `scripts/download/censo_revia_bg.py`.
