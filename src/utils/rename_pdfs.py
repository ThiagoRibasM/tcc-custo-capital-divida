#!/usr/bin/env python3
"""
Script para renomear PDFs existentes usando apenas o título.
"""
import os
import re
from pathlib import Path
from download_references import extract_references_from_markdown, normalize_filename, REFERENCES_MD, OUTPUT_DIR

def get_title_from_pdf_content(pdf_path):
    """Tenta extrair título do conteúdo do PDF (se possível)."""
    # Por enquanto, retorna None - pode ser implementado com PyPDF2 ou pdfplumber
    return None

def match_pdf_to_reference(pdf_path, references):
    """Tenta fazer match de um PDF com uma referência baseado no nome atual."""
    pdf_name = pdf_path.stem.lower()
    
    for ref in references:
        # Tenta match por título
        title = ref.get('title', '').lower()
        if title and title in pdf_name:
            return ref
        
        # Tenta match por autores
        authors = ref.get('authors', '').lower()
        if authors and any(author.split(',')[0].strip() in pdf_name for author in authors.split(';')):
            # Se encontrou match por autor, verifica se tem título
            if ref.get('title') and ref.get('title') != 'Unknown':
                return ref
    
    return None

def main():
    """Renomeia PDFs existentes."""
    print("🔄 Renomeando PDFs existentes...\n")
    
    # Extrai referências
    references = extract_references_from_markdown(REFERENCES_MD)
    print(f"📖 {len(references)} referências encontradas\n")
    
    # Lista PDFs existentes
    pdf_files = list(OUTPUT_DIR.glob("*.pdf"))
    print(f"📄 {len(pdf_files)} PDFs encontrados\n")
    
    renamed_count = 0
    skipped_count = 0
    
    for pdf_path in pdf_files:
        current_name = pdf_path.name
        print(f"📄 Processando: {current_name}")
        
        # Tenta fazer match com referência
        ref = match_pdf_to_reference(pdf_path, references)
        
        if ref:
            # Gera novo nome baseado no título
            new_name = normalize_filename(ref.get('title', 'Unknown'), max_length=150)
            if not new_name.endswith('.pdf'):
                new_name += '.pdf'
            
            new_path = OUTPUT_DIR / new_name
            
            # Se o novo nome já existe e é diferente, adiciona sufixo
            if new_path.exists() and new_path != pdf_path:
                base_name = new_name.replace('.pdf', '')
                counter = 1
                while new_path.exists():
                    new_name = f"{base_name}_{counter}.pdf"
                    new_path = OUTPUT_DIR / new_name
                    counter += 1
            
            if new_path != pdf_path:
                try:
                    pdf_path.rename(new_path)
                    print(f"  ✅ Renomeado para: {new_name}")
                    renamed_count += 1
                except Exception as e:
                    print(f"  ❌ Erro ao renomear: {e}")
            else:
                print(f"  ⏭️  Já está com o nome correto")
                skipped_count += 1
        else:
            print(f"  ⚠️  Não foi possível fazer match com referência")
            skipped_count += 1
        
        print()
    
    print(f"{'='*50}")
    print(f"✅ Renomeação concluída!")
    print(f"   Renomeados: {renamed_count}")
    print(f"   Ignorados: {skipped_count}")

if __name__ == "__main__":
    main()

