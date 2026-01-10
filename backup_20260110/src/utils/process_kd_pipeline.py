"""
Pipeline completo para processamento de indexadores e cálculo de Kd.
"""
import pandas as pd
import numpy as np
import re
from pathlib import Path
import sys
from typing import Dict, Optional

# Adiciona o diretório 'src' ao sys.path
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH
from utils.standardize_indexers import standardize_indexer
from utils.calculate_kd import calculate_kd


def convert_consolidado_to_numeric(value: any) -> Optional[float]:
    """
    Converte valor consolidado para numérico.
    
    Args:
        value: Valor a converter (pode ser string, número, etc.)
        
    Returns:
        Valor numérico ou None se não for possível converter
    """
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove espaços e caracteres especiais
        value = value.strip().replace(' ', '').replace('.', '').replace(',', '.')
        # Remove R$, $, etc.
        value = re.sub(r'[R$]', '', value, flags=re.IGNORECASE)
        try:
            return float(value)
        except ValueError:
            return None
    
    return None


def process_kd_pipeline(input_file: Path, output_file: Path) -> pd.DataFrame:
    """
    Processa planilha completa e calcula Kd para cada registro.
    
    Args:
        input_file: Caminho do arquivo Excel de entrada
        output_file: Caminho do arquivo CSV de saída
        
    Returns:
        DataFrame com resultados processados
    """
    print(f"📖 Carregando dados de: {input_file.name}")
    
    # Carrega dados
    df = pd.read_excel(input_file, sheet_name=0)
    print(f"   ✅ {len(df)} registros carregados")
    
    # Valida colunas necessárias
    required_cols = ['Empresa', 'descricao', 'indexador', 'consolidado_2024']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas faltando: {missing_cols}")
    
    # Lista para armazenar resultados
    results = []
    
    print(f"\n🔄 Processando {len(df)} registros...")
    
    for idx, row in df.iterrows():
        if (idx + 1) % 100 == 0:
            print(f"   Processados: {idx + 1}/{len(df)}")
        
        # Padroniza indexador
        indexer_result = standardize_indexer(row['indexador'])
        
        # Calcula Kd
        kd_result = calculate_kd(
            indexer_type=indexer_result['indexer_type'],
            spread=indexer_result['spread'],
            period=indexer_result['period'],
            is_prefixed=indexer_result['is_prefixed']
        )
        
        # Converte valor consolidado
        valor_consolidado = convert_consolidado_to_numeric(row['consolidado_2024'])
        
        # Combina observações
        all_observations = indexer_result['observations'] + kd_result['observations']
        observations_str = '; '.join(all_observations) if all_observations else ''
        
        # Cria registro de resultado
        result_row = {
            'Empresa': row['Empresa'],
            'Indexador_Processado': indexer_result['indexer_type'] or 'NÃO_IDENTIFICADO',
            'Spread_Percentual': (indexer_result['spread'] * 100) if indexer_result['spread'] is not None else None,
            'Tipo_Financiamento': row['descricao'],
            'Valor_Consolidado_2024': valor_consolidado,
            'Kd_Percentual': kd_result['kd_percentual'],
            'Kd_Decimal': kd_result['kd_decimal'],
            'Periodo_Original': indexer_result['period'],
            'Base_Indexador': kd_result['base_value'],
            'Observacoes': observations_str,
            'Kd_Valido': kd_result['is_valid']
        }
        
        results.append(result_row)
    
    # Cria DataFrame de resultados
    df_results = pd.DataFrame(results)
    
    print(f"\n✅ Processamento concluído!")
    print(f"   Total processado: {len(df_results)}")
    print(f"   Kd calculado: {df_results['Kd_Percentual'].notna().sum()}")
    print(f"   Kd válido: {df_results['Kd_Valido'].sum()}")
    
    # Salva CSV
    df_results.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 CSV salvo em: {output_file}")
    
    return df_results


def main():
    """Função principal."""
    # Arquivo de entrada
    input_file = CONSOLIDATED_PATH / "emp_e_fin_novo_mercado_20250920.xlsx"
    
    if not input_file.exists():
        # Tenta outros arquivos
        files = list(CONSOLIDATED_PATH.glob("emp_e_fin_novo_mercado*.xlsx"))
        if files:
            input_file = max(files, key=lambda x: x.stat().st_mtime)
            print(f"Usando arquivo: {input_file.name}")
        else:
            print("❌ Arquivo não encontrado!")
            return
    
    # Arquivo de saída
    output_file = CONSOLIDATED_PATH / "kd_calculated.csv"
    
    # Processa
    df_results = process_kd_pipeline(input_file, output_file)
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Indexadores processados:")
    print(df_results['Indexador_Processado'].value_counts().head(10))
    print(f"\n   Distribuição de Kd:")
    print(df_results['Kd_Percentual'].describe())
    
    return df_results


if __name__ == "__main__":
    import re
    main()

