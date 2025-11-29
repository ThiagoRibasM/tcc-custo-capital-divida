#!/usr/bin/env python3
"""
Extração otimizada de dados financeiros de PDFs usando LLM.
Implementa estratégias de otimização de tokens e chunking inteligente.
"""
import json
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import sys
import os
from openai import OpenAI

sys.path.append(str(Path(__file__).parent.parent))
from utils.financial_extraction_config import (
    get_extraction_prompt,
    LLM_MODEL,
    LLM_TEMPERATURE,
    CHUNKING_CONFIG
)


def find_relevant_pages(pdf_path: Path, sections: List[str] = None) -> List[int]:
    """
    Encontra páginas relevantes (Balanço e DRE) no PDF.
    
    Args:
        pdf_path: Caminho do PDF
        sections: Lista de seções a buscar
        
    Returns:
        Lista de números de páginas relevantes
    """
    if sections is None:
        sections = CHUNKING_CONFIG["sections_to_find"]
    
    relevant_pages = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue
                
                text_lower = text.lower()
                # Verifica se página contém alguma seção relevante
                for section in sections:
                    if section.lower() in text_lower:
                        relevant_pages.append(page_num)
                        break
    except Exception as e:
        print(f"⚠️  Erro ao processar PDF {pdf_path.name}: {e}")
        return []
    
    return relevant_pages


def extract_text_from_pages(pdf_path: Path, page_numbers: List[int] = None, max_pages: int = 15) -> str:
    """
    Extrai texto de páginas específicas do PDF.
    
    Args:
        pdf_path: Caminho do PDF
        page_numbers: Lista de números de páginas (None = todas)
        max_pages: Máximo de páginas a extrair
        
    Returns:
        Texto extraído
    """
    text_parts = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_numbers:
                pages_to_extract = [p for p in page_numbers if 1 <= p <= len(pdf.pages)][:max_pages]
            else:
                pages_to_extract = list(range(1, min(len(pdf.pages) + 1, max_pages + 1)))
            
            for page_num in pages_to_extract:
                page = pdf.pages[page_num - 1]
                text = page.extract_text()
                if text:
                    # Remove headers/footers repetitivos (linhas muito curtas)
                    lines = text.split('\n')
                    cleaned_lines = [line for line in lines if len(line.strip()) > 5]
                    text_parts.append('\n'.join(cleaned_lines))
    except Exception as e:
        print(f"⚠️  Erro ao extrair texto de {pdf_path.name}: {e}")
        return ""
    
    return '\n\n'.join(text_parts)


def extract_financial_data_from_pdf(pdf_path: Path) -> Tuple[Dict, float, List[str]]:
    """
    Extrai dados financeiros de um PDF usando LLM.
    
    Args:
        pdf_path: Caminho do PDF
        
    Returns:
        Tupla (dados_extraídos, confiança, observações)
    """
    # Tenta carregar de .env se disponível
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv não instalado, usa variável de ambiente
    
    # Inicializa cliente OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada. Configure em .env ou variável de ambiente")
    
    client = OpenAI(api_key=api_key)
    
    # Encontra páginas relevantes
    relevant_pages = find_relevant_pages(pdf_path)
    
    if not relevant_pages:
        # Se não encontrou, usa primeiras páginas
        relevant_pages = list(range(1, min(16, 20)))  # Primeiras 15-20 páginas
    
    # Extrai texto das páginas relevantes
    text = extract_text_from_pages(pdf_path, relevant_pages, max_pages=CHUNKING_CONFIG["max_pages"])
    
    if not text or len(text) < 100:
        return {}, 0.0, ["PDF vazio ou texto insuficiente"]
    
    # Limita tamanho do texto (aproximadamente 8000 tokens = ~32000 caracteres)
    max_chars = CHUNKING_CONFIG["max_tokens_per_chunk"] * 4
    if len(text) > max_chars:
        text = text[:max_chars]
        print(f"   ⚠️  Texto truncado para {max_chars} caracteres")
    
    # Prepara prompt
    prompt = get_extraction_prompt()
    full_prompt = f"{prompt}\n\nTEXTO DO PDF:\n\n{text}"
    
    # Chama LLM
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de demonstrações financeiras brasileiras."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=LLM_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        # Extrai resposta
        content = response.choices[0].message.content
        
        # Tenta parsear JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Tenta extrair JSON do texto
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                return {}, 0.0, ["Resposta não é JSON válido"]
        
        # Calcula confiança baseado em quantos campos foram preenchidos
        all_fields = [
            "Ativo_Total", "Passivo_Total", "Patrimonio_Liquido",
            "Divida_Total", "Receita_Liquida", "Lucro_Liquido"
        ]
        filled_fields = sum(1 for field in all_fields if data.get(field) is not None)
        confidence = filled_fields / len(all_fields)
        
        observations = []
        if confidence < 0.5:
            observations.append("Baixa confiança: poucos campos preenchidos")
        if not relevant_pages:
            observations.append("Páginas relevantes não encontradas automaticamente")
        
        return data, confidence, observations
        
    except Exception as e:
        return {}, 0.0, [f"Erro na chamada LLM: {str(e)}"]


