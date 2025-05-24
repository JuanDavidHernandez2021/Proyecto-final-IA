"""
Imagina que esta API es una biblioteca de películas:
La función load_movies() es como un bibliotecario que carga el catálogo de libros (películas) cuando se abre la biblioteca.
La función get_movies() muestra todo el catálogo cuando alguien lo pide.
La función get_movie(id) es como si alguien preguntara por un libro específico por su código de identificación.
La función chatbot (query) es un asistente que busca libros según palabras clave y sinónimo.
La función get_movies_by_category (cagory) ayuda a encontrar películas según su género (acción, comedia, etc.).
"""

# Importamos las herramientas necesarias para contruir nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException maneja errores.	I
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse nos permite responder con HTML, JSONResponse nos permite responder con JSON.
import pandas as pd # Pandas nos ayuda a manejar datos en tablasm como si fuera una hoja de cálculo.
import nltk # NLTK es una librería para procesar texto y analizar palabras.
from nltk.tokenize import word_tokenize # Se usa para dividir un texto en palabras individuales.
from nltk.corpus import wordnet # Nos ayuda a encontrar sinonimos de palabras.

# indicamos la ruta donde nltk buscara los datos descargados en nuestro computador
nltk.data.path.append(r'C:\Users\LENOVO\AppData\Roaming\nltk_data')

# Descargamos las herramentas necesarias para NLTK para el analisis de palbras.

nltk.download('punkt') # paquete para dividir frases en palabras.
nltk.download('wordnet') # paquete para encontrar sinonimos de palabras.
nltk.download('punkt_tab')

# Funcion para cargar las peliculas desde un archivo CSV

def load_movies():
    # Leemos el archivo que contiene informacion de peliculas y seleccionamos las columnas mas importantes
    df = pd.read_csv("Dataset/netflix_titles.csv")[['show_id', 'title', 'release_year', 'listed_in', 'rating',
    'description']]
    #Renombramos las columnas para que sean mas faciles de entender
    df.columns = ['id', 'title', 'year', 'category', 'rating', 'overview']
    
    # Llenamos los espacios vacios con texto vacio y convertimos los datos en una lista de diccionarios
    return df.fillna('').to_dict(orient='records')

# Cargamos las peliculas al iniciar la API para no leer el archivo cada vez que alguien pregunte por ellas.
movies_list = load_movies()

# Funcion para encontrar sinonimos de una palabra

def get_synonyms(word):
    # Usamos WordNet para obtener distintas palabras que significan lo mismo.
    return{lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Creamos la aplicacion de FastAPI, que sera el motor de nuestra API
# Esto inicializa la API con un nombre y una version.
app = FastAPI(title="Mi aplicacion de peliculas", version="1.0.0")

# Ruta de inicio: cuando alguien entra a la API sin especificar nada, vera un mensaje de bienvenida.

@app.get("/", tags=['Home'])
def home():
# Cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida.
    return HTMLResponse('<h1>Bienvenido a la API de peliculas</h1>')

# Obteniendo la lista de peliculas
# Creamos una ruta para obtener todas las peliculas

# Ruta para obtener todas las peliculas disponibles

@app.get('/movies', tags=['Movies'])
def get_movies():
    # si hay peliculas, las enviamos, si no, mostramos un error
    return movies_list or HTTPException(status_code=500, detail="no hay datos de peliculas disponibles")


# Ruta para obtener una pelicula especifica segun su ID
@app.get('/movies/{id}', tags=['Movies'])
def get_movie(id: str):
    # Buscamos en la lista de peliculas la que tenga el mismo ID
    return next((m for m in movies_list if m['id'] == id), {"detalle": "pelicula no entrada"})

# Ruta del chatbot que responde con peliculas segun palabras clave de la categoria

@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la cunsulta en palabras clave, para entender mejor la intencion del usuario
    query_words = word_tokenize(query.lower())
    
    # Buscamos sinonimos de las palabras clave para ampliar la busqueda
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)
    
    # Filtramos la lista de peliculas buscando coincidencias en la categoria
    results = [m for m in movies_list if any (s in m['category'].lower() for s in synonyms)]
    
    # Si ebcontamos peliculas, enviamos la lista; si no, mostramos un mensaje de que no se encontraron coincidencias
    
    return JSONResponse (content={
        "respuesta": "Aqui tienes algunas peliculas relacionadas." if results else "no encontre peliculas en esa categoria.",
        "peliculas": results
    })
    # Ruta para buscar peliculas por categoria especifica
    
@app.get ('/movies/by_category/', tags=['movies'])
def get_movies_by_category(category: str):
    # Filtramos la lista de peliculas segun la categoria ingresada
    return [m for m in movies_list if category.lower() in m['category'].lower()]
    
    
    
    
    

    
