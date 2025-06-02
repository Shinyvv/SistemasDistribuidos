import pymongo
import csv
from datetime import datetime
from pymongo.errors import ConnectionFailure
import os
os.makedirs("/output", exist_ok=True)


MONGO_HOST = "mongodb"
MONGO_PORT = 27017
MONGO_DB = "waze"
MONGO_COLLECTION = "eventos"

CAMPOS_REQUERIDOS = ["uuid", "type", "location", "pubMillis", "roadType", "street", "city"]

def normalizar_evento(evento):
    try:
        return {
            "uuid": evento.get("uuid", ""),
            "tipo": evento.get("type", "desconocido").lower().strip(),
            "comuna": evento.get("city", "desconocida").lower().strip(),
            "timestamp": datetime.fromtimestamp(evento.get("pubMillis", 0)/1000).isoformat(),
            "timestamp_clave": int(evento.get("pubMillis", 0) / 1000 / 300),
            "lat": round(evento["location"]["y"], 3),
            "lon": round(evento["location"]["x"], 3),
            "descripcion": evento.get("reportDescription", "").lower().strip()
        }
    except Exception:
        return None

def conectar_mongo():
    try:
        cliente = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT, serverSelectionTimeoutMS=5000)
        cliente.server_info()
        return cliente[MONGO_DB][MONGO_COLLECTION]
    except ConnectionFailure:
        return None

def filtrar_y_guardar():
    collection = conectar_mongo()
    if collection is None:
        return

    eventos = collection.find()
    eventos_filtrados = []
    eventos_clave = set()

    for evento in eventos:
        if not all(k in evento for k in CAMPOS_REQUERIDOS):
            continue

        normalizado = normalizar_evento(evento)
        if not normalizado:
            continue

        clave = (
            normalizado["tipo"],
            normalizado["comuna"],
            normalizado["timestamp_clave"],
            normalizado["lat"],
            normalizado["lon"]
        )

        if clave in eventos_clave:
            continue

        eventos_clave.add(clave)
        eventos_filtrados.append({
            "uuid": normalizado["uuid"],
            "tipo": normalizado["tipo"],
            "comuna": normalizado["comuna"],
            "timestamp": normalizado["timestamp"],
            "descripcion": normalizado["descripcion"]
        })

    with open("/output/eventos_limpios.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["uuid", "tipo", "comuna", "timestamp", "descripcion"])
        writer.writeheader()
        writer.writerows(eventos_filtrados)

if __name__ == "__main__":
    filtrar_y_guardar()
