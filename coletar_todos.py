import os
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import csv
import json
from enum import Enum
from typing import List


# Configurar logging
logging.basicConfig(level=logging.INFO)

# Definindo constantes
IN_WEB_BASE_URL = "https://www.in.gov.br/web/dou/-/" #não alterar
IN_API_BASE_URL = "https://www.in.gov.br/consulta/-/buscar/dou" #não alterar
LINK_OUTPUT_DIR = r"C:\path" #colocar local para salvar os arquivos coletados

# Enumerações
class Section(Enum):
    SECAO_1 = "do1"
    SECAO_2 = "do2"
    SECAO_3 = "do3"
    EDICAO_EXTRA = "doe"
    EDICAO_EXTRA_1A = "do1_extra_a"
    EDICAO_EXTRA_1B = "do1_extra_b"
    EDICAO_EXTRA_1D = "do1_extra_d"
    EDICAO_EXTRA_2A = "do2_extra_a"
    EDICAO_EXTRA_2B = "do2_extra_b"
    EDICAO_EXTRA_2D = "do2_extra_d"
    EDICAO_EXTRA_3A = "do3_extra_a"
    EDICAO_EXTRA_3B = "do3_extra_b"
    EDICAO_EXTRA_3D = "do3_extra_d"
    EDICAO_SUPLEMENTAR = "do1a"
    TODOS = "todos"

class Field(Enum):
    TUDO = "tudo"
    TITULO = "title_pt_BR"
    CONTEUDO = "ddm__text__21040__texto_pt_BR"

def get_query_str(term, field, is_exact_search):
    if is_exact_search:
        term = f'"{term}"'
    return f"{field.value}-{term}" if field != Field.TUDO else term

def request_page(payload: dict, with_retry: bool):
    try:
        logging.info(f"Requisitando página com payload: {payload}")
        response = requests.get(IN_API_BASE_URL, params=payload, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"Erro HTTP ocorreu: {http_err}")
    except requests.exceptions.ConnectionError:
        if with_retry:
            logging.info("Falha na conexão. Aguardando 30 segundos antes de tentar novamente.")
            time.sleep(30)
            return requests.get(IN_API_BASE_URL, params=payload, timeout=10)
    except Exception as err:
        logging.error(f"Erro ocorreu: {err}")

def search_text(
    search_term: str,
    sections: List[Section],
    organization: str,
    field=Field.TUDO,
    is_exact_search=True,
    with_retry=True,
):
    payload = {
        "q": get_query_str(search_term, field, is_exact_search),
        "exactDate": "dia",  # Usar "dia" para edição do dia - essa parte esta adaptada pois quero garantir o acesso apenas ao DOU do dia, abaixo você vai ver que teria como fazer a consulta na data que você desejar, ai nesse caso essa parte do código deverá ser alterada.
        "sortType": "0",
        "s": [section.value for section in sections],
        "orgPrin": organization
    }
    page = request_page(payload=payload, with_retry=with_retry)
    if page is None:
        logging.error("Falha ao requisitar a página.")
        return []

    logging.info(f"Resposta da página: {page.text[:500]}")  # Log da resposta 

    soup = BeautifulSoup(page.content, "html.parser")
    script_tag = soup.find("script", id="_br_com_seatecnologia_in_buscadou_BuscaDouPortlet_params")
    if not script_tag:
        logging.warning("Tag de script não encontrada. A busca pode não ter retornado resultados.")
        return []

    try:
        search_results = json.loads(script_tag.contents[0])["jsonArray"]
        logging.info(f"Resultados encontrados: {search_results[:5]}")  # Log dos primeiros 5 resultados
    except Exception as e:
        logging.error(f"Erro ao analisar resultados: {e}")
        return []

#garantir que a busca esta na data do dia desejado
    links = []
    if search_results:
        for content in search_results:
            links.append({
                "url": IN_WEB_BASE_URL + content["urlTitle"],
                "id": content["classPK"],
                "title": content["title"],
                "date": content["pubDate"]
            })
    else:
        logging.info("Nenhum resultado encontrado nesta página.")
    return links

def salvar_csv(dados, output_dir):
    if not dados:
        logging.info("Nenhum dado encontrado para salvar.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.join(output_dir, f"links_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
    keys = dados[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(dados)
    logging.info(f"Dados salvos em {filename}")
    
#essa é uma adaptação ao codigo original importante que fornece uma busca exata, no caso abaixo você pode fazer a busca por qualquer termo que quiser, escolher a seção correta, e a organização, os nome de ministérios devem ser exatamente como no exemplo e como esta no edital. Eu removi a parte da busca por data, mas você pode adaptar isso facilmente no codigo incluido no filtro as variaveis de datas. Como faço busca diarias não era termos importantes para mim, apesar de ter outro programa que faz essa busca com data, eu vou disponibilizar essa parte no README.

if __name__ == "__main__":
    search_term = "edital de notificação"  # Termo de pesquisa fixo
    is_exact_search = True  # Busca exata
    sections = [Section.SECAO_3]  # Seção 3
    organization = "Ministério do Trabalho e Emprego"  #
