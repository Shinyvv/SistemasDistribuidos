FROM python:3.10-slim

WORKDIR /app

COPY filtering.py ./
RUN pip install pymongo

CMD ["python", "filtering.py"]
