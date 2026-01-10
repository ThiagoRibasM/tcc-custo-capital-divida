#!/usr/bin/env python3
"""
Download de Ícones para Figura 2
Baixa ícones PNG transparentes do Wikimedia Commons para src/visualization/assets/
"""

import requests
from pathlib import Path
import sys

# Setup de diretórios
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "src" / "visualization" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento: Nome do Arquivo -> URL de Download (Icons8 CDN - Validado)
ICONS = {
    "db_icon.png": "https://img.icons8.com/color/128/database.png",
    "pdf_icon.png": "https://img.icons8.com/color/128/pdf-2.png",
    "ai_icon.png": "https://img.icons8.com/color/128/artificial-intelligence.png",
    "csv_icon.png": "https://img.icons8.com/color/128/csv.png"
}

def download_file(url, target_path):
    print(f"Baixando {target_path.name}...")
    headers = {'User-Agent': 'TCC-Research-Bot/1.0 (Educational Purpose)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        with open(target_path, 'wb') as f:
            f.write(response.content)
        print(" -> Sucesso!")
        return True
    except Exception as e:
        print(f" -> Erro: {e}")
        return False

def main():
    print(f"Iniciando download de ícones para: {ASSETS_DIR}")
    
    success_count = 0
    for filename, url in ICONS.items():
        target = ASSETS_DIR / filename
        if download_file(url, target):
            success_count += 1
            
    print("-" * 40)
    print(f"Download concluído: {success_count}/{len(ICONS)} ícones salvos.")

if __name__ == "__main__":
    main()
