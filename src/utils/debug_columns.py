import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import CONSOLIDATED_PATH

try:
    df = pd.read_csv(CONSOLIDATED_PATH / "indicadores_financeiros_completos.csv")
    print("Columns:")
    for col in df.columns:
        print(col)
except Exception as e:
    print(f"Error: {e}")
