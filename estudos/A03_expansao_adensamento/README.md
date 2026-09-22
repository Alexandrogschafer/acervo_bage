# A03 — Expansão e adensamento

**Status:** planejado · **Manifesto:** [`manifesto.yaml`](manifesto.yaml)

Dinâmica domiciliar de Bagé/RS entre 2010 e 2022: o descompasso entre população
estável e crescimento de domicílios, onde ele se materializou no território e com
que infraestrutura urbana. O dado bruto está em `data/raw/tabular/ibge/censo_<ano>/`
e `data/raw/vetor/ibge/censo_<ano>/` (obtido por
`scripts/download/baixar_censo_ibge.py`); `data/acervo/censo/` fica para as camadas
curadas do censo.

*O diretório se chamava `A03_censo` até 2026-09-22, quando a pergunta foi fechada. O
id do artigo continua **ACERVO_BAGE-A03**.*

## Pergunta

> Bagé ganhou 6.791 domicílios ocupados (+17,6 %) com a população praticamente estável
> (+1,0 %) entre 2010 e 2022. **Onde**, no território do município, esse crescimento de
> domicílios se materializou — em ocupação de área nova ou em adensamento da área já
> ocupada —, e **que infraestrutura urbana** existe em 2022 nas áreas que cresceram,
> comparada à do restante da cidade?

Três subordinadas, decididas pelo responsável em 2026-09-22 e escritas na íntegra no
[`manifesto.yaml`](manifesto.yaml):

1. Quanto do crescimento é **expansão** e quanto é **adensamento**?
2. **Onde domicílio e população andam em direções opostas?**
3. A **infraestrutura do entorno** acompanha onde a cidade cresceu?

## Recorte espacial (decidido)

- **Grade estatística** para a mudança 2010 → 2022: única geografia fixa entre os dois
  censos, com a coincidência das células conferida.
- **Setor censitário de 2022** para o entorno: único recorte em que ele existe.
- **Junção célula → setor**, com a incerteza da atribuição medida e declarada.
- **Área mínima comum** só se surgir necessidade de atributo do censo em série.
- **Urbano e rural definidos geograficamente** (área urbanizada ou a própria grade),
  nunca pelo rótulo de situação do setor — a reclassificação de 13 setores rurais de
  2010 em urbanos de 2022 entra como **seção de método** do artigo.

## Os dois documentos

**[`reconhecimento.md`](reconhecimento.md)** — o que os dados de 2000, 2010, 2022 e do
CNEFE permitem medir, o que não permitem e com que ressalvas (variáveis por censo,
totais, geografia entre censos, sigilo, comparabilidade do entorno, CNEFE × setores).

**[`dimensionamento.md`](dimensionamento.md)** — a medição que fechou a pergunta:
população +0,98 % contra domicílios ocupados +17,64 %; Bagé comparado ao RS e ao
Brasil (o descompasso é o padrão do estado, não anomalia local); a redistribuição na
grade (14.170 domicílios de ganho bruto contra 6.695 de perda; 573 células novas); e
os 10 itens do entorno de 2022 com a dispersão entre setores.

Os scripts que reproduzem cada número estão em [`scripts/`](scripts/) — `r00`–`r08`
para o reconhecimento, `d01`–`d04` para o dimensionamento.

**Antes de usar qualquer número, ler [`docs/ressalvas_censo_bage.md`](../../docs/ressalvas_censo_bage.md)**:
a soma dos setores fecha em 2022 e não fecha em 2010; a malha de 2000 vem com
CRS declarado errado; o geocódigo de setor não é estável entre censos.

## Como este estudo se relaciona com o acervo

Este estudo **lê** o acervo e **nunca escreve nele**. As camadas que consome
são declaradas em `manifesto.yaml`, com versão e sha256 fixados — é o
contrato que diz sobre qual estado do acervo os resultados foram produzidos. O
dado bruto do IBGE, que não é camada do acervo, é fixado no bloco
`fontes_brutas:` do mesmo manifesto.

- `scripts/`    — código próprio do estudo
- `derivados/`  — intermediários (fora do git; só os `.json` irmãos entram)
- `saidas/`     — resultados (fora do git; só os `.json` irmãos entram)

Se uma camada derivada aqui tiver valor para os demais estudos, ela entra no
acervo por **promoção**: conferência visual do responsável, depois cópia para
`data/acervo/<tema>/` com linha em `data/catalogo_camadas.csv`. Nunca por
escrita direta.

A publicação de qualquer saída herda a restrição **mais restritiva** entre as
camadas declaradas no manifesto (`scripts/utils/publicacao.py`). Hoje a saída
deste estudo é **não publicável**: `setores_2022` está com `pode_publicar=false`
no catálogo, à espera de conferência.
