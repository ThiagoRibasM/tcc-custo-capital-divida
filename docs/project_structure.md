# Estrutura do Projeto

Este documento descreve a organização do projeto TCC.

## Diretórios Principais

### `data/`
Contém todos os dados do projeto. **Não é versionado no Git.**

- `data/raw/`: Dados brutos (PDFs, ZIPs)
  - `dfp_2024/`: Demonstrações Financeiras Padronizadas (anuais) de 2024
  - `itr_2024/`: Informações Trimestrais (ITRs) de 2024
- `data/processed/`: Dados processados
  - `llm_extractions/`: CSVs extraídos pela IA por empresa
  - `consolidated/`: Arquivos Excel/CSV consolidados
- `data/external/`: Dados externos
  - `references/`: PDFs de referências acadêmicas

### `notebooks/`
Jupyter Notebooks organizados por etapa do projeto.

- `01_data_collection/`: Coleta de dados
  - `01_download_itr.ipynb`: Download de ITRs trimestrais
  - `02_download_dfp_cvm.ipynb`: Download de DFPs da CVM
  - `03_extract_pdfs_from_zips.ipynb`: Extração de PDFs dos ZIPs
  - `04_extract_b3_companies.ipynb`: Extração de lista de empresas da B3
  - `05_filter_novo_mercado.ipynb`: Filtro de empresas do Novo Mercado
- `02_data_extraction/`: Extração com IA
  - `01_extract_itr_llm.ipynb`: Extração de dados de ITRs usando LLM
  - `02_extract_dfp_kd.ipynb`: Extração de Kd das DFPs
- `03_analysis/`: Análises e modelagem (futuro)

### `src/`
Código Python reutilizável organizado em módulos.

- `data_collection/`: Módulos para coleta de dados
- `data_extraction/`: Módulos para extração de dados
- `utils/`: Utilitários e configurações
  - `config.py`: Configurações centralizadas de paths

### `models/`
Modelos treinados (futuro - para análises preditivas)

### `reports/`
Relatórios e visualizações (futuro)

### `docs/`
Documentação do projeto

## Arquivos de Configuração

- `.gitignore`: Define quais arquivos não devem ser versionados
- `requirements.txt`: Dependências Python do projeto
- `README.md`: Documentação principal

## Convenções

- **Paths**: Todos os paths devem usar `src/utils/config.py`
- **Notebooks**: Organizados por etapa, numerados sequencialmente
- **Dados**: Nunca versionados, apenas código e documentação

