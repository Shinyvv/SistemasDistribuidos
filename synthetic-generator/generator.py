import os
import time
import random
import argparse
import numpy as np
from pymongo import MongoClient
import redis
import json
from copy import deepcopy

def conectar_mongo():
    mongo_host = os.getenv("MONGO_HOST", "localhost")
    mongo_port = int(os.getenv("MONGO_PORT", 27017))
    mongo_db = os.getenv("MONGO_DB", "waze")
    cliente_mongo = MongoClient(mongo_host, mongo_port)
    return cliente_mongo[mongo_db]

def conectar_redis():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    return redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

def obtener_memoria_redis(conexion_redis):
    try:
        info_memoria = conexion_redis.info("memory")
        usada_mb = info_memoria.get("used_memory", 0) / (1024 * 1024)
        limite_mb = info_memoria.get("maxmemory", 0) / (1024 * 1024)
        return round(usada_mb, 2), round(limite_mb, 2)
    except:
        return 0, 0

def main(args):
    base_datos = conectar_mongo()
    conexion_redis = conectar_redis()

    politica_cache = os.getenv("POLITICA", "DESCONOCIDA")
    coleccion_eventos = base_datos[os.getenv("MONGO_COLLECTION", "eventos")]

    eventos_disponibles = list(coleccion_eventos.find())
    if not eventos_disponibles:
        print("[ERROR] No hay eventos en MongoDB para consultar.")
        return

    print(f"[INFO] Generador de tráfico iniciado.")
    print(f"Política de Cache activa: {politica_cache}")

    total_consultas = 0
    cantidad_hits = 0
    cantidad_misses = 0

    for _ in range(args.cantidad):
        evento = random.choice(eventos_disponibles)
        id_evento = evento.get("uuid")

        if not id_evento:
            continue

        evento_clonado = deepcopy(evento)
        evento_clonado.pop("_id", None)

        if conexion_redis.exists(id_evento):
            cantidad_hits += 1
        else:
            cantidad_misses += 1
            conexion_redis.set(id_evento, json.dumps(evento_clonado))

        total_consultas += 1

        if total_consultas % 100 == 0:
            print(f"[{total_consultas}/{args.cantidad}] eventos procesados", flush=True)

        if args.modelo == "poisson":
            intervalo = np.random.exponential(1.0 / args.tasa)
        elif args.modelo == "uniforme":
            intervalo = random.uniform(0.5, 2.0)
        elif args.modelo == "random":
            intervalo = random.random() 
        else:
            intervalo = 1

        time.sleep(intervalo)

    memoria_usada, memoria_maxima = obtener_memoria_redis(conexion_redis)

    print("\nResumen Final")
    print(f"Política de Cache: {politica_cache}")
    print(f"Memoria usada para cache: {memoria_usada:.2f} MB / {memoria_maxima:.2f} MB")
    print(f"Total de consultas realizadas: {total_consultas}")
    print(f" Hits: {cantidad_hits} ({(cantidad_hits / total_consultas) * 100:.2f}%)")
    print(f" Misses: {cantidad_misses} ({(cantidad_misses / total_consultas) * 100:.2f}%)")
    print("Termino")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--modelo", choices=["poisson", "uniforme","random"], required=True, help="Modelo")
    parser.add_argument("--tasa", type=float, default=5, help="Tasa de llegada")
    parser.add_argument("--cantidad", type=int, default=10000, help="Cantidad de consultas")
    args = parser.parse_args()

    main(args)
