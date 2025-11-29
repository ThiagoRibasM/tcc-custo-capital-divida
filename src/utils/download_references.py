#!/usr/bin/env python3
"""
Script para baixar PDFs das referências bibliográficas.
Extrai links e DOIs do arquivo references.md e baixa os PDFs disponíveis.
"""
import os
import re
import requests
import time
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import unicodedata

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
REFERENCES_MD = PROJECT_ROOT / "docs" / "references.md"
OUTPUT_DIR = PROJECT_ROOT / "data" / "external" / "references"
LOG_FILE = PROJECT_ROOT / "data" / "external" / "references" / "download_log.txt"

# Criar diretório se não existir
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Headers para requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def normalize_filename(text, max_length=100):
    """Normaliza texto para nome de arquivo."""
    # Remove acentos
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Remove caracteres especiais
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    text = text.strip('_')
    
    # Limita tamanho
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def extract_references_from_markdown(md_file):
    """Extrai informações das referências do arquivo markdown."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    references = []
    # Divide por linhas vazias para pegar referências completas
    blocks = re.split(r'\n\s*\n', content)
    
    for block in blocks:
        block = block.strip()
        if not block or block.startswith('#'):
            continue
        
        ref = {}
        lines = block.split('\n')
        
        # Primeira linha geralmente tem autores
        first_line = lines[0].strip() if lines else ""
        
        # Extrai autores (até o primeiro ponto, formato: SOBRENOME, Nome; SOBRENOME, Nome.)
        author_match = re.match(r'^([A-ZÁÉÍÓÚÇ][^\.]+)\.', first_line)
        if author_match:
            authors = author_match.group(1).strip()
            ref['authors'] = authors
        
        # Procura título (entre o ponto dos autores e **)
        # Procura em todo o bloco primeiro
        full_block_text = ' '.join(lines)
        
        # Padrão melhorado: captura texto entre ponto após autores e **
        # Tenta padrão mais específico: ponto, espaço, texto (que não começa com maiúscula seguida de vírgula), espaço, **
        title_match = re.search(r'\.\s+([A-ZÁÉÍÓÚÇ][^\.]+?)\s+\*\*', full_block_text)
        
        if not title_match:
            # Tenta padrão mais permissivo
            title_match = re.search(r'\.\s+([^\.]+?)\s+\*\*', full_block_text)
        
        if title_match:
            title = title_match.group(1).strip().rstrip('.')
            # Remove possíveis nomes de autores que possam ter ficado no título
            # Se o título começa com padrão de autor (SOBRENOME, Nome), remove
            title = re.sub(r'^[A-ZÁÉÍÓÚÇ][A-ZÁÉÍÓÚÇ\s,;]+\.\s*', '', title)
            # Remove vírgulas e pontos no início
            title = title.lstrip('.,; ')
            # Remove espaços múltiplos
            title = re.sub(r'\s+', ' ', title).strip()
            ref['title'] = title
        
        # Procura por links em todo o bloco
        full_block = ' '.join(lines)
        link_match = re.search(r'<https?://[^>]+>', full_block)
        if link_match:
            url = link_match.group(0).strip('<>')
            ref['url'] = url
        
        # Procura por DOI (formato completo)
        # DOIs podem ter formato: 10.xxxx/yyyy ou 10.xxxx/yyyy.zzz
        # Captura tudo até espaço, vírgula ou fim da linha (mas permite pontos dentro do DOI)
        doi_match = re.search(r'DOI:\s*(10\.[0-9]+/[^\s,]+)', full_block)
        if not doi_match:
            # Tenta sem "DOI:" prefix
            doi_match = re.search(r'\b(10\.[0-9]+/[^\s,]+)', full_block)
        
        if doi_match:
            doi = doi_match.group(1).strip('.')
            # Remove apenas ponto final se existir (mas mantém pontos internos)
            if doi.endswith('.'):
                doi = doi[:-1]
            ref['doi'] = doi
        
        # Extrai ano
        year_match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', full_block)
        if year_match:
            ref['year'] = year_match.group(1)
        
        # Se tem URL ou DOI, adiciona à lista
        if ref.get('url') or ref.get('doi'):
            if not ref.get('authors'):
                ref['authors'] = 'Unknown'
            if not ref.get('year'):
                ref['year'] = 'Unknown'
            if not ref.get('title'):
                ref['title'] = 'Unknown'
            
            references.append(ref)
    
    return references


def download_pdf_from_url(url, output_path, timeout=30):
    """Baixa PDF de uma URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Verifica se é PDF
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' in content_type:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        
        # Se não é PDF direto, tenta encontrar link de PDF na página
        if 'html' in content_type or 'text' in content_type:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Procura por links de PDF
            pdf_links = []
            
            # Procura por links com "pdf" no texto ou href
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().lower()
                
                if 'pdf' in href.lower() or 'pdf' in text or href.endswith('.pdf'):
                    if href.startswith('/'):
                        # URL relativa
                        parsed = urlparse(url)
                        pdf_url = f"{parsed.scheme}://{parsed.netloc}{href}"
                    elif href.startswith('http'):
                        pdf_url = href
                    elif href.startswith('//'):
                        pdf_url = f"{parsed.scheme}:{href}"
                    else:
                        # URL relativa
                        base_url = '/'.join(url.split('/')[:-1])
                        pdf_url = f"{base_url}/{href}"
                    pdf_links.append(pdf_url)
            
            # Para SciELO, tenta padrão comum
            if 'scielo' in url.lower() or 'revistas.usp.br' in url:
                # Tenta adicionar /pdf no final
                if not url.endswith('/pdf'):
                    pdf_url = url + '/pdf'
                    pdf_links.insert(0, pdf_url)
            
            # Tenta baixar o primeiro link de PDF encontrado
            for pdf_url in pdf_links[:3]:  # Tenta até 3 links
                try:
                    if download_pdf_from_url(pdf_url, output_path, timeout):
                        return True
                except:
                    continue
        
        return False
    except Exception as e:
        return False


