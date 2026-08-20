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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "banco-de-dados")
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa4")
os.makedirs(OUT_DIR, exist_ok=True)

CAMINHO_PICOS = os.path.join(DATA_DIR, "picos.csv")

# Usando a velocidade a 50m (WS50M) para o histograma de potencial eolico.
# Se quiser replicar estritamente o relatorio antigo, mude para "WS10M".
COL_VEL = "WS50M" 

ANOS = [2019, 2024]

df = pd.read_csv(CAMINHO_PICOS, skiprows=11, na_values=[-999.0, -999])

# Cria o indice temporal a partir das colunas da NASA para extrair o ano
df["datetime"] = pd.to_datetime({
    "year": df["YEAR"],
    "month": df["MO"],
    "day": df["DY"],
    "hour": df["HR"]
})
df["Ano"] = df["datetime"].dt.year

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
    # Filtra os dados do ano especifico e remove possiveis falhas (NaN) da NASA
    velocidades_ano = df.loc[df["Ano"] == ano, COL_VEL].dropna()
    tabela = montar_tabela_distribuicao(velocidades_ano)
    tabelas[ano] = tabela

    caminho = os.path.join(OUT_DIR, f"tabela_distribuicao_{ano}.csv")
    tabela.to_csv(caminho, sep=";", decimal=",", index=False)
    print(f"\nDistribuicao de frequencia - Picos {ano} (n = {velocidades_ano.count()} registros)")
    print(tabela.to_string(index=False))


tabela_comparativa = pd.DataFrame({"Velocidade do Vento (m/s)": labels})
for ano in ANOS:
    tabela_comparativa[f"Ocorrencias {ano}"] = tabelas[ano]["N. de Ocorrencias"].values
    tabela_comparativa[f"Freq. Relativa {ano} (%)"] = tabelas[ano]["Frequencia Relativa (%)"].values

caminho_comp = os.path.join(OUT_DIR, "tabela_distribuicao_comparativa.csv")
tabela_comparativa.to_csv(caminho_comp, sep=";", decimal=",", index=False)
print("\nTabela comparativa salva em:", caminho_comp)


x = np.arange(len(labels))
largura = 0.85 # Barras mais largas já que os graficos nao estao mais dividindo espaco

# Dicionario de cores para manter o padrao visual anterior
cores = {2019: "steelblue", 2024: "darkorange"}

for ano in ANOS:
    plt.figure(figsize=(10, 6))
    
    # Plota apenas as barras do ano atual no loop
    plt.bar(x, tabelas[ano]["Frequencia Relativa (%)"],
            width=largura, color=cores[ano], edgecolor="black")

    plt.xticks(x, labels, rotation=45)
    plt.xlabel(f"Velocidade do Vento a 50m (m/s)")
    plt.ylabel("Frequencia da distribuicao (%)")
    plt.title(f"Distribuicao de frequencia da velocidade do vento - Picos/PI ({ano})")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    caminho_hist = os.path.join(OUT_DIR, f"histograma_{ano}.png")
    plt.savefig(caminho_hist, dpi=150)
    plt.close()
    
    print(f"Histograma isolado de {ano} salvo em: {caminho_hist}")

print(f"\nTodos os resultados da Tarefa 4 foram salvos em: {OUT_DIR}")