# Documentação dos Indicadores Financeiros

**Data de Criação:** 2025-01-XX  
**Arquivo de Dados:** `data/processed/consolidated/indicadores_financeiros_completos.csv`  
**Total de Indicadores:** 34 (8 removidos por data leakage)

---

## Visão Geral

Este documento descreve todos os indicadores financeiros calculados a partir dos dados consolidados das empresas do Novo Mercado. Os indicadores foram desenvolvidos com base na literatura acadêmica revisada, especialmente:

- **Eça & Albanez (2022)**: Heterogeneidade da estrutura de dívida
- **Fazzari et al. (1988)**: Restrições financeiras e sensibilidade investimento-fluxo de caixa
- **Kaplan & Zingales (1997)**: Índice KZ de restrições financeiras
- **Kaloudis & Tsolis (2023)**: Relação entre alavancagem e lucratividade

---

## 1. Indicadores de Estrutura de Capital e Alavancagem

### 1.1 Divida_Total_Ativo
**Fórmula:** `Divida_Total / Ativo_Total`  
**Descrição:** Mede a proporção do ativo total financiada por dívida.  
**Interpretação:** 
- Valores altos (>0.5) indicam alta dependência de capital de terceiros
- Valores baixos (<0.3) indicam estrutura mais conservadora

### 1.2 Divida_Total_Patrimonio
**Fórmula:** `Divida_Total / Patrimonio_Liquido`  
**Descrição:** Também conhecido como D/E ratio (Debt-to-Equity). Mede a relação entre dívida e patrimônio líquido.  
**Interpretação:**
- Valores > 1 indicam mais dívida que patrimônio
- Valores < 1 indicam estrutura mais conservadora

### 1.3 Alavancagem_Total
**Fórmula:** `Divida_Total / (Divida_Total + Patrimonio_Liquido)`  
**Descrição:** Proporção da estrutura de capital representada por dívida.  
**Interpretação:**
- Valores entre 0 e 1
- Valores próximos de 1 = alta alavancagem

### 1.4 Divida_Liquida_Ativo
**Fórmula:** `(Divida_Total - Caixa_Equivalentes) / Ativo_Total`  
**Descrição:** Dívida líquida (descontando caixa) sobre ativo total.  
**Interpretação:**
- Considera a capacidade de pagamento imediato
- Valores negativos indicam caixa superior à dívida

### 1.5 Proporcao_Divida_CP
**Fórmula:** `Divida_Curto_Prazo / Divida_Total`  
**Descrição:** Proporção da dívida total com vencimento em até 12 meses.  
**Interpretação:**
- Valores altos indicam maior pressão de curto prazo
- Valores baixos indicam estrutura de dívida mais longa

### 1.6 Proporcao_Divida_LP
**Fórmula:** `Divida_Longo_Prazo / Divida_Total`  
**Descrição:** Proporção da dívida total com vencimento após 12 meses.  
**Interpretação:**
- Complemento de Proporcao_Divida_CP
- Valores altos indicam estrutura de dívida mais estável

---

## 2. Indicadores de Heterogeneidade da Dívida

Baseados em **Eça & Albanez (2022)**.

### 2.1 IHH_Indexador
**Fórmula:** `Σ(proporção_indexador_i)²`  
**Descrição:** Índice de Herfindahl-Hirschman calculado sobre a distribuição de indexadores (CDI, IPCA, TLP, etc.).  
**Interpretação:**
- Valores próximos de 1 = baixa heterogeneidade (concentrado em poucos indexadores)
- Valores próximos de 0 = alta heterogeneidade (diversificado)
- Segundo Eça & Albanez (2022), maior heterogeneidade está associada a menor custo de capital

### 2.2 IHH_Tipo_Financiamento
**Fórmula:** `Σ(proporção_tipo_i)²`  
**Descrição:** Índice de Herfindahl-Hirschman calculado sobre os tipos de financiamento (Capital de Giro, Financiamento, Debêntures, etc.).  
**Interpretação:**
- Similar ao IHH_Indexador, mas focado na diversidade de tipos
- Valores altos = concentração em poucos tipos

