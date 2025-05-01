import os
import json
import time
import requests
from datetime import datetime
from collections import defaultdict
from pymongo import MongoClient, errors

URL_WAZE = "https://www.waze.com/live-map/api/georss?top=-33.3&bottom=-33.7&left=-70.95&right=-70.35&env=row&types=alerts,traffic"
INTERVALO_ENTRE_CONSULTAS = 100  
PAUSA_EXTRA_EVENTOS = 100        
EVENTOS_ANTES_DE_PAUSA = 100

COMUNAS_REGION_METROPOLITANA = {
    "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", "Huechuraba",
    "Independencia", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina",
    "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "Ñuñoa",
    "Pedro Aguirre Cerda", "Peñalolén", "Providencia", "Pudahuel", "Puente Alto", "Quilicura",
    "Quinta Normal", "Recoleta", "Renca", "San Joaquín", "San Miguel", "San Ramón",
    "Santiago", "Vitacura", "San Bernardo", "Calera de Tango", "Buin", "Paine", "Talagante",
    "El Monte", "Isla de Maipo", "Padre Hurtado", "Peñaflor", "Melipilla", "Alhué", "Curacaví",
    "María Pinto", "San Pedro", "Colina", "Lampa", "Tiltil", "Malloco, Peñaflor", "San José de Maipo"
}

def conectar_mongo():
    mongo_host = os.getenv("MONGO_HOST", "localhost")
    mongo_port = int(os.getenv("MONGO_PORT", 27017))
    mongo_db_nombre = os.getenv("MONGO_DB", "waze")
    mongo_collection = os.getenv("MONGO_COLLECTION", "eventos")

    cliente_mongo = MongoClient(mongo_host, mongo_port)
    base_datos = cliente_mongo[mongo_db_nombre]
    coleccion_eventos = base_datos[mongo_collection]
    coleccion_eventos.create_index("uuid", unique=True)
    return coleccion_eventos

def pertenece_a_rm(ciudad, nearby):
    return ciudad in COMUNAS_REGION_METROPOLITANA or nearby in COMUNAS_REGION_METROPOLITANA

def main():
    coleccion = conectar_mongo()
    contador_nuevos_eventos = 0

    print(f"[{datetime.now()}] Scraper conectado", flush=True)

    while True:
        try:
            respuesta = requests.get(URL_WAZE)
            respuesta.raise_for_status()
            datos = respuesta.json()

            total_eventos = 0
            nuevos_eventos = 0
            eventos_en_rm = 0
            eventos_fuera_rm = 0
            comunas_fuera_rm = defaultdict(int)

            for evento in datos.get("alerts", []) + datos.get("jams", []):
                total_eventos += 1
                uuid_evento = evento.get("uuid")
                ciudad_evento = evento.get("city", "SIN_CIUDAD")
                nearby_evento = evento.get("nearBy", "SIN_NEARBY")

                if pertenece_a_rm(ciudad_evento, nearby_evento):
                    eventos_en_rm += 1
                else:
                    eventos_fuera_rm += 1
                    comuna_fuera = nearby_evento if ciudad_evento == "SIN_CIUDAD" else ciudad_evento
                    comunas_fuera_rm[comuna_fuera] += 1

                if uuid_evento:
                    try:
                        coleccion.insert_one(evento)
                        nuevos_eventos += 1
                        contador_nuevos_eventos += 1
                    except errors.DuplicateKeyError:
                        pass

            porcentaje_en_rm = (eventos_en_rm / total_eventos * 100) if total_eventos > 0 else 0
            porcentaje_fuera_rm = 100 - porcentaje_en_rm

            print("\nNuevo Ciclo", flush=True)
            print(f"Nuevos eventos insertados en MongoDB: {nuevos_eventos}", flush=True)
            print(f"Total acumulado de eventos en MongoDB: {coleccion.estimated_document_count()} eventos\n", flush=True)

            if contador_nuevos_eventos >= EVENTOS_ANTES_DE_PAUSA:
                print(f"Pausa Extra", flush=True)
                time.sleep(PAUSA_EXTRA_EVENTOS)
                contador_nuevos_eventos = 0
            else:
                print(f"Esperando por si acaso\n", flush=True)
                time.sleep(INTERVALO_ENTRE_CONSULTAS)

        except Exception as error:
            print(f"ERROR\n")
            time.sleep(3)

if __name__ == "__main__":
    main()
