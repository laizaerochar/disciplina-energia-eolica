"""
TAREFA 13 - Energia Eolica (Aula 07)
"Calcular os fatores de capacidade de um aerogerador para diferentes
velocidades medias do vento (localidades e ano de medicao) considerando
que elas sejam calculadas usando a distribuicao de Weibull. Para
calcular os parametros da distribuicao de Weibull, deve-se usar 3
metodos."

------------------------------------------------------------------------
DIFERENCA EM RELACAO A TAREFA 12
------------------------------------------------------------------------
Na Tarefa 12, a frequencia f(v) usada na tabela vinha do HISTOGRAMA REAL
dos dados medidos (contagem real de horas em cada velocidade).

Na Tarefa 13, f(v) NAO vem mais dos dados brutos -- vem da distribuicao
TEORICA de Weibull, calculada a partir dos parametros (k, c) que a
Tarefa 7 ja estimou por 3 metodos diferentes (Desvio Padrao, Metodo
Grafico e Maxima Verossimilhanca) para cada localidade/ano.

A potencia P(v) continua sendo a MESMA curva real de fabricante da
Tarefa 12 (turbina classe 1500 kW, Masters 2013) -- nao muda.

Isso gera: 2 localidades x 2 anos x 3 metodos = 12 fatores de
capacidade calculados ao final.

------------------------------------------------------------------------
COMO TRANSFORMAR A DENSIDADE DE WEIBULL EM FREQUENCIA POR FAIXA (%)
------------------------------------------------------------------------
A funcao de densidade de probabilidade de Weibull, f(v), NAO da
diretamente "quantos % do tempo o vento esta exatamente numa dada
velocidade" -- ela e uma densidade (a probabilidade so existe integrada
sobre um intervalo). Por isso, usa-se a funcao de distribuicao
CUMULATIVA de Weibull (ja apresentada em aula):

    F(v) = 1 - exp[-(v/c)^k]

e calcula-se a probabilidade de uma faixa de largura 1 m/s centrada no
inteiro v (faixa [v-0.5, v+0.5)) como a DIFERENCA da cumulativa nos dois
extremos da faixa:

    f_faixa(v) = F(v+0.5) - F(v-0.5)

Essa e exatamente a mesma logica da Equacao (12) apresentada no slide da
Aula 04 para o calculo discretizado da potencia media usando faixas
(bins) da distribuicao acumulada de Weibull -- aqui aplicada porque a
curva real do aerogerador nao possui forma fechada (diferentemente da
Tarefa 8, que usava a formula analitica de Betz/Gamma).

Verificacao: somando f_faixa(v) para todo v de 0 a ~30, o resultado deve
ser exatamente 1.0 (100%) -- isso e conferido automaticamente no script.

------------------------------------------------------------------------
CALCULO DA EAG E DO FATOR DE CAPACIDADE
------------------------------------------------------------------------
    EAG = SOMA[f_faixa(v) . P(v)] * 8760                         (kWh/ano)
    Fc  = EAG / (8760 * P_nominal)                                  [%]

Dado de vento utilizado (para obter V_media, base do calculo de k e c
pela Tarefa 7): WS50M (velocidade do vento a 50m, NASA POWER/MERRA-2).

Saidas (salvas em ../resultados/tarefa13/):
    tabela_fc_picos_2019.csv (e demais 3 combinacoes)
    resumo_fatores_capacidade.csv (os 12 valores consolidados)
"""

import os
import math
import numpy as np
import pandas as pd
from scipy.special import gamma

# ----------------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "banco-de-dados")
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa13")
os.makedirs(OUT_DIR, exist_ok=True)

LOCALIDADES = {"Picos": "picos.csv", "Fortaleza": "fortaleza.csv"}
COL_VEL = "WS50M"
ANOS = [2019, 2024]

HORAS_POR_ANO = 8760
V_MAX_SOMATORIO = 30  # faixa de velocidades consideradas na soma (m/s)

