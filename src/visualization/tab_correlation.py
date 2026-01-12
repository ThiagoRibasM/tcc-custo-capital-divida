#!/usr/bin/env python3
"""
Tabela de Correlação Triangular (Padrão Acadêmico)

Gera uma tabela LaTeX com correlações de Pearson no formato triangular inferior,
com asteriscos indicando significância estatística.

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH, FIGURES_DIR

# Features principais para a tabela (seleção mais compacta)
FEATURES = [
    'Kd_Ponderado',
    'Alavancagem_Total',
    'Liquidez_Corrente',
    'Liquidez_Imediata',
    'ROA',
    'Margem_EBITDA',
    'Tamanho',
    'Tangibilidade',
    'Indice_Diversificacao',
    'IHH_Indexador',
]

# Labels curtos para a tabela
LABELS = {
    'Kd_Ponderado': 'Kd',
    'Alavancagem_Total': 'Alav.',
    'Liquidez_Corrente': 'Liq.C',
    'Liquidez_Imediata': 'Liq.I',
    'ROA': 'ROA',
    'Margem_EBITDA': 'M.EBITDA',
    'Tamanho': 'Tam.',
    'Tangibilidade': 'Tang.',
    'Indice_Diversificacao': 'Div.',
    'IHH_Indexador': 'HHI',
}

def load_data():
    """Carrega dados e seleciona features."""
    df = pd.read_csv(CONSOLIDATED_PATH / "tabela_features.csv")
    available = [f for f in FEATURES if f in df.columns]
    return df[available]

def calc_correlation_with_pvalue(df):
    """Calcula correlação de Pearson com p-values."""
    n = len(df.columns)
    corr_matrix = np.zeros((n, n))
    pval_matrix = np.zeros((n, n))
    
    for i, col1 in enumerate(df.columns):
        for j, col2 in enumerate(df.columns):
            if i == j:
                corr_matrix[i, j] = 1.0
                pval_matrix[i, j] = 0.0
            else:
                # Remover NaNs pairwise
                mask = df[[col1, col2]].notna().all(axis=1)
                if mask.sum() > 2:
                    r, p = stats.pearsonr(df.loc[mask, col1], df.loc[mask, col2])
                    corr_matrix[i, j] = r
                    pval_matrix[i, j] = p
                else:
                    corr_matrix[i, j] = np.nan
                    pval_matrix[i, j] = np.nan
    
    return pd.DataFrame(corr_matrix, index=df.columns, columns=df.columns), \
           pd.DataFrame(pval_matrix, index=df.columns, columns=df.columns)

def format_corr_value(r, p):
    """Formata valor com asteriscos de significância."""
    if np.isnan(r):
        return ""
    
    stars = ""
    if p < 0.01:
        stars = "***"
    elif p < 0.05:
        stars = "**"
    elif p < 0.10:
        stars = "*"
    
    return f"{r:.2f}{stars}"

def generate_latex_table(corr, pval, labels):
    """Gera tabela LaTeX triangular inferior."""
    cols = corr.columns.tolist()
    n = len(cols)
    
    # Header
    header_labels = [labels.get(c, c) for c in cols]
    
    latex = []
    latex.append(r"\begin{table}[H]")
    latex.append(r"\centering")
    latex.append(r"\small")
    latex.append(r"\caption{Matriz de Correlação de Pearson entre Variáveis do Modelo}")
    latex.append(r"\label{tab:correlation}")
    
    # Definir colunas: primeira para variável, depois uma para cada coluna
    col_spec = "l" + "r" * n
    latex.append(r"\begin{tabular}{" + col_spec + "}")
    latex.append(r"\hline")
    
    # Linha de cabeçalho com números
    header_row = " & " + " & ".join([f"({i+1})" for i in range(n)]) + r" \\"
    latex.append(header_row)
    latex.append(r"\hline")
    
    # Linhas de dados (triangular inferior)
    for i, col in enumerate(cols):
        row_label = f"({i+1}) {labels.get(col, col)}"
        row_values = []
        
        for j in range(n):
            if j < i:
                # Triangular inferior: mostrar valor
                r = corr.iloc[i, j]
                p = pval.iloc[i, j]
                row_values.append(format_corr_value(r, p))
            elif j == i:
                # Diagonal: 1.00
                row_values.append("1.00")
            else:
                # Triangular superior: vazio
                row_values.append("")
        
        row = row_label + " & " + " & ".join(row_values) + r" \\"
        latex.append(row)
    
    latex.append(r"\hline")
    latex.append(r"\end{tabular}")
    latex.append(r"\begin{tablenotes}")
    latex.append(r"\small")
    latex.append(r"\item Nota: *** p<0.01, ** p<0.05, * p<0.10")
    latex.append(r"\end{tablenotes}")
    latex.append(r"\end{table}")
    
    return "\n".join(latex)

def main():
    print("=" * 60)
    print("GERANDO TABELA DE CORRELAÇÃO (PADRÃO ACADÊMICO)")
    print("=" * 60)
    
    # Carregar dados
    print("\n1. Carregando dados...")
    df = load_data()
    print(f"   → {len(df)} observações, {len(df.columns)} variáveis")
    
    # Calcular correlações
    print("\n2. Calculando correlações com p-values...")
    corr, pval = calc_correlation_with_pvalue(df)
    
    # Gerar tabela LaTeX
    print("\n3. Gerando tabela LaTeX...")
    latex_table = generate_latex_table(corr, pval, LABELS)
    
    # Salvar tabela
    output_path = Path(__file__).parent.parent.parent / "reports" / "tab_correlation.tex"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(latex_table, encoding='utf-8')
    
    print(f"\n✓ Tabela salva em: {output_path}")
    print("\n" + "=" * 60)
    print("TABELA LATEX GERADA:")
    print("=" * 60)
    print(latex_table)
    
    return latex_table

if __name__ == "__main__":
    main()
