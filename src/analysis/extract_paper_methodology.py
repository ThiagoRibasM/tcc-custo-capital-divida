#!/usr/bin/env python3
"""
Extrator de Metodologias de Papers Acadêmicos via LLM (OpenAI)

Este script extrai informações metodológicas estruturadas de papers em PDF:
- Modelo estatístico utilizado
- Especificação (Efeitos Fixos, Pooled, etc)
- Variáveis dependentes e independentes
- Tamanho da amostra e período
- Performance (R², F-stat)
- Testes diagnósticos

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

# Dependências externas
try:
    import pdfplumber
    from openai import OpenAI
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Dependência ausente: {e}")
    print("   Instale com: pip install pdfplumber openai python-dotenv")
    sys.exit(1)

# Carregar variáveis de ambiente (forçar override)
load_dotenv(override=True)

# Configuração
PAPERS_DIR = Path(__file__).parent.parent.parent / "data" / "external" / "references"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports"
OUTPUT_JSON = OUTPUT_DIR / "paper_methodologies.json"
OUTPUT_MD = OUTPUT_DIR / "comparacao_metodologias.md"

# Schema de extração
EXTRACTION_SCHEMA = """
{
  "titulo": "string",
  "autores": ["string"],
  "ano": int,
  "pais_estudo": "string",
  
  "metodologia": {
    "tipo_estudo": "empírico | teórico | revisão",
    "modelo_estatistico": "OLS | Painel (EF) | Painel (EA) | GMM | Quantile | Logit | Probit | 2SLS | outro",
    "erros_robustos": "sim (especificar) | não | não informado"
  },
  
  "amostra": {
    "n_empresas": int ou null,
    "n_observacoes": int ou null,
    "periodo": "string (ex: 2010-2019)",
    "tipo_empresa": "abertas | fechadas | ambas | não informado"
  },
  
  "variaveis": {
    "dependente": {
      "nome": "string",
      "proxy": "string (como foi medida)"
    },
    "independentes_principais": [
      {"nome": "string", "coeficiente": float ou null, "significancia": "1% | 5% | 10% | n.s. | não informado"}
    ],
    "controles": ["string"]
  },
  
  "performance": {
    "r_squared": float ou null,
    "r_squared_adj": float ou null,
    "f_stat": float ou null,
    "outros_indicadores": "string"
  },
  
  "testes_diagnosticos": ["string (ex: Breusch-Pagan, VIF, Hausman)"],
  
  "principais_achados": ["string"],
  
  "limitacoes_mencionadas": ["string"]
}
"""

# Prompt especializado para extração
EXTRACTION_PROMPT = """Você é um especialista em econometria e finanças corporativas. Sua tarefa é extrair informações metodológicas estruturadas do artigo acadêmico abaixo.

IMPORTANTE:
1. Extraia APENAS informações que estão explícitas no texto
2. Use null quando a informação não estiver disponível
3. Para coeficientes, extraia o valor numérico quando disponível
4. Para significância, use: "1%", "5%", "10%", "n.s." ou "não informado"
5. Seja preciso com os nomes das variáveis e testes

SCHEMA DE SAÍDA (JSON):
{schema}

TEXTO DO ARTIGO:
{text}

Retorne APENAS o JSON válido, sem explicações adicionais.
"""


def extract_text_from_pdf(pdf_path: Path, max_pages: int = 30) -> str:
    """Extrai texto de um PDF (primeiras N páginas)."""
    text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[:max_pages]):
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
    except Exception as e:
        print(f"   ⚠️ Erro ao ler PDF: {e}")
        return ""
    
    return "\n\n".join(text)


def parse_with_llm(text: str, client: OpenAI, model: str = "gpt-4o-mini") -> Optional[Dict]:
    """Envia texto para o LLM e retorna JSON estruturado."""
    
    # Truncar texto se muito longo (limite de tokens)
    max_chars = 80000  # ~20k tokens
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[TEXTO TRUNCADO]"
    
    prompt = EXTRACTION_PROMPT.format(schema=EXTRACTION_SCHEMA, text=text)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um especialista em econometria. Retorne apenas JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        
        # Limpar markdown se houver
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        return json.loads(content.strip())
        
    except json.JSONDecodeError as e:
        print(f"   ⚠️ Erro ao parsear JSON: {e}")
        return None
    except Exception as e:
        print(f"   ⚠️ Erro na chamada LLM: {e}")
        return None


def generate_comparison_table(methodologies: List[Dict]) -> str:
    """Gera tabela comparativa em Markdown."""
    
    md = """# Comparação de Metodologias - Papers de Referência

