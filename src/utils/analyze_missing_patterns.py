#!/usr/bin/env python3
"""
Analisa indexadores não identificados para encontrar padrões faltantes.
"""
import pandas as pd
import re
from collections import Counter
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH


def analyze_missing_indexers():
    """Analisa indexadores não identificados para encontrar padrões."""
    
    # Lê dados
    df_orig = pd.read_excel(CONSOLIDATED_PATH / 'emp_e_fin_novo_mercado_20250920.xlsx')
    df_proc = pd.read_csv(CONSOLIDATED_PATH / 'kd_calculated.csv')
    
    # Merge
    df_merged = df_proc.copy()
    df_merged['indexador_original'] = df_orig['indexador'].values
    
    # Filtra não identificados
    nao_id = df_merged[df_merged['Indexador_Processado'] == 'NÃO_IDENTIFICADO'].copy()
    nao_id_clean = nao_id[nao_id['indexador_original'].notna()].copy()
    nao_id_clean['indexador_upper'] = nao_id_clean['indexador_original'].astype(str).str.upper()
    
    print(f"📊 Análise de {len(nao_id_clean)} indexadores não identificados\n")
    
    # 1. Procura por palavras-chave
    keywords = {
        'CDI': ['CDI', 'CERTIFICADO', 'DEPOSITO', 'INTERBANCARIO'],
        'DI': ['DI', 'DEPOSITO INTERBANCARIO', '100% DO DI'],
        'TLP': ['TLP', 'TAXA LONGO PRAZO', 'LONGO PRAZO'],
        'TJLP': ['TJLP', 'TAXA JUROS LONGO PRAZO'],
        'IPCA': ['IPCA', 'IGP', 'INFLACAO'],
        'TR': ['TR', 'TAXA REFERENCIAL'],
        'SELIC': ['SELIC'],
        'PRE_FIXADO': ['PRE', 'FIX', 'FIXO', 'FIXA', 'PREFIXADO'],
        'VARIABLE': ['VARIAVEL', 'VARIABLE', 'FLOATING', 'AJUSTAVEL', 'FLUTUANTE'],
        'SPREAD': ['SPREAD', 'MARGEM', 'PREMIO'],
        'PERCENT': ['%', 'PERCENTUAL', 'PORCENTO']
    }
    
    print("🔍 Palavras-chave encontradas:")
    for keyword, patterns in keywords.items():
        matches = []
        for pattern in patterns:
            matches.extend(nao_id_clean[nao_id_clean['indexador_upper'].str.contains(pattern, na=False, regex=False)]['indexador_original'].tolist())
        if matches:
            print(f"\n{keyword}: {len(set(matches))} ocorrências únicas")
            for val in list(set(matches))[:5]:
                print(f"  - {str(val)[:65]}")
    
    # 2. Padrões numéricos
    print("\n\n📊 Padrões numéricos:")
    numeric_patterns = {
        'Percentual direto': r'^\d+[.,]\d+\s*%',
        'Percentual com a.a.': r'\d+[.,]\d+\s*%\s*a\.?a\.?',
        'Percentual com a.m.': r'\d+[.,]\d+\s*%\s*a\.?m\.?',
        'Faixa de percentual': r'\d+[.,]\d+\s*%\s*a\s*\d+[.,]\d+\s*%',
    }
    
    for pattern_name, pattern in numeric_patterns.items():
        matches = nao_id_clean[nao_id_clean['indexador_original'].astype(str).str.match(pattern, na=False, case=False)]
        if len(matches) > 0:
            print(f"\n{pattern_name}: {len(matches)} ocorrências")
            for val in matches['indexador_original'].head(5):
                print(f"  - {str(val)[:65]}")
    
    # 3. Valores mais frequentes
    print("\n\n📈 Top 30 indexadores não identificados mais frequentes:")
    value_counts = nao_id_clean['indexador_original'].value_counts().head(30)
    for idx, (val, count) in enumerate(value_counts.items(), 1):
        print(f"{idx:2d}. ({count:3d}x) {str(val)[:65]}")
    
    return nao_id_clean


if __name__ == "__main__":
    analyze_missing_indexers()

