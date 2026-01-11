#!/usr/bin/env python3
"""
Cálculo de Features para Modelo de Determinantes do Kd

Este script calcula indicadores financeiros a partir do CSV bruto extraído
dos Excel das DFPs e gera a tabela de features para o modelo de regressão.

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH

# -----------------------------------------------------------------------------
# MAPEAMENTO CÓDIGOS CVM → VARIÁVEIS
# -----------------------------------------------------------------------------
CVM_MAPPING = {
    # Ativo
    'Ativo_Total': 'AT_1',
    'Ativo_Circulante': 'AT_1.01',
    'Ativo_Nao_Circulante': 'AT_1.02',
    'Caixa': 'AT_1.01.01',
    'Ativo_Imobilizado': 'AT_1.02.03',  # Imobilizado
    
    # Passivo
    'Passivo_Total': 'PS_2',
    'Passivo_Circulante': 'PS_2.01',
    'Passivo_Nao_Circulante': 'PS_2.02',
    'Patrimonio_Liquido': 'PS_2.03',
    'Divida_CP': 'PS_2.01.04',  # Empréstimos e Financiamentos CP
    'Divida_LP': 'PS_2.02.01',  # Empréstimos e Financiamentos LP
    
    # DRE
    'Receita_Liquida': 'DRE_3.01',
    'Lucro_Bruto': 'DRE_3.03',
    'EBIT': 'DRE_3.05',  # Resultado antes do financeiro
    'Resultado_Financeiro': 'DRE_3.06',
    'Receitas_Financeiras': 'DRE_3.06.01',
    'Despesas_Financeiras': 'DRE_3.06.02',
    'Lucro_Liquido': 'DRE_3.11',
    
    # Fluxo de Caixa
    'FC_Operacional': 'FC_6.01',
    'FC_Investimento': 'FC_6.02',
    'FC_Financiamento': 'FC_6.03',
}


# -----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------------
def safe_divide(num, den, default=np.nan):
    """Divisão segura que trata divisão por zero."""
    if pd.isna(num) or pd.isna(den) or den == 0:
        return default
    return num / den


def parse_value(val, is_us_format=False):
    """Converte valor para float, tratando formatos BR e US."""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s == '' or s.lower() == 'nan':
        return np.nan
    
    # Se detectado formato US (ex: PDG Realty)
    if is_us_format:
        # Remover vírgulas de milhar (ex: 1,234.56 -> 1234.56)
        s = s.replace(',', '')
        try:
            return float(s)
        except:
            return np.nan

    # Formato BR: 1.234.567,89 -> remover pontos, trocar vírgula
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    # Formato BR sem vírgula (ex: 3.346.770) = múltiplos pontos = separador de milhar
    elif s.count('.') > 1:
        s = s.replace('.', '')
    # Um único ponto: verificar se é milhar BR ou decimal
    elif s.count('.') == 1:
        # Se tiver 3 dígitos após o ponto, provavelmente é milhar BR
        parts = s.split('.')
        if len(parts[1]) == 3 and len(parts[0]) <= 3:
            s = s.replace('.', '')  # É milhar
        # Senão, manter como decimal (fallback seguro)
    
    try:
        return float(s)
    except:
        return np.nan


def get_var(row, var_name, cvm_code=None):
    """Obtém variável da linha, usando mapeamento ou código direto."""
    if cvm_code is None:
        cvm_code = CVM_MAPPING.get(var_name)
    if cvm_code is None:
        return np.nan
    
    # Obter flag de formato da linha (injetada no loop)
    is_us_format = row.get('IS_US_FORMAT', False)
    
    return parse_value(row.get(cvm_code, np.nan), is_us_format)


# -----------------------------------------------------------------------------
# CÁLCULO DE INDICADORES
# -----------------------------------------------------------------------------
def calculate_leverage(row):
    """Indicadores de Alavancagem."""
    ativo = get_var(row, 'Ativo_Total')
    pl = get_var(row, 'Patrimonio_Liquido')
    divida_cp = get_var(row, 'Divida_CP')
    divida_lp = get_var(row, 'Divida_LP')
    caixa = get_var(row, 'Caixa')
    
    # Dívida Total = CP + LP
    divida_total = (divida_cp or 0) + (divida_lp or 0)
    
    return {
        'Divida_Total': divida_total,
        'Divida_Total_Ativo': safe_divide(divida_total, ativo),
        'Divida_Total_PL': safe_divide(divida_total, pl),
        'Alavancagem_Total': safe_divide(divida_total, divida_total + pl) if pl and pl > 0 else np.nan,
        'Divida_Liquida_Ativo': safe_divide(divida_total - (caixa or 0), ativo),
        'Proporcao_Divida_CP': safe_divide(divida_cp, divida_total),
        'Proporcao_Divida_LP': safe_divide(divida_lp, divida_total),
    }


def calculate_liquidity(row):
    """Indicadores de Liquidez."""
    ac = get_var(row, 'Ativo_Circulante')
    pc = get_var(row, 'Passivo_Circulante')
    caixa = get_var(row, 'Caixa')
    divida_cp = get_var(row, 'Divida_CP')
    divida_lp = get_var(row, 'Divida_LP')
    divida_total = (divida_cp or 0) + (divida_lp or 0)
    
    return {
        'Liquidez_Corrente': safe_divide(ac, pc),
        'Liquidez_Imediata': safe_divide(caixa, pc),
        'Cobertura_Caixa_Divida': safe_divide(caixa, divida_total),
    }


def calculate_profitability(row):
    """Indicadores de Rentabilidade."""
    ativo = get_var(row, 'Ativo_Total')
    pl = get_var(row, 'Patrimonio_Liquido')
    receita = get_var(row, 'Receita_Liquida')
    lucro_bruto = get_var(row, 'Lucro_Bruto')
    ebit = get_var(row, 'EBIT')
    lucro_liquido = get_var(row, 'Lucro_Liquido')
    fc_op = get_var(row, 'FC_Operacional')
    
    # EBITDA aproximado = EBIT + Depreciação
    # Como não temos depreciação separada, usamos FC Operacional como proxy
    # ajustado: EBITDA ≈ EBIT * 1.15 (margem típica de D&A)
    ebitda = ebit * 1.15 if ebit and not pd.isna(ebit) else np.nan
    
    return {
        'ROA': safe_divide(lucro_liquido, ativo),
        'ROE': safe_divide(lucro_liquido, pl),
        'Margem_Bruta': safe_divide(lucro_bruto, receita),
        'Margem_Operacional': safe_divide(ebit, receita),
        'Margem_Liquida': safe_divide(lucro_liquido, receita),
        'Margem_EBITDA': safe_divide(ebitda, receita),
        'EBITDA': ebitda,
    }


def calculate_coverage(row, divida_total, ebitda):
    """Indicadores de Cobertura."""
    desp_fin = get_var(row, 'Despesas_Financeiras')
    
    # Despesas financeiras são negativas no DRE, usar valor absoluto
    desp_fin_abs = abs(desp_fin) if desp_fin and not pd.isna(desp_fin) else np.nan
    
    return {
        'Cobertura_Juros': safe_divide(ebitda, desp_fin_abs),
        'Divida_EBITDA': safe_divide(divida_total, ebitda),
    }


def calculate_additional(row):
    """Indicadores Adicionais (da pesquisa web)."""
    ativo = get_var(row, 'Ativo_Total')
    ac = get_var(row, 'Ativo_Circulante')
    pc = get_var(row, 'Passivo_Circulante')
    imobilizado = get_var(row, 'Ativo_Imobilizado')
    fc_inv = get_var(row, 'FC_Investimento')
    fc_op = get_var(row, 'FC_Operacional')
    
    return {
        'Tamanho': np.log(ativo) if ativo and ativo > 0 else np.nan,
        'Tangibilidade': safe_divide(imobilizado, ativo),
        'Capital_Giro_Liquido': safe_divide((ac or 0) - (pc or 0), ativo),
        'Intensidade_Capex': safe_divide(abs(fc_inv) if fc_inv else np.nan, ativo),
        'Geracao_Caixa_Op': safe_divide(fc_op, ativo),
    }


def calculate_heterogeneity(empresa, df_fin):
    """Indicadores de Heterogeneidade da Dívida (Eça & Albanez 2022)."""
    group = df_fin[df_fin['Empresa'] == empresa].copy()
    
    if group.empty:
        return {
            'IHH_Indexador': np.nan,
            'IHH_Tipo': np.nan,
            'Indice_Diversificacao': np.nan,
        }
    
    # Usar valores absolutos positivos do consolidado_2024
    group['valor_abs'] = group['consolidado_2024'].abs()
    group = group[group['valor_abs'] > 0]  # Filtrar zeros
    
    total_valor = group['valor_abs'].sum()
    if total_valor == 0:
        return {
            'IHH_Indexador': np.nan,
            'IHH_Tipo': np.nan,
            'Indice_Diversificacao': np.nan,
        }
    
    # IHH por Indexador (proporções baseadas em valores absolutos)
    idx_props = group.groupby('indexador')['valor_abs'].sum() / total_valor
    ihh_idx = (idx_props ** 2).sum()
    
    # IHH por Tipo (usando descricao)
    tipo_props = group.groupby('descricao')['valor_abs'].sum() / total_valor
    ihh_tipo = (tipo_props ** 2).sum()
    
    # Garantir que IHH está entre 0 e 1
    ihh_idx = min(ihh_idx, 1.0)
    ihh_tipo = min(ihh_tipo, 1.0)
    
    return {
        'IHH_Indexador': ihh_idx,
        'IHH_Tipo': ihh_tipo,
        'Indice_Diversificacao': 1 - ihh_idx,
    }


# -----------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# -----------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("CÁLCULO DE FEATURES PARA MODELO DE KD")
    print("=" * 70)
    
    # Carregar dados
    print("\n1. Carregando dados...")
    df_raw = pd.read_csv(CONSOLIDATED_PATH / "dados_financeiros_excel_bruto.csv")
    df_kd = pd.read_csv(CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv")
    df_fin = pd.read_csv(CONSOLIDATED_PATH / "financiamentos_consolidados.csv")
    
    # Converter consolidado_2024 para numérico
    df_fin['consolidado_2024'] = pd.to_numeric(df_fin['consolidado_2024'], errors='coerce').fillna(0)
    
    print(f"   → {len(df_raw)} empresas com dados financeiros")
    print(f"   → {len(df_kd)} empresas com Kd")
    print(f"   → {len(df_fin)} financiamentos")
    
    # Calcular features
    print("\n2. Calculando indicadores...")
    features = []
    
    for idx, row in df_raw.iterrows():
        cod_cvm = row['Cod_CVM']
        empresa = row['Empresa']
        
        # Detecção de formato da linha
        # Verificar se linha usa formato BR (vírgula decimal) ou US (ponto decimal)
        # Heurística: 
        # 1. Se tem vírgula -> BR
        # 2. Se tem ponto com != 3 casas decimais (ex: 534.65) -> US
        # 3. Default -> BR (assumindo ponto como milhar)
        
        is_us_format = False
        row_str = row.astype(str).values
        
        # Checar smoking guns
        has_comma = any(',' in s for s in row_str)
        if not has_comma:
            # Se não tem vírgula, ver se tem ponto que parece decimal (ex: .45 ou .5)
            # Ignora .000 ou .123 (ambíguo)
            import re
            # Padrão: Ponto seguido de 1, 2, 4+ dígitos (não 3)
            # Ou ponto seguido de 3 dígitos mas valor pequeno? Difícil.
            # Focando em 2 dígitos (.XX) que é comum em US financeiro
            for s in row_str:
                if re.search(r'\.\d{2}$', s) or re.search(r'\.\d{1}$', s):
                    is_us_format = True
                    break
        
        # Wrapper para passar o formato
        row['IS_US_FORMAT'] = is_us_format
        
        # Indicadores
        leverage = calculate_leverage(row)
        liquidity = calculate_liquidity(row)
        profitability = calculate_profitability(row)
        coverage = calculate_coverage(row, leverage['Divida_Total'], profitability['EBITDA'])
        additional = calculate_additional(row)
        heterogeneity = calculate_heterogeneity(empresa, df_fin)
        
        # Consolidar
        record = {
            'Cod_CVM': cod_cvm,
            'Empresa': empresa,
        }
        record.update(leverage)
        record.update(liquidity)
        record.update(profitability)
        record.update(coverage)
        record.update(additional)
        record.update(heterogeneity)
        
        features.append(record)
    
    df_features = pd.DataFrame(features)
    
    # Agregar Kd por Cod_CVM (média ponderada por valor consolidado)
    # Isso trata SPEs que compartilham o mesmo Cod_CVM da holding
    df_kd_agg = df_kd.groupby('Cod_CVM').agg({
        'Kd_Ponderado': 'mean',  # Média das SPEs
        'Valor_Consolidado_Total': 'sum',
    }).reset_index()
    
    # Adicionar Kd_Ponderado
    df_features = df_features.merge(
        df_kd_agg[['Cod_CVM', 'Kd_Ponderado']], 
        on='Cod_CVM', 
        how='left'
    )
    
    # Remover Divida_Total e EBITDA (intermediários)
    # Manter apenas indicadores finais
    cols_to_keep = [
        'Cod_CVM', 'Empresa', 'Kd_Ponderado',
        # Alavancagem
        'Divida_Total_Ativo', 'Divida_Total_PL', 'Alavancagem_Total',
        'Divida_Liquida_Ativo', 'Proporcao_Divida_CP', 'Proporcao_Divida_LP',
        # Liquidez
        'Liquidez_Corrente', 'Liquidez_Imediata', 'Cobertura_Caixa_Divida',
        # Rentabilidade
        'ROA', 'ROE', 'Margem_Bruta', 'Margem_Operacional', 'Margem_Liquida', 'Margem_EBITDA',
        # Cobertura
        'Cobertura_Juros', 'Divida_EBITDA',
        # Adicionais
        'Tamanho', 'Tangibilidade', 'Capital_Giro_Liquido', 'Intensidade_Capex', 'Geracao_Caixa_Op',
        # Heterogeneidade
        'IHH_Indexador', 'IHH_Tipo', 'Indice_Diversificacao',
    ]
    
    df_features = df_features[[c for c in cols_to_keep if c in df_features.columns]]
    
    print(f"   → {len(df_features)} empresas")
    print(f"   → {len(df_features.columns) - 3} indicadores + chaves + target")
    
    # Estatísticas
    print("\n3. Estatísticas de NaN por indicador:")
    for col in df_features.columns:
        if col not in ['Cod_CVM', 'Empresa']:
            pct_nan = df_features[col].isna().sum() / len(df_features) * 100
            if pct_nan > 0:
                print(f"   {col:25}: {pct_nan:.1f}% NaN")
    
    # Salvar
    output_file = CONSOLIDATED_PATH / "tabela_features.csv"
    df_features.to_csv(output_file, index=False)
    
    print(f"\n✓ Features salvas em: {output_file}")
    
    # Preview
    print("\n4. Preview (5 primeiras empresas, 8 primeiros indicadores):")
    preview_cols = ['Empresa', 'Kd_Ponderado', 'Alavancagem_Total', 'Liquidez_Corrente', 
                    'ROA', 'Margem_Bruta', 'Tamanho', 'IHH_Indexador']
    preview_cols = [c for c in preview_cols if c in df_features.columns]
    print(df_features[preview_cols].head().to_string())
    
    print("\n" + "=" * 70)
    print("✓ CÁLCULO DE FEATURES CONCLUÍDO!")
    print("=" * 70)
    
    return df_features


if __name__ == "__main__":
    main()
