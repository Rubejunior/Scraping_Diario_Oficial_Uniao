import os
import json
import logging
from datetime import datetime
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Caminhos padrão
DEFAULT_INPUT_DIR = r"C:\path"
DEFAULT_OUTPUT_DIR = r"C:\paht"

# Mapeamento de siglas para nomes completos dos estados (melhora a qualidade dos dados visto que em alguns casos temos "GO" em outros "Goias". Essa parte do código pode ser removida caso não seja pertinente para seu estudo)
estado_map = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
}

# Função para extrair dados de uma tabela de conteúdo JSON - os dados JSON infelizmente não tem padrão, algo muito simples que deveria ser praticado pelos orgãos públicos mas não é, nesse exemplo eu deixei uma coleta coltada para esses dois itens, mas isso vai mudar e precisará ser alterado caso você perceba que os dados não estão sendo copilados da forma correta.
def extract_data_from_json(json_content):
    data = []
    for entry in json_content.get('full_table_content', []):
        if entry and len(entry) >= 3:
            razao_social = entry[0]
            cnpj_cpf = entry[3] if len(entry) > 3 else ''
            data.append({
                "RAZAO_SOCIAL": razao_social,
                "CPF_CNPJ": cnpj_cpf
            })
    return data

# Função para extrair o estado do texto e padronizar de aacordo com o "estado_map"
def extract_estado(text):
    for nome in estado_map.values():
        if nome in text:
            return nome
    return "Desconhecido"

# Função para processar arquivos JSON e salvar os dados extraídos em um Excel
def process_json_and_save_as_excel(input_dir: str, output_dir: str):
    all_data = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    for filename in os.listdir(input_dir):
        if filename.endswith('.json') and current_date in filename:
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as jsonfile:
                json_data = json.load(jsonfile)
                full_content = json_data.get('full_text_content', '')
                date_dou = json_data.get('date', current_date)  # Usar a data atual se não estiver disponível no JSON
                estado = extract_estado(full_content)  # Extrair o estado
                secao = "Seção de Multas e Recursos"  # Definido fixamente aqui, ajuste conforme necessário
                extracted_data = extract_data_from_json(json_data)
                
                # Adicionar a data extraída, estado e seção a cada entrada de dados
                for item in extracted_data:
                    item['DATA_DOU'] = date_dou
                    item['ESTADO'] = estado
                    item['SECAO'] = secao
                
                all_data.extend(extracted_data)

    if all_data:
        keys = ["RAZAO_SOCIAL", "CPF_CNPJ", "DATA_DOU", "ESTADO", "SECAO"]
        output_file = os.path.join(output_dir, f'dados_transformados_completos_{current_date}.xlsx')

        # Criar DataFrame a partir dos dados extraídos
        df = pd.DataFrame(all_data, columns=keys)
        
        #exemplo de como você pode tratar os dados e separar as planilhas para facilitar o estudo adiante.

        # Remover duplicatas com base na coluna 'RAZAO_SOCIAL'
        df.drop_duplicates(subset="RAZAO_SOCIAL", keep='first', inplace=True)

        # Renomear colunas
        df.rename(columns={"RAZAO_SOCIAL": "nome", "CPF_CNPJ": "cpf_cnpj"}, inplace=True)

        # Duplicar a coluna CPF_CNPJ
        df['cpf'] = df['cpf_cnpj'].apply(lambda x: x if len(x) == 11 else '')
        df['cnpj'] = df['cpf_cnpj'].apply(lambda x: x if len(x) == 14 else '')

        # Salvar o DataFrame completo em um arquivo Excel
        df.to_excel(output_file, index=False)
        logging.info(f"Dados completos salvos em {output_file}")

        # Criar planilhas específicas com as colunas necessárias

        # Planilha com a coluna 'nome' para pf
        df_nome_pf = df[['nome']]
        output_file_nome_pf = os.path.join(output_dir, f'nome_pf_{current_date}.xlsx')
        df_nome_pf.to_excel(output_file_nome_pf, index=False)
        
        # Planilha com a coluna 'nome' para pj (valores vazios em 'cpf' e 'cnpj')
        df_nome_pj = df[(df['cpf'] == '') & (df['cnpj'] == '')][['nome']]
        output_file_nome_pj = os.path.join(output_dir, f'nome_pj_{current_date}.xlsx')
        df_nome_pj.to_excel(output_file_nome_pj, index=False)

        # Planilha com a coluna 'cnpj' removendo linhas vazias
        df_cnpj = df[['cnpj']].dropna()
        output_file_cnpj = os.path.join(output_dir, f'cnpj_{current_date}.xlsx')
        df_cnpj.to_excel(output_file_cnpj, index=False)

        # Planilha com a coluna 'cpf' limitando a 11 números
        df_cpf = df[df['cpf'].str.replace(r'\D', '', regex=True).str.len() == 11][['cpf']].dropna()
        output_file_cpf = os.path.join(output_dir, f'cpf_{current_date}.xlsx')
        df_cpf.to_excel(output_file_cpf, index=False)

        # Planilha com as colunas 'nome' e 'cnpj'
        df_nome_cnpj = df[['nome', 'cnpj']]
        output_file_nome_cnpj = os.path.join(output_dir, f'nome_cnpj_{current_date}.xlsx')
        df_nome_cnpj.to_excel(output_file_nome_cnpj, index=False)

        # Planilha com as colunas 'nome' e 'cpf' limitando a 11 números
        df_nome_cpf = df[df['cpf'].str.replace(r'\D', '', regex=True).str.len() == 11][['nome', 'cpf']].dropna()
        output_file_nome_cpf = os.path.join(output_dir, f'nome_cpf_{current_date}.xlsx')
        df_nome_cpf.to_excel(output_file_nome_cpf, index=False)

        logging.info(f"Planilhas específicas salvas no diretório: {output_dir}")
    else:
        logging.info("Nenhum dado extraído para salvar.")

# Exemplo de uso
if __name__ == "__main__":
    input_dir = DEFAULT_INPUT_DIR
    output_dir = DEFAULT_OUTPUT_DIR
    logging.info(f"Processando arquivos JSON no diretório: {input_dir}")
    logging.info(f"Salvando dados extraídos no diretório: {output_dir}")
    process_json_and_save_as_excel(input_dir, output_dir)

    # Verifique e remova linhas em branco na planilha cnpj
    current_date = datetime.now().strftime('%Y-%m-%d')
    cnpj_file = os.path.join(output_dir, f'cnpj_{current_date}.xlsx')

    if os.path.exists(cnpj_file):
        df_cnpj = pd.read_excel(cnpj_file)
        df_cnpj.dropna(how='all', inplace=True)  # Remove as linhas que são completamente vazias
        df_cnpj.to_excel(cnpj_file, index=False)
        logging.info(f"Linhas em branco removidas do arquivo {cnpj_file}")
    else:
        logging.error(f"O arquivo {cnpj_file} não foi encontrado.")
