# Modelo Final de Regressão - Determinantes do Custo de Dívida (Kd)

> **Versão:** 1.0  
> **Data:** 2026-01-11  
> **Autor:** Pipeline Automatizado TCC  
> **Status:** FINAL

---

## 1. Resumo Executivo

Este documento registra a especificação final do modelo de regressão OLS para análise dos determinantes do custo de dívida (Kd) de empresas brasileiras listadas.

### Resultado Final
| Métrica | Valor |
|---------|-------|
| **R-Quadrado** | 26.9% |
| **R² Ajustado** | 23.7% |
| **F-Statistic** | 11.76 (p < 0.001) |
| **N Observações** | 119 empresas |
| **N Variáveis** | 5 |

---

## 2. Dados Utilizados

### Fonte de Dados
- **Arquivo:** `data/processed/consolidated/tabela_features.csv`
- **Período:** Exercício 2024 (DFP)
- **Fonte Original:** CVM (Demonstrações Financeiras Padronizadas)

### Pipeline de Dados
```
DFP 2024 (ZIP/XML) → Excel Extraction → Feature Engineering → Regression Pipeline
```

### Amostra
| Etapa | N Empresas | Motivo |
|-------|------------|--------|
| Dataset Original | 126 | - |
| Após KNN Imputation | 126 | Valores faltantes imputados |
| Após Outliers Kd (Z>4) | 126 | Nenhum removido |
| Após Outliers Cook's D | 119 | 7 observações influentes removidas |

---

## 3. Variável Dependente

| Campo | Valor |
|-------|-------|
| **Nome** | Kd_Ponderado |
| **Descrição** | Custo de Capital de Terceiros Ponderado |
| **Proxy** | Taxa média dos financiamentos ponderada pelo valor |
| **Unidade** | % a.a. |
| **Fonte** | Notas Explicativas (Financiamentos) |

---

## 4. Variáveis Independentes (Modelo Final)

| Variável | Coeficiente | Std Error | z-stat | P-valor | Sig. |
|----------|-------------|-----------|--------|---------|------|
| **const** | 23.38 | 3.31 | 7.06 | 0.000 | *** |
| **Alavancagem_Total** | +5.60 | 1.59 | 3.53 | 0.000 | *** |
| **Tamanho** | -0.76 | 0.22 | -3.46 | 0.001 | *** |
| **Tangibilidade** | -2.87 | 1.29 | -2.22 | 0.026 | ** |
| **IHH_Indexador** | -1.85 | 0.87 | -2.13 | 0.033 | ** |
| **Liquidez_Imediata** | -1.44 | 0.95 | -1.51 | 0.130 | |

**Legendas:** *** p<0.01, ** p<0.05, * p<0.10

### Interpretação dos Coeficientes

1. **Alavancagem_Total (+5.60)**: Empresas mais alavancadas pagam taxas ~5.6 p.p. maiores. Consistente com teoria de risco de crédito.

2. **Tamanho (-0.76)**: Cada aumento de 1 unidade no log(Ativo Total) reduz Kd em ~0.76 p.p. Empresas maiores têm melhor acesso a crédito.

3. **Tangibilidade (-2.87)**: Maior proporção de ativos fixos reduz custo. Garantias reais diminuem risco percebido.

4. **IHH_Indexador (-1.85)**: Maior concentração nos indexadores (menos diversificação) reduz custo. Suporta teoria de Relationship Banking.

5. **Liquidez_Imediata (-1.44)**: Marginalmente significativa. Maior liquidez associada a menor custo.

---

## 5. Pré-Processamento

### 5.1 Imputação de Valores Faltantes
- **Método:** KNN Imputer (k=5, weighted by distance)
- **Normalização:** StandardScaler antes da imputação
- **Justificativa:** Preservar amostra, não descartar empresas com dados parcialmente incompletos

### 5.2 Tratamento de Outliers
- **Winsorização:** 1%-99% em todas as features (antes da modelagem)
- **Cook's Distance:** Remoção de observações com D > 4/n (threshold = 0.032)
- **Outliers Removidos:** 7 empresas

### 5.3 Multicolinearidade (VIF)
- **Threshold:** VIF < 5
- **Variáveis Removidas por VIF:**
  - Proporcao_Divida_CP (VIF = inf)
  - Divida_Total_Ativo (VIF = 42)
  - Margem_Liquida (VIF = 14)
  - Divida_Liquida_Ativo (VIF = 6)

### 5.4 Seleção de Variáveis (Stepwise)
- **Método:** Backward Elimination
- **Critério:** p-value > 0.15 para exclusão
- **Variáveis Iniciais:** 19
- **Variáveis Finais:** 5

---

## 6. Diagnósticos do Modelo

### 6.1 Normalidade dos Resíduos
| Teste | Estatística | P-valor | Resultado |
|-------|-------------|---------|-----------|
| Jarque-Bera | 0.035 | 0.983 | ✓ Normal |
| Omnibus | 0.036 | 0.982 | ✓ Normal |
| Skewness | -0.027 | - | Simétrico |
| Kurtosis | 2.936 | - | Mesocúrtico |

### 6.2 Heterocedasticidade
| Teste | P-valor | Resultado |
|-------|---------|-----------|
| Breusch-Pagan | 0.143 | ⚠️ Marginalmente OK |
| White | - | - |

**Ação:** Erros robustos HC3 aplicados por precaução.

### 6.3 Autocorrelação
| Teste | Estatística | Resultado |
|-------|-------------|-----------|
| Durbin-Watson | 0.634 | ⚠️ Baixo (esperado em cross-section) |

### 6.4 Condition Number
- **Valor:** 173
- **Interpretação:** Aceitável (< 1000)

---

## 7. Arquivos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `reports/modelo_final_summary.txt` | Sumário OLS completo |
| `reports/figures/fig05_regression_diagnostics.png` | Diagnósticos visuais (4 painéis) |
| `reports/modelo_final_metadata.md` | Este documento |
| `src/models/regression_pipeline.py` | Script reproduzível |

---

## 8. Reprodutibilidade

Para reproduzir este modelo:

```bash
cd /Users/thiagomoncinhatto/Documents/02_MBA_Financas/TCC
python3 src/models/regression_pipeline.py
```

### Dependências
```
pandas>=1.5.0
numpy>=1.23.0
statsmodels>=0.14.0
scipy>=1.10.0
scikit-learn>=1.2.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## 9. Limitações e Considerações

1. **Cross-Section:** Dados de um único exercício (2024). Não captura efeitos temporais.
2. **Proxy de Kd:** Baseada em dados de Notas Explicativas, não taxas de mercado.
3. **Imputação:** ~24% dos dados foram imputados via KNN.
4. **Setor:** Variável de setor não incluída (melhoria potencial para versões futuras).

---

## 10. Versionamento

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | 2026-01-11 | Modelo final sem variáveis de setor |
| 0.3 | 2026-01-11 | Adição de dummies de setor (R²=49%) - Descartado |
| 0.2 | 2026-01-11 | KNN Imputation + Cook's D (R²=27%) |
| 0.1 | 2026-01-10 | Modelo inicial (R²=16.5%) |

---

*Documento gerado automaticamente pelo Pipeline de Regressão TCC.*
