"""
TAREFA 2 - energia eolica
massa especifica do ar em funcao da altitude e da temperatura ambiente
equacao (7) do slide:

    ro = 353.4 * (1 - z/45271)^5.2624 / (273.15 + T)

em que:
    z = altitude do local [m]  -> intervalo pedido: 0 a 1000 m
    T = temperatura ambiente [C] -> intervalo pedido: -5 a 30 C
    obs: esses intervalos estao de acordo com a tabela exibida no slide

alem da tabela completa (replicando a Tabela 2.1 do livro), plotar um
grafico especifico para a altitude de Picos (z = 232.91 m), variando T,
com destaque para o ponto T = 25 C (que seria a temperatura ambiente).

saidas
    tabela_massa_especifica.csv   -> tabela z (linhas) x T (colunas)
    grafico_massa_especifica_3d.png -> visao geral da equacao (z, T, ro)
    grafico_picos_232m.png        -> ro x T para z = 232.91 m, destacando T = 25 C, que é a regiao que eu escolhi para o decorrer da disciplina, picos.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de caminhos baseados na estrutura do seu projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa2")
os.makedirs(OUT_DIR, exist_ok=True)

# Aplica um tema visual limpo e profissional
sns.set_theme(style="whitegrid", palette="deep")

def calcular_rho(z, T):
    return (353.4 * (1 - (z / 45271))**5.2624) / (273.15 + T)

# --- 1. Tabela e Gráfico Geral ---
# Limites de acordo com a Tabela 2.1 do livro
altitudes = np.arange(0, 1001, 100)
temperaturas = np.arange(-5, 31, 5)

dados = {f"{T}°C": [calcular_rho(z, T) for z in altitudes] for T in temperaturas}
tabela_rho = pd.DataFrame(dados, index=altitudes)
tabela_rho.index.name = "Altitude [m]"

# SALVANDO A TABELA
caminho_tabela = os.path.join(OUT_DIR, 'tarefa2_tabela_massa_especifica.csv')
tabela_rho.round(3).to_csv(caminho_tabela, sep=";", decimal=",")
print(f"Tabela da Tarefa 2 salva em: {caminho_tabela}")

# PLOTANDO O GRÁFICO GERAL
plt.figure(figsize=(10, 6))
for T in temperaturas:
    sns.lineplot(x=tabela_rho.index, y=tabela_rho[f"{T}°C"], label=f"{T}°C", marker='o')

plt.title('Massa Específica do Ar em função da Altitude e Temperatura', fontsize=14, weight='bold', pad=15)
plt.xlabel('Altitude (m)', fontsize=12)
plt.ylabel('Massa Específica do Ar (kg/m³)', fontsize=12)
plt.legend(title="Temperatura", bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)
plt.tight_layout()

# SALVANDO O GRÁFICO GERAL
caminho_geral = os.path.join(OUT_DIR, 'tarefa2_grafico_geral.png')
plt.savefig(caminho_geral, dpi=300)
plt.close()

# --- 2. Gráfico Específico para Picos (NASA) ---
# z = 406.51m extraído do cabeçalho do CSV MERRA-2
z_picos = 406.51 
t_picos = 25

temps_picos = np.linspace(-5, 35, 100)
rho_picos_var = [calcular_rho(z_picos, t) for t in temps_picos]
rho_ponto_exato = calcular_rho(z_picos, t_picos)

plt.figure(figsize=(8, 5))
sns.lineplot(x=temps_picos, y=rho_picos_var, color='#2c3e50', label=f'Altitude Picos NASA ({z_picos} m)', linewidth=2)
plt.plot(t_picos, rho_ponto_exato, marker='o', color='#e74c3c', markersize=8, label=f'Ponto {t_picos}°C: {rho_ponto_exato:.4f} kg/m³')

# Pequena anotação para destacar o valor no gráfico
plt.annotate(f"({t_picos}°C, {rho_ponto_exato:.4f})",
             xy=(t_picos, rho_ponto_exato),
             xytext=(t_picos + 2, rho_ponto_exato + 0.005),
             arrowprops=dict(arrowstyle="->", color="black"))

plt.title('Variação da Massa Específica - Picos/PI (MERRA-2)', fontsize=14, weight='bold', pad=15)
plt.xlabel('Temperatura (°C)', fontsize=12)
plt.ylabel('Massa Específica do Ar (kg/m³)', fontsize=12)
plt.legend(frameon=True, shadow=True)
plt.tight_layout()

caminho_picos = os.path.join(OUT_DIR, 'tarefa2_grafico_picos.png')
plt.savefig(caminho_picos, dpi=300)
plt.close()

print(f"Gráficos da Tarefa 2 salvos na pasta: {OUT_DIR}")