# ----------------------------------------------------------------------
# Curva de potencia REAL do aerogerador (mesma da Tarefa 12)
# Fonte: MASTERS, G. M. Renewable and Efficient Electric Power Systems,
# Tabela 13-3 / Figura 13-14 (turbina classe 1,5 MW)
# ----------------------------------------------------------------------
NOME_TURBINA = "Turbina 1500 kW (curva de fabricante -- Masters, Tab. 13-3)"
P_NOMINAL = 1500.0  # kW

TABELA_POTENCIA_TURBINA = {
    0: 0.0, 1: 0.0, 2: 0.0,
    3: 14.0, 4: 60.0, 5: 155.0, 6: 269.0, 7: 420.0, 8: 625.0, 9: 900.0,
    10: 1195.0, 11: 1395.0, 12: 1485.0,
    13: 1500.0, 14: 1500.0, 15: 1500.0, 16: 1500.0, 17: 1500.0,
    18: 1500.0, 19: 1500.0, 20: 1500.0,
}
V_CUT_OUT = 21  # [m/s]


def potencia_turbina(v_int):
    if v_int >= V_CUT_OUT:
        return 0.0
    return TABELA_POTENCIA_TURBINA.get(v_int, 0.0)


# ----------------------------------------------------------------------
# Leitura dos dados e calculo de V_media (padrao NASA POWER)
# ----------------------------------------------------------------------
def carregar_dataframe(caminho_csv):
    df = pd.read_csv(caminho_csv, skiprows=11, na_values=[-999.0, -999])
    df["datetime"] = pd.to_datetime({
        "year": df["YEAR"], "month": df["MO"], "day": df["DY"], "hour": df["HR"]
    })
    df = df.set_index("datetime").sort_index()
    df["Ano"] = df.index.year
    return df


# ----------------------------------------------------------------------
# Os 3 metodos de estimativa de (k, c) -- identicos a Tarefa 7
# ----------------------------------------------------------------------
def metodo_desvio_padrao(v):
    v_media = v.mean()
    sigma = v.std(ddof=1)
    k = (sigma / v_media) ** (-1.086)
    c = v_media / gamma(1 + 1 / k)
    return k, c


def metodo_grafico(v):
    from scipy.stats import linregress
    n = len(v)
    vmax = v.max()
    bins = np.arange(0, np.ceil(vmax) + 1, 1)
    contagem, bordas = np.histogram(v, bins=bins)
    freq_acumulada = np.cumsum(contagem) / n
    bordas_superiores = bordas[1:]
    mask = (freq_acumulada > 0) & (freq_acumulada < 1)
    x = np.log(bordas_superiores[mask])
    y = np.log(-np.log(1 - freq_acumulada[mask]))
    reg = linregress(x, y)
    k = reg.slope
    c = math.exp(-reg.intercept / k)
    return k, c


def metodo_maxima_verossimilhanca(v, k_inicial=2.0, tol=1e-10, max_iter=200):
    k = k_inicial
    for _ in range(max_iter):
        vk = v ** k
        termo1 = np.sum(vk * np.log(v)) / np.sum(vk)
        termo2 = np.mean(np.log(v))
        k_novo = 1.0 / (termo1 - termo2)
        if abs(k_novo - k) < tol:
            k = k_novo
            break
        k = k_novo
    c = (np.mean(v ** k)) ** (1 / k)
    return k, c


# ----------------------------------------------------------------------
# Distribuicao de Weibull discretizada em faixas de 1 m/s (via CDF)
# ----------------------------------------------------------------------
def weibull_cdf(v, c, k):
    return 1 - np.exp(-(np.maximum(v, 0) / c) ** k)


def frequencia_faixa_weibull(v_int, c, k):
    """Probabilidade (fracao, 0-1) da faixa [v_int-0.5, v_int+0.5)"""
    lim_inf = max(v_int - 0.5, 0.0)
    lim_sup = v_int + 0.5
    return weibull_cdf(lim_sup, c, k) - weibull_cdf(lim_inf, c, k)


# ----------------------------------------------------------------------
# Processamento principal
# ----------------------------------------------------------------------
NOMES_METODOS = {
    "Desvio_Padrao": metodo_desvio_padrao,
    "Grafico_Min_Quadrados": metodo_grafico,
    "Maxima_Verossimilhanca": metodo_maxima_verossimilhanca,
}

