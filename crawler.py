from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Configurar opções do Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Inicializar o navegador apenas uma vez
driver = webdriver.Chrome(options=chrome_options)

def extract_video_and_steps(url):
    """
    Extrai os links dos vídeos e os passos do exercício de uma URL.
    """
    driver.get(url)

    try:
        # Espera até que pelo menos um <source> esteja presente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'source'))
        )

        # Espera até que os elementos <dd> com a classe 'font-medium' estejam presentes
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'dd.font-medium'))
        )

        # Espera até que os elementos <dd> com a classe 'text-sm' estejam presentes
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'dd.text-sm'))
        )

    except Exception as e:
        print(f"Erro ao carregar os dados da URL {url}: {e}")
        return [], [], []

    # Captura os links dos vídeos
    video_sources = driver.find_elements(By.TAG_NAME, 'source')
    video_links = [source.get_attribute('src') for source in video_sources]

    # Captura os passos do exercício
    step_elements = driver.find_elements(By.CSS_SELECTOR, 'dd.font-medium')
    exercise_steps = [step.text.strip() for step in step_elements]

    # Captura metainfo do exercício
    metainfo_elements = driver.find_elements(By.CSS_SELECTOR, 'dd.text-sm')
    exercise_metainfo = [info.text.strip() for info in metainfo_elements]

    return video_links, exercise_steps, exercise_metainfo

# Carregar o dataset
with open('dataset.json', 'r') as file:
    dataset = json.load(file)

# Criar um conjunto de links únicos
unique_links = set()
for data in dataset:
    videos_links = data.get('videos_links', [])
    if len(videos_links) >= 2:
        unique_links.add(videos_links[0])

print(f"Total de links únicos: {len(unique_links)}")

# Iterar sobre os links únicos e extrair dados
for index, video_link in enumerate(unique_links):
    print(f"Processando o índice {index}...")

    # Extrair dados para exercícios masculinos
    male_videos, male_steps, metainfo = extract_video_and_steps(video_link)

    # Simular os dados femininos substituindo "male" por "female" nos links
    female_videos = [video.replace("male", "female") for video in male_videos]
    female_steps = male_steps  # Assumindo que os passos são os mesmos

    # Encontrar todos os exercícios correspondentes no dataset original
    matching_exercises = [item for item in dataset if item['videos_links'][0] == video_link]
    if not matching_exercises:
        print(f"Nenhum exercício correspondente encontrado para o link {video_link}.")
        continue

    # Atualizar todos os exercícios correspondentes
    for exercise_data in matching_exercises:
        exercise_data["male_front_exercise_video"] = male_videos[0] if len(male_videos) > 0 else None
        exercise_data["male_side_exercise_video"] = male_videos[1] if len(male_videos) > 1 else None
        exercise_data["female_front_exercise_video"] = female_videos[0] if len(female_videos) > 0 else None
        exercise_data["female_side_exercise_video"] = female_videos[1] if len(female_videos) > 1 else None
        exercise_data["steps_for_male_exercise"] = male_steps
        exercise_data["steps_for_female_exercise"] = female_steps
        exercise_data["Difficulty"] = metainfo[0] if len(metainfo) > 0 else None
        exercise_data["Force"] = metainfo[1] if len(metainfo) > 1 else None
        exercise_data["Grips"] = metainfo[2] if len(metainfo) > 2 else None
        exercise_data["Mechanic"] = metainfo[3] if len(metainfo) > 3 else None

    print(f"Dados atualizados para {len(matching_exercises)} exercícios correspondentes ao índice {index}.")

    # Salvar o progresso a cada 100 itens processados
    if (index + 1) % 100 == 0:
        with open('dataset_final.json', 'w') as file:
            json.dump(dataset, file, indent=4)
        print(f"Progresso salvo após {index + 1} itens.")

# Encerrar o navegador após o processamento
driver.quit()

# Salvar o dataset completo no final
with open('dataset_final.json', 'w') as file:
    json.dump(dataset, file, indent=4)

print("Arquivo 'dataset_final.json' salvo com sucesso.")
