#!/usr/bin/env python3
"""
Script final para renomear todos os PDFs usando apenas títulos.
"""
import re
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
from download_references import extract_references_from_markdown, normalize_filename, REFERENCES_MD, OUTPUT_DIR

def extract_title_from_reference_text(text):
    """Extrai título diretamente do texto da referência."""
    # Padrão: AUTORES. Título. **Periódico**
    match = re.search(r'\.\s+([^\.]+?)\s+\*\*', text)
    if match:
        title = match.group(1).strip().rstrip('.')
        # Remove nomes de autores se houver
        title = re.sub(r'^[A-ZÁÉÍÓÚÇ][A-ZÁÉÍÓÚÇ\s,;]+\.\s*', '', title)
        title = title.lstrip('.,; ').strip()
        
        # Verifica se não é periódico (periódicos geralmente são só maiúsculas)
        first_words = title.split()[:3]
        if first_words:
            all_upper = all(word.replace('&', '').replace(',', '').isupper() 
                          for word in first_words if word and len(word) > 1)
            # Se é só maiúsculas e tem poucas palavras, provavelmente é periódico
            if all_upper and len(title.split()) < 5:
                return None
        
        if len(title) > 5:
            return title
    return None

def get_title_for_pdf(pdf_name, references):
    """Tenta encontrar o título correto para um PDF."""
    pdf_lower = pdf_name.lower()
    
    # Mapeamento manual para PDFs conhecidos
    manual_map = {
        'unknown_2009': 'Nível de evidenciação × custo da dívida das empresas brasileiras',
        'unknown_2017': 'A influência do disclosure voluntário no custo da dívida de financiamentos em empresas listadas na BM&FBOVESPA',
        'unknown_2018': 'Capital Structure in U.S., a Quantile Regression Approach with Macroeconomic Impacts',
        'unknown_2022': 'A heterogeneidade da estrutura de dívida reduz o custo de capital?',
        'financial_constraints_risk': 'Financial Constraints Risk',
        'financial_constraints_risk_1': 'New Evidence on Measuring Financial Constraints: Moving Beyond the KZ Index',
        'glenn_petersen': 'Financing Constraints and Corporate Investment',
        'kaloudis': 'Capital Structure in U.S., a Quantile Regression Approach with Macroeconomic Impacts',
    }
    
    for key, title in manual_map.items():
        if key in pdf_lower:
            return title
    
    # Tenta match automático
    for ref in references:
        title = ref.get('title', '')
        if title and title != 'Unknown':
            # Verifica se palavras do título estão no nome do PDF
            title_words = set(re.findall(r'\w+', title.lower()))
            pdf_words = set(re.findall(r'\w+', pdf_lower))
            common = title_words.intersection(pdf_words)
            if len(common) >= 3:  # Pelo menos 3 palavras em comum
                return title
    
    return None

def main():
    """Renomeia todos os PDFs."""
    print("🔄 Renomeando todos os PDFs para usar apenas títulos...\n")
    
    # Extrai referências
    references = extract_references_from_markdown(REFERENCES_MD)
    
    # Lê referências do markdown diretamente para melhor extração
    with open(REFERENCES_MD, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    blocks = re.split(r'\n\s*\n', md_content)
    title_map = {}
    
    for block in blocks:
        if not block.strip() or block.startswith('#'):
            continue
        title = extract_title_from_reference_text(block)
        if title:
            # Extrai autores para matching
            author_match = re.match(r'^([A-ZÁÉÍÓÚÇ][^\.]+)\.', block)
            if author_match:
                authors = author_match.group(1).strip()
                title_map[authors] = title
    
    # Lista PDFs
    pdf_files = list(OUTPUT_DIR.glob("*.pdf"))
    print(f"📄 {len(pdf_files)} PDFs encontrados\n")
    
    renamed = 0
    skipped = 0
    
    for pdf_path in pdf_files:
        current_name = pdf_path.name
        print(f"📄 {current_name}")
        
        # Tenta encontrar título
        title = get_title_for_pdf(current_name, references)
        
        if not title:
            # Tenta match por autores
            for authors, ref_title in title_map.items():
                first_author = authors.split(';')[0].split(',')[0].strip()
                if first_author.lower() in current_name.lower():
                    title = ref_title
                    break
        
        if title:
            new_name = normalize_filename(title, max_length=150) + '.pdf'
            new_path = OUTPUT_DIR / new_name
            
            # Se já existe e é diferente, adiciona sufixo
            if new_path.exists() and new_path != pdf_path:
                base = new_name.replace('.pdf', '')
                counter = 1
                while new_path.exists():
                    new_name = f"{base}_{counter}.pdf"
                    new_path = OUTPUT_DIR / new_name
                    counter += 1
            
            if new_path != pdf_path:
                try:
                    pdf_path.rename(new_path)
                    print(f"  ✅ Renomeado para: {new_name}")
                    renamed += 1
                except Exception as e:
                    print(f"  ❌ Erro: {e}")
                    skipped += 1
            else:
                print(f"  ⏭️  Já está correto")
                skipped += 1
        else:
            print(f"  ⚠️  Título não encontrado")
            skipped += 1
        
        print()
    
    print(f"{'='*50}")
    print(f"✅ Concluído!")
    print(f"   Renomeados: {renamed}")
    print(f"   Ignorados: {skipped}")
    
    # Verifica duplicatas finais
    print(f"\n🔍 Verificando duplicatas...")
    pdfs = list(OUTPUT_DIR.glob("*.pdf"))
    names = {}
    for pdf in pdfs:
        base = re.sub(r'_\d+\.pdf$', '.pdf', pdf.name)
        if base in names:
            names[base].append(pdf.name)
        else:
            names[base] = [pdf.name]
    
    dups = {k: v for k, v in names.items() if len(v) > 1}
    if dups:
        print("⚠️  Duplicatas encontradas:")
        for base, files in dups.items():
            print(f"  {base}:")
            for f in files:
                print(f"    - {f}")
    else:
        print("✅ Nenhuma duplicata encontrada")

if __name__ == "__main__":
    main()

