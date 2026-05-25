import subprocess
import sys
import os

# ==========================================
# CONFIGURAÇÕES DO EXECUTÁVEL
# ==========================================
EXE_NAME = "AnalisadorMDS"  # Nome da pasta e do executável (.exe)
# ==========================================

# Descobre o diretório deste arquivo build.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

print(f"Iniciando a compilação do executável (modo pasta - onedir): {EXE_NAME}...")

# Usamos o interpretador de Python ativo no momento (.venv)
python_exe = sys.executable

# Comando do PyInstaller estruturado para Modo Pasta (onedir)
cmd = [
    python_exe, "-m", "PyInstaller",
    "--clean",
    "-y",
    "--onedir",                      # Modo Pasta (onedir)
    "--noconsole",                   # Oculta console
    f"--name={EXE_NAME}",
    "--hidden-import=pandas",
    "--hidden-import=numpy",
    "--hidden-import=matplotlib",
    "--hidden-import=matplotlib.backends.backend_tkagg",
    "--collect-all=tksheet",
    "--hidden-import=scipy.spatial.distance",
    "--hidden-import=xlsxwriter",
    "--hidden-import=openpyxl",
    # Define onde as pastas 'build' e 'dist' serão criadas (dentro de mds_app)
    f"--distpath={os.path.join(current_dir, 'dist')}",
    f"--workpath={os.path.join(current_dir, 'build')}",
    os.path.join(current_dir, "run.py")
]

print("\nExecutando comando no terminal:")
print(" ".join(cmd))
print("\nPor favor, aguarde a compilação...")

try:
    # Garante que o diretório raiz esteja no PYTHONPATH para que o PyInstaller encontre o pacote mds_app
    env = os.environ.copy()
    env["PYTHONPATH"] = parent_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    # Executa a compilação
    result = subprocess.run(cmd, cwd=current_dir, env=env, check=True)
    
    print("\n" + "="*50)
    print("SUCESSO!")
    print(f"O executável (modo pasta) foi gerado em: {os.path.join(current_dir, 'dist', EXE_NAME)}")
    print("="*50)
except Exception as e:
    print("\n" + "!"*50)
    print(f"ERRO durante a compilação: {e}")
    print("!"*50)
