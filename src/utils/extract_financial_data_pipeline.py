#!/usr/bin/env python3
"""
Pipeline completo para extração de dados financeiros de todos os PDFs.
"""
import pandas as pd
from pathlib import Path
import sys
import os
import json
from datetime import datetime
from tqdm import tqdm
import time

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, FINANCIAL_EXTRACTIONS_PATH, ensure_dirs
from utils.extract_financial_data_optimized import (
    extract_financial_data_from_pdf,
    validate_extracted_data
)

# Tenta carregar .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def process_all_companies(
    mapping_csv: Path,
    output_csv: Path,
    results_dir: Path,
    max_retries: int = 3,
    delay_between_requests: float = 1.0
) -> pd.DataFrame:
    """
    Processa todas as empresas do mapeamento.
    
    Args:
        mapping_csv: Caminho para CSV de mapeamento empresa-PDF
        output_csv: Caminho para salvar CSV consolidado
        results_dir: Diretório para salvar resultados individuais
        max_retries: Número máximo de tentativas por PDF
        delay_between_requests: Delay entre requisições (segundos)
        
    Returns:
        DataFrame com todos os dados extraídos
    """
    # Verifica API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada. Configure em .env ou variável de ambiente")
    
    # Carrega mapeamento
    print("📊 Carregando mapeamento empresa-PDF...")
    df_mapping = pd.read_csv(mapping_csv)
    
    # Verifica se é mapeamento robusto ou antigo
    if 'Match_Status' in df_mapping.columns:
        df_ok = df_mapping[df_mapping['Match_Status'] == 'OK'].copy()
    else:
        # Mapeamento antigo não tem Match_Status, usa todas
        df_ok = df_mapping.copy()
    
    print(f"   ✅ {len(df_ok)} empresas com PDFs mapeados")
    
    # Cria diretório de resultados
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Lista para armazenar resultados
    all_results = []
    errors = []
    
    # Processa cada empresa
    print(f"\n🔄 Processando {len(df_ok)} empresas...")
    print(f"   Delay entre requisições: {delay_between_requests}s")
    print("="*70)
    
    for idx, row in tqdm(df_ok.iterrows(), total=len(df_ok), desc="Extraindo dados"):
        empresa = row['Empresa']
        pdf_path = Path(row['PDF_Path'])
        
        if not pdf_path.exists():
            errors.append({
                'empresa': empresa,
                'pdf': pdf_path.name,
                'erro': 'PDF não encontrado',
                'tentativa': 0
            })
            continue
        
        # Tenta extrair com retry
        success = False
        for attempt in range(1, max_retries + 1):
            try:
                # Delay entre requisições
                if idx > 0:
                    time.sleep(delay_between_requests)
                
                # Extrai dados
                data, confidence, observations = extract_financial_data_from_pdf(pdf_path)
                
                # Valida dados
                is_valid, validation_errors = validate_extracted_data(data)
                
                # Prepara resultado
                result = {
                    'Empresa': empresa,
                    'PDF_Nome': pdf_path.name,
                    'Confianca_Extracao': confidence,
                    'Data_Extracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Validacao_OK': is_valid,
                    'Observacoes': '; '.join(observations + validation_errors) if (observations or validation_errors) else None,
                }
                
                # Adiciona dados financeiros
                result.update(data)
                
                # Salva resultado individual em JSON
                result_json = {
                    'empresa': empresa,
                    'pdf': pdf_path.name,
                    'confidence': confidence,
                    'observations': observations,
                    'data': data,
                    'validation': {
                        'is_valid': is_valid,
                        'errors': validation_errors
                    },
                    'extraction_date': result['Data_Extracao']
                }
                
                json_file = results_dir / f"{empresa.replace('/', '_').replace(' ', '_')}_extraction.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result_json, f, indent=2, ensure_ascii=False)
                
                all_results.append(result)
                success = True
                break
                
            except Exception as e:
                if attempt < max_retries:
                    wait_time = delay_between_requests * attempt
                    print(f"\n   ⚠️  Erro na tentativa {attempt}/{max_retries} para {empresa}: {str(e)}")
                    print(f"      Aguardando {wait_time}s antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    errors.append({
                        'empresa': empresa,
                        'pdf': pdf_path.name,
                        'erro': str(e),
                        'tentativa': attempt
                    })
                    print(f"\n   ❌ Falha após {max_retries} tentativas para {empresa}")
    
    # Cria DataFrame consolidado
    if all_results:
        df_results = pd.DataFrame(all_results)
        
        # Reordena colunas (Empresa primeiro, depois dados financeiros)
        financial_cols = [
            'Ativo_Total', 'Passivo_Total', 'Patrimonio_Liquido',
            'Divida_Total', 'Divida_Curto_Prazo', 'Divida_Longo_Prazo',
            'Caixa_Equivalentes', 'Ativo_Circulante', 'Passivo_Circulante',
            'Ativo_Nao_Circulante', 'Passivo_Nao_Circulante',
            'Receita_Liquida', 'Lucro_Bruto', 'EBITDA',
            'Lucro_Operacional', 'Lucro_Liquido',
            'Despesas_Financeiras', 'Receitas_Financeiras',
            'Data_Referencia'
        ]
        
        other_cols = ['PDF_Nome', 'Confianca_Extracao', 'Data_Extracao', 
                     'Validacao_OK', 'Observacoes']
        
        # Garante que todas as colunas existam
        for col in financial_cols + other_cols:
            if col not in df_results.columns:
                df_results[col] = None
        
        # Reordena
        ordered_cols = ['Empresa'] + financial_cols + other_cols
        ordered_cols = [col for col in ordered_cols if col in df_results.columns]
        df_results = df_results[ordered_cols]
        
        # Salva CSV
        df_results.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"\n💾 Dados consolidados salvos em: {output_csv}")
    else:
        df_results = pd.DataFrame()
        print("\n⚠️  Nenhum resultado para salvar")
    
    # Salva log de erros
    if errors:
        df_errors = pd.DataFrame(errors)
        errors_csv = results_dir / "extraction_errors.csv"
        df_errors.to_csv(errors_csv, index=False, encoding='utf-8')
        print(f"⚠️  {len(errors)} erros registrados em: {errors_csv}")
    
    # Estatísticas
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS DA EXTRAÇÃO")
    print("="*70)
    print(f"✅ Sucessos: {len(all_results)} ({len(all_results)/len(df_ok)*100:.1f}%)")
    print(f"❌ Erros: {len(errors)} ({len(errors)/len(df_ok)*100:.1f}%)")
    
    if all_results:
        avg_confidence = sum(r['Confianca_Extracao'] for r in all_results) / len(all_results)
        valid_count = sum(1 for r in all_results if r.get('Validacao_OK', False))
        print(f"📈 Confiança média: {avg_confidence:.1%}")
        print(f"✅ Validações OK: {valid_count} ({valid_count/len(all_results)*100:.1f}%)")
    
    print("="*70)
    
    return df_results


