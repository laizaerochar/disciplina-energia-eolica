"""
TAREFA 12 - Energia Eolica (Aula 07)
"Os alunos irao fazer a tabela anterior para duas localidades e dois anos
diferentes e para 1 aerogerador diferente"

A "tabela anterior" (slide da Aula 07) tem o formato:

    Velocidade do vento (m/s) | Frequencia de ocorrencia (%) | Potencia do
    aerogerador (kW) | f(v).P(v)

e a energia anual gerada (EAG) por um aerogerador e dada por (slide):

    EAG = SOMA[f(v) . P(v)] * 8760                                   (kWh)

onde:
    f(v) = frequencia de ocorrencia da velocidade do vento v [%]
    P(v) = potencia produzida pelo aerogerador na velocidade v [kW]
    v    = velocidade do vento [m/s]

------------------------------------------------------------------------
SOBRE O AEROGERADOR UTILIZADO
------------------------------------------------------------------------
O enunciado pede explicitamente para usar os valores de POTENCIA REAIS
fornecidos pela FOLHA DE DADOS (datasheet) de um aerogerador -- ou seja,
uma tabela de fabricante (velocidade -> potencia), e nao uma formula
idealizada.

Este script usa a curva de potencia REAL e PUBLICADA de uma turbina
classe 1,5 MW, extraida da Tabela 13-3 / Figura 13-14 do livro-texto:

    MASTERS, Gilbert M. Renewable and Efficient Electric Power Systems.
    2nd ed. Wiley, 2013.

que e uma referencia classica e amplamente adotada em cursos de energia
renovavel, contendo o levantamento discreto de potencia por faixa de
velocidade do vento medido em ensaio de campo (nao e um ajuste
matematico teorico como Betz/idealizado). Os valores de potencia POR
FAIXA DE VELOCIDADE INTEIRA (m/s), conforme a tabela original do livro,
sao:

    Velocidade [m/s] | Potencia [kW]
    0 - 2            | 0      (abaixo do cut-in, ~3 m/s)
    3                | 14
    4                | 60
    5                | 155
    6                | 269
    7                | 420
    8                | 625
    9                | 900
    10               | 1195
    11               | 1395
    12               | 1485
    13 - 20          | 1500   (patamar de potencia nominal/rated)
    >= 21            | 0      (cut-out)

CASO O PROFESSOR TENHA ESPECIFICADO OUTRO AEROGERADOR (com tabela de
potencia de catalogo de outro fabricante), basta substituir o dicionario
TABELA_POTENCIA_TURBINA abaixo pelos valores da folha de dados
correspondente -- toda a logica de calculo da tabela e da EAG permanece
identica.

Dado de vento utilizado: WS50M (velocidade do vento a 50m, NASA
POWER/MERRA-2), mesma variavel usada nas Tarefas 4, 5, 6, 7 e 8, para
consistencia entre todas as analises deste projeto.

Localidades: Picos/PI e Fortaleza/CE (mesmas 2 localidades da Tarefa 5/6/7/8)
Anos: 2019 e 2024 (mesmos 2 anos das tarefas anteriores)

Saidas (salvas em ../resultados/tarefa12/):
    tabela_eag_picos_2019.csv
    tabela_eag_picos_2024.csv
    tabela_eag_fortaleza_2019.csv
    tabela_eag_fortaleza_2024.csv
    resumo_eag.csv (EAG consolidada das 4 combinacoes)
    curva_potencia_turbina_1500kW.png (grafico da curva de potencia utilizada)
    distribuicao_x_potencia_picos_2019.png (e demais combinacoes)
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
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa12")
os.makedirs(OUT_DIR, exist_ok=True)

LOCALIDADES = {"Picos": "picos.csv", "Fortaleza": "fortaleza.csv"}
COL_VEL = "WS50M"
ANOS = [2019, 2024]

HORAS_POR_ANO = 8760  # conforme formula do slide (EAG = soma[f(v).P(v)] * 8760)

# ----------------------------------------------------------------------
# Curva de potencia REAL do aerogerador (dados de folha de dados/datasheet)
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
    # 21 m/s em diante: cut-out (turbina desliga) -> potencia zero
}
V_CUT_OUT = 21  # [m/s], acima disso a folha de dados nao define potencia (cut-out)


def potencia_turbina(v):
    """
    Retorna a potencia do aerogerador (kW) para uma velocidade inteira de
    vento (m/s), consultando DIRETAMENTE a tabela de fabricante (nao usa
    nenhuma formula/interpolacao) -- conforme pedido no enunciado.
    """
    v_int = int(round(float(v)))
    if v_int >= V_CUT_OUT:
        return 0.0
    return TABELA_POTENCIA_TURBINA.get(v_int, 0.0)


def potencia_turbina_vetorial(v_array):
    return np.array([potencia_turbina(v) for v in np.atleast_1d(v_array)])



# ----------------------------------------------------------------------
# Leitura dos dados (padrao NASA POWER, igual as tarefas anteriores)
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
# Grafico da curva de potencia utilizada (documentacao/verificacao visual)
# Como a tabela do fabricante so define potencia em velocidades inteiras,
# o grafico conecta os pontos reais da tabela com retas (pratica usual
# para visualizar uma curva de datasheet), sem inventar nenhum valor
# intermediario nao fornecido pela fonte.
# ----------------------------------------------------------------------
v_tabela = sorted(TABELA_POTENCIA_TURBINA.keys())
p_tabela = [TABELA_POTENCIA_TURBINA[v] for v in v_tabela]
# adiciona o ponto de cut-out explicitamente, para deixar claro no grafico
v_tabela_plot = v_tabela + [V_CUT_OUT]
p_tabela_plot = p_tabela + [0.0]

plt.figure(figsize=(8, 5))
plt.plot(v_tabela_plot, p_tabela_plot, color="darkblue", linewidth=2, marker="o", markersize=4)
plt.axvline(3, color="gray", linestyle="--", linewidth=1, label="Cut-in (~3 m/s)")
plt.axvline(13, color="green", linestyle="--", linewidth=1, label="Inicio do patamar nominal (13 m/s)")
plt.axvline(V_CUT_OUT, color="red", linestyle="--", linewidth=1, label=f"Cut-out ({V_CUT_OUT} m/s)")
plt.title(f"Curva de potencia real (datasheet) - Turbina 1500 kW", fontsize=12)
plt.xlabel("Velocidade do vento v [m/s]")
plt.ylabel("Potencia P(v) [kW]")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
caminho_curva = os.path.join(OUT_DIR, "curva_potencia_turbina_1500kW.png")
plt.savefig(caminho_curva, dpi=150)
plt.close()
print(f"Grafico da curva de potencia salvo em: {caminho_curva}\n")


# ----------------------------------------------------------------------
# Processamento principal: para cada localidade e ano, monta a tabela
# (v, f(v)%, P(v), f(v).P(v)) e calcula a EAG
# ----------------------------------------------------------------------
resumo_eag = []

for nome_local, arquivo in LOCALIDADES.items():
    df = carregar_dataframe(os.path.join(DATA_DIR, arquivo))

    for ano in ANOS:
        velocidades = df.loc[df["Ano"] == ano, COL_VEL].dropna()
        n_total = len(velocidades)

        # arredonda cada observacao para o inteiro mais proximo (m/s),
        # reproduzindo o formato de tabela do slide (velocidades inteiras)
        v_arredondada = velocidades.round().astype(int)

        contagem = v_arredondada.value_counts().sort_index()
        freq_pct = (contagem / n_total * 100)

        tabela = pd.DataFrame({
            "Velocidade_do_vento_m_s": freq_pct.index,
            "Frequencia_ocorrencia_%": freq_pct.values.round(3),
        })
        tabela["Potencia_aerogerador_kW"] = potencia_turbina_vetorial(tabela["Velocidade_do_vento_m_s"].values).round(3)
        tabela["f(v).P(v)"] = (tabela["Frequencia_ocorrencia_%"] / 100 * tabela["Potencia_aerogerador_kW"]).round(5)

        soma_fv_pv = tabela["f(v).P(v)"].sum()
        eag = soma_fv_pv * HORAS_POR_ANO  # kWh/ano

        # linha de TOTAL, igual ao exemplo do slide
        linha_total = pd.DataFrame([{
            "Velocidade_do_vento_m_s": "TOTAL",
            "Frequencia_ocorrencia_%": round(tabela["Frequencia_ocorrencia_%"].sum(), 3),
            "Potencia_aerogerador_kW": "",
            "f(v).P(v)": round(soma_fv_pv, 5),
        }])
        tabela_final = pd.concat([tabela, linha_total], ignore_index=True)

        nome_arquivo = f"tabela_eag_{nome_local.lower()}_{ano}.csv"
        caminho_tabela = os.path.join(OUT_DIR, nome_arquivo)
        tabela_final.to_csv(caminho_tabela, sep=";", decimal=",", index=False)

        print(f"=== {nome_local} - {ano} (aerogerador: {NOME_TURBINA}) ===")
        print(tabela_final.to_string(index=False))
        print(f"Soma f(v).P(v) = {soma_fv_pv:.5f} kW  |  EAG = {eag:,.2f} kWh/ano\n")

        resumo_eag.append({
            "Localidade": nome_local, "Ano": ano, "Aerogerador": NOME_TURBINA,
            "Soma_fv_Pv_kW": round(soma_fv_pv, 5), "EAG_kWh_ano": round(eag, 2),
        })

        # ---- grafico de verificacao: histograma de frequencia + curva P(v) ----
        fig, ax1 = plt.subplots(figsize=(9, 6))
        cores_barras = "steelblue"
        ax1.bar(tabela["Velocidade_do_vento_m_s"], tabela["Frequencia_ocorrencia_%"],
                color=cores_barras, edgecolor="black", alpha=0.7, label="Frequencia de ocorrencia (%)")
        ax1.set_xlabel("Velocidade do vento v [m/s]")
        ax1.set_ylabel("Frequencia de ocorrencia [%]", color=cores_barras)
        ax1.tick_params(axis="y", labelcolor=cores_barras)

        ax2 = ax1.twinx()
        v_max_local = int(tabela["Velocidade_do_vento_m_s"].max()) + 2
        v_pontos = list(range(0, v_max_local + 1))
        p_pontos = [potencia_turbina(v) for v in v_pontos]
        ax2.plot(v_pontos, p_pontos, color="darkorange", linewidth=2.2, marker="o", markersize=3,
                 label=f"Curva de potencia real ({NOME_TURBINA})")
        ax2.set_ylabel("Potencia do aerogerador P(v) [kW]", color="darkorange")
        ax2.tick_params(axis="y", labelcolor="darkorange")

        plt.title(f"Distribuicao de frequencia x Curva de potencia - {nome_local} ({ano})\n"
                  f"EAG = {eag:,.0f} kWh/ano")
        fig.tight_layout()

        nome_fig = f"distribuicao_x_potencia_{nome_local.lower()}_{ano}.png"
        caminho_fig = os.path.join(OUT_DIR, nome_fig)
        plt.savefig(caminho_fig, dpi=150)
        plt.close()
        print(f"Grafico salvo: {caminho_fig}\n")


# ----------------------------------------------------------------------
# Tabela resumo consolidada (EAG das 4 combinacoes)
# ----------------------------------------------------------------------
tabela_resumo = pd.DataFrame(resumo_eag)
caminho_resumo = os.path.join(OUT_DIR, "resumo_eag.csv")
tabela_resumo.to_csv(caminho_resumo, sep=";", decimal=",", index=False)

print("=== RESUMO FINAL - Energia Anual Gerada (EAG) ===")
print(tabela_resumo.to_string(index=False))
print(f"\nTabela resumo salva em: {caminho_resumo}")
print(f"\nTodos os resultados da Tarefa 12 foram salvos em: {OUT_DIR}")