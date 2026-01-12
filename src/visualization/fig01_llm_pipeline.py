#!/usr/bin/env python3
"""
Figura 1: Pipeline de Extração de Dados com LLM (Profissional)

Este script gera um diagrama de fluxo usando MATPLOTLIB e ÍCONES REAIS (PNG).
Estilo: "Azure Architecture Diagram" / Infográfico Técnico.
Ajustes: Fontes Serif (Times New Roman), Contraste Alto, Métricas de Eficiência.

Requer:
- src/visualization/assets/*.png (Baixados via src/utils/download_icons.py)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.lines as mlines
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import FIGURES_DIR
from src.visualization import styles
styles.apply_style()

# Configurações de estilo acadêmico
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'figure.titlesize': 13,
    'figure.dpi': 300,
})

# Cores de Alto Contraste (Padronizadas)
COLORS = {
    'primary': styles.COLORS['primary'],
    'title': styles.COLORS['secondary'],
    'text': styles.COLORS['neutral'],
    'accent_line': styles.COLORS['secondary'], 
    'box_fill': '#f8f9fa'      
}

ASSETS_DIR = Path(__file__).parent / "assets"

def get_image(name, zoom=0.5):
    """Carrega imagem PNG e retorna OffsetImage."""
    path = ASSETS_DIR / name
    if not path.exists():
        print(f"AVISO: Ícone não encontrado: {path}")
        return None
    img = plt.imread(path)
    return OffsetImage(img, zoom=zoom)

def create_professional_pipeline():
    """Cria diagrama com ícones reais + matplotlib."""
    
    # Aumentar altura para acomodar todos os elementos sem sobreposição
    fig, ax = plt.subplots(figsize=(14, 7.5))
    ax.axis('off')
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.05, 1.0)  # Estendido para baixo para caber o prompt box

    # ==========================================================================
    # LAYOUT VERTICAL - ESPAÇAMENTO PROFISSIONAL
    # ==========================================================================
    # Zona Superior: Ícones e Labels (0.55 - 0.95)
    ARROW_LABEL_Y = 0.88    # Labels das setas
    ICON_Y = 0.78           # Ícones
    TEXT_Y = 0.62           # Títulos dos passos
    SUBTEXT_Y = 0.54        # Descrições
    
    # Zona Inferior: Prompt Box e Nota (0.05 - 0.45)
    PROMPT_BOX_TOP = 0.32   # Topo do box de prompt (abaixado)
    DIVIDER_Y = 0.12        # Linha divisória (abaixada)
    
    # Margens Horizontais
    MARGIN_LEFT = 0.05
    MARGIN_RIGHT = 0.95
    
    # Posições X distribuídas uniformemente
    X_POS = [0.125, 0.375, 0.625, 0.875]

    # ==========================================================================
    # PASSOS DO PIPELINE
    # ==========================================================================
    steps = [
        {
            "icon": "db_icon.png", "zoom": 0.40,
            "title": "FONTE DE DADOS", 
            "desc": "CVM / B3\n(Dados Públicos)",
        },
        {
            "icon": "pdf_icon.png", "zoom": 0.40,
            "title": "INPUT NÃO ESTRUTURADO", 
            "desc": "DFP e Notas Explicativas\n(PDF / Texto)",
        },
        {
            "icon": "ai_icon.png", "zoom": 0.40,
            "title": "MOTOR LLM AI", 
            "desc": "Google Gemini 1.5 Pro\n(Information Extraction)",
        },
        {
            "icon": "csv_icon.png", "zoom": 0.40,
            "title": "DADOS ESTRUTURADOS", 
            "desc": "Dataset Final\n(Painel Balanceado)",
        }
    ]

    # Desenhar cada passo
    for i, step in enumerate(steps):
        x = X_POS[i]
        img_box = get_image(step["icon"], zoom=step["zoom"])
        if img_box:
            ab = AnnotationBbox(img_box, (x, ICON_Y), frameon=False)
            ax.add_artist(ab)
        
        ax.text(x, TEXT_Y, step["title"], 
                ha='center', va='top', fontsize=12, fontweight='bold', 
                color=COLORS['primary'])
        
        ax.text(x, SUBTEXT_Y, step["desc"], 
                ha='center', va='top', fontsize=11, color=COLORS['text'],
                linespacing=1.4)

    # ==========================================================================
    # SETAS E LABELS (CORRIGIDO - DENTRO DO LOOP)
    # ==========================================================================
    arrow_labels = ["Coleta Automática", "Prompt Engineering", "Parsing & Validação"]
    for i in range(len(steps) - 1):
        x_start = X_POS[i] + 0.07
        x_end = X_POS[i+1] - 0.07
        center_x = (x_start + x_end) / 2
        
        # Seta
        ax.annotate("", xy=(x_end, ICON_Y), xytext=(x_start, ICON_Y),
                    arrowprops=dict(arrowstyle="->", color=COLORS['accent_line'], lw=1.5, 
                                  shrinkA=5, shrinkB=5))
        
        # Label da seta (DENTRO do loop)
        ax.text(center_x, ARROW_LABEL_Y, arrow_labels[i],
                ha='center', va='bottom', fontsize=11,
                color=COLORS['text'], backgroundcolor='white')

    # ==========================================================================
    # DESTAQUE DO NÚCLEO DE PROCESSAMENTO
    # ==========================================================================
    # Box roxo ao redor do LLM
    llm_box_left = X_POS[2] - 0.11
    llm_box_bottom = SUBTEXT_Y - 0.08
    llm_box_width = 0.22
    llm_box_height = ARROW_LABEL_Y - llm_box_bottom + 0.05
    
    rect = mpatches.FancyBboxPatch(
        (llm_box_left, llm_box_bottom), llm_box_width, llm_box_height,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor='#f3e5f5', edgecolor='#8e44ad',
        linewidth=1.5, linestyle='--', zorder=0, alpha=0.35
    )
    ax.add_patch(rect)
    
    # Label do núcleo
    ax.text(X_POS[2], llm_box_bottom + llm_box_height + 0.02, 
            "Núcleo de Processamento", 
            ha='center', va='bottom', fontsize=11, 
            color='#4a148c', fontweight='bold')
    
    # ==========================================================================
    # BOX DE PROMPT (POSICIONADO ABAIXO DOS STEPS)
    # ==========================================================================
    prompt_text = (
        r"$\bf{Prompt\ System:}$ 'Você é um especialista financeiro...'" + "\n"
        r"$\bf{Task:}$ 'Extraia da Nota Explicativa:'" + "\n"
        r"  - Taxa de Juros (Kd)" + "\n"
        r"  - Indexador (CDI, IPCA)" + "\n"
        r"  - Moeda / Prazos" + "\n"
        r"$\bf{Output:}$ JSON"
    )
    
    # Posicionar o box de prompt abaixo do SUBTEXT, conectando ao ícone LLM
    prompt_x = X_POS[2] - 0.08  # Movido para a esquerda para evitar corte
    ax.annotate(prompt_text,
                xy=(X_POS[2], SUBTEXT_Y - 0.10),  # Conecta abaixo da descrição
                xytext=(prompt_x, PROMPT_BOX_TOP),
                arrowprops=dict(arrowstyle='->', color='#2c3e50', 
                               connectionstyle="arc3,rad=-0.1", lw=1.2),
                ha='left', va='top', fontsize=10, 
                color=COLORS['text'], family='monospace',
                bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", 
                         ec="#2c3e50", alpha=1.0, lw=1.2))
    
    # ==========================================================================
    # NOTA METODOLÓGICA
    # ==========================================================================
    line = mlines.Line2D([MARGIN_LEFT, MARGIN_RIGHT], [DIVIDER_Y, DIVIDER_Y], 
                         color='#2c3e50', linewidth=1)
    ax.add_line(line)
    
    justificativa_note = (
        r"$\bf{Nota\ (Eficiência\ Computacional):}$ A extração manual de dados de dívida em Notas Explicativas é complexa "
        r"devido à falta de padronização." + "\n"
        r"O uso do LLM (Gemini 1.5 Pro) automatizou a leitura, reduzindo o tempo médio de coleta de $\approx$20 min/doc (manual) "
        r"para <30 seg/doc." + "\n" 
        r"A validação humana atuou apenas por amostragem, assegurando integridade para a regressão."
    )
    
    ax.text(MARGIN_LEFT, DIVIDER_Y - 0.02, justificativa_note, 
            ha='left', va='top', fontsize=12, color=COLORS['text'],
            linespacing=1.4)

    return fig

def main():
    print("=" * 60)
    print("GERANDO FIGURA 1: PIPELINE PROFISSIONAL (REFINADO)")
    print("=" * 60)
    
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    if not any(ASSETS_DIR.glob("*.png")):
        print("ERRO: Ícones não encontrados. Execute src/utils/download_icons.py primeiro.")
        return

    print("1. Renderizando diagrama com fontes serif e métricas...")
    fig = create_professional_pipeline()
    
    output_path = FIGURES_DIR / "fig01_llm_pipeline.pdf"
    fig.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.02, format='pdf')
    plt.close(fig)
    
    print(f"✓ Figura salva em: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
