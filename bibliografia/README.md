# Bibliografia do acervo de Bagé

## Como o `bage.bib` é produzido

O arquivo `bage.bib` **não é escrito à mão**. Ele é a exportação automática
de uma coleção do Zotero:

1. No Zotero, a coleção chama-se **`Bagé`** (subcoleções são exportadas junto).
2. O plugin **Better BibTeX** mantém a exportação sincronizada:
   clique direito na coleção → *Export Collection…* → formato
   **Better BibTeX**, marcando **`Keep updated`**.
3. Destino da exportação: `bibliografia/bage.bib` **deste repositório**.

Com `Keep updated` ligado, toda alteração na coleção reescreve o `.bib`
sozinha. Por isso a regra (vii) do [`CLAUDE.md`](../CLAUDE.md): **editar o
`.bib` à mão é perder o trabalho no próximo salvamento do Zotero** — a
correção tem que ser feita no item do Zotero.

### Chaves de citação

As chaves (`silva2021geobage`, etc.) vêm do *citation key format* do Better
BibTeX e são o identificador usado em `data/catalogo_camadas.csv`
(coluna `referencias_bibliograficas`). Para que uma chave não mude sozinha e
quebre o catálogo, fixe-a no Zotero (*Pin BibTeX key*) antes de referenciá-la.
`scripts/utils/validar_catalogos.py` falha se o catálogo citar uma chave que
não existe no `.bib`.

## PDFs

Os PDFs ficam **no Zotero**, na biblioteca do pesquisador — **nunca no git**.

- `bibliografia/pdfs/` existe só como ponto de montagem local e está inteiro
  no `.gitignore`.
- Motivo: o repositório é público e a maior parte dos PDFs é material
  protegido por direito autoral; publicá-los aqui seria redistribuição.
- O rastro público é o `.bib` (metadados + DOI/URL), que é o suficiente para
  qualquer pessoa localizar a obra na fonte original.

## Índice legível

`bibliografia/indice.md` é gerado a partir do `.bib`:

```bash
python scripts/bibliografia/gerar_indice.py
```

Traz uma tabela com chave, autores, ano, título, veículo, tema, DOI/URL e as
camadas do geoportal ligadas àquela referência (lidas de
`data/catalogo_camadas.csv`), mais a data de geração e o **sha256 do `.bib`**
que originou o índice — assim dá para saber, olhando só o índice, se ele está
defasado em relação ao `.bib` atual.

Como é arquivo gerado, `indice.md` também não deve ser editado à mão.

## Estado atual

O `bage.bib` deste commit é um **exemplo mínimo de uma entrada**, criado só
para o pipeline ter o que validar. Ele será substituído integralmente pela
primeira exportação do Zotero.
