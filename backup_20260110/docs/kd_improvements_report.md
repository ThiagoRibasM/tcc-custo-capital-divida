# Relatório de Melhorias na Padronização de Indexadores e Validação de Kd

**Data:** 29 de November de 2025

---

## 1. Resumo Executivo

- **Total de registros:** 937
- **Indexadores identificados:** 748 (79.8%)
- **Kd calculado:** 745 (79.5%)
- **Kd válido:** 602 (64.2%)

### Melhoria na Taxa de Identificação
- **Antes:** 79.8% (748/937)
- **Depois:** 79.8% (748/937)
- **Melhoria:** +0.0 pontos percentuais

## 2. Padrões Adicionados

### 2.1 Novos Indexadores Identificados

Os seguintes indexadores foram adicionados à detecção:
- **SOFR**: 22 ocorrências
- **LIBOR**: 4 ocorrências
- **IGPM**: 1 ocorrências
- **IPC**: 1 ocorrências

### 2.2 Melhorias nos Padrões Regex

1. **Detecção de Pré-fixado melhorada**:
   - Captura variações: 'Pré', 'Pré-fixado', 'Pré fixado', 'Fixo', 'Fixa'
   - Detecta percentuais diretos sem palavra-chave (ex: '18,44% a.a.')

2. **Extração de Spread melhorada**:
   - Captura spreads negativos (ex: 'CDI - 0,5%')
   - Trata faixas de percentual (ex: '5,60% a 9,88%') - usa primeiro valor
   - Melhor tratamento de formatos alternativos (vírgula, ponto)

3. **Indexadores Internacionais**:
   - SOFR (Secured Overnight Financing Rate)
   - LIBOR (London Interbank Offered Rate)

## 3. Distribuição de Indexadores


| Indexador | Quantidade | % do Total |
|-----------|-----------|------------|
| CDI | 339 | 36.2% |
| NÃO_IDENTIFICADO | 189 | 20.2% |
| PRE_FIXADO | 126 | 13.4% |
| IPCA | 89 | 9.5% |
| TLP | 69 | 7.4% |
| TR | 45 | 4.8% |
| DI | 41 | 4.4% |
| SOFR | 22 | 2.3% |
| SELIC | 11 | 1.2% |
| LIBOR | 4 | 0.4% |
| IPC | 1 | 0.1% |
| IGPM | 1 | 0.1% |

## 4. Validação de Casos Extremos


- **Kd extremo alto (>30%):** 22 registros
- **Kd extremo baixo (<5%):** 68 registros
- **Requer revisão manual:** 72 registros

### 4.1 Exemplos de Kd Extremo Alto

| Empresa | Indexador | Kd (%) | Observação |
|---------|-----------|--------|------------|
| ALLIANÇA SAÚDE E PARTICIPAÇÕES | CDI | 83.24 | Possível erro na conversão de taxa mensa |
| ALLIANÇA SAÚDE E PARTICIPAÇÕES | CDI | 83.24 | Possível erro na conversão de taxa mensa |
| EMPREENDA MENOS S.A. | CDI | 128.65 | Spread muito alto, verificar se não é er |
| EMPREENDA MENOS S.A. | CDI | 133.65 | Spread muito alto, verificar se não é er |
| LOJAS RENNER S.A. | CDI | 128.75 | Spread muito alto, verificar se não é er |

### 4.2 Exemplos de Kd Extremo Baixo

| Empresa | Indexador | Kd (%) | Observação |
|---------|-----------|--------|------------|
| Brisanet Serviços de Telecomun | PRE_FIXADO | 0.82 | Pré-fixado muito baixo, pode ser taxa in |
| Brisanet Serviços de Telecomun | PRE_FIXADO | 1.18 | Pré-fixado muito baixo, pode ser taxa in |
| Brisanet Serviços de Telecomun | TR | 3.55 | TR tem valor base muito baixo (0,01%), K |
| Brisanet Serviços de Telecomun | PRE_FIXADO | 0.40 | Pré-fixado muito baixo, pode ser taxa in |
| CM Hospitalar S.A. | TR | 3.81 | TR tem valor base muito baixo (0,01%), K |

## 5. Indexadores Não Identificados


Total: 189 registros (20.2%)

### 5.1 Top 20 Indexadores Não Identificados Mais Frequentes

| Indexador Original | Frequência |
|-------------------|------------|
| Não especificado | 4 |
| Pré-fixado | 4 |
| Pré-fixado 0,25% Iene | 3 |
| não especificado | 3 |
| spread de 1,21% a.m. | 2 |
| BRL - TJLP 7,97% | 2 |
| Variação cambial | 2 |
| Variação cambial + juros | 2 |
| Pré-fixado 6,00% a.a. | 2 |
| Pré-fixado+IPCA 9,17% a.a. | 2 |
| Pós-fixado | 2 |
| BRL - CDI 12,15% | 2 |
| - | 2 |
| Pré-fixado 8,21% a.a. | 2 |
| BRL - IPCA 4,83% | 2 |
| Poupança + 4,92% | 1 |
| EURIBOR + Variação cambial 3,02% a.a. | 1 |
| 2,90+EURIBOR | 1 |
| Eur+1,70% / USD+5,83 | 1 |
| Poupança + 3,81% | 1 |

## 6. Recomendações


### 6.1 Melhorias Adicionais Sugeridas

1. **Revisão manual dos indexadores não identificados**:
   - 189 registros ainda não identificados
   - Focar nos mais frequentes para identificar novos padrões

2. **Validação de casos extremos**:
   - Revisar 72 casos que requerem validação manual
   - Verificar se conversões de período estão corretas
   - Validar spreads extremos

3. **Tratamento de casos especiais**:
   - Variação cambial (VC, v.c.)
   - Múltiplos indexadores no mesmo campo
   - Moedas estrangeiras (USD, EUR, Dólar, Euro)

### 6.2 Próximos Passos

1. Revisar manualmente os casos em `kd_manual_review.csv`
2. Expandir padrões regex baseado nos indexadores não identificados mais frequentes
3. Validar valores base dos indexadores internacionais (SOFR, LIBOR)
4. Implementar tratamento para variação cambial

---

*Relatório gerado automaticamente pelo script `generate_improvements_report.py`*