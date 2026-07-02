# 💻 Mercado de Trabalho em TI no Brasil (2015–2024)

Projeto **G2** da disciplina *Linguagem de Programação — Análise e Visualização de Dados com Python*.
Análise exploratória, KPIs, visualizações e **dashboard interativo em Streamlit** sobre a
evolução do mercado de trabalho em Tecnologia da Informação no Brasil.

> **Tema:** Mercado de Trabalho em TI · **Autor:** Danilo

---

## 🎯 Problema

Como evoluíram, entre 2015 e 2024, a **quantidade de vagas**, os **salários** e as
**modalidades de trabalho** no mercado de TI brasileiro — e quais cargos, tecnologias e
regiões concentram as oportunidades?

---

## 🔗 Links de entrega

| Item | Link |
|---|---|
| Repositório GitHub | `https://github.com/danilosoc7/G2-LinguagensProgramacao` |
| GitHub Pages | `https://github.com/danilosoc7/G2-LinguagensProgramacao` |
| Dashboard (Streamlit Cloud) | `https://g2-linguagensprogramacao-dashboard.streamlit.app/` |

> Substitua os links acima após publicar (instruções na seção *Publicação*).

---

## 🧰 Tecnologias

**Obrigatórias:** Python · Pandas · Matplotlib · Seaborn · Streamlit · GitHub
**Complementares:** Plotly (gráficos interativos) · SQLAlchemy + SQLite (persistência)

### Funcionalidades intermediárias
- Filtros múltiplos no Streamlit (ano, região, senioridade, modalidade, cargo)
- KPIs dinâmicos (recalculados conforme os filtros)
- Gráficos interativos (Plotly)
- Análise temporal
- Dashboard organizado em seções

### Funcionalidades avançadas
- **Persistência em banco** com SQLAlchemy + SQLite (`database/mercado_ti.db`)
- **Correlação estatística** (Pandas/NumPy + heatmap Seaborn)

---

## 📁 Estrutura do projeto

```
projeto-g2/
│
├── app.py                 # Dashboard Streamlit
├── requirements.txt       # Dependências
├── README.md              # Este arquivo
├── index.html             # Página do projeto (GitHub Pages)
├── gerar_dados.py         # Gera a base (CSV + SQLite)
├── gerar_imagens.py       # Gera os gráficos estáticos
├── dados/
│   └── mercado_ti.csv     # Base de dados (CSV)
├── database/
│   └── mercado_ti.db      # Banco SQLite (SQLAlchemy)
├── notebooks/
│   └── analise_mercado_ti.ipynb   # Notebook de análise (10 seções)
└── imagens/
    └── *.png              # Gráficos gerados
```

---

## ▶️ Como executar localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. (Opcional) Regerar a base de dados e as imagens
python gerar_dados.py
python gerar_imagens.py

# 3. Rodar o dashboard
streamlit run app.py
```

O dashboard abre em `http://localhost:8501`.

---

## 📊 Alguns resultados

![Evolução das vagas](imagens/01_evolucao_vagas.png)
![Modalidades ao longo do tempo](imagens/05_modalidade_tempo.png)
![Correlação](imagens/06_correlacao.png)

---

## 🚀 Publicação

**GitHub** — suba o projeto:
```bash
git init
git add .
git commit -m "Projeto G2 - Mercado de TI"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/projeto-g2.git
git push -u origin main
```

**GitHub Pages** — em *Settings → Pages*, selecione a branch `main` / pasta `/root`.
A página `index.html` ficará disponível em `https://SEU_USUARIO.github.io/projeto-g2/`.

**Streamlit Community Cloud** — acesse [share.streamlit.io](https://share.streamlit.io),
conecte o repositório e aponte para `app.py`.

---

## 📌 Principais conclusões

- Mercado de TI em **expansão contínua** no período analisado.
- **Valorização salarial** ao longo dos anos (correlação positiva ano × salário).
- **Virada do trabalho remoto** a partir de 2020 (mudança estrutural pós-pandemia).
- **Sudeste** concentra a maior parte das oportunidades.
- Cargos e tecnologias de **Dados** e **Desenvolvimento** entre os mais demandados.
