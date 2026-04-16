import os
import subprocess
import sys

REPO_NAME = "cv-001-imagedecomposer"
GITHUB_USER = "cyph3rv3x"

def run_cmd(cmd):
    print(f"[*] Executing: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ SUCCESS")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {e.stderr}")
        sys.exit(1)

def main():
    print("🚀 INICIANDO DESPLIEGUE CYPHER VEX - MODO SUPERVIVENCIA...")
    
    if not os.path.exists(".git"):
        run_cmd("git init")
    
    # Generar estructura faltante si no existe para commit íntegro
    run_cmd("git add .")
    
    try:
        run_cmd('git commit -m "CV-001: Initial release - AI Image Decomposer with Inpainting Engine"')
    except Exception:
        print("[!] Nada que comitear o ya comiteado.")

    run_cmd("git branch -M main")
    
    print("\n=======================================================")
    print(f"[*] Repositorio preparado: https://github.com/{GITHUB_USER}/{REPO_NAME}.git")
    print("[!] Para finalizar la publicación ejecuta:")
    print(f"    gh repo create {REPO_NAME} --public --source=. --remote=origin --push")
    print("=======================================================\n")
    print("🎯 Herramienta de élite lista para aniquilar la competencia.")

if __name__ == "__main__":
    main()
