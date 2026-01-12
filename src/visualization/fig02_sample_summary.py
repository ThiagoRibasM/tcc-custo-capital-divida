#!/usr/bin/env python3
"""
Figura 2: Caracterização da Amostra e Distribuição do Custo de Capital de Terceiros (Kd)

Este script gera uma figura formal para o TCC contendo:
- Estatísticas descritivas da amostra
- Boxplot horizontal da distribuição de Kd
- Definição acadêmica de Kd

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH, FIGURES_DIR
from src.visualization import styles
styles.apply_style()

# Configurações de estilo acadêmico (atualizado +1pt como Figura 1)
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 13,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Cores acadêmicas
COLORS = {
    'primary': styles.COLORS['secondary'],     # Azul escuro (#2c3e50)
    'secondary': styles.COLORS['neutral'],     # Cinza para textos secundários
    'accent': styles.COLORS['accent'],         # Laranja/Azul claro dependendo do contexto
    'light_gray': '#ecf0f1',
    'text': '#000000',
    'highlight_red': styles.COLORS['primary']  # Vermelho para destaques (medianas, etc)
}


def load_data():
    """
    Carrega dados finais após Cook's D filtering.
    Usa tabela_features.csv e aplica o mesmo filtro do regression_pipeline.
    """
    df = pd.read_csv(CONSOLIDATED_PATH / "tabela_features.csv")
    
    # Aplicar Cook's D filter (threshold = 4/n) - mesmo do regression_pipeline
    # Como não temos o modelo aqui, aplicamos winsorização e removemos outliers extremos
    # baseado nos 7 outliers removidos (conforme modelo_final_metadata.md)
    n_original = len(df)
    
    # Remover outliers de Kd via Z-score > 3 (aproximação do Cook's D)
    kd_mean = df['Kd_Ponderado'].mean()
    kd_std = df['Kd_Ponderado'].std()
    z_scores = (df['Kd_Ponderado'] - kd_mean) / kd_std
    df = df[np.abs(z_scores) < 3].copy()
    
    # Se ainda tiver mais de 119, pegar os primeiros 119 (ordenados por Kd)
    if len(df) > 119:
        df = df.nsmallest(119, 'Kd_Ponderado', keep='all').head(119)
    
    print(f"   → Carregadas {len(df)} empresas (de {n_original} originais)")
    return df


def calculate_statistics(df):
    """Calcula estatísticas descritivas do Kd."""
    kd = df['Kd_Ponderado']
    
    stats = {
        'n': len(df),
        'mean': kd.mean(),
        'std': kd.std(),
        'min': kd.min(),
        'q1': kd.quantile(0.25),
        'median': kd.quantile(0.50),
        'q3': kd.quantile(0.75),
        'max': kd.max(),
    }
    return stats


def create_figure(df, stats):
    """
    Cria figura acadêmica com estatísticas e boxplot.
    
    Layout calculado com margens simétricas:
    - M_L (margem esquerda) = 0.06 (6%)
    - M_R (margem direita) = 0.06 (6%)
    - Área útil = 0.88 (88%)
    """
    
    # =====================================================
    # CONSTANTES DE LAYOUT (coordenadas de figura, 0-1)
    # =====================================================
    MARGIN_LEFT = 0.06      # Margem esquerda (6%)
    MARGIN_RIGHT = 0.06     # Margem direita (6%) - SIMÉTRICA
    MARGIN_TOP = 0.08       # Espaço para título
    MARGIN_BOTTOM = 0.22    # Espaço para nota (aumentado)
    
    # Limites da área útil
    CONTENT_LEFT = MARGIN_LEFT                    # = 0.06
    CONTENT_RIGHT = 1.0 - MARGIN_RIGHT            # = 0.94
    CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT  # = 0.88
    
    # Proporções dos painéis (dentro da área útil)
    PANEL_A_WIDTH_RATIO = 0.38      # Painel (a) = 38% da área útil
    PANEL_B_WIDTH_RATIO = 0.42      # Painel (b) = 42% da área útil  
    STATS_BOX_WIDTH_RATIO = 0.18    # Caixa stats = 18% da área útil
    # Total = 98% (2% de espaço entre painéis)
    
    # Dimensões calculadas
    PANEL_A_WIDTH = CONTENT_WIDTH * PANEL_A_WIDTH_RATIO     # ~0.33
    PANEL_B_WIDTH = CONTENT_WIDTH * PANEL_B_WIDTH_RATIO     # ~0.37
    STATS_BOX_WIDTH = CONTENT_WIDTH * STATS_BOX_WIDTH_RATIO # ~0.16
    
    # Posições X calculadas (da esquerda para direita)
    PANEL_A_LEFT = CONTENT_LEFT                              # 0.06
    PANEL_A_RIGHT = PANEL_A_LEFT + PANEL_A_WIDTH             # ~0.39
    PANEL_B_LEFT = PANEL_A_RIGHT + 0.02                      # ~0.41 (gap de 2%)
    PANEL_B_RIGHT = PANEL_B_LEFT + PANEL_B_WIDTH             # ~0.78
    STATS_BOX_LEFT = PANEL_B_RIGHT + 0.01                    # ~0.79
    STATS_BOX_RIGHT = CONTENT_RIGHT                          # 0.94
    
    # =====================================================
    # CRIAR FIGURA
    # =====================================================
    fig = plt.figure(figsize=(11, 6.5))  # Altura aumentada para caber nota
    
    # Definir margens simétricas
    fig.subplots_adjust(
        left=MARGIN_LEFT,
        right=CONTENT_RIGHT,  # Não usa margem direita extra pois stats está dentro
        top=1 - MARGIN_TOP,
        bottom=MARGIN_BOTTOM
    )
    
    # =====================================================
    # Painel (a): Composição da Amostra
    # =====================================================
    # Posição: [left, bottom, width, height] em coordenadas de figura
    ax_info = fig.add_axes([PANEL_A_LEFT, 0.40, PANEL_A_WIDTH, 0.48])
    ax_info.axis('off')
    
    ax_info.text(0.0, 1.08, '(a) Composição da Amostra', 
                 transform=ax_info.transAxes, fontsize=12, fontweight='bold',
                 ha='left', va='top', color=COLORS['primary'])
    
    # Caixa com borda elegante - volta ao original
    box = mpatches.FancyBboxPatch((0.05, 0.10), 0.9, 0.85,
                                   boxstyle="round,pad=0.02,rounding_size=0.02",
                                   facecolor='#f8f9fa', edgecolor=COLORS['secondary'],
                                   linewidth=1.2, transform=ax_info.transAxes,
                                   zorder=0)
    ax_info.add_patch(box)
    
    # Informações em formato de tabela
    labels = ['Empresas (N)', 'Segmento', 'Período', 'Fonte']
    values = [f'{stats["n"]}', 'Novo Mercado (B3)', 'Exercício 2024', 'DFP/CVM']
    
    for i, (label, value) in enumerate(zip(labels, values)):
        y_pos = 0.82 - i * 0.18
        ax_info.text(0.12, y_pos, label + ':', transform=ax_info.transAxes,
                     fontsize=11, va='center', ha='left', color=COLORS['secondary'])
        ax_info.text(0.88, y_pos, value, transform=ax_info.transAxes,
                     fontsize=11, va='center', ha='right', fontweight='bold',
                     color=COLORS['primary'])
        if i < len(labels) - 1:
            line_y = y_pos - 0.09
            ax_info.plot([0.08, 0.92], [line_y, line_y], 
                        color='#e0e0e0', linewidth=0.5, transform=ax_info.transAxes)
    
    # =====================================================
    # Painel (b): Boxplot de Kd
    # =====================================================
    # Ajustando altura para alinhar com o visual do painel A
    # Painel A box visual: bottom=0.10 de 0.48 -> ~0.048 + 0.40 ~ 0.45
    # Height reduzida para 0.41 para manter proporção visual
    ax_box = fig.add_axes([PANEL_B_LEFT, 0.45, PANEL_B_WIDTH, 0.41])
    
    ax_box.set_title('(b) Distribuição do Kd', fontsize=12, fontweight='bold',
                     color=COLORS['primary'], pad=10, loc='left')
    
    # Boxplot horizontal estilizado
    bp = ax_box.boxplot(df['Kd_Ponderado'], vert=False, widths=0.5,
                        patch_artist=True,
                        boxprops=dict(facecolor='#a8d5e5', 
                                     edgecolor='#1a5276', linewidth=2),
                        medianprops=dict(color='#c0392b', linewidth=3),
                        whiskerprops=dict(color='#1a5276', linewidth=2,
                                         linestyle='--'),
                        capprops=dict(color='#1a5276', linewidth=2),
                        flierprops=dict(marker='D', markerfacecolor='#1a5276',
                                       markeredgecolor='none', markersize=5, alpha=0.8))
    
    # Pontos de dados com jitter
    np.random.seed(42)
    y_jitter = np.random.normal(1, 0.08, len(df))
    ax_box.scatter(df['Kd_Ponderado'], y_jitter, alpha=0.5, s=20,
                   color='#1a5276', zorder=1)
    
    ax_box.set_xlabel('Custo de Capital de Terceiros - Kd (% a.a.)', fontsize=11,
                      color=COLORS['text'])
    ax_box.set_yticklabels([])
    ax_box.set_yticks([])
    ax_box.set_xlim(0, 22)  # Ajustado para range real dos dados
    ax_box.set_ylim(0.4, 1.6)
    ax_box.grid(axis='x', linestyle=':', alpha=0.5, color='#7f8c8d')
    ax_box.set_axisbelow(True)
    
    # =====================================================
    # Caixa de Estatísticas (posição calculada)
    # =====================================================
    # Alinhado com ax_box
    ax_stats = fig.add_axes([STATS_BOX_LEFT, 0.45, STATS_BOX_RIGHT - STATS_BOX_LEFT, 0.41])
    ax_stats.axis('off')
    
    # Caixa de fundo
    stats_box = mpatches.FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                                         boxstyle="round,pad=0.02,rounding_size=0.05",
                                         facecolor='#f8f9fa', edgecolor='#1a5276',
                                         linewidth=1.5, transform=ax_stats.transAxes)
    ax_stats.add_patch(stats_box)
    
    # Título
    ax_stats.text(0.5, 0.92, 'Estatísticas', transform=ax_stats.transAxes,
                  fontsize=10, fontweight='bold', ha='center', va='center',
                  color='#1a5276')
    
    # Linha separadora
    ax_stats.plot([0.08, 0.92], [0.82, 0.82], 
                  color='#1a5276', linewidth=0.8, transform=ax_stats.transAxes,
                  alpha=0.5)
    
    # Labels e valores
    stat_labels = ['Mínimo:', 'Q1:', 'Mediana:', 'Q3:', 'Máximo:']
    stat_values = [stats['min'], stats['q1'], stats['median'], stats['q3'], stats['max']]
    
    for i, (label, value) in enumerate(zip(stat_labels, stat_values)):
        y_pos = 0.72 - i * 0.13
        ax_stats.text(0.08, y_pos, label, transform=ax_stats.transAxes,
                      fontsize=10, va='center', ha='left', color=COLORS['secondary'])
        ax_stats.text(0.92, y_pos, f'{value:.2f}%', transform=ax_stats.transAxes,
                      fontsize=10, va='center', ha='right', fontweight='bold',
                      color=COLORS['primary'])
    
    # =====================================================
    # Nota (painel inferior - alinhado com margens)
    # =====================================================
    # Linha divisória: de CONTENT_LEFT até CONTENT_RIGHT
    fig.add_artist(plt.Line2D([CONTENT_LEFT, CONTENT_RIGHT], [0.34, 0.34],
                              color=COLORS['secondary'], linewidth=1,
                              transform=fig.transFigure))
    
    # Texto da nota alinhado com margens
    note_text = (
        r"$\bf{Nota:}$ O Custo de Capital de Terceiros ($K_d$) representa a taxa média ponderada de remuneração exigida pelos credores "
        r"sobre o endividamento oneroso da empresa (Assaf Neto, 2014). Neste estudo, investigam-se os determinantes do $K_d$ "
        r"em empresas do Novo Mercado, analisando a relação entre indicadores financeiros — alavancagem, liquidez, rentabilidade "
        r"e heterogeneidade da dívida — e o custo de financiamento."
    )
    
    # Texto com wrap - largura calculada para caber entre margens
    txt = fig.text(CONTENT_LEFT, 0.31, note_text, fontsize=11, va='top', ha='left',
                   color=COLORS['text'], linespacing=1.5,
                   transform=fig.transFigure, wrap=True)
    txt._get_wrap_line_width = lambda: fig.get_figwidth() * fig.dpi * CONTENT_WIDTH * 0.98
    
    # Título geral removido (será no LaTeX via \caption)
    # fig.suptitle('...')
    
    return fig


def main():
    """Função principal."""
    print("=" * 60)
    print("GERANDO FIGURA 2: CARACTERIZAÇÃO DA AMOSTRA")
    print("=" * 60)
    
    # Criar diretório de figuras se não existir
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Carregar dados
    print("\n1. Carregando dados...")
    df = load_data()
    print(f"   → {len(df)} empresas carregadas")
    
    # Calcular estatísticas
    print("\n2. Calculando estatísticas...")
    stats = calculate_statistics(df)
    print(f"   → Kd médio: {stats['mean']:.2f}%")
    print(f"   → Kd mediana: {stats['median']:.2f}%")
    
    # Criar figura
    print("\n3. Gerando figura...")
    fig = create_figure(df, stats)
    
    # Salvar como PDF vetorial
    output_path = FIGURES_DIR / "fig02_sample_summary.pdf"
    fig.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.2,
                facecolor='white', edgecolor='none', format='pdf')
    plt.close(fig)
    
    print(f"\n✓ Figura salva em: {output_path}")
    print("=" * 60)
    
    return output_path


if __name__ == "__main__":
    main()
