"""
app.py — Dashboard interativo: Mercado de Trabalho em TI no Brasil (2015–2024)
==============================================================================
Disciplina: Linguagem de Programação — Análise e Visualização de Dados com Python
Autor: Danilo

Como rodar localmente:
    streamlit run app.py

Tecnologias: Python, Pandas, Matplotlib, Seaborn, Plotly, Streamlit, SQLAlchemy (SQLite).
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

# ---------------------------------------------------------------------------
# Configuracao da pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Mercado de TI no Brasil",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid", palette="viridis")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DB = os.path.join(BASE_DIR, "database", "mercado_ti.db")
CAMINHO_CSV = os.path.join(BASE_DIR, "dados", "mercado_ti.csv")


# ---------------------------------------------------------------------------
# Garante que a base exista (gera CSV + SQLite caso os arquivos nao estejam
# no repositorio, ex.: deploy no Streamlit Cloud). Assim o app roda sozinho.
# ---------------------------------------------------------------------------
def garantir_base():
    if os.path.exists(CAMINHO_DB) or os.path.exists(CAMINHO_CSV):
        return
    try:
        from gerar_dados import gerar_base  # reaproveita o gerador do projeto
        base = gerar_base()
        os.makedirs(os.path.dirname(CAMINHO_CSV), exist_ok=True)
        os.makedirs(os.path.dirname(CAMINHO_DB), exist_ok=True)
        base.to_csv(CAMINHO_CSV, index=False)
        engine = create_engine(f"sqlite:///{CAMINHO_DB}")
        base.to_sql("vagas_ti", engine, if_exists="replace", index=False)
    except Exception as e:
        st.error(
            "Não foi possível localizar nem gerar a base de dados. "
            "Verifique se `dados/mercado_ti.csv` (ou `database/mercado_ti.db`) "
            f"e o arquivo `gerar_dados.py` estão no repositório.\n\nDetalhe: {e}"
        )
        st.stop()


# ---------------------------------------------------------------------------
# Carregamento dos dados (SQLite via SQLAlchemy, com fallback para CSV)
# ---------------------------------------------------------------------------
@st.cache_data
def carregar_dados() -> pd.DataFrame:
    garantir_base()

    if os.path.exists(CAMINHO_DB):
        engine = create_engine(f"sqlite:///{CAMINHO_DB}")
        df = pd.read_sql("SELECT * FROM vagas_ti", engine, parse_dates=["data"])
    else:
        df = pd.read_csv(CAMINHO_CSV, parse_dates=["data"])

    # Limpeza / preparacao
    df["salario_medio"] = df.groupby("senioridade")["salario_medio"].transform(
        lambda s: s.fillna(s.median())
    )
    df["data"] = pd.to_datetime(df["data"])

    # Engenharia de atributos
    df["faixa_salarial"] = pd.cut(
        df["salario_medio"],
        bins=[0, 4000, 8000, 12000, np.inf],
        labels=["Até 4k", "4k–8k", "8k–12k", "Acima de 12k"],
    )
    return df


df = carregar_dados()

# ---------------------------------------------------------------------------
# Sidebar: navegacao + filtros multiplos (interativos)
# ---------------------------------------------------------------------------
st.sidebar.title("💻 Mercado de TI")
st.sidebar.caption("Análise e Visualização de Dados — G2")

secao = st.sidebar.radio(
    "Navegação",
    ["🏠 Visão Geral", "💰 Análise Salarial", "📈 Análise Temporal",
     "🗺️ Análise Geográfica", "🔗 Correlações", "📋 Dados & Conclusão"],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros")

ano_min, ano_max = int(df["ano"].min()), int(df["ano"].max())
faixa_ano = st.sidebar.slider("Período (ano)", ano_min, ano_max, (ano_min, ano_max))

regioes = st.sidebar.multiselect(
    "Região", sorted(df["regiao"].unique()), default=sorted(df["regiao"].unique())
)
senioridades = st.sidebar.multiselect(
    "Senioridade", ["Junior", "Pleno", "Senior"], default=["Junior", "Pleno", "Senior"]
)
modalidades = st.sidebar.multiselect(
    "Modalidade", sorted(df["modalidade"].unique()),
    default=sorted(df["modalidade"].unique())
)
cargos = st.sidebar.multiselect(
    "Cargo", sorted(df["cargo"].unique()), default=sorted(df["cargo"].unique())
)

# Aplica os filtros
mask = (
    df["ano"].between(faixa_ano[0], faixa_ano[1])
    & df["regiao"].isin(regioes)
    & df["senioridade"].isin(senioridades)
    & df["modalidade"].isin(modalidades)
    & df["cargo"].isin(cargos)
)
dff = df[mask]

st.sidebar.markdown("---")
st.sidebar.metric("Registros filtrados", f"{len(dff):,}".replace(",", "."))


# ---------------------------------------------------------------------------
# Funcao utilitaria: barra de KPIs dinamicos
# ---------------------------------------------------------------------------
def render_kpis(base: pd.DataFrame):
    if base.empty:
        st.warning("Nenhum dado para os filtros selecionados.")
        return
    total_vagas = int(base["quantidade_vagas"].sum())
    salario_medio = base["salario_medio"].mean()
    cargo_top = base.groupby("cargo")["quantidade_vagas"].sum().idxmax()
    tec_top = base.groupby("tecnologia")["quantidade_vagas"].sum().idxmax()
    pct_remoto = (
        base.loc[base["modalidade"] == "Remoto", "quantidade_vagas"].sum()
        / total_vagas * 100 if total_vagas else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total de vagas", f"{total_vagas:,}".replace(",", "."))
    c2.metric("Salário médio", f"R$ {salario_medio:,.0f}".replace(",", "."))
    c3.metric("Cargo top", cargo_top)
    c4.metric("Tecnologia top", tec_top)
    c5.metric("% Remoto", f"{pct_remoto:.1f}%")


# ---------------------------------------------------------------------------
# SECAO 1 — Visao Geral
# ---------------------------------------------------------------------------
if secao == "🏠 Visão Geral":
    st.title("Mercado de Trabalho em TI no Brasil (2015–2024)")
    st.markdown(
        """
        **Problema:** entender como evoluíram a quantidade de vagas, os salários e as
        modalidades de trabalho no mercado de TI brasileiro, e quais cargos, tecnologias
        e regiões concentram as oportunidades.

        Use os **filtros na barra lateral** para explorar os dados de forma interativa.
        """
    )
    st.markdown("### Indicadores (KPIs)")
    render_kpis(dff)

    if not dff.empty:
        st.markdown("### Panorama geral")
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                dff.groupby("cargo")["quantidade_vagas"].sum()
                   .sort_values().reset_index(),
                x="quantidade_vagas", y="cargo", orientation="h",
                title="Vagas por cargo", labels={"quantidade_vagas": "Vagas", "cargo": ""},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            senior = dff.groupby("senioridade")["quantidade_vagas"].sum().reset_index()
            fig = px.pie(senior, names="senioridade", values="quantidade_vagas",
                         title="Distribuição por senioridade", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# SECAO 2 — Analise Salarial
# ---------------------------------------------------------------------------
elif secao == "💰 Análise Salarial":
    st.title("💰 Análise Salarial")
    render_kpis(dff)
    st.markdown("---")

    if not dff.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribuição por senioridade")
            fig, ax = plt.subplots(figsize=(6, 4))
            ordem = [s for s in ["Junior", "Pleno", "Senior"]
                     if s in dff["senioridade"].unique()]
            sns.boxplot(data=dff, x="senioridade", y="salario_medio",
                        order=ordem, ax=ax)
            ax.set_xlabel("Senioridade"); ax.set_ylabel("Salário (R$)")
            st.pyplot(fig)

        with col2:
            st.subheader("Salário médio por cargo")
            sal_cargo = (dff.groupby("cargo")["salario_medio"].mean()
                            .sort_values(ascending=False).reset_index())
            fig = px.bar(sal_cargo, x="salario_medio", y="cargo", orientation="h",
                         labels={"salario_medio": "Salário médio (R$)", "cargo": ""})
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Salário médio por senioridade e modalidade")
        pivot = dff.pivot_table(index="senioridade", columns="modalidade",
                                values="salario_medio", aggfunc="mean")
        st.dataframe(pivot.style.format("R$ {:,.2f}"), use_container_width=True)

        st.info(
            "**Interpretação:** o salário cresce de forma clara de Júnior → Pleno → Sênior. "
            "Cargos ligados a Dados e Segurança lideram as médias salariais."
        )


# ---------------------------------------------------------------------------
# SECAO 3 — Analise Temporal
# ---------------------------------------------------------------------------
elif secao == "📈 Análise Temporal":
    st.title("📈 Análise Temporal")
    render_kpis(dff)
    st.markdown("---")

    if not dff.empty:
        st.subheader("Evolução do total de vagas por ano")
        vagas_ano = dff.groupby("ano")["quantidade_vagas"].sum().reset_index()
        fig = px.line(vagas_ano, x="ano", y="quantidade_vagas", markers=True,
                      labels={"quantidade_vagas": "Vagas", "ano": "Ano"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Evolução das modalidades de trabalho")
        mod = (dff.groupby(["ano", "modalidade"])["quantidade_vagas"]
                  .sum().reset_index())
        fig = px.line(mod, x="ano", y="quantidade_vagas", color="modalidade",
                      markers=True, labels={"quantidade_vagas": "Vagas", "ano": "Ano"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Evolução do salário médio por ano")
        sal_ano = dff.groupby("ano")["salario_medio"].mean().reset_index()
        fig = px.area(sal_ano, x="ano", y="salario_medio",
                      labels={"salario_medio": "Salário médio (R$)", "ano": "Ano"})
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "**Interpretação:** as vagas crescem ao longo de todo o período. A partir de "
            "**2020** o trabalho remoto ultrapassa o presencial — mudança estrutural do mercado."
        )


# ---------------------------------------------------------------------------
# SECAO 4 — Analise Geografica
# ---------------------------------------------------------------------------
elif secao == "🗺️ Análise Geográfica":
    st.title("🗺️ Análise Geográfica")
    render_kpis(dff)
    st.markdown("---")

    if not dff.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Vagas por região")
            reg = (dff.groupby("regiao")["quantidade_vagas"].sum()
                      .sort_values(ascending=False).reset_index())
            fig = px.bar(reg, x="regiao", y="quantidade_vagas",
                         labels={"quantidade_vagas": "Vagas", "regiao": "Região"})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Top 10 cidades")
            cidades = (dff.groupby("cidade")["quantidade_vagas"].sum()
                          .sort_values(ascending=False).head(10).reset_index())
            fig = px.bar(cidades, x="quantidade_vagas", y="cidade", orientation="h",
                         labels={"quantidade_vagas": "Vagas", "cidade": ""})
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Salário médio por estado")
        sal_uf = (dff.groupby("estado")["salario_medio"].mean()
                     .sort_values(ascending=False).reset_index())
        st.dataframe(sal_uf.style.format({"salario_medio": "R$ {:,.2f}"}),
                     use_container_width=True)

        st.info("**Interpretação:** o **Sudeste** (com destaque para São Paulo) "
                "concentra a maior parte das oportunidades de TI no país.")


# ---------------------------------------------------------------------------
# SECAO 5 — Correlacoes (funcionalidade avancada: correlacao estatistica)
# ---------------------------------------------------------------------------
elif secao == "🔗 Correlações":
    st.title("🔗 Correlações Estatísticas")
    st.markdown(
        "Análise de correlação entre as variáveis numéricas (Pandas/NumPy + Seaborn)."
    )
    if not dff.empty:
        num = dff[["ano", "mes", "salario_medio", "quantidade_vagas"]].corr()

        col1, col2 = st.columns([1.2, 1])
        with col1:
            fig, ax = plt.subplots(figsize=(6, 5))
            sns.heatmap(num, annot=True, cmap="coolwarm", fmt=".2f",
                        vmin=-1, vmax=1, linewidths=.5, ax=ax)
            ax.set_title("Matriz de correlação")
            st.pyplot(fig)
        with col2:
            st.subheader("Dispersão: ano × salário")
            fig = px.scatter(dff.sample(min(1000, len(dff)), random_state=1),
                             x="ano", y="salario_medio", color="senioridade",
                             opacity=0.6,
                             labels={"salario_medio": "Salário (R$)", "ano": "Ano"})
            st.plotly_chart(fig, use_container_width=True)

        corr_ano_sal = dff["ano"].corr(dff["salario_medio"])
        st.info(
            f"**Interpretação:** a correlação entre `ano` e `salário` é de "
            f"**{corr_ano_sal:.2f}**, indicando tendência de valorização salarial ao "
            "longo do tempo."
        )


# ---------------------------------------------------------------------------
# SECAO 6 — Dados & Conclusao
# ---------------------------------------------------------------------------
elif secao == "📋 Dados & Conclusão":
    st.title("📋 Dados & Conclusão")

    st.subheader("Tabela de dados (filtrada)")
    st.dataframe(dff, use_container_width=True, height=350)

    # Download dos dados filtrados
    csv = dff.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar dados filtrados (CSV)", csv,
                       "mercado_ti_filtrado.csv", "text/csv")

    st.markdown("---")
    st.subheader("Conclusão executiva")
    st.markdown(
        """
        O mercado de TI no Brasil está em **expansão contínua**, com valorização salarial
        ao longo dos anos e uma **transformação estrutural** rumo ao trabalho remoto/híbrido
        a partir de 2020. As oportunidades ainda se concentram no **Sudeste**, e as
        tecnologias e cargos ligados a **Dados** e **Desenvolvimento de Software** estão
        entre os mais demandados.

        **Recomendações**
        - *Profissionais:* investir em tecnologias de alta demanda (Python, SQL, Cloud) e
          considerar posições remotas para ampliar oportunidades.
        - *Empresas:* fora do Sudeste, o modelo remoto é uma alavanca para atrair talentos.
        """
    )

st.sidebar.markdown("---")
st.sidebar.caption("Projeto G2 · Streamlit · Pandas · Seaborn · Plotly · SQLAlchemy")
