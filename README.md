# TCC - Análise de Custo de Capital de Dívida (Kd)

**MBA em Finanças - Trabalho de Conclusão de Curso**  
**Tema:** Determinantes do Custo de Capital de Dívida em Empresas do Novo Mercado (B3)

---

## 📊 Bases de Dados

### Dados Prontos para Modelagem

| Arquivo | Descrição | Registros |
|---------|-----------|-----------|
| `kd_ponderado_por_empresa.csv` | **Variável Y** - Kd ponderado por empresa | 129 empresas |
| `indicadores_financeiros_completos.csv` | **Variáveis X** - 34 indicadores financeiros | 100 empresas |
| `dados_financeiros_brutos.csv` | Dados de balanço e DRE | 100 empresas |
| `financiamentos_consolidados.csv` | Detalhes dos financiamentos | 937 registros |
| `empresas_novo_mercado.csv` | Lista de empresas do Novo Mercado | 141 empresas |

### Localização
```
data/processed/consolidated/
```

---

## 📚 Bibliografia

- `docs/references.md` - 25 referências no formato ABNT
- `docs/article_summaries.md` - Resumos dos artigos processados

---

## 🛠️ Estrutura do Projeto

```
TCC/
├── data/
│   └── processed/consolidated/   # Bases de dados
├── docs/                          # Bibliografia
├── src/utils/                     # Scripts Python core
├── notebooks/                     # (Vazio - para novos notebooks)
├── reports/                       # (Vazio - para novos relatórios)
└── models/                        # (Vazio - para modelos)
```

---

## 🚀 Próximos Passos

1. **EDA** - Análise exploratória das variáveis
2. **Feature Engineering** - Seleção de variáveis
3. **Modelagem** - Regressão para Kd
4. **Validação** - Testes de hipóteses
