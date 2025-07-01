import requests
import time
import random

BASE_URL = "http://localhost:5000"

def hacer_consulta(valor_buscado, indice):
    url = f"{BASE_URL}/query?key={valor_buscado}&index={indice}"
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"{valor_buscado} - {indice}, fuente: {datos.get('source')}")
        else:
            print("Consulta fallida")
    except Exception as error:
        print(f"Error")

def mostrar_tasa_aciertos():
    url = f"{BASE_URL}/hit_rate"
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            print(f"Hit Rate: {datos['hit_rate']:.2f} , Hits: {datos['hits']}, Misses: {datos['misses']}")
        else:
            print("Error")
    except Exception as error:
        print(f"Error")

if __name__ == "__main__":
    comunas = ["Maipú", "Providencia", "Ñuñoa", "Puente Alto", "Las Condes", "La Florida", "Santiago", "Recoleta", "San Miguel"]
    tipos = ["jam", "chit_chat", "hazard", "road_closed", "police"]

    consultas = []
    consultas += [("Maipú", "eventos_comuna")] * 6
    consultas += [("jam", "eventos_tipo")] * 5
    consultas += [("Providencia", "eventos_comuna")] * 4
    consultas += [("chit_chat", "eventos_tipo")] * 4
    consultas += [("Ñuñoa", "eventos_comuna")] * 3
    consultas += [("hazard", "eventos_tipo")] * 3

    for _ in range(35):
        key = random.choice(comunas + tipos)
        index = "eventos_comuna" if key in comunas else "eventos_tipo"
        consultas.append((key, index))

    for key, index in consultas:
        hacer_consulta(key, index)
        mostrar_tasa_aciertos()
        time.sleep(0.3)