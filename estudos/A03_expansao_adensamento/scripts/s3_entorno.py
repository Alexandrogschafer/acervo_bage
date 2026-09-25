"""
A03 — subordinada 3: a infraestrutura do entorno acompanha onde a cidade cresceu?

A MUDANÇA é medida na grade harmonizada (cenário adotado: setor de 2010
430160205000136 à parte); o ENTORNO só existe por setor censitário de 2022 (168
dos 199 setores). A ligação é uma junção espacial célula -> setor, e tudo depende
dela: por isso ela é medida e relatada antes dos cruzamentos.

JUNÇÃO
------
Cada unidade vai para o setor de 2022 com a MAIOR ÁREA DE INTERSEÇÃO (empate: menor
código). Operação em EPSG:31981; áreas no CRS de área (scripts/utils/medidas.py).
Incerteza medida: fração da área da unidade no setor atribuído; unidades repartidas
(2+ setores com ao menos REPARTIDA_MIN da área cada); unidades cujo setor não tem
entorno. SENSIBILIDADE: os mesmos cruzamentos só com unidades com LIMIAR_SENS ou
mais da área num único setor.

ENTORNO
-------
10 itens do entorno por domicílio de 2022 (dicionário do IBGE, como no d04): o
denominador de cada item é o próprio item (sim + não + não declarado). A unidade
recebe a proporção do setor atribuído; o grupo é a média ponderada por domicílios
de 2022 da unidade (extintas não têm domicílio em 2022: ponderadas pelos de 2010,
declarado). Referência "cidade": o município inteiro no entorno (43.744 domicílios
nos 168 setores). Cada valor vem de um setor: o número efetivo de observações é o
de SETORES distintos, relatado por grupo.

Grupos da datação (item 3): lidos de derivados/i02_evolucao_urbana_unidades.csv
(fora do git; fonte não redistribuível, só para interpretar). Saem daqui só
agregados por grupo.

LÊ a camada de trabalho (saidas/s1_celulas_2010_2022.gpkg, sha256_conteudo
conferido), a camada setores_2022 do acervo (conferida), derivados/ (entorno e
dicionário extraídos por r06; lista do i02).
ESCREVE derivados/s3_entorno.json (agregados, versionado) e
derivados/s3_unidades_setor.csv (por unidade, fora do git).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import d04_entorno as d04  # noqa: E402
import s1_expansao_adensamento as s1  # noqa: E402
import s1_extintas as ex  # noqa: E402
from scripts.utils import catalogo, medidas, metadados, paths  # noqa: E402

SAIDA = s1.DERIV / "s3_entorno.json"
LISTA = s1.DERIV / "s3_unidades_setor.csv"
I02 = s1.DERIV / "i02_evolucao_urbana_unidades.csv"
LIMIAR_SENS = 0.70
REPARTIDA_MIN = 0.01
PERMUTACOES = 9999
SEMENTE = 20260924

# item -> (categoria de leitura, sentido, papel). "sentido": +1 = mais é melhor
# servido; -1 = mais é pior (obstáculo). Papel: discrimina / controle / ausência /
# contexto (manifesto, subordinada 3; dimensionamento.md § 4).
ITENS = {
    "VIA PAVIMENTADA": ("SIM", +1, "discrimina"),
    "OBSTÁCULO NA CALÇADA": ("SIM", -1, "discrimina"),
    "ARBORIZAÇÃO": ("5 OU MAIS ÁRVORES", +1, "discrimina"),
    "BUEIRO": ("SIM", +1, "discrimina"),
    "RAMPA PARA CADEIRANTE": ("SIM", +1, "discrimina"),
    "PONTO DE ÔNIBUS": ("SIM", +1, "contexto"),
    "CALÇADA": ("SIM", +1, "contexto"),
    "CIRCULAÇÃO DA VIA": ("CAMINHÃO, ÔNIBUS", +1, "contexto"),
    "ILUMINAÇÃO PÚBLICA": ("SIM", +1, "controle (universal)"),
    "VIA SINALIZADA PARA BICICLETA": ("SIM", +1, "ausência"),
}
EXTRA = {"ARBORIZAÇÃO — sem árvores": ("ARBORIZAÇÃO", "SEM ÁRVORES")}
ROTULO_FORA = "fora do traçado mapeado até 2001"
ROTULO_BORDA = "borda sem data firme"
FIRMES_ANTIGOS = {"1938", "1960"}


# --------------------------------------------------------------------------
# entorno por setor
# --------------------------------------------------------------------------

def entorno_por_setor() -> tuple[pd.DataFrame, dict]:
    """% de domicílios com cada item, por setor, e o valor do município."""
    arquivo, dicionario = d04.UNIDADES["domicilios"]
    df = pd.read_csv(d04.B22 / arquivo, sep=";", dtype=str)
    itens, _ = d04.ler_dicionario(dicionario)
    setor = df[df.columns[0]].str.strip()
    colunas, municipio = {}, {}
    pares = {k: (k, v[0]) for k, v in ITENS.items()} | EXTRA
    for nome, (item, categoria) in pares.items():
        variaveis = list(itens[item].values())
        v = d04.num(df, variaveis)
        total = v.sum(axis=1)
        alvo = v[itens[item][categoria]]
        colunas[nome] = (100 * alvo / total).where(total > 0)
        municipio[nome] = round(100 * float(alvo.sum()) / float(total.sum()), 2)
    tabela = pd.DataFrame(colunas)
    tabela.index = setor
    tabela["dppo_entorno"] = d04.num(df, ["V05000"])["V05000"].values
    return tabela, municipio


# --------------------------------------------------------------------------
# junção célula -> setor
# --------------------------------------------------------------------------

def juncao(u: gpd.GeoDataFrame, setores: gpd.GeoDataFrame, fcu: set[str]) -> pd.DataFrame:
    area_u = medidas.areas_m2(u).set_axis(u["unidade"])
    p = gpd.overlay(u[["unidade", "geometry"]], setores[["CD_SETOR", "geometry"]],
                    how="intersection", keep_geom_type=True)
    p["m2"] = medidas.areas_m2(p).values
    p = p.groupby(["unidade", "CD_SETOR"], as_index=False)["m2"].sum()
    p["frac"] = p["m2"] / p["unidade"].map(area_u)
    maior = (p.sort_values(["unidade", "m2", "CD_SETOR"], ascending=[True, False, True])
             .drop_duplicates("unidade").set_index("unidade"))
    n_setores = p[p["frac"] >= REPARTIDA_MIN].groupby("unidade").size()
    em_fcu = p[p["CD_SETOR"].isin(fcu)].groupby("unidade")["frac"].sum()
    return pd.DataFrame({
        "setor": maior["CD_SETOR"], "frac_no_setor": maior["frac"],
        "setores_com_1pct": n_setores.reindex(area_u.index, fill_value=0),
        "frac_coberta_por_setores": (p.groupby("unidade")["m2"].sum() / area_u)
        .reindex(area_u.index, fill_value=0.0),
        "frac_em_fcu": em_fcu.reindex(area_u.index, fill_value=0.0),
    })


def incerteza(t: pd.DataFrame, peso: str) -> dict:
    com = t["tem_entorno"]
    return {
        "unidades": int(len(t)), peso: int(t[peso].sum()),
        "frac_no_setor_mediana": round(float(t["frac_no_setor"].median()), 3),
        "frac_no_setor_p10": round(float(t["frac_no_setor"].quantile(0.10)), 3),
        "frac_no_setor_ponderada_por_" + peso: round(
            float((t["frac_no_setor"] * t[peso]).sum() / t[peso].sum()), 3) if t[peso].sum() else None,
        "repartidas_2_ou_mais_setores": int((t["setores_com_1pct"] >= 2).sum()),
        "com_menos_de_70pct_num_setor": int((t["frac_no_setor"] < LIMIAR_SENS).sum()),
        f"{peso}_com_menos_de_70pct_num_setor": int(t.loc[t["frac_no_setor"] < LIMIAR_SENS, peso].sum()),
        "em_setor_sem_entorno": int((~com).sum()),
        f"{peso}_em_setor_sem_entorno": int(t.loc[~com, peso].sum()),
        "setores_distintos": int(t["setor"].nunique()),
        "setores_distintos_com_entorno": int(t.loc[com, "setor"].nunique()),
    }


# --------------------------------------------------------------------------
# entorno por grupo
# --------------------------------------------------------------------------

def perfil(t: pd.DataFrame, peso: str, municipio: dict) -> dict:
    """Proporção ponderada por `peso` de cada item, só nas unidades com entorno."""
    c = t[t["tem_entorno"] & (t[peso] > 0)]
    out = {"unidades_com_entorno": int(len(c)), f"{peso}_com_entorno": int(c[peso].sum()),
           "setores_distintos": int(c["setor"].nunique()), "itens": {}}
    if not len(c):
        return out
    por_setor = c.groupby("setor")[peso].sum().sort_values(ascending=False)
    out["peso_no_maior_setor_pct"] = round(100 * float(por_setor.iloc[0] / por_setor.sum()), 1)
    out["peso_nos_3_maiores_setores_pct"] = round(
        100 * float(por_setor.iloc[:3].sum() / por_setor.sum()), 1)
    for nome in [*ITENS, *EXTRA]:
        v = float((c[nome] * c[peso]).sum() / c[peso].sum())
        # tirando um setor de cada vez: quanto o valor do grupo depende de um só setor
        jk = [float((x[nome] * x[peso]).sum() / x[peso].sum())
              for s in por_setor.index if len(x := c[c["setor"] != s]) and x[peso].sum()]
        out["itens"][nome] = {"pct": round(v, 1),
                              "dif_pp_cidade": round(v - municipio[nome], 1),
                              "sem_um_setor_min_max": [round(min(jk), 1), round(max(jk), 1)]
                              if jk else None}
    return out


def permutacao(a: pd.DataFrame, b: pd.DataFrame, peso: str) -> dict:
    """Diferença ponderada A − B por item e p bicaudal por permutação dos rótulos
    entre as unidades. As unidades de um mesmo setor não são independentes: o p
    é otimista, e a leitura se apoia na diferença e no número de setores."""
    rng = np.random.default_rng(SEMENTE)
    juntos = pd.concat([a.assign(_g=1), b.assign(_g=0)])
    w = juntos[peso].to_numpy(float)
    g = juntos["_g"].to_numpy()
    out = {}
    for nome in [*ITENS, *EXTRA]:
        x = juntos[nome].to_numpy(float)

        def dif(rot):
            wa, wb = w * (rot == 1), w * (rot == 0)
            return (x * wa).sum() / wa.sum() - (x * wb).sum() / wb.sum()
        obs = dif(g)
        perm = np.array([dif(rng.permutation(g)) for _ in range(PERMUTACOES)])
        p = (1 + (np.abs(perm) >= abs(obs) - 1e-12).sum()) / (PERMUTACOES + 1)
        # tirando um setor de cada vez (de qualquer dos dois grupos)
        jk = []
        for s in juntos["setor"].unique():
            m = (juntos["setor"] != s).to_numpy()
            if (g[m] == 1).any() and (g[m] == 0).any():
                wa, wb = w * m * (g == 1), w * m * (g == 0)
                jk.append((x * wa).sum() / wa.sum() - (x * wb).sum() / wb.sum())
        out[nome] = {"dif_pp": round(float(obs), 1), "p_permutacao": round(float(p), 4),
                     "sem_um_setor_min_max": [round(float(min(jk)), 1), round(float(max(jk)), 1)],
                     "sinal_estavel_sem_um_setor": bool(min(jk) > 0 or max(jk) < 0)}
    return out


def blocos(t: pd.DataFrame, municipio: dict) -> dict:
    """Perfis de todos os recortes pedidos, num conjunto de unidades `t`."""
    r = {"classes": {}, "referencia_cidade_pct": {k: v for k, v in municipio.items()
                                                  if not k.startswith("_")}}
    for classe in s1.CLASSES:
        sub = t[t["classe"] == classe]
        peso = "dom_10" if classe == "extinta" else "dom_22"
        r["classes"][classe] = {"peso": peso, **perfil(sub, peso, municipio)}
        # "resto da cidade": todas as outras unidades com entorno, pelos domicílios de 2022
        resto = perfil(t[t["classe"] != classe], "dom_22", municipio)
        r["classes"][classe]["resto_da_cidade"] = {
            "unidades_com_entorno": resto["unidades_com_entorno"],
            "dom_22_com_entorno": resto["dom_22_com_entorno"],
            "itens": {k: v["pct"] for k, v in resto["itens"].items()}}
        for k, v in r["classes"][classe]["itens"].items():
            v["dif_pp_resto"] = round(v["pct"] - resto["itens"][k]["pct"], 1)
    r["todas_as_unidades_com_domicilio_2022"] = perfil(t, "dom_22", municipio)

    # extintas urbanas por fenômeno (resultados_s1.md § 12.4): esvaziamento medido ×
    # indício de deslocamento por repartição da face (efeito de medida) × outras
    faces = json.loads((s1.DERIV / "s1_faces_2010.json").read_text(encoding="utf-8"))
    fen = faces["extintas_urbanas_por_fenomeno"]
    rotulos = {"esvaziamento_medido_face_perdeu_os_enderecos": "esvaziamento medido",
               "deslocamento_por_reparticao": "deslocamento por repartição da face",
               "outros": "outras"}
    r["extintas_urbanas_por_fenomeno"] = {}
    for chave, rotulo in rotulos.items():
        x = t[t.index.isin(fen[chave]["unidades_lista"])]
        r["extintas_urbanas_por_fenomeno"][rotulo] = {
            "unidades": int(len(x)), "dom_10": int(x["dom_10"].sum()),
            **perfil(x, "dom_10", municipio)}

    # item 3: novas urbanas de 200 m pela datação (interpretação)
    n200 = t[(t["classe"] == "nova") & (t["resolucao"] == "200 m")]
    grupos = {
        "posterior_a_2001": n200[n200["periodo"] == ROTULO_FORA],
        "vazio_interno_1938_1960": n200[n200["periodo"].isin(FIRMES_ANTIGOS)],
        "borda_sem_data_firme (à parte)": n200[n200["periodo"] == ROTULO_BORDA],
        "incrementos_1970_2001 (à parte)": n200[n200["periodo"].isin({"1970", "2001"})],
    }
    r["datacao_novas_200m"] = {
        k: {"unidades": int(len(x)), "dom_22": int(x["dom_22"].sum()),
            **perfil(x, "dom_22", municipio)} for k, x in grupos.items()}
    a = grupos["posterior_a_2001"]
    b = grupos["vazio_interno_1938_1960"]
    a, b = a[a["tem_entorno"]], b[b["tem_entorno"]]
    r["datacao_novas_200m"]["diferenca_posterior_menos_vazio"] = permutacao(a, b, "dom_22")
    r["datacao_novas_200m"]["setores_em_comum"] = int(len(set(a["setor"]) & set(b["setor"])))

    # item 4: área urbanizada (dentro/fora) e favelas e comunidades urbanas
    au = {}
    for classe in s1.CLASSES:
        peso = "dom_10" if classe == "extinta" else "dom_22"
        sub = t[t["classe"] == classe]
        for lado, x in (("dentro_da_AU", sub[sub["dentro_au"]]),
                        ("fora_da_AU", sub[~sub["dentro_au"]])):
            au[f"{classe} | {lado}"] = {"unidades": int(len(x)), peso: int(x[peso].sum()),
                                        **perfil(x, peso, municipio)}
    grupo_pos = grupos["posterior_a_2001"]
    for lado, x in (("dentro_da_AU", grupo_pos[grupo_pos["dentro_au"]]),
                    ("fora_da_AU", grupo_pos[~grupo_pos["dentro_au"]])):
        au[f"novas 200 m posteriores a 2001 | {lado}"] = {
            "unidades": int(len(x)), "dom_22": int(x["dom_22"].sum()),
            **perfil(x, "dom_22", municipio)}
    r["area_urbanizada"] = au
    fcu = t[t["fcu"]]
    toca = t[t["frac_em_fcu"] >= REPARTIDA_MIN]
    setores_fcu = municipio["_setores_fcu"]
    com = {s: v for s, v in setores_fcu.items() if v["VIA PAVIMENTADA"] is not None}
    r["favelas_comunidades_urbanas"] = {
        "setores_fcu": len(setores_fcu), "setores_fcu_com_entorno": len(com),
        "entorno_dos_setores_fcu_media_simples": {
            k: round(float(np.mean([v[k] for v in com.values()])), 1) for k in [*ITENS, *EXTRA]},
        "entorno_por_setor_fcu": setores_fcu,
        "unidades_com_1pct_ou_mais_em_setor_de_FCU": {
            c: {"unidades": int((toca["classe"] == c).sum()),
                "dom_22_na_fracao_fcu": round(float((toca.loc[toca["classe"] == c, "dom_22"]
                                                    * toca.loc[toca["classe"] == c, "frac_em_fcu"]).sum()), 0)}
            for c in s1.CLASSES},
        "unidades_atribuidas_a_setor_de_FCU": int(len(fcu)),
        "por_classe": {c: {"unidades": int((fcu["classe"] == c).sum()),
                           "dom_10": int(fcu.loc[fcu["classe"] == c, "dom_10"].sum()),
                           "dom_22": int(fcu.loc[fcu["classe"] == c, "dom_22"].sum())}
                       for c in s1.CLASSES},
        "novas_200m_por_datacao_com_1pct_em_FCU": {
            k: int((x["frac_em_fcu"] >= REPARTIDA_MIN).sum()) for k, x in grupos.items()},
    }
    return r


# --------------------------------------------------------------------------

def main() -> None:
    entorno, municipio = entorno_por_setor()
    camada = ex.ler_camada()
    u = camada[~camada[s1.CAMPO_A_PARTE]].to_crs(paths.crs_producao()).reset_index(drop=True)
    _, arq_setores = catalogo.camada_conferida("setores_2022")
    setores = gpd.read_file(arq_setores).to_crs(u.crs)

    fcu = set(setores.loc[setores["CD_FCU"].notna(), "CD_SETOR"])
    j = juncao(u, setores, fcu)
    t = u.drop(columns="geometry").set_index("unidade").join(j)
    t["tem_entorno"] = t["setor"].isin(entorno.index)
    t = t.join(entorno, on="setor")
    t["dentro_au"] = t["fracao_au"] >= s1.LIMIAR_DENTRO
    t["fcu"] = t["setor"].isin(fcu)
    municipio["_setores_fcu"] = {s: {k: (round(float(entorno.at[s, k]), 1)
                                         if s in entorno.index else None)
                                     for k in [*ITENS, *EXTRA]} for s in sorted(fcu)}
    datacao = pd.read_csv(I02, dtype=str).set_index("unidade")
    datacao = datacao[datacao["grupo"] == "s1_nova_200 m"]["periodo"]
    t["periodo"] = datacao.reindex(t.index)
    faltam = set(t[(t["classe"] == "nova") & (t["resolucao"] == "200 m")].index) - set(datacao.index)
    if faltam:
        raise SystemExit(f"PARADO — {len(faltam)} novas de 200 m sem datação no i02")

    # incerteza da junção, por classe e no total
    inc = {"criterio": "setor de 2022 com a maior área de interseção (empate: menor código); "
                       f"repartida = 2+ setores com ≥ {REPARTIDA_MIN:.0%} da área da unidade",
           "setores_2022": int(len(setores)), "setores_com_entorno": int(len(entorno)),
           "todas": incerteza(t, "dom_22"),
           "com_domicilio_2022": incerteza(t[t["dom_22"] > 0], "dom_22")}
    for classe in s1.CLASSES:
        peso = "dom_10" if classe == "extinta" else "dom_22"
        inc[classe] = incerteza(t[t["classe"] == classe], peso)
    for res in ("200 m", "1 km", "1 km (2022 em 200 m)"):
        inc[f"resolucao {res}"] = incerteza(t[t["resolucao"] == res], "dom_22")

    sens = t[t["frac_no_setor"] >= LIMIAR_SENS]
    resultado = {
        "objeto": "subordinada 3 — entorno de 2022 (por domicílio) nas classes de mudança da "
                  "grade harmonizada; cenário adotado (setor de 2010 430160205000136 à parte)",
        "camada_sha256_conteudo": metadados.ler(s1.CAMADA)["sha256_conteudo"],
        "setores_2022": catalogo.camada_conferida("setores_2022")[0]["sha256"],
        "unidades": int(len(t)),
        "juncao": inc,
        "itens": {k: {"categoria": v[0], "sentido": "mais é melhor" if v[1] > 0 else "mais é pior",
                      "papel": v[2]} for k, v in ITENS.items()}
                 | {k: {"categoria": v[1], "sentido": "mais é pior", "papel": "discrimina"}
                    for k, v in EXTRA.items()},
        "ponderacao": "domicílios de 2022 da unidade (extintas: domicílios de 2010); só unidades "
                      "cujo setor atribuído tem entorno",
        "referencia": "cidade = município inteiro no entorno por domicílio (168 setores)",
        "principal": blocos(t, municipio),
        f"sensibilidade_so_unidades_com_{int(LIMIAR_SENS * 100)}pct_num_setor": {
            "unidades": int(len(sens)), **blocos(sens, municipio)},
        "datacao": "grupos do item 3 lidos de derivados/i02_evolucao_urbana_unidades.csv (fora "
                   "do git): fonte não redistribuível, interpretação; aqui só agregados",
        "fcu": "setores de favelas e comunidades urbanas pela coluna CD_FCU da camada "
               "setores_2022 (7 setores; iguais à planilha oficial do IBGE)",
        "crs_operacao": paths.crs_producao(),
        "crs_medicao_area": medidas.crs_medicao_area(),
    }
    SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    colunas = ["classe", "resolucao", "dom_10", "dom_22", "setor", "frac_no_setor",
               "setores_com_1pct", "tem_entorno", "dentro_au", "fcu", "frac_em_fcu", "periodo",
               *ITENS, *EXTRA]
    t[colunas].to_csv(LISTA, encoding="utf-8")
    print(f"gravado: {paths.relativo(SAIDA)} e {paths.relativo(LISTA)}")


if __name__ == "__main__":
    main()
