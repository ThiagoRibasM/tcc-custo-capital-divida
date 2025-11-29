#!/usr/bin/env python3
"""
Script de monitoramento do pipeline de extração de dados financeiros.
"""
import time
from pathlib import Path
import json
from datetime import datetime
import subprocess
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, FINANCIAL_EXTRACTIONS_PATH


def monitor_extraction():
    """Monitora o progresso da extração."""
    print("="*70)
    print("MONITORAMENTO DO PIPELINE DE EXTRAÇÃO")
    print("="*70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verifica se processo está rodando
    try:
        result = subprocess.run(
            ["pgrep", "-f", "extract_financial_data_pipeline"],
            capture_output=True,
            text=True
        )
        is_running = len(result.stdout.strip()) > 0
    except:
        is_running = False
    
    print(f"🔄 Status do Processo: {'✅ Rodando' if is_running else '⏹️  Parado'}")
    print()
    
    # Conta JSONs criados
    json_files = list(FINANCIAL_EXTRACTIONS_PATH.glob("*.json"))
    json_count = len(json_files)
    
    print(f"📁 Arquivos Gerados:")
    print(f"   JSONs individuais: {json_count} / 100 ({json_count}%)")
    
    # Verifica CSV consolidado
    csv_file = CONSOLIDATED_PATH / "dados_financeiros_brutos.csv"
    if csv_file.exists():
        import pandas as pd
        df = pd.read_csv(csv_file)
        print(f"   CSV consolidado: ✅ {len(df)} empresas")
    else:
        print(f"   CSV consolidado: ⏳ Ainda não criado")
    
    print()
    
    # Últimos arquivos criados
    if json_files:
        json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        print(f"📄 Últimos 5 JSONs Criados:")
        for json_file in json_files[:5]:
            mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
            print(f"   {json_file.name} - {mtime.strftime('%H:%M:%S')}")
        print()
        
        # Analisa último JSON
        latest_json = json_files[0]
        try:
            with open(latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📋 Último Processado:")
            print(f"   Empresa: {data.get('empresa', 'N/A')}")
            print(f"   Confiança: {data.get('confidence', 0):.1%}")
            print(f"   Validação: {'✅ OK' if data.get('validation', {}).get('is_valid', False) else '⚠️ Erros'}")
            
            financial_data = data.get('data', {})
            if financial_data.get('Ativo_Total'):
                print(f"   Ativo Total: R$ {financial_data['Ativo_Total']:,.0f} mil")
            if financial_data.get('Receita_Liquida'):
                print(f"   Receita Líquida: R$ {financial_data['Receita_Liquida']:,.0f} mil")
        except Exception as e:
            print(f"   Erro ao ler JSON: {e}")
        print()
    
    # Estatísticas de qualidade
    if json_files:
        valid_count = 0
        total_confidence = 0
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('validation', {}).get('is_valid', False):
                    valid_count += 1
                total_confidence += data.get('confidence', 0)
            except:
                pass
        
        avg_confidence = total_confidence / json_count if json_count > 0 else 0
        print(f"📊 Estatísticas de Qualidade:")
        print(f"   Validações OK: {valid_count} / {json_count} ({valid_count/json_count*100:.1f}%)")
        print(f"   Confiança média: {avg_confidence:.1%}")
        print()
    
    # Verifica erros
    errors_file = FINANCIAL_EXTRACTIONS_PATH / "extraction_errors.csv"
    if errors_file.exists():
        import pandas as pd
        df_errors = pd.read_csv(errors_file)
        print(f"⚠️  Erros Registrados: {len(df_errors)}")
        if len(df_errors) > 0:
            print("   Últimos erros:")
            for _, row in df_errors.tail(3).iterrows():
                print(f"      - {row['empresa']}: {row['erro'][:50]}...")
        print()
    
    # Tempo estimado
    if json_count > 0:
        remaining = 100 - json_count
        # Estimativa: ~2 segundos por empresa (1s delay + 1s processamento)
        estimated_seconds = remaining * 2
        estimated_min = estimated_seconds // 60
        estimated_sec = estimated_seconds % 60
        
        print(f"⏱️  Tempo Estimado:")
        print(f"   Restantes: {remaining} empresas")
        print(f"   Tempo estimado: ~{estimated_min}m {estimated_sec}s")
        print()
    
    print("="*70)
    
    if json_count >= 100:
        print("✅ EXTRAÇÃO CONCLUÍDA!")
    elif is_running:
        print(f"🔄 Processando... ({json_count}/100)")
    else:
        print("⏹️  Processo não está rodando")
    print("="*70)


if __name__ == "__main__":
    monitor_extraction()

