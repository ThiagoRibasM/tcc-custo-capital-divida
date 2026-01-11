# Arquivos Legados - Extração via PDF/LLM

## ⚠️ DEPRECATED

Esta pasta contém arquivos do processo **legado** de extração de indicadores financeiros via PDF e LLM, que foi substituído pela extração direta via Excel (DadosDocumento.xlsx) das DFPs.

## Motivo da Depreciação

O processo via PDF/LLM apresentou os seguintes problemas:
- **85% de NaN** nas métricas relacionadas a EBITDA
- Dependência de interpretação LLM (menos confiável)
- Dados intermediários com erros de parsing

## Nova Abordagem (Produtiva)

A nova abordagem extrai dados diretamente dos arquivos Excel oficiais da CVM:
- Script: `src/data_extraction/extract_financial_from_excel.py`
- Saída: `data/processed/consolidated/dados_financeiros_excel_bruto.csv`
- Taxa de sucesso: **100%**

## Conteúdo desta Pasta

```
_deprecated/
├── data/
│   ├── consolidated/
│   │   └── dados_financeiros_brutos.csv  # CSV antigo com dados LLM
│   ├── financial_extractions/
│   │   └── *.json                        # 100 JSONs de extração LLM
│   └── raw/
│       └── extracted_pdfs/               # PDFs extraídos
└── src/
    └── visualization/
        ├── fig01_llm_pipeline.py         # Figura do pipeline LLM
        └── fig03_feature_mosaic.py       # Mosaico (referenciava LLM)
```

## Data de Depreciação

Janeiro 2026

## Responsável

Pipeline TCC - Custo de Capital da Dívida
