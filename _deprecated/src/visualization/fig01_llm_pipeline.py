#!/usr/bin/env python3
"""
Figura 2: Pipeline de Extração de Dados com LLM (Profissional)

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

# Configurações de estilo acadêmico (Igual Figura 1)
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'figure.titlesize': 12,
    'figure.dpi': 300,
})

# Cores de Alto Contraste (Evitando cinza claro para texto)
COLORS = {
    'primary': '#000000',      # Preto para títulos principais
    'text': '#1a1a1a',         # Quase preto para descrições
    'accent_line': '#2c3e50',  # Azul escuro para linhas/setas
    'box_fill': '#f8f9fa'      # Fundo suave para métricas
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
    
    # Aumentar altura para caber a justificativa (Metrics)
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('off')
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0) # Normalizado

    # Layout Vertical (AJUSTE FINO 2.0 - Final Alignment)
    TITLE_Y = 0.90        # Baixou +0.02 (aprox 10% do gap anterior)
    ICON_Y = 0.72
    TEXT_Y = 0.57
    SUBTEXT_Y = 0.50
    
    # Margens Horizontais (Coordenadas de Figura 0-1)
    # Alinhamento estrito com Fig 1 (left=0.06, right=0.94)
    MARGIN_LEFT = 0.06
    MARGIN_RIGHT = 0.94
    
    # Posições X distribuídas dentro das margens
    X_POS = [0.12, 0.37, 0.62, 0.87] # O último em 0.87 permite que o texto não estoure 0.94.

    # Definição dos Passos
    steps = [
        {
            "icon": "db_icon.png", "zoom": 0.45,
            "title": "FONTE DE DADOS", 
            "desc": "CVM / B3\n(Dados Públicos)",
        },
        {
            "icon": "pdf_icon.png", "zoom": 0.45,
            "title": "INPUT NÃO ESTRUTURADO", 
            "desc": "DFP e Notas Explicativas\n(PDF / Texto)",
        },
        {
            "icon": "ai_icon.png", "zoom": 0.45,
            "title": "MOTOR LLM AI", 
            "desc": "Google Gemini 1.5 Pro\n(Information Extraction)",
        },
        {
            "icon": "csv_icon.png", "zoom": 0.45,
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
                ha='center', va='top', fontsize=10, fontweight='bold', 
                color=COLORS['primary'])
        
        ax.text(x, SUBTEXT_Y, step["desc"], 
                ha='center', va='top', fontsize=9.5, color=COLORS['text'],
                linespacing=1.5)

    # Desenhar Setas Conectores (Escuras e visíveis)
    ARROW_Y = ICON_Y
    arrow_labels = ["Coleta Automática", "Prompt Engineering", "Parsing & Validação"]
    for i in range(len(steps) - 1):
        x_start = X_POS[i] + 0.08
        x_end = X_POS[i+1] - 0.08
        center_x = (x_start + x_end) / 2
        
        ax.annotate("", xy=(x_end, ARROW_Y), xytext=(x_start, ARROW_Y),
                    arrowprops=dict(arrowstyle="->", color=COLORS['accent_line'], lw=1.5, 
                                  shrinkA=5, shrinkB=5))
        
        ax.text(center_x, ARROW_Y + 0.05, arrow_labels[i],
                ha='center', va='bottom', fontsize=9, style='italic',
                color=COLORS['text'], backgroundcolor='white')

    # Destaque LLM
    rect_y = 0.42
    rect = mpatches.FancyBboxPatch((0.50, rect_y), 0.24, 0.45,
                                   boxstyle="round,pad=0.02,rounding_size=0.04",
                                   facecolor='#f3e5f5', edgecolor='#8e44ad',
                                   linewidth=1.2, linestyle='--', zorder=0, alpha=0.4)
    ax.add_patch(rect)
    ax.text(0.62, rect_y + 0.43, "Núcleo de Processamento", ha='center', va='bottom', 
            fontsize=9, color='#4a148c', fontweight='bold') 
    
    # Prompt Text
    prompt_text = (
        r"$\bf{Prompt\ System:}$ 'Você é um especialista financeiro...'" + "\n"
        r"$\bf{Task:}$ 'Extraia da Nota Explicativa:'" + "\n"
        r" - Taxa de Juros (Kd)" + "\n"
        r" - Indexador (CDI, IPCA)" + "\n"
        r" - Moeda / Prazos" + "\n"
        r"$\bf{Output:}$ JSON"
    )
    
    # Subir Box Prompt ~5% (de 0.30 para 0.34)
    ax.annotate(prompt_text,
                xy=(X_POS[2], rect_y), xytext=(X_POS[2], 0.34), # Subiu
                arrowprops=dict(arrowstyle='->', color='#2c3e50', connectionstyle="arc3"),
                ha='left', va='top', fontsize=7.5, color=COLORS['text'], family='monospace',
                bbox=dict(boxstyle="round,pad=0.3", fc="#ffffff", ec="#2c3e50", alpha=1.0))
    
    # Nota Metodológica
    # Linha divisória alinhada com Fig 1 (0.06 -> 0.94)
    line_y = 0.18 
    line = mlines.Line2D([MARGIN_LEFT, MARGIN_RIGHT], [line_y, line_y], 
                         color='#2c3e50', linewidth=1)
    ax.add_line(line)
    
    justificativa_note = (
        r"$\bf{Nota\ (Eficiência\ Computacional):}$ A extração manual de dados de dívida em Notas Explicativas é complexa "
        r"devido à falta de padronização." + "\n"
        r"O uso do LLM (Gemini 1.5 Pro) automatizou a leitura, reduzindo o tempo médio de coleta de $\approx$20 min/doc (manual) "
        r"para <30 seg/doc." + "\n" 
        r"A validação humana atuou apenas por amostragem, assegurando integridade para a regressão."
    )
    
    # Texto com wrap alinhado no limite 0.94 (agora com quebra manual)
    txt = ax.text(MARGIN_LEFT, line_y - 0.02, justificativa_note, 
            ha='left', va='top', fontsize=9, color=COLORS['text'],
            linespacing=1.4) # wrap=True removido pois estamos controlando manualmente
    
    # Título Geral
    fig.suptitle('Figura 1: Arquitetura do Pipeline de Dados e Ganho de Eficiência via LLM',
                 fontsize=12, fontweight='bold', color='#000000', y=TITLE_Y)

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
    
    output_path = FIGURES_DIR / "fig01_llm_pipeline.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    
    print(f"✓ Figura salva em: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