def validate_extracted_data(data: Dict) -> Tuple[bool, List[str]]:
    """
    Valida dados extraídos.
    
    Args:
        data: Dados extraídos
        
    Returns:
        Tupla (é_válido, lista_de_erros)
    """
    errors = []
    
    # Verifica se há dados básicos
    if not data:
        return False, ["Nenhum dado extraído"]
    
    # Verifica consistência básica (Ativo = Passivo + PL)
    # Nota: Em alguns casos, Passivo_Total pode já incluir PL, então verificamos ambas possibilidades
    ativo = data.get("Ativo_Total")
    passivo = data.get("Passivo_Total")
    pl = data.get("Patrimonio_Liquido")
    
    if ativo and passivo is not None and pl is not None:
        # Tenta duas interpretações:
        # 1. Passivo Total não inclui PL: Ativo = Passivo + PL
        # 2. Passivo Total inclui PL: Ativo = Passivo
        expected_ativo_1 = passivo + pl
        expected_ativo_2 = passivo
        
        diff_pct_1 = abs(ativo - expected_ativo_1) / max(abs(expected_ativo_1), 1) * 100
        diff_pct_2 = abs(ativo - expected_ativo_2) / max(abs(expected_ativo_2), 1) * 100
        
        # Se nenhuma das duas interpretações estiver próxima (tolerância de 2%), marca erro
        if diff_pct_1 > 2 and diff_pct_2 > 2:
            errors.append(f"Inconsistência: Ativo ({ativo:,.0f}) não corresponde a Passivo ({passivo:,.0f}) + PL ({pl:,.0f}) ou Passivo Total")
    
    # Verifica se dívida total = curto prazo + longo prazo
    divida_total = data.get("Divida_Total")
    divida_cp = data.get("Divida_Curto_Prazo")
    divida_lp = data.get("Divida_Longo_Prazo")
    
    if divida_total and divida_cp is not None and divida_lp is not None:
        expected_divida = divida_cp + divida_lp
        if abs(divida_total - expected_divida) > divida_total * 0.05:  # 5% de tolerância
            errors.append(f"Inconsistência: Dívida Total pode não ser igual a CP + LP")
    
    return len(errors) == 0, errors


def main():
    """Função principal para teste."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python extract_financial_data_optimized.py <caminho_do_pdf>")
        return
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"❌ PDF não encontrado: {pdf_path}")
        return
    
    print(f"📄 Processando: {pdf_path.name}")
    print("=" * 70)
    
    data, confidence, observations = extract_financial_data_from_pdf(pdf_path)
    
    print(f"\n✅ Extração concluída (confiança: {confidence:.2%})")
    print(f"\n📊 Dados extraídos:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    if observations:
        print(f"\n⚠️  Observações:")
        for obs in observations:
            print(f"   - {obs}")
    
    is_valid, errors = validate_extracted_data(data)
    if is_valid:
        print("\n✅ Dados validados com sucesso")
    else:
        print("\n⚠️  Erros de validação:")
        for error in errors:
            print(f"   - {error}")


if __name__ == "__main__":
    main()

