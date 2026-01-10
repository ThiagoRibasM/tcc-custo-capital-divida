#!/usr/bin/env python3
"""
Validação completa dos dados financeiros extraídos.
Identifica inconsistências, valores suspeitos e fragilidades.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Tuple
import json

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, FINANCIAL_EXTRACTIONS_PATH


def validate_balance_sheet_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida consistência do balanço patrimonial.
    
    Regras:
    - Ativo Total = Passivo Total + Patrimônio Líquido (ou Ativo = Passivo se PL já incluído)
    - Ativo Total = Ativo Circulante + Ativo Não Circulante
    - Passivo Total = Passivo Circulante + Passivo Não Circulante
    - Dívida Total ≈ Dívida CP + Dívida LP (tolerância de 5%)
    """
    issues = []
    
    for idx, row in df.iterrows():
        empresa = row['Empresa']
        ativo = row.get('Ativo_Total')
        passivo = row.get('Passivo_Total')
        pl = row.get('Patrimonio_Liquido')
        
        # Validação 1: Ativo = Passivo + PL (ou Ativo = Passivo se PL incluído)
        if pd.notna(ativo) and pd.notna(passivo) and pd.notna(pl):
            expected_ativo_1 = passivo + pl
            expected_ativo_2 = passivo
            
            diff_1 = abs(ativo - expected_ativo_1) / max(abs(expected_ativo_1), 1) * 100
            diff_2 = abs(ativo - expected_ativo_2) / max(abs(expected_ativo_2), 1) * 100
            
            if diff_1 > 2 and diff_2 > 2:
                issues.append({
                    'Empresa': empresa,
                    'Tipo': 'Inconsistência Balanço',
                    'Descricao': f'Ativo ({ativo:,.0f}) não corresponde a Passivo ({passivo:,.0f}) + PL ({pl:,.0f})',
                    'Severidade': 'Alta',
                    'Valor_Ativo': ativo,
                    'Valor_Esperado_1': expected_ativo_1,
                    'Valor_Esperado_2': expected_ativo_2,
                    'Diferenca_Pct_1': diff_1,
                    'Diferenca_Pct_2': diff_2
                })
        
        # Validação 2: Ativo = AC + ANC
        ativo_circ = row.get('Ativo_Circulante')
        ativo_ncirc = row.get('Ativo_Nao_Circulante')
        if pd.notna(ativo) and pd.notna(ativo_circ) and pd.notna(ativo_ncirc):
            expected_ativo = ativo_circ + ativo_ncirc
            diff = abs(ativo - expected_ativo) / max(abs(ativo), 1) * 100
            if diff > 1:
                issues.append({
                    'Empresa': empresa,
                    'Tipo': 'Inconsistência Ativo',
                    'Descricao': f'Ativo Total ({ativo:,.0f}) ≠ AC ({ativo_circ:,.0f}) + ANC ({ativo_ncirc:,.0f})',
                    'Severidade': 'Média',
                    'Diferenca_Pct': diff
                })
        
        # Validação 3: Passivo = PC + PNC
        passivo_circ = row.get('Passivo_Circulante')
        passivo_ncirc = row.get('Passivo_Nao_Circulante')
        if pd.notna(passivo) and pd.notna(passivo_circ) and pd.notna(passivo_ncirc):
            expected_passivo = passivo_circ + passivo_ncirc
            diff = abs(passivo - expected_passivo) / max(abs(passivo), 1) * 100
            if diff > 1:
                issues.append({
                    'Empresa': empresa,
                    'Tipo': 'Inconsistência Passivo',
                    'Descricao': f'Passivo Total ({passivo:,.0f}) ≠ PC ({passivo_circ:,.0f}) + PNC ({passivo_ncirc:,.0f})',
                    'Severidade': 'Média',
                    'Diferenca_Pct': diff
                })
        
        # Validação 4: Dívida Total ≈ CP + LP
        divida_total = row.get('Divida_Total')
        divida_cp = row.get('Divida_Curto_Prazo')
        divida_lp = row.get('Divida_Longo_Prazo')
        if pd.notna(divida_total) and pd.notna(divida_cp) and pd.notna(divida_lp):
            expected_divida = divida_cp + divida_lp
            diff = abs(divida_total - expected_divida) / max(abs(divida_total), 1) * 100
            if diff > 5:  # Tolerância maior para dívidas (pode haver outras classificações)
                issues.append({
                    'Empresa': empresa,
                    'Tipo': 'Inconsistência Dívida',
                    'Descricao': f'Dívida Total ({divida_total:,.0f}) difere de CP ({divida_cp:,.0f}) + LP ({divida_lp:,.0f}) em {diff:.1f}%',
                    'Severidade': 'Baixa',
                    'Diferenca_Pct': diff
                })
    
    return pd.DataFrame(issues)


