import subprocess
import sys
import os

# ==========================================
# CONFIGURAÇÕES DO EXECUTÁVEL
# ==========================================
EXE_NAME = "GeradorFormulario"  # Altere aqui o nome do executável (.exe)
# ==========================================

# Descobre o diretório deste arquivo build.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

print(f"Iniciando a compilação do executável: {EXE_NAME}.exe...")

# Usamos o interpretador de Python ativo no momento
python_exe = sys.executable

# Comando do PyInstaller estruturado
cmd = [
    python_exe, "-m", "PyInstaller",
    "--clean",
    "-y",
    "--onefile",
    "--noconsole",
    f"--name={EXE_NAME}",
    f"--add-data=credentials/client_secret.json;credentials",
    "--hidden-import=googleapiclient.discovery",
    "--hidden-import=googleapiclient.errors",
    "--hidden-import=google.oauth2.credentials",
    "--hidden-import=google_auth_oauthlib.flow",
    "--hidden-import=google.auth.transport.requests",
    "--hidden-import=ttkbootstrap",
    "--collect-all=ttkbootstrap",
    "--hidden-import=pyperclip",
    "--collect-all=pyperclip",
    # Define onde as pastas 'build' e 'dist' serão criadas (dentro de formGenerator_app)
    f"--distpath={os.path.join(current_dir, 'dist')}",
    f"--workpath={os.path.join(current_dir, 'build')}",
    os.path.join(current_dir, "run_form_generator.py")
]

print("\nExecutando comando no terminal:")
print(" ".join(cmd))
print("\nPor favor, aguarde a compilação...")

try:
    # Garante que o diretório raiz esteja no PYTHONPATH para que o PyInstaller encontre o pacote formGenerator_app
    env = os.environ.copy()
    env["PYTHONPATH"] = parent_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    # Executa a compilação
    result = subprocess.run(cmd, cwd=current_dir, env=env, check=True)
    
    print("\n" + "="*50)
    print("SUCESSO!")
    print(f"O executável foi gerado em: {os.path.join(current_dir, 'dist', EXE_NAME + '.exe')}")
    print("="*50)
except Exception as e:
    print("\n" + "!"*50)
    print(f"ERRO durante a compilação: {e}")
    print("!"*50)
