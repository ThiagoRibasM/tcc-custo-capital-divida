#!/usr/bin/env python3
"""
Pipeline de Regressão Linear Múltipla: Determinantes do Kd

Este script executa a análise econométrica completa para o TCC:
1. Carregamento e Tratamento de Dados
2. Seleção de Variáveis (Domínio -> VIF -> Stepwise)
3. Estimação OLS (com correção robusta se necessário)
4. Diagnósticos e Report

Autor: Pipeline TCC
Data: Janeiro 2026
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_white, het_breuschpagan
import statsmodels.stats.api as sms
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH, FIGURES_DIR, REPORTS_DIR
from src.visualization import styles
styles.apply_style()

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES
# -----------------------------------------------------------------------------
# Categorias para pré-seleção (evitar redundância óbvia)
# -----------------------------------------------------------------------------
# CONFIGURAÇÕES
# -----------------------------------------------------------------------------
# Categorias para pré-seleção (evitar redundância óbvia)
FEATURE_GROUPS = {
    'Alavancagem': ['Divida_Total_Ativo', 'Divida_Total_PL', 'Alavancagem_Total', 'Divida_Liquida_Ativo', 'Proporcao_Divida_CP', 'Proporcao_Divida_LP'],
    'Liquidez': ['Liquidez_Corrente', 'Liquidez_Imediata', 'Cobertura_Caixa_Divida'],
    'Rentabilidade': ['ROA', 'ROE', 'Margem_Bruta', 'Margem_Operacional', 'Margem_Liquida', 'Margem_EBITDA'],
    'Cobertura': ['Cobertura_Juros', 'Divida_EBITDA'],
    'Adicionais': ['Tamanho', 'Tangibilidade', 'Capital_Giro_Liquido', 'Intensidade_Capex', 'Geracao_Caixa_Op'],
    'Heterogeneidade': ['IHH_Indexador', 'IHH_Tipo', 'Indice_Diversificacao']
}

TARGET_COL = 'Kd_Ponderado'

# -----------------------------------------------------------------------------
# FUNÇÕES
# -----------------------------------------------------------------------------

def load_data_raw():
    """Carrega dados e converte para numérico."""
    df = pd.read_csv(CONSOLIDATED_PATH / "tabela_features.csv")
    
    # Garantir que Kd existe
    df = df.dropna(subset=[TARGET_COL])
    
    # Todas as features candidatas
    all_features = []
    for group_cols in FEATURE_GROUPS.values():
        all_features.extend(group_cols)
        
    # Validar quais existem
    valid_features = [c for c in all_features if c in df.columns]
    
    # Converter para numérico (forçar NaN em erros)
    cols_to_convert = valid_features + [TARGET_COL]
    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Remover outliers extremos de Kd para não sujar a correlação inicial
    # Z-score > 4 apenas no target
    z_scores_kd = np.abs(stats.zscore(df[TARGET_COL]))
    df = df[z_scores_kd < 4].copy()
        
    print(f"Dados Carregados: {len(df)} empresas")
    return df, valid_features

def winsorize_features(df, features, lower=0.01, upper=0.99):
    """Aplica winsorização (clipping) nas features para reduzir outliers."""
    df_winsorized = df.copy()
    for col in features:
        if col in df_winsorized.columns:
            q_low = df_winsorized[col].quantile(lower)
            q_high = df_winsorized[col].quantile(upper)
            df_winsorized[col] = df_winsorized[col].clip(q_low, q_high)
    return df_winsorized

def impute_missing_knn(df, features, n_neighbors=5):
    """
    Imputação inteligente via KNN (K-Nearest Neighbors).
    Usa as K empresas mais similares para estimar valores faltantes.
    """
    from sklearn.impute import KNNImputer
    from sklearn.preprocessing import StandardScaler
    
    # Separar features para imputação
    df_features = df[features].copy()
    
    # Normalizar antes do KNN (importante para distância euclidiana)
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler.fit_transform(df_features), 
        columns=features, 
        index=df_features.index
    )
    
    # Aplicar KNN Imputer
    imputer = KNNImputer(n_neighbors=n_neighbors, weights='distance')
    df_imputed_scaled = imputer.fit_transform(df_scaled)
    
    # Reverter normalização
    df_imputed = pd.DataFrame(
        scaler.inverse_transform(df_imputed_scaled),
        columns=features,
        index=df_features.index
    )
    
    # Contar imputações
    n_missing_before = df_features.isna().sum().sum()
    n_missing_after = df_imputed.isna().sum().sum()
    
    print(f"Imputação KNN (k={n_neighbors}): {n_missing_before} valores imputados.")
    
    # Atualizar DataFrame original
    df_result = df.copy()
    df_result[features] = df_imputed
    
    return df_result

def get_clean_dataset(df, selected_features):
    """Retorna dataset limpo com imputação KNN, winsorização e dropna apenas no target."""
    cols = selected_features + [TARGET_COL]
    df_subset = df[cols].copy()
    
    # 1. Imputação KNN para features (preserva empresas)
    df_imputed = impute_missing_knn(df_subset, selected_features, n_neighbors=5)
    
    # 2. Dropna apenas no target (Kd é obrigatório)
    df_clean = df_imputed.dropna(subset=[TARGET_COL])
    
    # 3. Winsorização 1%-99% para reduzir impacto de outliers
    df_clean = winsorize_features(df_clean, selected_features, lower=0.01, upper=0.99)
    
    print(f"Dataset pronto para modelagem: {len(df_clean)} obs (usando {len(selected_features)} features)")
    return df_clean

def pre_select_features(df, valid_features):
    """
    Retorna todas as features candidatas para análise.
    Anteriormente limitava a 1 por grupo, agora deixa o VIF/Stepwise decidir.
    """
    print("\n--- Seleção de Candidatos ---")
    print(f"Considerando todas as {len(valid_features)} features definidas nos grupos.")
    return valid_features

def check_vif(df, features, threshold=5.0):
    """Verifica VIF e sugere remoção."""
    X = df[features]
    X = sm.add_constant(X)
    
    vif_data = pd.DataFrame()
    vif_data["Feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    
    # Remover constante da tabela
    vif_data = vif_data[vif_data["Feature"] != "const"]
    
    # Ordenar
    vif_data = vif_data.sort_values(by="VIF", ascending=False)
    
    print("\n--- Verificação Multicolinearidade (VIF) ---")
    print(vif_data)
    
    high_vif = vif_data[vif_data["VIF"] > threshold]["Feature"].tolist()
    
    if high_vif:
        worst = high_vif[0]
        print(f"⚠️ VIF Alto detectado ({vif_data.iloc[0]['VIF']:.2f}). Removendo: {worst}")
        features.remove(worst)
        # Recursivo
        return check_vif(df, features, threshold)
    
    return features

def stepwise_selection(df, features, significance_level=0.15):
    """Backward Elimination baseada em P-valor (Flexibilizado para 0.15)."""
    initial_features = features.copy()
    y = df[TARGET_COL]
    
    print(f"\n--- Seleção Stepwise Backward (p-value < {significance_level}) ---")
    
    while len(features) > 0:
        X = sm.add_constant(df[features])
        model = sm.OLS(y, X).fit()
        p_values = model.pvalues.drop('const')
        
        max_p_value = p_values.max()
        if max_p_value > significance_level:
            excluded_feature = p_values.idxmax()
            print(f"Removendo: {excluded_feature:25} (p-value: {max_p_value:.4f})")
            features.remove(excluded_feature)
        else:
            print("Nenhuma variável acima do nível de significância para remover.")
            break
    
    print(f"Vars Iniciais: {len(initial_features)} -> Finais: {len(features)}")
    return features

def run_diagnostics(model):
    """Executa testes de diagnóstico nos resíduos."""
    results = {}
    
    # 1. Normalidade (Jarque-Bera)
    jb_stat, jb_p = stats.jarque_bera(model.resid)
    results['Jarque-Bera p-val'] = jb_p
    
    # 2. Heterocedasticidade (Breusch-Pagan)
    # H0: Homocedasticidade (Variância constante)
    bp_test = het_breuschpagan(model.resid, model.model.exog)
    results['Breusch-Pagan p-val'] = bp_test[1]
    
    # 3. Heterocedasticidade (White)
    white_test = het_white(model.resid, model.model.exog)
    results['White p-val'] = white_test[1]
    
    return results

def plot_diagnostics(model, output_path):
    """
    Gera painel de diagnóstico visual (Figura 5) baseado em pilares econométricos:
    1. Ajuste (Fit Quality): Observado vs Predito
    2. Estrutura (Linearity/Homoscedasticity): Resíduos vs Fitted
    3. Normalidade (Normality): Q-Q Plot
    4. Influência (Robustness): Distância de Cook
    """
    fig = plt.figure(figsize=(12, 10))
    fig.suptitle('Figura 5: Diagnóstico do Modelo Final OLS', fontsize=12, fontweight='bold', y=0.96)
    
    # Grid 2x2
    gs = fig.add_gridspec(2, 2, wspace=0.3, hspace=0.3)
    
    # ---------------------------------------------------------
    # A. QUALIDADE DO AJUSTE (Actual vs Predicted)
    # ---------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    y_true = model.model.endog
    y_pred = model.fittedvalues
    
    # Scatter
    sns.scatterplot(x=y_pred, y=y_true, alpha=0.6, edgecolor='k', ax=ax1, color=styles.COLORS['secondary'])
    
    # Linha Ideal (45 graus)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', lw=1.5, label='Ideal (Perfeito)')
    
    # Linha de Regressão do Fit
    sns.regplot(x=y_pred, y=y_true, scatter=False, ax=ax1, color='blue', truncate=False, 
                line_kws={'lw': 1, 'alpha': 0.5, 'label': 'Tendência Real'})

    ax1.set_title('(a) Qualidade do Ajuste ($R^2$ Visual)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Kd Predito (%)')
    ax1.set_ylabel('Kd Observado (%)')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.2)
    
    # ---------------------------------------------------------
    # B. VIOLAÇÃO DE PRESSUPOSTOS (Residuals vs Fitted)
    # ---------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    resid = model.resid
    
    sns.scatterplot(x=y_pred, y=resid, alpha=0.6, edgecolor='k', ax=ax2, color=styles.COLORS['secondary'])
    ax2.axhline(0, color=styles.COLORS['primary'], linestyle='--', lw=1.5)
    
    # Lowess para detectar não-linearidade
    sns.regplot(x=y_pred, y=resid, scatter=False, lowess=True, ax=ax2, color='blue', 
                line_kws={'lw': 1.5, 'alpha': 0.8})
                
    ax2.set_title('(b) Homocedasticidade & Linearidade', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Kd Predito')
    ax2.set_ylabel('Resíduos')
    ax2.grid(True, alpha=0.2)

    # ---------------------------------------------------------
    # C. NORMALIDADE (Normal Q-Q Plot)
    # ---------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    (osm, osr), (slope, intercept, r) = stats.probplot(resid, dist="norm", plot=None)
    
    ax3.scatter(osm, osr, alpha=0.6, edgecolor='k', color=styles.COLORS['secondary'])
    ax3.plot(osm, slope * osm + intercept, color=styles.COLORS['primary'], lw=1.5, linestyle='-')
    
    ax3.set_title(f'(c) Normalidade dos Resíduos ($R^2$={r**2:.2f})', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Quantis Teóricos (Normal)')
    ax3.set_ylabel('Quantis Observados')
    ax3.grid(True, alpha=0.2)
    
    # ---------------------------------------------------------
    # D. INFLUÊNCIA (Cook's Distance)
    # ---------------------------------------------------------
    # Detecta pontos que mudam o modelo se removidos
    ax4 = fig.add_subplot(gs[1, 1])
    influence = model.get_influence()
    cooks = influence.cooks_distance[0]
    n = len(cooks)
    
    # Threshold padrão (4/n)
    threshold = 4 / n
    
    # Stem plot manual para controle estético
    ax4.vlines(range(n), 0, cooks, color=styles.COLORS['secondary'], alpha=0.4)
    ax4.scatter(range(n), cooks, s=15, color=styles.COLORS['secondary'], alpha=0.8)
    
    # Linha de corte
    ax4.axhline(threshold, color=styles.COLORS['primary'], linestyle='--', lw=1.5, label=f'Limiar (4/n = {threshold:.2f})')
    
    # Identificar outliers extremos
    outlier_indices = np.where(cooks > threshold)[0]
    # Marcar top 3
    top_3_indices = np.argsort(cooks)[-3:]
    
    for idx in top_3_indices:
        if cooks[idx] > threshold:
            ax4.text(idx, cooks[idx], f'{idx}', fontsize=8, ha='right', va='bottom', fontweight='bold')

    ax4.set_title('(d) Observações Influentes (Cook\'s D)', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Índice da Empresa')
    ax4.set_ylabel('Distância de Cook')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.2)
    
    # Salvar
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

def main():
    print("="*60)
    print("PIPELINE DE REGRESSÃO: DETERMINANTES DO KD")
    print("="*60)
    
    # 1. Carregar Dados Brutos
    df, valid_features = load_data_raw()
    
    # 2. Seleção de Features (baseada em correlação pairwise com todo dataset)
    candidate_features = pre_select_features(df, valid_features)
    
    # 3. Preparar Dataset Limpo para Modelagem
    df_clean = get_clean_dataset(df, candidate_features)
    
    if len(df_clean) < 50:
        print("❌ Erro: Dataset muito pequeno após remoção de NaNs.")
        return

    # 4. VIF Check
    candidate_features = check_vif(df_clean, candidate_features)
    
    # 5. Stepwise
    final_features = stepwise_selection(df_clean, candidate_features)
    
    if not final_features:
        print("❌ Erro: Nenhuma variável restou no modelo.")
        return
    
    print(f"\n→ Features Finais: {final_features}")

    # 6. Remoção de Outliers Influentes (Cook's Distance > 4/n)
    print("\n--- Remoção de Outliers Influentes (Cook's Distance) ---")
    
    # Primeiro ajuste para identificar outliers
    X_temp = sm.add_constant(df_clean[final_features])
    y_temp = df_clean[TARGET_COL]
    model_temp = sm.OLS(y_temp, X_temp).fit()
    
    # Calcular Cook's Distance
    influence = model_temp.get_influence()
    cooks = influence.cooks_distance[0]
    n = len(cooks)
    threshold = 4 / n
    
    # Identificar e remover outliers
    outlier_mask = cooks > threshold
    n_outliers = outlier_mask.sum()
    
    if n_outliers > 0:
        print(f"⚠️ {n_outliers} observações com Cook's D > {threshold:.3f} identificadas.")
        df_clean = df_clean[~outlier_mask].copy()
        print(f"   Dataset reduzido de {n} para {len(df_clean)} observações.")
    else:
        print(f"✓ Nenhuma observação com Cook's D > {threshold:.3f}.")

    # 7. Modelo Final OLS (pós-limpeza)
    print("\n--- Modelo OLS Final (pós-limpeza) ---")
    X = sm.add_constant(df_clean[final_features])
    y = df_clean[TARGET_COL]
    
    model = sm.OLS(y, X).fit()
    
    # 6. Diagnósticos
    print("\n--- Diagnósticos ---")
    diag = run_diagnostics(model)
    print(f"Normalidade (Jarque-Bera p-val): {diag['Jarque-Bera p-val']:.4f}")
    if diag['Jarque-Bera p-val'] < 0.05:
        print("  ⚠️ Resíduos NÃO são normais.")
    else:
        print("  ✓ Resíduos Normais.")
        
    print(f"Heterocedasticidade (Breusch-Pagan p-val): {diag['Breusch-Pagan p-val']:.4f}")
    
    # 7. Correção Robusta (se necessário)
    if diag['Breusch-Pagan p-val'] < 0.05 or diag['White p-val'] < 0.05:
        print("\n⚠️ Heterocedasticidade detectada! Reestimando com Robust Errors (HC3)...")
        robust_model = sm.OLS(y, X).fit(cov_type='HC3')
        print(robust_model.summary())
        final_model_to_plot = robust_model
    else:
        print("\n✓ Homocedasticidade aceita. Mantendo OLS padrão.")
        print(model.summary())
        final_model_to_plot = model

    # 8. Salvar Resultados
    output_fig = FIGURES_DIR / "fig05_regression_diagnostics.png"
    plot_diagnostics(final_model_to_plot, output_fig)
    print(f"\n✓ Diagnósticos visuais salvos em: {output_fig}")
    
    # Salvar tabela formatada
    output_txt = REPORTS_DIR / "modelo_final_summary.txt"
    with open(output_txt, 'w') as f:
        f.write(final_model_to_plot.summary().as_text())
    print(f"✓ Sumário do modelo salvo em: {output_txt}")
    
    print("="*60)

if __name__ == "__main__":
    main()