def validate_data_completeness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida completude dos dados.
    Identifica campos ausentes e empresas com dados incompletos.
    """
    issues = []
    
    # Campos críticos
    critical_fields = [
        'Ativo_Total', 'Passivo_Total', 'Patrimonio_Liquido',
        'Receita_Liquida', 'Lucro_Liquido'
    ]
    
    # Campos importantes
    important_fields = [
        'Divida_Total', 'Divida_Curto_Prazo', 'Divida_Longo_Prazo',
        'Lucro_Operacional', 'Despesas_Financeiras'
    ]
    
    for idx, row in df.iterrows():
        empresa = row['Empresa']
        missing_critical = [f for f in critical_fields if pd.isna(row.get(f))]
        missing_important = [f for f in important_fields if pd.isna(row.get(f))]
        
        if missing_critical:
            issues.append({
                'Empresa': empresa,
                'Tipo': 'Dados Críticos Ausentes',
                'Descricao': f'Campos críticos ausentes: {", ".join(missing_critical)}',
                'Severidade': 'Alta',
                'Campos_Ausentes': ', '.join(missing_critical)
            })
        
        if missing_important:
            issues.append({
                'Empresa': empresa,
                'Tipo': 'Dados Importantes Ausentes',
                'Descricao': f'Campos importantes ausentes: {", ".join(missing_important)}',
                'Severidade': 'Média',
                'Campos_Ausentes': ', '.join(missing_important)
            })
    
    return pd.DataFrame(issues)


def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta outliers usando método IQR.
    """
    issues = []
    
    numeric_fields = [
        'Ativo_Total', 'Receita_Liquida', 'Lucro_Liquido',
        'Divida_Total', 'Patrimonio_Liquido'
    ]
    
    for field in numeric_fields:
        if field not in df.columns:
            continue
        
        values = df[field].dropna()
        if len(values) < 4:
            continue
        
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[field] < lower_bound) | (df[field] > upper_bound)]
        
        for idx, row in outliers.iterrows():
            issues.append({
                'Empresa': row['Empresa'],
                'Tipo': 'Outlier',
                'Descricao': f'{field}: {row[field]:,.0f} (fora do range [{lower_bound:,.0f}, {upper_bound:,.0f}])',
                'Severidade': 'Média',
                'Campo': field,
                'Valor': row[field],
                'Limite_Inferior': lower_bound,
                'Limite_Superior': upper_bound
            })
    
    return pd.DataFrame(issues)


