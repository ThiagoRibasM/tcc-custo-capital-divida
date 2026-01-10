#!/usr/bin/env python3
"""
Script para reorganizar PDFs extraídos em estrutura unificada.
Copia PDFs mantendo organização, evitando duplicação.
"""
import shutil
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import (
    DFP_NOVO_MERCADO_PATH,
    DATA_RAW,
    LLM_EXTRACTIONS_PATH
)


def copy_dfp_pdfs():
    """
    Copia PDFs de DFPs (todos na mesma pasta).
    Origem: data/raw/dfp_2024/DFPs_CVM/Novo_Mercado/
    Destino: data/raw/extracted_pdfs/dfp/
    """
    source_dir = DFP_NOVO_MERCADO_PATH
    dest_dir = DATA_RAW / "extracted_pdfs" / "dfp"
    
    if not source_dir.exists():
        print(f"⚠️  Diretório origem não encontrado: {source_dir}")
        return 0, 0
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    skipped = 0
    
    print(f"\n📂 Copiando PDFs de DFPs...")
    print(f"   Origem: {source_dir}")
    print(f"   Destino: {dest_dir}")
    
    # Copia todos os PDFs
    for pdf_file in source_dir.glob("*.pdf"):
        dest_file = dest_dir / pdf_file.name
        
        if dest_file.exists():
            print(f"   ⏭️  Já existe: {pdf_file.name}")
            skipped += 1
        else:
            shutil.copy2(pdf_file, dest_file)
            copied += 1
            if copied % 10 == 0:
                print(f"   ✅ Copiados {copied} arquivos...")
    
    print(f"\n✅ DFPs: {copied} copiados, {skipped} já existentes")
    return copied, skipped


def organize_csvs():
    """
    Organiza CSVs existentes em subpasta dfp/.
    """
    source_dir = LLM_EXTRACTIONS_PATH
    dfp_dest = LLM_EXTRACTIONS_PATH / "dfp"
    
    dfp_dest.mkdir(exist_ok=True)
    
    moved = 0
    
    print(f"\n📂 Organizando CSVs...")
    print(f"   Origem: {source_dir}")
    
    # Move CSVs de DFPs (formato LLM_EMPRESA.csv)
    for csv_file in source_dir.glob("LLM_*.csv"):
        dest_file = dfp_dest / csv_file.name
        if not dest_file.exists():
            shutil.move(str(csv_file), str(dest_file))
            moved += 1
        else:
            # Se já existe no destino, remove o original
            csv_file.unlink()
            print(f"   ⏭️  Já existe: {csv_file.name}")
    
    print(f"   ✅ {moved} CSVs de DFPs movidos para dfp/")
    
    return moved


def main():
    """Função principal."""
    print("="*70)
    print("REORGANIZAÇÃO DE PDFs EXTRAÍDOS")
    print("="*70)
    
    # Copia PDFs
    dfp_copied, dfp_skipped = copy_dfp_pdfs()
    
    # Organiza CSVs
    csvs_moved = organize_csvs()
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO DA REORGANIZAÇÃO")
    print("="*70)
    print(f"📄 PDFs de DFPs: {dfp_copied} copiados, {dfp_skipped} já existentes")
    print(f"📊 CSVs organizados: {csvs_moved} movidos")
    print(f"\n✅ Reorganização concluída!")
    print(f"   PDFs em: data/raw/extracted_pdfs/dfp/")
    print(f"   CSVs em: data/processed/llm_extractions/dfp/")


if __name__ == "__main__":
    main()

