"""
Figura de Comparação Científica - Modelo de Kd vs Literatura
==============================================================
Figura composta com três painéis de análise:
  A) Comparação de R² com a literatura
  B) Matriz de variáveis determinantes (quem usa o quê)
  C) Visualização multidimensional (N, R², features)

Estilo: Paper acadêmico de finanças/economia
Autor: TCC Pipeline
Data: 2026-01-11
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd

# Adicionar path do projeto
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.visualization import styles

# Aplicar estilo padrão (Times New Roman, cores, etc)
styles.apply_style()


# =============================================================================
# DADOS DOS MODELOS
# =============================================================================

STUDIES = [
    {
        "id": "TCC",
        "label": "Este Estudo (2026)",
        "short": "Este Estudo",
        "r_squared": 0.269,
        "r_squared_adj": 0.237,
        "country": "Brasil",
        "n": 119,
        "n_vars": 5,
        "method": "OLS HC3",
        "var_dep": "Kd",
        "periodo": "2024",
        "tipo": "tcc",
        # Features usadas (1 = usa, 0 = não usa)
        "features": {
            "Alavancagem": 1,
            "Tamanho": 1,
            "Tangibilidade": 1,
            "Liquidez": 1,
            "Rentabilidade": 0,
            "Crescimento": 0,
            "Disclosure": 0,
            "Heterogeneidade Dívida": 1,
            "Cobertura de Juros": 0,
        }
    },
    {
        "id": "ECA2022",
        "label": "Eça & Albanez (2022)",
        "short": "Eça & Albanez",
        "r_squared": 0.12,
        "r_squared_adj": 0.116,
        "country": "Brasil",
        "n": 570,
        "n_vars": 8,
        "method": "Painel EF",
        "var_dep": "Kd",
        "periodo": "2010-2019",
        "tipo": "benchmark",
        "features": {
            "Alavancagem": 1,
            "Tamanho": 1,
            "Tangibilidade": 1,
            "Liquidez": 0,
            "Rentabilidade": 1,
            "Crescimento": 1,
            "Disclosure": 0,
            "Heterogeneidade Dívida": 1,
            "Cobertura de Juros": 1,
        }
    },
    {
        "id": "LIMA2009",
        "label": "Lima (2009)",
        "short": "Lima",
        "r_squared": 0.2848,
        "r_squared_adj": 0.187,
        "country": "Brasil",
        "n": 23,
        "n_vars": 6,
        "method": "Painel EF",
        "var_dep": "Kd",
        "periodo": "2000-2005",
        "tipo": "benchmark",
        "features": {
            "Alavancagem": 1,
            "Tamanho": 1,
            "Tangibilidade": 0,
            "Liquidez": 0,
            "Rentabilidade": 0,
            "Crescimento": 0,
            "Disclosure": 1,
            "Heterogeneidade Dívida": 0,
            "Cobertura de Juros": 0,
        }
    },
    {
        "id": "BARROS2017",
        "label": "Barros et al. (2017)",
        "short": "Barros et al.",
        "r_squared": 0.1542,
        "r_squared_adj": 0.1542,
        "country": "Brasil",
        "n": 57,
        "n_vars": 4,
        "method": "OLS",
        "var_dep": "Kd",
        "periodo": "2010-2012",
        "tipo": "benchmark",
        "features": {
            "Alavancagem": 1,
            "Tamanho": 1,
            "Tangibilidade": 0,
            "Liquidez": 0,
            "Rentabilidade": 0,
            "Crescimento": 0,
            "Disclosure": 1,
            "Heterogeneidade Dívida": 0,
            "Cobertura de Juros": 0,
        }
    },
    {
        "id": "KAPLAN1997",
        "label": "Kaplan & Zingales (1997)",
        "short": "Kaplan & Zingales",
        "r_squared": 0.201,
        "r_squared_adj": 0.223,
        "country": "EUA",
        "n": 49,
        "n_vars": 8,
        "method": "OLS",
        "var_dep": "Sensib. I-CF",
        "periodo": "1970-1984",
        "tipo": "benchmark",
        "features": {
            "Alavancagem": 1,
            "Tamanho": 0,
            "Tangibilidade": 0,
            "Liquidez": 1,
            "Rentabilidade": 0,
            "Crescimento": 1,
            "Disclosure": 0,
            "Heterogeneidade Dívida": 0,
            "Cobertura de Juros": 1,
        }
    },
]

FEATURE_NAMES = [
    "Alavancagem", "Tamanho", "Tangibilidade", "Liquidez",
    "Rentabilidade", "Crescimento", "Disclosure", 
    "Heterogeneidade Dívida", "Cobertura de Juros"
]

# Cores (Do módulo styles)
COLOR_TCC = styles.COLORS['primary']      # Vermelho (#D64045 ou configurado)
COLOR_BENCH = styles.COLORS['secondary']  # Azul (#1E3A5F ou configurado)
COLOR_GRID = styles.COLORS['light']


def create_comprehensive_figure(output_path=None):
    """
    Cria figura composta com três painéis de análise científica.
    """
    
    # Ordenar estudos por R² para consistência
    studies_sorted = sorted(STUDIES, key=lambda x: x['r_squared'], reverse=True)
    
    # Criar figura com GridSpec
    # Criar figura com GridSpec (Reduzido de 14,10 para 9,8 para manter legibilidade das fontes em A4)
    # Largura A4 texto ~ 6.3 in. Redução será de 9 -> 6.3 (0.7x).
    # Fonte 10pt virará 7pt. Então precisamos de fonte ~13-14 para ter 10pt visual.
    # Fonte 10pt virará 7pt. Então precisamos de fonte ~13-14 para ter 10pt visual.
    # Aumentando altura para 10 para dar espaço aos rótulos rotacionados do Painel B
    # Fonte 10pt virará 7pt. Então precisamos de fonte ~13-14 para ter 10pt visual.
    # Aumentando altura para 10 para dar espaço aos rótulos rotacionados do Painel B
    fig = plt.figure(figsize=(9, 10))
    # wspace reduzido drasticamente (0.05) para conectar visualmente os painéis A e B
    # hspace mantido em 0.6 para proteger o título inferior
    # Invertendo ratios: Heatmap (Esq) precisa de mais largura que Bars (Dir)
    # Reduzindo altura da linha superior (A/B) em 10% (0.9 vs 1.0)
    gs = GridSpec(2, 2, figure=fig, height_ratios=[0.9, 1], 
                  width_ratios=[1.3, 1], hspace=0.6, wspace=0.08)
    
    # Painel A: Feature Matrix (heatmap) - Agora à Esquerda
    ax_a = fig.add_subplot(gs[0, 0])
    
    # Painel B: R² Comparison (bar chart horizontal) - Agora à Direita (sharey com A)
    ax_b = fig.add_subplot(gs[0, 1], sharey=ax_a)
    
    # Painel C: Bubble Chart (N vs R² vs Features)
    ax_c = fig.add_subplot(gs[1, :])
    
    # =========================================================================
    # PAINEL A: Matriz de Features (Heatmap) - AGORA PAINEL A (ESQUERDA)
    # =========================================================================
    # Criar matriz de features
    feature_matrix = []
    study_labels = []
    for study in studies_sorted:
        row = [study['features'].get(f, 0) for f in FEATURE_NAMES]
        feature_matrix.append(row)
        study_labels.append(study['short'])
    
    feature_matrix = np.array(feature_matrix)
    
    # Heatmap customizado
    for i in range(len(studies_sorted)):
        for j in range(len(FEATURE_NAMES)):
            value = feature_matrix[i, j]
            if value == 1:
                color = COLOR_TCC if studies_sorted[i]['tipo'] == 'tcc' else COLOR_BENCH
                ax_a.add_patch(plt.Rectangle((j-0.4, i-0.35), 0.8, 0.7, 
                              facecolor=color, edgecolor='white', linewidth=1.5))
                ax_a.text(j, i, '●', ha='center', va='center', 
                         color='white', fontweight='bold', fontsize=14)
            else:
                ax_a.add_patch(plt.Rectangle((j-0.4, i-0.35), 0.8, 0.7, 
                              facecolor=COLOR_GRID, edgecolor='white', linewidth=1.5))
    
    ax_a.set_xlim(-0.5, len(FEATURE_NAMES)-0.5)
    ax_a.set_ylim(-0.5, len(studies_sorted)-0.5)
    ax_a.set_xticks(range(len(FEATURE_NAMES)))
    ax_a.set_xticklabels(FEATURE_NAMES, rotation=45, ha='right', fontsize=11)
    
    # Labels do Eixo Y no Heatmap (Esquerda)
    ax_a.set_yticks(range(len(study_labels)))
    ax_a.set_yticklabels(study_labels, fontsize=11)
    ax_a.invert_yaxis()
    
    ax_a.set_title('(a) Variáveis Determinantes Utilizadas', fontweight='bold', loc='left', pad=10)
    ax_a.tick_params(axis='both', which='both', length=0)

    # =========================================================================
    # PAINEL B: Comparação de R² - AGORA PAINEL B (DIREITA)
    # =========================================================================
    labels = [s['short'] for s in studies_sorted]
    r2_values = [s['r_squared'] * 100 for s in studies_sorted]
    colors = [COLOR_TCC if s['tipo'] == 'tcc' else COLOR_BENCH for s in studies_sorted]
    
    y_pos = np.arange(len(labels))
    bar_height = 0.55
    
    # R² (barras principais)
    bars = ax_b.barh(y_pos, r2_values, height=bar_height, color=colors, 
                     edgecolor='white', alpha=0.9)
    
    # Remover labels do eixo Y (ShareY cuida disso)
    plt.setp(ax_b.get_yticklabels(), visible=False)
    ax_b.tick_params(axis='y', which='both', length=0)
    
    ax_b.set_xlabel('Coeficiente de Determinação (%)')
    ax_b.set_xlim(0, 35)
    # ax_b.invert_yaxis() # Não precisa inverter, herda de A
    
    # Valores nas barras
    for i, (bar, study) in enumerate(zip(bars, studies_sorted)):
        width = bar.get_width()
        ax_b.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{width:.1f}%', ha='left', va='center',
                 fontweight='bold' if study['tipo'] == 'tcc' else 'normal',
                 fontsize=12, color=colors[i])
    
    ax_b.set_title('(b) Poder Explicativo (R²)', fontweight='bold', loc='left', pad=10)
    # Grid removido conforme solicitação
    ax_b.grid(False)
    
    # =========================================================================
    # PAINEL C: Bubble Chart Multidimensional
    # =========================================================================
    
    # Offsets customizados para cada estudo (para evitar sobreposição)
    label_offsets = {
        "Lima": (12, 10),
        "Este Estudo": (12, 0),
        "Kaplan & Zingales": (12, 0),
        "Barros et al.": (12, -12),
        "Eça & Albanez": (-90, 15),
    }
    
    for study in studies_sorted:
        # Tamanho do bubble proporcional ao número de variáveis
        size = study['n_vars'] * 80
        color = COLOR_TCC if study['tipo'] == 'tcc' else COLOR_BENCH
        marker = '*' if study['tipo'] == 'tcc' else 'o'
        
        ax_c.scatter(study['n'], study['r_squared'] * 100,
                    s=size, c=color, marker=marker,
                    edgecolors='white', linewidths=2,
                    alpha=0.85, zorder=3)
        
        # Labels com informações ricas
        label_text = f"{study['short']}\n({study['periodo']})"
        offset = label_offsets.get(study['short'], (10, 0))
        
        ax_c.annotate(label_text,
                     xy=(study['n'], study['r_squared'] * 100),
                     xytext=offset, textcoords='offset points',
                     fontsize=11, color='#333',
                     ha='left', va='center',
                     fontweight='bold' if study['tipo'] == 'tcc' else 'normal',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                              alpha=0.9, edgecolor='#ddd', linewidth=0.5))
    
    ax_c.set_xlabel('Tamanho Amostral (N)', fontweight='bold')
    ax_c.set_ylabel('R² (%)', fontweight='bold')
    ax_c.set_xscale('log')
    ax_c.set_xlim(15, 900)
    ax_c.set_ylim(8, 35)
    ax_c.grid(True, linestyle='--', alpha=0.4)
    ax_c.set_title('(c) Panorama Comparativo: Tamanho Amostral × Poder Explicativo × Complexidade do Modelo',
                  fontweight='bold', loc='left', pad=10)
    
    # Legenda compacta no canto inferior direito (fora dos dados)
    legend_elements = [
        plt.scatter([], [], c=COLOR_TCC, s=120, marker='*', 
                   edgecolors='white', label='Este Estudo'),
        plt.scatter([], [], c=COLOR_BENCH, s=80, marker='o', 
                   edgecolors='white', label='Literatura'),
        plt.scatter([], [], c='gray', s=4*60, marker='o', 
                   alpha=0.3, edgecolors='gray', label='4 vars'),
        plt.scatter([], [], c='gray', s=8*60, marker='o', 
                   alpha=0.3, edgecolors='gray', label='8 vars'),
    ]
    
    ax_c.legend(handles=legend_elements, loc='lower left', 
               framealpha=0.95, fontsize=11, ncol=1, 
               labelspacing=2.1, borderpad=1.2)
    
    # =========================================================================
    # TÍTULOS E ANOTAÇÕES
    # =========================================================================
    # Título removido - será no caption do LaTeX
    # fig.suptitle('Figura 6: Posicionamento do Modelo de Custo de Dívida (Kd) em Relação à Literatura',
    #             fontsize=12, fontweight='bold', y=0.98)
    
    # Nota de rodapé removida conforme solicitação
    
    # Salvar
    if output_path is None:
        import os
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'reports', 'figures', 'fig06_model_comparison_comprehensive.png'
        )
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Figura salva em: {output_path}")
    
    plt.close()
    return output_path


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Gerando Figura de Comparação Científica Compreensiva")
    print("="*60 + "\n")
    
    path = create_comprehensive_figure()
    
    print("\n✓ Figura gerada com sucesso!")
    print(f"  Arquivo: {path}")
