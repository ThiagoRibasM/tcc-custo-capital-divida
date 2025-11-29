# TCC - Análise de Custo de Capital de Dívida (Kd)

Trabalho de Conclusão de Curso (TCC) do MBA em Finanças focado na análise de custo de capital de dívida e restrições financeiras de empresas listadas na B3, com foco no Novo Mercado.

## Estrutura do Projeto

```
TCC/
├── data/                    # Dados (não versionados)
│   ├── raw/                 # Dados brutos (PDFs, ZIPs)
│   ├── processed/           # Dados processados (CSVs, Excel)
│   └── external/            # Dados externos (referências)
│
├── notebooks/               # Jupyter Notebooks
│   ├── 01_data_collection/ # Coleta de dados
│   ├── 02_data_extraction/ # Extração com IA
│   └── 03_analysis/         # Análises (futuro)
│
├── src/                     # Código Python reutilizável
│   ├── data_collection/    # Módulos de coleta
│   ├── data_extraction/     # Módulos de extração
│   └── utils/               # Utilitários e configurações
│
├── models/                  # Modelos treinados (futuro)
├── reports/                 # Relatórios (futuro)
└── docs/                    # Documentação
```

## Objetivo

Extrair e analisar informações de financiamentos e empréstimos de empresas listadas na B3, especialmente do Novo Mercado, utilizando técnicas de processamento de linguagem natural (LLM) para extrair dados estruturados das demonstrações financeiras.

## Metodologia

1. **Coleta de Dados**: Download automatizado de ITRs trimestrais e DFPs anuais da CVM
2. **Extração com IA**: Uso de GPT-4 para extrair informações estruturadas de financiamentos dos PDFs
3. **Análise**: Cálculo de métricas de custo de dívida (Kd bruto e líquido)

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd TCC
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure a API Key da OpenAI:
   ```bash
   export OPENAI_API_KEY="sua_chave_aqui"
   ```
   Ou crie um arquivo `.env` na raiz do projeto (não versionado):
   ```
   OPENAI_API_KEY=sua_chave_aqui
   ```
   **Importante**: A API key não deve ser commitada no repositório. Use variáveis de ambiente.

## Uso

### Coleta de Dados

1. **Download de ITRs**: Execute `notebooks/01_data_collection/01_download_itr.ipynb`
2. **Download de DFPs**: Execute `notebooks/01_data_collection/02_download_dfp_cvm.ipynb`
3. **Extração de PDFs**: Execute `notebooks/01_data_collection/03_extract_pdfs_from_zips.ipynb`

### Extração com IA

1. **Extração de ITRs**: Execute `notebooks/02_data_extraction/01_extract_itr_llm.ipynb`
2. **Extração de DFPs**: Execute `notebooks/02_data_extraction/02_extract_dfp_kd.ipynb`

## Dados

- **Dados brutos**: PDFs das demonstrações financeiras (não versionados)
- **Dados processados**: CSVs e Excel com dados extraídos (não versionados)
- **Arquivo principal**: `data/processed/consolidated/emp_e_fin_novo_mercado_YYYYMMDD.xlsx`

## Configuração de Paths

Todos os paths estão centralizados em `src/utils/config.py`. Os notebooks importam essas configurações automaticamente.

## Contribuindo

Este é um projeto acadêmico. Para sugestões ou melhorias, abra uma issue.

## Licença

Este projeto é parte de um trabalho acadêmico e está sujeito às políticas da instituição de ensino.

