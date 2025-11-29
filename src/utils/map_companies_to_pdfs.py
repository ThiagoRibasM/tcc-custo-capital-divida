#!/usr/bin/env python3
"""
Script para mapear empresas da tabela final de Kd para PDFs disponíveis.
"""
import pandas as pd
from pathlib import Path
from rapidfuzz import process, fuzz
import unicodedata
import re
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, EXTRACTED_PDFS_DFP


def normalize_text(text: str) -> str:
    """
    Normaliza texto para comparação fuzzy.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if pd.isna(text):
        return ""
    
    text = str(text).lower()
    # Remove sufixos comuns
    text = re.sub(r'_versao_\d+', '', text)
    text = re.sub(r'_s_a$', '', text)
    text = re.sub(r'_n_v$', '', text)
    text = re.sub(r'_s\.a\.$', '', text)
    text = re.sub(r'_ltda$', '', text)
    
    # Remove acentos
    text = ''.join(c for c in unicodedata.normalize('NFD', text) 
                   if unicodedata.category(c) != 'Mn')
    
    # Remove caracteres especiais
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    text = ' '.join(text.split())
    
    return text


def map_companies_to_pdfs(
    companies_csv: Path,
    pdfs_dir: Path,
    output_csv: Path,
    min_score: int = 70
) -> pd.DataFrame:
    """
    Mapeia empresas para PDFs usando matching fuzzy.
    
    Args:
        companies_csv: Caminho para CSV com empresas
        pdfs_dir: Diretório com PDFs
        output_csv: Caminho para salvar mapeamento
        min_score: Score mínimo para considerar match (0-100)
        
    Returns:
        DataFrame com mapeamento empresa-PDF
    """
    # Carrega lista de empresas
    print(f"📊 Carregando empresas de {companies_csv}...")
    df_companies = pd.read_csv(companies_csv)
    companies = df_companies['Empresa'].tolist()
    companies_norm = [normalize_text(c) for c in companies]
    
    print(f"   ✅ {len(companies)} empresas carregadas")
    
    # Lista PDFs disponíveis
    print(f"\n📄 Listando PDFs em {pdfs_dir}...")
    pdf_files = list(pdfs_dir.glob("*.pdf"))
    pdf_names = [p.name for p in pdf_files]
    pdf_names_norm = [normalize_text(p) for p in pdf_names]
    
    print(f"   ✅ {len(pdf_files)} PDFs encontrados")
    
    # Mapeamento
    print(f"\n🔍 Mapeando empresas para PDFs (score mínimo: {min_score})...")
    mappings = []
    
    for company, company_norm in zip(companies, companies_norm):
        if not company_norm:
            continue
            
        # Busca melhor match
        match_result = process.extractOne(
            company_norm,
            pdf_names_norm,
            scorer=fuzz.token_sort_ratio
        )
        
        if match_result:
            matched_name_norm, score, idx = match_result
            
            if score >= min_score:
                pdf_path = pdf_files[idx]
                mappings.append({
                    'Empresa': company,
                    'PDF_Nome': pdf_path.name,
                    'PDF_Path': str(pdf_path),
                    'Score_Match': score,
                    'Match_Status': 'OK'
                })
            else:
                mappings.append({
                    'Empresa': company,
                    'PDF_Nome': None,
                    'PDF_Path': None,
                    'Score_Match': score,
                    'Match_Status': 'SCORE_BAIXO'
                })
        else:
            mappings.append({
                'Empresa': company,
                'PDF_Nome': None,
                'PDF_Path': None,
                'Score_Match': 0,
                'Match_Status': 'NAO_ENCONTRADO'
            })
    
    # Cria DataFrame
    df_mapping = pd.DataFrame(mappings)
    
    # Estatísticas
    ok_count = (df_mapping['Match_Status'] == 'OK').sum()
    low_score_count = (df_mapping['Match_Status'] == 'SCORE_BAIXO').sum()
    not_found_count = (df_mapping['Match_Status'] == 'NAO_ENCONTRADO').sum()
    
    print(f"\n📊 Estatísticas do Mapeamento:")
    print(f"   ✅ Match OK: {ok_count} ({ok_count/len(companies)*100:.1f}%)")
    print(f"   ⚠️  Score baixo: {low_score_count}")
    print(f"   ❌ Não encontrado: {not_found_count}")
    
    # Salva CSV
    df_mapping.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n💾 Mapeamento salvo em: {output_csv}")
    
    return df_mapping


def main():
    """Função principal."""
    companies_csv = CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv"
    pdfs_dir = EXTRACTED_PDFS_DFP
    output_csv = CONSOLIDATED_PATH / "empresa_pdf_mapping.csv"
    
    if not companies_csv.exists():
        print(f"❌ Arquivo não encontrado: {companies_csv}")
        return
    
    if not pdfs_dir.exists():
        print(f"❌ Diretório não encontrado: {pdfs_dir}")
        return
    
    df_mapping = map_companies_to_pdfs(
        companies_csv,
        pdfs_dir,
        output_csv,
        min_score=70
    )
    
    print("\n✅ Mapeamento concluído!")


if __name__ == "__main__":
    main()

