"""
gerar_dados.py
---------------
Gera uma base sintetica (porem realista) do Mercado de Trabalho em TI no Brasil
entre 2015 e 2024 e a persiste em dois formatos:

    dados/mercado_ti.csv        -> fonte de dados "crua"
    database/mercado_ti.db      -> banco SQLite (via SQLAlchemy)

Executar apenas UMA vez para regenerar a base. O dashboard e o notebook
leem os arquivos ja gerados.

Uso:
    python gerar_dados.py
"""

import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# Semente fixa -> base sempre identica (reprodutibilidade)
RNG = np.random.default_rng(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(BASE_DIR, "dados", "mercado_ti.csv")
CAMINHO_DB = os.path.join(BASE_DIR, "database", "mercado_ti.db")

# ---------------------------------------------------------------------------
# Dominios (categorias possiveis)
# ---------------------------------------------------------------------------
CARGOS = [
    "Desenvolvedor Backend", "Desenvolvedor Frontend", "Desenvolvedor Fullstack",
    "Cientista de Dados", "Engenheiro de Dados", "Analista de Dados",
    "DevOps", "Engenheiro de Software", "Analista de Suporte",
    "Especialista em Seguranca", "QA / Testes", "Product Manager",
]

TECNOLOGIAS = [
    "Python", "Java", "JavaScript", "SQL", "AWS", "Azure",
    "Power BI", "React", "Docker", "Kubernetes", "C#", "Go",
]

SENIORIDADES = ["Junior", "Pleno", "Senior"]
MODALIDADES = ["Presencial", "Hibrido", "Remoto"]

# Regiao -> (estado, cidade principal, peso relativo de vagas)
REGIOES = {
    "Sudeste": [("SP", "Sao Paulo", 0.30), ("RJ", "Rio de Janeiro", 0.10),
                ("MG", "Belo Horizonte", 0.08)],
    "Sul": [("PR", "Curitiba", 0.07), ("RS", "Porto Alegre", 0.06),
            ("SC", "Florianopolis", 0.06)],
    "Nordeste": [("PE", "Recife", 0.06), ("CE", "Fortaleza", 0.05),
                 ("BA", "Salvador", 0.04)],
    "Centro-Oeste": [("DF", "Brasilia", 0.05), ("GO", "Goiania", 0.02)],
    "Norte": [("AM", "Manaus", 0.02), ("PA", "Belem", 0.01)],
}

# Base salarial media (R$) por senioridade
SALARIO_BASE = {"Junior": 3500, "Pleno": 7000, "Senior": 12500}

# Ajuste (multiplicador) de salario por cargo -> reflete valorizacao de mercado
FATOR_CARGO = {
    "Cientista de Dados": 1.25, "Engenheiro de Dados": 1.20,
    "DevOps": 1.18, "Especialista em Seguranca": 1.22,
    "Engenheiro de Software": 1.15, "Desenvolvedor Fullstack": 1.10,
    "Desenvolvedor Backend": 1.08, "Product Manager": 1.20,
    "Desenvolvedor Frontend": 1.00, "QA / Testes": 0.95,
    "Analista de Dados": 0.98, "Analista de Suporte": 0.80,
}


def gerar_base(n_linhas: int = 4000) -> pd.DataFrame:
    """Constroi o DataFrame com os registros do mercado de TI."""
    registros = []

    # Achata as regioes em listas paralelas para sortear com pesos
    combos, pesos = [], []
    for regiao, estados in REGIOES.items():
        for uf, cidade, peso in estados:
            combos.append((regiao, uf, cidade))
            pesos.append(peso)
    pesos = np.array(pesos) / sum(pesos)

    for _ in range(n_linhas):
        idx = RNG.choice(len(combos), p=pesos)
        regiao, uf, cidade = combos[idx]

        ano = int(RNG.integers(2015, 2025))          # 2015..2024
        mes = int(RNG.integers(1, 13))
        data = pd.Timestamp(year=ano, month=mes, day=1)

        cargo = RNG.choice(CARGOS)
        tecnologia = RNG.choice(TECNOLOGIAS)
        senioridade = RNG.choice(SENIORIDADES, p=[0.4, 0.4, 0.2])

        # Modalidade: remoto/hibrido crescem MUITO a partir de 2020 (pandemia)
        if ano >= 2020:
            modalidade = RNG.choice(MODALIDADES, p=[0.20, 0.35, 0.45])
        else:
            modalidade = RNG.choice(MODALIDADES, p=[0.75, 0.15, 0.10])

        # Salario: base * fator do cargo * inflacao anual * ruido
        crescimento_anual = 1 + 0.05 * (ano - 2015)   # ~5% a.a.
        base = SALARIO_BASE[senioridade] * FATOR_CARGO[cargo] * crescimento_anual
        salario = float(RNG.normal(base, base * 0.12))
        salario = round(max(salario, 1800), 2)

        # Quantidade de vagas cresce ao longo dos anos
        media_vagas = 8 + 1.5 * (ano - 2015)
        quantidade_vagas = int(max(1, RNG.poisson(media_vagas)))

        registros.append({
            "data": data,
            "ano": ano,
            "mes": mes,
            "regiao": regiao,
            "estado": uf,
            "cidade": cidade,
            "cargo": cargo,
            "tecnologia": tecnologia,
            "senioridade": senioridade,
            "modalidade": modalidade,
            "salario_medio": salario,
            "quantidade_vagas": quantidade_vagas,
        })

    df = pd.DataFrame(registros).sort_values("data").reset_index(drop=True)
    return df


def main():
    df = gerar_base()

    # Injeta alguns valores ausentes de proposito (para demonstrar limpeza)
    idx_nulos = RNG.choice(df.index, size=40, replace=False)
    df.loc[idx_nulos, "salario_medio"] = np.nan

    # CSV
    os.makedirs(os.path.dirname(CAMINHO_CSV), exist_ok=True)
    df.to_csv(CAMINHO_CSV, index=False)
    print(f"[OK] CSV gerado: {CAMINHO_CSV}  ({len(df)} linhas)")

    # SQLite via SQLAlchemy (funcionalidade avancada: persistencia em banco)
    os.makedirs(os.path.dirname(CAMINHO_DB), exist_ok=True)
    engine = create_engine(f"sqlite:///{CAMINHO_DB}")
    df.to_sql("vagas_ti", engine, if_exists="replace", index=False)
    print(f"[OK] Banco SQLite gerado: {CAMINHO_DB}  (tabela 'vagas_ti')")


if __name__ == "__main__":
    main()
