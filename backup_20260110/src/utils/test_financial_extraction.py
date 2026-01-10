#!/usr/bin/env python3
"""
Script de teste para extração de dados financeiros de um único PDF.
"""
import sys
import os
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, EXTRACTED_PDFS_DFP, FINANCIAL_EXTRACTIONS_PATH
from utils.extract_financial_data_optimized import extract_financial_data_from_pdf, validate_extracted_data
from utils.config import ensure_dirs
import json


def main():
    """Testa extração em um único PDF."""
    # Tenta carregar de .env se disponível
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv não instalado, usa variável de ambiente
    
    # Verifica API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY não configurada!")
        print("\nPor favor, configure a API key:")
        print("  - Crie arquivo .env na raiz do projeto com: OPENAI_API_KEY=sua_chave")
        print("  - Ou export OPENAI_API_KEY='sua_chave_aqui'")
        return
    
    print("✅ API Key configurada")
    
    # Carrega mapeamento
    mapping_file = CONSOLIDATED_PATH / "empresa_pdf_mapping.csv"
    if not mapping_file.exists():
        print(f"❌ Arquivo de mapeamento não encontrado: {mapping_file}")
        print("Execute primeiro: python src/utils/map_companies_to_pdfs.py")
        return
    
    df_mapping = pd.read_csv(mapping_file)
    df_ok = df_mapping[df_mapping['Match_Status'] == 'OK']
    
    if len(df_ok) == 0:
        print("❌ Nenhuma empresa com PDF mapeado encontrada")
        return
    
    # Seleciona primeira empresa com match OK (ou ALPHAVILLE se existir)
    if 'ALPHAVILLE' in df_ok['Empresa'].values:
        row = df_ok[df_ok['Empresa'].str.contains('ALPHAVILLE', case=False, na=False)].iloc[0]
    else:
        row = df_ok.iloc[0]
    
    empresa = row['Empresa']
    pdf_path = Path(row['PDF_Path'])
    
    print("\n" + "="*70)
    print(f"📄 TESTE DE EXTRAÇÃO - PDF ÚNICO")
    print("="*70)
    print(f"Empresa: {empresa}")
    print(f"PDF: {pdf_path.name}")
    print(f"Score Match: {row['Score_Match']:.1f}%")
    print("="*70)
    
    if not pdf_path.exists():
        print(f"❌ PDF não encontrado: {pdf_path}")
        return
    
    # Extrai dados
    print(f"\n🔄 Extraindo dados financeiros...")
    print("   (Isso pode levar alguns segundos...)\n")
    
    try:
        data, confidence, observations = extract_financial_data_from_pdf(pdf_path)
        
        print(f"\n✅ Extração concluída!")
        print(f"   Confiança: {confidence:.1%}")
        
        if observations:
            print(f"\n⚠️  Observações:")
            for obs in observations:
                print(f"   - {obs}")
        
        # Mostra dados extraídos
        print(f"\n📊 Dados Extraídos:")
        print("="*70)
        
        # Organiza por categoria
        balanco_fields = [
            "Ativo_Total", "Passivo_Total", "Patrimonio_Liquido",
            "Divida_Total", "Divida_Curto_Prazo", "Divida_Longo_Prazo",
            "Caixa_Equivalentes", "Ativo_Circulante", "Passivo_Circulante",
            "Ativo_Nao_Circulante", "Passivo_Nao_Circulante"
        ]
        
        dre_fields = [
            "Receita_Liquida", "Lucro_Bruto", "EBITDA",
            "Lucro_Operacional", "Lucro_Liquido",
            "Despesas_Financeiras", "Receitas_Financeiras"
        ]
        
        print("\n📋 BALANÇO PATRIMONIAL:")
        for field in balanco_fields:
            value = data.get(field)
            if value is not None:
                print(f"   {field:30s}: {value:>15,.0f}")
            else:
                print(f"   {field:30s}: {'N/A':>15s}")
        
        print("\n📋 DEMONSTRAÇÃO DO RESULTADO (DRE):")
        for field in dre_fields:
            value = data.get(field)
            if value is not None:
                print(f"   {field:30s}: {value:>15,.0f}")
            else:
                print(f"   {field:30s}: {'N/A':>15s}")
        
        print(f"\n📅 Data de Referência: {data.get('Data_Referencia', 'N/A')}")
        
        # Validação
        print(f"\n🔍 Validação:")
        is_valid, errors = validate_extracted_data(data)
        if is_valid:
            print("   ✅ Dados validados com sucesso")
        else:
            print("   ⚠️  Erros encontrados:")
            for error in errors:
                print(f"      - {error}")
        
        # Salva resultado em JSON para inspeção
        ensure_dirs()
        output_file = FINANCIAL_EXTRACTIONS_PATH / "test_extraction_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'empresa': empresa,
                'pdf': pdf_path.name,
                'confidence': confidence,
                'observations': observations,
                'data': data,
                'validation': {
                    'is_valid': is_valid,
                    'errors': errors
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultado completo salvo em: {output_file}")
        print("\n" + "="*70)
        print("✅ TESTE CONCLUÍDO")
        print("="*70)
        print("\nSe os dados estão corretos, você pode executar o pipeline completo.")
        print("Se houver problemas, ajuste o prompt ou a lógica de extração.")
        
    except Exception as e:
        print(f"\n❌ Erro durante extração:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

