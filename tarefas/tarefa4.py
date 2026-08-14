"""
TAREFA 4 - Energia Eolica (Aula 02)
Distribuicao de frequencia da velocidade do vento - Picos/PI, 2 anos (2019 e 2024)

Metodologia (igual a Tabela 3.1 / Figura 3.7 do livro):
    - Os dados de velocidade sao divididos em faixas (bins) de 1 m/s: 0-1, 1-2, 2-3, ...
    - Numero de ocorrencias: quantas vezes a velocidade caiu em cada faixa
    - Frequencia relativa (%) = (ocorrencias da faixa / total de ocorrencias do ano) * 100

Saidas (salvas em ../resultados/tarefa4/):
    tabela_distribuicao_2019.csv
    tabela_distribuicao_2024.csv
    tabela_distribuicao_comparativa.csv
    histograma_2019_vs_2024.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "banco-de-dados")
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa4")
os.makedirs(OUT_DIR, exist_ok=True)

CAMINHO_PICOS = os.path.join(DATA_DIR, "picos.csv")
COL_VEL = "VENTO, VELOCIDADE HORARIA(m/s)"

ANOS = [2019, 2024]


# ----------------------------------------------------------------------
# Leitura dos dados de Picos
# ----------------------------------------------------------------------
df = pd.read_csv(CAMINHO_PICOS, sep=";", skiprows=9, encoding="utf-8")
df["Data Medicao"] = pd.to_datetime(df["Data Medicao"])
df["Ano"] = df["Data Medicao"].dt.year

# remove apenas os registros sem leitura (NaN); nao ha problema de sensor em Picos
df = df.dropna(subset=[COL_VEL])


# ----------------------------------------------------------------------
# Montagem das faixas de 1 m/s (0-1, 1-2, ..., ate cobrir o maximo observado)
# ----------------------------------------------------------------------
vmax_global = df[df["Ano"].isin(ANOS)][COL_VEL].max()
limite_superior = int(np.ceil(vmax_global)) + 1
bins = np.arange(0, limite_superior + 1, 1)
labels = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(bins) - 1)]


def montar_tabela_distribuicao(velocidades):
    faixas = pd.cut(velocidades, bins=bins, labels=labels, right=False, include_lowest=True)
    contagem = faixas.value_counts().reindex(labels, fill_value=0)
    total = contagem.sum()
    freq_relativa = (contagem / total * 100).round(2)

    tabela = pd.DataFrame({
        "Velocidade do Vento (m/s)": labels,
        "N. de Ocorrencias": contagem.values,
        "Frequencia Relativa (%)": freq_relativa.values,
    })
    return tabela


tabelas = {}
for ano in ANOS:
    velocidades_ano = df.loc[df["Ano"] == ano, COL_VEL]
    tabela = montar_tabela_distribuicao(velocidades_ano)
    tabelas[ano] = tabela

    caminho = os.path.join(OUT_DIR, f"tabela_distribuicao_{ano}.csv")
    tabela.to_csv(caminho, sep=";", decimal=",", index=False)
    print(f"\nDistribuicao de frequencia - Picos {ano} (n = {velocidades_ano.count()} registros)")
    print(tabela.to_string(index=False))


# ----------------------------------------------------------------------
# Tabela comparativa (2019 x 2024 lado a lado)
# ----------------------------------------------------------------------
tabela_comparativa = pd.DataFrame({"Velocidade do Vento (m/s)": labels})
for ano in ANOS:
    tabela_comparativa[f"Ocorrencias {ano}"] = tabelas[ano]["N. de Ocorrencias"].values
    tabela_comparativa[f"Freq. Relativa {ano} (%)"] = tabelas[ano]["Frequencia Relativa (%)"].values

caminho_comp = os.path.join(OUT_DIR, "tabela_distribuicao_comparativa.csv")
tabela_comparativa.to_csv(caminho_comp, sep=";", decimal=",", index=False)
print("\nTabela comparativa salva em:", caminho_comp)


# ----------------------------------------------------------------------
# Histograma comparativo (barras lado a lado, 2019 x 2024)
# ----------------------------------------------------------------------
x = np.arange(len(labels))
largura = 0.4

plt.figure(figsize=(12, 6))
plt.bar(x - largura / 2, tabelas[ANOS[0]]["Frequencia Relativa (%)"],
        width=largura, label=str(ANOS[0]), color="steelblue", edgecolor="black")
plt.bar(x + largura / 2, tabelas[ANOS[1]]["Frequencia Relativa (%)"],
        width=largura, label=str(ANOS[1]), color="darkorange", edgecolor="black")

plt.xticks(x, labels, rotation=45)
plt.xlabel("Velocidade do Vento (m/s)")
plt.ylabel("Frequencia da distribuicao (%)")
plt.title("Distribuicao de frequencia da velocidade do vento - Picos/PI\n"
          f"Comparativo {ANOS[0]} x {ANOS[1]}")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

caminho_hist = os.path.join(OUT_DIR, "histograma_2019_vs_2024.png")
plt.savefig(caminho_hist, dpi=150)
plt.close()
print(f"\nHistograma salvo em: {caminho_hist}")
print(f"\nTodos os resultados da Tarefa 4 foram salvos em: {OUT_DIR}")