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

COL_VEL = "VENTO, VELOCIDADE HORARIA(m/s)"

ANO_INICIO, ANO_FIM = 2016, 2019

# funcao de leitura e extrapolacao para o NaN
def carregar_serie(caminho_csv, ano_inicio=None, ano_fim=None):
    df = pd.read_csv(caminho_csv, sep=";", skiprows=9, encoding="utf-8")
    df["Hora Medicao"] = df["Hora Medicao"].astype(str).str.zfill(4)
    df["datetime"] = pd.to_datetime(
        df["Data Medicao"] + " " + df["Hora Medicao"].str[:2] + ":00",
        format="%Y-%m-%d %H:%M",
    )
    df = df.set_index("datetime").sort_index()
    serie = df[COL_VEL]

    if ano_inicio is not None and ano_fim is not None:
        serie = serie[(serie.index.year >= ano_inicio) & (serie.index.year <= ano_fim)]

    # preenche as falhas (NaN) por interpolacao temporal antes de calcular medias
    serie = serie.interpolate(method="time", limit_direction="both")
    return serie


# series recortadas ao periodo comum e confiavel (2016-2019), usadas em 3.1 e 3.2
series = {
    nome: carregar_serie(os.path.join(DATA_DIR, arq), ANO_INICIO, ANO_FIM)
    for nome, arq in ARQUIVOS.items()
}

# serie completa de Picos (estacao "Operante", sem o problema de Barreiras),
# usada isoladamente na tarefa 3.3 (perfil vertical / variacao horaria)
serie_picos_completa = carregar_serie(os.path.join(DATA_DIR, ARQUIVOS["Picos"]))

# 3.1 VELOCIDADE MEDIA ANUAL (Equacao 8: V = (1/n) * soma(vi))

tabela_anual = pd.DataFrame({
    nome: serie.groupby(serie.index.year).mean()
    for nome, serie in series.items()
})
tabela_anual.index.name = "Ano"

caminho_csv_anual = os.path.join(OUT_DIR, "velocidade_media_anual.csv")
tabela_anual.round(3).to_csv(caminho_csv_anual, sep=";", decimal=",")
print("Velocidade media anual [m/s]:")
print(tabela_anual.round(3))

plt.figure(figsize=(9, 5))
for nome in ARQUIVOS:
    plt.plot(tabela_anual.index, tabela_anual[nome], marker="o", label=nome)
plt.xlabel("Ano")
plt.ylabel("Velocidade media do vento [m/s]")
plt.title(f"Variacao da velocidade media anual do vento ({ANO_INICIO}-{ANO_FIM})\n"
          f"Periodo restrito ao intervalo confiavel comum (ver nota sobre Barreiras)")
plt.xticks(tabela_anual.index)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "velocidade_media_anual.png"), dpi=150)
plt.close()

# 3.2 VARIACAO SAZONAL - media mensal, mesmo periodo, 3 localidades

tabela_sazonal = pd.DataFrame({
    nome: serie.groupby(serie.index.month).mean()
    for nome, serie in series.items()
})
tabela_sazonal.index.name = "Mes"

caminho_csv_sazonal = os.path.join(OUT_DIR, "variacao_sazonal.csv")
tabela_sazonal.round(3).to_csv(caminho_csv_sazonal, sep=";", decimal=",")
print("\nVariacao sazonal (media mensal) [m/s]:")
print(tabela_sazonal.round(3))

plt.figure(figsize=(9, 5))
for nome in ARQUIVOS:
    plt.plot(tabela_sazonal.index, tabela_sazonal[nome], marker="o", label=nome)
plt.xlabel("Mes")
plt.ylabel("Velocidade media do vento [m/s]")
plt.title(f"Variacao sazonal do vento - periodo {ANO_INICIO}-{ANO_FIM}")
plt.xticks(range(1, 13))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "variacao_sazonal.png"), dpi=150)
plt.close()


# 3.3 PERFIL VERTICAL (LEI DE HELLMANN) - Picos, 2 alturas, variacao horaria

H1 = 10.0    # altura de referencia (anemometro da estacao INMET) [m]
H2 = 50.0    # altura de interesse (ex.: altura de cubo do aerogerador) [m]
ALFA = 0.14  # coeficiente de Hellmann para terreno aberto

serie_picos = serie_picos_completa  # usa toda a serie disponivel de Picos (2016-2025)
media_horaria = serie_picos.groupby(serie_picos.index.hour).mean()  # v em H1 = 10 m

# Lei de Hellmann: v2 = v1 * (h2/h1)^alfa 

media_horaria_h2 = media_horaria * (H2 / H1) ** ALFA

tabela_perfil = pd.DataFrame({
    f"v a {H1:.0f}m [m/s]": media_horaria,
    f"v a {H2:.0f}m [m/s]": media_horaria_h2,
})
tabela_perfil.index.name = "Hora"

caminho_csv_perfil = os.path.join(OUT_DIR, "perfil_vertical_picos.csv")
tabela_perfil.round(3).to_csv(caminho_csv_perfil, sep=";", decimal=",")
print(f"\nVariacao horaria - Picos, {H1:.0f}m x {H2:.0f}m (Lei de Hellmann, alfa={ALFA}):")
print(tabela_perfil.round(3))

plt.figure(figsize=(9, 5))
plt.plot(tabela_perfil.index, tabela_perfil[f"v a {H1:.0f}m [m/s]"],
         marker="o", label=f"{H1:.0f} m (medido)")
plt.plot(tabela_perfil.index, tabela_perfil[f"v a {H2:.0f}m [m/s]"],
         marker="s", label=f"{H2:.0f} m (Lei de Hellmann, alfa={ALFA})")
plt.xlabel("Hora do dia")
plt.ylabel("Velocidade media do vento [m/s]")
plt.title(f"Variacao da velocidade media horaria - Picos/PI ({H1:.0f}m x {H2:.0f}m)")
plt.xticks(range(0, 24))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "perfil_vertical_picos.png"), dpi=150)
plt.close()

print(f"\nTodos os resultados da Tarefa 3 foram salvos em: {OUT_DIR}")