# Pedido ao IBGE: variável de abordagem por célula da Grade Estatística 2010

> **PRONTO PARA ENVIO — NÃO ENVIADO.** Redigido em 2026-09-23 e completado no mesmo dia
> com o remetente indicado pelo responsável.
> - **O e-mail de contato não está neste arquivo**, porque o repositório é público.
>   Ele entra no momento do envio, pelo canal escolhido.
> - **Canal ainda não confirmado.** Em 2016, a unidade responsável pela grade era a
>   CDDI, Coordenação de Projetos Especiais (ficha técnica da metodologia de 2010). Nas
>   notas de 2022, é a CDDI, Coordenação de Atendimento e Informação (ficha técnica). O
>   mais provável é enviar pelo atendimento do IBGE, endereçado à CDDI. Nenhum endereço
>   de e-mail do IBGE foi conferido.
> - **Contexto:** `estudos/A03_expansao_adensamento/resultados_s1.md` §§ 10.4, 10.6 e
>   11; `docs/ressalvas_censo_bage.md` § 8.

---

**Para:** IBGE — Centro de Documentação e Disseminação de Informações (CDDI),
Coordenação de Projetos Especiais (ou a coordenação que hoje responde pela Grade
Estatística)
**De:** Alexandro Schafer — Universidade Federal do Pampa (UNIPAMPA), Campus Bagé
**Assunto:** Grade Estatística do Censo 2010: variável de abordagem (agregação /
desagregação / misto) por célula

Prezados,

Escrevo pela Universidade Federal do Pampa (UNIPAMPA), Campus Bagé, em nome do projeto
de pesquisa **ACERVO_BAGE**. É um acervo público de dados espaciais,
dados não espaciais e bibliografia sobre o município de Bagé (RS), com estudos
derivados sobre a dinâmica urbana.

Um desses estudos usa a Grade Estatística do IBGE para comparar o Censo 2010 com o
Censo 2022 no município de Bagé (RS), código 4301602. A pergunta é onde o crescimento
de domicílios entre os dois censos se materializou: em ocupação de área nova ou em
adensamento da área já ocupada. Os arquivos são os quadrantes `grade_id14` e
`grade_id04`, obtidos em
`https://geoftp.ibge.gov.br/recortes_para_fins_estatisticos/grade_estatistica/`.

A publicação *Grade Estatística* (IBGE, 2016), que documenta a versão de 2010, informa
na p. 21:

> "Além dos dados relacionados com o censo de população e habitação, foi incluída uma
> variável para explicitar a abordagem utilizada para a obtenção dos dados em cada
> célula: agregação, desagregação ou misto (agregação e desagregação). O objetivo desta
> variável é permitir que o usuário tome conhecimento das diferenças relacionadas com as
> incertezas que estão envolvidas na geração dos dados agregados na grade estatística."

Os arquivos distribuídos no geoftp para 2010 não trazem essa variável. Os campos são
`ID_UNICO`, `nome_1KM`, `nome_5KM`, `nome_10KM`, `nome_50KM`, `nome_100KM`,
`nome_500KM`, `QUADRANTE`, `MASC`, `FEM`, `POP`, `DOM_OCU`, `Shape_Leng` e `Shape_Area`.
A listagem do diretório `censo_2010/` também não tem outro arquivo com ela.

A variável é necessária para a comparação com 2022. As *Notas metodológicas 01/2025*
indicam que a grade de 2022 foi obtida por totalização direta das coordenadas dos
endereços. Sem a variável de 2010, não é possível separar as células de 2010 que foram
desagregadas a partir do setor censitário, e a diferença entre as edições mistura dado
modelado com dado observado. Também não é possível reconstruir a regra do
limite de 50 % (p. 17–18), porque a "ausência de localização" por setor não é
publicada.

Solicitamos, se possível:

1. **A variável de abordagem por célula da Grade Estatística 2010** (agregação,
   desagregação ou misto), ao menos para os quadrantes ID_14 e ID_04, ou para as
   células do município de Bagé. Pode vir como tabela de `ID_UNICO` e abordagem.
2. Se houver, **a técnica de desagregação** usada por setor ou por célula: dasimétrico
   com vias, dasimétrico com uso e cobertura, ou ponderação zonal (p. 18–21).
3. Se puder ser divulgada, **a "ausência de localização" relativa por setor censitário
   de 2010** (p. 17), ou ao menos a indicação de quais setores de Bagé ficaram acima do
   limite de 50 %.

**Finalidade.** Os dados serão usados exclusivamente em pesquisa acadêmica, no
projeto ACERVO_BAGE da UNIPAMPA, Campus Bagé.
- O IBGE será citado como fonte.
- A divulgação será sempre agregada, na própria célula da grade ou em recortes maiores.
- Nenhum dado individual será solicitado nem divulgado.
- A variável será usada para separar, na comparação 2010 × 2022, as células
  observadas das modeladas, e para documentar isso na seção de método do trabalho.

Enquanto a variável não chega, o estudo trata à parte o único setor em que o próprio
dado mostra a marca da desagregação (o rural 430160205000136). Mas esse critério
indireto só detecta parte dos casos.

Atenciosamente,

Alexandro Schafer
Universidade Federal do Pampa (UNIPAMPA) — Campus Bagé
Projeto de pesquisa ACERVO_BAGE
[e-mail de contato — incluir no envio]

---

**Anexo interno (não enviar).** O que motivou o pedido:
- O teste indireto pela razão moradores/domicílio do setor não discrimina 2010 de 2022.
- O teste de pares idênticos contíguos acha um único setor com marca de desagregação:
  o rural `430160205000136`, com 968 domicílios de 2010 nas suas unidades e 31 das 232
  unidades "extintas" da subordinada 1.
- Detalhes em `resultados_s1.md` § 10.6.
