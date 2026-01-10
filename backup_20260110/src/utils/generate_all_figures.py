#!/usr/bin/env python3
"""
Orquestrador de Pipelines de Figuras com Subplots Consolidados.
Agrupa gráficos relacionados em subplots temáticos para reduzir número de arquivos.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import glob
from scipy import stats
from scipy.stats import shapiro, anderson, normaltest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
import warnings
warnings.filterwarnings('ignore')

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import CONSOLIDATED_PATH, FIGURES_DIR

# Configurações de estilo
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 8

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


class FigureOrchestrator:
    """Orquestrador para gerar figuras consolidadas com subplots."""
    
    def __init__(self):
        self.figures_dir = FIGURES_DIR
        self.consolidated_path = CONSOLIDATED_PATH
        
    def save_consolidated_figure(self, fig, filename, figsize=(16, 12)):
        """Salva figura consolidada com configurações padronizadas."""
        fig.set_size_inches(figsize)
        filepath = self.figures_dir / filename
        fig.savefig(filepath, bbox_inches='tight', facecolor='white', edgecolor='none', dpi=300)
        plt.close(fig)
        print(f"  ✅ {filename}")
    
    def cleanup_old_figures(self):
        """Remove todas as figuras antigas (01-134)."""
        print("\n🧹 Limpando figuras antigas...")
        old_patterns = [
            '01_*.png', '02_*.png', '03_*.png', '04_*.png', '05_*.png',
            '06_*.png', '07_*.png', '08_*.png', '09_*.png', '10_*.png',
            '11_*.png', '12_*.png', '13_*.png', '14_*.png', '15_*.png',
            '16_*.png', '17_*.png', '18_*.png', '19_*.png', '20_*.png',
            '21_*.png', '22_*.png', '23_*.png', '24_*.png', '25_*.png',
            '26_*.png', '27_*.png', '28_*.png', '29_*.png', '30_*.png',
            '31_*.png', '32_*.png', '33_*.png', '34_*.png', '35_*.png',
            '36_*.png', '37_*.png', '38_*.png', '39_*.png', '40_*.png',
            '50_*.png', '51_*.png', '52_*.png', '53_*.png', '54_*.png',
            '55_*.png', '56_*.png', '57_*.png', '58_*.png', '59_*.png',
            '60_*.png', '61_*.png', '62_*.png', '63_*.png', '64_*.png',
            '65_*.png', '66_*.png', '67_*.png', '68_*.png', '69_*.png',
            '70_*.png', '71_*.png', '72_*.png', '73_*.png', '74_*.png',
            '75_*.png', '76_*.png', '77_*.png', '78_*.png', '79_*.png',
            '80_*.png', '81_*.png', '82_*.png', '83_*.png', '84_*.png',
            '85_*.png', '86_*.png', '87_*.png', '88_*.png', '89_*.png',
            '90_*.png', '91_*.png', '92_*.png', '93_*.png', '94_*.png',
            '95_*.png', '96_*.png', '97_*.png', '98_*.png', '99_*.png',
            '100_*.png', '101_*.png', '102_*.png', '103_*.png', '104_*.png',
            '105_*.png', '106_*.png', '107_*.png', '108_*.png', '109_*.png',
            '110_*.png', '111_*.png', '112_*.png', '113_*.png', '114_*.png',
            '115_*.png', '116_*.png', '117_*.png', '118_*.png', '119_*.png',
            '120_*.png', '121_*.png', '122_*.png', '123_*.png', '124_*.png',
            '125_*.png', '126_*.png', '127_*.png', '128_*.png', '129_*.png',
            '130_*.png', '131_*.png', '132_*.png', '133_*.png', '134_*.png'
        ]
        
        deleted_count = 0
        for pattern in old_patterns:
            for filepath in self.figures_dir.glob(pattern):
                filepath.unlink()
                deleted_count += 1
        
        print(f"  ✅ {deleted_count} figuras antigas removidas")
    
    def load_eda_data(self):
        """Carrega dados para EDA."""
        df = pd.read_csv(self.consolidated_path / "kd_ponderado_por_empresa.csv")
        return df
    
    def load_regression_data(self):
        """Carrega dados para regressão."""
        df = pd.read_csv(self.consolidated_path / "indicadores_financeiros_completos.csv")
        y = df['Kd_Ponderado'].copy()
        exclude_cols = ['Empresa', 'Kd_Ponderado']
        X = df.drop(columns=[c for c in exclude_cols if c in df.columns])
        threshold = len(df) * 0.5
        X = X.loc[:, X.isnull().sum() < threshold]
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        X = X[numeric_cols]
        X = X.loc[:, X.var() > 0]
        return y, X, df
    
    def get_top_variables(self, X, y, n=9, method='correlation'):
        """Seleciona top variáveis por correlação."""
        data = pd.concat([y, X], axis=1).dropna()
        if len(data) < 5:
            return []
        y_clean = data[y.name]
        X_clean = data.drop(columns=[y.name])
        correlations = X_clean.corrwith(y_clean).abs().sort_values(ascending=False)
        return correlations.head(n).index.tolist()
    
    # ========================================================================
    # EDA FIGURES (01-08)
    # ========================================================================
    
    def generate_eda_figures(self):
        """Gera todas as figuras consolidadas de EDA."""
        print("\n" + "="*80)
        print("GERANDO FIGURAS EDA CONSOLIDADAS (01-08)")
        print("="*80)
        
        df = self.load_eda_data()
        kd = df['Kd_Ponderado'].dropna()
        
        # 01: Distribuição Kd
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Histograma com normal
        ax = axes[0]
        n, bins, patches = ax.hist(kd, bins=30, density=True, alpha=0.7, 
                                  color='steelblue', edgecolor='black')
        mu, sigma = kd.mean(), kd.std()
        x_norm = np.linspace(kd.min(), kd.max(), 100)
        y_norm = stats.norm.pdf(x_norm, mu, sigma)
        ax.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal (μ={mu:.2f}, σ={sigma:.2f})')
        ax.axvline(mu, color='red', linestyle='--', linewidth=2)
        ax.axvline(kd.median(), color='green', linestyle='--', linewidth=2)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_ylabel('Densidade')
        ax.set_title('Histograma com Curva Normal')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Boxplot
        ax = axes[1]
        bp = ax.boxplot(kd, vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_title('Boxplot')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Q-Q plot
        ax = axes[2]
        stats.probplot(kd, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot (Normalidade)')
        ax.grid(True, alpha=0.3)
        
        # Violin plot
        ax = axes[3]
        parts = ax.violinplot([kd], positions=[0], showmeans=True, showmedians=True)
        for pc in parts['bodies']:
            pc.set_facecolor('lightcoral')
            pc.set_alpha(0.7)
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_xticks([0])
        ax.set_xticklabels(['Kd Ponderado'])
        ax.set_title('Violin Plot')
        ax.grid(True, alpha=0.3, axis='y')
        
        fig.suptitle('01 - EDA: Distribuição de Kd Ponderado', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '01_eda_distribuicao_kd.png')
        
        # 02: Estatísticas Descritivas
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Tabela de estatísticas
        ax = axes[0]
        ax.axis('off')
        stats_desc = kd.describe()
        stats_data = [
            ['Estatística', 'Valor'],
            ['Média', f'{kd.mean():.4f}'],
            ['Mediana', f'{kd.median():.4f}'],
            ['Desvio Padrão', f'{kd.std():.4f}'],
            ['Mínimo', f'{kd.min():.4f}'],
            ['Máximo', f'{kd.max():.4f}'],
            ['Q1', f'{kd.quantile(0.25):.4f}'],
            ['Q3', f'{kd.quantile(0.75):.4f}'],
            ['IQR', f'{kd.quantile(0.75) - kd.quantile(0.25):.4f}']
        ]
        table = ax.table(cellText=stats_data[1:], colLabels=stats_data[0],
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax.set_title('Estatísticas Descritivas')
        
        # Gráfico de barras
        ax = axes[1]
        stats_names = ['Média', 'Mediana', 'Desvio\nPadrão']
        stats_values = [kd.mean(), kd.median(), kd.std()]
        bars = ax.bar(stats_names, stats_values, color=['steelblue', 'coral', 'lightgreen'])
        ax.set_ylabel('Valor')
        ax.set_title('Estatísticas Principais')
        ax.grid(True, alpha=0.3, axis='y')
        for bar, val in zip(bars, stats_values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9)
        
        # Assimetria e Curtose
        ax = axes[2]
        skewness = kd.skew()
        kurtosis = kd.kurtosis()
        ax.bar(['Assimetria', 'Curtose'], [skewness, kurtosis], 
              color=['purple', 'orange'], alpha=0.7)
        ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax.set_ylabel('Valor')
        ax.set_title('Assimetria e Curtose')
        ax.grid(True, alpha=0.3, axis='y')
        ax.text(0, skewness, f'{skewness:.3f}', ha='center', va='bottom', fontsize=9)
        ax.text(1, kurtosis, f'{kurtosis:.3f}', ha='center', va='bottom', fontsize=9)
        
        # Testes de normalidade
        ax = axes[3]
        ax.axis('off')
        shapiro_stat, shapiro_p = shapiro(kd)
        d_agostino_stat, d_agostino_p = normaltest(kd)
        test_results = [
            ['Teste', 'Estatística', 'p-value', 'Conclusão'],
            ['Shapiro-Wilk', f'{shapiro_stat:.4f}', f'{shapiro_p:.4f}',
             'Normal' if shapiro_p > 0.05 else 'Não Normal'],
            ["D'Agostino", f'{d_agostino_stat:.4f}', f'{d_agostino_p:.4f}',
             'Normal' if d_agostino_p > 0.05 else 'Não Normal']
        ]
        table = ax.table(cellText=test_results[1:], colLabels=test_results[0],
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        ax.set_title('Testes de Normalidade')
        
        fig.suptitle('02 - EDA: Estatísticas Descritivas de Kd', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '02_eda_estatisticas_kd.png')
        
        # 03: Outliers e Casos Extremos
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Boxplot com outliers
        ax = axes[0]
        bp = ax.boxplot(kd, vert=True, patch_artist=True, showfliers=True)
        bp['boxes'][0].set_facecolor('lightblue')
        Q1, Q3 = kd.quantile(0.25), kd.quantile(0.75)
        IQR = Q3 - Q1
        outliers = kd[(kd < Q1 - 1.5*IQR) | (kd > Q3 + 1.5*IQR)]
        if len(outliers) > 0:
            ax.scatter([1]*len(outliers), outliers, color='red', s=50, zorder=3)
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_title(f'Boxplot com Outliers (IQR: {len(outliers)})')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Scatter com outliers (Z-score)
        ax = axes[1]
        z_scores = np.abs(stats.zscore(kd))
        outliers_z = kd[z_scores > 3]
        ax.scatter(range(len(kd)), kd, alpha=0.6, s=30, color='steelblue')
        if len(outliers_z) > 0:
            outlier_indices = kd[z_scores > 3].index
            ax.scatter([list(kd.index).index(i) for i in outlier_indices], 
                      outliers_z, color='red', s=50, zorder=3, label=f'Outliers Z ({len(outliers_z)})')
        ax.set_xlabel('Índice')
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_title('Outliers (Z-score > 3)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Top empresas Kd alto
        ax = axes[2]
        top_high = df.nlargest(10, 'Kd_Ponderado')
        ax.barh(range(len(top_high)), top_high['Kd_Ponderado'], color='coral')
        ax.set_yticks(range(len(top_high)))
        ax.set_yticklabels([name[:30] for name in top_high['Empresa']], fontsize=8)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_title('Top 10 Empresas - Maior Kd')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Top empresas Kd baixo
        ax = axes[3]
        top_low = df.nsmallest(10, 'Kd_Ponderado')
        ax.barh(range(len(top_low)), top_low['Kd_Ponderado'], color='lightgreen')
        ax.set_yticks(range(len(top_low)))
        ax.set_yticklabels([name[:30] for name in top_low['Empresa']], fontsize=8)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_title('Top 10 Empresas - Menor Kd')
        ax.grid(True, alpha=0.3, axis='x')
        
        fig.suptitle('03 - EDA: Outliers e Casos Extremos', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '03_eda_outliers_kd.png')
        
        # 04: Heterogeneidade da Dívida
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Kd ponderado vs médio simples
        if 'Kd_Medio_Simples' in df.columns:
            ax = axes[0]
            ax.scatter(df['Kd_Medio_Simples'], df['Kd_Ponderado'], alpha=0.6, s=50)
            min_val = min(df['Kd_Medio_Simples'].min(), df['Kd_Ponderado'].min())
            max_val = max(df['Kd_Medio_Simples'].max(), df['Kd_Ponderado'].max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
            ax.set_xlabel('Kd Médio Simples')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Kd Ponderado vs Médio Simples')
            ax.grid(True, alpha=0.3)
        
        # Heterogeneidade (desvio padrão)
        if 'Kd_Desvio_Padrao' in df.columns:
            ax = axes[1]
            ax.scatter(df['Kd_Desvio_Padrao'], df['Kd_Ponderado'], alpha=0.6, s=50, color='coral')
            ax.set_xlabel('Desvio Padrão do Kd')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Heterogeneidade (Desvio Padrão)')
            ax.grid(True, alpha=0.3)
        
        # Range Kd (min vs max)
        if 'Kd_Min' in df.columns and 'Kd_Max' in df.columns:
            ax = axes[2]
            ax.scatter(df['Kd_Min'], df['Kd_Max'], alpha=0.6, s=50, color='lightgreen')
            min_val = min(df['Kd_Min'].min(), df['Kd_Max'].min())
            max_val = max(df['Kd_Min'].max(), df['Kd_Max'].max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
            ax.set_xlabel('Kd Mínimo')
            ax.set_ylabel('Kd Máximo')
            ax.set_title('Range Kd (Min vs Max)')
            ax.grid(True, alpha=0.3)
        
        # Correlação Kd vs desvio
        if 'Kd_Desvio_Padrao' in df.columns:
            ax = axes[3]
            corr = df[['Kd_Ponderado', 'Kd_Desvio_Padrao']].corr().iloc[0, 1]
            ax.scatter(df['Kd_Desvio_Padrao'], df['Kd_Ponderado'], alpha=0.6, s=50, color='purple')
            ax.set_xlabel('Desvio Padrão do Kd')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title(f'Correlação Kd vs Desvio (r={corr:.3f})')
            ax.grid(True, alpha=0.3)
        
        fig.suptitle('04 - EDA: Heterogeneidade da Dívida', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '04_eda_heterogeneidade.png')
        
        # 05: Indexadores e Tipos
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Distribuição indexadores únicos
        if 'Indexadores_Unicos' in df.columns:
            ax = axes[0]
            ax.hist(df['Indexadores_Unicos'], bins=range(1, int(df['Indexadores_Unicos'].max())+2), 
                   alpha=0.7, color='steelblue', edgecolor='black')
            ax.set_xlabel('Indexadores Únicos')
            ax.set_ylabel('Frequência')
            ax.set_title('Distribuição de Indexadores Únicos')
            ax.grid(True, alpha=0.3, axis='y')
        
        # Distribuição tipos financiamento
        if 'Tipos_Financiamento_Unicos' in df.columns:
            ax = axes[1]
            ax.hist(df['Tipos_Financiamento_Unicos'], 
                   bins=range(1, int(df['Tipos_Financiamento_Unicos'].max())+2),
                   alpha=0.7, color='coral', edgecolor='black')
            ax.set_xlabel('Tipos de Financiamento Únicos')
            ax.set_ylabel('Frequência')
            ax.set_title('Distribuição de Tipos de Financiamento')
            ax.grid(True, alpha=0.3, axis='y')
        
        # Kd vs quantidade indexadores
        if 'Indexadores_Unicos' in df.columns:
            ax = axes[2]
            ax.scatter(df['Indexadores_Unicos'], df['Kd_Ponderado'], alpha=0.6, s=50, color='lightgreen')
            ax.set_xlabel('Quantidade de Indexadores Únicos')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Kd vs Quantidade de Indexadores')
            ax.grid(True, alpha=0.3)
        
        # Distribuição por indexador principal (simplificado)
        if 'Indexadores_Usados' in df.columns:
            ax = axes[3]
            # Contar indexadores mais comuns
            all_indexers = []
            for idx_str in df['Indexadores_Usados'].dropna():
                if isinstance(idx_str, str):
                    all_indexers.extend([i.strip() for i in idx_str.split(',')])
            if all_indexers:
                from collections import Counter
                indexer_counts = Counter(all_indexers)
                top_indexers = dict(indexer_counts.most_common(5))
                ax.bar(range(len(top_indexers)), list(top_indexers.values()), 
                      color='purple', alpha=0.7)
                ax.set_xticks(range(len(top_indexers)))
                ax.set_xticklabels(list(top_indexers.keys()), rotation=45, ha='right', fontsize=8)
                ax.set_ylabel('Frequência')
                ax.set_title('Top 5 Indexadores Mais Usados')
                ax.grid(True, alpha=0.3, axis='y')
        
        fig.suptitle('05 - EDA: Indexadores e Tipos de Financiamento', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '05_eda_indexadores_tipos.png')
        
        # 06: Valor e Financiamentos
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Kd vs valor consolidado (scatter)
        if 'Valor_Consolidado_Media' in df.columns:
            ax = axes[0]
            ax.scatter(df['Valor_Consolidado_Media'], df['Kd_Ponderado'], alpha=0.6, s=50)
            ax.set_xlabel('Valor Consolidado Médio')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Kd vs Valor Consolidado')
            ax.grid(True, alpha=0.3)
        
        # Kd vs valor consolidado (log)
        if 'Valor_Consolidado_Media' in df.columns:
            ax = axes[1]
            val_log = np.log1p(df['Valor_Consolidado_Media'])
            ax.scatter(val_log, df['Kd_Ponderado'], alpha=0.6, s=50, color='coral')
            ax.set_xlabel('log(Valor Consolidado)')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Kd vs Valor Consolidado (Log)')
            ax.grid(True, alpha=0.3)
        
        # Kd vs total financiamentos
        if 'Total_Financiamentos' in df.columns:
            ax = axes[2]
            ax.scatter(df['Total_Financiamentos'], df['Kd_Ponderado'], alpha=0.6, s=50, color='lightgreen')
            ax.set_xlabel('Total de Financiamentos')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Kd vs Total de Financiamentos')
            ax.grid(True, alpha=0.3)
        
        # Distribuição valor por faixa Kd
        if 'Valor_Consolidado_Total' in df.columns:
            ax = axes[3]
            df['Kd_Faixa'] = pd.cut(df['Kd_Ponderado'], bins=5, labels=['Muito Baixo', 'Baixo', 'Médio', 'Alto', 'Muito Alto'])
            df_faixa = df.groupby('Kd_Faixa')['Valor_Consolidado_Total'].sum()
            ax.bar(range(len(df_faixa)), df_faixa.values, color='purple', alpha=0.7)
            ax.set_xticks(range(len(df_faixa)))
            ax.set_xticklabels(df_faixa.index, rotation=45, ha='right', fontsize=8)
            ax.set_ylabel('Valor Consolidado Total')
            ax.set_title('Distribuição de Valor por Faixa de Kd')
            ax.grid(True, alpha=0.3, axis='y')
        
        fig.suptitle('06 - EDA: Valor e Financiamentos', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '06_eda_valor_financiamentos.png')
        
        # 07: Correlações
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Matriz correlação completa (simplificada - apenas algumas variáveis)
        ax = axes[0]
        corr_vars = ['Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos', 
                    'Kd_Desvio_Padrao', 'Indexadores_Unicos', 'Tipos_Financiamento_Unicos']
        corr_vars = [v for v in corr_vars if v in df.columns]
        if len(corr_vars) > 1:
            corr_matrix = df[corr_vars].corr()
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
            ax.set_title('Matriz de Correlação (Selecionadas)')
        
        # Correlação Kd vs principais variáveis
        ax = axes[1]
        if len(corr_vars) > 1:
            corr_with_kd = df[corr_vars].corr()['Kd_Ponderado'].drop('Kd_Ponderado').sort_values()
            colors = ['red' if x < 0 else 'green' for x in corr_with_kd.values]
            bars = ax.barh(range(len(corr_with_kd)), corr_with_kd.values, color=colors, alpha=0.7)
            ax.set_yticks(range(len(corr_with_kd)))
            ax.set_yticklabels([v[:30] for v in corr_with_kd.index], fontsize=8)
            ax.set_xlabel('Correlação com Kd')
            ax.set_title('Correlação Kd vs Principais Variáveis')
            ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
            ax.grid(True, alpha=0.3, axis='x')
        
        # Heatmap indexadores vs Kd (simplificado)
        ax = axes[2]
        if 'Indexadores_Unicos' in df.columns:
            ax.scatter(df['Indexadores_Unicos'], df['Kd_Ponderado'], alpha=0.6, s=50, color='coral')
            ax.set_xlabel('Indexadores Únicos')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Indexadores vs Kd')
            ax.grid(True, alpha=0.3)
        
        # Correlação tipos vs Kd
        ax = axes[3]
        if 'Tipos_Financiamento_Unicos' in df.columns:
            ax.scatter(df['Tipos_Financiamento_Unicos'], df['Kd_Ponderado'], alpha=0.6, s=50, color='purple')
            ax.set_xlabel('Tipos de Financiamento Únicos')
            ax.set_ylabel('Kd Ponderado')
            ax.set_title('Tipos vs Kd')
            ax.grid(True, alpha=0.3)
        
        fig.suptitle('07 - EDA: Correlações', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '07_eda_correlacoes.png')
        
        # 08: Clustering e Análise Avançada
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Clustering Kd vs valor/financiamentos
        if 'Valor_Consolidado_Media' in df.columns and 'Total_Financiamentos' in df.columns:
            ax = axes[0]
            data_cluster = df[['Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos']].dropna()
            if len(data_cluster) > 3:
                scaler = StandardScaler()
                data_scaled = scaler.fit_transform(data_cluster)
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(data_scaled)
                scatter = ax.scatter(data_cluster['Valor_Consolidado_Media'], 
                                   data_cluster['Kd_Ponderado'], 
                                   c=clusters, cmap='viridis', alpha=0.6, s=50)
                ax.set_xlabel('Valor Consolidado Médio')
                ax.set_ylabel('Kd Ponderado')
                ax.set_title('Clustering Kd vs Valor/Financiamentos')
                plt.colorbar(scatter, ax=ax)
                ax.grid(True, alpha=0.3)
        
        # Heatmap empresas top 30 (simplificado)
        ax = axes[1]
        top_30 = df.nlargest(30, 'Kd_Ponderado')
        if 'Valor_Consolidado_Media' in top_30.columns and 'Total_Financiamentos' in top_30.columns:
            heatmap_data = top_30[['Kd_Ponderado', 'Valor_Consolidado_Media', 'Total_Financiamentos']].T
            sns.heatmap(heatmap_data, annot=False, cmap='YlOrRd', ax=ax, cbar_kws={"shrink": 0.8})
            ax.set_title('Heatmap Top 30 Empresas')
            ax.set_yticklabels(['Kd', 'Valor', 'Financ.'], fontsize=8)
            ax.set_xticklabels([], rotation=90)
        
        # Análise de resíduos (simplificado)
        ax = axes[2]
        if 'Valor_Consolidado_Media' in df.columns:
            X_reg = df[['Valor_Consolidado_Media']].dropna()
            y_reg = df.loc[X_reg.index, 'Kd_Ponderado']
            if len(X_reg) > 5:
                model = LinearRegression()
                model.fit(X_reg, y_reg)
                y_pred = model.predict(X_reg)
                residuals = y_reg - y_pred
                ax.scatter(y_pred, residuals, alpha=0.6, s=50, color='steelblue')
                ax.axhline(0, color='red', linestyle='--', linewidth=2)
                ax.set_xlabel('Valores Preditos')
                ax.set_ylabel('Resíduos')
                ax.set_title('Análise de Resíduos (Kd vs Valor)')
                ax.grid(True, alpha=0.3)
        
        # Sumário estatístico completo
        ax = axes[3]
        ax.axis('off')
        summary_stats = {
            'Média': kd.mean(),
            'Mediana': kd.median(),
            'Desvio Padrão': kd.std(),
            'Mínimo': kd.min(),
            'Máximo': kd.max(),
            'Assimetria': kd.skew(),
            'Curtose': kd.kurtosis()
        }
        rows = [[k, f'{v:.4f}'] for k, v in summary_stats.items()]
        table = ax.table(cellText=rows, colLabels=['Estatística', 'Valor'],
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax.set_title('Sumário Estatístico Completo')
        
        fig.suptitle('08 - EDA: Clustering e Análise Avançada', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '08_eda_clustering_avancado.png')
        
        print("✅ Figuras EDA geradas com sucesso!")
    
    # ========================================================================
    # REGRESSION FIGURES (09-20)
    # ========================================================================
    
    def generate_regression_figures(self):
        """Gera todas as figuras consolidadas de Regressão."""
        print("\n" + "="*80)
        print("GERANDO FIGURAS REGRESSÃO CONSOLIDADAS (09-20)")
        print("="*80)
        
        y, X, df = self.load_regression_data()
        data = pd.concat([y, X], axis=1).dropna()
        
        if len(data) < 10:
            print("  ⚠️ Sem dados suficientes para regressão")
            return None
        
        y_clean = data[y.name]
        X_clean = data.drop(columns=[y.name])
        
        # 09: Análise Univariada Resposta
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Histograma com normal
        ax = axes[0]
        n, bins, patches = ax.hist(y_clean, bins=30, density=True, alpha=0.7, 
                                  color='steelblue', edgecolor='black')
        mu, sigma = y_clean.mean(), y_clean.std()
        x_norm = np.linspace(y_clean.min(), y_clean.max(), 100)
        y_norm = stats.norm.pdf(x_norm, mu, sigma)
        ax.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal (μ={mu:.2f}, σ={sigma:.2f})')
        ax.axvline(mu, color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_ylabel('Densidade')
        ax.set_title('Histograma com Curva Normal')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Q-Q plot
        ax = axes[1]
        stats.probplot(y_clean, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot (Normalidade)')
        ax.grid(True, alpha=0.3)
        
        # Boxplot outliers
        ax = axes[2]
        bp = ax.boxplot(y_clean, vert=True, patch_artist=True, showfliers=True)
        bp['boxes'][0].set_facecolor('lightblue')
        Q1, Q3 = y_clean.quantile(0.25), y_clean.quantile(0.75)
        IQR = Q3 - Q1
        outliers = y_clean[(y_clean < Q1 - 1.5*IQR) | (y_clean > Q3 + 1.5*IQR)]
        if len(outliers) > 0:
            ax.scatter([1]*len(outliers), outliers, color='red', s=50, zorder=3)
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_title(f'Boxplot com Outliers ({len(outliers)})')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Violin plot
        ax = axes[3]
        parts = ax.violinplot([y_clean], positions=[0], showmeans=True, showmedians=True)
        for pc in parts['bodies']:
            pc.set_facecolor('lightcoral')
            pc.set_alpha(0.7)
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_xticks([0])
        ax.set_xticklabels(['Kd Ponderado'])
        ax.set_title('Violin Plot')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Log-transformado
        ax = axes[4]
        y_log = np.log1p(y_clean - y_clean.min() + 1)
        ax.hist(y_log, bins=30, alpha=0.7, color='coral', edgecolor='black', density=True)
        ax.set_xlabel('log(Kd Ponderado)')
        ax.set_ylabel('Densidade')
        ax.set_title('Log-Transformado')
        ax.grid(True, alpha=0.3)
        
        # Distribuição completa
        ax = axes[5]
        ax.hist(y_clean, bins=30, alpha=0.7, color='steelblue', edgecolor='black', density=True)
        ax.axvline(mu, color='red', linestyle='-', linewidth=2, label=f'Média: {mu:.2f}%')
        ax.axvline(y_clean.median(), color='green', linestyle='-', linewidth=2, label=f'Mediana: {y_clean.median():.2f}%')
        ax.axvline(mu + sigma, color='orange', linestyle='--', linewidth=1, alpha=0.7, label=f'±1σ')
        ax.axvline(mu - sigma, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax.set_xlabel('Kd Ponderado (% a.a.)')
        ax.set_ylabel('Densidade')
        ax.set_title('Distribuição Completa')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
        
        fig.suptitle('09 - Regressão: Análise Univariada da Variável Resposta', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '09_regressao_univariada_resposta.png', figsize=(18, 12))
        
        # 10: Análise Univariada Preditoras
        top_vars = self.get_top_variables(X_clean, y_clean, n=9)
        if len(top_vars) < 9:
            top_vars = X_clean.columns[:9].tolist() if len(X_clean.columns) >= 9 else X_clean.columns.tolist()
        
        fig, axes = plt.subplots(3, 3, figsize=(18, 18))
        axes = axes.flatten()
        
        for idx, var in enumerate(top_vars[:9]):
            ax = axes[idx]
            var_data = X_clean[var].dropna()
            if len(var_data) < 5:
                ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(var[:30])
                continue
            
            # Histograma
            ax.hist(var_data, bins=20, alpha=0.7, color='steelblue', edgecolor='black', density=True)
            ax.axvline(var_data.mean(), color='red', linestyle='--', linewidth=2)
            ax.set_xlabel(var[:25])
            ax.set_ylabel('Densidade')
            ax.set_title(f'{var[:25]}\nSkew: {var_data.skew():.3f}')
            ax.grid(True, alpha=0.3)
        
        fig.suptitle('10 - Regressão: Análise Univariada das Variáveis Preditoras (Top 9)', 
                    fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '10_regressao_univariada_preditoras.png', figsize=(18, 18))
        
        # 11-12: Análises Bivariadas
        top_vars_biv = self.get_top_variables(X_clean, y_clean, n=18)
        if len(top_vars_biv) < 18:
            corr_with_kd = X_clean.corrwith(y_clean).abs().sort_values(ascending=False)
            top_vars_biv = corr_with_kd.head(18).index.tolist()
        
        # Parte 1 (primeiras 9)
        fig, axes = plt.subplots(3, 3, figsize=(18, 18))
        axes = axes.flatten()
        
        for idx, var in enumerate(top_vars_biv[:9]):
            ax = axes[idx]
            x_data = X_clean[var].dropna()
            y_data = y_clean[x_data.index]
            
            if len(x_data) < 5:
                ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', transform=ax.transAxes)
                continue
            
            # Scatter plot
            ax.scatter(x_data, y_data, alpha=0.6, s=30, color='steelblue', edgecolors='black', linewidth=0.3)
            
            # Regressão linear
            X_reg = x_data.values.reshape(-1, 1)
            model = LinearRegression()
            model.fit(X_reg, y_data.values)
            y_pred = model.predict(X_reg)
            
            x_line = np.linspace(x_data.min(), x_data.max(), 100).reshape(-1, 1)
            y_line = model.predict(x_line)
            ax.plot(x_line, y_line, 'r-', linewidth=2)
            
            # Estatísticas
            r2 = r2_score(y_data.values, y_pred)
            from scipy.stats import linregress
            _, _, _, p_value, _ = linregress(x_data, y_data)
            
            sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
            ax.text(0.05, 0.95, f'R²={r2:.3f}\np={p_value:.4f}{sig}', 
                   transform=ax.transAxes, fontsize=8, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_xlabel(var[:25])
            ax.set_ylabel('Kd Ponderado')
            ax.set_title(f'Kd vs {var[:20]}')
            ax.grid(True, alpha=0.3)
        
        fig.suptitle('11 - Regressão: Análises Bivariadas (Parte 1 - Top 9)', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '11_regressao_bivariadas_1.png', figsize=(18, 18))
        
        # Parte 2 (próximas 9)
        if len(top_vars_biv) >= 18:
            fig, axes = plt.subplots(3, 3, figsize=(18, 18))
            axes = axes.flatten()
            
            for idx, var in enumerate(top_vars_biv[9:18]):
                ax = axes[idx]
                x_data = X_clean[var].dropna()
                y_data = y_clean[x_data.index]
                
                if len(x_data) < 5:
                    ax.text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center', transform=ax.transAxes)
                    continue
                
                ax.scatter(x_data, y_data, alpha=0.6, s=30, color='coral', edgecolors='black', linewidth=0.3)
                
                X_reg = x_data.values.reshape(-1, 1)
                model = LinearRegression()
                model.fit(X_reg, y_data.values)
                x_line = np.linspace(x_data.min(), x_data.max(), 100).reshape(-1, 1)
                y_line = model.predict(x_line)
                ax.plot(x_line, y_line, 'r-', linewidth=2)
                
                r2 = r2_score(y_data.values, model.predict(X_reg))
                _, _, _, p_value, _ = linregress(x_data, y_data)
                sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
                ax.text(0.05, 0.95, f'R²={r2:.3f}\np={p_value:.4f}{sig}', 
                       transform=ax.transAxes, fontsize=8, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                
                ax.set_xlabel(var[:25])
                ax.set_ylabel('Kd Ponderado')
                ax.set_title(f'Kd vs {var[:20]}')
                ax.grid(True, alpha=0.3)
            
            fig.suptitle('12 - Regressão: Análises Bivariadas (Parte 2 - Próximas 9)', fontsize=14, y=0.995)
            self.save_consolidated_figure(fig, '12_regressao_bivariadas_2.png', figsize=(18, 18))
        
        # 13: Correlações
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Matriz correlação completa
        ax = axes[0]
        corr_matrix = data.corr()
        # Limitar para não ficar muito grande
        if len(corr_matrix) > 20:
            top_vars_corr = X_clean.corrwith(y_clean).abs().nlargest(15).index
            corr_subset = data[list(top_vars_corr) + [y.name]].corr()
            sns.heatmap(corr_subset, annot=False, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax, fmt='.2f')
        else:
            sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax, fmt='.2f')
        ax.set_title('Matriz de Correlação Completa')
        
        # Pearson vs Spearman
        ax = axes[1]
        pearson_corr = X_clean.corrwith(y_clean, method='pearson')
        spearman_corr = X_clean.corrwith(y_clean, method='spearman')
        common_vars = pearson_corr.index.intersection(spearman_corr.index)
        if len(common_vars) > 0:
            pearson_aligned = pearson_corr[common_vars]
            spearman_aligned = spearman_corr[common_vars]
            ax.scatter(pearson_aligned, spearman_aligned, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
            min_val = min(pearson_aligned.min(), spearman_aligned.min())
            max_val = max(pearson_aligned.max(), spearman_aligned.max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)
            ax.set_xlabel('Correlação de Pearson')
            ax.set_ylabel('Correlação de Spearman')
            ax.set_title('Pearson vs Spearman')
            ax.grid(True, alpha=0.3)
        
        # Correlação com Kd (barras)
        ax = axes[2]
        corr_with_kd = X_clean.corrwith(y_clean).sort_values()
        top_corr = corr_with_kd.head(15) if len(corr_with_kd) > 15 else corr_with_kd
        colors = ['red' if x < 0 else 'green' for x in top_corr.values]
        bars = ax.barh(range(len(top_corr)), top_corr.values, color=colors, alpha=0.7)
        ax.set_yticks(range(len(top_corr)))
        ax.set_yticklabels([v[:30] for v in top_corr.index], fontsize=7)
        ax.set_xlabel('Correlação com Kd')
        ax.set_title('Correlação com Kd (Ordenado)')
        ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Heatmap top 15 variáveis
        ax = axes[3]
        top_vars_heat = X_clean.corrwith(y_clean).abs().nlargest(15).index
        corr_subset = data[list(top_vars_heat) + [y.name]].corr()
        sns.heatmap(corr_subset, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax, annot_kws={"size": 7})
        ax.set_title('Heatmap Top 15 Variáveis')
        
        fig.suptitle('13 - Regressão: Análise de Correlações', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '13_regressao_correlacoes.png')
        
        # 14: Modelo Base
        # Selecionar variáveis para modelo
        top_vars_model = X_clean.corrwith(y_clean).abs().sort_values(ascending=False).head(10).index.tolist()
        X_selected = X_clean[top_vars_model]
        X_with_const = sm.add_constant(X_selected)
        model = sm.OLS(y_clean, X_with_const).fit()
        y_pred = model.fittedvalues
        residuals = model.resid
        standardized_residuals = model.resid_pearson
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Observado vs Predito
        ax = axes[0]
        ax.scatter(y_clean, y_pred, alpha=0.6, s=50, color='steelblue', edgecolors='black', linewidth=0.5)
        min_val = min(y_clean.min(), y_pred.min())
        max_val = max(y_clean.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
        r2 = model.rsquared
        ax.set_xlabel('Kd Observado')
        ax.set_ylabel('Kd Predito')
        ax.set_title(f'Observado vs Predito (R² = {r2:.3f})')
        ax.grid(True, alpha=0.3)
        
        # Resíduos vs Preditos
        ax = axes[1]
        ax.scatter(y_pred, residuals, alpha=0.6, s=50, color='steelblue', edgecolors='black', linewidth=0.5)
        ax.axhline(0, color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Valores Preditos')
        ax.set_ylabel('Resíduos')
        ax.set_title('Resíduos vs Valores Preditos')
        ax.grid(True, alpha=0.3)
        
        # Resíduos Padronizados
        ax = axes[2]
        ax.scatter(y_pred, standardized_residuals, alpha=0.6, s=50, color='coral', edgecolors='black', linewidth=0.5)
        ax.axhline(0, color='red', linestyle='--', linewidth=2)
        ax.axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax.axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax.set_xlabel('Valores Preditos')
        ax.set_ylabel('Resíduos Padronizados')
        ax.set_title('Resíduos Padronizados')
        ax.grid(True, alpha=0.3)
        
        # Q-Q plot resíduos
        ax = axes[3]
        stats.probplot(residuals, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot dos Resíduos')
        ax.grid(True, alpha=0.3)
        
        # Scale-Location
        ax = axes[4]
        sqrt_abs_residuals = np.sqrt(np.abs(standardized_residuals))
        ax.scatter(y_pred, sqrt_abs_residuals, alpha=0.6, s=50, color='lightgreen', 
                  edgecolors='black', linewidth=0.5)
        ax.set_xlabel('Valores Preditos')
        ax.set_ylabel('√|Resíduos Padronizados|')
        ax.set_title('Scale-Location Plot')
        ax.grid(True, alpha=0.3)
        
        # Resumo do modelo
        ax = axes[5]
        ax.axis('off')
        metrics_text = f"""R² = {model.rsquared:.4f}