def validate_value_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida se valores estão em ranges esperados.
    """
    issues = []
    
    # Ranges esperados (em R$ mil)
    ranges = {
        'Ativo_Total': (1000, 1000000000),  # 1 milhão a 1 trilhão
        'Receita_Liquida': (100, 500000000),  # 100 mil a 500 bilhões
        'Lucro_Liquido': (-100000000, 100000000),  # Pode ser negativo
        'Divida_Total': (0, 100000000),  # 0 a 100 bilhões
        'Patrimonio_Liquido': (-10000000, 100000000),  # Pode ser negativo
    }
    
    for field, (min_val, max_val) in ranges.items():
        if field not in df.columns:
            continue
        
        for idx, row in df.iterrows():
            value = row.get(field)
            if pd.notna(value):
                if value < min_val or value > max_val:
                    issues.append({
                        'Empresa': row['Empresa'],
                        'Tipo': 'Valor Fora do Range',
                        'Descricao': f'{field}: {value:,.0f} (esperado: {min_val:,.0f} a {max_val:,.0f})',
                        'Severidade': 'Alta',
                        'Campo': field,
                        'Valor': value,
                        'Range_Esperado': f'{min_val:,.0f} - {max_val:,.0f}'
                    })
    
    return pd.DataFrame(issues)


def validate_negative_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica valores negativos que podem ser suspeitos.
    """
    issues = []
    
    # Campos que NÃO devem ser negativos
    non_negative_fields = [
        'Ativo_Total', 'Passivo_Total', 'Receita_Liquida',
        'Divida_Total', 'Divida_Curto_Prazo', 'Divida_Longo_Prazo',
        'Caixa_Equivalentes', 'Ativo_Circulante', 'Passivo_Circulante'
    ]
    
    for field in non_negative_fields:
        if field not in df.columns:
            continue
        
        negative = df[df[field] < 0]
        for idx, row in negative.iterrows():
            issues.append({
                'Empresa': row['Empresa'],
                'Tipo': 'Valor Negativo Suspeito',
                'Descricao': f'{field}: {row[field]:,.0f} (não deveria ser negativo)',
                'Severidade': 'Alta',
                'Campo': field,
                'Valor': row[field]
            })
    
    return pd.DataFrame(issues)


def validate_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida razões financeiras básicas.
    """
    issues = []
    
    for idx, row in df.iterrows():
        empresa = row['Empresa']
        
        # Liquidez Corrente = AC / PC
        ac = row.get('Ativo_Circulante')
        pc = row.get('Passivo_Circulante')
        if pd.notna(ac) and pd.notna(pc) and pc != 0:
            liquidez = ac / pc
            if liquidez < 0.1 or liquidez > 10:
                issues.append({
                    'Empresa': empresa,
                    'Tipo': 'Razão Suspeita',
                    'Descricao': f'Liquidez Corrente: {liquidez:.2f} (esperado: 0.5 - 3.0)',
                    'Severidade': 'Média',
                    'Razao': 'Liquidez_Corrente',
                    'Valor': liquidez
                })
        
        # Alavancagem = Dívida / PL
        divida = row.get('Divida_Total')
        pl = row.get('Patrimonio_Liquido')
        if pd.notna(divida) and pd.notna(pl) and pl != 0:
            alavancagem = divida / abs(pl)  # Usa abs para PL negativo
            if alavancagem > 20:  # Alavancagem muito alta
                issues.append({
                    'Empresa': empresa,
                    'Tipo': 'Alavancagem Extrema',
                    'Descricao': f'Alavancagem: {alavancagem:.2f} (muito alta, pode indicar erro)',
                    'Severidade': 'Média',
                    'Razao': 'Alavancagem',
                    'Valor': alavancagem
                })
        
        # Margem Líquida = Lucro Líquido / Receita
        lucro = row.get('Lucro_Liquido')
        receita = row.get('Receita_Liquida')
        if pd.notna(lucro) and pd.notna(receita) and receita != 0:
            margem = lucro / receita
            if abs(margem) > 1:  # Margem > 100% ou < -100% é suspeito
                issues.append({
                    'Empresa': empresa,
                    'Tipo': 'Margem Suspeita',
                    'Descricao': f'Margem Líquida: {margem:.1%} (fora do range esperado)',
                    'Severidade': 'Média',
                    'Razao': 'Margem_Liquida',
                    'Valor': margem
                })
    
    return pd.DataFrame(issues)


def validate_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verifica duplicatas e empresas com dados idênticos.
    """
    issues = []
    
    # Verifica empresas duplicadas
    duplicates = df[df.duplicated(subset=['Empresa'], keep=False)]
    if len(duplicates) > 0:
        for empresa in duplicates['Empresa'].unique():
            issues.append({
                'Empresa': empresa,
                'Tipo': 'Empresa Duplicada',
                'Descricao': f'Empresa aparece {len(duplicates[duplicates["Empresa"] == empresa])} vezes',
                'Severidade': 'Alta'
            })
    
    # Verifica dados idênticos (pode indicar erro de extração)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) > 0:
        # Remove empresas com todos os valores iguais (exceto empresa)
        for idx, row in df.iterrows():
            values = [row[col] for col in numeric_cols if pd.notna(row.get(col))]
            if len(set(values)) == 1 and len(values) > 5:
                issues.append({
                    'Empresa': row['Empresa'],
                    'Tipo': 'Dados Idênticos Suspeitos',
                    'Descricao': f'Todos os valores numéricos são iguais ({values[0]:,.0f})',
                    'Severidade': 'Alta'
                })
    
    return pd.DataFrame(issues)


