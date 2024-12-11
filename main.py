import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebScraper:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        self.driver = None

    def setup_driver(self):
        """Configura o WebDriver com as opções necessárias."""
        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def download_data(self, url, btn1_xpath, btn2_xpath):
        """Acessa uma página, clica nos botões necessários e baixa os dados."""
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20)

            # Primeiro botão
            button_recursos = wait.until(EC.element_to_be_clickable((By.XPATH, btn1_xpath)))
            button_recursos.click()
            time.sleep(2)

            # Segundo botão
            button_acessar = wait.until(EC.element_to_be_clickable((By.XPATH, btn2_xpath)))
            button_acessar.click()

            # Trocar para a nova aba
            self.driver.switch_to.window(self.driver.window_handles[1])
            print("Nova URL:", self.driver.current_url)

            # Aguarda o download do arquivo
            self.wait_for_download()

        except Exception as e:
            print("Erro durante o download:", e)

        finally:
            self.driver.quit()

    def verify_download(self):
        """Verifica se os arquivos foram baixados corretamente."""
        downloaded_files = os.listdir(self.download_dir)
        print("Arquivos na pasta de download:", downloaded_files)
        if any(file.endswith(".csv") for file in downloaded_files):
            print("Arquivo CSV baixado com sucesso!")
            return True
        else:
            print("Nenhum arquivo CSV encontrado.")
            return False

    def wait_for_download(self, timeout=500):
        """Espera até que o arquivo seja completamente baixado."""
        time.sleep(1)
        end_time = time.time() + timeout
        while time.time() < end_time:
            if any(file.endswith(".crdownload") for file in os.listdir(self.download_dir)):
                # Ainda está baixando
                print("esperando mais")
                time.sleep(5)
            else:
                # Nenhum arquivo .crdownload encontrado, download concluído
                return True
        print("Timeout esperando o download.")
        return False
    def create_dataframe(self, url):
        """Processa os arquivos baixados e gera um dataframe consolidado."""
        dfs = []
        for arquivo in os.listdir(self.download_dir):
            if arquivo.endswith('.csv'):
                try:
                    df = pd.read_csv(
                        os.path.join(self.download_dir, arquivo),
                        delimiter=';',
                        encoding='ISO-8859-1',
                        low_memory=False,
                    )
                    # Transformações
                    df['dt_obito'] = pd.to_datetime(df['DTOBITO'], format='%d%m%Y', errors='coerce')
                    df['dt_nasc'] = pd.to_datetime(df['DTNASC'], format='%d%m%Y', errors='coerce')
                    df = df.dropna(subset=['dt_nasc', 'dt_obito'])
                    df['idade'] = (df['dt_obito'] - df['dt_nasc']).dt.days
                    df['ano_obito'] = df['dt_obito'].dt.year.astype(int)
                    # Manter apenas dados com idades válidas
                    df = df[df['idade'] >= 0]
                    # Manter apenas dados de Menores de 28 dias
                    df = df[df['idade'] <= 28]
                    df['quad_obito'] = pd.cut(df['dt_obito'].dt.month, bins=[1, 5, 9, 13], labels=[1, 2, 3], right=False)
                    df['cd_mun_res'] = df['CODMUNRES'].astype(str).str.slice(stop=6)
                    df['link_dados'] = url
                    df['dt_obito'] = df['dt_obito'].dt.strftime('%Y-%m-%d')
                    df['dt_nasc'] = df['dt_nasc'].dt.strftime('%Y-%m-%d')
                    df = df[['ano_obito', 'quad_obito', 'dt_obito', 'dt_nasc', 'idade', 'cd_mun_res', 'link_dados']]
                    dfs.append(df)
                except Exception as e:
                    print(f"Erro ao processar o arquivo {arquivo}: {e}")

        if dfs:
            df_group = pd.concat(dfs, ignore_index=True)
            print("Dataframe consolidado:")
            df_group.info()
            return df_group
        else:
            print("Nenhum dataframe foi criado.")
            return None


# Uso da classe
if __name__ == "__main__":
    DOWNLOAD_DIR = r"C:\Users\pmati\PycharmProjects\trabalhoFinalDados\dados"
    URL = "https://dados.gov.br/dados/conjuntos-dados/sim-1979-2019"
    BTN1_XPATH = "(//*[@id='btnCollapse'])[3]"
    BTN2_XPATH = "/html/body/div/section/div/div[3]/div[2]/div[3]/div[2]/div/div[35]/div[2]/div[2]/div/button[1]"

    scraper = WebScraper(DOWNLOAD_DIR)
    scraper.setup_driver()
    scraper.download_data(URL, BTN1_XPATH, BTN2_XPATH)

    if scraper.verify_download():
        df = scraper.create_dataframe(URL)
        if df is not None:
            output_path = os.path.join(DOWNLOAD_DIR, "dados_consolidados.json")
            df.to_json(output_path, orient="records", lines=True, force_ascii=False)
            print(f"Dados salvos em: {output_path}")
