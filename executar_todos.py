import subprocess
import time

# Lista dos scripts a serem executados na ordem correta
scripts = [
    r"C:\Users\facun\OneDrive\Desktop\01_scrapdou\final_code\coletar_todos.py",
    r"C:\Users\facun\OneDrive\Desktop\01_scrapdou\final_code\baixar_todos.py",
    r"C:\Users\facun\OneDrive\Desktop\01_scrapdou\final_code\trans_mte.py",
    r"C:\Users\facun\OneDrive\Desktop\01_scrapdou\final_code\trans_ibama.py",
   
]

# Função para executar um script
def executar_script(script):
    try:
        print(f"Executando {script}...")
        subprocess.run(["python", script], check=True)
        print(f"{script} executado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script}: {e}")

# Executar todos os scripts com intervalo de 15 segundos
for script in scripts:
    executar_script(script)
    time.sleep(15)

print("Todos os scripts foram executados.")
