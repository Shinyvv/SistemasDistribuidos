## Nuevos componentes

### 1. Módulo `filtering`

- **Función principal:** Conectar a MongoDB, extraer eventos, limpiar y normalizar campos, filtrar duplicados y exportar un archivo CSV limpio (`eventos_limpios.csv`).
- **Tecnologías:** Python, PyMongo.

### 2. Módulo `analyzer-pig`

- **Función principal:** Procesar el archivo CSV generado por el módulo `filtering`, generando estadísticas de:
  - Eventos por tipo.
  - Eventos por comuna.
  - Eventos por hora.
- **Tecnologías:** Apache Pig, Hadoop.

### 3. Carpeta `datos-salida`

- Contiene los archivos CSV resultantes del análisis.
- También se incluyen los gráficos generados en LaTeX para el informe.

## Instrucciones de uso.

### Requisitos

- Docker y Docker Compose instalados.

### Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Shinyvv/SistemasDistribuidos.git
   cd SistemasDistribuidos


2. copiar la data a la base
docker cp eventos1.json mongo-waze:/eventos1.json
docker cp eventos2.json mongo-waze:/eventos2.json
docker exec -it mongo-waze bash
mongoimport --db waze --collection eventos --file /eventos1.json --jsonArray
mongoimport --db waze --collection eventos --file /eventos2.json

3. Arrancar contenedores
docker compose build
docker compose up -d
funciona!!!

## En caso de no funcionar o querer probar contenedores especificos.

### Scraper
docker compose build scraper
docker compose run scraper

### filtering
docker compose build filtering
docker compose run filtering

### analyzer-pig
docker compose build analyzer-pig
docker compose run analyzer-pig
-Luego de correr estos dos se pueden observar los resultados en datos-salida.





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