def main():
    """Função principal."""
    ensure_dirs()
    
    # Usa mapeamento robusto se disponível, senão usa o antigo
    mapping_csv_robust = CONSOLIDATED_PATH / "empresa_pdf_mapping_robust.csv"
    mapping_csv_old = CONSOLIDATED_PATH / "empresa_pdf_mapping.csv"
    
    if mapping_csv_robust.exists():
        mapping_csv = mapping_csv_robust
        print("✅ Usando mapeamento robusto (100% match garantido)")
    elif mapping_csv_old.exists():
        mapping_csv = mapping_csv_old
        print("⚠️  Usando mapeamento antigo (pode não ter 100% match)")
    else:
        print(f"❌ Arquivo de mapeamento não encontrado")
        print("Execute primeiro: python src/utils/map_companies_to_pdfs_robust.py")
        return
    
    output_csv = CONSOLIDATED_PATH / "dados_financeiros_brutos.csv"
    results_dir = FINANCIAL_EXTRACTIONS_PATH
    
    print("="*70)
    print("PIPELINE DE EXTRAÇÃO DE DADOS FINANCEIROS")
    print("="*70)
    print(f"📄 Mapeamento: {mapping_csv}")
    print(f"💾 Saída CSV: {output_csv}")
    print(f"📁 Resultados individuais: {results_dir}")
    print("="*70)
    
    df_results = process_all_companies(
        mapping_csv,
        output_csv,
        results_dir,
        max_retries=3,
        delay_between_requests=1.0  # 1 segundo entre requisições para evitar rate limit
    )
    
    print("\n✅ Pipeline concluído!")
    print(f"\n📊 Total de empresas processadas: {len(df_results)}")
    print(f"💾 Arquivo consolidado: {output_csv}")


if __name__ == "__main__":
    main()

