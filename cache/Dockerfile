FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask redis elasticsearch
CMD ["python", "cache.py"]