resultados_finais = []

for nome_local, arquivo in LOCALIDADES.items():
    df = carregar_dataframe(os.path.join(DATA_DIR, arquivo))

    for ano in ANOS:
        v_dados = df.loc[df["Ano"] == ano, COL_VEL].dropna().values
        v_dados = v_dados[v_dados > 0]  # remove zeros exatos (necessario p/ log nos metodos)
        v_media_real = v_dados.mean()

        for nome_metodo, funcao_metodo in NOMES_METODOS.items():
            k, c = funcao_metodo(v_dados)

            # monta a tabela de frequencia TEORICA (Weibull) x potencia real
            velocidades = list(range(0, V_MAX_SOMATORIO))
            freqs = [frequencia_faixa_weibull(v, c, k) * 100 for v in velocidades]  # em %
            potencias = [potencia_turbina(v) for v in velocidades]
            fv_pv = [f / 100 * p for f, p in zip(freqs, potencias)]

            soma_freq = sum(freqs)          # deve ser ~100.000
            soma_fv_pv = sum(fv_pv)          # kW medio
            eag = soma_fv_pv * HORAS_POR_ANO  # kWh/ano
            fc = eag / (HORAS_POR_ANO * P_NOMINAL) * 100  # %

            # salva a tabela detalhada desta combinacao (apenas as faixas
            # com contribuicao numericamente relevante, para nao poluir
            # o arquivo com dezenas de linhas de f(v)~0)
            tabela = pd.DataFrame({
                "Velocidade_m_s": velocidades,
                "Frequencia_Weibull_%": [round(f, 4) for f in freqs],
                "Potencia_kW": potencias,
                "f(v).P(v)": [round(x, 5) for x in fv_pv],
            })
            tabela = tabela[(tabela["Frequencia_Weibull_%"] > 0.0005) | (tabela["Potencia_kW"] > 0)]

            nome_arquivo = f"tabela_fc_{nome_local.lower()}_{ano}_{nome_metodo.lower()}.csv"
            tabela.to_csv(os.path.join(OUT_DIR, nome_arquivo), sep=";", decimal=",", index=False)

            print(f"=== {nome_local} {ano} | Metodo: {nome_metodo} | k={k:.4f} c={c:.4f} ===")
            print(f"  V_media (dados reais) = {v_media_real:.3f} m/s")
            print(f"  Soma f(v) = {soma_freq:.4f}% (verificacao: deve ser ~100%)")
            print(f"  Soma f(v).P(v) = {soma_fv_pv:.3f} kW")
            print(f"  EAG = {eag:,.2f} kWh/ano")
            print(f"  Fator de capacidade Fc = {fc:.2f}%\n")

            resultados_finais.append({
                "Localidade": nome_local, "Ano": ano, "Metodo": nome_metodo,
                "k": round(k, 4), "c_m_s": round(c, 4),
                "V_media_m_s": round(v_media_real, 3),
                "Soma_fv_Pv_kW": round(soma_fv_pv, 3),
                "EAG_kWh_ano": round(eag, 2),
                "Fc_%": round(fc, 2),
            })

# ----------------------------------------------------------------------
# Tabela resumo final consolidada (os 12 fatores de capacidade)
# ----------------------------------------------------------------------
tabela_resumo = pd.DataFrame(resultados_finais)
caminho_resumo = os.path.join(OUT_DIR, "resumo_fatores_capacidade.csv")
tabela_resumo.to_csv(caminho_resumo, sep=";", decimal=",", index=False)

print("=" * 90)
print("RESUMO FINAL - Fatores de Capacidade via distribuicao de Weibull (3 metodos)")
print("=" * 90)
print(tabela_resumo.to_string(index=False))
print(f"\nTabela resumo salva em: {caminho_resumo}")

# ----------------------------------------------------------------------
# GRAFICO 1: Fc por metodo, um grafico separado por combinacao localidade/ano
# ----------------------------------------------------------------------
import matplotlib.pyplot as plt

