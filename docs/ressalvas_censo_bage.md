# Ressalvas do Censo e do CNEFE para Bagé/RS

> **Origem destas ressalvas:** medições feitas no projeto **REVIA_BG**
> (`~/projetos/rede_viaria_bage`) sobre os arquivos do IBGE que ele baixou em
> 20/09/2026. Não foram refeitas aqui; valem porque os arquivos deste
> repositório têm o **mesmo sha256** dos medidos lá. Desde 22/09/2026 esses
> arquivos ficam como dado bruto em `data/raw/tabular/ibge/censo_<ano>/` e
> `data/raw/vetor/ibge/censo_<ano>/`, obtidos direto do IBGE por
> `scripts/download/baixar_censo_ibge.py` (lista fixa em
> `config/fontes_censo_ibge.yaml`). A procedência da cópia original está em
> `docs/procedencia/revia_bg_censo/`.

Quem usar os arquivos brutos do Censo (`data/raw/*/ibge/censo_<ano>/`) neste acervo precisa ler isto antes.
São conclusões **medidas** sobre estes arquivos exatos — os mesmos sha256 que estão
no `.json` irmão de cada um e em `data/catalogo_fontes.csv` — no projeto REVIA_BG
(`~/projetos/rede_viaria_bage`), de onde os arquivos vieram por cópia em 20/09/2026.

Não são opinião nem estimativa: cada número abaixo saiu de uma contagem sobre o
arquivo. O que não foi medido está dito como não medido.

**Município:** Bagé/RS, código IBGE `4301602`.

---

## 1. A soma dos setores fecha nos três censos — comparando a mesma grandeza

