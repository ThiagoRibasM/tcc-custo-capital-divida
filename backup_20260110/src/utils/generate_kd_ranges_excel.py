#!/usr/bin/env python3
"""
Gera tabela Excel com análise detalhada dos ranges de Kd.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, PROJECT_ROOT

DOCS_DIR = PROJECT_ROOT / "docs"


def generate_kd_ranges_excel():
    """Gera tabela Excel com análise de ranges."""
    
    # Lê dados
    df_final = pd.read_csv(CONSOLIDATED_PATH / "kd_final_calculados.csv")
    
    # Cria arquivo Excel com múltiplas abas
    output_file = DOCS_DIR / "kd_ranges_analysis.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # 1. Estatísticas Gerais
        stats_data = {
            'Estatística': ['Total', 'Média', 'Mediana', 'Desvio Padrão', 'Mínimo', 'Máximo', 
                           'Q1 (25%)', 'Q3 (75%)', 'IQR', 'Percentil 1%', 'Percentil 5%', 
                           'Percentil 10%', 'Percentil 90%', 'Percentil 95%', 'Percentil 99%'],
            'Valor (% a.a.)': [
                len(df_final),
                df_final['Kd_Percentual'].mean(),
                df_final['Kd_Percentual'].median(),
                df_final['Kd_Percentual'].std(),
                df_final['Kd_Percentual'].min(),
                df_final['Kd_Percentual'].max(),
                df_final['Kd_Percentual'].quantile(0.25),
                df_final['Kd_Percentual'].quantile(0.75),
                df_final['Kd_Percentual'].quantile(0.75) - df_final['Kd_Percentual'].quantile(0.25),
                df_final['Kd_Percentual'].quantile(0.01),
                df_final['Kd_Percentual'].quantile(0.05),
                df_final['Kd_Percentual'].quantile(0.10),
                df_final['Kd_Percentual'].quantile(0.90),
                df_final['Kd_Percentual'].quantile(0.95),
                df_final['Kd_Percentual'].quantile(0.99)
            ]
        }
        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='Estatísticas Gerais', index=False)
        
        # 2. Distribuição por Faixas
        faixas = [
            (0, 5, "Muito Baixo (< 5%)"),
            (5, 8, "Baixo (5% - 8%)"),
            (8, 12, "Moderado-Baixo (8% - 12%)"),
            (12, 16, "Moderado (12% - 16%)"),
            (16, 20, "Moderado-Alto (16% - 20%)"),
            (20, 30, "Alto (20% - 30%)"),
            (30, 50, "Muito Alto (30% - 50%)"),
            (50, float('inf'), "Extremo (> 50%)")
        ]
        
        faixas_data = []
        for min_val, max_val, label in faixas:
            if max_val == float('inf'):
                mask = df_final['Kd_Percentual'] >= min_val
            else:
                mask = (df_final['Kd_Percentual'] >= min_val) & (df_final['Kd_Percentual'] < max_val)
            
            count = mask.sum()
            pct = (count / len(df_final)) * 100
            if count > 0:
                mean_kd = df_final[mask]['Kd_Percentual'].mean()
                median_kd = df_final[mask]['Kd_Percentual'].median()
                std_kd = df_final[mask]['Kd_Percentual'].std()
                min_kd = df_final[mask]['Kd_Percentual'].min()
                max_kd = df_final[mask]['Kd_Percentual'].max()
            else:
                mean_kd = median_kd = std_kd = min_kd = max_kd = 0
            
            faixas_data.append({
                'Faixa': label,
                'Quantidade': count,
                '% do Total': pct,
                'Kd Médio': mean_kd,
                'Kd Mediano': median_kd,
                'Desvio Padrão': std_kd,
                'Mínimo': min_kd,
                'Máximo': max_kd
            })
        
        df_faixas = pd.DataFrame(faixas_data)
        df_faixas.to_excel(writer, sheet_name='Distribuição por Faixas', index=False)
        
        # 3. Análise por Indexador
        indexadores = df_final['Indexador_Processado'].value_counts().index
        
        indexador_data = []
        for idx in indexadores:
            if idx == 'NÃO_IDENTIFICADO':
                continue
            
            df_idx = df_final[df_final['Indexador_Processado'] == idx]
            stats = df_idx['Kd_Percentual'].describe()
            iqr = stats['75%'] - stats['25%']
            
            indexador_data.append({
                'Indexador': idx,
                'Quantidade': len(df_idx),
                'Média': stats['mean'],
                'Mediana': stats['50%'],
                'Desvio Padrão': stats['std'],
                'Mínimo': stats['min'],
                'Máximo': stats['max'],
                'Q1 (25%)': stats['25%'],
                'Q3 (75%)': stats['75%'],
                'IQR': iqr,
                'Limite Inferior (Q1-1.5*IQR)': stats['25%'] - 1.5*iqr,
                'Limite Superior (Q3+1.5*IQR)': stats['75%'] + 1.5*iqr
            })
        
        df_indexadores = pd.DataFrame(indexador_data)
        df_indexadores.to_excel(writer, sheet_name='Análise por Indexador', index=False)
        
        # 4. Outliers por Indexador
        outliers_data = []
        for idx in indexadores:
            if idx == 'NÃO_IDENTIFICADO':
                continue
            
            df_idx = df_final[df_final['Indexador_Processado'] == idx]
            stats = df_idx['Kd_Percentual'].describe()
            iqr = stats['75%'] - stats['25%']
            lower_bound = stats['25%'] - 1.5*iqr
            upper_bound = stats['75%'] + 1.5*iqr
            
            outliers = df_idx[(df_idx['Kd_Percentual'] < lower_bound) | (df_idx['Kd_Percentual'] > upper_bound)]
            
            for _, row in outliers.iterrows():
                outliers_data.append({
                    'Indexador': idx,
                    'Empresa': row['Empresa'],
                    'Kd (%)': row['Kd_Percentual'],
                    'Spread (%)': row['Spread_Percentual'],
                    'Tipo Financiamento': row['Tipo_Financiamento'],
                    'Valor Consolidado 2024': row['Valor_Consolidado_2024'],
                    'Observação': row['Kd_Observacao_Validacao'] if pd.notna(row['Kd_Observacao_Validacao']) else ""
                })
        
        if outliers_data:
            df_outliers = pd.DataFrame(outliers_data)
            df_outliers.to_excel(writer, sheet_name='Outliers', index=False)
        
        # 5. Casos Extremos
        kd_baixo = df_final[df_final['Kd_Percentual'] < 5].copy()
        kd_alto = df_final[df_final['Kd_Percentual'] > 30].copy()
        
        if len(kd_baixo) > 0:
            df_kd_baixo = kd_baixo[['Empresa', 'Indexador_Processado', 'Kd_Percentual', 
                                    'Spread_Percentual', 'Tipo_Financiamento', 
                                    'Valor_Consolidado_2024', 'Kd_Observacao_Validacao']].copy()
            df_kd_baixo.to_excel(writer, sheet_name='Kd Muito Baixo (<5%)', index=False)
        
        if len(kd_alto) > 0:
            df_kd_alto = kd_alto[['Empresa', 'Indexador_Processado', 'Kd_Percentual', 
                                  'Spread_Percentual', 'Tipo_Financiamento', 
                                  'Valor_Consolidado_2024', 'Kd_Observacao_Validacao']].copy()
            df_kd_alto.to_excel(writer, sheet_name='Kd Muito Alto (>30%)', index=False)
        
        # 6. Análise por Tipo de Financiamento
        tipos = df_final['Tipo_Financiamento'].value_counts()
        
        tipos_data = []
        for tipo, count in tipos.items():
            df_tipo = df_final[df_final['Tipo_Financiamento'] == tipo]
            stats = df_tipo['Kd_Percentual'].describe()
            
            tipos_data.append({
                'Tipo de Financiamento': tipo,
                'Quantidade': count,
                'Kd Médio': stats['mean'],
                'Kd Mediano': stats['50%'],
                'Desvio Padrão': stats['std'],
                'Mínimo': stats['min'],
                'Máximo': stats['max'],
                'Q1 (25%)': stats['25%'],
                'Q3 (75%)': stats['75%']
            })
        
        df_tipos = pd.DataFrame(tipos_data)
        df_tipos.to_excel(writer, sheet_name='Análise por Tipo', index=False)
        
        # 7. Comparação com Literatura
        literatura_data = {
            'Contexto': [
                'Brasil - Mercado Desenvolvido',
                'Brasil - Taxas Indexadas (CDI/DI)',
                'Brasil - Taxas Indexadas (IPCA/TLP)',
                'Brasil - Pré-fixado',
                'Mercados Emergentes',
                'Mercados Desenvolvidos'
            ],
            'Range Típico': [
                '8% - 20%',
                '12% - 25%',
                '6% - 15%',
                '5% - 30%',
                '10% - 30%',
                '3% - 12%'
            ],
            'Observações': [
                'Maioria dos casos',
                'Com spread típico',
                'Com spread típico',
                'Depende do prazo e risco',
                'Maior risco país',
                'Taxas de juros mais baixas'
            ]
        }
        df_literatura = pd.DataFrame(literatura_data)
        df_literatura.to_excel(writer, sheet_name='Comparação Literatura', index=False)
    
    print(f"✅ Tabela Excel gerada em: {output_file}")


if __name__ == "__main__":
    generate_kd_ranges_excel()

