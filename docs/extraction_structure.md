# Estrutura de Arquivos Extraídos dos ZIPs

## Resumo da Extração

- **Total de ZIPs processados:** 688
- **ZIPs com erro:** 0
- **Apenas PDFs são extraídos:** Planilhas e XMLs são ignorados

## Tipo de Arquivo Extraído

### PDFs
**Localização:** `data/raw/extracted_pdfs/dfp/`

- **Descrição:** PDFs das Demonstrações Financeiras Padronizadas (DFPs)
- **Uso:** Extração de dados com LLM para cálculo de Kd e variáveis independentes
- **Nota:** Os PDFs já estavam parcialmente extraídos, então muitos foram ignorados (já existiam)

## Decisão de Projeto

**Apenas PDFs são extraídos dos ZIPs.** Planilhas (Excel/CSV) e XMLs não são extraídos porque:

1. A extração de variáveis independentes será feita diretamente dos PDFs usando LLM
2. Os PDFs contêm todas as informações necessárias para o projeto
3. Isso simplifica a estrutura de dados e reduz a complexidade do pipeline

## Scripts Relacionados

- `src/utils/extract_all_from_zips.py`: Script principal de extração (extrai apenas PDFs)
- `src/utils/config.py`: Configuração de paths (inclui `EXTRACTED_PDFS_DFP`)

## Notas

- A extração evita duplicação verificando se o arquivo já existe antes de extrair
- Os PDFs são a única fonte de dados extraída dos ZIPs
- A maioria dos PDFs já estava extraída (por isso muitos foram ignorados), mas a extração completa garante que temos todos os dados disponíveis
