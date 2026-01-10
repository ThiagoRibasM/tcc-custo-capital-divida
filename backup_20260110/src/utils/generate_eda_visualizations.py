#!/usr/bin/env python3
"""
Pipeline completo de Análise Exploratória de Dados (EDA) com visualizações profissionais.
Gera 40 figuras em PNG de alta resolução para análise da variável resposta (Kd ponderado).
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, FIGURES_DIR, PROJECT_ROOT

# Configurações de estilo
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Garante que o diretório existe
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def save_figure(fig, filename, figsize=(10, 6)):
    """Salva figura com configurações padronizadas."""
    fig.set_size_inches(figsize)
    filepath = FIGURES_DIR / filename
    fig.savefig(filepath, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  ✅ {filename}")


def load_data():
    """Carrega dados do CSV."""
    df = pd.read_csv(CONSOLIDATED_PATH / "kd_ponderado_por_empresa.csv")
    print(f"📖 Dados carregados: {len(df)} empresas")
    return df


# ============================================================================
# 1. ANÁLISE DESCRITIVA BÁSICA (01-05)
# ============================================================================

def generate_basic_descriptive(df):
    """Gera visualizações 01-05: Análise descritiva básica."""
    print("\n📊 1. Análise Descritiva Básica (01-05)")
    
    # 01: Histograma
    fig, ax = plt.subplots()
    ax.hist(df['Kd_Ponderado'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax.axvline(df['Kd_Ponderado'].mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {df["Kd_Ponderado"].mean():.2f}%')
    ax.axvline(df['Kd_Ponderado'].median(), color='green', linestyle='--', linewidth=2, label=f'Mediana: {df["Kd_Ponderado"].median():.2f}%')
    ax.set_xlabel('Kd Ponderado (% a.a.)')
    ax.set_ylabel('Frequência')
    ax.set_title('01 - Distribuição de Kd Ponderado (Histograma)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '01_distribuicao_kd_ponderado_histograma.png')
    
    # 02: Boxplot
    fig, ax = plt.subplots()
    bp = ax.boxplot(df['Kd_Ponderado'], vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('02 - Distribuição de Kd Ponderado (Boxplot)')
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '02_distribuicao_kd_ponderado_boxplot.png')
    
    # 03: Violin plot
    fig, ax = plt.subplots()
    parts = ax.violinplot([df['Kd_Ponderado']], positions=[0], showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor('lightcoral')
        pc.set_alpha(0.7)
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_xticks([0])
    ax.set_xticklabels(['Kd Ponderado'])
    ax.set_title('03 - Distribuição de Kd Ponderado (Violin Plot)')
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '03_distribuicao_kd_ponderado_violino.png')
    
    # 04: Tabela de estatísticas descritivas
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('tight')
    ax.axis('off')
    stats_data = df['Kd_Ponderado'].describe()
    stats_data['IQR'] = stats_data['75%'] - stats_data['25%']
    stats_data['CV'] = (stats_data['std'] / stats_data['mean']) * 100  # Coeficiente de variação
    table_data = [[f"{val:.2f}" if isinstance(val, (int, float)) else str(val) for val in stats_data.values]]
    table = ax.table(cellText=table_data, 
                     colLabels=[f"{k}" for k in stats_data.index],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    ax.set_title('04 - Estatísticas Descritivas de Kd Ponderado', pad=20, fontsize=14, fontweight='bold')
    save_figure(fig, '04_estatisticas_descritivas_tabela.png', figsize=(10, 4))
    
    # 05: Q-Q plot
    fig, ax = plt.subplots()
    stats.probplot(df['Kd_Ponderado'], dist="norm", plot=ax)
    ax.set_title('05 - Q-Q Plot: Normalidade de Kd Ponderado')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '05_distribuicao_kd_ponderado_qqplot.png')


# ============================================================================
# 2. ANÁLISE DEMOGRÁFICA (06-12)
# ============================================================================

def generate_demographic_analysis(df):
    """Gera visualizações 06-12: Análise demográfica."""
    print("\n👥 2. Análise Demográfica (06-12)")
    
    # 06: Distribuição por faixas de Kd
    faixas = [0, 5, 8, 12, 16, 20, 30, 50, float('inf')]
    labels = ['< 5%', '5-8%', '8-12%', '12-16%', '16-20%', '20-30%', '30-50%', '> 50%']
    df['Faixa_Kd'] = pd.cut(df['Kd_Ponderado'], bins=faixas, labels=labels, right=False)
    
    fig, ax = plt.subplots()
    counts = df['Faixa_Kd'].value_counts().sort_index()
    bars = ax.bar(range(len(counts)), counts.values, color='steelblue', edgecolor='black', alpha=0.7)
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(counts.index, rotation=45, ha='right')
    ax.set_ylabel('Quantidade de Empresas')
    ax.set_xlabel('Faixa de Kd Ponderado (% a.a.)')
    ax.set_title('06 - Distribuição de Empresas por Faixa de Kd')
    ax.grid(True, alpha=0.3, axis='y')
    for i, (bar, val) in enumerate(zip(bars, counts.values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(val), ha='center', va='bottom', fontweight='bold')
    save_figure(fig, '06_distribuicao_empresas_por_faixa_kd.png')
    
    # 07: Scatter Kd vs Valor Consolidado
    fig, ax = plt.subplots()
    scatter = ax.scatter(df['Valor_Consolidado_Media'], df['Kd_Ponderado'], 
                        alpha=0.6, s=60, c=df['Total_Financiamentos'], 
                        cmap='viridis', edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Valor Consolidado Médio (R$)')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('07 - Kd Ponderado vs Valor Consolidado Médio')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Total de Financiamentos')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '07_kd_vs_valor_consolidado_scatter.png')
    
    # 08: Kd vs Total de Financiamentos
    fig, ax = plt.subplots()
    scatter = ax.scatter(df['Total_Financiamentos'], df['Kd_Ponderado'], 
                        alpha=0.6, s=60, c=df['Valor_Consolidado_Media'], 
                        cmap='plasma', edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Total de Financiamentos')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('08 - Kd Ponderado vs Total de Financiamentos')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Valor Consolidado Médio (R$)')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '08_kd_vs_total_financiamentos.png')
    
    # 09: Top 20 empresas com maior Kd
    top20_maior = df.nlargest(20, 'Kd_Ponderado')
    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(range(len(top20_maior)), top20_maior['Kd_Ponderado'], color='crimson', edgecolor='black', alpha=0.7)
    ax.set_yticks(range(len(top20_maior)))
    ax.set_yticklabels([name[:40] for name in top20_maior['Empresa']], fontsize=8)
    ax.set_xlabel('Kd Ponderado (% a.a.)')
    ax.set_title('09 - Top 20 Empresas com Maior Kd Ponderado')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    for i, (bar, val) in enumerate(zip(bars, top20_maior['Kd_Ponderado'])):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                f'{val:.2f}%', ha='left', va='center', fontsize=8)
    save_figure(fig, '09_top_20_empresas_kd_maior.png', figsize=(10, 8))
    
    # 10: Top 20 empresas com menor Kd
    top20_menor = df.nsmallest(20, 'Kd_Ponderado')
    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(range(len(top20_menor)), top20_menor['Kd_Ponderado'], color='lightgreen', edgecolor='black', alpha=0.7)
    ax.set_yticks(range(len(top20_menor)))
    ax.set_yticklabels([name[:40] for name in top20_menor['Empresa']], fontsize=8)
    ax.set_xlabel('Kd Ponderado (% a.a.)')
    ax.set_title('10 - Top 20 Empresas com Menor Kd Ponderado')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    for i, (bar, val) in enumerate(zip(bars, top20_menor['Kd_Ponderado'])):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{val:.2f}%', ha='left', va='center', fontsize=8)
    save_figure(fig, '10_top_20_empresas_kd_menor.png', figsize=(10, 8))
    
    # 11: Distribuição de indexadores únicos
    fig, ax = plt.subplots()
    ax.hist(df['Indexadores_Unicos'], bins=range(1, df['Indexadores_Unicos'].max()+2), 
           edgecolor='black', alpha=0.7, color='mediumpurple')
    ax.set_xlabel('Quantidade de Indexadores Únicos')
    ax.set_ylabel('Frequência')
    ax.set_title('11 - Distribuição de Indexadores Únicos por Empresa')
    ax.set_xticks(range(1, df['Indexadores_Unicos'].max()+1))
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '11_distribuicao_indexadores_unicos.png')
    
    # 12: Distribuição de tipos de financiamento únicos
    fig, ax = plt.subplots()
    ax.hist(df['Tipos_Financiamento_Unicos'], bins=range(1, df['Tipos_Financiamento_Unicos'].max()+2), 
           edgecolor='black', alpha=0.7, color='orange')
    ax.set_xlabel('Quantidade de Tipos de Financiamento Únicos')
    ax.set_ylabel('Frequência')
    ax.set_title('12 - Distribuição de Tipos de Financiamento Únicos por Empresa')
    ax.set_xticks(range(1, min(df['Tipos_Financiamento_Unicos'].max()+1, 20)))
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '12_distribuicao_tipos_financiamento_unicos.png')


# ============================================================================
# 3. ANÁLISE DE HETEROGENEIDADE (13-16)
# ============================================================================

def generate_heterogeneity_analysis(df):
    """Gera visualizações 13-16: Análise de heterogeneidade."""
    print("\n📊 3. Análise de Heterogeneidade (13-16)")
    
    # 13: Kd ponderado vs médio simples
    fig, ax = plt.subplots()
    scatter = ax.scatter(df['Kd_Medio_Simples'], df['Kd_Ponderado'], 
                        alpha=0.6, s=60, c=df['Valor_Consolidado_Total'], 
                        cmap='coolwarm', edgecolors='black', linewidth=0.5)
    # Linha de referência y=x
    min_val = min(df['Kd_Medio_Simples'].min(), df['Kd_Ponderado'].min())
    max_val = max(df['Kd_Medio_Simples'].max(), df['Kd_Ponderado'].max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='y=x (sem diferença)')
    ax.set_xlabel('Kd Médio Simples (% a.a.)')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('13 - Kd Ponderado vs Kd Médio Simples')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Valor Consolidado Total (R$)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '13_kd_ponderado_vs_kd_medio_simples.png')
    
    # 14: Heterogeneidade (desvio padrão)
    df_valid_std = df[df['Kd_Desvio_Padrao'].notna()].copy()
    if len(df_valid_std) > 0:
        fig, ax = plt.subplots()
        scatter = ax.scatter(df_valid_std['Kd_Ponderado'], df_valid_std['Kd_Desvio_Padrao'], 
                            alpha=0.6, s=60, c=df_valid_std['Total_Financiamentos'], 
                            cmap='YlOrRd', edgecolors='black', linewidth=0.5)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_ylabel('Desvio Padrão do Kd (% a.a.)')
        ax.set_title('14 - Heterogeneidade: Kd Ponderado vs Desvio Padrão')
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Total de Financiamentos')
        ax.grid(True, alpha=0.3)
        save_figure(fig, '14_heterogeneidade_kd_desvio_padrao.png')
    
    # 15: Range de Kd (min vs max)
    fig, ax = plt.subplots()
    for idx, row in df.iterrows():
        if pd.notna(row['Kd_Min']) and pd.notna(row['Kd_Max']):
            ax.plot([row['Kd_Min'], row['Kd_Max']], [idx, idx], 
                   'o-', alpha=0.5, linewidth=1, markersize=3)
    ax.set_xlabel('Kd (% a.a.)')
    ax.set_ylabel('Empresa (índice)')
    ax.set_title('15 - Range de Kd (Mínimo vs Máximo) por Empresa')
    ax.grid(True, alpha=0.3, axis='x')
    save_figure(fig, '15_range_kd_min_max.png', figsize=(10, 12))
    
    # 16: Correlação Kd ponderado vs desvio padrão
    df_valid_std = df[df['Kd_Desvio_Padrao'].notna()].copy()
    if len(df_valid_std) > 0:
        corr = df_valid_std['Kd_Ponderado'].corr(df_valid_std['Kd_Desvio_Padrao'])
        fig, ax = plt.subplots()
        ax.scatter(df_valid_std['Kd_Ponderado'], df_valid_std['Kd_Desvio_Padrao'], 
                  alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
        # Linha de tendência
        z = np.polyfit(df_valid_std['Kd_Ponderado'], df_valid_std['Kd_Desvio_Padrao'], 1)
        p = np.poly1d(z)
        ax.plot(df_valid_std['Kd_Ponderado'], p(df_valid_std['Kd_Ponderado']), 
               "r--", alpha=0.8, linewidth=2, label=f'Tendência (r={corr:.3f})')
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_ylabel('Desvio Padrão do Kd (% a.a.)')
        ax.set_title(f'16 - Correlação: Kd Ponderado vs Desvio Padrão (r={corr:.3f})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        save_figure(fig, '16_correlacao_kd_ponderado_desvio.png')


# ============================================================================
# 4. ANÁLISE DE VALOR CONSOLIDADO (17-20)
# ============================================================================

def generate_value_analysis(df):
    """Gera visualizações 17-20: Análise de valor consolidado."""
    print("\n💰 4. Análise de Valor Consolidado (17-20)")
    
    # 17: Histograma do valor consolidado
    fig, ax = plt.subplots()
    ax.hist(df['Valor_Consolidado_Media'], bins=30, edgecolor='black', alpha=0.7, color='teal')
    ax.set_xlabel('Valor Consolidado Médio (R$)')
    ax.set_ylabel('Frequência')
    ax.set_title('17 - Distribuição do Valor Consolidado Médio')
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '17_distribuicao_valor_consolidado_histograma.png')
    
    # 18: Scatter com escala logarítmica
    fig, ax = plt.subplots()
    scatter = ax.scatter(df['Valor_Consolidado_Media'], df['Kd_Ponderado'], 
                        alpha=0.6, s=60, c=df['Total_Financiamentos'], 
                        cmap='viridis', edgecolors='black', linewidth=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('Valor Consolidado Médio (R$) - Escala Logarítmica')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('18 - Kd Ponderado vs Valor Consolidado (Escala Log)')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Total de Financiamentos')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '18_kd_vs_valor_consolidado_log.png')
    
    # 19: Valor consolidado total vs Kd
    fig, ax = plt.subplots()
    scatter = ax.scatter(df['Valor_Consolidado_Total'], df['Kd_Ponderado'], 
                        alpha=0.6, s=60, c=df['Total_Financiamentos'], 
                        cmap='plasma', edgecolors='black', linewidth=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('Valor Consolidado Total (R$) - Escala Logarítmica')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('19 - Valor Consolidado Total vs Kd Ponderado')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Total de Financiamentos')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '19_valor_consolidado_total_vs_kd.png')
    
    # 20: Distribuição de valor por faixa de Kd
    fig, ax = plt.subplots()
    df['Faixa_Kd'] = pd.cut(df['Kd_Ponderado'], bins=[0, 5, 8, 12, 16, 20, 30, 50, float('inf')], 
                           labels=['< 5%', '5-8%', '8-12%', '12-16%', '16-20%', '20-30%', '30-50%', '> 50%'], 
                           right=False)
    box_data = [df[df['Faixa_Kd'] == faixa]['Valor_Consolidado_Media'].values 
                for faixa in df['Faixa_Kd'].cat.categories if len(df[df['Faixa_Kd'] == faixa]) > 0]
    labels = [faixa for faixa in df['Faixa_Kd'].cat.categories if len(df[df['Faixa_Kd'] == faixa]) > 0]
    bp = ax.boxplot(box_data, labels=labels, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)
    ax.set_yscale('log')
    ax.set_ylabel('Valor Consolidado Médio (R$) - Escala Log')
    ax.set_xlabel('Faixa de Kd Ponderado (% a.a.)')
    ax.set_title('20 - Distribuição de Valor Consolidado por Faixa de Kd')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '20_distribuicao_valor_por_faixa_kd.png')


# ============================================================================
# 5. ANÁLISE DE OUTLIERS E CASOS EXTREMOS (21-24)
# ============================================================================

def generate_outliers_analysis(df):
    """Gera visualizações 21-24: Análise de outliers."""
    print("\n⚠️  5. Análise de Outliers e Casos Extremos (21-24)")
    
    # 21: Boxplot com outliers destacados
    fig, ax = plt.subplots()
    bp = ax.boxplot(df['Kd_Ponderado'], vert=True, patch_artist=True, showfliers=True)
    bp['boxes'][0].set_facecolor('lightcoral')
    bp['boxes'][0].set_alpha(0.7)
    # Identifica outliers
    Q1 = df['Kd_Ponderado'].quantile(0.25)
    Q3 = df['Kd_Ponderado'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df[(df['Kd_Ponderado'] < Q1 - 1.5*IQR) | (df['Kd_Ponderado'] > Q3 + 1.5*IQR)]
    ax.scatter([1]*len(outliers), outliers['Kd_Ponderado'], 
              color='red', s=100, marker='x', zorder=10, label=f'Outliers (n={len(outliers)})')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('21 - Identificação de Outliers (Boxplot)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '21_identificacao_outliers_boxplot.png')
    
    # 22: Scatter com outliers identificados
    fig, ax = plt.subplots()
    normal = df[(df['Kd_Ponderado'] >= Q1 - 1.5*IQR) & (df['Kd_Ponderado'] <= Q3 + 1.5*IQR)]
    ax.scatter(normal['Valor_Consolidado_Media'], normal['Kd_Ponderado'], 
              alpha=0.6, s=60, color='blue', label='Normal', edgecolors='black', linewidth=0.5)
    ax.scatter(outliers['Valor_Consolidado_Media'], outliers['Kd_Ponderado'], 
              alpha=0.8, s=100, color='red', marker='x', linewidth=2, label=f'Outliers (n={len(outliers)})')
    ax.set_xscale('log')
    ax.set_xlabel('Valor Consolidado Médio (R$) - Escala Log')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('22 - Outliers de Kd Ponderado (Scatter Plot)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '22_outliers_kd_ponderado_scatter.png')
    
    # 23: Casos extremos Kd alto (>30%)
    kd_alto = df[df['Kd_Ponderado'] > 30].copy()
    if len(kd_alto) > 0:
        fig, ax = plt.subplots(figsize=(10, max(6, len(kd_alto)*0.3)))
        bars = ax.barh(range(len(kd_alto)), kd_alto['Kd_Ponderado'], color='crimson', edgecolor='black', alpha=0.7)
        ax.set_yticks(range(len(kd_alto)))
        ax.set_yticklabels([name[:50] for name in kd_alto['Empresa']], fontsize=8)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_title(f'23 - Casos Extremos: Kd Muito Alto (>30%) - {len(kd_alto)} empresas')
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        for i, (bar, val) in enumerate(zip(bars, kd_alto['Kd_Ponderado'])):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                   f'{val:.2f}%', ha='left', va='center', fontsize=8)
        save_figure(fig, '23_casos_extremos_kd_alto.png', figsize=(10, max(6, len(kd_alto)*0.3)))
    
    # 24: Casos extremos Kd baixo (<5%)
    kd_baixo = df[df['Kd_Ponderado'] < 5].copy()
    if len(kd_baixo) > 0:
        fig, ax = plt.subplots(figsize=(10, max(6, len(kd_baixo)*0.3)))
        bars = ax.barh(range(len(kd_baixo)), kd_baixo['Kd_Ponderado'], color='lightgreen', edgecolor='black', alpha=0.7)
        ax.set_yticks(range(len(kd_baixo)))
        ax.set_yticklabels([name[:50] for name in kd_baixo['Empresa']], fontsize=8)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_title(f'24 - Casos Extremos: Kd Muito Baixo (<5%) - {len(kd_baixo)} empresas')
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        for i, (bar, val) in enumerate(zip(bars, kd_baixo['Kd_Ponderado'])):
            ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2, 
                   f'{val:.2f}%', ha='left', va='center', fontsize=8)
        save_figure(fig, '24_casos_extremos_kd_baixo.png', figsize=(10, max(6, len(kd_baixo)*0.3)))


# ============================================================================
# 6. ANÁLISE DE INDEXADORES (25-28)
# ============================================================================

def generate_indexers_analysis(df):
    """Gera visualizações 25-28: Análise de indexadores."""
    print("\n📈 6. Análise de Indexadores (25-28)")
    
    # Extrai indexador principal de cada empresa
    df['Indexador_Principal'] = df['Indexadores_Usados'].str.split(',').str[0].str.strip()
    
    # 25: Distribuição por indexador principal
    indexador_counts = df['Indexador_Principal'].value_counts()
    fig, ax = plt.subplots()
    bars = ax.bar(range(len(indexador_counts)), indexador_counts.values, 
                 color='steelblue', edgecolor='black', alpha=0.7)
    ax.set_xticks(range(len(indexador_counts)))
    ax.set_xticklabels(indexador_counts.index, rotation=45, ha='right')
    ax.set_ylabel('Quantidade de Empresas')
    ax.set_xlabel('Indexador Principal')
    ax.set_title('25 - Distribuição de Empresas por Indexador Principal')
    ax.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, indexador_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
               str(val), ha='center', va='bottom', fontweight='bold')
    save_figure(fig, '25_distribuicao_por_indexador_principal.png')
    
    # 26: Kd vs quantidade de indexadores
    fig, ax = plt.subplots()
    scatter = ax.scatter(df['Indexadores_Unicos'], df['Kd_Ponderado'], 
                        alpha=0.6, s=60, c=df['Valor_Consolidado_Media'], 
                        cmap='viridis', edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Quantidade de Indexadores Únicos')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('26 - Kd Ponderado vs Quantidade de Indexadores Únicos')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Valor Consolidado Médio (R$)')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '26_kd_vs_quantidade_indexadores.png')
    
    # 27: Heatmap indexadores únicos vs Kd
    df_heatmap = df.groupby('Indexadores_Unicos')['Kd_Ponderado'].agg(['mean', 'count']).reset_index()
    df_heatmap = df_heatmap[df_heatmap['count'] >= 3]  # Apenas grupos com pelo menos 3 empresas
    if len(df_heatmap) > 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        pivot_data = df_heatmap.pivot_table(values='mean', index='Indexadores_Unicos', aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Kd Médio (%)'})
        ax.set_xlabel('')
        ax.set_ylabel('Indexadores Únicos')
        ax.set_title('27 - Heatmap: Kd Médio por Quantidade de Indexadores Únicos')
        save_figure(fig, '27_heatmap_indexadores_unicos_vs_kd.png')
    
    # 28: Boxplot comparativo por indexador principal
    indexadores_comuns = df['Indexador_Principal'].value_counts().head(5).index
    df_comparacao = df[df['Indexador_Principal'].isin(indexadores_comuns)]
    if len(df_comparacao) > 0:
        fig, ax = plt.subplots()
        box_data = [df_comparacao[df_comparacao['Indexador_Principal'] == idx]['Kd_Ponderado'].values 
                   for idx in indexadores_comuns]
        bp = ax.boxplot(box_data, labels=indexadores_comuns, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_xlabel('Indexador Principal')
        ax.set_title('28 - Comparação de Kd por Indexador Principal (Top 5)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        save_figure(fig, '28_comparacao_indexadores_boxplot.png')


# ============================================================================
# 7. ANÁLISE DE TIPOS DE FINANCIAMENTO (29-31)
# ============================================================================

def generate_financing_types_analysis(df):
    """Gera visualizações 29-31: Análise de tipos de financiamento."""
    print("\n💳 7. Análise de Tipos de Financiamento (29-31)")
    
    # 29: Kd vs tipos de financiamento únicos
    fig, ax = plt.subplots()
    scatter = ax.scatter(df['Tipos_Financiamento_Unicos'], df['Kd_Ponderado'], 
                        alpha=0.6, s=60, c=df['Valor_Consolidado_Media'], 
                        cmap='plasma', edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Quantidade de Tipos de Financiamento Únicos')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('29 - Kd Ponderado vs Tipos de Financiamento Únicos')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Valor Consolidado Médio (R$)')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '29_kd_vs_tipos_financiamento_unicos.png')
    
    # 30: Distribuição de tipos de financiamento
    fig, ax = plt.subplots()
    ax.hist(df['Tipos_Financiamento_Unicos'], bins=range(1, min(df['Tipos_Financiamento_Unicos'].max()+2, 20)), 
           edgecolor='black', alpha=0.7, color='orange')
    ax.set_xlabel('Quantidade de Tipos de Financiamento Únicos')
    ax.set_ylabel('Frequência')
    ax.set_title('30 - Distribuição de Tipos de Financiamento Únicos')
    ax.set_xticks(range(1, min(df['Tipos_Financiamento_Unicos'].max()+1, 20)))
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '30_distribuicao_tipos_financiamento.png')
    
    # 31: Correlação tipos vs Kd
    corr = df['Tipos_Financiamento_Unicos'].corr(df['Kd_Ponderado'])
    fig, ax = plt.subplots()
    ax.scatter(df['Tipos_Financiamento_Unicos'], df['Kd_Ponderado'], 
              alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
    # Linha de tendência
    z = np.polyfit(df['Tipos_Financiamento_Unicos'], df['Kd_Ponderado'], 1)
    p = np.poly1d(z)
    ax.plot(df['Tipos_Financiamento_Unicos'], p(df['Tipos_Financiamento_Unicos']), 
           "r--", alpha=0.8, linewidth=2, label=f'Tendência (r={corr:.3f})')
    ax.set_xlabel('Tipos de Financiamento Únicos')
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title(f'31 - Correlação: Tipos de Financiamento vs Kd (r={corr:.3f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '31_correlacao_tipos_vs_kd.png')


# ============================================================================
# 8. MATRIZ DE CORRELAÇÃO (32-33)
# ============================================================================

def generate_correlation_analysis(df):
    """Gera visualizações 32-33: Matriz de correlação."""
    print("\n🔗 8. Matriz de Correlação (32-33)")
    
    # Seleciona variáveis numéricas
    numeric_cols = ['Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos',
                   'Valor_Consolidado_Total', 'Kd_Medio_Simples', 'Kd_Desvio_Padrao',
                   'Kd_Min', 'Kd_Max', 'Indexadores_Unicos', 'Tipos_Financiamento_Unicos']
    numeric_cols = [col for col in numeric_cols if col in df.columns]
    df_numeric = df[numeric_cols].select_dtypes(include=[np.number])
    
    # 32: Matriz de correlação completa
    corr_matrix = df_numeric.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
               square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('32 - Matriz de Correlação Completa', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    save_figure(fig, '32_matriz_correlacao_completa.png', figsize=(12, 10))
    
    # 33: Correlação de Kd com principais variáveis
    kd_correlations = df_numeric.corr()['Kd_Ponderado'].drop('Kd_Ponderado').sort_values(ascending=False)
    fig, ax = plt.subplots()
    colors = ['red' if x < 0 else 'green' for x in kd_correlations.values]
    bars = ax.barh(range(len(kd_correlations)), kd_correlations.values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_yticks(range(len(kd_correlations)))
    ax.set_yticklabels(kd_correlations.index)
    ax.set_xlabel('Correlação com Kd Ponderado')
    ax.set_title('33 - Correlação de Kd Ponderado com Principais Variáveis')
    ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='x')
    for i, (bar, val) in enumerate(zip(bars, kd_correlations.values)):
        ax.text(val + 0.01 if val >= 0 else val - 0.01, bar.get_y() + bar.get_height()/2, 
               f'{val:.3f}', ha='left' if val >= 0 else 'right', va='center', fontweight='bold')
    save_figure(fig, '33_correlacao_kd_principais_variaveis.png')


# ============================================================================
# 9. ANÁLISE DE AGRUPAMENTOS (34-36)
# ============================================================================

def generate_clustering_analysis(df):
    """Gera visualizações 34-36: Análise de agrupamentos."""
    print("\n🔍 9. Análise de Agrupamentos (34-36)")
    
    # Prepara dados para clustering
    features = ['Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos']
    df_cluster = df[features].dropna()
    
    if len(df_cluster) > 3:
        # Normaliza dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_cluster)
        
        # K-means clustering
        n_clusters = min(5, len(df_cluster) // 3)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        df_cluster['Cluster'] = clusters
        
        # 34: Clustering Kd, Valor, Financiamentos
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(df_cluster['Valor_Consolidado_Media'], df_cluster['Kd_Ponderado'],
                           c=df_cluster['Cluster'], cmap='tab10', s=df_cluster['Total_Financiamentos']*10,
                           alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xscale('log')
        ax.set_xlabel('Valor Consolidado Médio (R$) - Escala Log')
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_title(f'34 - Clustering: Kd, Valor e Financiamentos (K-means, k={n_clusters})')
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Cluster')
        ax.grid(True, alpha=0.3)
        save_figure(fig, '34_clustering_kd_valor_financiamentos.png')
        
        # 35: Dendrograma
        if len(df_cluster) <= 50:  # Dendrograma só para amostras menores
            sample_size = min(30, len(df_cluster))
            df_sample = df_cluster.sample(n=sample_size, random_state=42)
            X_sample = scaler.transform(df_sample[features])
            linkage_matrix = linkage(X_sample, method='ward')
            fig, ax = plt.subplots(figsize=(12, 8))
            dendrogram(linkage_matrix, labels=df_sample.index.tolist(), ax=ax, leaf_rotation=90)
            ax.set_title(f'35 - Dendrograma: Empresas Similares (amostra de {sample_size})')
            ax.set_xlabel('Empresa (índice)')
            ax.set_ylabel('Distância')
            plt.tight_layout()
            save_figure(fig, '35_dendrograma_empresas_similares.png', figsize=(14, 10))
    
    # 36: Heatmap top 30 empresas
    top30 = df.nlargest(30, 'Valor_Consolidado_Total')
    heatmap_data = top30[['Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos',
                         'Kd_Medio_Simples', 'Indexadores_Unicos', 'Tipos_Financiamento_Unicos']].T
    heatmap_data.columns = [name[:30] for name in top30['Empresa']]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(heatmap_data, annot=False, fmt='.1f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Valor Normalizado'})
    ax.set_title('36 - Heatmap: Top 30 Empresas por Valor Consolidado Total')
    ax.set_ylabel('Variável')
    plt.tight_layout()
    save_figure(fig, '36_heatmap_empresas_top30.png', figsize=(16, 8))


# ============================================================================
# 10. ANÁLISE ESTATÍSTICA AVANÇADA (37-40)
# ============================================================================

def generate_advanced_statistics(df):
    """Gera visualizações 37-40: Análise estatística avançada."""
    print("\n📐 10. Análise Estatística Avançada (37-40)")
    
    # 37: Teste de normalidade
    from scipy.stats import shapiro, normaltest
    stat_sw, p_sw = shapiro(df['Kd_Ponderado'].sample(min(5000, len(df)), random_state=42))
    stat_da, p_da = normaltest(df['Kd_Ponderado'])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Q-Q plot
    stats.probplot(df['Kd_Ponderado'], dist="norm", plot=ax1)
    ax1.set_title(f'Q-Q Plot\nShapiro-Wilk: p={p_sw:.4f}')
    ax1.grid(True, alpha=0.3)
    
    # Histograma com curva normal
    ax2.hist(df['Kd_Ponderado'], bins=30, density=True, alpha=0.7, color='steelblue', edgecolor='black')
    mu, sigma = df['Kd_Ponderado'].mean(), df['Kd_Ponderado'].std()
    x = np.linspace(df['Kd_Ponderado'].min(), df['Kd_Ponderado'].max(), 100)
    ax2.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, label=f'Normal(μ={mu:.2f}, σ={sigma:.2f})')
    ax2.set_xlabel('Kd Ponderado (% a.a.)')
    ax2.set_ylabel('Densidade')
    ax2.set_title(f'Distribuição vs Normal\nD\'Agostino: p={p_da:.4f}')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle('37 - Teste de Normalidade de Kd Ponderado', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_figure(fig, '37_teste_normalidade_kd.png', figsize=(14, 6))
    
    # 38: Distribuição do log de Kd
    df_log = df[df['Kd_Ponderado'] > 0].copy()
    df_log['Log_Kd'] = np.log(df_log['Kd_Ponderado'])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.hist(df_log['Kd_Ponderado'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.set_xlabel('Kd Ponderado (% a.a.)')
    ax1.set_ylabel('Frequência')
    ax1.set_title('Distribuição Original')
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax2.hist(df_log['Log_Kd'], bins=30, edgecolor='black', alpha=0.7, color='lightcoral')
    ax2.set_xlabel('Log(Kd Ponderado)')
    ax2.set_ylabel('Frequência')
    ax2.set_title('Distribuição Logarítmica')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('38 - Transformação Logarítmica de Kd Ponderado', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_figure(fig, '38_distribuicao_log_kd.png', figsize=(14, 6))
    
    # 39: Análise de resíduos (regressão simples)
    from sklearn.linear_model import LinearRegression
    X = df[['Valor_Consolidado_Media']].values
    y = df['Kd_Ponderado'].values
    X_log = np.log1p(X)  # Log(1+x) para evitar log(0)
    
    model = LinearRegression()
    model.fit(X_log, y)
    y_pred = model.predict(X_log)
    residuals = y - y_pred
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.scatter(y_pred, residuals, alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
    ax1.axhline(0, color='red', linestyle='--', linewidth=2)
    ax1.set_xlabel('Valores Preditos')
    ax1.set_ylabel('Resíduos')
    ax1.set_title('Resíduos vs Valores Preditos')
    ax1.grid(True, alpha=0.3)
    
    ax2.hist(residuals, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax2.set_xlabel('Resíduos')
    ax2.set_ylabel('Frequência')
    ax2.set_title('Distribuição dos Resíduos')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('39 - Análise de Resíduos (Regressão: Kd ~ Log(Valor))', fontsize=14, fontweight='bold')
    plt.tight_layout()
    save_figure(fig, '39_analise_residuos_kd.png', figsize=(14, 6))
    
    # 40: Sumário estatístico completo
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = df[numeric_cols].describe().T
    summary['IQR'] = summary['75%'] - summary['25%']
    summary['CV'] = (summary['std'] / summary['mean']) * 100
    
    fig, ax = plt.subplots(figsize=(14, max(8, len(summary)*0.5)))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=[[f"{val:.2f}" if isinstance(val, (int, float)) and not np.isnan(val) else "-" 
                                for val in row] for row in summary.values],
                    rowLabels=summary.index,
                    colLabels=['Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max', 'IQR', 'CV'],
                    cellLoc='center',
                    loc='center',
                    bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    ax.set_title('40 - Sumário Estatístico Completo', pad=20, fontsize=16, fontweight='bold')
    save_figure(fig, '40_sumario_estatistico_completo.png', figsize=(16, max(10, len(summary)*0.6)))


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que executa todo o pipeline de EDA."""
    print("="*70)
    print("PIPELINE COMPLETO DE ANÁLISE EXPLORATÓRIA DE DADOS (EDA)")
    print("="*70)
    
    # Carrega dados
    df = load_data()
    
    # Executa todas as análises
    generate_basic_descriptive(df)
    generate_demographic_analysis(df)
    generate_heterogeneity_analysis(df)
    generate_value_analysis(df)
    generate_outliers_analysis(df)
    generate_indexers_analysis(df)
    generate_financing_types_analysis(df)
    generate_correlation_analysis(df)
    generate_clustering_analysis(df)
    generate_advanced_statistics(df)
    
    print("\n" + "="*70)
    print("✅ PIPELINE DE EDA CONCLUÍDO!")
    print(f"📁 Todas as figuras salvas em: {FIGURES_DIR}")
    print(f"📊 Total de figuras geradas: 40")
    print("="*70)


if __name__ == "__main__":
    main()

