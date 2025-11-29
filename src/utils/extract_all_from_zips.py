#!/usr/bin/env python3
"""
Script para extrair todos os arquivos dos ZIPs de DFPs.
Extrai PDFs, planilhas e outros arquivos, organizando por tipo.
"""
import zipfile
import shutil
from pathlib import Path
import sys
from collections import defaultdict

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import DFP_2024_PATH, EXTRACTED_PDFS_DFP, DATA_RAW


def get_file_type(file_path: Path) -> str:
    """
    Determina o tipo de arquivo baseado na extensão.
    
    Returns:
        'pdf', 'spreadsheet', 'other'
    """
    ext = file_path.suffix.lower()
    
    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.xlsx', '.xls', '.csv']:
        return 'spreadsheet'
    else:
        return 'other'


def extract_all_from_zips(
    zip_dir: Path,
    pdf_dest: Path,
    spreadsheet_dest: Path,
    other_dest: Path
) -> dict:
    """
    Extrai todos os arquivos dos ZIPs, organizando por tipo.
    
    Args:
        zip_dir: Diretório com os ZIPs
        pdf_dest: Destino para PDFs
        spreadsheet_dest: Destino para planilhas
        other_dest: Destino para outros arquivos
    
    Returns:
        Dicionário com estatísticas da extração
    """
    # Cria diretórios de destino
    pdf_dest.mkdir(parents=True, exist_ok=True)
    spreadsheet_dest.mkdir(parents=True, exist_ok=True)
    other_dest.mkdir(parents=True, exist_ok=True)
    
    # Estatísticas
    stats = {
        'zips_processed': 0,
        'zips_errors': 0,
        'files_extracted': defaultdict(int),
        'files_skipped': defaultdict(int),
        'file_types_found': set(),
        'errors': []
    }
    
    # Lista todos os ZIPs
    zip_files = list(zip_dir.glob('*.zip'))
    total_zips = len(zip_files)
    
    print("="*70)
    print("EXTRAÇÃO DE ARQUIVOS DOS ZIPs")
    print("="*70)
    print(f"📦 Total de ZIPs encontrados: {total_zips}")
    print(f"📄 PDFs → {pdf_dest}")
    print(f"📊 Planilhas → {spreadsheet_dest}")
    print(f"📁 Outros → {other_dest}")
    print()
    
    # Processa cada ZIP
    for idx, zip_path in enumerate(zip_files, 1):
        if idx % 50 == 0:
            print(f"   Processando ZIP {idx}/{total_zips}...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Lista todos os arquivos no ZIP
                file_list = zip_ref.namelist()
                
                for file_name in file_list:
                    # Ignora diretórios
                    if file_name.endswith('/'):
                        continue
                    
                    # Determina tipo de arquivo
                    file_path = Path(file_name)
                    file_type = get_file_type(file_path)
                    stats['file_types_found'].add(file_path.suffix.lower())
                    
                    # Define destino baseado no tipo
                    if file_type == 'pdf':
                        dest_dir = pdf_dest
                    elif file_type == 'spreadsheet':
                        dest_dir = spreadsheet_dest
                    else:
                        dest_dir = other_dest
                    
                    # Nome do arquivo final
                    final_name = file_path.name
                    dest_path = dest_dir / final_name
                    
                    # Verifica se já existe (evita duplicação)
                    if dest_path.exists():
                        stats['files_skipped'][file_type] += 1
                        continue
                    
                    # Extrai arquivo
                    try:
                        # Lê conteúdo do arquivo
                        file_content = zip_ref.read(file_name)
                        
                        # Salva no destino
                        with open(dest_path, 'wb') as f:
                            f.write(file_content)
                        
                        stats['files_extracted'][file_type] += 1
                        
                    except Exception as e:
                        error_msg = f"Erro ao extrair {file_name} de {zip_path.name}: {e}"
                        stats['errors'].append(error_msg)
                        print(f"   ⚠️  {error_msg}")
            
            stats['zips_processed'] += 1
            
        except zipfile.BadZipFile:
            error_msg = f"ZIP corrompido: {zip_path.name}"
            stats['errors'].append(error_msg)
            stats['zips_errors'] += 1
            print(f"   ❌ {error_msg}")
        except Exception as e:
            error_msg = f"Erro ao processar {zip_path.name}: {e}"
            stats['errors'].append(error_msg)
            stats['zips_errors'] += 1
            print(f"   ❌ {error_msg}")
    
    return stats


def generate_extraction_report(stats: dict, report_path: Path):
    """
    Gera relatório da extração.
    """
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Extração de ZIPs\n\n")
        f.write(f"**Data:** {Path(__file__).stat().st_mtime}\n\n")
        f.write("---\n\n")
        
        f.write("## Estatísticas Gerais\n\n")
        f.write(f"- **ZIPs processados:** {stats['zips_processed']}\n")
        f.write(f"- **ZIPs com erro:** {stats['zips_errors']}\n")
        f.write(f"- **Total de erros:** {len(stats['errors'])}\n\n")
        
        f.write("## Arquivos Extraídos\n\n")
        total_extracted = sum(stats['files_extracted'].values())
        f.write(f"**Total:** {total_extracted} arquivos\n\n")
        
        f.write("| Tipo | Quantidade |\n")
        f.write("|------|------------|\n")
        for file_type, count in sorted(stats['files_extracted'].items()):
            f.write(f"| {file_type} | {count} |\n")
        f.write("\n")
        
        f.write("## Arquivos Ignorados (já existiam)\n\n")
        total_skipped = sum(stats['files_skipped'].values())
        f.write(f"**Total:** {total_skipped} arquivos\n\n")
        
        f.write("| Tipo | Quantidade |\n")
        f.write("|------|------------|\n")
        for file_type, count in sorted(stats['files_skipped'].items()):
            f.write(f"| {file_type} | {count} |\n")
        f.write("\n")
        
        f.write("## Tipos de Arquivo Encontrados\n\n")
        f.write("Extensões encontradas nos ZIPs:\n\n")
        for ext in sorted(stats['file_types_found']):
            if ext:
                f.write(f"- `{ext}`\n")
            else:
                f.write("- (sem extensão)\n")
        f.write("\n")
        
        if stats['errors']:
            f.write("## Erros Encontrados\n\n")
            f.write(f"Total de erros: {len(stats['errors'])}\n\n")
            for error in stats['errors'][:50]:  # Limita a 50 erros no relatório
                f.write(f"- {error}\n")
            if len(stats['errors']) > 50:
                f.write(f"\n... e mais {len(stats['errors']) - 50} erros.\n")


def main():
    """Função principal."""
    # Paths
    zip_dir = DFP_2024_PATH
    pdf_dest = EXTRACTED_PDFS_DFP
    spreadsheet_dest = DATA_RAW / "spreadsheets" / "dfp"
    other_dest = DFP_2024_PATH / "extracted_other"
    report_path = DFP_2024_PATH / "extraction_report.md"
    
    # Extrai arquivos
    stats = extract_all_from_zips(
        zip_dir,
        pdf_dest,
        spreadsheet_dest,
        other_dest
    )
    
    # Gera relatório
    generate_extraction_report(stats, report_path)
    
    # Resumo final
    print("\n" + "="*70)
    print("RESUMO DA EXTRAÇÃO")
    print("="*70)
    print(f"✅ ZIPs processados: {stats['zips_processed']}")
    if stats['zips_errors'] > 0:
        print(f"❌ ZIPs com erro: {stats['zips_errors']}")
    print()
    print("📄 Arquivos extraídos:")
    for file_type, count in sorted(stats['files_extracted'].items()):
        print(f"   {file_type}: {count}")
    print()
    print("⏭️  Arquivos ignorados (já existiam):")
    for file_type, count in sorted(stats['files_skipped'].items()):
        print(f"   {file_type}: {count}")
    print()
    print(f"📋 Tipos de arquivo encontrados: {len(stats['file_types_found'])}")
    print(f"   {', '.join(sorted(stats['file_types_found']))}")
    print()
    print(f"📄 Relatório salvo em: {report_path}")
    print("="*70)


if __name__ == "__main__":
    main()

