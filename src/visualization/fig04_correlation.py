#!/usr/bin/env python3
"""
Figura 4: Matriz de Correlação de Pearson da Features do Modelo

Este script gera uma figura formal para o TCC contendo um heatmap
de correlação entre as features explicativas, excluindo a variável resposta (Kd).

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH, FIGURES_DIR
from src.visualization import styles
styles.apply_style()

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE ESTILO
# -----------------------------------------------------------------------------
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10,
    'axes.labelsize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
})

COLORS = {
    'primary': styles.COLORS['secondary'], # Azul escuro
    'text': '#1a1a1a',
}

# -----------------------------------------------------------------------------
# DEFINIÇÃO DAS FEATURES POR CATEGORIA
# -----------------------------------------------------------------------------
# Ordem lógica para o heatmap
# -----------------------------------------------------------------------------
# DEFINIÇÃO DAS FEATURES POR CATEGORIA
# -----------------------------------------------------------------------------
# Ordem lógica para o heatmap
FEATURE_ORDER = [
    # ALAVANCAGEM
    'Divida_Total_Ativo',
    'Divida_Total_PL',
    'Alavancagem_Total',
    'Divida_Liquida_Ativo',
    
    # LIQUIDEZ E COBERTURA
    'Liquidez_Corrente',
    'Liquidez_Imediata',
    'Cobertura_Caixa_Divida',
    'Cobertura_Juros',
    'Divida_EBITDA',
    
    # RENTABILIDADE
    'ROA',
    'ROE',
    'Margem_Bruta',
    'Margem_EBITDA',
    'Margem_Liquida',
    
    # ADICIONAIS
    'Tamanho',
    'Tangibilidade',
    'Capital_Giro_Liquido',
    
    # HETEROGENEIDADE E PERFIL
    'Indice_Diversificacao',     # Diversificação Dívida (1-HHI)
    'IHH_Indexador',
    'IHH_Tipo',
    'Proporcao_Divida_CP',
    'Proporcao_Divida_LP',
]

# Mapa de labels para nome mais legível na figura
LABEL_MAP = {
    'Divida_Total_Ativo': 'Dívida / Ativo',
    'Divida_Total_PL': 'Dívida / PL',
    'Alavancagem_Total': 'Alavancagem Total',
    'Divida_Liquida_Ativo': 'Dívida Líq. / Ativo',
    'Liquidez_Corrente': 'Liq. Corrente',
    'Liquidez_Imediata': 'Liq. Imediata',
    'Cobertura_Caixa_Divida': 'Cobertura Caixa',
    'Cobertura_Juros': 'Cob. Juros (ICJ)',
    'Divida_EBITDA': 'Dívida / EBITDA',
    'ROA': 'ROA',
    'ROE': 'ROE',
    'Margem_Bruta': 'Margem Bruta',
    'Margem_EBITDA': 'Margem EBITDA',
    'Margem_Liquida': 'Margem Líquida',
    'Tamanho': 'Tamanho (Log)',
    'Tangibilidade': 'Tangibilidade',
    'Capital_Giro_Liquido': 'Cap. Giro Líq.',
    'Indice_Diversificacao': 'Div. Fontes (1-HHI)',
    'IHH_Indexador': 'HHI Indexador',
    'IHH_Tipo': 'HHI Tipo',
    'Proporcao_Divida_CP': '% Curto Prazo',
    'Proporcao_Divida_LP': '% Longo Prazo',
}

def load_data():
    """Carrega dados e seleciona features."""
    df = pd.read_csv(CONSOLIDATED_PATH / "tabela_features.csv")
    
    # Filtrar apenas as colunas desejadas que existem no DF
    available_cols = [col for col in FEATURE_ORDER if col in df.columns]
    
    # Aviso se faltar alguma
    missing = set(FEATURE_ORDER) - set(available_cols)
    if missing:
        print(f"Aviso: Colunas não encontradas no dataset: {missing}")
        
    return df[available_cols]

def create_correlation_plot(df):
    """Gera o heatmap de correlação."""
    
    # Calcular correlação
    corr = df.corr(method='pearson')
    
    # Renomear colunas/linhas para labels legíveis
    corr = corr.rename(index=LABEL_MAP, columns=LABEL_MAP)
    
    # Máscara para o triângulo superior
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    # Configurar figura
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Paleta divergente
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    
    # Heatmap
    sns.heatmap(
        corr, 
        mask=mask, 
        cmap=cmap, 
        vmax=1.0, 
        vmin=-1.0,
        center=0,
        square=True, 
        linewidths=.5, 
        cbar_kws={"shrink": .8, "label": "Correlação de Pearson (r)"},
        annot=True,          # Mostrar valores
        fmt=".2f",           # 2 casas decimais
        annot_kws={"size": 6}, # Tamanho da fonte dos números
        ax=ax
    )
    
    # Título (removido - usar caption no LaTeX)
    # ax.set_title(
    #     'Figura 4: Matriz de Correlação de Pearson entre Variáveis Explicativas',
    #     fontsize=14, 
    #     fontweight='bold', 
    #     color=COLORS['primary'],
    #     pad=20
    # )
    
    # Ajustes finais
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    return fig

def main():
    print("="*60)
    print("GERANDO FIGURA 4: CORRELAÇÃO")
    print("="*60)
    
    # Carregar
    print("1. Carregando dados...")
    df = load_data()
    print(f"   → {df.shape[1]} features selecionadas")
    
    # Gerar
    print("2. Gerando heatmap...")
    fig = create_correlation_plot(df)
    
    # Salvar
    print("3. Salvando...")
    output_path = FIGURES_DIR / "fig04_correlation.pdf"
    fig.savefig(output_path, bbox_inches='tight', facecolor='white', format='pdf')
    plt.close(fig)
    
    print(f"✓ Figura salva em: {output_path}")
    print("="*60)

if __name__ == "__main__":
    main()
