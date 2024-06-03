import requests
from bs4 import BeautifulSoup
import os
import re

# Función para obtener la URL de la imagen de la portada del juego en Google
def get_game_cover_url(game_title):
    search_query = game_title.replace(' ', '+') + '+game+cover'
    url = f'https://www.google.com/search?q={search_query}&tbm=isch'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img', {'class': 't0fcAb'})
    if img_tags:
        return img_tags[0]['src']
    else:
        return None

# Función para leer el archivo de texto y obtener los títulos de los juegos
def read_game_titles_from_txt(file_path):
    with open(file_path, 'r') as file:
        return file.read().splitlines()

# Función para escribir el HTML con las imágenes de las portadas de los juegos
def write_html_with_game_covers(game_titles, output_file):
    with open(output_file, 'w') as file:
        file.write('<html>\n<body>\n')
        for title in game_titles:
            cover_url = get_game_cover_url(title)
            if cover_url:
                file.write(f'<img src="{cover_url}" alt="{title}">\n')
        file.write('</body>\n</html>')

# Archivo de texto con los títulos de los juegos
input_file = 'juegos1.txt'
# Archivo HTML de salida
output_file = 'juegos_covers.html'

# Obtener los títulos de los juegos del archivo de texto
game_titles = read_game_titles_from_txt(input_file)

# Escribir el HTML con las imágenes de las portadas de los juegos
write_html_with_game_covers(game_titles, output_file)

print("Se ha creado el archivo HTML con las imágenes de las portadas de los juegos.")
