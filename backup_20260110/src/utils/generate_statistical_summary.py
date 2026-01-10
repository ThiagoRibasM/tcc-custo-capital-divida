#!/usr/bin/env python3
"""
Script para gerar resumo estatístico e demográfico da planilha de modelagem.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Adiciona o diretório 'src' ao sys.path
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH

# Arquivo principal (mais recente)
file_path = CONSOLIDATED_PATH / "emp_e_fin_novo_mercado_20250920.xlsx"

if not file_path.exists():
    # Tenta outros arquivos
    files = list(CONSOLIDATED_PATH.glob("emp_e_fin_novo_mercado*.xlsx"))
    if files:
        file_path = max(files, key=lambda x: x.stat().st_mtime)
        print(f"Usando arquivo: {file_path.name}")
    else:
        print("❌ Nenhum arquivo encontrado!")
        sys.exit(1)

print(f"\n{'='*80}")
print(f"RESUMO ESTATÍSTICO E DEMOGRÁFICO")
print(f"Arquivo: {file_path.name}")
print(f"{'='*80}\n")

# Lê o arquivo Excel
xl_file = pd.ExcelFile(file_path)
print(f"📊 Abas disponíveis: {xl_file.sheet_names}\n")

# Processa cada aba
for sheet_name in xl_file.sheet_names:
    print(f"\n{'='*80}")
    print(f"📋 ABA: {sheet_name}")
    print(f"{'='*80}\n")
    
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Informações básicas
    print(f"📐 DIMENSÕES:")
    print(f"   - Linhas: {df.shape[0]:,}")
    print(f"   - Colunas: {df.shape[1]}")
    print(f"   - Células: {df.shape[0] * df.shape[1]:,}")
    
    # Informações sobre colunas
    print(f"\n📝 COLUNAS ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        null_pct = (df[col].isna().sum() / len(df)) * 100
        print(f"   {i:2d}. {col[:50]:<50} | Tipo: {str(dtype):<10} | Preenchido: {non_null:>6} ({100-null_pct:5.1f}%)")
    
    # Estatísticas descritivas para colunas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(f"\n📊 ESTATÍSTICAS DESCRITIVAS (Colunas Numéricas):")
        print(f"   Total de colunas numéricas: {len(numeric_cols)}")
        
        desc = df[numeric_cols].describe()
        print(f"\n{desc.to_string()}")
        
        # Estatísticas adicionais
        print(f"\n   📈 ESTATÍSTICAS ADICIONAIS:")
        for col in numeric_cols[:15]:  # Limita a 15 para não ficar muito longo
            print(f"\n   {col}:")
            try:
                print(f"      - Média: {df[col].mean():,.2f}")
                print(f"      - Mediana: {df[col].median():,.2f}")
                print(f"      - Desvio Padrão: {df[col].std():,.2f}")
                print(f"      - Mínimo: {df[col].min():,.2f}")
                print(f"      - Máximo: {df[col].max():,.2f}")
                print(f"      - Q1 (25%): {df[col].quantile(0.25):,.2f}")
                print(f"      - Q3 (75%): {df[col].quantile(0.75):,.2f}")
                print(f"      - IQR: {df[col].quantile(0.75) - df[col].quantile(0.25):,.2f}")
                print(f"      - Valores únicos: {df[col].nunique()}")
                print(f"      - Valores nulos: {df[col].isna().sum()} ({df[col].isna().sum()/len(df)*100:.1f}%)")
            except Exception as e:
                print(f"      - Erro ao calcular estatísticas: {e}")
    
    # Análise demográfica (colunas categóricas)
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        print(f"\n👥 ANÁLISE DEMOGRÁFICA (Colunas Categóricas):")
        print(f"   Total de colunas categóricas: {len(categorical_cols)}")
        
        for col in categorical_cols[:15]:  # Limita a 15
            print(f"\n   📊 {col}:")
            value_counts = df[col].value_counts()
            print(f"      - Valores únicos: {df[col].nunique()}")
            print(f"      - Valores nulos: {df[col].isna().sum()} ({df[col].isna().sum()/len(df)*100:.1f}%)")
            
            if df[col].nunique() <= 20:  # Só mostra distribuição se tiver poucos valores únicos
                print(f"      - Distribuição:")
                for val, count in value_counts.head(10).items():
                    pct = (count / len(df)) * 100
                    print(f"        • {str(val)[:40]:<40}: {count:>6} ({pct:5.1f}%)")
            else:
                print(f"      - Top 10 valores:")
                for val, count in value_counts.head(10).items():
                    pct = (count / len(df)) * 100
                    print(f"        • {str(val)[:40]:<40}: {count:>6} ({pct:5.1f}%)")
    
    # Informações sobre duplicatas
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"\n⚠️  DUPLICATAS:")
        print(f"   - Linhas duplicadas: {duplicates} ({duplicates/len(df)*100:.1f}%)")
    
    # Informações sobre completude dos dados
    print(f"\n✅ COMPLETUDE DOS DADOS:")
    completeness = (df.notna().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    print(f"   - Completude geral: {completeness:.1f}%")
    print(f"   - Células preenchidas: {df.notna().sum().sum():,} / {df.shape[0] * df.shape[1]:,}")
    print(f"   - Células vazias: {df.isna().sum().sum():,} ({100-completeness:.1f}%)")

print(f"\n{'='*80}")
print("✅ Resumo concluído!")
print(f"{'='*80}\n")

