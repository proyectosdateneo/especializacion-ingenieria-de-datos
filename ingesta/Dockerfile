FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python usando el requirements de ingesta
COPY ingesta/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar todo el repositorio dentro de la imagen
COPY . /app

# Copiar el script de entry point a /app y dar permisos de ejecución
COPY ingesta/entry_point.sh /app/entry_point.sh
RUN chmod +x /app/entry_point.sh

# Comando por defecto
ENTRYPOINT ["/app/entry_point.sh"]