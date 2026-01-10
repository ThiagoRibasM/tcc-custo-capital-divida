#!/usr/bin/env python3
"""
Script para renomear PDFs existentes usando apenas o título.
"""
import os
import re
from pathlib import Path
import sys

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))
from download_references import extract_references_from_markdown, normalize_filename, REFERENCES_MD, OUTPUT_DIR

def match_pdf_to_reference(pdf_path, references):
    """Tenta fazer match de um PDF com uma referência baseado no nome atual."""
    pdf_name = pdf_path.stem.lower()
    
    best_match = None
    best_score = 0
    
    for ref in references:
        score = 0
        
        # Tenta match por título
        title = ref.get('title', '').lower()
        if title and title != 'unknown':
            # Verifica se palavras do título estão no nome do PDF
            title_words = set(re.findall(r'\w+', title))
            pdf_words = set(re.findall(r'\w+', pdf_name))
            common_words = title_words.intersection(pdf_words)
            if common_words:
                score = len(common_words) / max(len(title_words), 1)
        
        # Tenta match por autores (primeiro sobrenome)
        authors = ref.get('authors', '').lower()
        if authors:
            author_parts = authors.split(';')
            for author in author_parts:
                first_name = author.split(',')[0].strip() if ',' in author else author.split()[0]
                if first_name and len(first_name) > 3 and first_name in pdf_name:
                    score += 0.3
                    break
        
        if score > best_score:
            best_score = score
            best_match = ref
    
    # Só retorna match se score for razoável
    return best_match if best_score > 0.2 else None

def main():
    """Renomeia PDFs existentes."""
    print("🔄 Renomeando PDFs existentes usando títulos...\n")
    
    # Extrai referências
    references = extract_references_from_markdown(REFERENCES_MD)
    print(f"📖 {len(references)} referências encontradas\n")
    
    # Lista PDFs existentes
    pdf_files = list(OUTPUT_DIR.glob("*.pdf"))
    print(f"📄 {len(pdf_files)} PDFs encontrados\n")
    
    renamed_count = 0
    skipped_count = 0
    not_found_count = 0
    
    for pdf_path in pdf_files:
        current_name = pdf_path.name
        print(f"📄 {current_name}")
        
        # Tenta fazer match com referência
        ref = match_pdf_to_reference(pdf_path, references)
        
        if ref and ref.get('title') and ref.get('title') != 'Unknown':
            # Gera novo nome baseado no título
            new_name = normalize_filename(ref.get('title'), max_length=150)
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
                    skipped_count += 1
            else:
                print(f"  ⏭️  Já está com o nome correto")
                skipped_count += 1
        else:
            print(f"  ⚠️  Não foi possível fazer match com referência")
            not_found_count += 1
        
        print()
    
    print(f"{'='*50}")
    print(f"✅ Renomeação concluída!")
    print(f"   Renomeados: {renamed_count}")
    print(f"   Já corretos/Ignorados: {skipped_count}")
    print(f"   Não encontrados: {not_found_count}")

if __name__ == "__main__":
    main()

