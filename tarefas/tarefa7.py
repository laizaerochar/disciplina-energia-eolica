"""
TAREFA 7 - Energia Eolica (Aula 04)
Calculo dos parametros de Weibull (k, c) por pelo menos 3 metodos, para as
duas localidades trabalhadas nas Tarefas 5/6 (Picos/PI e Fortaleza/CE) e
para os dois anos considerados (2019 e 2024).

Dado utilizado: WS50M (velocidade do vento a 50m, NASA POWER/MERRA-2),
mesma variavel usada nas Tarefas 4, 5 e 6, para consistencia entre todas
as analises deste projeto.

------------------------------------------------------------------------
METODOS IMPLEMENTADOS (3, conforme exigido pela Tarefa 7)
------------------------------------------------------------------------

(1) METODO DO DESVIO PADRAO (empirico, Justus) -- conforme slides da
    Aula 04 (Equacoes 5 e 9):

        k = (sigma / V_media)^(-1,086)                              (Eq. 9)
        c = V_media / Gamma(1 + 1/k)                                (Eq. 5)

    onde sigma e o desvio padrao amostral da velocidade do vento e
    V_media e a velocidade media. Este e um metodo aproximado (formula
    empirica de Justus), rapido de calcular e muito usado na pratica.

(2) METODO GRAFICO (regressao linear / minimos quadrados sobre a funcao
    de distribuicao acumulada linearizada):

    A funcao de distribuicao cumulativa de Weibull e (Equacao 2 do
    slide): F(v) = 1 - exp[-(v/c)^k]. Aplicando logaritmo natural duas
    vezes:

        ln( -ln(1 - F(v)) ) = k * ln(v) - k * ln(c)

    que e uma reta em y = ln(-ln(1-F(v))) vs x = ln(v), com:
        inclinacao (slope) = k
        intercepto = -k * ln(c)  =>  c = exp(-intercepto / k)

    Os dados sao agrupados em faixas (bins) de 1 m/s (mesmo criterio da
    Tarefa 4), calcula-se a frequencia acumulada empirica F em cada
    faixa, e ajusta-se a reta por minimos quadrados (scipy.stats.linregress).

(3) METODO DA MAXIMA VEROSSIMILHANCA (MLE, formula iterativa de
    Stevens & Smulders):

        k_(n+1) = [ (soma(v_i^k * ln(v_i)) / soma(v_i^k)) - media(ln(v_i)) ]^(-1)

    iterado ate convergencia (tolerancia 1e-10), partindo de k0 = 2,0.
    Em seguida:

        c = ( media(v_i^k) )^(1/k)

    Este e o metodo estatisticamente mais rigoroso (maximiza a
    verossimilhanca da amostra observada dado o modelo Weibull).

Saidas (salvas em ../resultados/tarefa7/):
    tabela_parametros_weibull_3metodos.csv
    comparacao_metodos_picos_2019.png
    comparacao_metodos_picos_2024.png
    comparacao_metodos_fortaleza_2019.png
    comparacao_metodos_fortaleza_2024.png
"""

import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.special import gamma

# ----------------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "banco-de-dados")
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa7")
os.makedirs(OUT_DIR, exist_ok=True)

LOCALIDADES = {"Picos": "picos.csv", "Fortaleza": "fortaleza.csv"}
COL_VEL = "WS50M"
ANOS = [2019, 2024]


# ----------------------------------------------------------------------
# Leitura dos dados (padrao NASA POWER)
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
# Metodo 1 - Desvio padrao (Justus), Equacoes 5 e 9 do slide
# ----------------------------------------------------------------------
def metodo_desvio_padrao(v):
    v_media = v.mean()
    sigma = v.std(ddof=1)
    k = (sigma / v_media) ** (-1.086)
    c = v_media / gamma(1 + 1 / k)
    return k, c