NOMES_CURTOS_METODO = {
    "Desvio_Padrao": "Desvio\nPadrao",
    "Grafico_Min_Quadrados": "Grafico",
    "Maxima_Verossimilhanca": "Max.\nVerossim.",
}
CORES_METODO = {
    "Desvio_Padrao": "#e74c3c",
    "Grafico_Min_Quadrados": "#27ae60",
    "Maxima_Verossimilhanca": "#2980b9",
}

combinacoes = tabela_resumo[["Localidade", "Ano"]].drop_duplicates().values.tolist()

for localidade, ano in combinacoes:
    sub = tabela_resumo[(tabela_resumo["Localidade"] == localidade) & (tabela_resumo["Ano"] == ano)]
    labels = [NOMES_CURTOS_METODO[m] for m in sub["Metodo"]]
    valores = sub["Fc_%"].values
    cores = [CORES_METODO[m] for m in sub["Metodo"]]

    plt.figure(figsize=(7, 5.5))
    barras = plt.bar(labels, valores, color=cores, edgecolor="black")
    for barra, valor in zip(barras, valores):
        plt.text(barra.get_x() + barra.get_width() / 2, valor, f"{valor:.2f}%",
                  ha="center", va="bottom", fontsize=10)
    plt.title(f"Fator de capacidade (Weibull) - {localidade} ({ano})\nTurbina 1500 kW")
    plt.ylabel("Fator de capacidade [%]")
    plt.ylim(0, max(valores) * 1.2)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    nome_fig = f"fc_metodos_{localidade.lower()}_{ano}.png"
    plt.savefig(os.path.join(OUT_DIR, nome_fig), dpi=150)
    plt.close()
    print(f"Grafico salvo: {nome_fig}")

# ----------------------------------------------------------------------
# GRAFICO 2: Fc real (Tarefa 12, dados medidos) vs Fc Weibull (Tarefa 13,
# media dos 3 metodos) -- grafico de validacao, 1 unico grafico com as
# 4 combinacoes lado a lado
# ----------------------------------------------------------------------
# Fatores de capacidade reais, calculados na Tarefa 12 a partir do
# histograma medido (EAG real / (8760 * 1500)) -- valores citados no
# proprio relatorio da Tarefa 12
FC_REAL_TAREFA12 = {
    ("Picos", 2019): 23.51,
    ("Picos", 2024): 22.22,
    ("Fortaleza", 2019): 39.32,
    ("Fortaleza", 2024): 40.34,
}

fc_medio_weibull = tabela_resumo.groupby(["Localidade", "Ano"])["Fc_%"].mean().reset_index()

labels_x = [f"{loc}\n{ano}" for loc, ano in zip(fc_medio_weibull["Localidade"], fc_medio_weibull["Ano"])]
fc_real_vals = [FC_REAL_TAREFA12[(loc, ano)] for loc, ano in zip(fc_medio_weibull["Localidade"], fc_medio_weibull["Ano"])]
fc_weibull_vals = fc_medio_weibull["Fc_%"].values

x = np.arange(len(labels_x))
largura = 0.35

plt.figure(figsize=(9, 6))
barras1 = plt.bar(x - largura/2, fc_real_vals, largura, label="Fc real (dados medidos, Tarefa 12)",
                   color="#2980b9", edgecolor="black")
barras2 = plt.bar(x + largura/2, fc_weibull_vals, largura, label="Fc Weibull (media dos 3 metodos, Tarefa 13)",
                   color="#27ae60", edgecolor="black")

for barra in list(barras1) + list(barras2):
    altura = barra.get_height()
    plt.text(barra.get_x() + barra.get_width()/2, altura, f"{altura:.2f}%",
              ha="center", va="bottom", fontsize=9)

plt.xticks(x, labels_x)
plt.ylabel("Fator de capacidade [%]")
plt.title("Validacao: Fator de capacidade real vs. estimado por Weibull\nTurbina 1500 kW")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

caminho_validacao = os.path.join(OUT_DIR, "fc_validacao_real_vs_weibull.png")
plt.savefig(caminho_validacao, dpi=150)
plt.close()
print(f"Grafico salvo: fc_validacao_real_vs_weibull.png")

print(f"\nTodos os resultados da Tarefa 13 foram salvos em: {OUT_DIR}")