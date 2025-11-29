"""
Configurações centralizadas de paths do projeto.
"""
import os
from pathlib import Path

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Paths de dados
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_EXTERNAL = PROJECT_ROOT / "data" / "external"

# Paths específicos
DFP_2024_PATH = DATA_RAW / "dfp_2024"
ITR_2024_PATH = DATA_RAW / "itr_2024"
DFP_NOVO_MERCADO_PATH = DFP_2024_PATH / "DFPs_CVM" / "Novo_Mercado"
LLM_EXTRACTIONS_PATH = DATA_PROCESSED / "llm_extractions"
CONSOLIDATED_PATH = DATA_PROCESSED / "consolidated"
REFERENCES_PATH = DATA_EXTERNAL / "references"

# Paths de notebooks (para referência)
NOTEBOOKS_ROOT = PROJECT_ROOT / "notebooks"

# Paths de relatórios
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Função helper para criar diretórios se não existirem
def ensure_dirs():
    """Cria todos os diretórios necessários se não existirem."""
    for path in [DATA_RAW, DATA_PROCESSED, DATA_EXTERNAL, 
                 LLM_EXTRACTIONS_PATH, CONSOLIDATED_PATH, REFERENCES_PATH,
                 REPORTS_DIR, FIGURES_DIR]:
        path.mkdir(parents=True, exist_ok=True)

