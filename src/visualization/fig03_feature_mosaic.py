#!/usr/bin/env python3
"""
Figura 3: Mosaico Científico de Criação de Features (Ajustes Finais Aesthetics)

Este script gera uma figura formal para o TCC (Figura 03) contendo:
(a) Fluxograma metodológico com ÍCONES (Visual Flow)
(b) Taxonomia em formato de CARDS (Grid) - Sem overlaps
(c) Estatísticas descritivas (Violin Plots) - UX Melhorada

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
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
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 300,
})

COLORS = {
    'primary': styles.COLORS['secondary'],      # Azul escuro
    'secondary': styles.COLORS['secondary'],
    'accent': '#3498db',                        # Azul claro (manter para violins)
    'highlight': styles.COLORS['primary'],      # Vermelho (#D64045/c0392b)
    'card_bg': '#f8f9fa',
    'card_edge': styles.COLORS['secondary'],
    'text': '#000000',
}

ASSETS_DIR = Path(__file__).parent / "assets"

# -----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------------

def load_data():
    """Carrega dados."""
    return pd.read_csv(CONSOLIDATED_PATH / "tabela_features.csv")

def add_icon(ax, filename, xy, zoom=0.15):
    """Adiciona ícone ao plot."""
    path = ASSETS_DIR / filename
    if path.exists():
        img = plt.imread(path)
        imagebox = OffsetImage(img, zoom=zoom)
        ab = AnnotationBbox(imagebox, xy, frameon=False, box_alignment=(0.5, 0.5))
        ax.add_artist(ab)
    else:
        ax.text(xy[0], xy[1], "?", fontsize=20, ha='center', va='center')

# -----------------------------------------------------------------------------
# PAINEL A: FLUXOGRAMA COM ÍCONES
# -----------------------------------------------------------------------------
def draw_methodology_panel(ax):
    """Desenha o fluxo metodológico com ícones."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Título
    ax.text(0.0, 1.0, "(a) Metodologia de Extração", fontsize=11, fontweight='bold', color=COLORS['primary'], va='top')
    
    steps = [
        ("Relatórios\nDFP/Excel", "pdf_icon.png"),
        ("Extração\nDireta", "settings_icon.png"),
        ("Mapeamento\nCVM", "ai_icon.png"),
        ("Limpeza &\nSanidade", "clean_icon.png"),
        ("Cálculo de\nFeatures", "calc_icon.png")
    ]
    
    y_pos = 0.55
    spacing = 0.18 # Ajuste manual do espaçamento
    start_x = 0.14
    
    # Desenhar conexões
    for i in range(len(steps) - 1):
        x1 = start_x + i * spacing
        x2 = start_x + (i + 1) * spacing
        ax.annotate("",
            xy=(x2 - 0.05, y_pos), xycoords='data',
            xytext=(x1 + 0.05, y_pos), textcoords='data',
            arrowprops=dict(arrowstyle="->", color=COLORS['primary'], lw=1.5) # Arrow darker
        )

    # Desenhar Ícones e Labels
    for i, (label, icon_file) in enumerate(steps):
        x = start_x + i * spacing
        add_icon(ax, icon_file, (x, y_pos), zoom=0.35)
        # Ajustado y_pos - 0.28 (mais 6% para baixo conforme solicitado)
        ax.text(x, y_pos - 0.28, label, ha='center', va='top', fontsize=10, color=COLORS['text']) # Text Black

