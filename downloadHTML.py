import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DownloadHTML():

    def downloadHtml(pathWork):
        edge_options = Options()
        edge_options.add_experimental_option('prefs', {
            "download.default_directory": os.path.abspath("./download"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        webdriver_path = "./webdriver/msedgedriver.exe"
        driver = webdriver.Edge(service=Service(webdriver_path), options=edge_options)

        # Rutas de carpetas
        docx_directory = pathWork
        output_directory = "./download"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        try:
            # Iterar sobre los archivos .docx
            for filename in os.listdir(docx_directory):
                if filename.endswith(".docx"):
                    file_path = os.path.join(docx_directory, filename)
                    
                    # Navegar al sitio web
                    driver.get("https://products.groupdocs.app/es/conversion/docx-to-html")
                    time.sleep(6)  # Esperar a que cargue la página
                    
                    # Subir archivo
                    upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
                    upload_input.send_keys(file_path)
                    time.sleep(20)  # Esperar a que se procese la carga
                    
                    convert_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Convertir ahora')]")
                    driver.execute_script("arguments[0].scrollIntoView();", convert_button)  # Desplazarse hasta el boton
                    time.sleep(1)  # Esperar un momento para asegurarse de que el scroll se haya completado
                    convert_button.click()
                    time.sleep(20)
                    
                    # Descargar el archivo
                    download_link = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@id='convertDownload']"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView();", download_link)  # Desplazarse hasta el enlace de descarga
                    time.sleep(1)
                    download_link.click()
                    time.sleep(10) # Esperar a que se descargue el archivo
        finally:
            driver.quit()



