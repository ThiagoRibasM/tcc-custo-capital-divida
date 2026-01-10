# Documentação de Empresas Excluídas por Outliers

**Data:** 29 de November de 2025

---

## Metodologia de Identificação de Outliers

Foi utilizado o método **IQR (Interquartile Range)** para identificar outliers:

- **Q1 (25%):** 8.11%
- **Q3 (75%):** 15.43%
- **IQR:** 7.32%
- **Limite Inferior:** Q1 - 1.5 × IQR = -2.87%
- **Limite Superior:** Q3 + 1.5 × IQR = 26.41%

**Critério:** Empresas com Kd_Ponderado < -2.87% OU > 26.41% foram consideradas outliers.

## Estatísticas de Exclusão

- **Total de empresas:** 135
- **Empresas excluídas (outliers):** 6 (4.4%)
- **Empresas mantidas:** 129 (95.6%)

## Lista de Empresas Excluídas

| # | Empresa | Kd Ponderado (%) | Valor Consolidado Médio (R$) | Total Financiamentos | Justificativa |
|---|---------|-------------------|-------------------------------|---------------------|---------------|
| 1 | LOJAS RENNER S.A. | 127.20 | 123,038.00 | 5 | Kd muito alto (> 26.41%) |
| 2 | MINERVA S.A. | 62.69 | 665,903.20 | 5 | Kd muito alto (> 26.41%) |
| 3 | EMPREENDA MENOS S.A. | 44.71 | 39,155.43 | 7 | Kd muito alto (> 26.41%) |
| 4 | SEQUOIA LOGÍSTICA E TRANSPORTES S.A. | 41.97 | 253,735.00 | 1 | Kd muito alto (> 26.41%) |
| 5 | ALLIANÇA SAÚDE E PARTICIPAÇÕES S.A. | 27.70 | 721,713.00 | 15 | Kd muito alto (> 26.41%) |
| 6 | BOA SAFRA SEMENTES S.A. | 26.84 | 52,588.75 | 4 | Kd muito alto (> 26.41%) |

### Análise dos Outliers

#### Outliers com Kd Muito Alto (> 26.41%)

**Quantidade:** 6 empresas

| Empresa | Kd (%) | Valor Médio (R$) |
|---------|--------|------------------|
| LOJAS RENNER S.A. | 127.20 | 123,038.00 |
| MINERVA S.A. | 62.69 | 665,903.20 |
| EMPREENDA MENOS S.A. | 44.71 | 39,155.43 |
| SEQUOIA LOGÍSTICA E TRANSPORTES S.A. | 41.97 | 253,735.00 |
| ALLIANÇA SAÚDE E PARTICIPAÇÕES S.A. | 27.70 | 721,713.00 |
| BOA SAFRA SEMENTES S.A. | 26.84 | 52,588.75 |

#### Outliers com Kd Muito Baixo (< -2.87%)

**Quantidade:** 0 empresas


## Comparação: Antes vs Depois da Remoção

### Estatísticas de Kd Ponderado

| Estatística | Antes (com outliers) | Depois (sem outliers) | Diferença |
|------------|---------------------|----------------------|-----------|
| Média | 13.69% | 11.76% | -1.93% (-14.1%) |
| Mediana | 12.20% | 11.68% | -0.52% (-4.2%) |
| Desvio Padrão | 12.36% | 4.50% | -7.87% (-63.6%) |
| Mínimo | 2.82% | 2.82% | +0.00% (+0.0%) |
| Máximo | 127.20% | 25.87% | -101.34% (-79.7%) |

---

*Documento gerado automaticamente pelo script `remove_outliers.py`*