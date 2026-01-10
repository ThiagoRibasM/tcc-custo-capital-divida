#!/usr/bin/env python3
"""
Script para extrair hipóteses e resultados principais de artigos acadêmicos.
Gera resumo executivo em markdown e tabela Excel.
"""
import os
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
import pdfplumber
import pandas as pd
from openai import OpenAI
import sys

# Adiciona o diretório 'src' ao sys.path
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import PROJECT_ROOT, DATA_EXTERNAL, REFERENCES_PATH

# Paths
REFERENCES_DIR = REFERENCES_PATH
OUTPUT_MD = PROJECT_ROOT / "docs" / "article_summaries.md"
OUTPUT_XLSX = PROJECT_ROOT / "docs" / "article_summaries_table.xlsx"

# Configuração OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Tamanho máximo de tokens por chunk (deixar margem para prompt e resposta)
MAX_TOKENS_PER_CHUNK = 100000  # ~75k caracteres
CHUNK_OVERLAP = 2000  # Sobreposição entre chunks


def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """Extrai texto de um PDF usando pdfplumber."""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"❌ Erro ao ler PDF {pdf_path.name}: {e}")
        return None


def split_text_into_chunks(text: str, max_chars: int = MAX_TOKENS_PER_CHUNK) -> List[str]:
    """Divide texto longo em chunks com sobreposição."""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chars
        
        # Se não é o último chunk, tenta quebrar em parágrafo
        if end < len(text):
            # Procura último parágrafo antes do limite
            last_paragraph = text.rfind('\n\n', start, end)
            if last_paragraph > start:
                end = last_paragraph + 2
        
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Próximo chunk começa com sobreposição
        start = end - CHUNK_OVERLAP
        if start >= len(text):
            break
    
    return chunks


