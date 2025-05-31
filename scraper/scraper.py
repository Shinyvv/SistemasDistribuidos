import os
import time
from datetime import datetime
from pymongo import MongoClient, errors
from playwright.sync_api import sync_playwright

INTERVALO_ENTRE_CONSULTAS = 50  
PAUSA_EXTRA_EVENTOS = 50        
LIMITE_EVENTOS = 50

ZONAS_RM = [
    (-33.4489, -70.6693), (-33.4569, -70.6483), (-33.5019, -70.7594), (-33.4284, -70.5737),
    (-33.3955, -70.7856), (-33.5866, -70.7055), (-33.3773, -70.6414), (-33.4189, -70.6075),
    (-33.4811, -70.6126), (-33.4027, -70.5796)
]

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
    cliente_mongo = MongoClient(mongo_host, mongo_port)
    base_datos = cliente_mongo["waze"]
    coleccion_eventos = base_datos["eventos"]
    coleccion_eventos.create_index("uuid", unique=True)
    return coleccion_eventos

def pertenece_a_rm(ciudad, nearby):
    return ciudad in COMUNAS_REGION_METROPOLITANA or nearby in COMUNAS_REGION_METROPOLITANA

def extraer_eventos(lat, lon):
    eventos = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def interceptar_respuesta(response):
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    data = response.json()
                    for key in ("alerts", "jams"):
                        if key in data:
                            eventos.extend(data[key])
                except Exception:
                    pass

        page.on("response", interceptar_respuesta)
        page.goto("https://www.waze.com/live-map")
        page.wait_for_timeout(5000)

        try:
            page.evaluate(f"""() => {{
                if (typeof W !== 'undefined' && W.map && typeof W.map.setCenter === 'function') {{
                    W.map.setCenter({{lat: {lat}, lon: {lon}}});
                    W.map.setZoom(11);
                }}
            }}""")
        except:
            pass

        for _ in range(5):
            page.keyboard.press('-')
            page.wait_for_timeout(500)

        page.wait_for_timeout(8000)
        browser.close()

    return eventos

def main():
    coleccion = conectar_mongo()
    contador_nuevos_eventos = 0
    contador_zona = 0

    print(f"Scraper iniciado", flush=True)

    while True:
        try:
            lat, lon = ZONAS_RM[contador_zona]
            eventos_live = extraer_eventos(lat, lon)
            print(f"Eventos recibidos: {len(eventos_live)}", flush=True)

            nuevos_eventos = 0

            for evento in eventos_live:
                uuid = evento.get("uuid")
                ciudad = evento.get("city", "SIN_CIUDAD")
                nearby = evento.get("nearBy", "SIN_NEARBY")

                if not uuid:
                    continue

                if pertenece_a_rm(ciudad, nearby):
                    try:
                        coleccion.insert_one(evento)
                        nuevos_eventos += 1
                        contador_nuevos_eventos += 1
                    except errors.DuplicateKeyError:
                        pass

            print(f"Nuevos insertados: {nuevos_eventos} - total en Mongo: {coleccion.estimated_document_count()}", flush=True)

            if contador_nuevos_eventos >= LIMITE_EVENTOS:
                print("PAUSA", flush=True)
                time.sleep(PAUSA_EXTRA_EVENTOS)
                contador_nuevos_eventos = 0
            else:
                print("Esperando\n", flush=True)
                time.sleep(INTERVALO_ENTRE_CONSULTAS)

            if len(eventos_live) < 10:
                contador_zona = (contador_zona + 1) % len(ZONAS_RM)
                print(" Cambiando zona\n", flush=True)

        except:
            time.sleep(3)

if __name__ == "__main__":
    main()