# -----------------------------------------------------------------------------
# PAINEL B: TAXONOMIA (GRID DE CARDS)
# -----------------------------------------------------------------------------
def draw_taxonomy_panel(ax):
    """Desenha a taxonomia em cards."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    ax.text(0.0, 1.02, "(b) Blocos Financeiros", fontsize=11, fontweight='bold', color=COLORS['primary'], va='bottom')
    
    cards = [
        ("1. Alavancagem", ["Divida / Ativo", "Divida / PL", "Alavancagem Total"]),
        ("2. Liquidez", ["Liquidez Corrente", "Liquidez Imediata", "Cobertura Caixa"]),
        ("3. Rentabilidade", ["ROA", "ROE", "Margem EBITDA"]),
        ("4. Estrutura/Perfil", ["Tamanho (Log)", "Tangibilidade", "% Curto Prazo"]),
        ("5. Heterogeneidade", ["IHH Indexador", "IHH Tipo", "Indice Diversif."]),
        ("6. Cobertura", ["Cobertura Juros", "Divida / EBITDA", "Geração Caixa Op"])
    ]
    
    cols = 3
    
    # Dimensões do card - Reduzidas levemente para evitar overlap
    card_w = 0.28   # Antes era 0.30
    card_h = 0.35
    h_gap = 0.05    # Aumentado gap horizontal
    v_gap = 0.10
    
    start_x = 0.02
    start_y = 0.95
    
    for i, (title, items) in enumerate(cards):
        r = i // cols
        c = i % cols
        
        x = start_x + c * (card_w + h_gap)
        y = start_y - (r + 1) * card_h - r * v_gap
        
        # Sombra
        shadow = mpatches.FancyBboxPatch(
            (x + 0.005, y - 0.005), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=0.02",
            facecolor='#bdc3c7', edgecolor='none', zorder=1 # Sombra mais escura
        )
        ax.add_patch(shadow)
        
        # Card
        box = mpatches.FancyBboxPatch(
            (x, y), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=0.02",
            facecolor='white', edgecolor=COLORS['card_edge'], linewidth=1.0, zorder=2
        )
        ax.add_patch(box)
        
        # Header
        header_h = 0.08
        header = mpatches.FancyBboxPatch(
            (x, y + card_h - header_h), card_w, header_h,
            boxstyle="round,pad=0,rounding_size=0.02", 
            facecolor=COLORS['primary'], edgecolor='none', zorder=3
        )
        ax.add_patch(header)
        
        ax.text(x + card_w/2, y + card_h - header_h/2, title, 
                ha='center', va='center', color='white', fontweight='bold', fontsize=10, zorder=4)
        
        # Lista
        for j, item in enumerate(items):
            iy = y + card_h - header_h - 0.06 - j * 0.075 # Mais espaçamento vertical
            ax.text(x + 0.02, iy, f"• {item}", fontsize=10, color=COLORS['text'], va='top', zorder=4)

# -----------------------------------------------------------------------------
# PAINEL C: ESTATÍSTICAS
# -----------------------------------------------------------------------------
def draw_stats_panel(fig, gs_base, df):
    """Desenha os violin plots com UX melhorado (sem cinza, mais contraste)."""
    gs_inner = gs_base.subgridspec(2, 3, wspace=0.3, hspace=0.4)
    
    ax_title = fig.add_subplot(gs_base)
    ax_title.axis('off')
    # Ajustado de 1.08 para 1.15 para subir o título
    ax_title.text(0.0, 1.15, "(c) Distribuições Representativas", fontsize=11, fontweight='bold', color=COLORS['primary'], va='bottom')
    
    features = [
        ('Divida_Total_Ativo', 'Alavancagem\n(Debt/Asset)'),
        ('Liquidez_Corrente', 'Liquidez\nCorrente'),
        ('ROA', 'Rentabilidade\n(ROA)'),
        ('Tamanho', 'Tamanho\n(Log Ativo)'),
        ('IHH_Indexador', 'Concentração\n(IHH Indexador)'),
        ('Proporcao_Divida_CP', 'Perfil\n(% Curto Prazo)')
    ]
    
    for i, (col, label) in enumerate(features):
        ax = fig.add_subplot(gs_inner[i // 3, i % 3])
        
        if col in df.columns:
            data = df[col].replace([np.inf, -np.inf], np.nan).dropna()
            
            # Winsorização leve para visualização (1%-99%)
            q1, q99 = data.quantile([0.01, 0.99])
            data = data.clip(q1, q99)
            
            # Violin simplificado e limpo
            parts = ax.violinplot(data, vert=True, showextrema=False, widths=0.7)
            for pc in parts['bodies']:
                pc.set_facecolor(COLORS['accent'])
                pc.set_alpha(0.8) # Mais opaco para contraste
                pc.set_edgecolor(COLORS['primary']) # Borda escura
                
            # Boxplot simplificado (Preto)
            ax.boxplot(data, vert=True, widths=0.05, patch_artist=False,
                       boxprops=dict(linewidth=1.2, color='black'),
                       whiskerprops=dict(linewidth=1.2, color='black'),
                       capprops=dict(linewidth=1.2, color='black'),
                       medianprops=dict(linewidth=1.5, color='white'), 
                       showfliers=False)
            
            # Mediana vermelha
            m = data.median()
            ax.plot([1], [m], color=COLORS['highlight'], marker='o', markersize=3)
        else:
            ax.text(0.5, 0.5, "Dados não\ndisponíveis", ha='center', va='center')
        
        ax.set_title(label, fontsize=10, color=COLORS['text'], fontweight='bold') # Title Darker
        ax.set_xticks([])
        ax.grid(axis='y', linestyle='-', alpha=0.2, color='black') # Grid preto suave
        
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(left=False, labelsize=8, labelcolor='black')



# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def create_figure(df):
    fig = plt.figure(figsize=(11, 10))

    # Título Geral - Removido (será no LaTeX via \caption)
    # fig.suptitle('Figura 3: Criação de Features e Análise Exploratória', 
    #              fontsize=14, fontweight='bold', color=COLORS['primary'], y=0.98)
    
    # Ajuste de layout: A menor (0.15) para puxar B para cima (0.42)
    # hspace reduzido de 0.45 para 0.35
    gs = fig.add_gridspec(3, 1, height_ratios=[0.15, 0.42, 0.43], hspace=0.35) 
    
    # Ajuste manual do topo para caber o título
    plt.subplots_adjust(top=0.92, bottom=0.05)
    
    ax_a = fig.add_subplot(gs[0])
    draw_methodology_panel(ax_a)
    
    ax_b = fig.add_subplot(gs[1])
    draw_taxonomy_panel(ax_b)
    
    draw_stats_panel(fig, gs[2], df)
    
    return fig

def main():
    print("Gerando Figura 03 Refinada (Final Aesthetics)...")
    df = load_data()
    fig = create_figure(df)
    
    output = FIGURES_DIR / "fig03_feature_mosaic.pdf"
    fig.savefig(output, facecolor='white', bbox_inches='tight', format='pdf')
    print(f"Salvo em: {output}")

if __name__ == "__main__":
    main()
