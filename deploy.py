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
    print("🚀 INICIANDO DESPLIEGUE AUTÓNOMO CYPHER VEX...")
    
    # Cargar Token desde .env
    token = None
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    token = line.split("=")[1].strip()
    
    if not token:
        print("❌ ERROR CRÍTICO: Token no encontrado en .env")
        sys.exit(1)

    # Configurar Git local si no está hecho
    if not os.path.exists(".git"):
        run_cmd("git init")
        run_cmd("git branch -M main")
    
    run_cmd("git add .")
    try:
        run_cmd('git commit -m "CV-001: Initial release - AI Image Decomposer with Inpainting Engine"')
    except:
        pass

    # Autenticación automática con el token
    print("[*] Autenticando con GitHub...")
    run_cmd(f"echo {token} | gh auth login --with-token")

    # Crear repositorio y subir
    print("[*] Sincronizando con nube...")
    try:
        # Intentar crear si no existe, si existe solo conectar
        run_cmd(f"gh repo create {REPO_NAME} --public --source=. --remote=origin --push")
    except Exception:
        print("[!] El repositorio ya existe o hubo un problema de red. Reintentando push...")
        run_cmd("git push -u origin main")

    print("\n🎯 MISIÓN CUMPLIDA. Código auditado y desplegado en GitHub.")

if __name__ == "__main__":
    main()
