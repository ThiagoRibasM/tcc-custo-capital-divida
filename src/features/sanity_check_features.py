#!/usr/bin/env python3
"""
Teste de Sanidade das Features Financeiras
Verifica outliers e valores fora de faixas esperadas para cada indicador.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH

# Definição de limites "soft" (alertas) e "hard" (erros prováveis)
# Formato: (min_soft, max_soft, min_hard, max_hard)
# None significa sem limite
LIMITS = {
    # Target
    'Kd_Ponderado': (0, 35, 0, 100), # Kd normal entre 0% e 35% (BR), erro se < 0 ou > 100%
    
    # Alavancagem
    'Divida_Total_Ativo': (0, 1.0, 0, 10.0), # Dívida > 10x Ativo é muito estranho
    'Alavancagem_Total': (0, 1.0, 0, 1.0), # Deve ser entre 0 e 1 por definição
    'Proporcao_Divida_CP': (0, 1.0, 0, 1.01), # Proporção 0-1
    'Proporcao_Divida_LP': (0, 1.0, 0, 1.01), # Proporção 0-1
    
    # Liquidez
    'Liquidez_Corrente': (0.1, 5.0, 0, 100.0), # > 100 de liquidez é caixa infinito?
    'Liquidez_Imediata': (0.01, 2.0, 0, 100.0),
    
    # Rentabilidade
    'ROA': (-0.5, 0.5, -5.0, 5.0), # Retorno sobre ativo > 500% ou < -500% é erro ou holding estranha
    'ROE': (-1.0, 1.0, -50.0, 50.0), # ROE explode com PL pequeno, limites largos
    'Margem_Bruta': (0, 0.8, -5.0, 1.0), # Geralmente positiva, max 100%
    'Margem_Liquida': (-0.5, 0.5, -10.0, 10.0),
    'Margem_EBITDA': (-0.5, 0.8, -10.0, 10.0),
    
    # Cobertura
    'Cobertura_Juros': (-10, 20, -1000, 1000), # Volátil
    'Divida_EBITDA': (-5, 10, -100, 100),
    
    # Adicionais
    'Tangibilidade': (0, 1.0, 0, 1.01), # Ativo Fixo / Total
    'IHH_Indexador': (0, 1.0, 0, 1.0001), # Índice 0-1
    'IHH_Tipo': (0, 1.0, 0, 1.0001), # Índice 0-1
}

def analyze_feature(df, col, limits):
    """Analisa uma feature quanto a limites e outliers."""
    min_s, max_s, min_h, max_h = limits
    
    vals = df[col].dropna()
    n = len(vals)
    if n == 0:
        return
    
    # Checar Hard Limits (Valores Esdrúxulos)
    invalid_low = vals[vals < (min_h if min_h is not None else -np.inf)]
    invalid_high = vals[vals > (max_h if max_h is not None else np.inf)]
    
    # Checar Soft Limits (Valores Suspeitos / Outliers da Indústria)
    suspect_low = vals[(vals >= (min_h if min_h is not None else -np.inf)) & (vals < (min_s if min_s is not None else -np.inf))]
    suspect_high = vals[(vals <= (max_h if max_h is not None else np.inf)) & (vals > (max_s if max_s is not None else np.inf))]
    
    if len(invalid_low) > 0 or len(invalid_high) > 0 or len(suspect_low) > 0 or len(suspect_high) > 0:
        print(f"\n[{col}]")
        print(f"  Range esperado: {min_s} a {max_s} (Hard: {min_h} a {max_h})")
        
        if len(invalid_low) > 0:
            print(f"  ❌ {len(invalid_low)} valores EXTREMAMENTE BAIXOS (< {min_h}):")
            for idx, v in invalid_low.head(3).items():
                emp = df.loc[idx, 'Empresa']
                print(f"     - {emp[:30]}: {v:.4f}")
                
        if len(invalid_high) > 0:
            print(f"  ❌ {len(invalid_high)} valores EXTREMAMENTE ALTOS (> {max_h}):")
            for idx, v in invalid_high.head(3).items():
                emp = df.loc[idx, 'Empresa']
                print(f"     - {emp[:30]}: {v:.4f}")
                
        if len(suspect_low) > 0:
            print(f"  ⚠️ {len(suspect_low)} valores suspeitos (baixos):")
            for idx, v in suspect_low.head(2).items():
                emp = df.loc[idx, 'Empresa']
                print(f"     - {emp[:30]}: {v:.4f}")

        if len(suspect_high) > 0:
            print(f"  ⚠️ {len(suspect_high)} valores suspeitos (altos):")
            for idx, v in suspect_high.head(2).items():
                emp = df.loc[idx, 'Empresa']
                print(f"     - {emp[:30]}: {v:.4f}")

def main():
    print("="*70)
    print("TESTE DE SANIDADE DAS FEATURES")
    print("="*70)
    
    df = pd.read_csv(CONSOLIDATED_PATH / "tabela_features.csv")
    print(f"Analisando {len(df)} empresas...")
    
    for col, limits in LIMITS.items():
        if col in df.columns:
            analyze_feature(df, col, limits)
        else:
            print(f"\n[AVISO] Coluna {col} não encontrada no dataset.")

    # Análise de Tamanho (Log Ativo) separada
    if 'Tamanho' in df.columns:
        print("\n[Tamanho (Log Ativo)]")
        print(df['Tamanho'].describe())
        # Tamanho < 10 significa ativo < 22k reais (muito pequeno para bolsa)
        pequenos = df[df['Tamanho'] < 10]
        if not pequenos.empty:
            print(f"  ⚠️ {len(pequenos)} empresas muito pequenas (Log < 10):")
            for _, r in pequenos.iterrows():
                print(f"     - {r['Empresa'][:30]}: {r['Tamanho']:.2f}")

if __name__ == "__main__":
    main()
