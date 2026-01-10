#####################################################################
# Rozwiązanie zadania z FastAPI na ocenę 4.0
# Autor: Rami Ayoush
# ###################################################################

from http.client import responses
import sqlite3

from fastapi import FastAPI, HTTPException
import requests

from typing import Any

app = FastAPI()

######################################################################
# Część wstępna labu: punkty 1-4 konspektu (przed obsługą bazy danych)
######################################################################

# Wyswietla napis "Hello World"
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Wyswietla napis "Hello {name}"
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# Oblicza sumę x oraz y; domyślnie x = 0, y = 10
@app.get("/sum")
def sum(x: int = 0, y: int = 10):
    return x+y

# Podaje nazwę miejsca o współrzędnych geograficznych lat (szerokość geograficzna) i lon (długość geograficzna)
@app.get("/geocode")
def geoc(lat: float, lon: float):
    url=f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}" #http://api.open-notify.org/?lat={lat}&lon={lon}
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()

#######################################################################
# Część labu od punktu 5 (obsługa bazy danych)
#######################################################################

# Funkcja łączy się z bazą danych dbase i tworzy cursor
#def init_connection(dbase: str):
#    db = sqlite3.connect(dbase)
#    cursor = db.cursor()
#init_connection()

# Pobiera informacje o filmach z bazy movies.db; zwraca wynik w formie listy słowników
@app.get('/movies')
def get_movies():
    try:
        db = sqlite3.connect('movies.db')
        cursor = db.cursor()
        movies = cursor.execute('SELECT * FROM movies').fetchall()
        db.close()

        output = []
        for movie in movies:
            movie = {'id': movie[0], 'title': movie[1], 'year': movie[2], 'actors': movie[3]}
            output.append(movie)
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Pobiera informacje o filmie z id = {movie_id}
@app.get('/movies/{movie_id}')
def get_single_movie(movie_id:int):
    try:
        db = sqlite3.connect('movies.db')
        cursor = db.cursor()
        movie = cursor.execute(f"SELECT * FROM movies WHERE id={movie_id}").fetchone()
        db.close()

        if movie is None:
            return {"message": "Nie znaleziono filmu"}
        return {"id": movie[0], "title": movie[1], "year": movie[2], "actors": movie[3]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")
    
# Dodaje film do bazy
@app.post("/movies")
def add_movie(params: dict[str, Any]):
    try:
        db = sqlite3.connect('movies.db')
        cursor = db.cursor()
        cursor.execute('INSERT INTO movies (title, year, actors) VALUES (?, ?, ?)', (params["title"], params["year"], params["actors"]))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": f"Film zostal dodany!"}
        else:
            return {"message": f"Nic nie dodano!"}       
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Usuwa wszystkie filmy z bazy
@app.delete("/movies")
async def rem_movies_all():
    try:
        db = sqlite3.connect('movies.db')
        cursor = db.cursor()
        cursor.execute('DELETE FROM movies;')
        db.commit()

        if cursor.rowcount > 0:
            db.close()
            return {"message": f"Wszystkie filmy zostały usunięte!"}
        else:
            db.close()
            return {"message": f"Nic nie zostało zmodyfikowane/pusta tabela"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")


# Aktualizuje dane filmu o id = {id}
@app.put("/movies/{id}")
def update_movie_id(id: int, params: dict[str, Any]):
    try:
        db = sqlite3.connect('movies.db')
        cursor = db.cursor()
        cursor.execute('UPDATE movies SET title = ?, year = ?, actors =? WHERE id = ?;', (params["title"], params["year"], params["actors"], id))
        db.commit()
        if cursor.rowcount > 0:
            db.close()
            return {"message": f"Dane filmu zostały zaktualizowane"}
        else:
            db.close()
            return {"message": f"Nic nie zostało zmodyfikowane"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")

# Usuwa film o id = {id}
@app.delete("/movies/{id}")
def rem_movie_id(id: int):
    try:
        db = sqlite3.connect('movies.db')
        cursor = db.cursor()
        cursor.execute('DELETE FROM movies WHERE id = ?;', (id,))
        db.commit()
        if cursor.rowcount > 0:
            db.close()
            return {"message": f"Film został usunięty"}
        else:
            db.close()
            return {"message": f"Nic nie zostało zmodyfikowane"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd: {str(e)}")



