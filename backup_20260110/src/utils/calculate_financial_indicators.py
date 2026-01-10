#!/usr/bin/env python3
"""
Cálculo de indicadores financeiros a partir dos dados consolidados.
Baseado na literatura acadêmica revisada, especialmente:
- Eça & Albanez (2022): Heterogeneidade da dívida
- Fazzari et al. (1988): Restrições financeiras
- Kaplan & Zingales (1997): Índice KZ
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH


def safe_divide(numerator: float, denominator: float, default: float = np.nan) -> float:
    """
    Divisão segura que trata divisão por zero e valores negativos.
    
    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor padrão se divisão inválida
        
    Returns:
        Resultado da divisão ou default
    """
    if pd.isna(numerator) or pd.isna(denominator):
        return default
    if denominator == 0 or denominator < 0:
        return default
    return numerator / denominator


def calculate_leverage_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de alavancagem e estrutura de capital.
    
    Indicadores:
    - Divida_Total_Ativo: Dívida Total / Ativo Total
    - Divida_Total_Patrimonio: Dívida Total / Patrimônio Líquido (D/E ratio)
    - Alavancagem_Total: Dívida Total / (Dívida Total + Patrimônio Líquido)
    - Divida_Liquida_Ativo: (Dívida Total - Caixa) / Ativo Total
    - Proporcao_Divida_CP: Dívida Curto Prazo / Dívida Total
    - Proporcao_Divida_LP: Dívida Longo Prazo / Dívida Total
    """
    result = df[['Empresa']].copy()
    
    # Divida_Total_Ativo
    result['Divida_Total_Ativo'] = df.apply(
        lambda row: safe_divide(row.get('Divida_Total', 0), row.get('Ativo_Total', 0)),
        axis=1
    )
    
    # Divida_Total_Patrimonio (D/E ratio)
    result['Divida_Total_Patrimonio'] = df.apply(
        lambda row: safe_divide(
            row.get('Divida_Total', 0), 
            row.get('Patrimonio_Liquido', 0)
        ),
        axis=1
    )
    
    # Alavancagem_Total
    result['Alavancagem_Total'] = df.apply(
        lambda row: safe_divide(
            row.get('Divida_Total', 0),
            (row.get('Divida_Total', 0) + row.get('Patrimonio_Liquido', 0))
        ),
        axis=1
    )
    
    # Divida_Liquida_Ativo
    result['Divida_Liquida_Ativo'] = df.apply(
        lambda row: safe_divide(
            (row.get('Divida_Total', 0) - row.get('Caixa_Equivalentes', 0)),
            row.get('Ativo_Total', 0)
        ),
        axis=1
    )
    
    # Proporcao_Divida_CP
    result['Proporcao_Divida_CP'] = df.apply(
        lambda row: safe_divide(
            row.get('Divida_Curto_Prazo', 0),
            row.get('Divida_Total', 0)
        ),
        axis=1
    )
    
    # Proporcao_Divida_LP
    result['Proporcao_Divida_LP'] = df.apply(
        lambda row: safe_divide(
            row.get('Divida_Longo_Prazo', 0),
            row.get('Divida_Total', 0)
        ),
        axis=1
    )
    
    return result


