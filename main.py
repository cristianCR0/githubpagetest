import re
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import random  
from time import sleep
import json
import multiprocessing
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------------Buscar duración-------------------------------------
gecko_driver_path = r'C:\Users\crist\Desktop\ProyectoMultiproceso'

firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument('--start-maximized')
firefox_options.add_argument('--disable-extensions')
#-------------------------------------------------------------------------------------------

def crearJson():
    with open('juegos1.txt', 'r') as file:
        lines = file.read().splitlines()

    # Crea un diccionario vacío para almacenar los datos
    juegos_dict = {}

    # Procesa las líneas y crea la estructura del diccionario
    for line in lines:
        partes = line.split(',')
        juego = partes[0].strip()
        precioox = partes[1].strip() if len(partes) > 1 else None

        juegos_dict[juego] = {
            "nombre": juego,
            "duracion": "",
            "puntuacion": None,
            "precio1": None,
            "precio2": None,
            "descuento1": None,
            "descuento2": None,
            "precioox": precioox,
            "cover_url": ""  # Nueva clave para almacenar la URL de la portada
        }

    # Convierte el diccionario a JSON
    json_data = json.dumps(juegos_dict, indent=4)

    # Guarda el JSON en un archivo si es necesario
    with open('juegosMulti.json', 'w') as json_file:
        json_file.write(json_data)

def convertir_precio_a_colones(precio_en_dolares, tasa_cambio=500):
    if precio_en_dolares == "No disponible":
        return "No disponible"
    else:
        try:
            precio_dolares = float(''.join(filter(str.isdigit, precio_en_dolares.replace('US$', '').replace('.', '').replace("\n","")))) / 100
            precio_colones = round(precio_dolares * tasa_cambio)
            precio_colones_str = str(precio_colones).split('.')[0]
            return precio_colones_str
        except:
            return "No disponible"

def calcular_descuento(precio_original, nuevo_precio):
    if precio_original == "No disponible" or nuevo_precio == "No disponible":
        return "No disponible"
    else:
        try:
            precio_original = int(precio_original)
            nuevo_precio = int(nuevo_precio)
            if precio_original <= 0:
                raise ValueError("Los precios deben ser mayores que cero.")
            descuento = abs(round( ((precio_original - nuevo_precio) / precio_original) * 100 ))
            return f"{descuento}%"
        except:
            return "No disponible"

def limpiar_y_convertir(cadena):
    if cadena == "No disponible":
        return "No disponible"
    else:
        cadena = cadena.replace("\u20a1", "").replace(".", "")
        for line in cadena.splitlines():
            partes = line.split(',')
            x = partes[0].strip()
        return x  

def get_game_cover_url(game_title):
    search_query = game_title.replace(' ', '+') + '+game+cover'
    url = f'https://www.google.com/search?q={search_query}&tbm=isch'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    # Filtra las imágenes que no son del logotipo de Google
    for img in img_tags:
        img_url = img.get('src')
        if img_url and 'googlelogo' not in img_url and img_url.startswith('http'):
            return img_url
    
    return None



def read_game_titles_from_txt(file_path):
    with open(file_path, 'r') as file:
        return [line.split(',')[0].strip() for line in file]