# ----------------------------------------------------------------------
# Metodo 2 - Grafico (regressao linear sobre a CDF linearizada)
# ----------------------------------------------------------------------
def metodo_grafico(v):
    n = len(v)
    vmax = v.max()
    bins = np.arange(0, np.ceil(vmax) + 1, 1)
    contagem, bordas = np.histogram(v, bins=bins)
    freq_acumulada = np.cumsum(contagem) / n
    bordas_superiores = bordas[1:]

    # remove F=0 (ln(0) indefinido) e F=1 (ln(-ln(0)) indefinido)
    mask = (freq_acumulada > 0) & (freq_acumulada < 1)
    x = np.log(bordas_superiores[mask])
    y = np.log(-np.log(1 - freq_acumulada[mask]))

    reg = linregress(x, y)
    k = reg.slope
    c = math.exp(-reg.intercept / k)
    r2 = reg.rvalue ** 2
    return k, c, r2


# ----------------------------------------------------------------------
# Metodo 3 - Maxima Verossimilhanca (MLE, iterativo Stevens & Smulders)
# ----------------------------------------------------------------------
def metodo_maxima_verossimilhanca(v, k_inicial=2.0, tol=1e-10, max_iter=200):
    k = k_inicial
    for iteracao in range(1, max_iter + 1):
        vk = v ** k
        termo1 = np.sum(vk * np.log(v)) / np.sum(vk)
        termo2 = np.mean(np.log(v))
        k_novo = 1.0 / (termo1 - termo2)
        if abs(k_novo - k) < tol:
            k = k_novo
            break
        k = k_novo
    else:
        raise RuntimeError("Metodo MLE nao convergiu no numero maximo de iteracoes.")
    c = (np.mean(v ** k)) ** (1 / k)
    return k, c, iteracao


# ----------------------------------------------------------------------
# Processamento principal
# ----------------------------------------------------------------------
resultados = []

for nome_local, arquivo in LOCALIDADES.items():
    df = carregar_dataframe(os.path.join(DATA_DIR, arquivo))

    for ano in ANOS:
        v = df.loc[df["Ano"] == ano, COL_VEL].dropna().values
        v = v[v > 0]  # remove zeros exatos (necessario para os metodos com log)
        n = len(v)
        v_media = v.mean()
        sigma = v.std(ddof=1)

        k1, c1 = metodo_desvio_padrao(v)
        k2, c2, r2 = metodo_grafico(v)
        k3, c3, n_iter = metodo_maxima_verossimilhanca(v)

        print(f"\n=== {nome_local} - {ano} (n={n}, V_media={v_media:.3f} m/s, "
              f"sigma={sigma:.3f} m/s) ===")
        print(f"  Metodo 1 (Desvio Padrao) : k={k1:.4f}  c={c1:.4f} m/s")
        print(f"  Metodo 2 (Grafico)       : k={k2:.4f}  c={c2:.4f} m/s  (R2={r2:.5f})")
        print(f"  Metodo 3 (Max. Verossim.): k={k3:.4f}  c={c3:.4f} m/s  ({n_iter} iteracoes)")

        resultados.append({"Localidade": nome_local, "Ano": ano, "Metodo": "Desvio_Padrao",
                            "k": round(k1, 4), "c_m_s": round(c1, 4),
                            "V_media_m_s": round(v_media, 3), "sigma_m_s": round(sigma, 3)})
        resultados.append({"Localidade": nome_local, "Ano": ano, "Metodo": "Grafico_Min_Quadrados",
                            "k": round(k2, 4), "c_m_s": round(c2, 4),
                            "V_media_m_s": round(v_media, 3), "sigma_m_s": round(sigma, 3),
                            "R2": round(r2, 5)})
        resultados.append({"Localidade": nome_local, "Ano": ano, "Metodo": "Maxima_Verossimilhanca",
                            "k": round(k3, 4), "c_m_s": round(c3, 4),
                            "V_media_m_s": round(v_media, 3), "sigma_m_s": round(sigma, 3)})

