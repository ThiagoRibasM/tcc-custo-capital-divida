#!/usr/bin/env python3
"""
Script para melhorar a extração de títulos das referências.
"""
import re
from pathlib import Path

REFERENCES_MD = Path(__file__).parent.parent.parent / "docs" / "references.md"

def extract_title_improved(block):
    """Extrai título de uma referência de forma mais robusta."""
    # Remove quebras de linha
    text = ' '.join(block.split('\n'))
    
    # Padrão 1: Título entre ponto após autores e ** (periódico)
    # Ex: AUTORES. Título. **Periódico**
    match = re.search(r'\.\s+([A-ZÁÉÍÓÚÇ][^\.]+?)\s+\*\*', text)
    if match:
        title = match.group(1).strip().rstrip('.')
        # Remove nomes de autores se houver no início
        title = re.sub(r'^[A-ZÁÉÍÓÚÇ][A-ZÁÉÍÓÚÇ\s,;]+\.\s*', '', title)
        title = title.lstrip('.,; ').strip()
        if len(title) > 5:
            return title
    
    # Padrão 2: Título em negrito **Título**
    match = re.search(r'\*\*([^*]+)\*\*', text)
    if match:
        title = match.group(1).strip()
        # Se não começa com maiúscula, pode ser periódico, não título
        if title and title[0].isupper() and len(title) > 10:
            # Verifica se não é um padrão de periódico
            if not re.match(r'^[A-Z\s]+$', title[:20]):  # Não é só maiúsculas
                return title
    
    return None

def main():
    """Testa extração melhorada."""
    with open(REFERENCES_MD, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'\n\s*\n', content)
    titles_found = 0
    
    for block in blocks:
        if not block.strip() or block.startswith('#'):
            continue
        
        title = extract_title_improved(block)
        if title:
            titles_found += 1
            print(f"✅ {title[:70]}")
        else:
            # Tenta extrair autores para debug
            author_match = re.match(r'^([A-ZÁÉÍÓÚÇ][^\.]+)\.', block)
            if author_match:
                print(f"❌ [Sem título] - {author_match.group(1)[:50]}")
    
    print(f"\nTotal: {titles_found} títulos extraídos")

if __name__ == "__main__":
    main()

