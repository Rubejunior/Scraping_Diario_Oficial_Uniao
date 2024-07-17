import os
import csv
import requests
import logging
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Caminhos padrão para acessar os links gerados pelo programa coletar_todos.py
BASE_INPUT_DIR = r"C:\Users\facun\OneDrive\Desktop\01_scrapdou\final_code\link_todos" # Caminhos padrão para acessar os links gerados pelo programa coletar_todos.py
BASE_OUTPUT_DIR = r"C:\Users\facun\OneDrive\Desktop\01_scrapdou\final_code\json_todos" # Saída dos dados coeltados em formato json

# Função para obter acesso completo de um link \ no meu caso coletou os dados corretamnte para três diferentes ministérios, mas você pode ter algum desfio aqui visto a falta de padronização dos dados públicos. (o que é lamentável) 
def get_full_content(url: str) -> dict:
    try:
        logging.info(f"Requisitando conteúdo completo da URL: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        content_div = soup.find("div", class_="texto-dou")
        if not content_div:
            return {"text": "", "table": ""}

        text_content = content_div.get_text(separator="\n", strip=True)

        table_content = ""
        table = content_div.find("table", class_="dou-table")
        if table:
            rows = table.find_all("tr")
            table_data = []
            for row in rows:
                cols = row.find_all("td")
                cols = [col.get_text(separator="\n", strip=True) for col in cols]
                table_data.append(cols)
            table_content = table_data

        return {"text": text_content, "table": table_content}
    except Exception as err:
        logging.error(f"Erro ao obter o conteúdo da URL {url}: {err}")
        return {"text": "", "table": ""} #foi muito importante para melhorar o codigoo acessando diretamente o link e comparando com os dados json, eu optei em capturar tudo e no próximo código realizar a organização dos dados, visto mais uma vez a falta de padronização, e como agora os dados estão em seu banco de dados esse acesso e tratamento fica mais prático.

# Função para ler o CSV e coletar os dados completos
def process_csv_and_save_as_json(csv_file: str, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_date = datetime.now().strftime('%Y-%m-%d')

    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row['url']
            full_content = get_full_content(url)
            row['full_text_content'] = full_content["text"]
            row['full_table_content'] = full_content["table"]

            # Criar nome de arquivo baseado na URL e incluir a data atual
            filename = os.path.join(output_dir, f"{url.split('/')[-1]}_{current_date}.json")
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(row, jsonfile, ensure_ascii=False, indent=4)

            logging.info(f"Dados salvos em {filename}")

# Função para encontrar o arquivo CSV mais recente na pasta especificada / essa função é importante para meu caso de buscas diárias 
def find_latest_csv(input_dir: str) -> str:
    csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado no diretório especificado.")
    latest_csv = max(csv_files, key=os.path.getctime)
    return latest_csv

# Exemplo de uso
def process_files(org):
    input_dir = os.path.join(BASE_INPUT_DIR, org)
    output_dir = os.path.join(BASE_OUTPUT_DIR, org)

    try:
        csv_file = find_latest_csv(input_dir)
        logging.info(f"Lendo dados do CSV: {csv_file}")
        logging.info(f"Salvando dados JSON no diretório: {output_dir}")
        process_csv_and_save_as_json(csv_file, output_dir)
    except FileNotFoundError as e:
        logging.error(f"Erro ao processar arquivos para {org}: {e}")
    except Exception as e:
        logging.error(f"Erro geral ao processar arquivos para {org}: {e}")

if __name__ == "__main__":
    orgs = ["MTE", "IBAMA", "PREV"]
    for org in orgs:
        process_files(org)