def extract_summary_with_llm(text: str, pdf_name: str) -> Optional[Dict]:
    """Extrai resumo executivo usando OpenAI API."""
    if not client:
        print("❌ OPENAI_API_KEY não configurada")
        return None
    
    print(f"   🤖 Enviando {len(text)} caracteres para LLM...")
    start_time = time.time()
    
    prompt = f"""Extraia do seguinte texto de artigo acadêmico um RESUMO EXECUTIVO:

1. Título e autores
2. Hipóteses principais testadas (apenas as hipóteses centrais, H1, H2 principais)
3. Metodologia resumida (tipo de estudo, amostra, período - apenas uma linha)
4. Resultados principais (apenas resultados mais relevantes: significância, direção do efeito, estatísticas principais)
5. Conclusões principais (2-3 conclusões mais importantes)

Foque em informações essenciais para discussão acadêmica. Evite detalhes metodológicos extensos.

Retorne a resposta em formato JSON com as seguintes chaves:
- "titulo": string
- "autores": string
- "ano": string (se disponível)
- "hipoteses_principais": lista de strings
- "metodologia_resumida": string (uma linha)
- "resultados_principais": lista de strings
- "conclusoes_principais": lista de strings

Texto do artigo:
{text[:MAX_TOKENS_PER_CHUNK]}
"""
    
    try:
        print(f"   ⏳ Aguardando resposta da API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em análise de artigos acadêmicos. Extraia informações de forma precisa e estruturada."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        elapsed = time.time() - start_time
        print(f"   ✅ Resposta recebida em {elapsed:.1f}s")
        
        content = response.choices[0].message.content.strip()
        print(f"   📝 Resposta tem {len(content)} caracteres")
        
        # Tenta extrair JSON da resposta
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            print(f"   ✅ JSON encontrado na resposta")
            summary = json.loads(json_match.group(0))
            print(f"   ✅ Resumo extraído: título={bool(summary.get('titulo'))}, hipóteses={len(summary.get('hipoteses_principais', []))}")
            return summary
        else:
            # Se não encontrou JSON, tenta parsear manualmente
            print(f"   ⚠️  Resposta não está em JSON para {pdf_name}, tentando parsear...")
            summary = parse_text_response(content, pdf_name)
            print(f"   ✅ Resumo parseado: título={bool(summary.get('titulo'))}, hipóteses={len(summary.get('hipoteses_principais', []))}")
            return summary
    
    except Exception as e:
        print(f"   ❌ Erro ao processar com LLM {pdf_name}: {e}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return None


def parse_text_response(text: str, pdf_name: str) -> Dict:
    """Tenta parsear resposta em texto para estrutura JSON."""
    summary = {
        "titulo": "",
        "autores": "",
        "ano": "",
        "hipoteses_principais": [],
        "metodologia_resumida": "",
        "resultados_principais": [],
        "conclusoes_principais": []
    }
    
    # Tenta extrair título
    titulo_match = re.search(r'(?:Título|Title)[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
    if titulo_match:
        summary["titulo"] = titulo_match.group(1).strip()
    
    # Tenta extrair autores
    autores_match = re.search(r'(?:Autores|Authors)[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
    if autores_match:
        summary["autores"] = autores_match.group(1).strip()
    
    # Tenta extrair hipóteses
    hipoteses_section = re.search(r'(?:Hipóteses|Hypotheses)[:\s]+(.+?)(?:\n\n|\n(?:Metodologia|Methodology))', text, re.IGNORECASE | re.DOTALL)
    if hipoteses_section:
        hipoteses_text = hipoteses_section.group(1)
        # Divide por linhas que começam com H1, H2, ou números
        hipoteses = re.findall(r'(?:H\d+|^\d+\.)\s*(.+?)(?=\n|$)', hipoteses_text, re.MULTILINE)
        summary["hipoteses_principais"] = [h.strip() for h in hipoteses if h.strip()]
    
    # Tenta extrair resultados
    resultados_section = re.search(r'(?:Resultados|Results)[:\s]+(.+?)(?:\n\n|\n(?:Conclusões|Conclusions))', text, re.IGNORECASE | re.DOTALL)
    if resultados_section:
        resultados_text = resultados_section.group(1)
        # Divide por linhas que começam com bullet ou números
        resultados = re.findall(r'(?:[-•*]|\d+\.)\s*(.+?)(?=\n|$)', resultados_text, re.MULTILINE)
        summary["resultados_principais"] = [r.strip() for r in resultados if r.strip()][:5]  # Limita a 5
    
    # Tenta extrair conclusões
    conclusoes_section = re.search(r'(?:Conclusões|Conclusions)[:\s]+(.+?)(?:\n\n|$)', text, re.IGNORECASE | re.DOTALL)
    if conclusoes_section:
        conclusoes_text = conclusoes_section.group(1)
        conclusoes = re.findall(r'(?:[-•*]|\d+\.)\s*(.+?)(?=\n|$)', conclusoes_text, re.MULTILINE)
        summary["conclusoes_principais"] = [c.strip() for c in conclusoes if c.strip()][:3]  # Limita a 3
    
    return summary


def process_pdf(pdf_path: Path) -> Optional[Dict]:
    """Processa um PDF e retorna resumo estruturado."""
    print(f"\n{'='*60}")
    print(f"📄 Processando: {pdf_path.name}")
    print(f"{'='*60}")
    
    # Extrai texto
    print(f"   📖 Extraindo texto do PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"   ❌ Falha ao extrair texto")
        return None
    
    print(f"   ✅ Texto extraído: {len(text)} caracteres ({len(text.split())} palavras)")
    
    # Se texto é muito longo, processa em chunks
    if len(text) > MAX_TOKENS_PER_CHUNK:
        print(f"   ⚠️  Texto muito longo ({len(text)} chars), processando em chunks...")
        chunks = split_text_into_chunks(text)
        print(f"   📦 {len(chunks)} chunks criados (tamanhos: {[len(c) for c in chunks[:3]]}...)")
        
        # Processa primeiro chunk (geralmente contém abstract, introdução, conclusão)
        # e último chunk (geralmente contém conclusões)
        summaries = []
        chunks_to_process = [chunks[0], chunks[-1]] if len(chunks) > 1 else [chunks[0]]
        
        for i, chunk in enumerate(chunks_to_process):
            print(f"   🔄 Processando chunk {i+1}/{len(chunks_to_process)} ({len(chunk)} caracteres)...")
            summary = extract_summary_with_llm(chunk, pdf_path.name)
            if summary:
                summaries.append(summary)
                print(f"   ✅ Chunk {i+1} processado com sucesso")
            else:
                print(f"   ❌ Falha ao processar chunk {i+1}")
            time.sleep(2)  # Rate limiting
        
        # Combina summaries (prioriza informações do último chunk para conclusões)
        if summaries:
            print(f"   🔗 Combinando {len(summaries)} resumos...")
            combined = summaries[0].copy()
            if len(summaries) > 1:
                # Atualiza com informações do último chunk se disponíveis
                last_summary = summaries[-1]
                if last_summary.get("conclusoes_principais"):
                    combined["conclusoes_principais"] = last_summary["conclusoes_principais"]
                if last_summary.get("resultados_principais"):
                    combined["resultados_principais"] = last_summary["resultados_principais"]
            print(f"   ✅ Resumo combinado criado")
            return combined
        else:
            print(f"   ❌ Nenhum resumo foi gerado dos chunks")
            return None
    else:
        # Processa texto completo
        print(f"   📝 Processando texto completo...")
        summary = extract_summary_with_llm(text, pdf_path.name)
        if summary:
            print(f"   ✅ Resumo gerado com sucesso")
        else:
            print(f"   ❌ Falha ao gerar resumo")
        return summary


def generate_markdown(summaries: List[Dict]) -> str:
    """Gera markdown estruturado com resumos."""
    md_content = "# Resumo Executivo dos Artigos\n\n"
    md_content += "Este documento contém resumos executivos dos artigos acadêmicos, incluindo hipóteses principais testadas e resultados encontrados.\n\n"
    md_content += f"**Total de artigos processados:** {len(summaries)}\n\n"
    md_content += "---\n\n"
    
    for i, summary in enumerate(summaries, 1):
        md_content += f"## {i}. {summary.get('titulo', 'Título não disponível')}\n\n"
        
        if summary.get('autores'):
            md_content += f"**Autores:** {summary['autores']}\n\n"
        
        if summary.get('ano'):
            md_content += f"**Ano:** {summary['ano']}\n\n"
        
        if summary.get('metodologia_resumida'):
            md_content += f"**Metodologia:** {summary['metodologia_resumida']}\n\n"
        
        if summary.get('hipoteses_principais'):
            md_content += "### Hipóteses Principais\n\n"
            for j, hip in enumerate(summary['hipoteses_principais'], 1):
                md_content += f"{j}. {hip}\n"
            md_content += "\n"
        
        if summary.get('resultados_principais'):
            md_content += "### Resultados Principais\n\n"
            for j, res in enumerate(summary['resultados_principais'], 1):
                md_content += f"{j}. {res}\n"
            md_content += "\n"
        
        if summary.get('conclusoes_principais'):
            md_content += "### Conclusões Principais\n\n"
            for j, conc in enumerate(summary['conclusoes_principais'], 1):
                md_content += f"{j}. {conc}\n"
            md_content += "\n"
        
        md_content += "---\n\n"
    
    return md_content


def generate_excel(summaries: List[Dict]) -> pd.DataFrame:
    """Gera DataFrame para Excel."""
    rows = []
    
    for summary in summaries:
        row = {
            "Título": summary.get('titulo', ''),
            "Autores": summary.get('autores', ''),
            "Ano": summary.get('ano', ''),
            "Hipóteses Principais": "\n".join(summary.get('hipoteses_principais', [])),
            "Resultados Principais": "\n".join(summary.get('resultados_principais', [])),
            "Conclusões Principais": "\n".join(summary.get('conclusoes_principais', []))
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def main():
    """Função principal."""
    print("📚 Iniciando extração de resumos executivos dos artigos...\n")
    
    if not client:
        print("❌ OPENAI_API_KEY não configurada. Configure a variável de ambiente.")
        return
    
    # Lista PDFs
    pdf_files = sorted(REFERENCES_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ Nenhum PDF encontrado em {REFERENCES_DIR}")
        return
    
    print(f"📄 {len(pdf_files)} PDFs encontrados\n")
    
    summaries = []
    failed = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n{'#'*60}")
        print(f"# Artigo {i}/{len(pdf_files)}")
        print(f"{'#'*60}")
        
        summary = process_pdf(pdf_path)
        if summary:
            summaries.append(summary)
            print(f"✅ Artigo {i} processado com sucesso!")
        else:
            failed.append(pdf_path.name)
            print(f"❌ Falha ao processar artigo {i}")
        
        # Rate limiting entre artigos
        if i < len(pdf_files):
            print(f"\n⏸️  Aguardando 3 segundos antes do próximo artigo...")
            time.sleep(3)
    
    print(f"\n{'='*50}")
    print(f"✅ Processamento concluído!")
    print(f"   Sucessos: {len(summaries)}")
    print(f"   Falhas: {len(failed)}")
    
    if failed:
        print(f"\n⚠️  PDFs que falharam:")
        for f in failed:
            print(f"   - {f}")
    
    if summaries:
        # Gera markdown
        print(f"\n📝 Gerando markdown...")
        md_content = generate_markdown(summaries)
        OUTPUT_MD.write_text(md_content, encoding='utf-8')
        print(f"   ✅ Salvo em: {OUTPUT_MD}")
        
        # Gera Excel
        print(f"\n📊 Gerando tabela Excel...")
        df = generate_excel(summaries)
        df.to_excel(OUTPUT_XLSX, index=False, engine='openpyxl')
        print(f"   ✅ Salvo em: {OUTPUT_XLSX}")
        
        print(f"\n✅ Resumos gerados com sucesso!")


if __name__ == "__main__":
    main()

