# Descargador automático de PDFs para Moodle (Atenea)

Este script automatiza la descarga de archivos PDF desde un curso de Atenea (el campus virtual de la UPC). Abre la página del curso, espera a que el usuario 
inicie sesión manualmente, detecta cuando el usuario ya está dentro del curso y descarga los PDFs organizándolos en carpetas por sección.

---

## Cómo funciona

- El script abre el navegador y navega a la URL del curso.
- Moodle redirige automáticamente a la página de inicio de sesión.
- El usuario debe introducir sus credenciales manualmente.
- Una vez el usuario inicia sesión correctamente, Moodle redirige a la página del curso.
- El script detecta esta redirección, obtiene el contenido HTML del curso y comienza la descarga de los PDFs.
- Los archivos se guardan en una carpeta local llamada `ATENEA`, organizada por secciones.

---

## Requisitos

- Python 3.8+
- Google Chrome instalado (compatible con el ChromeDriver)
- ChromeDriver en el PATH o configurado en el script
- Librerías Python:
  - selenium
  - requests
  - beautifulsoup4

Puedes instalar las dependencias con:

```bash
pip install selenium requests beautifulsoup4