def download_from_doi(doi, output_path):
    """Baixa PDF usando DOI."""
    try:
        # Resolve DOI para URL
        doi_url = f"https://doi.org/{doi}"
        session = requests.Session()
        session.headers.update(HEADERS)
        response = session.get(doi_url, allow_redirects=True, timeout=30)
        
        # Pega a URL final após redirecionamento
        final_url = response.url
        
        # Para alguns sites, tenta adicionar /pdf
        if 'sciencedirect' in final_url.lower():
            final_url = final_url.replace('/article/', '/article/pii/')
            if not final_url.endswith('/pdf'):
                final_url = final_url + '/pdf'
        elif 'jstor' in final_url.lower():
            final_url = final_url.replace('/stable/', '/stable/pdf/')
        elif 'academic.oup.com' in final_url.lower():
            final_url = final_url.replace('/article/', '/article-pdf/')
        
        # Tenta baixar PDF da URL final
        return download_pdf_from_url(final_url, output_path)
    except Exception as e:
        return False


def download_from_arxiv(arxiv_id, output_path):
    """Baixa PDF do arXiv."""
    try:
        # arXiv IDs podem estar em formato abs/ID ou pdf/ID
        if '/abs/' in arxiv_id:
            arxiv_id = arxiv_id.split('/abs/')[-1]
        elif '/pdf/' in arxiv_id:
            arxiv_id = arxiv_id.split('/pdf/')[-1].replace('.pdf', '')
        
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        return download_pdf_from_url(pdf_url, output_path)
    except Exception as e:
        print(f"  ❌ Erro ao baixar arXiv {arxiv_id}: {e}")
        return False


def generate_filename(ref):
    """Gera nome de arquivo baseado apenas no título da referência."""
    title = ref.get('title', 'Unknown')
    
    # Se o título for "Unknown", tenta usar autores como fallback
    if title == 'Unknown' and ref.get('authors'):
        title = ref.get('authors', 'Unknown')
    
    # Normaliza o título para nome de arquivo
    filename = normalize_filename(title, max_length=150)
    
    # Adiciona extensão
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    return filename


def main():
    """Função principal."""
    print("📚 Iniciando download de PDFs das referências...\n")
    
    # Extrai referências do markdown
    print("📖 Extraindo referências do arquivo markdown...")
    references = extract_references_from_markdown(REFERENCES_MD)
    print(f"✅ {len(references)} referências com links/DOIs encontradas\n")
    
    # Log
    log_entries = []
    log_entries.append(f"Download iniciado em: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_entries.append(f"Total de referências: {len(references)}\n\n")
    
    success_count = 0
    fail_count = 0
    
    for i, ref in enumerate(references, 1):
        authors = ref.get('authors', 'Desconhecido')
        title = ref.get('title', 'Sem título')[:60]
        
        print(f"[{i}/{len(references)}] {authors} - {title}")
        
        filename = generate_filename(ref)
        output_path = OUTPUT_DIR / filename
        
        # Verifica se já existe
        if output_path.exists():
            print(f"  ⏭️  Arquivo já existe: {filename}")
            log_entries.append(f"✅ {filename} - Já existe\n")
            success_count += 1
            continue
        
        success = False
        
        # Tenta baixar por URL direta
        if ref.get('url'):
            url = ref['url']
            print(f"  🔗 Tentando baixar de: {url[:60]}...")
            
            # arXiv
            if 'arxiv.org' in url:
                success = download_from_arxiv(url, output_path)
            else:
                success = download_pdf_from_url(url, output_path)
        
        # Se falhou, tenta por DOI
        if not success and ref.get('doi'):
            doi = ref['doi']
            print(f"  🔍 Tentando baixar via DOI: {doi}")
            success = download_from_doi(doi, output_path)
        
        if success and output_path.exists() and output_path.stat().st_size > 1000:
            print(f"  ✅ Baixado: {filename}")
            log_entries.append(f"✅ {filename} - Baixado com sucesso\n")
            success_count += 1
        else:
            print(f"  ❌ Falha ao baixar")
            log_entries.append(f"❌ {filename} - Falha no download\n")
            fail_count += 1
        
        # Delay para não sobrecarregar servidores
        time.sleep(2)
        print()
    
    # Salva log
    log_entries.append(f"\n{'='*50}\n")
    log_entries.append(f"Download finalizado em: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_entries.append(f"Sucessos: {success_count}\n")
    log_entries.append(f"Falhas: {fail_count}\n")
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.writelines(log_entries)
    
    print(f"\n{'='*50}")
    print(f"✅ Download concluído!")
    print(f"   Sucessos: {success_count}")
    print(f"   Falhas: {fail_count}")
    print(f"   Log salvo em: {LOG_FILE}")


if __name__ == "__main__":
    main()