> Gerado automaticamente via LLM em {date}

---

## Resumo Geral

| Paper | Modelo | Amostra | R² | Variável Dependente |
|-------|--------|---------|----|--------------------|
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    for m in methodologies:
        titulo = m.get('titulo', 'N/A')[:40] + "..." if len(m.get('titulo', '')) > 40 else m.get('titulo', 'N/A')
        modelo = m.get('metodologia', {}).get('modelo_estatistico', 'N/A')
        
        amostra_info = m.get('amostra', {})
        n_emp = amostra_info.get('n_empresas', 'N/A')
        periodo = amostra_info.get('periodo', 'N/A')
        amostra = f"{n_emp} ({periodo})"
        
        r2 = m.get('performance', {}).get('r_squared')
        r2_str = f"{r2:.2%}" if r2 else "N/A"
        
        dep = m.get('variaveis', {}).get('dependente', {}).get('nome', 'N/A')
        
        md += f"| {titulo} | {modelo} | {amostra} | {r2_str} | {dep} |\n"
    
    md += """
---

## Detalhes por Paper

"""
    
    for i, m in enumerate(methodologies, 1):
        md += f"""### {i}. {m.get('titulo', 'N/A')}

**Autores:** {', '.join(m.get('autores', ['N/A']))}  
**Ano:** {m.get('ano', 'N/A')}  
**País:** {m.get('pais_estudo', 'N/A')}

#### Metodologia
- **Modelo:** {m.get('metodologia', {}).get('modelo_estatistico', 'N/A')}
- **Erros Robustos:** {m.get('metodologia', {}).get('erros_robustos', 'N/A')}

#### Variáveis
- **Dependente:** {m.get('variaveis', {}).get('dependente', {}).get('nome', 'N/A')} ({m.get('variaveis', {}).get('dependente', {}).get('proxy', 'N/A')})
- **Independentes Principais:**
"""
        for var in m.get('variaveis', {}).get('independentes_principais', []):
            coef = var.get('coeficiente', 'N/A')
            sig = var.get('significancia', 'N/A')
            md += f"  - {var.get('nome', 'N/A')}: coef={coef}, sig={sig}\n"
        
        md += f"""
#### Performance
- **R²:** {m.get('performance', {}).get('r_squared', 'N/A')}
- **R² Ajustado:** {m.get('performance', {}).get('r_squared_adj', 'N/A')}

#### Principais Achados
"""
        for achado in m.get('principais_achados', ['N/A']):
            md += f"- {achado}\n"
        
        md += "\n---\n\n"
    
    return md


def main():
    print("="*60)
    print("EXTRAÇÃO DE METODOLOGIAS DE PAPERS VIA LLM")
    print("="*60)
    
    # Verificar API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY não configurada.")
        print("   Configure em .env ou variável de ambiente.")
        return
    
    client = OpenAI(api_key=api_key)
    print(f"✓ OpenAI API configurada")
    
    # Listar papers
    if not PAPERS_DIR.exists():
        print(f"❌ Diretório de papers não encontrado: {PAPERS_DIR}")
        return
    
    pdf_files = list(PAPERS_DIR.glob("*.pdf"))
    print(f"✓ Encontrados {len(pdf_files)} papers para processar")
    
    # Processar cada paper
    methodologies = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processando: {pdf_path.name[:50]}...")
        
        # Extrair texto
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print("   ⚠️ Texto vazio, pulando...")
            continue
        print(f"   → {len(text)} caracteres extraídos")
        
        # Enviar para LLM
        result = parse_with_llm(text, client)
        if result:
            result['_source_file'] = pdf_path.name
            methodologies.append(result)
            print(f"   ✓ Metodologia extraída: {result.get('metodologia', {}).get('modelo_estatistico', 'N/A')}")
        else:
            print("   ⚠️ Falha na extração")
    
    # Salvar resultados
    print(f"\n--- Salvando Resultados ---")
    
    # JSON
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(methodologies, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON salvo em: {OUTPUT_JSON}")
    
    # Markdown
    md_content = generate_comparison_table(methodologies)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✓ Markdown salvo em: {OUTPUT_MD}")
    
    print("\n" + "="*60)
    print(f"CONCLUÍDO: {len(methodologies)}/{len(pdf_files)} papers processados")
    print("="*60)


if __name__ == "__main__":
    main()