def calculate_heterogeneity_indicators(df_financiamentos: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de heterogeneidade da dívida baseados em Eça & Albanez (2022).
    
    Indicadores:
    - IHH_Indexador: Índice de Herfindahl-Hirschman por indexador
    - IHH_Tipo_Financiamento: IHH por tipo de financiamento
    - Indice_Diversificacao: 1 - IHH_Indexador
    - Heterogeneidade_Combinada: (1 - IHH_Indexador) × (1 - IHH_Tipo_Financiamento)
    """
    if df_financiamentos.empty:
        return pd.DataFrame()
    
    # Converter valores numéricos
    df_financiamentos = df_financiamentos.copy()
    if 'consolidado_2024' in df_financiamentos.columns:
        df_financiamentos['consolidado_2024'] = pd.to_numeric(
            df_financiamentos['consolidado_2024'], errors='coerce'
        ).fillna(0)
    
    results = []
    
    for empresa, group_df in df_financiamentos.groupby('Empresa'):
        total_valor = group_df['consolidado_2024'].sum()
        
        if total_valor == 0:
            continue
        
        # IHH por Indexador
        indexador_proportions = group_df.groupby('indexador')['consolidado_2024'].sum() / total_valor
        ihh_indexador = (indexador_proportions ** 2).sum()
        
        # IHH por Tipo de Financiamento (usando descricao como proxy)
        tipo_proportions = group_df.groupby('descricao')['consolidado_2024'].sum() / total_valor
        ihh_tipo = (tipo_proportions ** 2).sum()
        
        # Índice de Diversificação
        indice_diversificacao = 1 - ihh_indexador
        
        # Heterogeneidade Combinada
        heterogeneidade_combinada = (1 - ihh_indexador) * (1 - ihh_tipo)
        
        results.append({
            'Empresa': empresa,
            'IHH_Indexador': ihh_indexador,
            'IHH_Tipo_Financiamento': ihh_tipo,
            'Indice_Diversificacao': indice_diversificacao,
            'Heterogeneidade_Combinada': heterogeneidade_combinada
        })
    
    return pd.DataFrame(results)


def calculate_liquidity_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de liquidez.
    
    Indicadores:
    - Liquidez_Corrente: Ativo Circulante / Passivo Circulante
    - Liquidez_Seca: (Ativo Circulante - Estoques) / Passivo Circulante
      (Nota: Como não temos estoques, usamos Ativo_Circulante como proxy)
    - Liquidez_Imediata: Caixa / Passivo Circulante
    - Cobertura_Caixa_Divida: Caixa / Dívida Total
    """
    result = df[['Empresa']].copy()
    
    # Liquidez_Corrente
    result['Liquidez_Corrente'] = df.apply(
        lambda row: safe_divide(
            row.get('Ativo_Circulante', 0),
            row.get('Passivo_Circulante', 0)
        ),
        axis=1
    )
    
    # Liquidez_Seca (sem dados de estoques, usamos AC como proxy)
    result['Liquidez_Seca'] = df.apply(
        lambda row: safe_divide(
            row.get('Ativo_Circulante', 0),
            row.get('Passivo_Circulante', 0)
        ),
        axis=1
    )
    
    # Liquidez_Imediata
    result['Liquidez_Imediata'] = df.apply(
        lambda row: safe_divide(
            row.get('Caixa_Equivalentes', 0),
            row.get('Passivo_Circulante', 0)
        ),
        axis=1
    )
    
    # Cobertura_Caixa_Divida
    result['Cobertura_Caixa_Divida'] = df.apply(
        lambda row: safe_divide(
            row.get('Caixa_Equivalentes', 0),
            row.get('Divida_Total', 0)
        ),
        axis=1
    )
    
    return result


def calculate_profitability_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de rentabilidade.
    
    Indicadores:
    - ROA: Lucro Líquido / Ativo Total
    - ROA_Operacional: Lucro Operacional / Ativo Total
    - ROA_EBITDA: EBITDA / Ativo Total
    - ROE: Lucro Líquido / Patrimônio Líquido
    - Margem_Bruta: Lucro Bruto / Receita Líquida
    - Margem_Operacional: Lucro Operacional / Receita Líquida
    - Margem_Liquida: Lucro Líquido / Receita Líquida
    - Margem_EBITDA: EBITDA / Receita Líquida
    """
    result = df[['Empresa']].copy()
    
    # ROA
    result['ROA'] = df.apply(
        lambda row: safe_divide(
            row.get('Lucro_Liquido', 0),
            row.get('Ativo_Total', 0)
        ),
        axis=1
    )
    
    # ROA_Operacional
    result['ROA_Operacional'] = df.apply(
        lambda row: safe_divide(
            row.get('Lucro_Operacional', 0),
            row.get('Ativo_Total', 0)
        ),
        axis=1
    )
    
    # ROA_EBITDA
    result['ROA_EBITDA'] = df.apply(
        lambda row: safe_divide(
            row.get('EBITDA', 0),
            row.get('Ativo_Total', 0)
        ),
        axis=1
    )
    
    # ROE
    result['ROE'] = df.apply(
        lambda row: safe_divide(
            row.get('Lucro_Liquido', 0),
            row.get('Patrimonio_Liquido', 0)
        ),
        axis=1
    )
    
    # Margem_Bruta
    result['Margem_Bruta'] = df.apply(
        lambda row: safe_divide(
            row.get('Lucro_Bruto', 0),
            row.get('Receita_Liquida', 0)
        ),
        axis=1
    )
    
    # Margem_Operacional
    result['Margem_Operacional'] = df.apply(
        lambda row: safe_divide(
            row.get('Lucro_Operacional', 0),
            row.get('Receita_Liquida', 0)
        ),
        axis=1
    )
    
    # Margem_Liquida
    result['Margem_Liquida'] = df.apply(
        lambda row: safe_divide(
            row.get('Lucro_Liquido', 0),
            row.get('Receita_Liquida', 0)
        ),
        axis=1
    )
    
    # Margem_EBITDA
    result['Margem_EBITDA'] = df.apply(
        lambda row: safe_divide(
            row.get('EBITDA', 0),
            row.get('Receita_Liquida', 0)
        ),
        axis=1
    )
    
    return result


## REMOVED: calculate_kd_related_indicators
# This function was removed because these indicators use Kd in their calculation,
# which causes data leakage when Kd is the target variable in regression models.
# Removed indicators: Spread_Medio, Coeficiente_Variacao_Kd, Range_Kd, 
# Range_Kd_Relativo, Diferenca_Kd_Ponderado_Simples


def calculate_financial_constraint_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de restrições financeiras.
    Baseado em Kaplan & Zingales (1997) e Fazzari et al. (1988).
    
    Indicadores:
    - KZ_Index: Índice Kaplan-Zingales (versão simplificada)
    - Restricao_Financeira_Simplificada: Score 0-1 baseado em múltiplos fatores
    - FCF_Operacional: EBITDA - Despesas_Financeiras (aproximado)
    - FCF_Ativo: FCF_Operacional / Ativo_Total
    """
    result = df[['Empresa']].copy()
    
    # KZ Index (versão simplificada)
    # KZ = -1.002 × (CF/Ativo) + 0.283 × Q + 3.139 × (Divida/Ativo) - 39.368 × (Dividendos/Ativo) - 1.315 × (Caixa/Ativo)
    # Como não temos Q (Tobin's Q) e Dividendos, usamos versão simplificada:
    result['KZ_Index'] = df.apply(
        lambda row: (
            -1.002 * safe_divide(row.get('Lucro_Liquido', 0), row.get('Ativo_Total', 0), 0) +
            3.139 * safe_divide(row.get('Divida_Total', 0), row.get('Ativo_Total', 0), 0) -
            1.315 * safe_divide(row.get('Caixa_Equivalentes', 0), row.get('Ativo_Total', 0), 0)
        ),
        axis=1
    )
    
    # Restrição Financeira Simplificada (score 0-1)
    # Combina: baixa liquidez + alta alavancagem + baixa rentabilidade
    # Calcular liquidez corrente e ROA diretamente
    result['Restricao_Financeira_Simplificada'] = df.apply(
        lambda row: (
            (1 - min(safe_divide(row.get('Ativo_Circulante', 0), row.get('Passivo_Circulante', 0), 0) / 2.0, 1.0)) * 0.33 +
            min(safe_divide(row.get('Divida_Total', 0), row.get('Ativo_Total', 0), 0), 1.0) * 0.33 +
            (1 - min(max(safe_divide(row.get('Lucro_Liquido', 0), row.get('Ativo_Total', 0), 0) / 0.1, 0), 1.0)) * 0.34
        ),
        axis=1
    )
    
    # FCF_Operacional (aproximado: EBITDA - Despesas Financeiras)
    result['FCF_Operacional'] = df.apply(
        lambda row: (
            (row.get('EBITDA', 0) or 0) - (row.get('Despesas_Financeiras', 0) or 0)
        ),
        axis=1
    )
    
    # FCF_Ativo
    result['FCF_Ativo'] = df.apply(
        lambda row: safe_divide(
            result.loc[result['Empresa'] == row['Empresa'], 'FCF_Operacional'].values[0] if len(result.loc[result['Empresa'] == row['Empresa']]) > 0 else 0,
            row.get('Ativo_Total', 0)
        ),
        axis=1
    )
    
    # Corrigir FCF_Ativo (calcular diretamente)
    result['FCF_Ativo'] = df.apply(
        lambda row: safe_divide(
            (row.get('EBITDA', 0) or 0) - (row.get('Despesas_Financeiras', 0) or 0),
            row.get('Ativo_Total', 0)
        ),
        axis=1
    )
    
    return result


def calculate_coverage_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de cobertura e capacidade de pagamento.
    
    Indicadores:
    - Cobertura_Juros: EBITDA / Despesas_Financeiras
    - Cobertura_Divida_EBITDA: Dívida Total / EBITDA
    - Cobertura_Divida_Liquida_EBITDA: (Dívida Total - Caixa) / EBITDA
    """
    result = df[['Empresa']].copy()
    
    # Cobertura_Juros
    result['Cobertura_Juros'] = df.apply(
        lambda row: safe_divide(
            row.get('EBITDA', 0),
            row.get('Despesas_Financeiras', 0)
        ),
        axis=1
    )
    
    # Cobertura_Divida_EBITDA
    result['Cobertura_Divida_EBITDA'] = df.apply(
        lambda row: safe_divide(
            row.get('Divida_Total', 0),
            row.get('EBITDA', 0)
        ),
        axis=1
    )
    
    # Cobertura_Divida_Liquida_EBITDA
    result['Cobertura_Divida_Liquida_EBITDA'] = df.apply(
        lambda row: safe_divide(
            (row.get('Divida_Total', 0) - row.get('Caixa_Equivalentes', 0)),
            row.get('EBITDA', 0)
        ),
        axis=1
    )
    
    return result


def calculate_composition_indicators(df_kd: pd.DataFrame, df_financiamentos: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores de composição e estrutura dos financiamentos.
    
    Indicadores:
    - Concentracao_Financiamentos: 1 / Total_Financiamentos
    - Diversidade_Indexadores: Indexadores_Unicos / Total_Financiamentos
    - Diversidade_Tipos: Tipos_Financiamento_Unicos / Total_Financiamentos
    """
    result = df_kd[['Empresa']].copy()
    
    # Concentracao_Financiamentos
    result['Concentracao_Financiamentos'] = df_kd.apply(
        lambda row: safe_divide(1, row.get('Total_Financiamentos', 1)),
        axis=1
    )
    
    # Diversidade_Indexadores
    result['Diversidade_Indexadores'] = df_kd.apply(
        lambda row: safe_divide(
            row.get('Indexadores_Unicos', 0),
            row.get('Total_Financiamentos', 1)
        ),
        axis=1
    )
    
    # Diversidade_Tipos
    result['Diversidade_Tipos'] = df_kd.apply(
        lambda row: safe_divide(
            row.get('Tipos_Financiamento_Unicos', 0),
            row.get('Total_Financiamentos', 1)
        ),
        axis=1
    )
    
    return result


## REMOVED: calculate_comparative_indicators
# This function was removed because these indicators use Kd in their calculation,
# which causes data leakage when Kd is the target variable in regression models.
# Removed indicators: Spread_ROA_Kd, Kd_Alavancagem_Ratio, Eficiencia_Endividamento


def calculate_prazo_medio_divida(df_financiamentos: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula prazo médio da dívida baseado nos vencimentos dos financiamentos.
    
    Indicador:
    - Prazo_Medio_Divida: Média ponderada dos vencimentos (em dias)
    """
    if df_financiamentos.empty or 'vencimento' not in df_financiamentos.columns:
        return pd.DataFrame(columns=['Empresa', 'Prazo_Medio_Divida'])
    
    # Converter valores numéricos
    df_financiamentos = df_financiamentos.copy()
    if 'consolidado_2024' in df_financiamentos.columns:
        df_financiamentos['consolidado_2024'] = pd.to_numeric(
            df_financiamentos['consolidado_2024'], errors='coerce'
        ).fillna(0)
    
    results = []
    
    for empresa, group_df in df_financiamentos.groupby('Empresa'):
        try:
            # Converter vencimentos para datetime e calcular dias até hoje
            hoje = datetime.now()
            vencimentos_dias = []
            valores = []
            
            for _, row in group_df.iterrows():
                vencimento_str = str(row.get('vencimento', ''))
                if pd.notna(vencimento_str) and vencimento_str:
                    try:
                        # Tentar diferentes formatos de data
                        if '/' in vencimento_str:
                            vencimento = datetime.strptime(vencimento_str, '%d/%m/%Y')
                        else:
                            vencimento = pd.to_datetime(vencimento_str)
                        
                        dias_ate_vencimento = (vencimento - hoje).days
                        if dias_ate_vencimento > 0:
                            vencimentos_dias.append(dias_ate_vencimento)
                            valores.append(float(row.get('consolidado_2024', 0)))
                    except:
                        continue
            
            if vencimentos_dias and valores:
                # Média ponderada
                total_valor = sum(valores)
                if total_valor > 0:
                    prazo_medio = sum(d * v for d, v in zip(vencimentos_dias, valores)) / total_valor
                    results.append({
                        'Empresa': empresa,
                        'Prazo_Medio_Divida': prazo_medio
                    })
        except Exception as e:
            continue
    
    return pd.DataFrame(results)


def calculate_all_indicators(
    df_financial: pd.DataFrame,
    df_kd: pd.DataFrame,
    df_financiamentos: pd.DataFrame
) -> pd.DataFrame:
    """
    Calcula todos os indicadores financeiros e consolida em um único DataFrame.
    
    Args:
        df_financial: DataFrame com dados financeiros (balanço + DRE)
        df_kd: DataFrame com dados de Kd por empresa
        df_financiamentos: DataFrame com dados detalhados de financiamentos
        
    Returns:
        DataFrame consolidado com todos os indicadores
    """
    # Começar com a coluna Empresa
    result = df_financial[['Empresa']].copy()
    
    # 1. Indicadores de Alavancagem
    print("Calculando indicadores de alavancagem...")
    leverage = calculate_leverage_indicators(df_financial)
    result = result.merge(leverage, on='Empresa', how='left')
    
    # 2. Indicadores de Heterogeneidade
    print("Calculando indicadores de heterogeneidade...")
    heterogeneity = calculate_heterogeneity_indicators(df_financiamentos)
    if not heterogeneity.empty:
        result = result.merge(heterogeneity, on='Empresa', how='left')
    
    # 3. Indicadores de Liquidez
    print("Calculando indicadores de liquidez...")
    liquidity = calculate_liquidity_indicators(df_financial)
    result = result.merge(liquidity, on='Empresa', how='left')
    
    # 4. Indicadores de Rentabilidade
    print("Calculando indicadores de rentabilidade...")
    profitability = calculate_profitability_indicators(df_financial)
    result = result.merge(profitability, on='Empresa', how='left')
    
    # 5. REMOVED: Indicadores relacionados ao Kd (data leakage - usam Kd no cálculo)
    
    # 6. Indicadores de Restrições Financeiras
    print("Calculando indicadores de restrições financeiras...")
    # Precisamos de liquidez corrente primeiro
    if 'Liquidez_Corrente' not in result.columns:
        liquidity_temp = calculate_liquidity_indicators(df_financial)
        result = result.merge(liquidity_temp[['Empresa', 'Liquidez_Corrente']], on='Empresa', how='left')
    
    # Adicionar ROA temporariamente se não existir
    if 'ROA' not in result.columns:
        profitability_temp = calculate_profitability_indicators(df_financial)
        result = result.merge(profitability_temp[['Empresa', 'ROA']], on='Empresa', how='left')
    
    constraints = calculate_financial_constraint_indicators(df_financial)
    result = result.merge(constraints, on='Empresa', how='left')
    
    # 7. Indicadores de Cobertura
    print("Calculando indicadores de cobertura...")
    coverage = calculate_coverage_indicators(df_financial)
    result = result.merge(coverage, on='Empresa', how='left')
    
    # 8. Indicadores de Composição
    print("Calculando indicadores de composição...")
    composition = calculate_composition_indicators(df_kd, df_financiamentos)
    result = result.merge(composition, on='Empresa', how='left')
    
    # 9. Prazo Médio da Dívida
    print("Calculando prazo médio da dívida...")
    prazo_medio = calculate_prazo_medio_divida(df_financiamentos)
    if not prazo_medio.empty:
        result = result.merge(prazo_medio, on='Empresa', how='left')
    
    # 10. REMOVED: Indicadores Comparativos (data leakage - usam Kd no cálculo)
    
    # Adicionar Kd_Ponderado para uso como variável dependente
    if 'Kd_Ponderado' not in result.columns:
        result = result.merge(df_kd[['Empresa', 'Kd_Ponderado']], on='Empresa', how='left')
    
    return result


def main():
    """Função principal para executar o cálculo de indicadores."""
    print("=" * 80)
    print("CÁLCULO DE INDICADORES FINANCEIROS")
    print("=" * 80)
    
    # Carregar dados
    print("\nCarregando dados...")
    df_financial = pd.read_csv(CONSOLIDATED_PATH / "dados_financeiros_brutos.csv")
    df_kd = pd.read_csv(CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv")
    df_financiamentos = pd.read_csv(CONSOLIDATED_PATH / "financiamentos_consolidados.csv")
    
    # Converter colunas numéricas
    numeric_cols_financial = [
        'Ativo_Total', 'Passivo_Total', 'Patrimonio_Liquido', 'Divida_Total',
        'Divida_Curto_Prazo', 'Divida_Longo_Prazo', 'Caixa_Equivalentes',
        'Ativo_Circulante', 'Passivo_Circulante', 'Ativo_Nao_Circulante',
        'Passivo_Nao_Circulante', 'Receita_Liquida', 'Lucro_Bruto', 'EBITDA',
        'Lucro_Operacional', 'Lucro_Liquido', 'Despesas_Financeiras', 'Receitas_Financeiras'
    ]
    for col in numeric_cols_financial:
        if col in df_financial.columns:
            df_financial[col] = pd.to_numeric(df_financial[col], errors='coerce')
    
    numeric_cols_kd = [
        'Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos',
        'Valor_Consolidado_Total', 'Kd_Medio_Simples', 'Kd_Desvio_Padrao',
        'Kd_Min', 'Kd_Max', 'Indexadores_Unicos', 'Tipos_Financiamento_Unicos'
    ]
    for col in numeric_cols_kd:
        if col in df_kd.columns:
            df_kd[col] = pd.to_numeric(df_kd[col], errors='coerce')
    
    if 'consolidado_2024' in df_financiamentos.columns:
        df_financiamentos['consolidado_2024'] = pd.to_numeric(
            df_financiamentos['consolidado_2024'], errors='coerce'
        ).fillna(0)
    
    print(f"  - Dados financeiros: {len(df_financial)} empresas")
    print(f"  - Dados de Kd: {len(df_kd)} empresas")
    print(f"  - Financiamentos: {len(df_financiamentos)} registros")
    
    # Calcular indicadores
    print("\nCalculando indicadores...")
    df_indicators = calculate_all_indicators(df_financial, df_kd, df_financiamentos)
    
    # Salvar resultado
    output_file = CONSOLIDATED_PATH / "indicadores_financeiros_completos.csv"
    df_indicators.to_csv(output_file, index=False)
    
    print(f"\n✓ Indicadores calculados e salvos em: {output_file}")
    print(f"  Total de empresas: {len(df_indicators)}")
    print(f"  Total de indicadores: {len(df_indicators.columns) - 1}")  # -1 para coluna Empresa
    
    # Estatísticas básicas
    print("\nEstatísticas básicas dos indicadores:")
    print(df_indicators.describe())
    
    return df_indicators


if __name__ == "__main__":
    main()