tabela = pd.DataFrame(resultados)
caminho_tabela = os.path.join(OUT_DIR, "tabela_parametros_weibull_3metodos.csv")
tabela.to_csv(caminho_tabela, sep=";", decimal=",", index=False)
print(f"\n\nTabela consolidada salva em: {caminho_tabela}")
print(tabela.to_string(index=False))


# ----------------------------------------------------------------------
# Grafico de verificacao visual (opcional): compara as 3 curvas
# ajustadas por cada metodo contra o histograma real, um painel por
# combinacao localidade/ano
# ----------------------------------------------------------------------
def weibull_pdf(v, c, k):
    v = np.asarray(v, dtype=float)
    resultado = np.zeros_like(v)
    mask = v > 0
    resultado[mask] = (k / c) * (v[mask] / c) ** (k - 1) * np.exp(-(v[mask] / c) ** k)
    return resultado


# ----------------------------------------------------------------------
# Graficos de verificacao visual (opcional): um arquivo PNG separado por
# combinacao localidade/ano, cada um comparando as 3 curvas ajustadas
# contra o histograma real
# ----------------------------------------------------------------------
def weibull_pdf(v, c, k):
    v = np.asarray(v, dtype=float)
    resultado = np.zeros_like(v)
    mask = v > 0
    resultado[mask] = (k / c) * (v[mask] / c) ** (k - 1) * np.exp(-(v[mask] / c) ** k)
    return resultado


cores = {"Desvio_Padrao": "#e74c3c", "Grafico_Min_Quadrados": "#27ae60",
         "Maxima_Verossimilhanca": "#2980b9"}
nomes_curtos = {"Desvio_Padrao": "Desvio Padrao", "Grafico_Min_Quadrados": "Grafico",
                "Maxima_Verossimilhanca": "Max. Verossimilhanca"}

for nome_local, ano in [(loc, ano) for loc in LOCALIDADES for ano in ANOS]:
    df = carregar_dataframe(os.path.join(DATA_DIR, LOCALIDADES[nome_local]))
    v = df.loc[df["Ano"] == ano, COL_VEL].dropna().values
    v = v[v > 0]

    vmax = v.max()
    bins = np.arange(0, np.ceil(vmax) + 1, 1)
    contagem, bordas = np.histogram(v, bins=bins, density=True)
    centros = (bordas[:-1] + bordas[1:]) / 2

    plt.figure(figsize=(9, 6))
    plt.bar(centros, contagem, width=0.9, color="lightgray", edgecolor="black",
            label="Dados medidos", zorder=1)

    linha = tabela[(tabela["Localidade"] == nome_local) & (tabela["Ano"] == ano)]
    v_continuo = np.linspace(0.01, vmax + 2, 300)
    for _, linha_metodo in linha.iterrows():
        k, c = linha_metodo["k"], linha_metodo["c_m_s"]
        f_v = weibull_pdf(v_continuo, c, k)
        plt.plot(v_continuo, f_v, color=cores[linha_metodo["Metodo"]], linewidth=2.2,
                  label=f"{nomes_curtos[linha_metodo['Metodo']]} (k={k:.2f}, c={c:.2f})")

    plt.title(f"Comparacao dos 3 metodos de ajuste de Weibull - {nome_local} ({ano})")
    plt.xlabel("Velocidade do vento v [m/s]")
    plt.ylabel("Densidade de probabilidade f(v)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    nome_arquivo = f"comparacao_metodos_{nome_local.lower()}_{ano}.png"
    caminho_fig = os.path.join(OUT_DIR, nome_arquivo)
    plt.savefig(caminho_fig, dpi=150)
    plt.close()
    print(f"Grafico salvo: {caminho_fig}")

print(f"\nTodos os resultados da Tarefa 7 foram salvos em: {OUT_DIR}")