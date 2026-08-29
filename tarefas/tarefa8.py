"""
TAREFA 8 - Energia Eolica (Aula 04)
Calculo da produtividade (potencia media disponivel por unidade de area
varrida do rotor) para cada caso visto na Tarefa 7, utilizando as duas
distribuicoes apresentadas nos slides (Rayleigh e Weibull), considerando
os 3 metodos de ajuste de (k, c) da Tarefa 7, para as duas localidades
(Picos/PI e Fortaleza/CE) e os dois anos (2019 e 2024).

DEPENDENCIA: este script LE a tabela gerada pela tarefa7.py
(../resultados/tarefa7/tabela_parametros_weibull_3metodos.csv).
Execute tarefa7.py antes deste script.

------------------------------------------------------------------------
FUNDAMENTACAO (conforme slides da Aula 04)
------------------------------------------------------------------------
Para uma "maquina ideal" (eficiencia eta=1, coeficiente de potencia no
limite de Betz, Cp_Betz = 16/27), a potencia media por unidade de area
varrida do rotor e obtida a partir do terceiro momento estatistico da
velocidade do vento:

    Pw_media / A = (1/2) * rho * Cp_Betz * E[V^3]                   (*)

onde E[V^3] e o valor esperado do cubo da velocidade do vento segundo a
distribuicao de probabilidade considerada.

CASO RAYLEIGH (slides 11-12, Equacoes 4-9):
    Distribuicao de Rayleigh e o caso particular de Weibull com k=2,
    parametrizada apenas pela velocidade media V (nao precisa de
    metodo de ajuste). Slide define a velocidade caracteristica
    Vc = 2*V/sqrt(pi), e mostra que a integral se resolve
    analiticamente para:

        Pw_media / A = rho * (2/3)^2 * V^3 * (constante geometrica),

    que, generalizando pela relacao E[V^3] = c^3 * Gamma(1+3/k) com
    k=2 (c = Vc = 2V/sqrt(pi), Gamma(2.5) = (3/4)*sqrt(pi)), da:

        Pw_media / A = (1/2) * rho * Cp_Betz * Vc^3 * Gamma(2,5)

CASO WEIBULL GERAL (generalizacao das Equacoes 7-9 do slide para k
qualquer, usando o terceiro momento da Weibull, E[V^3] = c^3*Gamma(1+3/k)):

        Pw_media / A = (1/2) * rho * Cp_Betz * c^3 * Gamma(1 + 3/k)  (**)

Aqui, o par (k, c) e o obtido por cada um dos 3 metodos calculados na
Tarefa 7 -- portanto, para cada localidade/ano, calculam-se 3 valores de
produtividade Weibull (um por metodo) + 1 valor de produtividade Rayleigh
(referencia, usa so a media V).

Massa especifica do ar (rho): calculada pela mesma Equacao (2) da
Tarefa 2, particularizada para a altitude de cada localidade (Picos:
406,51 m; Fortaleza: 21,44 m) e T=25 graus C (mesma referencia de
temperatura usada na Tarefa 2), para manter a coerencia entre todas as
tarefas deste projeto.

NOTA IMPORTANTE: como nao foi fornecida uma curva de potencia de uma
turbina real (Pw(V) especifica de fabricante), os resultados aqui sao
reportados como DENSIDADE DE POTENCIA (W/m^2 de area varrida do rotor),
e nao como potencia absoluta de uma maquina especifica -- isso evita
supor um diametro de rotor arbitrario nao fornecido pelo enunciado, e
segue exatamente a formulacao apresentada nos slides para a "maquina
ideal" no limite de Betz.

Saidas (salvas em ../resultados/tarefa8/):
    tabela_produtividade.csv
    produtividade_picos_2019.png
    produtividade_picos_2024.png
    produtividade_fortaleza_2019.png
    produtividade_fortaleza_2024.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import gamma

# ----------------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_DIR = os.path.join(BASE_DIR, "resultados", "tarefa7")
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa8")
os.makedirs(OUT_DIR, exist_ok=True)

CAMINHO_TABELA_T7 = os.path.join(IN_DIR, "tabela_parametros_weibull_3metodos.csv")

CP_BETZ = 16 / 27  # coeficiente de potencia no limite de Betz
ALTITUDES = {"Picos": 406.51, "Fortaleza": 21.44}  # [m], mesmas da Tarefa 2
T_REF = 25.0  # [C], mesma referencia de temperatura da Tarefa 2


# ----------------------------------------------------------------------
# Verificacao de dependencia
# ----------------------------------------------------------------------
if not os.path.exists(CAMINHO_TABELA_T7):
    raise FileNotFoundError(
        f"Nao foi encontrado o arquivo '{CAMINHO_TABELA_T7}'.\n"
        f"Execute tarefa7.py antes de rodar tarefa8.py, pois esta tarefa "
        f"depende diretamente dos parametros (k, c) calculados na Tarefa 7."
    )


# ----------------------------------------------------------------------
# Equacao (2) da Tarefa 2: massa especifica do ar em funcao da altitude
# e da temperatura
# ----------------------------------------------------------------------
def massa_especifica(z, T):
    return 353.4 * (1 - z / 45271) ** 5.2624 / (273.15 + T)


# ----------------------------------------------------------------------
# Densidade de potencia (W/m^2) - Equacao (**) do cabecalho, valida
# tanto para Weibull generico quanto para Rayleigh (k=2 e' um caso
# particular desta mesma formula)
# ----------------------------------------------------------------------
def densidade_potencia_weibull(rho, c, k):
    return 0.5 * rho * CP_BETZ * (c ** 3) * gamma(1 + 3 / k)


def densidade_potencia_rayleigh(rho, v_media):
    # Rayleigh: k=2 fixo, c = Vc = 2*V_media/sqrt(pi)
    c_rayleigh = 2 * v_media / np.sqrt(np.pi)
    return densidade_potencia_weibull(rho, c_rayleigh, k=2.0)


# ----------------------------------------------------------------------
# Processamento principal
# ----------------------------------------------------------------------
tabela_t7 = pd.read_csv(CAMINHO_TABELA_T7, sep=";", decimal=",")

resultados = []

for (localidade, ano), grupo in tabela_t7.groupby(["Localidade", "Ano"]):
    z = ALTITUDES[localidade]
    rho = massa_especifica(z, T_REF)
    v_media = grupo["V_media_m_s"].iloc[0]  # igual em todas as linhas do grupo

    # --- Rayleigh (referencia, nao depende de metodo) ---
    dp_rayleigh = densidade_potencia_rayleigh(rho, v_media)
    resultados.append({
        "Localidade": localidade, "Ano": ano, "Distribuicao": "Rayleigh",
        "Metodo": "N/A (usa apenas V_media)", "k": 2.0,
        "c_m_s": round(2 * v_media / np.sqrt(np.pi), 4),
        "rho_kg_m3": round(rho, 4),
        "Densidade_Potencia_W_m2": round(dp_rayleigh, 3),
    })

    # --- Weibull, um valor por metodo da Tarefa 7 ---
    for _, linha in grupo.iterrows():
        k, c = linha["k"], linha["c_m_s"]
        dp_weibull = densidade_potencia_weibull(rho, c, k)
        resultados.append({
            "Localidade": localidade, "Ano": ano, "Distribuicao": "Weibull",
            "Metodo": linha["Metodo"], "k": round(k, 4), "c_m_s": round(c, 4),
            "rho_kg_m3": round(rho, 4),
            "Densidade_Potencia_W_m2": round(dp_weibull, 3),
        })

tabela_final = pd.DataFrame(resultados)
caminho_tabela = os.path.join(OUT_DIR, "tabela_produtividade.csv")
tabela_final.to_csv(caminho_tabela, sep=";", decimal=",", index=False)

print("=== TAREFA 8 - Densidade de potencia media (W/m^2), maquina ideal (Cp_Betz=16/27) ===\n")
print(tabela_final.to_string(index=False))
print(f"\nTabela salva em: {caminho_tabela}")


# ----------------------------------------------------------------------
# Grafico comparativo: barras agrupadas por localidade/ano, mostrando
# Rayleigh + os 3 metodos de Weibull lado a lado
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Graficos comparativos: um arquivo PNG separado por combinacao
# localidade/ano, cada um com barras lado a lado (Rayleigh + 3 metodos
# de Weibull)
# ----------------------------------------------------------------------
nomes_curtos_metodo = {
    "N/A (usa apenas V_media)": "Rayleigh",
    "Desvio_Padrao": "Weibull\n(Desvio Padrao)",
    "Grafico_Min_Quadrados": "Weibull\n(Grafico)",
    "Maxima_Verossimilhanca": "Weibull\n(Max. Verossim.)",
}
cores_metodo = {
    "N/A (usa apenas V_media)": "#7f8c8d",
    "Desvio_Padrao": "#e74c3c",
    "Grafico_Min_Quadrados": "#27ae60",
    "Maxima_Verossimilhanca": "#2980b9",
}

combinacoes = tabela_final[["Localidade", "Ano"]].drop_duplicates().values.tolist()

for localidade, ano in combinacoes:
    sub = tabela_final[(tabela_final["Localidade"] == localidade) & (tabela_final["Ano"] == ano)]
    labels = [nomes_curtos_metodo[m] for m in sub["Metodo"]]
    valores = sub["Densidade_Potencia_W_m2"].values
    cores = [cores_metodo[m] for m in sub["Metodo"]]

    plt.figure(figsize=(8, 6))
    barras = plt.bar(labels, valores, color=cores, edgecolor="black")
    for barra, valor in zip(barras, valores):
        plt.text(barra.get_x() + barra.get_width() / 2, valor, f"{valor:.0f}",
                  ha="center", va="bottom", fontsize=10)

    plt.title(f"Densidade de potencia media - {localidade} ({ano})\n"
              f"Maquina ideal, limite de Betz (Cp=16/27)")
    plt.ylabel("Densidade de potencia [W/m²]")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    nome_arquivo = f"produtividade_{localidade.lower()}_{ano}.png"
    caminho_fig = os.path.join(OUT_DIR, nome_arquivo)
    plt.savefig(caminho_fig, dpi=150)
    plt.close()
    print(f"Grafico salvo: {caminho_fig}")

print(f"\nTodos os resultados da Tarefa 8 foram salvos em: {OUT_DIR}")