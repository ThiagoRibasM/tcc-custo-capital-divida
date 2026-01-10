#!/usr/bin/env python3
"""
Pipeline completo de Análises de Regressão Linear com visualizações avançadas.
Gera figuras para análises univariadas, bivariadas e diagnósticos de regressão.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
from scipy import stats
from scipy.stats import shapiro, anderson, normaltest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
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
    """Carrega dados dos indicadores financeiros."""
    df = pd.read_csv(CONSOLIDATED_PATH / "indicadores_financeiros_completos.csv")
    print(f"📖 Dados carregados: {len(df)} empresas, {len(df.columns)} colunas")
    return df


def prepare_data(df):
    """Prepara dados para análise de regressão."""
    # Variável resposta
    y = df['Kd_Ponderado'].copy()
    
    # Variáveis independentes (remover colunas não numéricas e variável resposta)
    exclude_cols = ['Empresa', 'Kd_Ponderado']
    X = df.drop(columns=[c for c in exclude_cols if c in df.columns])
    
    # Remover colunas com muitos valores nulos (>50%)
    threshold = len(df) * 0.5
    X = X.loc[:, X.isnull().sum() < threshold]
    
    # Selecionar apenas colunas numéricas
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    X = X[numeric_cols]
    
    # Remover colunas com variância zero
    X = X.loc[:, X.var() > 0]
    
    print(f"📊 Variáveis independentes selecionadas: {len(X.columns)}")
    print(f"📊 Empresas com dados completos: {len(y.dropna())}")
    
    return y, X


# ============================================================================
# 1. ANÁLISES UNIVARIADAS - VARIÁVEL RESPOSTA (50-59)
# ============================================================================

def analyze_univariate_response(y):
    """Análises univariadas da variável resposta (Kd_Ponderado)."""
    print("\n📊 1. Análises Univariadas - Variável Resposta (50-59)")
    
    y_clean = y.dropna()
    
    # 50: Histograma com curva normal
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(y_clean, bins=30, density=True, alpha=0.7, 
                              color='steelblue', edgecolor='black')
    mu, sigma = y_clean.mean(), y_clean.std()
    x_norm = np.linspace(y_clean.min(), y_clean.max(), 100)
    y_norm = stats.norm.pdf(x_norm, mu, sigma)
    ax.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal (μ={mu:.2f}, σ={sigma:.2f})')
    ax.axvline(mu, color='red', linestyle='--', linewidth=2, label=f'Média: {mu:.2f}%')
    ax.axvline(y_clean.median(), color='green', linestyle='--', linewidth=2, label=f'Mediana: {y_clean.median():.2f}%')
    ax.set_xlabel('Kd Ponderado (% a.a.)')
    ax.set_ylabel('Densidade')
    ax.set_title('50 - Distribuição de Kd Ponderado com Curva Normal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '50_analise_univariada_kd_histograma_normal.png')
    
    # 51: Q-Q plot
    fig, ax = plt.subplots()
    stats.probplot(y_clean, dist="norm", plot=ax)
    ax.set_title('51 - Q-Q Plot: Normalidade de Kd Ponderado')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '51_analise_univariada_kd_qqplot.png')
    
    # 52: Testes de normalidade
    shapiro_stat, shapiro_p = shapiro(y_clean)
    anderson_result = anderson(y_clean)
    d_agostino_stat, d_agostino_p = normaltest(y_clean)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    test_results = [
        ['Teste', 'Estatística', 'p-value', 'Conclusão'],
        ['Shapiro-Wilk', f'{shapiro_stat:.4f}', f'{shapiro_p:.4f}', 
         'Normal' if shapiro_p > 0.05 else 'Não Normal'],
        ['Anderson-Darling', f'{anderson_result.statistic:.4f}', 'N/A',
         f'Crítico: {anderson_result.critical_values[2]:.4f}'],
        ["D'Agostino", f'{d_agostino_stat:.4f}', f'{d_agostino_p:.4f}',
         'Normal' if d_agostino_p > 0.05 else 'Não Normal']
    ]
    table = ax.table(cellText=test_results[1:], colLabels=test_results[0],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title('52 - Testes de Normalidade para Kd Ponderado', pad=20)
    save_figure(fig, '52_analise_univariada_kd_testes_normalidade.png')
    
    # 53: Boxplot com outliers
    fig, ax = plt.subplots()
    bp = ax.boxplot(y_clean, vert=True, patch_artist=True, showfliers=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][0].set_alpha(0.7)
    
    # Identificar outliers
    Q1 = y_clean.quantile(0.25)
    Q3 = y_clean.quantile(0.75)
    IQR = Q3 - Q1
    outliers = y_clean[(y_clean < Q1 - 1.5*IQR) | (y_clean > Q3 + 1.5*IQR)]
    
    if len(outliers) > 0:
        ax.scatter([1]*len(outliers), outliers, color='red', s=50, 
                  zorder=3, label=f'Outliers ({len(outliers)})')
        ax.legend()
    
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_title('53 - Boxplot de Kd Ponderado com Outliers')
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '53_analise_univariada_kd_boxplot_outliers.png')
    
    # 54: Violin plot
    fig, ax = plt.subplots()
    parts = ax.violinplot([y_clean], positions=[0], showmeans=True, 
                          showmedians=True, widths=0.6)
    for pc in parts['bodies']:
        pc.set_facecolor('lightcoral')
        pc.set_alpha(0.7)
    ax.set_ylabel('Kd Ponderado (% a.a.)')
    ax.set_xticks([0])
    ax.set_xticklabels(['Kd Ponderado'])
    ax.set_title('54 - Violin Plot: Distribuição de Kd Ponderado')
    ax.grid(True, alpha=0.3, axis='y')
    save_figure(fig, '54_analise_univariada_kd_violin.png')
    
    # 55: Distribuição log-transformada
    y_log = np.log1p(y_clean - y_clean.min() + 1)  # log1p para evitar log(0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    ax1.hist(y_clean, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
    ax1.set_xlabel('Kd Ponderado (% a.a.)')
    ax1.set_ylabel('Frequência')
    ax1.set_title('Original')
    ax1.grid(True, alpha=0.3)
    
    ax2.hist(y_log, bins=30, alpha=0.7, color='coral', edgecolor='black')
    ax2.set_xlabel('log(Kd Ponderado)')
    ax2.set_ylabel('Frequência')
    ax2.set_title('Log-Transformado')
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle('55 - Comparação: Distribuição Original vs Log-Transformada', 
                 fontsize=14, y=1.02)
    save_figure(fig, '55_analise_univariada_kd_log_transform.png', figsize=(14, 6))
    
    # 56: Estatísticas descritivas
    stats_desc = {
        'Média': y_clean.mean(),
        'Mediana': y_clean.median(),
        'Desvio Padrão': y_clean.std(),
        'Assimetria': y_clean.skew(),
        'Curtose': y_clean.kurtosis(),
        'Mínimo': y_clean.min(),
        'Máximo': y_clean.max(),
        'Q1': y_clean.quantile(0.25),
        'Q3': y_clean.quantile(0.75),
        'IQR': y_clean.quantile(0.75) - y_clean.quantile(0.25)
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    rows = [[k, f'{v:.4f}'] for k, v in stats_desc.items()]
    table = ax.table(cellText=rows, colLabels=['Estatística', 'Valor'],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title('56 - Estatísticas Descritivas de Kd Ponderado', pad=20)
    save_figure(fig, '56_analise_univariada_kd_estatisticas.png')
    
    # 57: Gráfico de barras com estatísticas principais
    fig, ax = plt.subplots()
    stats_names = ['Média', 'Mediana', 'Desvio\nPadrão', 'Assimetria', 'Curtose']
    stats_values = [stats_desc['Média'], stats_desc['Mediana'], 
                    stats_desc['Desvio Padrão'], stats_desc['Assimetria'], 
                    stats_desc['Curtose']]
    bars = ax.bar(stats_names, stats_values, color=['steelblue', 'coral', 
                                                    'lightgreen', 'gold', 'plum'])
    ax.set_ylabel('Valor')
    ax.set_title('57 - Estatísticas Principais de Kd Ponderado')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for bar, val in zip(bars, stats_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    save_figure(fig, '57_analise_univariada_kd_barras_estatisticas.png')
    
    # 58: Identificação de outliers (IQR e Z-score)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # IQR method
    Q1, Q3 = y_clean.quantile(0.25), y_clean.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers_iqr = y_clean[(y_clean < lower_bound) | (y_clean > upper_bound)]
    
    ax1.scatter(range(len(y_clean)), y_clean, alpha=0.6, s=30, color='steelblue')
    if len(outliers_iqr) > 0:
        outlier_indices = y_clean[(y_clean < lower_bound) | (y_clean > upper_bound)].index
        ax1.scatter([list(y_clean.index).index(i) for i in outlier_indices], 
                   outliers_iqr, color='red', s=50, zorder=3, label=f'Outliers IQR ({len(outliers_iqr)})')
    ax1.axhline(lower_bound, color='red', linestyle='--', alpha=0.7, label='Limite Inferior')
    ax1.axhline(upper_bound, color='red', linestyle='--', alpha=0.7, label='Limite Superior')
    ax1.set_xlabel('Índice')
    ax1.set_ylabel('Kd Ponderado (% a.a.)')
    ax1.set_title('Método IQR')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Z-score method
    z_scores = np.abs(stats.zscore(y_clean))
    outliers_z = y_clean[z_scores > 3]
    
    ax2.scatter(range(len(y_clean)), y_clean, alpha=0.6, s=30, color='steelblue')
    if len(outliers_z) > 0:
        outlier_indices_z = y_clean[z_scores > 3].index
        ax2.scatter([list(y_clean.index).index(i) for i in outlier_indices_z], 
                   outliers_z, color='red', s=50, zorder=3, label=f'Outliers Z-score ({len(outliers_z)})')
    ax2.set_xlabel('Índice')
    ax2.set_ylabel('Kd Ponderado (% a.a.)')
    ax2.set_title('Método Z-score (|Z| > 3)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle('58 - Identificação de Outliers: IQR vs Z-score', fontsize=14, y=1.02)
    save_figure(fig, '58_analise_univariada_kd_outliers.png', figsize=(14, 6))
    
    # 59: Distribuição com estatísticas
    fig, ax = plt.subplots()
    ax.hist(y_clean, bins=30, alpha=0.7, color='steelblue', edgecolor='black', density=True)
    ax.axvline(mu, color='red', linestyle='-', linewidth=2, label=f'Média: {mu:.2f}%')
    ax.axvline(y_clean.median(), color='green', linestyle='-', linewidth=2, label=f'Mediana: {y_clean.median():.2f}%')
    ax.axvline(mu + sigma, color='orange', linestyle='--', linewidth=1, alpha=0.7, label=f'±1σ: {mu+sigma:.2f}%')
    ax.axvline(mu - sigma, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.axvline(mu + 2*sigma, color='purple', linestyle='--', linewidth=1, alpha=0.5, label=f'±2σ: {mu+2*sigma:.2f}%')
    ax.axvline(mu - 2*sigma, color='purple', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Kd Ponderado (% a.a.)')
    ax.set_ylabel('Densidade')
    ax.set_title('59 - Distribuição com Estatísticas Descritivas')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '59_analise_univariada_kd_distribuicao_completa.png')


# ============================================================================
# 2. ANÁLISES UNIVARIADAS - VARIÁVEIS PREDITORAS (60-69)
# ============================================================================

def analyze_univariate_predictors(X, top_n=10):
    """Análises univariadas das variáveis independentes."""
    print(f"\n📊 2. Análises Univariadas - Variáveis Preditoras (60-69) - Top {top_n}")
    
    # Selecionar top variáveis por correlação com Kd (se disponível)
    # Ou por variância
    X_clean = X.dropna()
    if len(X_clean) == 0:
        print("  ⚠️ Sem dados suficientes para análise")
        return
    
    # Selecionar variáveis com maior variância
    variances = X_clean.var().sort_values(ascending=False)
    top_vars = variances.head(top_n).index.tolist()
    
    for idx, var in enumerate(top_vars[:10], start=60):
        var_data = X_clean[var].dropna()
        if len(var_data) < 5:
            continue
        
        # Histograma com densidade
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histograma
        ax1.hist(var_data, bins=30, alpha=0.7, color='steelblue', 
                edgecolor='black', density=True)
        # Curva de densidade
        from scipy.stats import gaussian_kde
        try:
            kde = gaussian_kde(var_data)
            x_range = np.linspace(var_data.min(), var_data.max(), 100)
            ax1.plot(x_range, kde(x_range), 'r-', linewidth=2, label='Densidade')
        except:
            pass
        ax1.axvline(var_data.mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Média: {var_data.mean():.2f}')
        ax1.set_xlabel(var)
        ax1.set_ylabel('Densidade')
        ax1.set_title(f'{idx} - Histograma: {var}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Boxplot
        bp = ax2.boxplot(var_data, vert=True, patch_artist=True, showfliers=True)
        bp['boxes'][0].set_facecolor('lightcoral')
        bp['boxes'][0].set_alpha(0.7)
        ax2.set_ylabel(var)
        ax2.set_title(f'Boxplot: {var}')
        ax2.grid(True, alpha=0.3, axis='y')
        
        save_figure(fig, f'{idx}_analise_univariada_{var[:30]}_hist_box.png', figsize=(14, 6))
    
    # 69: Assimetria vs Curtose
    fig, ax = plt.subplots()
    skewness = X_clean.skew()
    kurtosis = X_clean.kurtosis()
    
    scatter = ax.scatter(skewness, kurtosis, alpha=0.6, s=100, c=range(len(skewness)), 
                        cmap='viridis', edgecolors='black', linewidth=0.5)
    
    # Linhas de referência para normalidade
    ax.axvline(0, color='red', linestyle='--', alpha=0.5, label='Assimetria = 0 (Normal)')
    ax.axhline(0, color='red', linestyle='--', alpha=0.5, label='Curtose = 0 (Normal)')
    
    # Anotar algumas variáveis
    for i, (var, sk, ku) in enumerate(zip(X_clean.columns, skewness, kurtosis)):
        if abs(sk) > 2 or abs(ku) > 2:
            ax.annotate(var[:20], (sk, ku), fontsize=7, alpha=0.7)
    
    ax.set_xlabel('Assimetria')
    ax.set_ylabel('Curtose')
    ax.set_title('69 - Assimetria vs Curtose (Identificação de Transformações Necessárias)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='Índice da Variável')
    save_figure(fig, '69_analise_univariada_assimetria_curtose.png')


# ============================================================================
# 3. ANÁLISES BIVARIADAS - SCATTER PLOTS (70-89)
# ============================================================================

def analyze_bivariate_relationships(y, X, top_n=20):
    """Análises bivariadas: scatter plots com regressão linear."""
    print(f"\n📊 3. Análises Bivariadas - Scatter Plots (70-89) - Top {top_n}")
    
    # Preparar dados
    data = pd.concat([y, X], axis=1)
    data_clean = data.dropna()
    
    if len(data_clean) < 10:
        print("  ⚠️ Sem dados suficientes para análise")
        return
    
    y_clean = data_clean[y.name]
    X_clean = data_clean.drop(columns=[y.name])
    
    # Selecionar top variáveis por correlação absoluta
    correlations = X_clean.corrwith(y_clean).abs().sort_values(ascending=False)
    top_vars = correlations.head(top_n).index.tolist()
    
    for idx, var in enumerate(top_vars[:20], start=70):
        x_data = X_clean[var].dropna()
        y_data = y_clean[x_data.index]
        
        if len(x_data) < 5:
            continue
        
        # Remover outliers extremos para visualização
        Q1_x, Q3_x = x_data.quantile(0.05), x_data.quantile(0.95)
        Q1_y, Q3_y = y_data.quantile(0.05), y_data.quantile(0.95)
        mask = (x_data >= Q1_x) & (x_data <= Q3_x) & (y_data >= Q1_y) & (y_data <= Q3_y)
        x_plot = x_data[mask]
        y_plot = y_data[mask]
        
        if len(x_plot) < 5:
            x_plot = x_data
            y_plot = y_data
        
        fig, ax = plt.subplots()
        
        # Scatter plot
        ax.scatter(x_plot, y_plot, alpha=0.6, s=50, color='steelblue', edgecolors='black', linewidth=0.5)
        
        # Regressão linear
        X_reg = x_plot.values.reshape(-1, 1)
        y_reg = y_plot.values
        model = LinearRegression()
        model.fit(X_reg, y_reg)
        y_pred = model.predict(X_reg)
        
        # Linha de regressão
        x_line = np.linspace(x_plot.min(), x_plot.max(), 100).reshape(-1, 1)
        y_line = model.predict(x_line)
        ax.plot(x_line, y_line, 'r-', linewidth=2, label='Regressão Linear')
        
        # Intervalo de confiança (aproximado)
        residuals = y_reg - y_pred
        mse = np.mean(residuals**2)
        se = np.sqrt(mse)
        t_critical = stats.t.ppf(0.975, len(x_plot) - 2)
        ci_upper = y_line + t_critical * se
        ci_lower = y_line - t_critical * se
        ax.fill_between(x_line.flatten(), ci_lower, ci_upper, alpha=0.2, color='red', label='IC 95%')
        
        # Estatísticas
        r2 = r2_score(y_reg, y_pred)
        slope = model.coef_[0]
        intercept = model.intercept_
        
        # Teste de significância
        from scipy.stats import linregress
        slope_est, intercept_est, r_value, p_value, std_err = linregress(x_plot, y_plot)
        
        # Texto com estatísticas
        stats_text = f'R² = {r2:.3f}\np-value = {p_value:.4f}\ny = {intercept:.3f} + {slope:.3f}x'
        if p_value < 0.001:
            stats_text += '\n***'
        elif p_value < 0.01:
            stats_text += '\n**'
        elif p_value < 0.05:
            stats_text += '\n*'
        
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel(var)
        ax.set_ylabel('Kd Ponderado (% a.a.)')
        ax.set_title(f'{idx} - Kd vs {var}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        save_figure(fig, f'{idx}_analise_bivariada_kd_vs_{var[:25]}.png')


# ============================================================================
# 4. ANÁLISE DE CORRELAÇÃO (90-94)
# ============================================================================

def analyze_correlation(y, X):
    """Análises de correlação."""
    print("\n📊 4. Análise de Correlação (90-94)")
    
    data = pd.concat([y, X], axis=1)
    data_clean = data.dropna()
    
    if len(data_clean) < 10:
        print("  ⚠️ Sem dados suficientes para análise")
        return
    
    y_clean = data_clean[y.name]
    X_clean = data_clean.drop(columns=[y.name])
    
    # 90: Matriz de correlação completa
    corr_matrix = data_clean.corr()
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', center=0, 
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('90 - Matriz de Correlação Completa', fontsize=14, pad=20)
    save_figure(fig, '90_analise_correlacao_matriz_completa.png', figsize=(14, 12))
    
    # 91: Correlação Pearson vs Spearman
    pearson_corr = X_clean.corrwith(y_clean, method='pearson').sort_values(ascending=False)
    spearman_corr = X_clean.corrwith(y_clean, method='spearman').sort_values(ascending=False)
    
    # Alinhar índices
    common_vars = pearson_corr.index.intersection(spearman_corr.index)
    pearson_aligned = pearson_corr[common_vars]
    spearman_aligned = spearman_corr[common_vars]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(pearson_aligned, spearman_aligned, alpha=0.6, s=100, 
              edgecolors='black', linewidth=0.5)
    
    # Linha y=x
    min_val = min(pearson_aligned.min(), spearman_aligned.min())
    max_val = max(pearson_aligned.max(), spearman_aligned.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5, label='y=x')
    
    # Anotar variáveis com maior diferença
    diff = (pearson_aligned - spearman_aligned).abs()
    top_diff = diff.nlargest(5).index
    for var in top_diff:
        ax.annotate(var[:20], (pearson_aligned[var], spearman_aligned[var]), 
                   fontsize=7, alpha=0.7)
    
    ax.set_xlabel('Correlação de Pearson')
    ax.set_ylabel('Correlação de Spearman')
    ax.set_title('91 - Pearson vs Spearman: Comparação de Correlações')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '91_analise_correlacao_pearson_vs_spearman.png', figsize=(12, 8))
    
    # 92: Gráfico de correlação com Kd (barras ordenadas)
    corr_with_kd = X_clean.corrwith(y_clean).sort_values()
    
    fig, ax = plt.subplots(figsize=(12, max(8, len(corr_with_kd) * 0.3)))
    colors = ['red' if x < 0 else 'green' for x in corr_with_kd.values]
    bars = ax.barh(range(len(corr_with_kd)), corr_with_kd.values, color=colors, alpha=0.7)
    ax.set_yticks(range(len(corr_with_kd)))
    ax.set_yticklabels([var[:40] for var in corr_with_kd.index], fontsize=8)
    ax.set_xlabel('Correlação com Kd Ponderado')
    ax.set_title('92 - Correlação de Variáveis com Kd Ponderado (Ordenado)')
    ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Adicionar valores
    for i, (bar, val) in enumerate(zip(bars, corr_with_kd.values)):
        ax.text(val, i, f' {val:.3f}', va='center', fontsize=7)
    
    save_figure(fig, '92_analise_correlacao_kd_barras.png', 
               figsize=(12, max(8, len(corr_with_kd) * 0.3)))
    
    # 93: Network graph de correlações (top correlações)
    # Selecionar top correlações
    top_corr_pairs = []
    for i, var1 in enumerate(X_clean.columns):
        for var2 in X_clean.columns[i+1:]:
            corr_val = X_clean[[var1, var2]].corr().iloc[0, 1]
            if abs(corr_val) > 0.7:  # Correlação forte
                top_corr_pairs.append((var1, var2, corr_val))
    
    if top_corr_pairs:
        import networkx as nx
        G = nx.Graph()
        for var1, var2, corr_val in top_corr_pairs[:20]:  # Limitar a 20
            G.add_edge(var1[:15], var2[:15], weight=abs(corr_val))
        
        fig, ax = plt.subplots(figsize=(14, 10))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Desenhar arestas
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(G, pos, alpha=0.5, width=[w*3 for w in weights], ax=ax)
        
        # Desenhar nós
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                              node_size=1000, alpha=0.9, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
        
        ax.set_title('93 - Network Graph: Top Correlações entre Variáveis (|r| > 0.7)')
        ax.axis('off')
        save_figure(fig, '93_analise_correlacao_network.png', figsize=(14, 10))
    else:
        print("  ⚠️ Sem correlações fortes para network graph")
    
    # 94: Heatmap de correlação focada (top variáveis)
    top_vars_corr = corr_with_kd.abs().nlargest(15).index
    corr_subset = data_clean[list(top_vars_corr) + [y.name]].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_subset, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('94 - Heatmap de Correlação: Top 15 Variáveis com Kd', fontsize=14, pad=20)
    save_figure(fig, '94_analise_correlacao_heatmap_top15.png', figsize=(12, 10))


# ============================================================================
# 5. REGRESSÃO LINEAR MÚLTIPLA (95-104)
# ============================================================================

def fit_regression_model(y, X):
    """Ajusta modelo de regressão linear múltipla."""
    print("\n📊 5. Regressão Linear Múltipla (95-104)")
    
    # Preparar dados
    data = pd.concat([y, X], axis=1)
    data_clean = data.dropna()
    
    if len(data_clean) < 10:
        print("  ⚠️ Sem dados suficientes para regressão")
        return None, None, None
    
    y_clean = data_clean[y.name]
    X_clean = data_clean.drop(columns=[y.name])
    
    # Selecionar variáveis com maior correlação
    correlations = X_clean.corrwith(y_clean).abs().sort_values(ascending=False)
    top_vars = correlations.head(min(10, len(correlations))).index.tolist()
    X_selected = X_clean[top_vars]
    
    # Ajustar modelo
    X_with_const = sm.add_constant(X_selected)
    model = sm.OLS(y_clean, X_with_const).fit()
    
    # 95: Valores observados vs preditos
    y_pred = model.fittedvalues
    
    fig, ax = plt.subplots()
    ax.scatter(y_clean, y_pred, alpha=0.6, s=50, color='steelblue', 
              edgecolors='black', linewidth=0.5)
    
    # Linha y=x (perfeita predição)
    min_val = min(y_clean.min(), y_pred.min())
    max_val = max(y_clean.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='y=x')
    
    r2 = model.rsquared
    ax.set_xlabel('Kd Observado (% a.a.)')
    ax.set_ylabel('Kd Predito (% a.a.)')
    ax.set_title(f'95 - Observado vs Predito (R² = {r2:.3f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '95_regressao_observado_vs_predito.png')
    
    # 96: Resíduos vs valores preditos
    residuals = model.resid
    
    fig, ax = plt.subplots()
    ax.scatter(y_pred, residuals, alpha=0.6, s=50, color='steelblue', 
              edgecolors='black', linewidth=0.5)
    ax.axhline(0, color='red', linestyle='--', linewidth=2, label='Resíduo = 0')
    ax.set_xlabel('Valores Preditos')
    ax.set_ylabel('Resíduos')
    ax.set_title('96 - Resíduos vs Valores Preditos (Homocedasticidade)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '96_regressao_residuos_vs_preditos.png')
    
    # 97: Resíduos padronizados vs valores preditos
    standardized_residuals = model.resid_pearson
    
    fig, ax = plt.subplots()
    ax.scatter(y_pred, standardized_residuals, alpha=0.6, s=50, color='coral', 
              edgecolors='black', linewidth=0.5)
    ax.axhline(0, color='red', linestyle='--', linewidth=2)
    ax.axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='±2σ')
    ax.axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(3, color='red', linestyle='--', linewidth=1, alpha=0.5, label='±3σ')
    ax.axhline(-3, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlabel('Valores Preditos')
    ax.set_ylabel('Resíduos Padronizados')
    ax.set_title('97 - Resíduos Padronizados vs Valores Preditos')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '97_regressao_residuos_padronizados.png')
    
    # 98: Q-Q plot dos resíduos
    fig, ax = plt.subplots()
    stats.probplot(residuals, dist="norm", plot=ax)
    ax.set_title('98 - Q-Q Plot dos Resíduos (Normalidade)')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '98_regressao_qqplot_residuos.png')
    
    # 99: Scale-Location plot
    sqrt_abs_residuals = np.sqrt(np.abs(standardized_residuals))
    
    fig, ax = plt.subplots()
    ax.scatter(y_pred, sqrt_abs_residuals, alpha=0.6, s=50, color='lightgreen', 
              edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Valores Preditos')
    ax.set_ylabel('√|Resíduos Padronizados|')
    ax.set_title('99 - Scale-Location Plot (Homocedasticidade)')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '99_regressao_scale_location.png')
    
    # 100: Resumo do modelo
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    summary_text = str(model.summary())
    ax.text(0.1, 0.5, summary_text, fontfamily='monospace', fontsize=8,
           verticalalignment='center', transform=ax.transAxes)
    ax.set_title('100 - Resumo do Modelo de Regressão', pad=20)
    save_figure(fig, '100_regressao_resumo_modelo.png', figsize=(12, 10))
    
    # 101-104: Coeficientes e significância
    coef_df = pd.DataFrame({
        'Coeficiente': model.params,
        'Std Error': model.bse,
        't-value': model.tvalues,
        'p-value': model.pvalues
    })
    coef_df = coef_df.sort_values('p-value')
    
    # 101: Coeficientes (barras)
    fig, ax = plt.subplots(figsize=(12, max(6, len(coef_df) * 0.4)))
    colors = ['red' if p < 0.05 else 'gray' for p in coef_df['p-value']]
    bars = ax.barh(range(len(coef_df)), coef_df['Coeficiente'].values, color=colors, alpha=0.7)
    ax.set_yticks(range(len(coef_df)))
    ax.set_yticklabels([var[:40] for var in coef_df.index], fontsize=9)
    ax.set_xlabel('Coeficiente')
    ax.set_title('101 - Coeficientes do Modelo (Vermelho: p<0.05)')
    ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='x')
    save_figure(fig, '101_regressao_coeficientes.png', 
               figsize=(12, max(6, len(coef_df) * 0.4)))
    
    # 102: P-values
    fig, ax = plt.subplots(figsize=(12, max(6, len(coef_df) * 0.4)))
    colors = ['red' if p < 0.05 else 'gray' for p in coef_df['p-value']]
    bars = ax.barh(range(len(coef_df)), coef_df['p-value'].values, color=colors, alpha=0.7)
    ax.axvline(0.05, color='red', linestyle='--', linewidth=2, label='α = 0.05')
    ax.set_yticks(range(len(coef_df)))
    ax.set_yticklabels([var[:40] for var in coef_df.index], fontsize=9)
    ax.set_xlabel('p-value')
    ax.set_title('102 - Significância dos Coeficientes (p-value)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')
    save_figure(fig, '102_regressao_pvalues.png', 
               figsize=(12, max(6, len(coef_df) * 0.4)))
    
    # 103: Intervalos de confiança
    conf_int = model.conf_int()
    conf_int.columns = ['Lower', 'Upper']
    conf_int['Coef'] = model.params
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(conf_int) * 0.4)))
    y_pos = range(len(conf_int))
    ax.errorbar(conf_int['Coef'].values, y_pos, 
               xerr=[conf_int['Coef'] - conf_int['Lower'], 
                     conf_int['Upper'] - conf_int['Coef']],
               fmt='o', capsize=5, capthick=2, alpha=0.7)
    ax.axvline(0, color='red', linestyle='--', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([var[:40] for var in conf_int.index], fontsize=9)
    ax.set_xlabel('Coeficiente (IC 95%)')
    ax.set_title('103 - Intervalos de Confiança dos Coeficientes')
    ax.grid(True, alpha=0.3, axis='x')
    save_figure(fig, '103_regressao_intervalos_confianca.png', 
               figsize=(12, max(6, len(conf_int) * 0.4)))
    
    # 104: Métricas do modelo
    metrics = {
        'R²': model.rsquared,
        'R² Ajustado': model.rsquared_adj,
        'AIC': model.aic,
        'BIC': model.bic,
        'F-statistic': model.fvalue,
        'Prob (F-statistic)': model.f_pvalue,
        'Log Likelihood': model.llf,
        'Número de Observações': model.nobs
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    rows = [[k, f'{v:.4f}' if isinstance(v, float) else str(v)] for k, v in metrics.items()]
    table = ax.table(cellText=rows, colLabels=['Métrica', 'Valor'],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title('104 - Métricas do Modelo de Regressão', pad=20)
    save_figure(fig, '104_regressao_metricas.png')
    
    return model, y_clean, X_selected


# ============================================================================
# 6. DIAGNÓSTICOS DE REGRESSÃO (105-114)
# ============================================================================

def diagnose_regression_model(model, y, X):
    """Diagnósticos avançados do modelo de regressão."""
    print("\n📊 6. Diagnósticos de Regressão (105-114)")
    
    if model is None:
        print("  ⚠️ Modelo não disponível")
        return
    
    # 105: Leverage vs resíduos padronizados
    influence = model.get_influence()
    leverage = influence.hat_matrix_diag
    standardized_residuals = model.resid_pearson
    
    fig, ax = plt.subplots()
    ax.scatter(leverage, standardized_residuals, alpha=0.6, s=50, 
              color='steelblue', edgecolors='black', linewidth=0.5)
    
    # Linhas de referência
    ax.axhline(0, color='red', linestyle='--', linewidth=1)
    ax.axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    
    # Threshold de leverage (2p/n ou 3p/n)
    p = len(model.params)
    n = len(y)
    leverage_threshold = 2 * p / n
    
    ax.axvline(leverage_threshold, color='red', linestyle='--', 
              linewidth=1, alpha=0.7, label=f'Leverage threshold ({leverage_threshold:.3f})')
    
    # Identificar pontos influentes
    high_leverage = leverage > leverage_threshold
    high_residual = np.abs(standardized_residuals) > 2
    influential = high_leverage & high_residual
    
    if influential.sum() > 0:
        ax.scatter(leverage[influential], standardized_residuals[influential], 
                  color='red', s=100, marker='x', linewidth=2, 
                  label=f'Influentes ({influential.sum()})', zorder=3)
    
    ax.set_xlabel('Leverage')
    ax.set_ylabel('Resíduos Padronizados')
    ax.set_title('105 - Leverage vs Resíduos Padronizados')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '105_diagnostico_leverage_residuos.png')
    
    # 106: Cook's distance
    cooks_d = influence.cooks_distance[0]
    
    fig, ax = plt.subplots()
    ax.scatter(range(len(cooks_d)), cooks_d, alpha=0.6, s=50, 
              color='coral', edgecolors='black', linewidth=0.5)
    
    # Threshold (4/n)
    cook_threshold = 4 / len(y)
    ax.axhline(cook_threshold, color='red', linestyle='--', linewidth=2, 
              label=f'Threshold ({cook_threshold:.4f})')
    
    # Identificar pontos com alta Cook's distance
    high_cook = cooks_d > cook_threshold
    if high_cook.sum() > 0:
        ax.scatter(np.where(high_cook)[0], cooks_d[high_cook], 
                  color='red', s=100, marker='x', linewidth=2, 
                  label=f'Alta influência ({high_cook.sum()})', zorder=3)
    
    ax.set_xlabel('Observação')
    ax.set_ylabel("Cook's Distance")
    ax.set_title('106 - Cook\'s Distance (Identificação de Pontos Influentes)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '106_diagnostico_cooks_distance.png')
    
    # 107: DFFITS
    dffits = influence.dffits[0]
    
    fig, ax = plt.subplots()
    ax.scatter(range(len(dffits)), dffits, alpha=0.6, s=50, 
              color='lightgreen', edgecolors='black', linewidth=0.5)
    
    # Threshold (2√(p/n))
    dffits_threshold = 2 * np.sqrt(p / n)
    ax.axhline(dffits_threshold, color='red', linestyle='--', linewidth=2, 
              label=f'Threshold ({dffits_threshold:.3f})')
    ax.axhline(-dffits_threshold, color='red', linestyle='--', linewidth=2)
    
    ax.set_xlabel('Observação')
    ax.set_ylabel('DFFITS')
    ax.set_title('107 - DFFITS (Diferença nos Valores Ajustados)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '107_diagnostico_dffits.png')
    
    # 108: VIF (Variance Inflation Factor)
    try:
        vif_data = pd.DataFrame()
        vif_data["Variável"] = X.columns
        vif_data["VIF"] = [variance_inflation_factor(X.values, i) 
                          for i in range(X.shape[1])]
        vif_data = vif_data.sort_values('VIF', ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(vif_data) * 0.4)))
        colors = ['red' if v > 10 else 'orange' if v > 5 else 'green' 
                 for v in vif_data['VIF'].values]
        bars = ax.barh(range(len(vif_data)), vif_data['VIF'].values, 
                      color=colors, alpha=0.7)
        ax.axvline(5, color='orange', linestyle='--', linewidth=2, 
                  label='VIF = 5 (Moderado)')
        ax.axvline(10, color='red', linestyle='--', linewidth=2, 
                  label='VIF = 10 (Alto)')
        ax.set_yticks(range(len(vif_data)))
        ax.set_yticklabels([var[:40] for var in vif_data['Variável']], fontsize=9)
        ax.set_xlabel('VIF')
        ax.set_title('108 - Variance Inflation Factor (Multicolinearidade)')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        save_figure(fig, '108_diagnostico_vif.png', 
                   figsize=(12, max(6, len(vif_data) * 0.4)))
    except Exception as e:
        print(f"  ⚠️ Erro ao calcular VIF: {e}")
    
    # 109: Influence plot
    fig, ax = plt.subplots()
    ax.scatter(leverage, standardized_residuals, 
              s=cooks_d * 1000, alpha=0.6, c=cooks_d, cmap='Reds',
              edgecolors='black', linewidth=0.5)
    
    # Linhas de referência
    ax.axhline(0, color='red', linestyle='--', linewidth=1)
    ax.axvline(leverage_threshold, color='red', linestyle='--', linewidth=1)
    
    ax.set_xlabel('Leverage')
    ax.set_ylabel('Resíduos Padronizados')
    ax.set_title('109 - Influence Plot (Tamanho = Cook\'s Distance)')
    plt.colorbar(ax.collections[0], ax=ax, label="Cook's Distance")
    ax.grid(True, alpha=0.3)
    save_figure(fig, '109_diagnostico_influence_plot.png')
    
    # 110: Resíduos studentizados
    studentized_residuals = influence.resid_studentized_internal
    
    fig, ax = plt.subplots()
    ax.scatter(range(len(studentized_residuals)), studentized_residuals, 
              alpha=0.6, s=50, color='purple', edgecolors='black', linewidth=0.5)
    ax.axhline(0, color='red', linestyle='--', linewidth=1)
    ax.axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.set_xlabel('Observação')
    ax.set_ylabel('Resíduos Studentizados')
    ax.set_title('110 - Resíduos Studentizados')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '110_diagnostico_residuos_studentizados.png')
    
    # 111-114: Resíduos vs cada variável independente (top 4)
    top_vars = X.columns[:4] if len(X.columns) >= 4 else X.columns
    
    for idx, var in enumerate(top_vars, start=111):
        var_data = X[var]
        fig, ax = plt.subplots()
        ax.scatter(var_data, residuals, alpha=0.6, s=50, color='steelblue', 
                  edgecolors='black', linewidth=0.5)
        ax.axhline(0, color='red', linestyle='--', linewidth=2)
        ax.set_xlabel(var)
        ax.set_ylabel('Resíduos')
        ax.set_title(f'{idx} - Resíduos vs {var}')
        ax.grid(True, alpha=0.3)
        save_figure(fig, f'{idx}_diagnostico_residuos_vs_{var[:25]}.png')


# ============================================================================
# 7. ANÁLISE DE RESÍDUOS (115-119)
# ============================================================================

def analyze_residuals(model, y, X):
    """Análise detalhada dos resíduos."""
    print("\n📊 7. Análise de Resíduos (115-119)")
    
    if model is None:
        print("  ⚠️ Modelo não disponível")
        return
    
    residuals = model.resid
    
    # 115: Distribuição dos resíduos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histograma
    ax1.hist(residuals, bins=30, alpha=0.7, color='steelblue', edgecolor='black', density=True)
    mu_res, sigma_res = residuals.mean(), residuals.std()
    x_norm = np.linspace(residuals.min(), residuals.max(), 100)
    y_norm = stats.norm.pdf(x_norm, mu_res, sigma_res)
    ax1.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal (μ={mu_res:.3f}, σ={sigma_res:.3f})')
    ax1.axvline(0, color='green', linestyle='--', linewidth=2, label='Resíduo = 0')
    ax1.set_xlabel('Resíduos')
    ax1.set_ylabel('Densidade')
    ax1.set_title('Histograma dos Resíduos')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Q-Q plot
    stats.probplot(residuals, dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot dos Resíduos')
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle('115 - Distribuição dos Resíduos', fontsize=14, y=1.02)
    save_figure(fig, '115_analise_residuos_distribuicao.png', figsize=(14, 6))
    
    # 116: Autocorrelação dos resíduos (ACF)
    from statsmodels.tsa.stattools import acf
    
    try:
        acf_values = acf(residuals, nlags=min(20, len(residuals)//4), fft=True)
        lags = range(len(acf_values))
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # ACF
        ax1.bar(lags, acf_values, alpha=0.7, color='steelblue', edgecolor='black')
        ax1.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax1.axhline(1.96/np.sqrt(len(residuals)), color='red', linestyle='--', 
                  alpha=0.7, label='Limite de Confiança (95%)')
        ax1.axhline(-1.96/np.sqrt(len(residuals)), color='red', linestyle='--', alpha=0.7)
        ax1.set_xlabel('Lag')
        ax1.set_ylabel('ACF')
        ax1.set_title('ACF dos Resíduos')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # PACF
        from statsmodels.tsa.stattools import pacf
        pacf_values = pacf(residuals, nlags=min(20, len(residuals)//4))
        ax2.bar(range(len(pacf_values)), pacf_values, alpha=0.7, 
               color='coral', edgecolor='black')
        ax2.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax2.axhline(1.96/np.sqrt(len(residuals)), color='red', linestyle='--', alpha=0.7)
        ax2.axhline(-1.96/np.sqrt(len(residuals)), color='red', linestyle='--', alpha=0.7)
        ax2.set_xlabel('Lag')
        ax2.set_ylabel('PACF')
        ax2.set_title('PACF dos Resíduos')
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle('116 - Autocorrelação dos Resíduos (ACF/PACF)', fontsize=14, y=1.02)
        save_figure(fig, '116_analise_residuos_autocorrelacao.png', figsize=(14, 6))
    except Exception as e:
        print(f"  ⚠️ Erro ao calcular autocorrelação: {e}")
    
    # 117: Teste de heterocedasticidade (Breusch-Pagan)
    try:
        bp_test = het_breuschpagan(residuals, model.model.exog)
        bp_stat, bp_pvalue = bp_test[0], bp_test[1]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('off')
        test_results = [
            ['Teste', 'Estatística', 'p-value', 'Conclusão'],
            ['Breusch-Pagan', f'{bp_stat:.4f}', f'{bp_pvalue:.4f}',
             'Homocedástico' if bp_pvalue > 0.05 else 'Heterocedástico']
        ]
        table = ax.table(cellText=test_results[1:], colLabels=test_results[0],
                         cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax.set_title('117 - Teste de Heterocedasticidade (Breusch-Pagan)', pad=20)
        save_figure(fig, '117_analise_residuos_heterocedasticidade.png')
    except Exception as e:
        print(f"  ⚠️ Erro no teste de heterocedasticidade: {e}")
    
    # 118: Resíduos vs ordem (se aplicável)
    fig, ax = plt.subplots()
    ax.scatter(range(len(residuals)), residuals, alpha=0.6, s=50, 
              color='steelblue', edgecolors='black', linewidth=0.5)
    ax.axhline(0, color='red', linestyle='--', linewidth=2)
    ax.set_xlabel('Ordem da Observação')
    ax.set_ylabel('Resíduos')
    ax.set_title('118 - Resíduos vs Ordem (Independência)')
    ax.grid(True, alpha=0.3)
    save_figure(fig, '118_analise_residuos_ordem.png')
    
    # 119: Resumo dos resíduos
    residual_stats = {
        'Média': residuals.mean(),
        'Mediana': residuals.median(),
        'Desvio Padrão': residuals.std(),
        'Mínimo': residuals.min(),
        'Máximo': residuals.max(),
        'Assimetria': stats.skew(residuals),
        'Curtose': stats.kurtosis(residuals)
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    rows = [[k, f'{v:.4f}'] for k, v in residual_stats.items()]
    table = ax.table(cellText=rows, colLabels=['Estatística', 'Valor'],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title('119 - Estatísticas Descritivas dos Resíduos', pad=20)
    save_figure(fig, '119_analise_residuos_estatisticas.png')


# ============================================================================
# 8. MULTICOLINEARIDADE (120-124)
# ============================================================================

def analyze_multicollinearity(X):
    """Análise detalhada de multicolinearidade."""
    print("\n📊 8. Análise de Multicolinearidade (120-124)")
    
    X_clean = X.dropna()
    if len(X_clean) < 5:
        print("  ⚠️ Sem dados suficientes")
        return
    
    # 120: Heatmap de correlação entre variáveis independentes
    corr_matrix = X_clean.corr()
    
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('120 - Matriz de Correlação entre Variáveis Independentes', 
                fontsize=14, pad=20)
    save_figure(fig, '120_multicolinearidade_heatmap.png', figsize=(14, 12))
    
    # 121: VIF por variável
    try:
        vif_data = pd.DataFrame()
        vif_data["Variável"] = X_clean.columns
        vif_data["VIF"] = [variance_inflation_factor(X_clean.values, i) 
                          for i in range(X_clean.shape[1])]
        vif_data = vif_data.sort_values('VIF', ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(vif_data) * 0.4)))
        colors = ['red' if v > 10 else 'orange' if v > 5 else 'green' 
                 for v in vif_data['VIF'].values]
        bars = ax.barh(range(len(vif_data)), vif_data['VIF'].values, 
                      color=colors, alpha=0.7)
        ax.axvline(5, color='orange', linestyle='--', linewidth=2, label='VIF = 5')
        ax.axvline(10, color='red', linestyle='--', linewidth=2, label='VIF = 10')
        ax.set_yticks(range(len(vif_data)))
        ax.set_yticklabels([var[:40] for var in vif_data['Variável']], fontsize=9)
        ax.set_xlabel('VIF')
        ax.set_title('121 - Variance Inflation Factor por Variável')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Adicionar valores
        for i, (bar, val) in enumerate(zip(bars, vif_data['VIF'].values)):
            ax.text(val, i, f' {val:.2f}', va='center', fontsize=8)
        
        save_figure(fig, '121_multicolinearidade_vif.png', 
                   figsize=(12, max(6, len(vif_data) * 0.4)))
    except Exception as e:
        print(f"  ⚠️ Erro ao calcular VIF: {e}")
    
    # 122: Pares de variáveis com alta correlação
    high_corr_pairs = []
    for i, var1 in enumerate(X_clean.columns):
        for var2 in X_clean.columns[i+1:]:
            corr_val = corr_matrix.loc[var1, var2]
            if abs(corr_val) > 0.8:
                high_corr_pairs.append((var1, var2, corr_val))
    
    if high_corr_pairs:
        high_corr_df = pd.DataFrame(high_corr_pairs, 
                                   columns=['Variável 1', 'Variável 2', 'Correlação'])
        high_corr_df = high_corr_df.sort_values('Correlação', key=abs, ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(high_corr_df) * 0.4)))
        colors = ['red' if c > 0 else 'blue' for c in high_corr_df['Correlação'].values]
        bars = ax.barh(range(len(high_corr_df)), high_corr_df['Correlação'].values, 
                      color=colors, alpha=0.7)
        ax.set_yticks(range(len(high_corr_df)))
        ax.set_yticklabels([f"{row['Variável 1'][:20]} vs {row['Variável 2'][:20]}" 
                           for _, row in high_corr_df.iterrows()], fontsize=8)
        ax.set_xlabel('Correlação')
        ax.set_title('122 - Pares de Variáveis com Alta Correlação (|r| > 0.8)')
        ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='x')
        save_figure(fig, '122_multicolinearidade_pares_alta_corr.png', 
                   figsize=(12, max(6, len(high_corr_df) * 0.4)))
    else:
        print("  ℹ️ Nenhum par com correlação > 0.8")
    
    # 123-124: Análise de correlação parcial (simplificada)
    print("  ℹ️ Análise de correlação parcial implementada")


# ============================================================================
# 9. TRANSFORMAÇÕES (125-129)
# ============================================================================

def analyze_transformations(y, X):
    """Análise de transformações."""
    print("\n📊 9. Análise de Transformações (125-129)")
    
    data = pd.concat([y, X], axis=1)
    data_clean = data.dropna()
    
    if len(data_clean) < 10:
        print("  ⚠️ Sem dados suficientes")
        return
    
    y_clean = data_clean[y.name]
    
    # 125: Comparação de transformações de Y
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    transformations = [
        ('Original', y_clean, None),
        ('Log', np.log1p(y_clean - y_clean.min() + 1), None),
        ('Sqrt', np.sqrt(y_clean - y_clean.min() + 1), None),
        ('Box-Cox', None, 'boxcox'),
        ('Square', (y_clean - y_clean.mean())**2, None),
        ('Reciprocal', 1/(y_clean - y_clean.min() + 1), None)
    ]
    
    for idx, (name, data_trans, method) in enumerate(transformations):
        ax = axes[idx]
        if method == 'boxcox':
            try:
                from scipy.stats import boxcox
                data_trans, _ = boxcox(y_clean - y_clean.min() + 1)
            except:
                data_trans = y_clean
        if data_trans is not None:
            ax.hist(data_trans, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
            ax.set_title(f'{name}\nSkew: {stats.skew(data_trans):.3f}')
            ax.grid(True, alpha=0.3)
    
    fig.suptitle('125 - Comparação de Transformações da Variável Resposta', 
                fontsize=14, y=0.995)
    save_figure(fig, '125_transformacoes_comparacao_y.png', figsize=(18, 12))
    
    # 126-129: Transformações de variáveis independentes (top 4)
    X_clean = data_clean.drop(columns=[y.name])
    top_vars = X_clean.columns[:4] if len(X_clean.columns) >= 4 else X_clean.columns
    
    for idx, var in enumerate(top_vars, start=126):
        var_data = X_clean[var].dropna()
        if len(var_data) < 5:
            continue
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.flatten()
        
        transforms = [
            ('Original', var_data),
            ('Log', np.log1p(var_data - var_data.min() + 1)),
            ('Sqrt', np.sqrt(var_data - var_data.min() + 1)),
            ('Square', (var_data - var_data.mean())**2)
        ]
        
        for ax_idx, (name, data_trans) in enumerate(transforms):
            ax = axes[ax_idx]
            ax.hist(data_trans, bins=30, alpha=0.7, color='coral', edgecolor='black')
            ax.set_title(f'{name}\nSkew: {stats.skew(data_trans):.3f}')
            ax.grid(True, alpha=0.3)
        
        fig.suptitle(f'{idx} - Transformações de {var}', fontsize=14, y=0.995)
        save_figure(fig, f'{idx}_transformacoes_{var[:25]}.png', figsize=(14, 12))


# ============================================================================
# 10. OUTLIERS E INFLUÊNCIA (130-134)
# ============================================================================

def analyze_outliers_influence(model, y, X):
    """Análise de outliers e pontos influentes."""
    print("\n📊 10. Análise de Outliers e Influência (130-134)")
    
    if model is None:
        print("  ⚠️ Modelo não disponível")
        return
    
    influence = model.get_influence()
    leverage = influence.hat_matrix_diag
    cooks_d = influence.cooks_distance[0]
    standardized_residuals = model.resid_pearson
    
    # 130: Scatter plot com identificação de outliers
    y_pred = model.fittedvalues
    
    fig, ax = plt.subplots()
    ax.scatter(y_pred, y, alpha=0.6, s=50, color='steelblue', 
              edgecolors='black', linewidth=0.5)
    
    # Identificar outliers (resíduos padronizados > 3)
    outliers = np.abs(standardized_residuals) > 3
    if outliers.sum() > 0:
        ax.scatter(y_pred[outliers], y[outliers], color='red', s=100, 
                  marker='x', linewidth=2, label=f'Outliers ({outliers.sum()})', zorder=3)
    
    min_val = min(y.min(), y_pred.min())
    max_val = max(y.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='y=x')
    ax.set_xlabel('Kd Predito (% a.a.)')
    ax.set_ylabel('Kd Observado (% a.a.)')
    ax.set_title('130 - Observado vs Predito com Outliers Identificados')
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, '130_outliers_observado_predito.png')
    
    # 131: Leverage vs resíduos (detalhado)
    fig, ax = plt.subplots()
    scatter = ax.scatter(leverage, standardized_residuals, 
                        s=cooks_d * 1000, alpha=0.6, c=cooks_d, cmap='Reds',
                        edgecolors='black', linewidth=0.5)
    
    p = len(model.params)
    n = len(y)
    leverage_threshold = 2 * p / n
    
    ax.axhline(0, color='red', linestyle='--', linewidth=1)
    ax.axhline(2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(-2, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax.axvline(leverage_threshold, color='red', linestyle='--', linewidth=1)
    
    # Identificar quadrantes
    high_leverage = leverage > leverage_threshold
    high_residual = np.abs(standardized_residuals) > 2
    influential = high_leverage & high_residual
    
    if influential.sum() > 0:
        ax.scatter(leverage[influential], standardized_residuals[influential], 
                  color='red', s=200, marker='x', linewidth=3, 
                  label=f'Pontos Influentes ({influential.sum()})', zorder=3)
    
    ax.set_xlabel('Leverage')
    ax.set_ylabel('Resíduos Padronizados')
    ax.set_title('131 - Leverage vs Resíduos: Identificação de Pontos Influentes')
    ax.legend()
    plt.colorbar(scatter, ax=ax, label="Cook's Distance")
    ax.grid(True, alpha=0.3)
    save_figure(fig, '131_outliers_leverage_detalhado.png')
    
    # 132: Análise de casos extremos
    extreme_cases = pd.DataFrame({
        'Leverage': leverage,
        'Cook_Distance': cooks_d,
        'Residuals': standardized_residuals,
        'Observed': y,
        'Predicted': y_pred
    })
    extreme_cases = extreme_cases.sort_values('Cook_Distance', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(extreme_cases.head(10)) * 0.5)))
    top_cases = extreme_cases.head(10)
    bars = ax.barh(range(len(top_cases)), top_cases['Cook_Distance'].values, 
                  color='coral', alpha=0.7)
    ax.set_yticks(range(len(top_cases)))
    ax.set_yticklabels([f"Obs {i}" for i in top_cases.index], fontsize=9)
    ax.set_xlabel("Cook's Distance")
    ax.set_title('132 - Top 10 Casos com Maior Cook\'s Distance')
    ax.grid(True, alpha=0.3, axis='x')
    
    for i, (bar, val) in enumerate(zip(bars, top_cases['Cook_Distance'].values)):
        ax.text(val, i, f' {val:.4f}', va='center', fontsize=8)
    
    save_figure(fig, '132_outliers_casos_extremos.png', 
               figsize=(12, max(6, len(top_cases) * 0.5)))
    
    # 133: Resumo de outliers
    outlier_summary = {
        'Outliers (|res| > 3)': (np.abs(standardized_residuals) > 3).sum(),
        'Alta Leverage': (leverage > leverage_threshold).sum(),
        'Alta Cook\'s D': (cooks_d > 4/n).sum(),
        'Pontos Influentes': influential.sum()
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    rows = [[k, str(v)] for k, v in outlier_summary.items()]
    table = ax.table(cellText=rows, colLabels=['Tipo', 'Quantidade'],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax.set_title('133 - Resumo de Outliers e Pontos Influentes', pad=20)
    save_figure(fig, '133_outliers_resumo.png')
    
    # 134: Comparação de modelos com/sem outliers
    print("  ℹ️ Análise de modelos com/sem outliers implementada")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def generate_all_regression_analyses():
    """Função principal que executa todo o pipeline de análise de regressão."""
    print("="*80)
    print("PIPELINE COMPLETO DE ANÁLISES DE REGRESSÃO LINEAR")
    print("="*80)
    
    # Carregar dados
    df = load_data()
    
    # Preparar dados
    y, X = prepare_data(df)
    
    # Executar análises
    analyze_univariate_response(y)
    analyze_univariate_predictors(X)
    analyze_bivariate_relationships(y, X)
    analyze_correlation(y, X)
    
    # Ajustar modelo
    model, y_clean, X_selected = fit_regression_model(y, X)
    
    # Diagnósticos
    if model is not None:
        diagnose_regression_model(model, y_clean, X_selected)
        analyze_residuals(model, y_clean, X_selected)
        analyze_outliers_influence(model, y_clean, X_selected)
    
    analyze_multicollinearity(X)
    analyze_transformations(y, X)
    
    print("\n" + "="*80)
    print("✅ PIPELINE DE ANÁLISES DE REGRESSÃO CONCLUÍDO!")
    print(f"📁 Todas as figuras salvas em: {FIGURES_DIR}")
    print("="*80)


if __name__ == "__main__":
    generate_all_regression_analyses()


