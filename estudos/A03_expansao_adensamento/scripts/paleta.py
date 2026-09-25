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

# Subordinada 3 (2026-09-24): coropleta do ENTORNO por setor (% de domicílios com o
# item). É magnitude, não ganho–perda: por isso um terceiro matiz, violeta (OKLCH h
# 300°), fora do eixo azul/laranja, para não colidir com as classes sobrepostas.
# 5 degraus, L 0,77 → 0,43. Validação (validate_palette.js --mode light --ordinal,
# superfície #fcfcfb): monotônica, ΔL ≥ 0,06, degrau claro 2,08:1, matiz único —
# passa. O degrau claro precisa aparecer: setor SEM entorno é desenhado à parte, em
# COR_CONTEXTO com hachura, e não pode se confundir com "perto de zero".
VIOLETA = ["#bca8e3", "#a48ad4", "#8d6cc2", "#7550ad", "#5e3594"]   # sequencial, claro -> escuro
# Ajuste da conferência (2026-09-24): o fundo dos setores sem entorno competia com o
# dado. Cinza mais claro que COR_CONTEXTO e hachura mais esparsa (em s3_figuras.py);
# segue distinto do degrau claro do violeta, que é cromático.
COR_SEM_ENTORNO = "#efeeea"

# Comparação de dois grupos de NOVAS (subordinada 3, item 3): dois tons do mesmo braço
# azul (os dois são ganho), com forma diferente e rótulo direto. Validado como par
# categórico: CVD ΔE 26,1, visão normal 26,1; contraste do claro 2,61:1 (aviso) — o
# alívio é o rótulo de valor em cada marcador.
PAR_NOVAS = {"posterior_a_2001": AZUL[-1], "vazio_interno_1938_1960": AZUL[0]}
# Hachura dos itens em que principal e sensibilidade divergem no sinal (item 3): cinza
# neutro, fora do azul dos grupos, para marcar a faixa sem disputar com os marcadores.
COR_DIVERGE = "#b3b2ac"
