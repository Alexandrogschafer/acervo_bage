# A03 — Submissão à RA'E GA

**Periódico alvo:** RA'E GA — O Espaço Geográfico em Análise (UFPR), ISSN 2177-2738
(eletrônico). **Idioma de submissão:** português. **Decisão do responsável:** 2026-09-24
(registrada em [`manifesto.yaml`](manifesto.yaml), bloco `publicacao`).

Normas lidas em **2026-09-24** nas páginas da revista:

- Diretrizes e condições de submissão: <https://revistas.ufpr.br/raega/about/submissions>
- Sobre, foco e escopo, periodicidade: <https://revistas.ufpr.br/raega/about>
- Modelo de diagramação (último commit no repositório: 2022-11-16):
  <https://github.com/revistaraega/templates/blob/main/template.docx>
- Vídeo sobre a diagramação: <https://youtu.be/KPHBI3QLQF8> (não assistido)

As normas mudam. **Reler as duas páginas e baixar o modelo de novo antes de submeter.**
Onde a página e o modelo divergem, está marcado abaixo; nesse caso vale a página de
diretrizes, que é a que a revista usa para devolver a submissão.

---

## 1. Escopo: o ponto que mais pesa para o A03

A revista declara que **não** entram "inventários, relatórios técnicos ou acadêmicos de
abrangência local, que não acrescentem inovação ao conhecimento científico correlato a
análise espacial". A análise de escopo, feita pelos editores em até 60 dias, devolve
artigo que aplica método consagrado e "concentra os resultados na caracterização da
área de estudo".

Artigo de abrangência local entra quando permite "a identificação de incongruências
metodológicas, divergências em relação ao conhecimento científico posto ou esperado".
A revista também verifica se o método "possibilita a validação dos resultados e a
replicação da pesquisa".

**Consequência para o A03:** o eixo do texto são os **quatro achados metodológicos**
do `manifesto.yaml` (`metodo_previsto`): o falso êxodo rural pelo rótulo de situação,
a troca de resolução da grade, a grade de 2010 híbrida e o posicionamento pela face de
logradouro. Eles valem para qualquer município e são o que tira o artigo da categoria
de "caracterização de Bagé". Os números de Bagé entram como a aplicação que os mede.

## 2. Formato do manuscrito

| item | exigência |
| --- | --- |
| arquivo | DOC ou DOCX |
| tamanho | **no máximo 20 páginas** no modelo da revista e **no máximo 10 MB** ("casos excepcionais poderão ser justificados") |
| diagramação | pode ser submetido com ou sem; **se aceito**, tem de ser diagramado no modelo, por conta dos autores |
| linguagem | impessoal, 3ª pessoa; texto inédito |
| anonimato | autores **não** identificáveis no corpo do texto, nas figuras, nos gráficos e nos mapas |
| título | em português e em inglês |
| resumo e abstract | **200 a 250 palavras** cada, com objetivo e conclusão (o modelo pede, sem rótulos: introdução, objetivo, materiais e métodos, resultados e discussões, conclusões) |
| palavras-chave | **3 a 5**, que **não** estejam no título. Separador: página diz **ponto e vírgula**; o modelo diz vírgulas. Usar ponto e vírgula |
| seções obrigatórias | introdução, materiais e métodos, resultados e discussão, **conclusão**, referências. O modelo marca a conclusão como "não obrigatória"; a página diz que todas são obrigatórias. Incluir |
| papel e margens (modelo) | Carta (216 × 279 mm); margens superior e inferior de 1,78 cm, laterais de 1,27 cm; cabeçalho e rodapé a 0,79 cm |
| fonte (modelo) | Calibri; título em 22 pt negrito; títulos de seção em 14 pt negrito versalete |
| números (modelo) | milhar sem ponto: `25000` ou `25 000`, nunca `25.000`; seguir o SI |

**Limite de palavras:** a revista não fixa limite de palavras para o corpo do texto.
O limite é de **20 páginas diagramadas**. O único limite em palavras é o do resumo e do
abstract.

## 3. Figuras, quadros e tabelas

| item | exigência (do modelo) |
| --- | --- |
| número de figuras | **sem limite declarado**. O limite prático é o das 20 páginas |
| resolução | **300 dpi** |
| tamanho máximo | **20 cm de altura × 18 cm de largura** |
| texto dentro da figura | nada abaixo de **Calibri 8** ou equivalente (vale para rótulos de mapa e fluxograma) |
| posição | figura **alinhada com o texto**, não flutuante |
| legenda | "Figura N – título. (fonte/autoria)", inserida pela legenda do Word, citada no texto por referência cruzada |
| quadros e tabelas | normas da **ABNT** e do **IBGE** (Normas de apresentação tabular, 1993); nota, fonte e autoria abaixo; comentados no texto |
| anonimato | nada nas figuras e nos mapas que identifique a autoria |

**Para as figuras do A03** (`scripts/s1_figuras.py`, `s3_figuras.py`): conferir largura
de até 18 cm a 300 dpi (até 2126 px), rótulos de pelo menos 8 pt no tamanho final e
retirar dos mapas qualquer crédito com nome de autor.

## 4. Citação e referências

- **Citação e referências pela ABNT.** O modelo sugere o estilo "Universidade Federal do
  Paraná – ABNT" do Mendeley, com citação autor-data: `(SAMPAIO, 2019)` e
  `Sampaio (2019)`.
- **No mínimo 80 % das referências** devem ser artigos publicados **em periódicos**. É
  uma das declarações da lista de conferência da submissão.
