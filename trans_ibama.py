import os
import json
import logging
import time
from datetime import datetime
import pandas as pd
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Caminhos padrão
DEFAULT_INPUT_DIR = r"C:\path"
DEFAULT_OUTPUT_DIR = r"C:\path"

# Aqui uma parte importante (nesse caso foi utilizado expreções regulares, mas é um sofrimento pela falta de padrão na publicação) como já frizei algumas vezes os dados não tem padrão e por isso eu separei os programas para tratar os dados json coletados, veja que fazer isso no site da união por scraping (eu tentei) gerou muitos erros e percebi ao longo dos dias que o melhor formato foi esse. Mas veja bem, isso não me livrou de todos os problemas, separei os codigos e 
CNPJ_REGEX = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-(\d{2})')
CPF_REGEX = re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}')
COMPANY_NAME_REGEX = re.compile(r'.*\b(LTDA|ME|MEI|EPP)\b', re.IGNORECASE)
PERSON_NAME_REGEX = re.compile(r'^[A-Z][a-z]+(\s[A-Z][a-z]+)+')

# Função para extrair dados de uma tabela de conteúdo JSON
def extract_data_from_json(json_content):
    data = []

    def extract_name_and_cpf_cnpj(text):
        names_and_ids = []
        lines = text.split('\n')
        for line in lines:
            # Buscar CNPJ com sequências específicas
            cnpj_match = CNPJ_REGEX.search(line)
            if cnpj_match and cnpj_match.group(1) in {'01', '02', '03'}:
                cnpj = cnpj_match.group()
                # Buscar o nome da empresa associado
                for i in range(lines.index(line), max(lines.index(line) - 5, -1), -1):
                    name_match = COMPANY_NAME_REGEX.search(lines[i])
                    if name_match:
                        names_and_ids.append({
                            "nome": name_match.group().strip(),
                            "cnpj": cnpj
                        })
                        break
            # Buscar CPF e nome de pessoa física
            cpf_match = CPF_REGEX.search(line)
            if cpf_match:
                cpf = cpf_match.group()
                for i in range(lines.index(line), max(lines.index(line) - 5, -1), -1):
                    name_match = PERSON_NAME_REGEX.match(lines[i])
                    if name_match:
                        names_and_ids.append({
                            "nome_pf": name_match.group().strip(),
                            "cpf": cpf
                        })
                        break
        return names_and_ids

    # Extração de dados do texto completo
    if 'full_text_content' in json_content and json_content['full_text_content']:
        text = json_content['full_text_content']
        data.extend(extract_name_and_cpf_cnpj(text))

    # Extração de dados da tabela
    if 'full_table_content' in json_content and json_content['full_table_content']:
        table = json_content['full_table_content']
        for row in table:
            if len(row) >= 2:
                # Verificar e adicionar nomes e CNPJs
                if CNPJ_REGEX.match(row[1]) and CNPJ_REGEX.match(row[1]).group(1) in {'01', '02', '03'}:
                    cnpj = CNPJ_REGEX.match(row[1]).group()
                    name_match = COMPANY_NAME_REGEX.search(row[0])
                    if name_match:
                        data.append({
                            "nome": name_match.group().strip(),
                            "cnpj": cnpj
                        })
                # Verificar e adicionar nomes e CPFs
                if CPF_REGEX.match(row[1]):
                    cpf = CPF_REGEX.match(row[1]).group()
                    name_match = PERSON_NAME_REGEX.match(row[0])
                    if name_match:
                        data.append({
                            "nome_pf": name_match.group().strip(),
                            "cpf": cpf
                        })

    return data

