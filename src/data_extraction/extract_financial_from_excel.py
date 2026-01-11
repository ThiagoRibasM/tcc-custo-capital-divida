#!/usr/bin/env python3
"""
Extração de Indicadores Financeiros via Excel (DadosDocumento.xlsx)

Este script extrai dados das DFPs (Demonstrações Financeiras Padronizadas)
diretamente dos arquivos Excel contidos nos ZIPs da CVM, para as 127 empresas
do estudo de Kd.

Abas extraídas (Individual):
- DF Ind Ativo (Balanço Patrimonial - Ativo)
- DF Ind Passivo (Balanço Patrimonial - Passivo e PL)
- DF Ind Resultado Periodo (DRE)
- DF Ind Fluxo de Caixa (DFC)

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import pandas as pd
import zipfile
import os
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES
# -----------------------------------------------------------------------------
ZIP_DIR = Path("data/raw/dfp_2024")
OUTPUT_FILE = CONSOLIDATED_PATH / "dados_financeiros_excel_bruto.csv"

# Abas a extrair: (nome_cons, nome_ind, prefixo)
# Prioridade: Consolidado, fallback para Individual se zerado
SHEETS_TO_EXTRACT = [
    ("DF Cons Ativo", "DF Ind Ativo", "AT"),
    ("DF Cons Passivo", "DF Ind Passivo", "PS"),
    ("DF Cons Resultado Periodo", "DF Ind Resultado Periodo", "DRE"),
    ("DF Cons Fluxo de Caixa", "DF Ind Fluxo de Caixa", "FC"),
]

# Coluna de valor a usar
VALUE_COLUMN = "Valor Ultimo Exercicio"


# -----------------------------------------------------------------------------
# FUNÇÕES
# -----------------------------------------------------------------------------
def find_zip_for_cod_cvm(cod_cvm: str, zip_dir: Path) -> Path | None:
    """Encontra o ZIP correspondente a um código CVM."""
    cod_clean = cod_cvm.replace("-", "")
    
    # Listar ZIPs que começam com o código
    matching = [f for f in os.listdir(zip_dir) 
                if f.startswith(cod_clean) and f.endswith(".zip")]
    
    if matching:
        # Pegar o mais recente (maior número de versão)
        matching.sort(reverse=True)
        return zip_dir / matching[0]
    
    return None


def extract_sheet_data(xlsx_path: str, sheet_name: str, prefix: str) -> tuple[dict, bool]:
    """Extrai dados de uma aba do Excel e retorna como dicionário.
    
    Returns:
        tuple: (dados, is_zerado) - dados extraídos e flag se todos são zero
    """
    try:
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
        
        # Verificar se colunas existem
        if "Codigo Conta" not in df.columns or VALUE_COLUMN not in df.columns:
            return {}, True
        
        # Criar dicionário: prefixo_codigo -> valor
        result = {}
        total_sum = 0
        
        for _, row in df.iterrows():
            codigo = str(row["Codigo Conta"]).strip()
            valor = row[VALUE_COLUMN]
            
            # Limpar código (remover espaços)
            codigo_clean = codigo.replace(" ", "")
            
            # Nome da coluna: PREFIXO_CODIGO
            col_name = f"{prefix}_{codigo_clean}"
            result[col_name] = valor
            
            # Somar para verificar se zerado
            if pd.notna(valor):
                try:
                    total_sum += abs(float(str(valor).replace('.', '').replace(',', '.')))
                except:
                    pass
        
        is_zerado = total_sum == 0
        return result, is_zerado
    
    except Exception as e:
        return {}, True


def extract_empresa(cod_cvm: str, empresa: str, zip_dir: Path) -> dict | None:
    """Extrai todos os dados financeiros de uma empresa."""
    
    # Encontrar ZIP
    zip_path = find_zip_for_cod_cvm(cod_cvm, zip_dir)
    if not zip_path:
        print(f"  ⚠️ ZIP não encontrado para {cod_cvm}")
        return None
    
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            # Encontrar Excel
            xlsx_list = [f for f in z.namelist() if "DadosDocumento" in f]
            if not xlsx_list:
                print(f"  ⚠️ Excel não encontrado em {zip_path.name}")
                return None
            
            # Extrair para temp
            xlsx_name = xlsx_list[0]
            z.extract(xlsx_name, "/tmp/")
            xlsx_path = f"/tmp/{xlsx_name}"
            
            # Iniciar registro
            record = {
                "Cod_CVM": cod_cvm,
                "Empresa": empresa,
            }
            
            # Extrair cada aba (Cons com fallback para Ind)
            for sheet_cons, sheet_ind, prefix in SHEETS_TO_EXTRACT:
                # Tentar consolidado primeiro
                sheet_data, is_zerado = extract_sheet_data(xlsx_path, sheet_cons, prefix)
                
                # Se consolidado zerado, usar individual
                if is_zerado:
                    sheet_data, _ = extract_sheet_data(xlsx_path, sheet_ind, prefix)
                
                record.update(sheet_data)
            
            # Limpar temp
            os.remove(xlsx_path)
            
            return record
    
    except Exception as e:
        print(f"  ❌ Erro ao processar {cod_cvm}: {e}")
        return None


def main():
    print("=" * 70)
    print("EXTRAÇÃO DE INDICADORES FINANCEIROS VIA EXCEL")
    print("=" * 70)
    
    # Carregar lista de empresas
    print("\n1. Carregando lista de empresas...")
    kd = pd.read_csv(CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv")
    print(f"   → {len(kd)} empresas a processar")
    
    # Processar cada empresa
    print("\n2. Extraindo dados dos Excel...")
    records = []
    success = 0
    errors = 0
    
    for idx, row in kd.iterrows():
        cod_cvm = row["Cod_CVM"]
        empresa = row["Empresa"]
        
        print(f"  [{idx+1:3}/{len(kd)}] {empresa[:40]}...", end=" ")
        
        record = extract_empresa(cod_cvm, empresa, ZIP_DIR)
        
        if record:
            records.append(record)
            success += 1
            print("✓")
        else:
            errors += 1
            print("✗")
    
    print(f"\n   Sucesso: {success}/{len(kd)}")
    print(f"   Erros: {errors}/{len(kd)}")
    
    # Consolidar em DataFrame
    print("\n3. Consolidando dados...")
    df_result = pd.DataFrame(records)
    
    # Ordenar colunas
    fixed_cols = ["Cod_CVM", "Empresa"]
    other_cols = sorted([c for c in df_result.columns if c not in fixed_cols])
    df_result = df_result[fixed_cols + other_cols]
    
    print(f"   → {len(df_result)} empresas")
    print(f"   → {len(df_result.columns)} colunas")
    
    # Salvar
    print("\n4. Salvando CSV...")
    df_result.to_csv(OUTPUT_FILE, index=False)
    print(f"   → {OUTPUT_FILE}")
    
    # Resumo de colunas por prefixo
    print("\n5. Resumo de colunas extraídas:")
    for _, _, prefix in SHEETS_TO_EXTRACT:
        cols = [c for c in df_result.columns if c.startswith(f"{prefix}_")]
        print(f"   {prefix}: {len(cols)} colunas")
    
    print("\n" + "=" * 70)
    print("✓ EXTRAÇÃO CONCLUÍDA!")
    print("=" * 70)


if __name__ == "__main__":
    main()
