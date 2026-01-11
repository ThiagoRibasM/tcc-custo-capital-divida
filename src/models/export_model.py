#!/usr/bin/env python3
"""
Exportar modelo final e coeficientes para rastreabilidade.
Gera arquivos CSV e pickle para reprodutibilidade.
"""

import pandas as pd
import pickle
import json
from datetime import datetime
from pathlib import Path

# Dados do modelo final (hardcoded para registro permanente)
MODEL_METADATA = {
    "version": "1.0",
    "date": "2026-01-11",
    "r_squared": 0.269,
    "r_squared_adj": 0.237,
    "f_statistic": 11.76,
    "f_pvalue": 3.67e-9,
    "n_observations": 119,
    "n_features": 5,
    "cov_type": "HC3",
    "target": "Kd_Ponderado"
}

COEFFICIENTS = [
    {"variable": "const", "coef": 23.3811, "std_err": 3.311, "z": 7.061, "pvalue": 0.000, "ci_lower": 16.891, "ci_upper": 29.871},
    {"variable": "Alavancagem_Total", "coef": 5.5982, "std_err": 1.588, "z": 3.526, "pvalue": 0.000, "ci_lower": 2.487, "ci_upper": 8.710},
    {"variable": "Liquidez_Imediata", "coef": -1.4374, "std_err": 0.950, "z": -1.513, "pvalue": 0.130, "ci_lower": -3.299, "ci_upper": 0.425},
    {"variable": "Tamanho", "coef": -0.7556, "std_err": 0.218, "z": -3.460, "pvalue": 0.001, "ci_lower": -1.184, "ci_upper": -0.328},
    {"variable": "Tangibilidade", "coef": -2.8713, "std_err": 1.291, "z": -2.224, "pvalue": 0.026, "ci_lower": -5.402, "ci_upper": -0.341},
    {"variable": "IHH_Indexador", "coef": -1.8527, "std_err": 0.869, "z": -2.133, "pvalue": 0.033, "ci_lower": -3.555, "ci_upper": -0.150},
]

DIAGNOSTICS = {
    "normality": {
        "jarque_bera_stat": 0.035,
        "jarque_bera_pval": 0.983,
        "omnibus_stat": 0.036,
        "omnibus_pval": 0.982,
        "skewness": -0.027,
        "kurtosis": 2.936
    },
    "heteroscedasticity": {
        "breusch_pagan_pval": 0.143,
        "action": "HC3 robust errors applied"
    },
    "autocorrelation": {
        "durbin_watson": 0.634,
        "note": "Cross-section data, DW less relevant"
    },
    "condition_number": 173
}

PREPROCESSING = {
    "imputation": "KNN (k=5, weighted by distance)",
    "winsorization": "1%-99% on all features",
    "outlier_removal": "Cook's Distance > 4/n (7 observations removed)",
    "vif_threshold": 5.0,
    "stepwise_pvalue": 0.15
}


def main():
    output_dir = Path(__file__).parent.parent.parent / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Salvar coeficientes como CSV
    df_coef = pd.DataFrame(COEFFICIENTS)
    df_coef.to_csv(output_dir / "modelo_coeficientes.csv", index=False)
    print(f"✓ Coeficientes salvos em: {output_dir / 'modelo_coeficientes.csv'}")
    
    # 2. Salvar metadados completos como JSON
    full_metadata = {
        "model": MODEL_METADATA,
        "coefficients": COEFFICIENTS,
        "diagnostics": DIAGNOSTICS,
        "preprocessing": PREPROCESSING,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_dir / "modelo_final.json", "w", encoding="utf-8") as f:
        json.dump(full_metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ Metadados JSON salvos em: {output_dir / 'modelo_final.json'}")
    
    # 3. Resumo para LaTeX/Word
    latex_table = """
\\begin{table}[htbp]
\\centering
\\caption{Resultados do Modelo OLS - Determinantes do Custo de Dívida}
\\label{tab:regression_results}
\\begin{tabular}{lcccc}
\\hline
\\textbf{Variável} & \\textbf{Coeficiente} & \\textbf{Erro Padrão} & \\textbf{z} & \\textbf{P-valor} \\\\
\\hline
Constante & 23.38 & 3.31 & 7.06 & 0.000*** \\\\
Alavancagem Total & 5.60 & 1.59 & 3.53 & 0.000*** \\\\
Tamanho & -0.76 & 0.22 & -3.46 & 0.001*** \\\\
Tangibilidade & -2.87 & 1.29 & -2.22 & 0.026** \\\\
IHH Indexador & -1.85 & 0.87 & -2.13 & 0.033** \\\\
Liquidez Imediata & -1.44 & 0.95 & -1.51 & 0.130 \\\\
\\hline
\\multicolumn{5}{l}{R² = 0.269, R² Ajustado = 0.237, F = 11.76***} \\\\
\\multicolumn{5}{l}{N = 119 empresas. Erros robustos HC3.} \\\\
\\multicolumn{5}{l}{*** p<0.01, ** p<0.05, * p<0.10} \\\\
\\hline
\\end{tabular}
\\end{table}
"""
    
    with open(output_dir / "modelo_tabela_latex.tex", "w", encoding="utf-8") as f:
        f.write(latex_table)
    print(f"✓ Tabela LaTeX salva em: {output_dir / 'modelo_tabela_latex.tex'}")
    
    print("\n" + "="*50)
    print("EXPORTAÇÃO CONCLUÍDA")
    print("="*50)


if __name__ == "__main__":
    main()