### 2.3 Indice_Diversificacao
**Fórmula:** `1 - IHH_Indexador`  
**Descrição:** Mede o grau de diversificação dos indexadores.  
**Interpretação:**
- Valores altos = maior diversificação
- Valores baixos = maior concentração

### 2.4 Heterogeneidade_Combinada
**Fórmula:** `(1 - IHH_Indexador) × (1 - IHH_Tipo_Financiamento)`  
**Descrição:** Mede heterogeneidade considerando tanto indexadores quanto tipos de financiamento.  
**Interpretação:**
- Medida abrangente de diversificação da estrutura de dívida
- Valores altos = estrutura muito diversificada

---

## 3. Indicadores de Liquidez

### 3.1 Liquidez_Corrente
**Fórmula:** `Ativo_Circulante / Passivo_Circulante`  
**Descrição:** Capacidade de pagar obrigações de curto prazo com recursos de curto prazo.  
**Interpretação:**
- Valores > 1 = capacidade de pagar obrigações
- Valores < 1 = possível dificuldade de pagamento
- Ideal: entre 1.5 e 2.0

### 3.2 Liquidez_Seca
**Fórmula:** `Ativo_Circulante / Passivo_Circulante` (proxy, sem estoques)  
**Descrição:** Liquidez sem considerar estoques (não disponível nos dados, usando proxy).  
**Interpretação:**
- Similar à liquidez corrente, mas mais conservadora
- Remove ativos menos líquidos

### 3.3 Liquidez_Imediata
**Fórmula:** `Caixa_Equivalentes / Passivo_Circulante`  
**Descrição:** Capacidade de pagar obrigações apenas com caixa disponível.  
**Interpretação:**
- Medida mais conservadora de liquidez
- Valores altos indicam boa reserva de caixa

### 3.4 Cobertura_Caixa_Divida
**Fórmula:** `Caixa_Equivalentes / Divida_Total`  
**Descrição:** Proporção da dívida total coberta por caixa.  
**Interpretação:**
- Valores > 1 = caixa suficiente para quitar toda a dívida
- Valores baixos = dependência de geração de caixa futura

---

## 4. Indicadores de Rentabilidade

### 4.1 ROA (Return on Assets)
**Fórmula:** `Lucro_Liquido / Ativo_Total`  
**Descrição:** Rentabilidade sobre os ativos totais.  
**Interpretação:**
- Mede eficiência no uso dos ativos
- Valores positivos e crescentes são desejáveis
- Comparar com Kd para avaliar criação de valor

### 4.2 ROA_Operacional
**Fórmula:** `Lucro_Operacional / Ativo_Total`  
**Descrição:** Rentabilidade operacional sobre ativos.  
**Interpretação:**
- Foca no resultado operacional (antes de juros e impostos)
- Remove efeitos financeiros e tributários

### 4.3 ROA_EBITDA
**Fórmula:** `EBITDA / Ativo_Total`  
**Descrição:** EBITDA sobre ativos totais.  
**Interpretação:**
- Mede geração de caixa operacional
- Não considera depreciação e amortização

### 4.4 ROE (Return on Equity)
**Fórmula:** `Lucro_Liquido / Patrimonio_Liquido`  
**Descrição:** Rentabilidade sobre o patrimônio líquido.  
**Interpretação:**
- Mede retorno para acionistas
- Valores altos indicam boa rentabilidade do capital próprio

### 4.5 Margem_Bruta
**Fórmula:** `Lucro_Bruto / Receita_Liquida`  
**Descrição:** Margem bruta de lucro.  
**Interpretação:**
- Mede eficiência na produção/venda
- Valores altos indicam boa capacidade de precificação

