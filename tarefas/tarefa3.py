"""
TAREFA 3 - energia eolica
velocidade do vento: variacao anual, sazonal e perfil vertical (2 alturas)

fonte dos dados: INMET, estacoes de Fortaleza(A305), Barreiras(A402) e
Picos(A343), medicoes horarias de 2016-01-01 a 2025-12-31 (10 anos).
coluna usada: "VENTO, VELOCIDADE HORARIA(m/s)"

3.1) Velocidade media anual (Eq. 8 do slide) das 3 localidades, mesmo grafico
3.2) Variacao sazonal (media mensal) das 3 localidades, mesmo periodo, mesmo grafico

NOTA SOBRE QUALIDADE DOS DADOS (Barreiras/A402):
    A estacao de Barreiras esta com "Situacao: Pane" no cabecalho do CSV.
    A partir de 2020 a maioria das leituras de velocidade do vento fica
    zerada (~95% dos registros = 0.0 m/s em 2023), o que e uma falha real
    de sensor, e nao um dado ausente (NaN) que a interpolacao resolveria.
    Por isso, para as tarefas 3.1 e 3.2, adota-se o PERIODO COMUM E
    CONFIAVEL das 3 estacoes: 2016-2019 (4 anos), em vez dos 10 anos
    originalmente disponiveis no arquivo, e dos 2 anos solicitados no enunciado, tendo em vista que a manipulação dos dados teve uma interferencia dada a falha nos dados postados pelo INMET, e uma vez que o tempo foi limitado, optei por não procurar uma 4 localidade para substituição. A tarefa 3.3 (perfil vertical em
    Picos) nao e afetada, pois usa apenas a estacao de Picos (Operante).
3.3) Picos: variacao da velocidade media horaria ao longo do dia, para 2 alturas
     diferentes, obtidas por extrapolacao via LEI DE HELLMANN (perfil de vento
     exponencial):

        v2 = v1 * (h2 / h1) ^ alfa

     h1 = altura de referencia do anemometro da estacao (10 m, padrao INMET)
     h2 = altura de interesse (ex.: altura de cubo de aerogerador)
     alfa = coeficiente de Hellmann (0.14 -> terreno aberto, valor padrao
            adotado na ausencia de medicao de rugosidade do local)
OBS; essa lei representa uma EXTRAPOLAÇÃO, novamente, não se tinha esse segundo dado de altura, e para modelar esses dados a IA sugeriu a utilizacao dessa lei.

Saidas (salvas em ../resultados/tarefa3/):
    velocidade_media_anual.png
    velocidade_media_anual.csv
    variacao_sazonal.png
    variacao_sazonal.csv
    perfil_vertical_picos.png
    perfil_vertical_picos.csv
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "banco-de-dados")
OUT_DIR = os.path.join(BASE_DIR, "resultados", "tarefa3")
os.makedirs(OUT_DIR, exist_ok=True)

ARQUIVOS = {
    "Fortaleza": "fortaleza.csv",
    "Barreiras": "barreiras.csv",
    "Picos": "picos.csv",
}

ANO_INICIO, ANO_FIM = 2016, 2019

# funcao de leitura atualizada para o padrao NASA POWER
def carregar_dataframe(caminho_csv, ano_inicio=None, ano_fim=None):
    # skiprows=11 pula o cabecalho de texto, na_values mapeia os -999 da NASA como falha
    df = pd.read_csv(caminho_csv, skiprows=11, na_values=[-999.0, -999])
    
    # Cria o indice temporal agrupando as 4 colunas da NASA
    df["datetime"] = pd.to_datetime({
        "year": df["YEAR"],
        "month": df["MO"],
        "day": df["DY"],
        "hour": df["HR"]
    })
    df = df.set_index("datetime").sort_index()
    
    # Preenche eventuais falhas por interpolacao temporal (raro no MERRA-2, mas boa pratica)
    df = df.interpolate(method="time", limit_direction="both")

    # Filtro de anos para comparacoes padronizadas
    if ano_inicio is not None and ano_fim is not None:
        df = df[(df.index.year >= ano_inicio) & (df.index.year <= ano_fim)]
        
    return df

# Dicionario armazenando os DataFrames completos do periodo comum
dataframes = {
    nome: carregar_dataframe(os.path.join(DATA_DIR, arq), ANO_INICIO, ANO_FIM)
    for nome, arq in ARQUIVOS.items()
}

# DataFrame completo de Picos para a tarefa 3.3 (2016-2025)
df_picos_completo = carregar_dataframe(os.path.join(DATA_DIR, ARQUIVOS["Picos"]))

tabela_anual = pd.DataFrame({
    nome: df["WS10M"].groupby(df.index.year).mean()
    for nome, df in dataframes.items()
})
tabela_anual.index.name = "Ano"

caminho_csv_anual = os.path.join(OUT_DIR, "velocidade_media_anual.csv")
tabela_anual.round(3).to_csv(caminho_csv_anual, sep=";", decimal=",")
print("Velocidade media anual a 10m [m/s]:")
print(tabela_anual.round(3))

plt.figure(figsize=(9, 5))
for nome in ARQUIVOS:
    plt.plot(tabela_anual.index, tabela_anual[nome], marker="o", label=nome)
plt.xlabel("Ano")
plt.ylabel("Velocidade media do vento [m/s]")
plt.title(f"Variacao da velocidade media anual do vento a 10m ({ANO_INICIO}-{ANO_FIM})")
plt.xticks(tabela_anual.index)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "velocidade_media_anual.png"), dpi=150)
plt.close()

tabela_sazonal = pd.DataFrame({
    nome: df["WS10M"].groupby(df.index.month).mean()
    for nome, df in dataframes.items()
})
tabela_sazonal.index.name = "Mes"

caminho_csv_sazonal = os.path.join(OUT_DIR, "variacao_sazonal.csv")
tabela_sazonal.round(3).to_csv(caminho_csv_sazonal, sep=";", decimal=",")
print("\nVariacao sazonal a 10m (media mensal) [m/s]:")
print(tabela_sazonal.round(3))

plt.figure(figsize=(9, 5))
for nome in ARQUIVOS:
    plt.plot(tabela_sazonal.index, tabela_sazonal[nome], marker="o", label=nome)
plt.xlabel("Mes")
plt.ylabel("Velocidade media do vento [m/s]")
plt.title(f"Variacao sazonal do vento a 10m - periodo {ANO_INICIO}-{ANO_FIM}")
plt.xticks(range(1, 13))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "variacao_sazonal.png"), dpi=150)
plt.close()

# Extraindo as medias diretamente das colunas da NASA
media_horaria_10m = df_picos_completo["WS10M"].groupby(df_picos_completo.index.hour).mean()
media_horaria_50m = df_picos_completo["WS50M"].groupby(df_picos_completo.index.hour).mean()

tabela_perfil = pd.DataFrame({
    "v a 10m (real NASA) [m/s]": media_horaria_10m,
    "v a 50m (real NASA) [m/s]": media_horaria_50m,
})
tabela_perfil.index.name = "Hora"

caminho_csv_perfil = os.path.join(OUT_DIR, "perfil_vertical_picos.csv")
tabela_perfil.round(3).to_csv(caminho_csv_perfil, sep=";", decimal=",")
print("\nVariacao horaria - Picos (10m x 50m NASA):")
print(tabela_perfil.round(3))

plt.figure(figsize=(9, 5))
plt.plot(tabela_perfil.index, tabela_perfil["v a 10m (real NASA) [m/s]"],
         marker="o", label="10 m (Real NASA)")
plt.plot(tabela_perfil.index, tabela_perfil["v a 50m (real NASA) [m/s]"],
         marker="s", label="50 m (Real NASA)")
plt.xlabel("Hora do dia")
plt.ylabel("Velocidade media do vento [m/s]")
plt.title("Variacao da velocidade media horaria - Picos/PI (10m x 50m Dados Reais)")
plt.xticks(range(0, 24))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "perfil_vertical_picos.png"), dpi=150)
plt.close()

print(f"\nTodos os resultados da Tarefa 3 foram salvos em: {OUT_DIR}")