def crearPagina():
    with open("infoPagina.json", "r") as archivo:
        datos = json.load(archivo)

    juegos_aleatorios = random.sample(list(datos.values()), 2)
    html = """
    <html>
    <head>
        <title>InforJuegos</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-image: url('https://i.pinimg.com/originals/ec/b6/41/ecb6416c16b66e9e5409def9271224a2.gif');
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }
            .container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-around;
                margin: 20px;
            }
            .juego {
                background-color: rgba(255, 255, 255, 0.8);
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin: 10px;
                padding: 20px;
                width: calc(33% - 40px);
                box-sizing: border-box;
            }
            .juego h2 {
                font-size: 1.5em;
                margin-top: 0;
            }
            .juego p {
                margin: 0.5em 0;
            }
            .juego img {
                max-width: 100%;
                height: auto;
                margin-bottom: 10px;
            }
            .section {
                margin: 20px;
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                font-size: 1em;
                color: #fff;
                background-color: #007BFF;
                border: none;
                border-radius: 5px;
                text-decoration: none;
                margin: 20px;
            }
            .button:hover {
                background-color: #0056b3;
            }
        </style>
        <script>
            function mostrarCatalogo() {
                document.getElementById('catalogo').style.display = 'block';
                document.getElementById('juegosAleatorios').style.display = 'none';
            }
        </script>
    </head>
    <body>
        <h1 style="text-align:center;">Info de Juegos</h1>
        <div id="juegosAleatorios" class="section">
            <h2>Juegos Aleatorios</h2>
            <div class="container">
    """

    for detalles in juegos_aleatorios:
        html += f"""
        <div class='juego'>
            <img src="{detalles['cover_url']}" alt="Portada de {detalles['nombre']}">
            <h2>{detalles['nombre']}</h2>
            <p>Duracion: {detalles['duracion']}</p>
            <p>Puntuacion: {detalles['puntuacion']}</p>
            <p>Precio Amazon: {detalles['precio1'] if detalles['precio1'] else 'No disponible'}</p>
            <p>Precio Steam: {detalles['precio2'] if detalles['precio2'] else 'No disponible'}</p>
            <p>Descuento Amazon: {detalles['descuento1'] if detalles['descuento1'] else 'No disponible'}</p>
            <p>Descuento Steam: {detalles['descuento2'] if detalles['descuento2'] else 'No disponible'}</p>
        </div>
        """
    
    html += """
            </div>
            <button class="button" onclick="mostrarCatalogo()">Ver Catálogo Completo</button>
        </div>
        <div id="catalogo" class="section" style="display:none;">
            <h2>Catálogo Completo</h2>
            <div class="container">
    """

    for juego, detalles in datos.items():
        html += f"""
        <div class='juego'>
            <img src="{detalles['cover_url']}" alt="Portada de {detalles['nombre']}">
            <h2>{detalles['nombre']}</h2>
            <p>Duracion: {detalles['duracion']}</p>
            <p>Puntuacion: {detalles['puntuacion']}</p>
            <p>Precio Amazon: {detalles['precio1'] if detalles['precio1'] else 'No disponible'}</p>
            <p>Precio Steam: {detalles['precio2'] if detalles['precio2'] else 'No disponible'}</p>
            <p>Descuento Amazon: {detalles['descuento1'] if detalles['descuento1'] else 'No disponible'}</p>
            <p>Descuento Steam: {detalles['descuento2'] if detalles['descuento2'] else 'No disponible'}</p>
        </div>
        """
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """

    with open("pagina.html", "w") as archivo_html:
        archivo_html.write(html)

    print("Página web generada y guardada como 'pagina.html'.")

def score(juego):
    juego = juego.replace(" ", "-").lower()
    url_base = "https://www.metacritic.com/game/"
    website = url_base + juego + "/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    resultado = requests.get(website, headers=headers)
    content = resultado.text
    patron = r"<span data-v-4cdca868>(\d+)"
    scoreRepetidos = re.findall(patron, content)
    if scoreRepetidos:
        score = scoreRepetidos[0]
        return score
    else:
        return "No disponible"

def leer_juegos(archivo):
    with open(archivo, "r") as archivo_juegos:
        juegos = [line.strip() for line in archivo_juegos]
    return juegos

def obtener_duracion(juego):
    juego= str(juego)
    driver = webdriver.Firefox(options=firefox_options)
    driver.get('https://howlongtobeat.com')
    element_to_click = driver.find_element(By.XPATH, '/html/body/div[1]/div/header/nav/div/input')
    element_to_click.click()
    time.sleep(2)
    search_box = driver.find_element(By.XPATH, '/html/body/div[1]/div/header/nav/div/input')
    search_box.clear()
    search_box.send_keys(juego)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    element_with_options = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div/div/div[5]/ul/li[1]/div/div[2]/div')
    try:
        sixth_option = element_with_options.find_element(By.XPATH, 'div/div[2]')
        sixth_option_text = sixth_option.text
        driver.quit()
        return sixth_option_text
    except:
        return "No disponible"

def search_and_get_price(url, search_keyword, search_selector, price_element_xpath):
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )

    driver.get(url)
    search_box = driver.find_element(By.CSS_SELECTOR, search_selector)
    search_box.send_keys(search_keyword)
    search_box.send_keys(Keys.RETURN)
    sleep(2)

    try:
        primer_precio = driver.find_element(By.XPATH, price_element_xpath).text
        driver.quit()
        return primer_precio
    except:
        driver.quit()
        return "No disponible"

def obtener_duracion_puntuacion(juego):
    duracion =  obtener_duracion(juego)
    puntuacion = score(juego)
    precioAmazon= search_and_get_price('https://www.amazon.com/', str(juego), 'input[type="text"]', '//span[@class="a-price"]')
    xprecioSteam= search_and_get_price('https://store.steampowered.com/?l=spanish', str(juego), 'input[id="store_nav_search_term"]', '//div[@class="discount_final_price"]')
    precioSteam = xprecioSteam.replace('\u20a1', '')
    cover_url = get_game_cover_url(juego)  # Utilizamos la función para obtener la URL de la portada
    return juego, duracion, puntuacion, precioAmazon, precioSteam, cover_url

def procesar_juegos(juegos):
    with multiprocessing.Pool(processes=4) as pool:
        resultados = pool.starmap(obtener_duracion_puntuacion, ((juego,) for juego in juegos.keys()))

    for juego, duracion, puntuacion, precioAmazon, precioSteam, cover_url in resultados:
        juegos[juego]['duracion'] = duracion
        juegos[juego]['puntuacion'] = puntuacion
        juegos[juego]['precio1'] = convertir_precio_a_colones(precioAmazon)
        juegos[juego]['precio2'] = limpiar_y_convertir(precioSteam)
        juegos[juego]['descuento1'] = calcular_descuento(juegos[juego]['precioox'], juegos[juego]['precio1'])
        juegos[juego]['descuento2'] = calcular_descuento(juegos[juego]['precioox'], juegos[juego]['precio2'])
        juegos[juego]['cover_url'] = cover_url  # Añadimos la URL de la portada al diccionario

if __name__ == "__main__":
    crearJson()
    with open("juegosMulti.json", "r") as archivo_json:
        juegos = json.load(archivo_json)

    procesar_juegos(juegos)

    with open("infoPagina.json", "w") as archivo_json:
        json.dump(juegos, archivo_json, indent=4)
    
    crearPagina()
