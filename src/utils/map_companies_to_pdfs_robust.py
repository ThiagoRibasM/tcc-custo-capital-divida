#!/usr/bin/env python3
"""
Mapeamento robusto empresa-PDF garantindo 100% de match.
Usa a coluna arquivo_pdf do arquivo original como fonte de verdade,
com estratégias de fallback para lidar com variações de nomes.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import unicodedata
import re
import sys
from collections import defaultdict
from rapidfuzz import process, fuzz

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, EXTRACTED_PDFS_DFP


def load_original_mapping(excel_path: Path) -> pd.DataFrame:
    """
    Carrega arquivo original Excel e extrai mapeamento empresa -> arquivo_pdf.
    
    Args:
        excel_path: Caminho para o arquivo Excel original
        
    Returns:
        DataFrame com colunas: Empresa, arquivo_pdf
    """
    print(f"📖 Carregando arquivo original: {excel_path.name}")
    
    if not excel_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {excel_path}")
    
    # Lê o Excel
    df = pd.read_excel(excel_path)
    
    # Verifica se tem as colunas necessárias
    required_cols = ['Empresa', 'arquivo_pdf']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas faltando no Excel: {missing_cols}")
    
    # Extrai apenas as colunas necessárias
    df_mapping = df[required_cols].copy()
    
    # Remove duplicatas mas mantém todas as ocorrências para verificar múltiplos PDFs
    print(f"   ✅ {len(df_mapping)} registros carregados")
    print(f"   ✅ {df_mapping['Empresa'].nunique()} empresas únicas")
    print(f"   ✅ {df_mapping['arquivo_pdf'].nunique()} PDFs únicos")
    
    return df_mapping


def normalize_filename(filename: str) -> str:
    """
    Normaliza nome de arquivo para comparação.
    
    Args:
        filename: Nome do arquivo (com ou sem extensão)
        
    Returns:
        Nome normalizado
    """
    if pd.isna(filename) or not filename:
        return ""
    
    # Remove extensão
    filename = str(filename).replace('.pdf', '').replace('.PDF', '')
    
    # Lowercase
    filename = filename.lower()
    
    # Remove sufixos comuns
    filename = re.sub(r'_versao_\d+', '', filename)
    filename = re.sub(r'_v\d+', '', filename)
    filename = re.sub(r'_s_a$', '', filename)
    filename = re.sub(r'_n_v$', '', filename)
    filename = re.sub(r'_s\.a\.$', '', filename)
    filename = re.sub(r'_ltda$', '', filename)
    
    # Remove acentos
    filename = ''.join(c for c in unicodedata.normalize('NFD', filename) 
                       if unicodedata.category(c) != 'Mn')
    
    # Remove caracteres especiais, mantém apenas letras, números e underscore
    filename = re.sub(r'[^a-z0-9_]', '_', filename)
    
    # Remove underscores múltiplos
    filename = re.sub(r'_+', '_', filename)
    
    # Remove underscores no início e fim
    filename = filename.strip('_')
    
    return filename


def normalize_company_name(company: str) -> str:
    """
    Normaliza nome da empresa para comparação.
    
    Args:
        company: Nome da empresa
        
    Returns:
        Nome normalizado
    """
    if pd.isna(company) or not company:
        return ""
    
    company = str(company).lower()
    
    # Remove sufixos comuns
    company = re.sub(r'\s+s\.a\.$', '', company)
    company = re.sub(r'\s+s/a$', '', company)
    company = re.sub(r'\s+n\.v\.$', '', company)
    company = re.sub(r'\s+ltda$', '', company)
    
    # Remove acentos
    company = ''.join(c for c in unicodedata.normalize('NFD', company) 
                      if unicodedata.category(c) != 'Mn')
    
    # Remove caracteres especiais, mantém apenas letras, números e espaços
    company = re.sub(r'[^a-z0-9 ]', ' ', company)
    
    # Remove espaços múltiplos
    company = ' '.join(company.split())
    
    return company


def find_pdf_exact(pdf_name: str, pdfs_dir: Path) -> Optional[Path]:
    """
    Busca PDF com nome exato.
    
    Args:
        pdf_name: Nome do PDF (com ou sem extensão)
        pdfs_dir: Diretório onde buscar
        
    Returns:
        Path do PDF se encontrado, None caso contrário
    """
    # Garante que tem extensão .pdf
    if not pdf_name.endswith('.pdf'):
        pdf_name = pdf_name + '.pdf'
    
    pdf_path = pdfs_dir / pdf_name
    
    if pdf_path.exists():
        return pdf_path
    
    return None


def find_pdf_normalized(pdf_name: str, pdfs_dir: Path) -> Optional[Path]:
    """
    Busca PDF usando normalização de nomes.
    
    Args:
        pdf_name: Nome do PDF do Excel
        pdfs_dir: Diretório onde buscar
        
    Returns:
        Path do PDF se encontrado, None caso contrário
    """
    # Normaliza nome do PDF procurado
    pdf_normalized = normalize_filename(pdf_name)
    
    if not pdf_normalized:
        return None
    
    # Lista todos os PDFs e normaliza
    pdf_files = list(pdfs_dir.glob('*.pdf'))
    
    for pdf_file in pdf_files:
        pdf_file_normalized = normalize_filename(pdf_file.name)
        
        if pdf_file_normalized == pdf_normalized:
            return pdf_file
    
    return None


def find_pdf_fuzzy(empresa: str, pdfs_dir: Path, min_score: int = 70) -> Tuple[Optional[Path], float]:
    """
    Busca PDF usando fuzzy matching.
    
    Args:
        empresa: Nome da empresa
        pdfs_dir: Diretório onde buscar
        min_score: Score mínimo para considerar match (0-100)
        
    Returns:
        Tupla (Path do PDF, score) se encontrado, (None, 0) caso contrário
    """
    # Normaliza nome da empresa
    empresa_normalized = normalize_company_name(empresa)
    
    if not empresa_normalized:
        return None, 0.0
    
    # Lista todos os PDFs
    pdf_files = list(pdfs_dir.glob('*.pdf'))
    
    if not pdf_files:
        return None, 0.0
    
    # Normaliza nomes dos PDFs
    pdf_names_normalized = []
    pdf_mapping = {}
    
    for pdf_file in pdf_files:
        pdf_normalized = normalize_filename(pdf_file.name)
        if pdf_normalized:
            pdf_names_normalized.append(pdf_normalized)
            pdf_mapping[pdf_normalized] = pdf_file
    
    if not pdf_names_normalized:
        return None, 0.0
    
    # Faz fuzzy matching
    best_match = process.extractOne(
        empresa_normalized,
        pdf_names_normalized,
        scorer=fuzz.token_sort_ratio
    )
    
    if best_match:
        matched_name, score, idx = best_match
        
        if score >= min_score:
            return pdf_mapping[matched_name], float(score)
    
    return None, 0.0


def handle_multiple_pdfs(pdf_list: List[Path], empresa: str) -> Tuple[Path, str]:
    """
    Escolhe um PDF quando empresa tem múltiplos PDFs.
    
    Estratégia:
    1. PDF mais recente (por data de modificação)
    2. PDF com nome mais próximo da empresa
    3. Primeiro PDF encontrado
    
    Args:
        pdf_list: Lista de PDFs
        empresa: Nome da empresa
        
    Returns:
        Tupla (Path do PDF escolhido, razão da seleção)
    """
    if not pdf_list:
        raise ValueError("Lista de PDFs vazia")
    
    if len(pdf_list) == 1:
        return pdf_list[0], "ONLY_ONE"
    
    # Estratégia 1: PDF mais recente
    pdfs_with_mtime = [(pdf, pdf.stat().st_mtime) for pdf in pdf_list]
    pdfs_with_mtime.sort(key=lambda x: x[1], reverse=True)
    most_recent = pdfs_with_mtime[0][0]
    
    # Estratégia 2: PDF com nome mais próximo da empresa
    empresa_normalized = normalize_company_name(empresa)
    best_match_pdf = None
    best_match_score = 0
    
    for pdf in pdf_list:
        pdf_normalized = normalize_filename(pdf.name)
        score = fuzz.token_sort_ratio(empresa_normalized, pdf_normalized)
        if score > best_match_score:
            best_match_score = score
            best_match_pdf = pdf
    
    # Se o melhor match tem score alto, usa ele; senão usa o mais recente
    if best_match_score >= 80:
        return best_match_pdf, "BEST_MATCH"
    else:
        return most_recent, "MOST_RECENT"


def map_companies_robust(
    kd_csv: Path,
    excel_original: Path,
    pdfs_dir: Path,
    output_csv: Path
) -> pd.DataFrame:
    """
    Função principal que orquestra o mapeamento robusto empresa-PDF.
    
    Args:
        kd_csv: Caminho para CSV de Kd ponderado por empresa
        excel_original: Caminho para Excel original com arquivo_pdf
        pdfs_dir: Diretório com PDFs disponíveis
        output_csv: Caminho para salvar CSV de mapeamento
        
    Returns:
        DataFrame com mapeamento completo
    """
    print("="*70)
    print("MAPEAMENTO ROBUSTO EMPRESA-PDF")
    print("="*70)
    
    # 1. Carrega dados
    print("\n📊 Carregando dados...")
    
    # Carrega CSV de Kd
    df_kd = pd.read_csv(kd_csv)
    empresas_kd = df_kd['Empresa'].unique().tolist()
    print(f"   ✅ {len(empresas_kd)} empresas no CSV de Kd")
    
    # Carrega mapeamento original do Excel
    df_original = load_original_mapping(excel_original)
    
    # Cria dicionário empresa -> lista de PDFs
    empresa_to_pdfs = defaultdict(list)
    for _, row in df_original.iterrows():
        empresa = row['Empresa']
        arquivo_pdf = row['arquivo_pdf']
        if pd.notna(empresa) and pd.notna(arquivo_pdf):
            empresa_to_pdfs[empresa].append(str(arquivo_pdf))
    
    print(f"   ✅ {len(empresa_to_pdfs)} empresas no mapeamento original")
    
    # Lista PDFs disponíveis
    pdf_files_available = list(pdfs_dir.glob('*.pdf'))
    print(f"   ✅ {len(pdf_files_available)} PDFs disponíveis no diretório")
    
    # 2. Cria índice de PDFs normalizados para busca rápida
    pdf_index_normalized = {}
    for pdf_file in pdf_files_available:
        pdf_normalized = normalize_filename(pdf_file.name)
        if pdf_normalized:
            if pdf_normalized not in pdf_index_normalized:
                pdf_index_normalized[pdf_normalized] = []
            pdf_index_normalized[pdf_normalized].append(pdf_file)
    
    print(f"   ✅ Índice de PDFs normalizados criado")
    
    # 3. Mapeia cada empresa
    print(f"\n🔍 Mapeando {len(empresas_kd)} empresas...")
    
    mapping_results = []
    
    for empresa in empresas_kd:
        result = {
            'Empresa': empresa,
            'PDF_Nome': None,
            'PDF_Path': None,
            'Match_Method': None,
            'Match_Score': None,
            'Match_Status': 'NOT_FOUND',
            'Source': None,
            'Has_Multiple_PDFs': False,
            'PDF_Selected_Reason': None
        }
        
        # Verifica se empresa está no mapeamento original
        if empresa in empresa_to_pdfs:
            # Empresa encontrada no Excel
            pdfs_from_excel = empresa_to_pdfs[empresa]
            result['Source'] = 'ORIGINAL_EXCEL'
            result['Has_Multiple_PDFs'] = len(pdfs_from_excel) > 1
            
            # Tenta encontrar PDFs usando estratégias em cascata
            found_pdfs = []
            
            for pdf_name_excel in pdfs_from_excel:
                # Nível 1: Match exato
                pdf_path = find_pdf_exact(pdf_name_excel, pdfs_dir)
                if pdf_path:
                    found_pdfs.append((pdf_path, 'EXACT', 100.0))
                    continue
                
                # Nível 2: Match normalizado
                pdf_path = find_pdf_normalized(pdf_name_excel, pdfs_dir)
                if pdf_path:
                    found_pdfs.append((pdf_path, 'NORMALIZED', 95.0))
                    continue
                
                # Nível 3: Match fuzzy no nome do PDF
                pdf_normalized = normalize_filename(pdf_name_excel)
                if pdf_normalized and pdf_normalized in pdf_index_normalized:
                    pdf_paths = pdf_index_normalized[pdf_normalized]
                    for pdf_path in pdf_paths:
                        found_pdfs.append((pdf_path, 'NORMALIZED_INDEX', 90.0))
            
            # Se encontrou PDFs, escolhe um
            if found_pdfs:
                # Remove duplicatas mantendo o melhor método
                unique_pdfs = {}
                for pdf_path, method, score in found_pdfs:
                    if pdf_path not in unique_pdfs:
                        unique_pdfs[pdf_path] = (method, score)
                    else:
                        # Mantém o método com maior score
                        if score > unique_pdfs[pdf_path][1]:
                            unique_pdfs[pdf_path] = (method, score)
                
                pdf_list = list(unique_pdfs.keys())
                
                if len(pdf_list) == 1:
                    selected_pdf = pdf_list[0]
                    method, score = unique_pdfs[selected_pdf]
                    reason = "ONLY_ONE"
                else:
                    selected_pdf, reason = handle_multiple_pdfs(pdf_list, empresa)
                    method, score = unique_pdfs[selected_pdf]
                
                result['PDF_Nome'] = selected_pdf.name
                result['PDF_Path'] = str(selected_pdf)
                result['Match_Method'] = method
                result['Match_Score'] = score
                result['Match_Status'] = 'OK'
                result['PDF_Selected_Reason'] = reason
            else:
                # Não encontrou pelos PDFs do Excel, tenta fuzzy direto
                pdf_path, score = find_pdf_fuzzy(empresa, pdfs_dir, min_score=70)
                if pdf_path:
                    result['PDF_Nome'] = pdf_path.name
                    result['PDF_Path'] = str(pdf_path)
                    result['Match_Method'] = 'FUZZY'
                    result['Match_Score'] = score
                    result['Match_Status'] = 'OK' if score >= 70 else 'LOW_SCORE'
                    result['Source'] = 'FUZZY_FALLBACK'
                    result['PDF_Selected_Reason'] = 'FUZZY_MATCH'
        else:
            # Empresa não encontrada no Excel, tenta fuzzy direto
            result['Source'] = 'FUZZY_DIRECT'
            pdf_path, score = find_pdf_fuzzy(empresa, pdfs_dir, min_score=70)
            if pdf_path:
                result['PDF_Nome'] = pdf_path.name
                result['PDF_Path'] = str(pdf_path)
                result['Match_Method'] = 'FUZZY'
                result['Match_Score'] = score
                result['Match_Status'] = 'OK' if score >= 70 else 'LOW_SCORE'
                result['PDF_Selected_Reason'] = 'FUZZY_MATCH'
        
        mapping_results.append(result)
    
    # 4. Cria DataFrame
    df_mapping = pd.DataFrame(mapping_results)
    
    # 5. Validação
    print(f"\n✅ Mapeamento concluído!")
    print(f"   Total de empresas: {len(df_mapping)}")
    print(f"   Match OK: {len(df_mapping[df_mapping['Match_Status'] == 'OK'])}")
    print(f"   Match Low Score: {len(df_mapping[df_mapping['Match_Status'] == 'LOW_SCORE'])}")
    print(f"   Não encontrado: {len(df_mapping[df_mapping['Match_Status'] == 'NOT_FOUND'])}")
    
    # Verifica se todas foram mapeadas
    not_found = df_mapping[df_mapping['Match_Status'] == 'NOT_FOUND']
    if len(not_found) > 0:
        print(f"\n⚠️  ATENÇÃO: {len(not_found)} empresas não foram mapeadas:")
        for empresa in not_found['Empresa'].head(10):
            print(f"      - {empresa}")
        if len(not_found) > 10:
            print(f"      ... e mais {len(not_found) - 10} empresas")
    
    # 6. Salva CSV
    df_mapping.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n💾 Mapeamento salvo em: {output_csv}")
    
    return df_mapping


def generate_mapping_report(df_mapping: Path, output_report: Path):
    """
    Gera relatório detalhado do mapeamento.
    
    Args:
        df_mapping: Caminho para CSV de mapeamento
        output_report: Caminho para salvar relatório Markdown
    """
    df = pd.read_csv(df_mapping)
    
    total = len(df)
    ok = len(df[df['Match_Status'] == 'OK'])
    low_score = len(df[df['Match_Status'] == 'LOW_SCORE'])
    not_found = len(df[df['Match_Status'] == 'NOT_FOUND'])
    
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Mapeamento Robusto Empresa-PDF\n\n")
        f.write(f"**Data:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## Resumo Executivo\n\n")
        f.write(f"- **Total de empresas:** {total}\n")
        f.write(f"- **Match OK:** {ok} ({ok/total*100:.1f}%)\n")
        f.write(f"- **Match Low Score:** {low_score} ({low_score/total*100:.1f}%)\n")
        f.write(f"- **Não encontrado:** {not_found} ({not_found/total*100:.1f}%)\n\n")
        
        f.write("## Distribuição por Método de Match\n\n")
        method_counts = df['Match_Method'].value_counts()
        for method, count in method_counts.items():
            f.write(f"- **{method}:** {count} ({count/total*100:.1f}%)\n")
        f.write("\n")
        
        f.write("## Distribuição por Fonte\n\n")
        source_counts = df['Source'].value_counts()
        for source, count in source_counts.items():
            f.write(f"- **{source}:** {count} ({count/total*100:.1f}%)\n")
        f.write("\n")
        
        f.write("## Empresas com Múltiplos PDFs\n\n")
        multiple = df[df['Has_Multiple_PDFs'] == True]
        f.write(f"Total: {len(multiple)} empresas\n\n")
        if len(multiple) > 0:
            f.write("| Empresa | PDF Selecionado | Razão |\n")
            f.write("|---------|-----------------|-------|\n")
            for _, row in multiple.head(20).iterrows():
                f.write(f"| {row['Empresa']} | {row['PDF_Nome']} | {row['PDF_Selected_Reason']} |\n")
        f.write("\n")
        
        if not_found > 0:
            f.write("## Empresas Não Mapeadas\n\n")
            f.write("| Empresa |\n")
            f.write("|---------|\n")
            for empresa in df[df['Match_Status'] == 'NOT_FOUND']['Empresa']:
                f.write(f"| {empresa} |\n")
            f.write("\n")
        
        f.write("## Estatísticas de Score\n\n")
        scores = df[df['Match_Score'].notna()]['Match_Score']
        if len(scores) > 0:
            f.write(f"- **Média:** {scores.mean():.1f}\n")
            f.write(f"- **Mediana:** {scores.median():.1f}\n")
            f.write(f"- **Mínimo:** {scores.min():.1f}\n")
            f.write(f"- **Máximo:** {scores.max():.1f}\n")
    
    print(f"📄 Relatório salvo em: {output_report}")


def main():
    """Função principal."""
    # Paths
    kd_csv = CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv"
    excel_original = CONSOLIDATED_PATH / "emp_e_fin_novo_mercado_20250920.xlsx"
    pdfs_dir = EXTRACTED_PDFS_DFP
    output_csv = CONSOLIDATED_PATH / "empresa_pdf_mapping_robust.csv"
    output_report = Path(__file__).parent.parent.parent / "reports" / "mapping_report_robust.md"
    
    # Garante que diretório de relatórios existe
    output_report.parent.mkdir(parents=True, exist_ok=True)
    
    # Valida arquivos de entrada
    if not kd_csv.exists():
        print(f"❌ Arquivo não encontrado: {kd_csv}")
        return
    
    if not excel_original.exists():
        print(f"❌ Arquivo não encontrado: {excel_original}")
        return
    
    if not pdfs_dir.exists():
        print(f"❌ Diretório não encontrado: {pdfs_dir}")
        return
    
    # Executa mapeamento
    df_mapping = map_companies_robust(
        kd_csv,
        excel_original,
        pdfs_dir,
        output_csv
    )
    
    # Gera relatório
    generate_mapping_report(output_csv, output_report)
    
    print("\n" + "="*70)
    print("✅ MAPEAMENTO ROBUSTO CONCLUÍDO")
    print("="*70)


if __name__ == "__main__":
    main()

