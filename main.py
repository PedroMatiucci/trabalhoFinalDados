from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Configurações iniciais
DOWNLOAD_DIR = "dados"

# Configuração para baixar arquivos automaticamente
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": DOWNLOAD_DIR}
options.add_experimental_option("prefs", prefs)

# Inicializa o driver
driver = webdriver.Chrome(options=options)  # Certifique-se de que o chromedriver está no PATH
driver.maximize_window()

try:
    # Acesse a URL da página
    driver.get("https://dados.gov.br/dados/conjuntos-dados/sim-1979-2019")  # Substitua pela URL da página

    # Aguarda até que o botão seja carregado (ajuste o seletor conforme necessário)
    wait = WebDriverWait(driver, 20)
    button_recursos = wait.until(
        EC.element_to_be_clickable((By.XPATH, "(//*[@id='btnCollapse'])[3]"))
    )
    button_recursos.click()

    time.sleep(2)

    # Aguarda até que o segundo botão esteja clicável
    button_acessar = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div/section/div/div[3]/div[2]/div[3]/div[2]/div/div[2]/div[2]/div[2]/div/button[1]"))
    )
    print('cheguei')
    button_acessar.click()
    print('cliquei')

    driver.switch_to.window(driver.window_handles[1])
    # Aguarda o download do arquivo (ajuste o tempo se necessário)
    time.sleep(10)

    # Verifica se o arquivo CSV foi baixado
    downloaded_files = os.listdir(DOWNLOAD_DIR)
    print("Arquivos na pasta de download:", downloaded_files)
    if any(file.endswith(".csv") for file in downloaded_files):
        print("Arquivo CSV baixado com sucesso!")
    else:
        print("Nenhum arquivo CSV encontrado.")
finally:
    # Fecha o navegador
    driver.quit()

#TOdo quando clica o botao abre outro site adicnoar suporte para isso