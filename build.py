import os
import subprocess
import sys
import shutil

TEX_DIR = 'tex'
MAIN_TEX = 'main.tex'
BUILD_DIR = 'build'
PDF_NAME = 'TCC_Final.pdf'

def clean():
    """Clean up build artifacts."""
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    # Also clean root pdf if needed, but usually we keep it.

def generate_figures():
    """Run python scripts to generate figures."""
    print("Generating figures...")
    # Example: Run all scripts in src/ that start with 'generate_'
    src_dir = 'src'
    for filename in os.listdir(src_dir):
        if filename.startswith('generate_') and filename.endswith('.py'):
            filepath = os.path.join(src_dir, filename)
            print(f"Running {filepath}...")
            subprocess.run([sys.executable, filepath], check=True)

def compile_tex():
    """Compile LaTeX document using pdflatex."""
    print("Compiling LaTeX...")
    
    # Create build directory if it doesn't exist to keep root clean
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)
        
    # Create chapters directory in build for auxiliary files
    build_chapters = os.path.join(BUILD_DIR, 'chapters')
    if not os.path.exists(build_chapters):
        os.makedirs(build_chapters)

    # We need to run pdflatex multiple times for references
    # Using -output-directory to keep things clean
    cmd = [
        'pdflatex',
        '-interaction=nonstopmode',
        f'-output-directory=../{BUILD_DIR}',
        MAIN_TEX
    ]
    
    # Run from TEX_DIR so relative paths in tex file work
    try:
        # Pass 1
        subprocess.run(cmd, cwd=TEX_DIR, check=True)
        
        # Bibtex (if references.bib exists)
        if os.path.exists(os.path.join(TEX_DIR, 'references.bib')):
            subprocess.run(['bibtex', os.path.splitext(MAIN_TEX)[0]], cwd=BUILD_DIR, check=False)
            
        # Pass 2 & 3
        subprocess.run(cmd, cwd=TEX_DIR, check=True)
        subprocess.run(cmd, cwd=TEX_DIR, check=True)
        
        # Move PDF to root
        src_pdf = os.path.join(BUILD_DIR, os.path.splitext(MAIN_TEX)[0] + '.pdf')
        dst_pdf = PDF_NAME
        shutil.copy(src_pdf, dst_pdf)
        print(f"Success! PDF generated at: {dst_pdf}")
        
    except subprocess.CalledProcessError as e:
        print("Error compiling LaTeX.")
        print(e)
    except FileNotFoundError:
        print("Error: pdflatex not found. Please install a LaTeX distribution (e.g., MacTeX).")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--figures':
        generate_figures()
    
    compile_tex()
