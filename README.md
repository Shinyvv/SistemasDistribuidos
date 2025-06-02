MONGODB
-------
# Conectarse a MongoDB
mongo mongodb://localhost:27017

# Comandos útiles MongoDB
use waze                // Seleccionar base de datos
db.eventos.count()      // Contar documentos
db.eventos.find()       // Ver documentos

CONFIGURACIONES


-copiar la data a la base
docker cp eventos1.json mongo-waze:/eventos1.json
docker cp eventos2.json mongo-waze:/eventos2.json


docker exec -it mongo-waze bash
mongoimport --db waze --collection eventos --file /eventos1.json --jsonArray
mongoimport --db waze --collection eventos --file /eventos2.json --jsonArray
mongoimport --db waze --collection eventos --file /eventos2.json

docker compose build
docker compose up -d
funciona!!!





--------------
Redis LRU 10MB:    puerto 6379
Redis Random 10MB: puerto 6380
Redis LRU 50MB:    puerto 6381  
Redis Random 50MB: puerto 6382
MongoDB:          puerto 27017

PARÁMETROS GENERADOR
-------------------
--modelo: poisson, uniforme, random
--tasa: frecuencia de consultas (default 5)
--cantidad: número total de consultas (default 10100)

TROUBLESHOOTING
--------------
1. Si Redis no responde:
   docker-compose restart redis-lru-10mb

2. Si el scraper falla:
   docker-compose logs scraper
   docker-compose restart scraper

3. Limpiar todo y empezar de nuevo:
   docker-compose down
   docker volume prune
   docker-compose up -d

=============================================