def generate_validation_report(df: pd.DataFrame, output_path: Path):
    """
    Gera relatório completo de validação.
    """
    print("="*70)
    print("VALIDAÇÃO DOS DADOS FINANCEIROS EXTRAÍDOS")
    print("="*70)
    print(f"\nTotal de empresas: {len(df)}")
    
    # Executa todas as validações
    print("\n🔍 Executando validações...")
    
    issues_balance = validate_balance_sheet_consistency(df)
    issues_completeness = validate_data_completeness(df)
    issues_outliers = detect_outliers(df)
    issues_ranges = validate_value_ranges(df)
    issues_negative = validate_negative_values(df)
    issues_ratios = validate_ratios(df)
    issues_duplicates = validate_duplicates(df)
    
    # Consolida todos os problemas
    all_issues = pd.concat([
        issues_balance, issues_completeness, issues_outliers,
        issues_ranges, issues_negative, issues_ratios, issues_duplicates
    ], ignore_index=True)
    
    # Estatísticas
    print("\n📊 ESTATÍSTICAS DE VALIDAÇÃO")
    print("="*70)
    print(f"Total de problemas encontrados: {len(all_issues)}")
    print(f"Empresas com problemas: {all_issues['Empresa'].nunique()}")
    print()
    
    # Por tipo
    print("Problemas por tipo:")
    tipo_counts = all_issues['Tipo'].value_counts()
    for tipo, count in tipo_counts.items():
        print(f"  {tipo:40s}: {count:3d}")
    print()
    
    # Por severidade
    print("Problemas por severidade:")
    severidade_counts = all_issues['Severidade'].value_counts()
    for sev, count in severidade_counts.items():
        print(f"  {sev:40s}: {count:3d}")
    print()
    
    # Empresas mais problemáticas
    if len(all_issues) > 0:
        empresas_problemas = all_issues['Empresa'].value_counts()
        print("Top 10 empresas com mais problemas:")
        for empresa, count in empresas_problemas.head(10).items():
            print(f"  {empresa:40s}: {count:2d} problemas")
        print()
    
    # Completude dos dados
    print("📈 COMPLETUDE DOS DADOS")
    print("="*70)
    critical_fields = ['Ativo_Total', 'Passivo_Total', 'Patrimonio_Liquido', 
                       'Receita_Liquida', 'Lucro_Liquido', 'Divida_Total']
    
    for field in critical_fields:
        if field in df.columns:
            filled = df[field].notna().sum()
            pct = filled / len(df) * 100
            print(f"  {field:30s}: {filled:3d}/{len(df)} ({pct:5.1f}%)")
    print()
    
    # Estatísticas descritivas
    print("📊 ESTATÍSTICAS DESCRITIVAS")
    print("="*70)
    numeric_fields = ['Ativo_Total', 'Receita_Liquida', 'Lucro_Liquido', 'Divida_Total']
    
    for field in numeric_fields:
        if field in df.columns:
            values = df[field].dropna()
            if len(values) > 0:
                print(f"\n{field}:")
                print(f"  Média:   R$ {values.mean():>15,.0f} mil")
                print(f"  Mediana: R$ {values.median():>15,.0f} mil")
                print(f"  Min:     R$ {values.min():>15,.0f} mil")
                print(f"  Max:     R$ {values.max():>15,.0f} mil")
                print(f"  Desvio:  R$ {values.std():>15,.0f} mil")
    
    # Salva relatório detalhado
    if len(all_issues) > 0:
        issues_csv = output_path.parent / "validation_issues.csv"
        all_issues.to_csv(issues_csv, index=False, encoding='utf-8')
        print(f"\n💾 Problemas detalhados salvos em: {issues_csv}")
    
    # Salva resumo
    summary = {
        'total_empresas': len(df),
        'total_problemas': len(all_issues),
        'empresas_com_problemas': all_issues['Empresa'].nunique() if len(all_issues) > 0 else 0,
        'problemas_por_tipo': tipo_counts.to_dict() if len(all_issues) > 0 else {},
        'problemas_por_severidade': severidade_counts.to_dict() if len(all_issues) > 0 else {},
        'completude': {
            field: {
                'filled': int(df[field].notna().sum()),
                'total': len(df),
                'pct': float(df[field].notna().sum() / len(df) * 100)
            }
            for field in critical_fields if field in df.columns
        }
    }
    
    summary_json = output_path.parent / "validation_summary.json"
    with open(summary_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resumo salvo em: {summary_json}")
    
    print("\n" + "="*70)
    if len(all_issues) == 0:
        print("✅ NENHUM PROBLEMA ENCONTRADO - DADOS VALIDADOS COM SUCESSO")
    else:
        print(f"⚠️  {len(all_issues)} PROBLEMAS ENCONTRADOS")
        print("   Revise o arquivo validation_issues.csv para detalhes")
    print("="*70)
    
    return all_issues, summary


def main():
    """Função principal."""
    csv_file = CONSOLIDATED_PATH / "dados_financeiros_brutos.csv"
    output_path = CONSOLIDATED_PATH / "validation_report.md"
    
    if not csv_file.exists():
        print(f"❌ Arquivo não encontrado: {csv_file}")
        return
    
    print("📊 Carregando dados...")
    df = pd.read_csv(csv_file)
    print(f"   ✅ {len(df)} empresas carregadas")
    
    # Gera relatório
    issues, summary = generate_validation_report(df, output_path)
    
    # Salva relatório em Markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Validação dos Dados Financeiros\n\n")
        f.write(f"**Data:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## Resumo Executivo\n\n")
        f.write(f"- **Total de empresas:** {summary['total_empresas']}\n")
        f.write(f"- **Total de problemas encontrados:** {summary['total_problemas']}\n")
        f.write(f"- **Empresas com problemas:** {summary['empresas_com_problemas']}\n\n")
        
        if summary['problemas_por_severidade']:
            f.write("### Problemas por Severidade\n\n")
            for sev, count in summary['problemas_por_severidade'].items():
                f.write(f"- **{sev}:** {count}\n")
            f.write("\n")
        
        f.write("## Completude dos Dados\n\n")
        f.write("| Campo | Preenchido | Total | % |\n")
        f.write("|-------|------------|-------|---|\n")
        for field, stats in summary['completude'].items():
            f.write(f"| {field} | {stats['filled']} | {stats['total']} | {stats['pct']:.1f}% |\n")
        f.write("\n")
        
        if len(issues) > 0:
            f.write("## Problemas Encontrados\n\n")
            f.write(f"Total: {len(issues)} problemas\n\n")
            
            f.write("### Por Tipo\n\n")
            tipo_counts = issues['Tipo'].value_counts()
            for tipo, count in tipo_counts.items():
                f.write(f"- **{tipo}:** {count}\n")
            f.write("\n")
            
            f.write("### Detalhes\n\n")
            f.write("| Empresa | Tipo | Severidade | Descrição |\n")
            f.write("|---------|------|------------|-----------|\n")
            for _, row in issues.head(50).iterrows():
                empresa = row['Empresa'][:30]
                tipo = row['Tipo']
                severidade = row['Severidade']
                descricao = row['Descricao'][:60]
                f.write(f"| {empresa} | {tipo} | {severidade} | {descricao} |\n")
            
            if len(issues) > 50:
                f.write(f"\n... e mais {len(issues) - 50} problemas. Ver `validation_issues.csv` para lista completa.\n")
        
        f.write("\n---\n\n")
        f.write("**Arquivos gerados:**\n")
        f.write("- `validation_issues.csv`: Lista completa de problemas\n")
        f.write("- `validation_summary.json`: Resumo em JSON\n")
    
    print(f"\n📄 Relatório Markdown salvo em: {output_path}")


if __name__ == "__main__":
    main()

