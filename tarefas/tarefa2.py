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

# config d caminhos 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa2")
os.makedirs(OUT_DIR, exist_ok=True)

# eq (7) do slide
def massa_especifica(z, T):
    return 353.4 * (1 - z / 45271) ** 5.2624 / (273.15 + T)

# 1) TABELA - replica a do slide (z de 0 a 1000, passo 100) e (T de -5 a 30, passo 5)
altitudes = np.arange(0, 1001, 100)      # 0, 100, ..., 1000 m
temperaturas = np.arange(-5, 31, 5)      # -5, 0, 5, ..., 30 C

tabela = pd.DataFrame(
    index=altitudes,
    columns=[f"{t}C" for t in temperaturas],
    dtype=float,
)

for z in altitudes:
    for T in temperaturas:
        tabela.loc[z, f"{T}C"] = round(massa_especifica(z, T), 3)

tabela.index.name = "Altitude [m]"

caminho_tabela = os.path.join(OUT_DIR, "tabela_massa_especifica.csv")
tabela.to_csv(caminho_tabela, sep=";", decimal=",")
print(f"Tabela salva em: {caminho_tabela}")
print(tabela)


# grafico 3d p visualizacao geral da equacao, com heatmap de cores tb 
Z, Tg = np.meshgrid(altitudes, temperaturas)
ro = massa_especifica(Z, Tg)

fig = plt.figure(figsize=(9, 6))
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(Z, Tg, ro, cmap="viridis", edgecolor="none", alpha=0.9)
ax.set_xlabel("Altitude z [m]")
ax.set_ylabel("Temperatura T [C]")
ax.set_zlabel("Massa especifica ro [kg/m3]")
ax.set_title("Massa especifica do ar - Equacao (7)")
plt.tight_layout()
caminho_3d = os.path.join(OUT_DIR, "grafico_massa_especifica_3d.png")
plt.savefig(caminho_3d, dpi=150)
plt.close()
print(f"Grafico 3D salvo em: {caminho_3d}")

# grafico especifico de picos 
z_picos = 232.91
T_range = np.linspace(-5, 30, 200)
ro_picos = massa_especifica(z_picos, T_range)

T_destaque = 25
ro_destaque = massa_especifica(z_picos, T_destaque)

plt.figure(figsize=(8, 5))
plt.plot(T_range, ro_picos, color="darkorange", linewidth=2,
         label=f"z = {z_picos} m (Picos-PI)")
plt.scatter([T_destaque], [ro_destaque], color="red", zorder=5,
            label=f"T = {T_destaque} C -> ro = {ro_destaque:.4f} kg/m3")
plt.annotate(f"({T_destaque}C, {ro_destaque:.4f})",
             xy=(T_destaque, ro_destaque),
             xytext=(T_destaque + 2, ro_destaque + 0.01),
             arrowprops=dict(arrowstyle="->", color="black"))
plt.xlabel("Temperatura ambiente T [C]")
plt.ylabel("Massa especifica do ar ro [kg/m3]")
plt.title("Massa especifica do ar - Picos/PI (Altitude = 232.91 m)")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
caminho_picos = os.path.join(OUT_DIR, "grafico_picos_232m.png")
plt.savefig(caminho_picos, dpi=150)
plt.close()
print(f"grafico de picos salvo em: {caminho_picos}")

print(f"\nValor pedido no enunciado -> ro(z=232.91m, T=25C) = {ro_destaque:.4f} kg/m3")