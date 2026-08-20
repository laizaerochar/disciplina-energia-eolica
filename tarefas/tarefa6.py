"""
TAREFA 6 - Energia Eolica (Aula 03)
Curvas de Weibull para a outra localidade -- Fortaleza/CE -- em relacao a
Tarefa 5 (que usou Picos/PI), nos MESMOS dois anos (2019 e 2024) e com os
MESMOS 3 valores de k, para permitir comparacao direta entre as duas
localidades.

Fundamentacao (slides da Aula 03):
    Equacao (10) - Funcao densidade de probabilidade de Weibull:

        f(v) = (k/c) * (v/c)^(k-1) * exp( -(v/c)^k )

    onde:
        v = velocidade do vento [m/s]
        c = fator de escala [m/s] (relacionado a velocidade media do local)
        k = fator de forma [adimensional] (relacionado a dispersao em torno
            da media)

    O slide 8 mostra o metodo usado aqui: para uma MESMA localidade/ano
    (mesmo c), tracam-se varias curvas de Weibull variando apenas k.

    O slide 9 lista os 3 valores de k usados neste trabalho, cada um
    reproduzindo uma distribuicao classica conhecida:
        k = 1.0 -> Distribuicao Exponencial
        k = 2.0 -> Distribuicao de Rayleigh
        k = 3.5 -> aproxima-se de uma Distribuicao Normal

Estimativa do fator de escala c:
    Para cada ano, c e estimado a partir da velocidade media medida no
    periodo (V_mean, Eq. A do slide 2), usando a relacao de Rayleigh
    (k=2, simplificacao classica e amplamente usada quando nao se dispoe
    de um ajuste MLE completo aos dados, citada no slide 9):

        c = V_mean / Gamma(1 + 1/2) = V_mean / Gamma(1.5)

    Esse MESMO c (por ano) e entao usado para tracar as 3 curvas de k
    diferentes, reproduzindo a metodologia do slide 8 (c fixo, k variavel).

Dado utilizado: WS50M (velocidade do vento a 50m, NASA POWER/MERRA-2),
mesma coluna usada na Tarefa 5, garantindo consistencia entre as tarefas.

Saidas (salvas em ../resultados/tarefa6/):
    weibull_fortaleza_2019.png
    weibull_fortaleza_2024.png
    tabela_parametros_weibull_fortaleza.csv
"""

import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "banco-de-dados")
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa6")
os.makedirs(OUT_DIR, exist_ok=True)

CAMINHO_CSV = os.path.join(DATA_DIR, "fortaleza.csv")
LOCALIDADE = "Fortaleza/CE"
COL_VEL = "WS50M"  # mesma coluna usada na Tarefa 5, para comparacao direta

ANOS = [2019, 2024]
VALORES_K = [1.0, 2.0, 3.5]
CORES_K = {1.0: "#27ae60", 2.0: "#e74c3c", 3.5: "#2980b9"}
NOMES_K = {1.0: "k=1,0 (Exponencial)", 2.0: "k=2,0 (Rayleigh)", 3.5: "k=3,5 (~Normal)"}


# ----------------------------------------------------------------------
# Leitura dos dados (padrao NASA POWER, igual as tarefas 3 e 4)
# ----------------------------------------------------------------------
def carregar_dataframe(caminho_csv):
    df = pd.read_csv(caminho_csv, skiprows=11, na_values=[-999.0, -999])
    df["datetime"] = pd.to_datetime({
        "year": df["YEAR"], "month": df["MO"], "day": df["DY"], "hour": df["HR"]
    })
    df = df.set_index("datetime").sort_index()
    df["Ano"] = df.index.year
    return df


df = carregar_dataframe(CAMINHO_CSV)


# ----------------------------------------------------------------------
# Funcao densidade de probabilidade de Weibull - Equacao (10)
# ----------------------------------------------------------------------
def weibull_pdf(v, c, k):
    v = np.asarray(v, dtype=float)
    resultado = np.zeros_like(v)
    mask = v > 0
    resultado[mask] = (k / c) * (v[mask] / c) ** (k - 1) * np.exp(-(v[mask] / c) ** k)
    return resultado


# ----------------------------------------------------------------------
# Processamento por ano: estimar c, montar histograma real e curvas de Weibull
# ----------------------------------------------------------------------
resumo = []

for ano in ANOS:
    velocidades = df.loc[df["Ano"] == ano, COL_VEL].dropna()
    v_mean = velocidades.mean()

    # fator de escala c, via aproximacao de Rayleigh (k=2) a partir da
    # velocidade media medida (ver fundamentacao no cabecalho do script)
    c = v_mean / math.gamma(1.5)

    # histograma real dos dados (densidade de probabilidade, area = 1,
    # para poder ser comparado diretamente com f(v))
    vmax = velocidades.max()
    bins = np.arange(0, np.ceil(vmax) + 1, 1)
    contagem, bordas = np.histogram(velocidades, bins=bins, density=True)
    centros = (bordas[:-1] + bordas[1:]) / 2

    # curva continua de v para plotar f(v)
    v_continuo = np.linspace(0.01, vmax + 2, 400)

    # --- grafico ---
    plt.figure(figsize=(10, 6))
    plt.bar(centros, contagem, width=0.9, color="lightgray",
            edgecolor="black", label="Dados medidos (histograma)")

    for k in VALORES_K:
        f_v = weibull_pdf(v_continuo, c, k)
        plt.plot(v_continuo, f_v, color=CORES_K[k], linewidth=2.2,
                  label=NOMES_K[k])

    plt.title(f"Distribuicao de Weibull - {LOCALIDADE} ({ano})\n"
              f"V_media = {v_mean:.3f} m/s | c = {c:.3f} m/s (Rayleigh, k=2)")
    plt.xlabel("Velocidade do vento v [m/s]")
    plt.ylabel("Densidade de probabilidade f(v)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    caminho_fig = os.path.join(OUT_DIR, f"weibull_fortaleza_{ano}.png")
    plt.savefig(caminho_fig, dpi=150)
    plt.close()
    print(f"Grafico salvo: {caminho_fig}")

    resumo.append({
        "Ano": ano,
        "V_media [m/s]": round(v_mean, 3),
        "c [m/s]": round(c, 3),
        "k_1": VALORES_K[0], "k_2": VALORES_K[1], "k_3": VALORES_K[2],
        "n_registros": int(velocidades.count()),
    })

tabela_resumo = pd.DataFrame(resumo)
caminho_tabela = os.path.join(OUT_DIR, "tabela_parametros_weibull_fortaleza.csv")
tabela_resumo.to_csv(caminho_tabela, sep=";", decimal=",", index=False)
print(f"\nTabela de parametros salva em: {caminho_tabela}")
print(tabela_resumo.to_string(index=False))

print(f"\nTodos os resultados da Tarefa 6 foram salvos em: {OUT_DIR}")