# Imagem base leve do Python 3.10
FROM python:3.10-slim

# Instalar dependências de sistema para Postgres (psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Expor porta da API
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]