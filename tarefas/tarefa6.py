"""
TAREFA 6 - Energia Eolica (Aula 03) -- VERSAO CORRIGIDA (Fortaleza e Picos)
Curvas de Weibull para Fortaleza/CE e Picos/PI, em dois anos (2019 e 2024), 
considerando 3 tipos de k, CADA UM COM SEU PROPRIO fator de escala c.
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

# LISTA DE LOCALIDADES PARA ITERAR
LOCALIDADES = [
    {"arquivo": "fortaleza.csv", "nome": "Fortaleza/CE", "prefixo": "fortaleza"},
    {"arquivo": "picos.csv", "nome": "Picos/PI", "prefixo": "picos"}
]

COL_VEL = "WS50M"
ANOS = [2019, 2024]
VALORES_K = [1.0, 2.0, 3.5]
NOMES_K = {1.0: "Exponencial", 2.0: "Rayleigh", 3.5: "~Normal"}
CORES_K = {1.0: "#27ae60", 2.0: "#e74c3c", 3.5: "#2980b9"}

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
# Funcao densidade de probabilidade de Weibull - Equacao (10)
# ----------------------------------------------------------------------
def weibull_pdf(v, c, k):
    v = np.asarray(v, dtype=float)
    resultado = np.zeros_like(v)
    mask = v > 0
    resultado[mask] = (k / c) * (v[mask] / c) ** (k - 1) * np.exp(-(v[mask] / c) ** k)
    return resultado

# ----------------------------------------------------------------------
# Processamento: para cada local, ano e cada k, calcular c_k e plotar
# ----------------------------------------------------------------------
resumo = []

# LAÇO EXTERNO PARA ITERAR SOBRE AS LOCALIDADES
for loc in LOCALIDADES:
    caminho_csv = os.path.join(DATA_DIR, loc["arquivo"])
    nome_local = loc["nome"]
    prefixo = loc["prefixo"]
    
    print(f"\n--- Processando dados de {nome_local} ---")
    
    # Carrega o dataframe correspondente a localidade atual
    df = carregar_dataframe(caminho_csv)

    for ano in ANOS:
        velocidades = df.loc[df["Ano"] == ano, COL_VEL].dropna()
        if velocidades.empty:
            print(f"Sem dados para {nome_local} no ano {ano}.")
            continue
            
        v_mean = velocidades.mean()

        # histograma real dos dados (densidade, area = 1)
        vmax = velocidades.max()
        bins = np.arange(0, np.ceil(vmax) + 1, 1)
        contagem, bordas = np.histogram(velocidades, bins=bins, density=True)
        centros = (bordas[:-1] + bordas[1:]) / 2
        v_continuo = np.linspace(0.01, vmax + 2, 400)

        for k in VALORES_K:
            # fator de escala PROPRIO para este k (nao compartilhado)
            c_k = v_mean / math.gamma(1 + 1 / k)
            f_v = weibull_pdf(v_continuo, c_k, k)

            plt.figure(figsize=(9, 6))
            plt.bar(centros, contagem, width=0.9, color="lightgray",
                    edgecolor="black", label="Dados medidos (histograma)")
            plt.plot(v_continuo, f_v, color=CORES_K[k], linewidth=2.4,
                      label=f"k={k:.1f} ({NOMES_K[k]}), c={c_k:.3f} m/s")

            plt.title(f"Distribuicao de Weibull - {nome_local} ({ano})\n"
                      f"k={k:.1f} ({NOMES_K[k]}) | V_media={v_mean:.3f} m/s | c={c_k:.3f} m/s", fontsize=11)
            plt.xlabel("Velocidade do vento v [m/s]")
            plt.ylabel("Densidade de probabilidade f(v)")
            plt.legend()
            plt.grid(alpha=0.3)
            plt.tight_layout()

            # O nome do arquivo usa o prefixo da localidade de forma dinâmica
            nome_arquivo = f"weibull_{prefixo}_{ano}_k{k}.png"
            caminho_fig = os.path.join(OUT_DIR, nome_arquivo)
            plt.savefig(caminho_fig, dpi=150)
            plt.close()
            print(f"Grafico salvo: {caminho_fig}")

            resumo.append({
                "Localidade": nome_local, "Ano": ano, "k": k,
                "V_media [m/s]": round(v_mean, 3), "c_k [m/s]": round(c_k, 4),
                "n_registros": int(velocidades.count()),
            })

# Salvando a tabela conjunta
tabela_resumo = pd.DataFrame(resumo)
caminho_tabela = os.path.join(OUT_DIR, "tabela_parametros_weibull.csv")
tabela_resumo.to_csv(caminho_tabela, sep=";", decimal=",", index=False)

print(f"\nTabela de parametros salva em: {caminho_tabela}")
print(tabela_resumo.to_string(index=False))

print(f"\nTotal de graficos gerados nesta tarefa: {len(resumo)} "
      f"({len(LOCALIDADES)} localidades x {len(ANOS)} anos x {len(VALORES_K)} valores de k)")
print(f"Todos os resultados da Tarefa 6 foram salvos em: {OUT_DIR}")