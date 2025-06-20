FROM python:3.10

WORKDIR /app

COPY cargar_elastic.py .

RUN pip install elasticsearch

CMD ["python", "cargar_elastic.py"]
