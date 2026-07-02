"""
gerar_imagens.py
----------------
Gera os graficos estaticos (Matplotlib + Seaborn) usados no README e no
notebook, salvando-os na pasta imagens/.

Uso:
    python gerar_imagens.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")            # backend sem interface grafica
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE_DIR, "dados", "mercado_ti.csv")
IMG = os.path.join(BASE_DIR, "imagens")
os.makedirs(IMG, exist_ok=True)

sns.set_theme(style="whitegrid", palette="viridis")

df = pd.read_csv(CSV, parse_dates=["data"])
df["salario_medio"] = df["salario_medio"].fillna(df["salario_medio"].median())


def salvar(fig, nome):
    caminho = os.path.join(IMG, nome)
    fig.tight_layout()
    fig.savefig(caminho, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {caminho}")


# 1) Evolucao de vagas por ano (analise temporal)
fig, ax = plt.subplots(figsize=(9, 4.5))
vagas_ano = df.groupby("ano")["quantidade_vagas"].sum()
sns.lineplot(x=vagas_ano.index, y=vagas_ano.values, marker="o", ax=ax, color="#2563eb")
ax.set_title("Evolucao do total de vagas de TI (2015-2024)")
ax.set_xlabel("Ano"); ax.set_ylabel("Total de vagas")
salvar(fig, "01_evolucao_vagas.png")

# 2) Salario medio por senioridade (boxplot)
fig, ax = plt.subplots(figsize=(8, 4.5))
sns.boxplot(data=df, x="senioridade", y="salario_medio",
            order=["Junior", "Pleno", "Senior"], ax=ax)
ax.set_title("Distribuicao salarial por senioridade")
ax.set_xlabel("Senioridade"); ax.set_ylabel("Salario medio (R$)")
salvar(fig, "02_salario_senioridade.png")

# 3) Top 10 tecnologias mais demandadas
fig, ax = plt.subplots(figsize=(9, 5))
top_tec = (df.groupby("tecnologia")["quantidade_vagas"].sum()
             .sort_values(ascending=False).head(10))
sns.barplot(x=top_tec.values, y=top_tec.index, ax=ax)
ax.set_title("Top 10 tecnologias mais demandadas")
ax.set_xlabel("Total de vagas"); ax.set_ylabel("")
salvar(fig, "03_top_tecnologias.png")

# 4) Vagas por regiao
fig, ax = plt.subplots(figsize=(8, 4.5))
reg = (df.groupby("regiao")["quantidade_vagas"].sum()
         .sort_values(ascending=False))
sns.barplot(x=reg.index, y=reg.values, ax=ax)
ax.set_title("Total de vagas por regiao")
ax.set_xlabel("Regiao"); ax.set_ylabel("Total de vagas")
salvar(fig, "04_vagas_regiao.png")

# 5) Evolucao da modalidade de trabalho (analise temporal comparativa)
fig, ax = plt.subplots(figsize=(9, 4.5))
mod = (df.groupby(["ano", "modalidade"])["quantidade_vagas"].sum()
         .reset_index())
sns.lineplot(data=mod, x="ano", y="quantidade_vagas",
             hue="modalidade", marker="o", ax=ax)
ax.set_title("Evolucao das modalidades de trabalho")
ax.set_xlabel("Ano"); ax.set_ylabel("Total de vagas")
salvar(fig, "05_modalidade_tempo.png")

# 6) Mapa de correlacao (funcionalidade avancada: correlacao estatistica)
fig, ax = plt.subplots(figsize=(6.5, 5))
num = df[["ano", "mes", "salario_medio", "quantidade_vagas"]].corr()
sns.heatmap(num, annot=True, cmap="coolwarm", fmt=".2f", ax=ax,
            vmin=-1, vmax=1, linewidths=.5)
ax.set_title("Matriz de correlacao (variaveis numericas)")
salvar(fig, "06_correlacao.png")

print("\nTodos os graficos foram gerados em imagens/")
