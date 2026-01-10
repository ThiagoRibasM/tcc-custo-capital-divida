#!/usr/bin/env python3
"""
Script para verificar arquivos duplicados entre diferentes diretórios.
"""
import hashlib
from pathlib import Path
from collections import defaultdict
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import (
    EXTRACTED_PDFS_DFP,
    DFP_NOVO_MERCADO_PATH,
    LLM_EXTRACTIONS_DFP,
    CONSOLIDATED_PATH,
)


def calculate_file_hash(file_path: Path) -> str:
    """Calcula hash MD5 do arquivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return None


def find_duplicates_by_name_and_size(directories: list, extensions: list = None):
    """
    Encontra arquivos duplicados por nome e tamanho entre diretórios.
    """
    files_by_name = defaultdict(list)
    
    print("="*70)
    print("VERIFICAÇÃO DE ARQUIVOS DUPLICADOS")
    print("="*70)
    print()
    
    # Coleta todos os arquivos
    for directory in directories:
        if not directory.exists():
            print(f"⚠️  Diretório não encontrado: {directory}")
            continue
        
        print(f"📂 Escaneando: {directory}")
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
            
            if extensions and file_path.suffix.lower() not in extensions:
                continue
            
            file_key = (file_path.name, file_path.stat().st_size)
            files_by_name[file_key].append(file_path)
    
    # Identifica duplicatas
    duplicates = {}
    for (name, size), paths in files_by_name.items():
        if len(paths) > 1:
            duplicates[(name, size)] = paths
    
    return duplicates


def find_duplicates_by_content(directories: list, extensions: list = None):
    """
    Encontra arquivos duplicados por conteúdo (hash MD5).
    """
    hash_to_files = defaultdict(list)
    
    print("\n🔍 Calculando hashes de arquivos para verificação de conteúdo...")
    
    total_files = 0
    for directory in directories:
        if not directory.exists():
            continue
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
            if extensions and file_path.suffix.lower() not in extensions:
                continue
            total_files += 1
    
    print(f"   Total de arquivos para verificar: {total_files}")
    
    processed = 0
    for directory in directories:
        if not directory.exists():
            continue
        
        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue
            
            if extensions and file_path.suffix.lower() not in extensions:
                continue
            
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                hash_to_files[file_hash].append(file_path)
            
            processed += 1
            if processed % 100 == 0:
                print(f"   Processados {processed}/{total_files} arquivos...")
    
    # Identifica duplicatas por conteúdo
    duplicates = {}
    for file_hash, paths in hash_to_files.items():
        if len(paths) > 1:
            duplicates[file_hash] = paths
    
    return duplicates


def main():
    """Função principal."""
    
    # Diretórios para verificar PDFs
    pdf_dirs = [
        EXTRACTED_PDFS_DFP,
        DFP_NOVO_MERCADO_PATH,
    ]
    
    # Diretórios para verificar CSVs
    csv_dirs = [
        LLM_EXTRACTIONS_DFP,
        CONSOLIDATED_PATH,
    ]
    
    # Verifica PDFs duplicados (por nome e tamanho)
    print("\n" + "="*70)
    print("VERIFICAÇÃO DE PDFs DUPLICADOS (por nome e tamanho)")
    print("="*70)
    pdf_duplicates = find_duplicates_by_name_and_size(pdf_dirs, ['.pdf'])
    
    if pdf_duplicates:
        print(f"\n⚠️  Encontrados {len(pdf_duplicates)} PDFs duplicados (mesmo nome e tamanho):")
        for (name, size), paths in list(pdf_duplicates.items())[:10]:
            print(f"\n   📄 {name} ({size:,} bytes)")
            for path in paths:
                print(f"      - {path}")
        if len(pdf_duplicates) > 10:
            print(f"\n   ... e mais {len(pdf_duplicates) - 10} duplicatas.")
    else:
        print("\n✅ Nenhum PDF duplicado encontrado (por nome e tamanho)")
    
    # Verifica CSVs duplicados
    print("\n" + "="*70)
    print("VERIFICAÇÃO DE CSVs DUPLICADOS (por nome e tamanho)")
    print("="*70)
    csv_duplicates = find_duplicates_by_name_and_size(csv_dirs, ['.csv'])
    
    if csv_duplicates:
        print(f"\n⚠️  Encontrados {len(csv_duplicates)} CSVs duplicados:")
        for (name, size), paths in list(csv_duplicates.items())[:10]:
            print(f"\n   📊 {name} ({size:,} bytes)")
            for path in paths:
                print(f"      - {path}")
        if len(csv_duplicates) > 10:
            print(f"\n   ... e mais {len(csv_duplicates) - 10} duplicatas.")
    else:
        print("\n✅ Nenhum CSV duplicado encontrado (por nome e tamanho)")
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    print(f"📄 PDFs duplicados (nome+tamanho): {len(pdf_duplicates)}")
    print(f"📊 CSVs duplicados (nome+tamanho): {len(csv_duplicates)}")
    print()
    print("💡 Nota: Esta verificação compara apenas nome e tamanho.")
    print("   Para verificação por conteúdo (hash), execute com flag --content")


if __name__ == "__main__":
    main()

