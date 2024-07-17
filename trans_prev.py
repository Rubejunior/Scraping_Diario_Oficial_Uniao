import os
import re
import json
import logging
import time
from datetime import datetime
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Caminhos padrão
DEFAULT_INPUT_DIR = r"C:\path"
DEFAULT_OUTPUT_DIR = r"C:\path"

# Função para extrair dados do JSON
def extract_data_from_json(json_content):
    data = []
    
    # Regex para capturar dados do full_text_content # no caso do ibama a busca 
    pattern = re.compile(
        r'([\w\s]+) \(NB: (\d+), CPF: (\d{3})\*{5}\d{2}(?:, Protocolo: (\d+))?(?:, Representante Legal: ([\w\s]+), CPF (\d{3})\*{5}\d{2})?\)' #o cpf não é importante em meu estudo mas uso o os 3 primeiros digitod o cpf como chave para distinguir determinada pessoa e seu representante, mas isso eu não faço nesse codigo, apenas deixo preparado para facilitar analise lá na frente, tudo vai depender do seu estudo, no meu caso para garantir não ocorrer duplicadas e não coleta de dados no programa a frente eu uso CPF (3 digitos fornecidos pela união) e NOME como key.
    
    full_text_content = json_content.get('full_text_content', '')
    matches = pattern.findall(full_text_content)
    
    for match in matches:
        data.append({
            "NOME": match[0],
            "NB": match[1],
            "CPF": match[2],  # Manter apenas os 3 primeiros dígitos #mais uma vez a falta de padrão, em alguns casos os numeros fonercidos são os tres primeiros e dois ultimos, em outros estão no meio do CPF, a LAI padroniza que sejam publicado 5 numeros, mas deveria tambem padronizar o local exato, visto que o acesso aos dados devem ser facilitados e não gerarem mais dificuldades.
            "PROTOCOLO": match[3] if match[3] else '',
            "REPRESENTANTE_LEGAL": match[4] if match[4] else '',
            "CPF_REPRESENTANTE": match[5] if match[5] else '',
            "DATA_DOU": datetime.now().strftime("%d/%m/%Y")  # Adicionar a data atual
        })
    
    return data

# Função para processar arquivos JSON e salvar os dados extraídos em um Excel
def process_json_and_save_as_excel(input_dir: str, output_dir: str):
    all_data = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    for filename in os.listdir(input_dir):
        if filename.endswith('.json') and current_date in filename:
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as jsonfile:
                json_data = json.load(jsonfile)
                extracted_data = extract_data_from_json(json_data)
                all_data.extend(extracted_data)

    if all_data:
        keys = ["NOME", "NB", "CPF", "PROTOCOLO", "REPRESENTANTE_LEGAL", "CPF_REPRESENTANTE", "DATA_DOU"]
        df = pd.DataFrame(all_data, columns=keys)

        # Remover duplicatas
        df.drop_duplicates(inplace=True)

        # Obter a data atual
        data_atual = datetime.now().strftime('%Y-%m-%d')

        # Salvar o DataFrame completo em um arquivo Excel
        output_file = os.path.join(output_dir, f'dados_transformados_completos_prev_{data_atual}.xlsx')
        df.to_excel(output_file, index=False)
        logging.info(f"Dados completos salvos em {output_file}")

        # Salvar apenas a coluna 'NOME'
        df_nomes = df[['NOME']].dropna(subset=['NOME'])
        output_file_nomes = os.path.join(output_dir, f'nomes_prev_{data_atual}.xlsx')
        df_nomes.to_excel(output_file_nomes, index=False)
        logging.info(f"Dados com apenas nomes salvos em {output_file_nomes}")

        # Salvar as colunas 'NOME' e 'CPF'
        df_nomes_cpf = df[['NOME', 'CPF']].dropna(subset=['CPF'])
        output_file_nomes_cpf = os.path.join(output_dir, f'nome_cpf_prev_{data_atual}.xlsx')
        df_nomes_cpf.to_excel(output_file_nomes_cpf, index=False)
        logging.info(f"Dados com nomes e CPFs salvos em {output_file_nomes_cpf}")
    else:
        logging.info("Nenhum dado extraído para salvar.")

# Função para aguardar a presença dos arquivos JSON
def wait_for_json_files(input_dir: str, timeout: int = 3600):
    logging.info(f"Aguardando arquivos JSON no diretório {input_dir}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_date = datetime.now().strftime("%Y-%m-%d")
        json_files = [f for f in os.listdir(input_dir) if f.endswith('.json') and current_date in f]
        if json_files:
            logging.info(f"Arquivos JSON encontrados: {json_files}")
            return True
        else:
            logging.info("Arquivos JSON ainda não disponíveis. Verificando novamente em 30 segundos...")
            time.sleep(30)
    raise TimeoutError("Tempo limite excedido para encontrar os arquivos JSON.")

# Exemplo de uso
if __name__ == "__main__":
    input_dir = DEFAULT_INPUT_DIR
    output_dir = DEFAULT_OUTPUT_DIR

    try:
        wait_for_json_files(input_dir)
        logging.info(f"Processando arquivos JSON no diretório: {input_dir}")
        logging.info(f"Salvando dados extraídos no diretório: {output_dir}")
        process_json_and_save_as_excel(input_dir, output_dir)
    except (FileNotFoundError, TimeoutError) as e:
        logging.error(e)