### 4.6 Margem_Operacional
**Fórmula:** `Lucro_Operacional / Receita_Liquida`  
**Descrição:** Margem operacional.  
**Interpretação:**
- Mede eficiência operacional
- Considera despesas operacionais

### 4.7 Margem_Liquida
**Fórmula:** `Lucro_Liquido / Receita_Liquida`  
**Descrição:** Margem líquida de lucro.  
**Interpretação:**
- Mede lucratividade final
- Considera todos os custos e despesas

### 4.8 Margem_EBITDA
**Fórmula:** `EBITDA / Receita_Liquida`  
**Descrição:** Margem de EBITDA.  
**Interpretação:**
- Mede geração de caixa operacional sobre receita
- Útil para comparar empresas com diferentes estruturas de capital

---

> [!WARNING]
> **Seção Removida: Indicadores Relacionados ao Custo da Dívida (Kd)**
>
> Os seguintes indicadores foram removidos por causarem **data leakage** na modelagem
> (usam Kd no cálculo, que é a variável dependente):
> - Spread_Medio, Coeficiente_Variacao_Kd, Range_Kd, Range_Kd_Relativo, Diferenca_Kd_Ponderado_Simples

## 5. Indicadores de Restrições Financeiras

Baseados em **Kaplan & Zingales (1997)** e **Fazzari et al. (1988)**.

### 5.1 KZ_Index
**Fórmula:** Versão simplificada do índice Kaplan-Zingales  
`-1.002 × (CF/Ativo) + 3.139 × (Divida/Ativo) - 1.315 × (Caixa/Ativo)`  
**Descrição:** Índice de restrições financeiras (versão simplificada, sem Q e Dividendos).  
**Interpretação:**
- Valores altos = maior restrição financeira
- Empresas com restrições tendem a ter menor investimento e crescimento

### 5.2 Restricao_Financeira_Simplificada
**Fórmula:** Score combinado (0-1) baseado em:
- Baixa liquidez (33%)
- Alta alavancagem (33%)
- Baixa rentabilidade (34%)  
**Descrição:** Score de restrição financeira simplificado.  
**Interpretação:**
- Valores próximos de 1 = alta restrição financeira
- Valores próximos de 0 = baixa restrição financeira

### 5.3 FCF_Operacional
**Fórmula:** `EBITDA - Despesas_Financeiras` (aproximado)  
**Descrição:** Fluxo de caixa livre operacional aproximado.  
**Interpretação:**
- Mede capacidade de geração de caixa após despesas financeiras
- Valores positivos = geração de caixa

### 5.4 FCF_Ativo
**Fórmula:** `FCF_Operacional / Ativo_Total`  
**Descrição:** Fluxo de caixa livre sobre ativos.  
**Interpretação:**
- Mede eficiência na geração de caixa
- Útil para avaliar capacidade de investimento

---

## 6. Indicadores de Composição e Estrutura

### 6.1 Concentracao_Financiamentos
**Fórmula:** `1 / Total_Financiamentos`  
**Descrição:** Mede concentração dos financiamentos.  
**Interpretação:**
- Valores altos = poucos financiamentos (mais concentrado)
- Valores baixos = muitos financiamentos (mais diversificado)

### 6.2 Diversidade_Indexadores
**Fórmula:** `Indexadores_Unicos / Total_Financiamentos`  
**Descrição:** Proporção de indexadores únicos.  
**Interpretação:**
- Valores próximos de 1 = cada financiamento usa indexador diferente
- Valores baixos = poucos indexadores únicos

### 6.3 Diversidade_Tipos
**Fórmula:** `Tipos_Financiamento_Unicos / Total_Financiamentos`  
**Descrição:** Proporção de tipos de financiamento únicos.  
**Interpretação:**
- Similar à diversidade de indexadores
- Mede variedade de instrumentos financeiros

### 6.4 Prazo_Medio_Divida
**Fórmula:** Média ponderada dos vencimentos (em dias)  
**Descrição:** Prazo médio até o vencimento dos financiamentos.  
**Interpretação:**
- Valores altos = estrutura de dívida de longo prazo
- Valores baixos = maior pressão de curto prazo

