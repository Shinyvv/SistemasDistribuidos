from flask import Flask, request, jsonify
import redis
import json
from elasticsearch import Elasticsearch
import os

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
es = Elasticsearch(ELASTIC_URL)

hits = 0
misses = 0

@app.route("/query")
def query():
    global hits, misses
    key = request.args.get("key")
    index = request.args.get("index")
    if not key or not index:
        return jsonify({"error": "ParÃ¡metros requeridos: key e index"}), 400

    cache_key = f"{index}:{key}"
    cached_result = r.get(cache_key)

    if cached_result:
        hits += 1
        return jsonify({"source": "cache", "result": json.loads(cached_result)})
    
    misses += 1
    query_body = {
        "query": {
            "multi_match": {
                "query": key,
                "fields": ["nombre_comuna", "tipo_evento"]
            }
        }
    }
    res = es.search(index=index, body=query_body)
    r.set(cache_key, json.dumps(res["hits"]["hits"]), ex=300)
    return jsonify({"source": "elasticsearch", "result": res["hits"]["hits"]})

@app.route("/hit_rate")
def hit_rate():
    total = hits + misses
    rate = hits / total if total > 0 else 0
    return jsonify({"hits": hits, "misses": misses, "hit_rate": round(rate, 2)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)