*Corrigido em 2026-09-22 (texto anterior preservado na seção
[Corrigido em 2026-09-22](#corrigido-em-2026-09-22)). Medição:
`estudos/A03_censo/reconhecimento.md` § 2, script `estudos/A03_censo/scripts/r02_totais.py`.*

Cada soma de setores confrontada com o total oficial **da mesma grandeza**:

| censo | grandeza | soma dos setores (urbana / rural) | total oficial | diferença |
| --- | --- | --- | --- | ---: |
| 2022 | população (`v0001`) | 117.938 (114.883 / 3.055) | 117.938 (114.883 / 3.055) | **0** |
| 2010 | população (`Domicilio02 V001`) | 116.794 (97.765 / 19.029) | 116.794 (97.765 / 19.029) | **0** |
| 2010 | DPP (`Basico V001`) | 38.504 (32.642 / 5.862) | 38.504 | **0** |
| 2010 | moradores em DPP (`Basico V002`) | 116.318 (97.304 / 19.014) | 116.318 | **0** |
| 2000 | população (`Pessoa1 V1330`) | 118.767 (97.290 / 21.477) | 118.767 (97.290 / 21.477) | **0** |
| 2000 | DPP (`Basico Var01`) | 35.119 | 35.119 | **0** |

Em 2010 a igualdade vale também **distrito a distrito**, nas três grandezas.

**A soma dos setores serve como total municipal nos três censos.** O que não se pode é
comparar grandezas diferentes: `V002` de 2010 e `Var12` de 2000 são **moradores em
domicílios particulares permanentes**, e ficam abaixo da população total porque ela
inclui domicílios improvisados e coletivos (2010: 116.318 × 116.794; 2000: 117.893 ×
118.767). Era essa a origem das diferenças de −476 (2010) e −874 (2000) registradas
antes.

## 2. 2010: quatro setores sem linha na tabela — contribuem zero

A malha de 2010 tem **168 setores** em Bagé; as tabelas, **164**. Os 4 sem linha:
`430160205000142` (rural, entre a Estrada dos Vieiras, o rio Negro e a BR-153) e as
sedes das vilas de Joca Tavares (`430160217000001`), José Otávio (`430160220000001`) e
Palmas (`430160221000001`), desenhadas como quadrados de ~100 m em torno de escola ou
subprefeitura.

Procurados em **todos** os arquivos de dados da divulgação de 2010 (26 CSV e 26 XLS), na
documentação, nas 21 tabelas por município/distrito e no de/para 2010→2022: aparecem
**só** na descrição dos setores (`Descrição_RS.xls`) e no de/para, **em nenhum arquivo
de dados**.

Como os totais fecham exatamente sem eles — no município e em cada distrito (§ 1) —, os
4 **contribuem zero pessoas e zero domicílios**. A razão da omissão não está escrita na
divulgação; "setor sem domicílio não tem linha" é inferência coerente com os totais, não
afirmação do IBGE. O setor `430160221000001` reaparece em 2022 só na tabela básica, com
população 0.

## 3. 2000: o território não é o de hoje; a malha tem CRS a resolver

**Território.** A própria divulgação de 2000 traz `Compatibilização_2000-2001_RS.xls`:
**11 setores** de Bagé (distritos `…10` e `…12`) passaram a **Aceguá**, instalado em
2001 — **3.927 pessoas** e 1.147 DPP. Bagé de 2000 no território de 2001 = **114.840**
habitantes, o mesmo número da planilha oficial "Municípios instalados em 2001". Na
geometria, 1.545 km² desses setores estão hoje em Aceguá. Comparação 2000 × 2010/2022
do município inteiro tem de descontar esses setores.

Lado espacial:

- a malha urbana de Bagé (`data/raw/vetor/ibge/censo_2000/4301602.zip`, 127 setores) vem
  declarada em **EPSG:32621 — UTM 21 NORTE**, hemisfério errado para Bagé. Lida em UTM 21
  Sul (WGS 84, SAD69 ou SIRGAS) ela cai inteira sobre a cidade, com deslocamento residual
  de ~90–105 m em relação à malha de 2010; as hipóteses estão medidas em
  `estudos/A03_censo/reconhecimento.md` § 3.2, **sem decisão**. **7 das 127 geometrias
  são inválidas**;
- a malha rural (`rs_setores_censitarios.zip`, 44 códigos em Bagé) vem **sem CRS
  declarado**, em graus; 6 dos seus polígonos são envoltórias de faixas de setores
  urbanos (ex.: `…001-0114`), e não setores;
- o CRS tem de ser decidido e registrado **antes** de qualquer medição métrica;
- as tabelas de 2000 (XLS BIFF8) **foram lidas** em 2026-09-22 com `xlrd`
  (`requirements.txt`); 127 setores urbanos + 38 rurais = 165, exatamente as linhas da
  tabela.

## 4. Comparabilidade 2010 → 2022: o geocódigo não é identificador estável

Só **141 dos 199 setores de 2022 (70,9 %)** têm correspondência **1:1** com 2010.
**21 setores de 2010 foram divididos**, chegando a **6 destinos**.

> **O geocódigo de setor NÃO é identificador estável entre censos.** Qualquer série
> temporal por setor tem de passar pelo de/para do IBGE —
> `data/raw/tabular/ibge/censo_2022/doc/Historico_formacao_Setores_Censitarios_2010_2022.xlsx`
> — ou usar um recorte estável (bairros, município).

O próprio IBGE publica a ressalva em
`data/raw/tabular/ibge/censo_2022/doc/Leia_me_Comparabilidade_2010_2022.pdf`.

Juntar 2010 com 2022 por igualdade de geocódigo **não gera erro**: gera número plausível
e falso, porque parte dos códigos casa por coincidência de recorte parcial.

## 5. Bagé não tem bairros na divulgação do Censo 2022

Medido nos 199 setores de Bagé por `CD_MUN`, `NM_MUN` e `NM_BAIRRO`: **Bagé não tem
bairro na divulgação do IBGE de 2022**. Dos 497 municípios do RS, 162 têm; Bagé não é
um deles, e os 199 setores têm `NM_BAIRRO` vazio.

**Controle negativo:** a mesma medição em **Porto Alegre** devolve **99 bairros** — ou
seja, a contagem zero em Bagé é ausência real na fonte, não filtro quebrado.

Consequência: `data/raw/vetor/ibge/censo_2022/malha_com_atributos/RS_bairros_CD2022.gpkg` está guardado pelo
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

## Corrigido em 2026-09-22

Texto anterior dos §§ 1 a 3, mantido como registro. Foi substituído porque comparava
moradores em domicílios particulares permanentes com população total (diferenças de
−476 em 2010 e −874 em 2000, que desaparecem quando se compara a mesma grandeza), não
considerava a transferência de 11 setores de 2000 para Aceguá e deixava em aberto o
efeito dos 4 setores de 2010 sem linha. Medição que motivou a correção:
`estudos/A03_censo/reconhecimento.md` § 2.

<details>
<summary>Texto anterior (até 2026-09-22)</summary>

> ## 1. A soma dos setores fecha em 2022, e não fecha em 2010
>
> | censo | soma dos setores | total oficial do município | diferença | serve como total municipal? |
> | --- | ---: | ---: | ---: | --- |
> | 2022 | **117.938** | 117.938 | **0** | **sim** |
> | 2010 | 116.318 (`V002`) | 116.794 | **−476** (−0,408 %) | **não** |
> | 2000 | 117.893 (`Var12`) | 118.767 | −874 | não, mas por outro motivo (§ 4) |
>
> Em 2022 a soma dos **199 setores** de Bagé fecha **exatamente** com o total oficial
> (urbana 114.883 + rural 3.055). A tabela e a malha têm os mesmos 199 códigos:
> 0 só na tabela, 0 só na malha.
>
> ## 2. 2010: quatro setores sem linha na tabela — causa em aberto
>
> A malha de 2010 tem **168 setores** em Bagé; a tabela de agregados tem **164**.
> **Quatro setores existem na malha e não têm linha na tabela** — três sedes de distrito
> e um rural — e **não aparecem em nenhuma das 26 planilhas** do pacote.
>
> A causa **não foi determinada**; fica declarada em aberto. A consequência é operacional
> e não depende de descobrir a causa:
>
> > **A soma dos setores de 2010 NÃO serve como total municipal.** Para o total de 2010,
> > usar a tabela oficial por município (`2010/tabelas/rio_grande_do_sul.zip`), não a soma.
>
> ## 3. 2000: a diferença é de recorte, não erro
>
> `Var12` (moradores em domicílios particulares permanentes) soma **117.893** contra
> **118.767** oficiais, −874. **Não é erro de soma nem de junção:** as duas quantidades
> medem coisas diferentes — o total oficial inclui **domicílios improvisados e coletivos**,
> que `Var12` por definição não conta. Comparar as duas como se fossem a mesma grandeza
> produz uma discrepância que não existe.
>
> Ressalva adicional de 2000, do lado espacial:
>
> - a malha urbana de Bagé (`2000/malha/4301602.zip`, 127 setores) vem declarada em
>   **EPSG:32621 — UTM 21 NORTE**, hemisfério errado para Bagé: é erro de declaração no
>   `.prj`, não dado do sul projetado. **7 das 127 geometrias são inválidas**;
> - a malha rural (`rs_setores_censitarios.zip`, 47 setores em Bagé) vem **sem CRS declarado**;
> - o CRS tem de ser decidido e registrado **antes** de qualquer medição métrica;
> - as **tabelas de 2000 não foram lidas** no REVIA_BG: vêm só em `.XLS` legado (BIFF8) e
>   aquele ambiente não tinha leitor. Os arquivos estão guardados intactos; falta o leitor.
>

</details>

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

Os arquivos chegaram primeiro por **cópia** de
`~/projetos/rede_viaria_bage/dados/externos/censo/` (projeto REVIA_BG), que os baixou das
fontes oficiais do IBGE em 20/09/2026 navegando as listagens do FTP — nenhuma URL montada
por adivinhação. A cópia foi conferida arquivo a arquivo (sha256 origem = sha256 cópia) e
a origem saiu inalterada.

Em 22/09/2026 os 50 arquivos de dado foram movidos (sha256 conferido antes e depois) para
`data/raw/tabular/ibge/censo_<ano>/` (tabelas; documentação em `doc/`) e
`data/raw/vetor/ibge/censo_<ano>/` (malhas; `malha_com_atributos/` e `cnefe/` em 2022).
A malha territorial de setores 2022 do geoftp, que também veio na cópia, é hoje obtida por
`scripts/download/baixar_malhas_ibge.py`. Cada arquivo tem `.json` irmão com URL exata,
`Last-Modified` do servidor, data do download original e sha256; a lista fixa está em
`config/fontes_censo_ibge.yaml`, e `scripts/download/baixar_censo_ibge.py --verificar`
confere a origem sem baixar.

O registro da cópia original — `.json` irmãos antigos (com `origem_da_copia`),
`manifesto_copia_censo.json`, `FONTE.md` e `manifesto_censo_<ano>.json` do REVIA_BG — está,
sem edição, em `docs/procedencia/revia_bg_censo/`.

Script: `scripts/download/baixar_censo_ibge.py` (substitui `scripts/download/censo_revia_bg.py`).