# Função para processar arquivos JSON e salvar os dados extraídos em um Excel
def process_json_and_save_as_excel(input_dir: str, output_dir: str):
    all_data = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    for filename in os.listdir(input_dir):
        if filename.endswith('.json') and current_date in filename:
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                json_data = json.load(jsonfile)
                extracted_data = extract_data_from_json(json_data)
                
                for item in extracted_data:
                    item['DATA_DOU'] = current_date
                all_data.extend(extracted_data)

    if all_data:
        output_file = os.path.join(output_dir, f'dados_transformados_completos_{current_date}.xlsx')
        df = pd.DataFrame(all_data)

        # Adiciona colunas vazias caso não existam
        for col in ['nome', 'cnpj', 'nome_pf', 'cpf', 'multa']: #eu deixei esse exemplo de como os dados estão para você adaptar ao seu caso de estudo
            if col not in df.columns:
                df[col] = ''

        # Remover duplicatas 
        df.drop_duplicates(subset=["nome", "cnpj", "nome_pf", "cpf"], keep='first', inplace=True)

        df.to_excel(output_file, index=False)
        logging.info(f"Dados completos salvos em {output_file}")

        # acho válido dexiar os exemplos para salvar os dados, eu acredigo que você deva fazer um bom planejamento antes de começar para que gere planilhas corretas e facilite o tratamento dos dados para o fim de seus estudos
        df_nomes = df[['nome']].dropna().rename(columns={'nome': 'nome'})
        output_file_nomes_ibama = os.path.join(output_dir, f'nomes_ibama_{current_date}.xlsx')
        df_nomes.to_excel(output_file_nomes_ibama, index=False)
        logging.info(f"Nomes salvos em {output_file_nomes_ibama}")

        # Salvar a coluna 'nome', 'cpf', e 'cnpj' em uma nova planilha
        df_nomes_cpfs_cnpjs = df[['nome', 'cpf', 'cnpj']].dropna(subset=['nome', 'cpf', 'cnpj']).rename(columns={'nome': 'nome'})
        output_file_nomes_cpfs_cnpjs_ibama = os.path.join(output_dir, f'nome_cpf_cnpj_ibama_{current_date}.xlsx')
        df_nomes_cpfs_cnpjs.to_excel(output_file_nomes_cpfs_cnpjs_ibama, index=False)

        # Garantir que os arquivos sejam gerados mesmo se não houver dados (aqui é uma checagem quando retorna muitos dados em branco fica claro que há falha transformação ou conteúdo vazio no json (isso é raro))
        if df_nomes.empty:
            open(output_file_nomes_ibama, 'a').close()
        if df_nomes_cpfs_cnpjs.empty:
            open(output_file_nomes_cpfs_cnpjs_ibama, 'a').close()

        logging.info(f"Nomes com CPFs/CNPJs salvos em {output_file_nomes_cpfs_cnpjs_ibama}")

    else:
        logging.info("Nenhum dado extraído para salvar.")

# Função para aguardar a presença dos arquivos JSON # essa parte é irrelevante para o tratamento, mas como eu automatizei a busca pelo bat no WINDOWS VOU DEIXAR PARA VOCÊS COMO FICOU O CÓDIGO. No caso do código como tem uma ordem correta de coleta o programa precisa garantir que o outros foi concluido com exito, ou deverpa repetir. Veja, o programa no meu caso foi programado para acessar as 10h, mas a energia pode acabar, a intenet falhar, o dou não ter sido publicado, e ai o programa trans_ibama seria executado sem sentido e gerado resultados não verdadeiros. 
def wait_for_json_files(input_dir: str, timeout: int = 3600):
    logging.info(f"Aguardando arquivos JSON no diretório {input_dir}...")
    start_time = time.time()
    current_date = datetime.now().strftime("%Y-%m-%d")
    while time.time() - start_time < timeout:
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
    logging.info(f"Processando arquivos JSON no diretório: {input_dir}")
    logging.info(f"Salvando dados extraídos no diretório: {output_dir}")
    try:
        wait_for_json_files(input_dir)
        process_json_and_save_as_excel(input_dir, output_dir)
    except (FileNotFoundError, TimeoutError) as e:
        logging.error(e)
