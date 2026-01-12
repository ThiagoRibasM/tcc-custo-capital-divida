import matplotlib.pyplot as plt
import numpy as np
import os

# Ensure output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'figures')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def main():
    # Data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Sine Wave', color='#D64045') # Using TCC color palette
    plt.title('Exemplo de Gráfico Gerado via Python')
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Save
    output_path = os.path.join(OUTPUT_DIR, 'exemplo_plot.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Generated {output_path}")

if __name__ == '__main__':
    main()
