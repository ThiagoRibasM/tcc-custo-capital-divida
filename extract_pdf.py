import pdfplumber

pdf_path = 'docs/Manual TCC EAD Financas turma 6.pdf'

try:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n\n"
            
        print(full_text)
except Exception as e:
    print(f"Error: {e}")
