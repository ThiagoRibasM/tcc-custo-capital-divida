# Estrutura de Arquivos Extraídos dos ZIPs

## Resumo da Extração

- **Total de ZIPs processados:** 688
- **ZIPs com erro:** 0
- **Total de arquivos extraídos:** 1.379 arquivos

## Tipos de Arquivo Encontrados

Os ZIPs contêm três tipos principais de arquivos:

1. **PDFs** (`.pdf`): Demonstrações Financeiras Padronizadas em formato PDF
2. **Planilhas** (`.xlsx`): Planilhas Excel com dados estruturados
3. **XMLs** (`.xml`): Demonstrações Financeiras em formato XML estruturado (padrão CVM)

## Estrutura de Organização

### PDFs
**Localização:** `data/raw/extracted_pdfs/dfp/`

- **Total extraído:** 688 arquivos
- **Descrição:** PDFs das DFPs já estavam parcialmente extraídos, então muitos foram ignorados (já existiam)
- **Uso:** Extração de dados com LLM para cálculo de Kd

### Planilhas
**Localização:** `data/raw/spreadsheets/dfp/`

- **Total extraído:** 1 arquivo (`DadosDocumento.xlsx`)
- **Total ignorado:** 687 arquivos (já existiam)
- **Descrição:** Planilhas Excel com dados estruturados das demonstrações financeiras
- **Uso:** Potencial fonte de dados estruturados para variáveis independentes

### XMLs
**Localização:** `data/raw/dfp_2024/extracted_other/`

- **Total extraído:** 690 arquivos
- **Total ignorado:** 1.374 arquivos (já existiam)
- **Descrição:** Demonstrações Financeiras em formato XML estruturado (padrão CVM/XBRL)
- **Estrutura:** Cada XML contém:
  - Dados da empresa (Código CVM, Razão Social, CNPJ)
  - Tipo de documento (DFP = 4)
  - Demonstrações financeiras estruturadas
- **Uso:** Fonte rica de dados estruturados para extração de variáveis independentes (balanços, DREs, etc.)

## Exemplo de Estrutura XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<XmlDemonstracoesFinanceiras>
  <DadosEmpresa>
    <CodigoCvm>011312</CodigoCvm>
    <RazaoSocialEmpresa>OI S.A. - EM RECUPERAÇÃO JUDICIAL</RazaoSocialEmpresa>
    <CnpjEmpresa>76535764000143</CnpjEmpresa>
    <TipoEmpresa>1</TipoEmpresa>
  </DadosEmpresa>
  <Documento>
    <TipoDocumento>4</TipoDocumento>
    <!-- Demonstrações financeiras estruturadas -->
  </Documento>
</XmlDemonstracoesFinanceiras>
```

## Próximos Passos

1. **Análise dos XMLs:** Os XMLs contêm dados estruturados que podem ser facilmente parseados para extrair:
   - Balanços Patrimoniais
   - Demonstrações de Resultado (DREs)
   - Demonstrações de Fluxo de Caixa
   - Notas Explicativas

2. **Extração de Variáveis Independentes:** Usar os XMLs para extrair métricas financeiras como:
   - Endividamento
   - Liquidez
   - Rentabilidade
   - Tamanho da empresa
   - Outras variáveis relevantes para o modelo

3. **Processamento de Planilhas:** Analisar a planilha `DadosDocumento.xlsx` para entender sua estrutura e conteúdo.

## Scripts Relacionados

- `src/utils/extract_all_from_zips.py`: Script principal de extração
- `src/utils/config.py`: Configuração de paths (inclui `SPREADSHEETS_DFP` e `XMLS_DFP`)

## Notas

- A extração evita duplicação verificando se o arquivo já existe antes de extrair
- Os XMLs são particularmente valiosos por conterem dados estruturados que facilitam a extração automatizada
- A maioria dos arquivos já estava extraída (por isso muitos foram ignorados), mas a extração completa garante que temos todos os dados disponíveis