---

## 7. Indicadores de Cobertura e Capacidade de Pagamento

### 7.1 Cobertura_Juros
**Fórmula:** `EBITDA / Despesas_Financeiras`  
**Descrição:** Capacidade de pagar juros com EBITDA.  
**Interpretação:**
- Valores > 1 = capacidade de pagar juros
- Valores < 1 = dificuldade de pagar juros
- Ideal: > 2.0

### 7.2 Cobertura_Divida_EBITDA
**Fórmula:** `Divida_Total / EBITDA`  
**Descrição:** Anos necessários para pagar dívida com EBITDA.  
**Interpretação:**
- Valores baixos (< 5) = estrutura de dívida saudável
- Valores altos (> 10) = possível sobre-endividamento

### 7.3 Cobertura_Divida_Liquida_EBITDA
**Fórmula:** `(Divida_Total - Caixa_Equivalentes) / EBITDA`  
**Descrição:** Anos para pagar dívida líquida com EBITDA.  
**Interpretação:**
- Similar à cobertura de dívida, mas considera caixa disponível
- Mais conservador que Cobertura_Divida_EBITDA

---

> [!WARNING]
> **Seção Removida: Indicadores Comparativos e Relativos**
>
> Os seguintes indicadores foram removidos por causarem **data leakage** na modelagem:
> - Spread_ROA_Kd, Kd_Alavancagem_Ratio, Eficiencia_Endividamento

---

## 8. Variáveis Adicionais

### 8.1 Kd_Ponderado
**Fórmula:** `Σ(Kd_i × Valor_i) / Σ(Valor_i)`  
**Descrição:** Custo médio ponderado da dívida por valor.  
**Interpretação:**
- Variável principal do estudo
- Mede custo efetivo da dívida considerando o tamanho de cada financiamento

---

## Notas Técnicas

### Tratamento de Valores Especiais

- **Divisão por zero:** Retorna `NaN` quando o denominador é zero ou negativo
- **Valores negativos:** Patrimônio Líquido negativo é tratado como inválido para cálculos de ROE e D/E
- **Valores missing:** Mantidos como `NaN` para preservar informação

### Limitações

1. **Liquidez Seca:** Não temos dados de estoques, usando Ativo_Circulante como proxy
2. **KZ Index:** Versão simplificada sem Tobin's Q e dividendos (dados não disponíveis)
3. **FCF Operacional:** Aproximação sem considerar impostos e variações de capital de giro
4. **Prazo Médio:** Depende da qualidade dos dados de vencimento

### Validação

Todos os indicadores foram calculados com validação de:
- Divisão por zero
- Valores negativos em denominadores críticos
- Valores nulos/missing
- Consistência entre indicadores relacionados

---

## Referências Bibliográficas

1. **Eça, J. P. A., & Albanez, T. (2022).** A heterogeneidade da estrutura de dívida reduz o custo de capital? *Revista Contabilidade & Finanças*.

2. **Fazzari, S. M., Hubbard, R. G., & Petersen, B. C. (1988).** Financing Constraints and Corporate Investment. *Brookings Papers on Economic Activity*.

3. **Kaplan, S. N., & Zingales, L. (1997).** Do Investment-Cash Flow Sensitivities Provide Useful Measures of Financing Constraints? *The Quarterly Journal of Economics*.

4. **Kaloudis, A., & Tsolis, D. (2023).** Capital Structure in U.S., A Quantile Regression Approach with Macroeconomic Impacts. *Journal of Financial Research*.

---

## Próximos Passos

1. Análise descritiva dos indicadores
2. Análise de correlações entre indicadores e Kd
3. Análise de clusters (empresas similares)
4. Modelos de regressão (Kd vs indicadores)
5. Validação de hipóteses dos artigos acadêmicos

