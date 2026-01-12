"""
Estilos Padronizados para Figuras do TCC
=========================================
Arquivo central de configuração visual para garantir consistência
entre todas as figuras do trabalho.

Autor: TCC Pipeline
Data: 2026-01-11
"""

import matplotlib.pyplot as plt
import matplotlib as mpl

# =============================================================================
# PALETA DE CORES OFICIAL DO TCC
# =============================================================================

COLORS = {
    # Cores principais
    'primary': '#D64045',      # Vermelho - destaque principal
    'secondary': '#1E3A5F',    # Azul escuro - elementos secundários
    
    # Cores de suporte
    'accent': '#E8913A',       # Laranja - acentos
    'neutral': '#4A5568',      # Cinza escuro - texto
    'light': '#E8E8E8',        # Cinza claro - fundos, grids
    
    # Cores para escalas
    'positive': '#2E7D32',     # Verde - valores positivos
    'negative': '#C62828',     # Vermelho - valores negativos
    
    # Cores para séries (gráficos com múltiplas linhas/barras)
    'series': [
        '#1E3A5F',  # Azul escuro
        '#D64045',  # Vermelho
        '#E8913A',  # Laranja
        '#2E7D32',  # Verde
        '#7B1FA2',  # Roxo
        '#00838F',  # Teal
    ]
}

# =============================================================================
# CONFIGURAÇÕES DE FONTE
# =============================================================================

FONTS = {
    'family': 'serif',
    'title': 15,
    'subtitle': 12,
    'axis_label': 11,
    'tick': 10,
    'legend': 9,
    'annotation': 9,
    'note': 8,
}

# =============================================================================
# ESTILO MATPLOTLIB GLOBAL
# =============================================================================

STYLE_PARAMS = {
    # Fonte
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif', 'serif'],
    'font.size': FONTS['tick'],
    
    # Textos matemáticos (LaTeX)
    'mathtext.fontset': 'stix', # Estilo similar a Times para equações
    'mathtext.rm': 'Times New Roman',
    'mathtext.it': 'Times New Roman:italic',
    'mathtext.bf': 'Times New Roman:bold',
    
    # Títulos
    'axes.titlesize': FONTS['subtitle'],
    'axes.titleweight': 'bold',
    'axes.labelsize': FONTS['axis_label'],
    
    # Ticks
    'xtick.labelsize': FONTS['tick'],
    'ytick.labelsize': FONTS['tick'],
    
    # Legenda
    'legend.fontsize': FONTS['legend'],
    'legend.framealpha': 0.95,
    
    # Figura
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
    'savefig.edgecolor': 'none',
    
    # Eixos
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    
    # Grid
    'axes.grid': False,
    'grid.alpha': 0.4,
    'grid.linestyle': '--',
}


def apply_style():
    """Aplica o estilo padrão do TCC às figuras matplotlib."""
    plt.rcParams.update(STYLE_PARAMS)


def format_title(fig_number: int, title: str) -> str:
    """
    Formata título da figura no padrão do TCC.
    
    Args:
        fig_number: Número da figura (1, 2, 3...)
        title: Título descritivo da figura
        
    Returns:
        Título formatado: "Figura X: Título"
    """
    return f"Figura {fig_number}: {title}"


def format_panel_label(letter: str, title: str) -> str:
    """
    Formata label de painel no padrão do TCC.
    
    Args:
        letter: Letra do painel (a, b, c...)
        title: Título do painel
        
    Returns:
        Label formatado: "(a) Título"
    """
    return f"({letter.lower()}) {title}"


def get_colormap_diverging():
    """Retorna colormap divergente (azul-branco-vermelho) para correlações."""
    from matplotlib.colors import LinearSegmentedColormap
    colors = [COLORS['secondary'], 'white', COLORS['primary']]
    return LinearSegmentedColormap.from_list('tcc_diverging', colors)


def get_colormap_sequential():
    """Retorna colormap sequencial (branco para azul escuro)."""
    from matplotlib.colors import LinearSegmentedColormap
    colors = ['white', COLORS['secondary']]
    return LinearSegmentedColormap.from_list('tcc_sequential', colors)


# =============================================================================
# ESTILOS PARA ELEMENTOS ESPECÍFICOS
# =============================================================================

BAR_STYLE = {
    'edgecolor': 'white',
    'linewidth': 0.5,
    'alpha': 0.9,
}

SCATTER_STYLE = {
    'edgecolors': 'white',
    'linewidths': 1.5,
    'alpha': 0.85,
}

GRID_STYLE = {
    'linestyle': '--',
    'alpha': 0.4,
    'color': COLORS['light'],
}

ANNOTATION_BOX = {
    'boxstyle': 'round,pad=0.3',
    'facecolor': 'white',
    'alpha': 0.9,
    'edgecolor': '#ddd',
    'linewidth': 0.5,
}


# Aplicar estilo automaticamente ao importar
apply_style()


if __name__ == "__main__":
    print("Estilos do TCC carregados com sucesso!")
    print(f"Cores disponíveis: {list(COLORS.keys())}")
    print(f"Fonte: {FONTS['family']}")
