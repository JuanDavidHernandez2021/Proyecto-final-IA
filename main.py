"""
Imagina que esta API es una biblioteca de peliculas.. la funcion load_movies() es como un bibliotecario que carga el catalogo de libros (pelicula) cuando se abre la biblioteca. la funcion get_movies() muestra todo el catalogo cuando alguien lo pide. La funcion get_movie(id) es como si alguien preguntara por una pelicula especifica por su codigo de identificacion. la funcion chatbot (query) es un asistente que busca peliculas segun palabras claves y sinonimo. la funcion get_movies_by_category(category) ayuda a encontrar peliculas segun su genero (acción, comedia, etc)  
"""

# Importamos las herramientas para construir nuesta API 
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException maneja errores
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse para paginas web, JSONResponse para respuestas en formato JSON
import pandas as pd #p pandas nos ayuda a manejar datos en tablas como si fuera un excel.
import nltk #nltk es un libreria para procesar texto y analizar palabras
from nltk.tokenize import word_tokenize # Se usa para dividir un texto en palabras individuales
from nltk. corpus import wordnet # Nos ayuda a encontrar sinonomos de palabras

# Descargamos la herramientas necesatias de nltk para el analisis de palabras

nltk.download('punkt') # Herramienta para dividir texto en palabras
nltk.download('wordnet') # Herramienta para encontrar sinonomos de palabras en ingles

# Indicamos la ruta donde nltk buscará los datos descartrgados en nuestro computador 
nltk.data.path.append(r'C:\Users\andre\AppData\Roaming\nltk_data')

# Funcion para cargar las peliculas desde un arvhivo CSV 
def load_movies():
    # Leemos el archivo que contiene informacion de peliculas y seleccionamos las columnas mas importantes
    df = pd.read_csv(r"Dataset/netflix_titles.csv")
    [['show_id','title','release_year','listed_in','description','rating']]

    # Renombramos las columnas para que sean más faciles de entender.
    df.columns = ['id','title','year','category','rating','overview']
    # Llenamos los espacios vacios con texto vacío y convertimos los datos en una lista de diccionarios
    return df.fillna('').to_dict(orient = 'records')

# Cargamos las películas al iniciar la API para no leer el archivo cada vez que alguien pregunte por ellas.
movies_list = load_movies()

# Función para encontrar sinónimos de una palabra (word)
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms

# Creamos la aplicación FastAPI, que será el motor de nuestra API
# Esto inicializa la API con un nombre y una versión
app = FastAPI(title="Mi aplicación de Películas", versión="1.0.0")

# Ruta de inicio: Cuando alguien entra a la API sin especificar nada, verá un mensaje de bienvenda
@app.get('/', tags=['Home'])
def home():
# Cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida.
    return HTMLResponse('<h1>Bienvenido a la API de Películas</h1>')

# Obteniendo la lista de películas
# Creamos una ruta para obtener todas las películas
# Ruta para obtener todas las películas disponibles

@app.get('/movies', tags=['Movies'])
def get_movies():
    # Si hay películas, las enviamos, si no, mostramos un error
    return movies_list or HTTPException(status_code=500, detail="No hay datos de películas disponibles")

# Ruta para obtener una película específica según su ID
@app.get('/movies/{id}', tags=['Movies'])
def get_movie(id : str):
    # Buscamos en la lista de películas la que tenga el mismo ID
    return next((m for m in movies_list if m['id'] == id), {"detalle": "película no encontrada"})

# Ruta del chatbot que responde con películas según palabras clave de la categoría
@app.get("/chatbot", tags=["Chatbot"])
def chatbot(query: str):
    try:
        # Intentamos tokenizar con word_tokenize
        query_words = word_tokenize(query.lower())
    except LookupError:
        # Si falla, usamos un método más simple
        query_words = query.lower().split()

    # Obtenemos sinónimos para cada palabra
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)

    # Validamos que la película tenga categoría y buscamos coincidencias
    results = [m for m in movies_list if any(s in m["title"].lower() for s in synonyms)]

    return JSONResponse(content={
        "respuesta": "Aquí tienes algunas películas relacionadas." if results else "No encontré películas en esa categoría.",
        "películas": results
    })



# Ruta para buscar películas por categoría específica
@app.get ('/movies/by_category/', tags=[ 'Movies'])
def get_movies_by_category( category: str):
    # Filtramos la lista de películas según la categoría ingresada
    return [m for m in movies_list if category.lower() in m['category'] .lower()]

