#!/usr/bin/env python3
"""
Script para extrair apenas PDFs dos ZIPs de DFPs.
Planilhas e XMLs não são extraídos, apenas PDFs.
"""
import zipfile
from pathlib import Path
import sys
from collections import defaultdict

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import DFP_2024_PATH, EXTRACTED_PDFS_DFP


def extract_pdfs_from_zips(
    zip_dir: Path,
    pdf_dest: Path
) -> dict:
    """
    Extrai apenas PDFs dos ZIPs, ignorando planilhas e XMLs.
    
    Args:
        zip_dir: Diretório com os ZIPs
        pdf_dest: Destino para PDFs
    
    Returns:
        Dicionário com estatísticas da extração
    """
    # Cria diretório de destino
    pdf_dest.mkdir(parents=True, exist_ok=True)
    
    # Estatísticas
    stats = {
        'zips_processed': 0,
        'zips_errors': 0,
        'pdfs_extracted': 0,
        'pdfs_skipped': 0,
        'other_files_found': 0,
        'errors': []
    }
    
    # Lista todos os ZIPs
    zip_files = list(zip_dir.glob('*.zip'))
    total_zips = len(zip_files)
    
    print("="*70)
    print("EXTRAÇÃO DE PDFs DOS ZIPs")
    print("="*70)
    print(f"📦 Total de ZIPs encontrados: {total_zips}")
    print(f"📄 PDFs → {pdf_dest}")
    print("⚠️  Apenas PDFs serão extraídos (planilhas e XMLs ignorados)")
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
                    
                    # Verifica se é PDF
                    file_path = Path(file_name)
                    if file_path.suffix.lower() != '.pdf':
                        stats['other_files_found'] += 1
                        continue  # Ignora arquivos que não são PDFs
                    
                    # Nome do arquivo final
                    final_name = file_path.name
                    dest_path = pdf_dest / final_name
                    
                    # Verifica se já existe (evita duplicação)
                    if dest_path.exists():
                        stats['pdfs_skipped'] += 1
                        continue
                    
                    # Extrai apenas PDFs
                    try:
                        # Lê conteúdo do arquivo
                        file_content = zip_ref.read(file_name)
                        
                        # Salva no destino
                        with open(dest_path, 'wb') as f:
                            f.write(file_content)
                        
                        stats['pdfs_extracted'] += 1
                        
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
        f.write("# Relatório de Extração de PDFs dos ZIPs\n\n")
        f.write(f"**Data:** {Path(__file__).stat().st_mtime}\n\n")
        f.write("---\n\n")
        
        f.write("## Estatísticas Gerais\n\n")
        f.write(f"- **ZIPs processados:** {stats['zips_processed']}\n")
        f.write(f"- **ZIPs com erro:** {stats['zips_errors']}\n")
        f.write(f"- **Total de erros:** {len(stats['errors'])}\n\n")
        
        f.write("## PDFs Extraídos\n\n")
        f.write(f"- **PDFs extraídos:** {stats['pdfs_extracted']}\n")
        f.write(f"- **PDFs ignorados (já existiam):** {stats['pdfs_skipped']}\n")
        f.write(f"- **Outros arquivos encontrados (ignorados):** {stats['other_files_found']}\n\n")
        
        f.write("## Nota\n\n")
        f.write("Apenas PDFs são extraídos. Planilhas (Excel/CSV) e XMLs são ignorados.\n\n")
        
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
    report_path = DFP_2024_PATH / "extraction_report.md"
    
    # Extrai apenas PDFs
    stats = extract_pdfs_from_zips(
        zip_dir,
        pdf_dest
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
    print(f"📄 PDFs extraídos: {stats['pdfs_extracted']}")
    print(f"⏭️  PDFs ignorados (já existiam): {stats['pdfs_skipped']}")
    print(f"📁 Outros arquivos encontrados (ignorados): {stats['other_files_found']}")
    print()
    print(f"📄 Relatório salvo em: {report_path}")
    print("="*70)


if __name__ == "__main__":
    main()

