#!/usr/bin/env python3
"""
Script para remover arquivos duplicados, mantendo apenas os da estrutura unificada.
"""
from pathlib import Path
from collections import defaultdict
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import (
    EXTRACTED_PDFS_DFP,
    DFP_NOVO_MERCADO_PATH,
)


def find_and_remove_duplicates(dry_run: bool = True):
    """
    Encontra e remove PDFs duplicados da estrutura antiga.
    Mantém apenas os da estrutura unificada (extracted_pdfs/).
    """
    print("="*70)
    print("REMOÇÃO DE ARQUIVOS DUPLICADOS")
    print("="*70)
    print()
    
    if dry_run:
        print("🔍 MODO DRY-RUN (simulação - nenhum arquivo será removido)")
    else:
        print("⚠️  MODO REAL - Arquivos serão REMOVIDOS permanentemente!")
    print()
    
    # Estrutura: (nome, tamanho) -> lista de paths
    files_by_key = defaultdict(list)
    
    # Coleta PDFs da estrutura nova (manter)
    print("📂 Escaneando estrutura nova (MANTER):")
    new_structure_dirs = [
        EXTRACTED_PDFS_DFP,
    ]
    
    for directory in new_structure_dirs:
        if not directory.exists():
            continue
        print(f"   {directory}")
        for pdf_file in directory.rglob("*.pdf"):
            if pdf_file.is_file():
                key = (pdf_file.name, pdf_file.stat().st_size)
                files_by_key[key].append(('new', pdf_file))
    
    # Coleta PDFs da estrutura antiga (verificar duplicação)
    print("\n📂 Escaneando estrutura antiga (VERIFICAR):")
    old_structure_dirs = [
        DFP_NOVO_MERCADO_PATH,
    ]
    
    files_to_remove = []
    
    for directory in old_structure_dirs:
        if not directory.exists():
            continue
        print(f"   {directory}")
        for pdf_file in directory.rglob("*.pdf"):
            if pdf_file.is_file():
                key = (pdf_file.name, pdf_file.stat().st_size)
                
                # Verifica se existe na estrutura nova
                if key in files_by_key:
                    # Verifica se algum arquivo na lista é da estrutura nova
                    has_new = any(origin == 'new' for origin, _ in files_by_key[key])
                    if has_new:
                        files_to_remove.append(pdf_file)
                        print(f"   ⚠️  Duplicado encontrado: {pdf_file.name}")
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    print(f"📄 Total de PDFs duplicados encontrados: {len(files_to_remove)}")
    print()
    
    if files_to_remove:
        print("📋 Arquivos que serão removidos (primeiros 20):")
        for i, file_path in enumerate(files_to_remove[:20], 1):
            print(f"   {i}. {file_path}")
        if len(files_to_remove) > 20:
            print(f"   ... e mais {len(files_to_remove) - 20} arquivos.")
        print()
        
        if not dry_run:
            print("🗑️  Removendo arquivos...")
            removed = 0
            errors = 0
            
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    removed += 1
                    if removed % 50 == 0:
                        print(f"   ✅ Removidos {removed}/{len(files_to_remove)} arquivos...")
                except Exception as e:
                    errors += 1
                    print(f"   ❌ Erro ao remover {file_path}: {e}")
            
            print(f"\n✅ Remoção concluída:")
            print(f"   Arquivos removidos: {removed}")
            if errors > 0:
                print(f"   Erros: {errors}")
        else:
            print("💡 Execute com --execute para remover os arquivos de fato.")
    else:
        print("✅ Nenhum arquivo duplicado encontrado para remover.")
    
    return files_to_remove


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remove arquivos duplicados')
    parser.add_argument('--execute', action='store_true', 
                       help='Executa a remoção (sem este flag, apenas simula)')
    args = parser.parse_args()
    
    find_and_remove_duplicates(dry_run=not args.execute)


if __name__ == "__main__":
    main()

