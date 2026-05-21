FROM python:3.12-slim

WORKDIR /app

# Instalace závislostí jako samostatná vrstva – cachuje se pokud se requirements nezmění
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
