from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os 
import requests
import re
from bs4 import BeautifulSoup
import time

# URL del curso (debes estar logueado para acceder)
COURSE_URL = "https://atenea.upc.edu/course/view.php?id=90338"  # URL del curso específico

# Ruta donde se guardarán los PDFs descargados
DOWNLOAD_FOLDER = "descargas"

# Configuración del navegador (chrome_options)
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Abre el navegador maximizado

# Inicializar el driver
driver = webdriver.Chrome(options=chrome_options)

# Función para obtener el HTML del curso
def get_course_html():
    # Navegar a la página del curso después de iniciar sesión
    print("Navegando a la página de Moodle...")
    driver.get(COURSE_URL)

    # Esperar a que se cargue el contenido del curso
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "course-content"))
    )

    # Obtener el HTML del curso
    course_html = driver.page_source

    # Mostrar el HTML para depuración
    print("HTML de la página del curso obtenido")
    return course_html

# Función para limpiar nombres de archivo
def sanitize_filename(filename):
    """Reemplaza caracteres no válidos para nombres de archivo."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_pdfs_from_html(html):
    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Buscar todas las secciones del curso
    sections = soup.find_all("li", class_="section")

    # Transferir las cookies de Selenium a la sesión de requests
    session = requests.Session()
    session.cookies.update({cookie['name']: cookie['value'] for cookie in driver.get_cookies()})

    # Configurar encabezados para simular una solicitud desde un navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    # Iterar por las secciones
    for section in sections:
        # Obtener el nombre de la sección
        section_name = section.find("h3", class_="sectionname")
        if not section_name:
            continue  # Saltar secciones que no tengan nombre
        section_name = sanitize_filename(section_name.text.strip())

        # Crear la carpeta para la sección
        section_folder = os.path.join(DOWNLOAD_FOLDER, section_name)
        os.makedirs(section_folder, exist_ok=True)

        # Buscar los enlaces PDF dentro de la sección
        pdf_links = section.find_all("a", class_="aalink")
        if not pdf_links:
            print(f"No se encontraron PDF en la sección '{section_name}'.")
            continue

        # Descargar cada archivo PDF
        for link in pdf_links:
            pdf_url = link.get("href")
            if pdf_url:
                # Resolver URLs relativas si las hubiera
                if not pdf_url.startswith("http"):
                    pdf_url = f"{COURSE_URL.rstrip('/')}/{pdf_url.lstrip('/')}"

                # Obtener el nombre del archivo
                file_name = link.text.strip()  # Extraer el texto visible del enlace
                if not file_name:
                    file_name = "archivo_" + str(int(time.time()))  # Nombre predeterminado en caso de fallo

                # Eliminar "Fitxer" del nombre del archivo
                file_name = file_name.replace("Fitxer", "").strip()

                # Asegurarse de que el nombre sea válido
                file_name = sanitize_filename(file_name) + ".pdf"

                try:
                    # Hacer una solicitud HEAD para comprobar el tipo de contenido
                    response = session.head(pdf_url, headers=headers, allow_redirects=True)
                    if response.headers.get("Content-Type") == "application/pdf":
                        print(f"PDF encontrado: {pdf_url}")

                        # Descargar el archivo PDF
                        download_response = session.get(pdf_url, headers=headers, stream=True)
                        filepath = os.path.join(section_folder, file_name)

                        # Guardar el PDF
                        with open(filepath, "wb") as f:
                            for chunk in download_response.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                        print(f"Archivo guardado: {filepath}")
                    else:
                        print(f"No es un PDF: {pdf_url} (Content-Type: {response.headers.get('Content-Type')})")
                except Exception as e:
                    print(f"Error al procesar {pdf_url}: {e}")

# Función principal para descargar PDFs
def main():
    print("Navegando a la página de Moodle...")

    # Obtener el HTML del curso
    html = get_course_html()

    if html:
        print("HTML de la página obtenido correctamente")
        # Descargar los PDFs de las secciones
        download_pdfs_from_html(html)

    # Esperar un poco antes de cerrar el navegador para asegurar que todo se haya descargado
    print("Esperando 10 segundos antes de cerrar...")
    time.sleep(10)  # Espera 10 segundos

# Ejecutar el script
if __name__ == "__main__":
    main()

    # Cerrar el navegador después de completar las descargas
    driver.quit()