R² Ajustado = {model.rsquared_adj:.4f}
AIC = {model.aic:.2f}
BIC = {model.bic:.2f}
F-statistic = {model.fvalue:.2f}
Prob (F-statistic) = {model.f_pvalue:.4f}
N = {model.nobs}"""
        ax.text(0.1, 0.5, metrics_text, fontfamily='monospace', fontsize=10,
               verticalalignment='center', transform=ax.transAxes)
        ax.set_title('Métricas do Modelo')
        
        fig.suptitle('14 - Regressão: Modelo Base e Diagnósticos', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '14_regressao_modelo_base.png', figsize=(18, 12))
        
        # 15: Coeficientes e Significância
        coef_df = pd.DataFrame({
            'Coeficiente': model.params,
            'Std Error': model.bse,
            't-value': model.tvalues,
            'p-value': model.pvalues
        }).sort_values('p-value')
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Coeficientes
        ax = axes[0]
        colors = ['red' if p < 0.05 else 'gray' for p in coef_df['p-value']]
        bars = ax.barh(range(len(coef_df)), coef_df['Coeficiente'].values, color=colors, alpha=0.7)
        ax.set_yticks(range(len(coef_df)))
        ax.set_yticklabels([var[:30] for var in coef_df.index], fontsize=8)
        ax.set_xlabel('Coeficiente')
        ax.set_title('Coeficientes (Vermelho: p<0.05)')
        ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='x')
        
        # P-values
        ax = axes[1]
        colors = ['red' if p < 0.05 else 'gray' for p in coef_df['p-value']]
        bars = ax.barh(range(len(coef_df)), coef_df['p-value'].values, color=colors, alpha=0.7)
        ax.axvline(0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')
        ax.set_yticks(range(len(coef_df)))
        ax.set_yticklabels([var[:30] for var in coef_df.index], fontsize=8)
        ax.set_xlabel('p-value')
        ax.set_title('Significância (p-value)')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Intervalos de confiança
        ax = axes[2]
        conf_int = model.conf_int()
        conf_int.columns = ['Lower', 'Upper']
        conf_int['Coef'] = model.params
        y_pos = range(len(conf_int))
        ax.errorbar(conf_int['Coef'].values, y_pos,
                   xerr=[conf_int['Coef'] - conf_int['Lower'], 
                        conf_int['Upper'] - conf_int['Coef']],
                   fmt='o', capsize=5, capthick=2, alpha=0.7)
        ax.axvline(0, color='red', linestyle='--', linewidth=1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([var[:30] for var in conf_int.index], fontsize=8)
        ax.set_xlabel('Coeficiente (IC 95%)')
        ax.set_title('Intervalos de Confiança')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Métricas
        ax = axes[3]
        ax.axis('off')
        metrics_data = [
            ['Métrica', 'Valor'],
            ['R²', f'{model.rsquared:.4f}'],
            ['R² Ajustado', f'{model.rsquared_adj:.4f}'],
            ['AIC', f'{model.aic:.2f}'],
            ['BIC', f'{model.bic:.2f}'],
            ['F-statistic', f'{model.fvalue:.2f}'],
            ['Prob (F-statistic)', f'{model.f_pvalue:.4f}'],
            ['N', f'{model.nobs}']
        ]
        table = ax.table(cellText=metrics_data[1:], colLabels=metrics_data[0],
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax.set_title('Métricas do Modelo')
        
        fig.suptitle('15 - Regressão: Coeficientes e Significância', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '15_regressao_coeficientes.png')
        
        # 16: Diagnósticos
        influence = model.get_influence()
        leverage = influence.hat_matrix_diag
        cooks_d = influence.cooks_distance[0]
        dffits = influence.dffits[0]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Leverage vs Resíduos
        ax = axes[0]
        ax.scatter(leverage, standardized_residuals, alpha=0.6, s=50, 
                  color='steelblue', edgecolors='black', linewidth=0.5)
        p = len(model.params)
        n = len(y_clean)
        leverage_threshold = 2 * p / n
        ax.axhline(0, color='red', linestyle='--', linewidth=1)
        ax.axvline(leverage_threshold, color='red', linestyle='--', linewidth=1)
        ax.set_xlabel('Leverage')
        ax.set_ylabel('Resíduos Padronizados')
        ax.set_title('Leverage vs Resíduos')
        ax.grid(True, alpha=0.3)
        
        # Cook's Distance
        ax = axes[1]
        ax.scatter(range(len(cooks_d)), cooks_d, alpha=0.6, s=50, 
                  color='coral', edgecolors='black', linewidth=0.5)
        cook_threshold = 4 / n
        ax.axhline(cook_threshold, color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Observação')
        ax.set_ylabel("Cook's Distance")
        ax.set_title("Cook's Distance")
        ax.grid(True, alpha=0.3)
        
        # DFFITS
        ax = axes[2]
        ax.scatter(range(len(dffits)), dffits, alpha=0.6, s=50, 
                  color='lightgreen', edgecolors='black', linewidth=0.5)
        dffits_threshold = 2 * np.sqrt(p / n)
        ax.axhline(dffits_threshold, color='red', linestyle='--', linewidth=2)
        ax.axhline(-dffits_threshold, color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Observação')
        ax.set_ylabel('DFFITS')
        ax.set_title('DFFITS')
        ax.grid(True, alpha=0.3)
        
        # VIF
        ax = axes[3]
        try:
            vif_data = pd.DataFrame()
            vif_data["Variável"] = X_selected.columns
            vif_data["VIF"] = [variance_inflation_factor(X_selected.values, i) 
                              for i in range(X_selected.shape[1])]
            vif_data = vif_data.sort_values('VIF', ascending=False)
            colors = ['red' if v > 10 else 'orange' if v > 5 else 'green' 
                     for v in vif_data['VIF'].values]
            bars = ax.barh(range(len(vif_data)), vif_data['VIF'].values, 
                          color=colors, alpha=0.7)
            ax.axvline(5, color='orange', linestyle='--', linewidth=2)
            ax.axvline(10, color='red', linestyle='--', linewidth=2)
            ax.set_yticks(range(len(vif_data)))
            ax.set_yticklabels([var[:25] for var in vif_data['Variável']], fontsize=8)
            ax.set_xlabel('VIF')
            ax.set_title('VIF (Multicolinearidade)')
            ax.grid(True, alpha=0.3, axis='x')
        except:
            ax.text(0.5, 0.5, 'Erro ao calcular VIF', ha='center', va='center', transform=ax.transAxes)
        
        # Influence Plot
        ax = axes[4]
        scatter = ax.scatter(leverage, standardized_residuals, 
                            s=cooks_d * 1000, alpha=0.6, c=cooks_d, cmap='Reds',
                            edgecolors='black', linewidth=0.5)
        ax.axhline(0, color='red', linestyle='--', linewidth=1)
        ax.axvline(leverage_threshold, color='red', linestyle='--', linewidth=1)
        ax.set_xlabel('Leverage')
        ax.set_ylabel('Resíduos Padronizados')
        ax.set_title('Influence Plot')
        plt.colorbar(scatter, ax=ax, label="Cook's Distance")
        ax.grid(True, alpha=0.3)
        
        # Resíduos Studentizados
        ax = axes[5]
        studentized_residuals = influence.resid_studentized_internal
        ax.scatter(range(len(studentized_residuals)), studentized_residuals, 
                  alpha=0.6, s=50, color='purple', edgecolors='black', linewidth=0.5)
        ax.axhline(0, color='red', linestyle='--', linewidth=1)
        ax.axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax.axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax.set_xlabel('Observação')
        ax.set_ylabel('Resíduos Studentizados')
        ax.set_title('Resíduos Studentizados')
        ax.grid(True, alpha=0.3)
        
        fig.suptitle('16 - Regressão: Diagnósticos Avançados', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '16_regressao_diagnosticos.png', figsize=(18, 12))
        
        # 17: Análise de Resíduos
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Distribuição resíduos (hist + Q-Q)
        ax = axes[0]
        ax.hist(residuals, bins=30, alpha=0.7, color='steelblue', edgecolor='black', density=True)
        mu_res, sigma_res = residuals.mean(), residuals.std()
        x_norm = np.linspace(residuals.min(), residuals.max(), 100)
        y_norm = stats.norm.pdf(x_norm, mu_res, sigma_res)
        ax.plot(x_norm, y_norm, 'r-', linewidth=2)
        ax.axvline(0, color='green', linestyle='--', linewidth=2)
        ax.set_xlabel('Resíduos')
        ax.set_ylabel('Densidade')
        ax.set_title('Distribuição dos Resíduos')
        ax.grid(True, alpha=0.3)
        
        ax = axes[1]
        stats.probplot(residuals, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot dos Resíduos')
        ax.grid(True, alpha=0.3)
        
        # ACF/PACF (simplificado)
        ax = axes[2]
        try:
            from statsmodels.tsa.stattools import acf, pacf
            acf_values = acf(residuals, nlags=min(10, len(residuals)//4), fft=True)
            ax.bar(range(len(acf_values)), acf_values, alpha=0.7, color='steelblue', edgecolor='black')
            ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
            ax.set_xlabel('Lag')
            ax.set_ylabel('ACF')
            ax.set_title('ACF dos Resíduos')
            ax.grid(True, alpha=0.3)
        except:
            ax.text(0.5, 0.5, 'Erro ao calcular ACF', ha='center', va='center', transform=ax.transAxes)
        
        # Teste heterocedasticidade
        ax = axes[3]
        ax.axis('off')
        try:
            bp_test = het_breuschpagan(residuals, model.model.exog)
            bp_stat, bp_pvalue = bp_test[0], bp_test[1]
            test_results = [
                ['Teste', 'Estatística', 'p-value', 'Conclusão'],
                ['Breusch-Pagan', f'{bp_stat:.4f}', f'{bp_pvalue:.4f}',
                 'Homocedástico' if bp_pvalue > 0.05 else 'Heterocedástico']
            ]
            table = ax.table(cellText=test_results[1:], colLabels=test_results[0],
                           cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 2)
            ax.set_title('Teste de Heterocedasticidade')
        except:
            ax.text(0.5, 0.5, 'Erro no teste', ha='center', va='center', transform=ax.transAxes)
        
        # Resíduos vs ordem
        ax = axes[4]
        ax.scatter(range(len(residuals)), residuals, alpha=0.6, s=50, 
                  color='steelblue', edgecolors='black', linewidth=0.5)
        ax.axhline(0, color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Ordem da Observação')
        ax.set_ylabel('Resíduos')
        ax.set_title('Resíduos vs Ordem')
        ax.grid(True, alpha=0.3)
        
        # Estatísticas resíduos
        ax = axes[5]
        ax.axis('off')
        residual_stats = {
            'Média': residuals.mean(),
            'Mediana': residuals.median(),
            'Desvio Padrão': residuals.std(),
            'Mínimo': residuals.min(),
            'Máximo': residuals.max(),
            'Assimetria': stats.skew(residuals),
            'Curtose': stats.kurtosis(residuals)
        }
        rows = [[k, f'{v:.4f}'] for k, v in residual_stats.items()]
        table = ax.table(cellText=rows, colLabels=['Estatística', 'Valor'],
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        ax.set_title('Estatísticas dos Resíduos')
        
        fig.suptitle('17 - Regressão: Análise de Resíduos', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '17_regressao_residuos.png', figsize=(18, 12))
        
        # 18: Multicolinearidade
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Heatmap correlação entre preditoras
        ax = axes[0]
        corr_pred = X_selected.corr()
        sns.heatmap(corr_pred, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax, annot_kws={"size": 7})
        ax.set_title('Correlação entre Preditoras')
        
        # VIF por variável
        ax = axes[1]
        try:
            vif_data = pd.DataFrame()
            vif_data["Variável"] = X_selected.columns
            vif_data["VIF"] = [variance_inflation_factor(X_selected.values, i) 
                              for i in range(X_selected.shape[1])]
            vif_data = vif_data.sort_values('VIF', ascending=False)
            colors = ['red' if v > 10 else 'orange' if v > 5 else 'green' 
                     for v in vif_data['VIF'].values]
            bars = ax.barh(range(len(vif_data)), vif_data['VIF'].values, 
                          color=colors, alpha=0.7)
            ax.axvline(5, color='orange', linestyle='--', linewidth=2)
            ax.axvline(10, color='red', linestyle='--', linewidth=2)
            ax.set_yticks(range(len(vif_data)))
            ax.set_yticklabels([var[:25] for var in vif_data['Variável']], fontsize=8)
            ax.set_xlabel('VIF')
            ax.set_title('VIF por Variável')
            ax.grid(True, alpha=0.3, axis='x')
        except:
            ax.text(0.5, 0.5, 'Erro ao calcular VIF', ha='center', va='center', transform=ax.transAxes)
        
        # Pares alta correlação
        ax = axes[2]
        high_corr_pairs = []
        for i, var1 in enumerate(X_selected.columns):
            for var2 in X_selected.columns[i+1:]:
                corr_val = corr_pred.loc[var1, var2]
                if abs(corr_val) > 0.8:
                    high_corr_pairs.append((var1, var2, corr_val))
        
        if high_corr_pairs:
            high_corr_df = pd.DataFrame(high_corr_pairs, 
                                       columns=['Variável 1', 'Variável 2', 'Correlação'])
            high_corr_df = high_corr_df.sort_values('Correlação', key=abs, ascending=False)
            colors = ['red' if c > 0 else 'blue' for c in high_corr_df['Correlação'].values]
            bars = ax.barh(range(len(high_corr_df)), high_corr_df['Correlação'].values, 
                          color=colors, alpha=0.7)
            ax.set_yticks(range(len(high_corr_df)))
            ax.set_yticklabels([f"{row['Variável 1'][:15]} vs {row['Variável 2'][:15]}" 
                               for _, row in high_corr_df.iterrows()], fontsize=7)
            ax.set_xlabel('Correlação')
            ax.set_title('Pares com Alta Correlação (|r| > 0.8)')
            ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
            ax.grid(True, alpha=0.3, axis='x')
        else:
            ax.text(0.5, 0.5, 'Nenhum par com |r| > 0.8', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Pares com Alta Correlação')
        
        # Análise correlação parcial (simplificada)
        ax = axes[3]
        ax.axis('off')
        ax.text(0.5, 0.5, 'Análise de correlação parcial\nimplementada no VIF', 
               ha='center', va='center', transform=ax.transAxes, fontsize=10)
        ax.set_title('Correlação Parcial')
        
        fig.suptitle('18 - Regressão: Multicolinearidade', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '18_regressao_multicolinearidade.png')
        
        # 19: Transformações
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Comparação transformações Y
        transforms_y = [
            ('Original', y_clean),
            ('Log', np.log1p(y_clean - y_clean.min() + 1)),
            ('Sqrt', np.sqrt(y_clean - y_clean.min() + 1)),
            ('Square', (y_clean - y_clean.mean())**2),
            ('Reciprocal', 1/(y_clean - y_clean.min() + 1)),
            ('Box-Cox', None)
        ]
        
        for idx, (name, data_trans) in enumerate(transforms_y[:6]):
            ax = axes[idx]
            if name == 'Box-Cox':
                try:
                    from scipy.stats import boxcox
                    data_trans, _ = boxcox(y_clean - y_clean.min() + 1)
                except:
                    data_trans = y_clean
            if data_trans is not None:
                ax.hist(data_trans, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
                ax.set_title(f'{name}\nSkew: {stats.skew(data_trans):.3f}')
                ax.grid(True, alpha=0.3)
        
        fig.suptitle('19 - Regressão: Transformações da Variável Resposta', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '19_regressao_transformacoes.png', figsize=(18, 12))
        
        # 20: Outliers e Influência
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # Observado vs Predito com outliers
        ax = axes[0]
        outliers_mask = np.abs(standardized_residuals) > 3
        ax.scatter(y_clean[~outliers_mask], y_pred[~outliers_mask], alpha=0.6, s=50, 
                  color='steelblue', edgecolors='black', linewidth=0.5)
        if outliers_mask.sum() > 0:
            ax.scatter(y_clean[outliers_mask], y_pred[outliers_mask], color='red', s=100, 
                      marker='x', linewidth=2, label=f'Outliers ({outliers_mask.sum()})', zorder=3)
        min_val = min(y_clean.min(), y_pred.min())
        max_val = max(y_clean.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
        ax.set_xlabel('Kd Observado')
        ax.set_ylabel('Kd Predito')
        ax.set_title('Observado vs Predito com Outliers')
        if outliers_mask.sum() > 0:
            ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Leverage detalhado
        ax = axes[1]
        scatter = ax.scatter(leverage, standardized_residuals, 
                            s=cooks_d * 1000, alpha=0.6, c=cooks_d, cmap='Reds',
                            edgecolors='black', linewidth=0.5)
        ax.axhline(0, color='red', linestyle='--', linewidth=1)
        ax.axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax.axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax.axvline(leverage_threshold, color='red', linestyle='--', linewidth=1)
        influential = (leverage > leverage_threshold) & (np.abs(standardized_residuals) > 2)
        if influential.sum() > 0:
            ax.scatter(leverage[influential], standardized_residuals[influential], 
                      color='red', s=200, marker='x', linewidth=3, 
                      label=f'Influentes ({influential.sum()})', zorder=3)
        ax.set_xlabel('Leverage')
        ax.set_ylabel('Resíduos Padronizados')
        ax.set_title('Leverage Detalhado')
        plt.colorbar(scatter, ax=ax, label="Cook's Distance")
        if influential.sum() > 0:
            ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Casos extremos
        ax = axes[2]
        extreme_cases = pd.DataFrame({
            'Cook_Distance': cooks_d,
            'Observed': y_clean,
            'Predicted': y_pred
        }).sort_values('Cook_Distance', ascending=False).head(10)
        bars = ax.barh(range(len(extreme_cases)), extreme_cases['Cook_Distance'].values, 
                      color='coral', alpha=0.7)
        ax.set_yticks(range(len(extreme_cases)))
        ax.set_yticklabels([f"Obs {i}" for i in extreme_cases.index], fontsize=8)
        ax.set_xlabel("Cook's Distance")
        ax.set_title('Top 10 Casos Extremos')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Resumo outliers
        ax = axes[3]
        ax.axis('off')
        outlier_summary = {
            'Outliers (|res| > 3)': (np.abs(standardized_residuals) > 3).sum(),
            'Alta Leverage': (leverage > leverage_threshold).sum(),
            "Alta Cook's D": (cooks_d > 4/n).sum(),
            'Pontos Influentes': influential.sum()
        }
        rows = [[k, str(v)] for k, v in outlier_summary.items()]
        table = ax.table(cellText=rows, colLabels=['Tipo', 'Quantidade'],
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax.set_title('Resumo de Outliers')
        
        # Espaços vazios para completar
        axes[4].axis('off')
        axes[5].axis('off')
        
        fig.suptitle('20 - Regressão: Outliers e Influência', fontsize=14, y=0.995)
        self.save_consolidated_figure(fig, '20_regressao_outliers_influencia.png', figsize=(18, 12))
        
        print("✅ Figuras Regressão geradas com sucesso!")
        return model
    
    def generate_all(self):
        """Orquestra a geração de todas as figuras."""
        print("="*80)
        print("ORQUESTRADOR DE PIPELINES DE FIGURAS")
        print("="*80)
        
        # Limpar figuras antigas
        self.cleanup_old_figures()
        
        # Gerar figuras EDA
        self.generate_eda_figures()
        
        # Gerar figuras Regressão
        self.generate_regression_figures()
        
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETO CONCLUÍDO!")
        print(f"📁 Todas as figuras salvas em: {self.figures_dir}")
        print("="*80)


def main():
    """Função principal."""
    orchestrator = FigureOrchestrator()
    orchestrator.generate_all()


if __name__ == "__main__":
    main()