- **Situação no acervo:** `bibliografia/bage.bib` ainda é um exemplo de uma entrada, e
  `referencias_bib` do manifesto está vazio. A regra dos 80 % pesa aqui, porque as
  fontes naturais do A03 são publicações do IBGE (notas metodológicas da grade,
  censos), e elas **não** contam como periódico. O trabalho de bibliografia precisa
  buscar artigos em periódico para a discussão.

## 5. Dados abertos e declaração de disponibilidade

- **Nada encontrado.** As páginas de diretrizes e "Sobre" **não** exigem dados abertos,
  depósito em repositório, declaração de disponibilidade de dados nem ORCID. Também
  não citam preprint.
- A exigência que chega mais perto é a da análise de escopo: o método tem de permitir
  "a validação dos resultados e a replicação da pesquisa".
- **Decisão pendente do responsável (não é norma da revista):** incluir ou não uma
  declaração de disponibilidade apontando para este repositório.
  - A favor: ela sustenta a replicação.
  - Contra, durante a avaliação: o repositório é público e identifica a autoria. Isso
    fere o anonimato exigido. Se a declaração entrar, na submissão ela tem de ir sem o
    link, que só é incluído na versão aceita.
  - Em qualquer caso, a declaração só pode apontar para o que tem `pode_publicar=true`.
    A fonte não redistribuível das camadas de interpretação (i01, i02) fica de fora.

## 6. Documentos e declarações na submissão

| documento | exigência |
| --- | --- |
| cadastro | login no sistema da revista (SER/OJS) |
| aprovação do CEP | só para pesquisa com seres humanos. **Não se aplica ao A03** (dado agregado do censo) |
| lista de revisores sugeridos | PDF com **1 a 3 nomes**. Cada nome sem publicação conjunta com os autores nos últimos 3 anos, com trabalho na área, com pelo menos 1 artigo nos três estratos superiores do Qualis nos últimos 3 anos e cadastrado no SER |
| declarações da lista de conferência | ≥ 80 % de referências em periódico; ciência da tradução e diagramação por conta dos autores se aceito; **compromisso do primeiro autor de atuar como avaliador** da revista se o artigo for aprovado |
| declaração de direito autoral | artigo inédito, original e não submetido a outra revista; ciência da Lei 9.610/98 e responsabilidade por plágio; coautores cientes e sem remuneração; autorização prévia de publicação |

## 7. Depois do aceite

- **Publicação bilíngue obrigatória:** todo artigo aceito sai em português (ou espanhol)
  **e em inglês**.
- **A tradução e a diagramação são por conta dos autores.** Podem ser feitas por
  empresa especializada, por professor de Letras–Inglês com tradução comprovada, ou
  por pessoas credenciadas que a revista lista na página de diretrizes. Quem não usar
  o credenciado envia um termo de comprovação de capacitação.
- Envio da versão diagramada em português e em inglês.
- Etapas: revisão ortográfica, leitura crítica, prova dos autores e publicação. Nas três
  primeiras podem ser pedidas alterações. Os editores decidem sobre a publicação.

## 8. Prazos, taxas, licença e periodicidade

| item | situação |
| --- | --- |
| taxa de submissão ou de publicação (APC) | **nenhuma**: "não são cobradas taxas ou encargos aos autores" |
| custo real para o autor | **tradução para o inglês e diagramação**, obrigatórias após o aceite |
| fluxo | submissão **contínua**. Há volumes especiais com chamada própria; a chamada aberta em 2026-09 é sobre pesca artesanal e não se aplica |
| prazos da revista | análises de escopo, de normas e de plágio em **até 60 dias** (sem aviso nesse prazo, o artigo seguiu para a avaliação cega); primeira decisão em **cerca de 40 dias** em média (submissões de 2025) |
| avaliação | por pares, cega |
| periodicidade | quadrimestral |
| acesso | aberto e gratuito |
| licença de publicação | **não declarada** nas páginas lidas (não aparece Creative Commons). Conferir no artigo publicado mais recente antes de submeter, por causa da regra do acervo: nenhuma saída mais permissiva que a fonte dela |
| classificação | Qualis A1 (2017–2020 e 2021–2024), segundo a própria revista; indexada no Scopus |

## 9. Pendências para chegar à submissão

1. **Bibliografia:** atingir os 80 % em periódico (§ 4). Revisão preparada em
   2026-09-25: [`revisao_a03.md`](revisao_a03.md), com as entradas conferidas em
   [`bibliografia_a03.bib`](bibliografia_a03.bib) para importar no Zotero. O núcleo
   final dá **81,8 %** (36 periódicos contra 8 outros), com as 4 referências de reserva
   incluídas por decisão do responsável em 2026-09-25. Absorve 1 citação nova que
   não seja de periódico (§ 5).
2. **Tamanho:** caber em 20 páginas diagramadas, com os quatro achados de método e as
   três subordinadas. É provável que seja preciso escolher figuras.
3. **Figuras:** refazer no padrão de 18 × 20 cm, 300 dpi e texto de 8 pt ou mais (§ 3).
4. **Anonimato:** tirar o nome do repositório, do acervo e dos autores do texto e dos
   mapas da versão submetida (§ 5).
5. **Revisores sugeridos:** lista de 1 a 3 nomes (§ 6).
6. **Tradução para o inglês:** orçar antes de submeter, porque é custo certo se o
   artigo for aceito (§ 7).
