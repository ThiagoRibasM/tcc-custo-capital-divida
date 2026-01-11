# Comparação de Metodologias - Papers de Referência

> Gerado automaticamente via LLM em 2026-01-11 16:19

---

## Resumo Geral

| Paper | Modelo | Amostra | R² | Variável Dependente |
|-------|--------|---------|----|--------------------|
| A heterogeneidade da estrutura de dívida... | Painel (EF) | 570 (2010-2019) | 12.00% | Custo da dívida |
| Financing Constraints and Corporate Inve... | OLS | 422 (1970-1984) | 55.00% | I/K |
| Nível de evidenciação × custo da dívida ... | Painel (EF) | 23 (2000-2005) | 28.49% | custo de capital de terceiros (Kd) |
| Do Measures of Financial Constraints Mea... | OLS | 10112 (1989-2011) | N/A | leverage |
| A new measure of financial constraints a... | Logit | 723 (1989-2012) | N/A | FinCon |
| CAPITAL STRUCTURE IN U.S., A QUANTILE RE... | Quantile | 28793 (1970-2014) | N/A | Debt Ratio |
| A INFLUÊNCIA DO DISCLOSURE VOLUNTÁRIO NO... | OLS | 57 (2010-2012) | 15.42% | custo da dívida (K) |
| Do Investment-Cash Flow Sensitivities Pr... | OLS | 49 (1970-1984) | 20.10% | investment-cash flow sensitivity |

---

## Detalhes por Paper

### 1. A heterogeneidade da estrutura de dívida reduz o custo de capital?

**Autores:** João Paulo Augusto Eça, Tatiana Albanez  
**Ano:** 2022  
**País:** Brasil

#### Metodologia
- **Modelo:** Painel (EF)
- **Erros Robustos:** sim (clusterizados por firma)

#### Variáveis
- **Dependente:** Custo da dívida (Despesa financeira líquida de impostos sobre passivo oneroso médio)
- **Independentes Principais:**
  - Índice Herfindahl-Hirschman: coef=0.023, sig=1%
  - Índice de dependência econômica: coef=0.01, sig=5%

#### Performance
- **R²:** 0.12
- **R² Ajustado:** 0.116

#### Principais Achados
- Maior heterogeneidade da dívida está relacionada a menor custo de capital de terceiros.
- Relação negativa entre heterogeneidade e custo de capital é mais intensa para empresas com altos custos de agência.

---

### 2. Financing Constraints and Corporate Investment

**Autores:** Steven M. Fazzari, R. Glenn Hubbard, Bruce C. Petersen, Alan S. Blinder, James M. Poterba  
**Ano:** 1988  
**País:** Estados Unidos

#### Metodologia
- **Modelo:** OLS
- **Erros Robustos:** não informado

#### Variáveis
- **Dependente:** I/K (investimento em planta e equipamentos dividido pelo estoque de capital no início do período)
- **Independentes Principais:**
  - Q: coef=0.001, sig=não informado
  - CF/K: coef=0.67, sig=não informado

#### Performance
- **R²:** 0.55
- **R² Ajustado:** None

#### Principais Achados
- A sensibilidade do investimento ao fluxo de caixa é maior para empresas que retêm a maior parte de seus lucros.
- As empresas com maior retenção de lucros enfrentam mais restrições financeiras.

---

### 3. Nível de evidenciação × custo da dívida das empresas brasileiras

**Autores:** Gerlando Augusto Sampaio Franco de Lima  
**Ano:** 2009  
**País:** Brasil

#### Metodologia
- **Modelo:** Painel (EF)
- **Erros Robustos:** sim (White)

#### Variáveis
- **Dependente:** custo de capital de terceiros (Kd) (despesa financeira líquida de impostos dividida pela média dos empréstimos)
- **Independentes Principais:**
  - nível de disclosure (ND): coef=-0.054902, sig=1%
  - ADR: coef=-0.021854, sig=1%
  - taxa de endividamento (TXENDIV): coef=-0.000236, sig=1%
  - receita bruta total (RECBRUTA): coef=0.035785, sig=1%
  - valor de mercado (VALORMERCADO): coef=-0.02321, sig=1%
  - patrimônio líquido total (PLTOTAL): coef=-0.031256, sig=1%

#### Performance
- **R²:** 0.284884
- **R² Ajustado:** 0.18657

#### Principais Achados
- A variável dependente custo de capital de terceiros possui uma relação inversa com o nível de disclosure.
- Empresas com maiores níveis de disclosure apresentam um custo de capital de terceiros menor.

---

### 4. Do Measures of Financial Constraints Measure Financial Constraints?

**Autores:** Joan Farre-Mensa, Alexander Ljungqvist  
**Ano:** 2015  
**País:** Estados Unidos

#### Metodologia
- **Modelo:** OLS
- **Erros Robustos:** não informado

#### Variáveis
- **Dependente:** leverage (long-term book leverage)
- **Independentes Principais:**
  - tax increase: coef=None, sig=não informado

#### Performance
- **R²:** None
- **R² Ajustado:** None

