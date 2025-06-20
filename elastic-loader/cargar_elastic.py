import os
import csv
import time
from elasticsearch import Elasticsearch

def conectar_elasticsearch():
    es = None
    while es is None:
        try:
            es = Elasticsearch("http://elasticsearch:9200")
            if es.ping():
                break
        except Exception:
            time.sleep(30)
    return es

def esperar_archivos(rutas):
    for path in rutas:
        while not os.path.exists(path):
            time.sleep(2)

def indexar_archivo(path, index_name, headers, es):
    if not os.path.exists(path):
        return
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != len(headers):
                continue
            doc = dict(zip(headers, row))
            es.index(index=index_name, document=doc)

def indexar_eventos_crudos(path, es):
    if not os.path.exists(path):
        return
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = {
                "uuid": row["uuid"],
                "tipo": row["tipo"],
                "comuna": row["comuna"],
                "timestamp": row["timestamp"],
                "descripcion": row["descripcion"]
            }
            es.index(index="eventos_raw", document=doc)

if __name__ == "__main__":
    esperar_archivos([
        "/output/output_por_tipo/part-r-00000",
        "/output/output_por_comuna/part-r-00000",
        "/output/output_por_hora/part-r-00000",
        "/output/eventos_limpios.csv"
    ])

    es = conectar_elasticsearch()

    indexar_archivo("/output/output_por_tipo/part-r-00000", "eventos_tipo", ["tipo", "cantidad"], es)
    indexar_archivo("/output/output_por_comuna/part-r-00000", "eventos_comuna", ["comuna", "cantidad"], es)
    indexar_archivo("/output/output_por_hora/part-r-00000", "eventos_hora", ["hora", "cantidad"], es)
    indexar_eventos_crudos("/output/eventos_limpios.csv", es)
