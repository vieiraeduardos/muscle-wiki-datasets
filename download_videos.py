import json
import os
import logging
import requests
from tqdm import tqdm
from urllib.parse import urlparse
import hashlib  # Importação para gerar o hash

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_hash(url):
    """Gera um hash único baseado na URL."""
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def download_video(url, output_dir):
    if not url:
        logging.warning("URL inválida ou ausente. Pulando download.")
        return None

    try:
        # Gerar o hash da URL para criar um nome único
        file_hash = generate_hash(url)
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1]  # Obter a extensão do arquivo
        filename = f"{file_hash}{file_extension}"  # Nome do arquivo com hash e extensão

        # Criar o caminho completo para salvar o vídeo
        output_path = os.path.join(output_dir, filename)

        # Verificar se o vídeo já foi baixado
        if os.path.exists(output_path):
            logging.info(f"Vídeo {filename} já existe. Pulando download.")
            return output_path

        # Fazer o download do vídeo
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Levantar exceção para códigos de status HTTP inválidos

        with open(output_path, 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size=8192), desc=f"Baixando {filename}", unit='B', unit_scale=True):
                f.write(chunk)

        logging.info(f"Vídeo {filename} baixado com sucesso.")
        return output_path

    except requests.RequestException as e:
        logging.error(f"Erro ao baixar {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao processar {url}: {e}")
        return None

def process_videos(dataset, output_dir):
    for index, exercise in enumerate(set(item.get('exercise') for item in dataset)):
        matching_exercises = [item for item in dataset if item.get('exercise') == exercise and item.get('male_front_exercise_video_path') is None]

        if not matching_exercises:
            logging.warning(f"Nenhum exercício correspondente encontrado para {exercise}.")
            continue

        # Baixar vídeos para o exercício
        video_links = ['male_front_exercise_video', 'female_front_exercise_video', 'male_side_exercise_video', 'female_side_exercise_video']
        downloaded_videos = {key: download_video(matching_exercises[0].get(key), output_dir) for key in video_links}

        # Atualizar os dados do exercício
        for exercise_data in matching_exercises:
            exercise_data.update(downloaded_videos)

        logging.info(f"Dados atualizados para {len(matching_exercises)} exercícios correspondentes ao índice {index} {exercise}.")

        # Salvar progresso a cada 100 itens processados
        if (index + 1) % 100 == 0:
            save_dataset(dataset, 'dataset_final.json')
            logging.info(f"Progresso salvo após {index + 1} itens.")

def save_dataset(dataset, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(dataset, file, indent=4)
        logging.info(f"Arquivo '{filename}' salvo com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo '{filename}': {e}")

def main():
    output_dir = 'videos'
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open('dataset.json', 'r') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        logging.error("Arquivo 'dataset.json' não encontrado.")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar 'dataset.json': {e}")
        return

    process_videos(dataset, output_dir)
    save_dataset(dataset, 'dataset_final2.json')

if __name__ == "__main__":
    main()