#### Principais Achados
- Firms classified as constrained do not behave as if they are constrained.
- Constrained firms increase leverage in response to tax increases.
- Constrained firms recycle equity similarly to unconstrained firms.

---

### 5. A new measure of financial constraints applicable to private and public firms

**Autores:** Catharina Schauer, Ralf Elsas, Nikolas Breitkopf  
**Ano:** 2019  
**País:** Alemanha

#### Metodologia
- **Modelo:** Logit
- **Erros Robustos:** sim (clusterizados a nível de firma)

#### Variáveis
- **Dependente:** FinCon (autoavaliação dos gerentes sobre a situação financeira da empresa)
- **Independentes Principais:**
  - Size: coef=-0.123, sig=1%
  - Interest coverage: coef=-0.024, sig=1%
  - Profitability: coef=-4.404, sig=1%
  - Cash holdings: coef=-1.716, sig=5%

#### Performance
- **R²:** None
- **R² Ajustado:** None

#### Principais Achados
- A nova medida de restrições financeiras (FCP index) é capaz de prever a situação financeira real das empresas.
- Empresas classificadas como financeiramente restritas têm menor rentabilidade e maior dificuldade de acesso a capital.

---

### 6. CAPITAL STRUCTURE IN U.S., A QUANTILE REGRESSION APPROACH WITH MACROECONOMIC IMPACTS

**Autores:** Andreas Kaloudis, Dimitrios Tsolis  
**Ano:** 2023  
**País:** U.S.

#### Metodologia
- **Modelo:** Quantile
- **Erros Robustos:** sim (não especificado)

#### Variáveis
- **Dependente:** Debt Ratio (book value of interest-bearing debt to total assets)
- **Independentes Principais:**
  - Size: coef=None, sig=não informado
  - Asset Structure: coef=None, sig=não informado
  - Growth: coef=None, sig=não informado
  - Profitability: coef=None, sig=não informado
  - Non-Debt Tax Shields: coef=None, sig=não informado
  - Risk: coef=None, sig=não informado
  - Trade Credit: coef=None, sig=não informado
  - Cash: coef=None, sig=não informado
  - Financial Expenses: coef=None, sig=não informado
  - Credit Supply: coef=None, sig=não informado
  - Inflation: coef=None, sig=não informado
  - Interest Rate: coef=None, sig=não informado

#### Performance
- **R²:** None
- **R² Ajustado:** None

#### Principais Achados
- A relação entre alavancagem e lucratividade é negativa.
- A relação entre ativos tangíveis e alavancagem é positiva.
- A velocidade de ajuste da alavancagem de longo prazo desacelera durante crises.

---

### 7. A INFLUÊNCIA DO DISCLOSURE VOLUNTÁRIO NO CUSTO DA DÍVIDA DE FINANCIAMENTOS EM EMPRESAS LISTADAS NA BM&FBOVESPA

**Autores:** Claudio Marcelo Edwards Barros, Sonia Raifur Kos, Silvia Consoni, Romualdo Douglas Colauto  
**Ano:** 2017  
**País:** Brasil

#### Metodologia
- **Modelo:** OLS
- **Erros Robustos:** não informado

#### Variáveis
- **Dependente:** custo da dívida (K) (juros de financiamentos obtidos da Demonstração do Valor Adicionado (DVA))
- **Independentes Principais:**
  - Índice de Divulgação Voluntária (IDV): coef=-1.0693, sig=5%
  - Alavancagem Financeira (ALAV): coef=-0.4938, sig=5%
  - Tamanho (TAM): coef=0.0395, sig=não informado
  - Valor de Mercado (MKV): coef=0.0949, sig=10%

#### Performance
- **R²:** 0.1542
- **R² Ajustado:** 0.1542

#### Principais Achados
- O nível de disclosure voluntário não influencia negativamente a magnitude da taxa de juros de financiamentos.

---

### 8. Do Investment-Cash Flow Sensitivities Provide Useful Measures of Financing Constraints?

**Autores:** Steven N. Kaplan, Luigi Zingales  
**Ano:** 1997  
**País:** não informado

#### Metodologia
- **Modelo:** OLS
- **Erros Robustos:** não informado

#### Variáveis
- **Dependente:** investment-cash flow sensitivity (relação entre investimento e fluxo de caixa)
- **Independentes Principais:**
  - cash flow: coef=0.702, sig=não informado
  - Tobin's Q: coef=0.276, sig=1%
  - debt/total capital: coef=2.071, sig=1%
  - dividends: coef=-23.039, sig=1%
  - dividends restricted: coef=1.496, sig=1%
  - unrestricted retained earnings: coef=-1.897, sig=1%
  - cash: coef=-1.704, sig=1%
  - unused line of credit: coef=-0.711, sig=1%

#### Performance
- **R²:** 0.201
- **R² Ajustado:** 0.223

#### Principais Achados
- Firms classified as less financially constrained exhibit greater investment-cash flow sensitivity.
- 85% of firm-years showed no evidence of financing constraints.
- Investment-cash flow sensitivity does not increase monotonically with financing constraints.

---

