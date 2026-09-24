"""
A03 — paleta das figuras do estudo (ponto único; s1_figuras.py e
s2_agrupamentos.py importam daqui).

Convenção de sentido, igual em todas as figuras: AZUL = ganho, LARANJA = perda,
CINZA = sem mudança. As classes da subordinada 1 seguem o mesmo eixo
ganho–perda (decisão do responsável, 2026-09-23):

    nova       azul escuro      adensada   azul claro
    estável    cinza neutro
    esvaziada  laranja claro    extinta    laranja escuro

As rampas são uma só para classes e variação: AZUL e LARANJA, 4 degraus cada,
do claro ao escuro, com a MESMA luminosidade OKLCH por degrau nos dois braços
(L 0,70 / 0,62 / 0,53 / 0,44; matiz 256° e 48°), para que nenhum lado pese mais.

Validação (validate_palette.js do skill de visualização, superfície #fcfcfb):
- classes, todos os pares (mapa): separação CVD pior par 13,0 (deutan,
  esvaziada × estável); visão normal pior par 16,1 — passam. O cinza "falha"
  faixa de luminosidade e croma por construção (é neutro, não é série).
- cada rampa (--ordinal): monotônica, ΔL ≥ 0,06, degrau claro ≥ 2:1 — passam.
- contraste < 3:1 nos degraus claros (2,6 e 2,7:1) e no cinza: aviso. O alívio
  exigido está nas figuras (legenda com rótulo e contagem) e nas tabelas de
  resultados_s1.md.

DESTAQUE é outro papel (subordinada 2: ganhou domicílio e perdeu moradores) e
não entra no eixo ganho–perda; nunca aparece junto das rampas.
"""

SUPERFICIE = "#fcfcfb"

AZUL = ["#63a0f1", "#3c86e4", "#226ac3", "#0e509d"]       # ganho, claro -> escuro
LARANJA = ["#e1824e", "#d06217", "#ac4b00", "#853900"]    # perda, claro -> escuro
CINZA_ESTAVEL = "#bdbcb6"                                  # classe "estável"
CINZA_ZERO = "#dddcd7"                                     # variação zero (meio da divergente)

CORES_CLASSE = {"nova": AZUL[-1], "adensada": AZUL[0], "estavel": CINZA_ESTAVEL,
                "esvaziada": LARANJA[0], "extinta": LARANJA[-1]}

# divergente: laranja (perda, escuro -> claro) | zero | azul (ganho, claro -> escuro)
DIVERGENTE = LARANJA[::-1] + [CINZA_ZERO] + AZUL

COR_DIVERGENCIA = "#9e2626"      # destaque (subordinada 2); validado contra a superfície
COR_OUTRA_DIV = "#ec7a6a"        # demais unidades da divergência, nos detalhes
COR_CONTEXTO = "#e4e3de"
