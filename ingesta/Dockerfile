# Dockerfile (ingesta/Dockerfile)
# Construye la imagen colocando el código en /app/ingesta para que coincida con entry_point.sh

FROM python:3.13-slim

# el entrypoint espera /app/ingesta
WORKDIR /app/ingesta

# deps de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# con context: ./ingesta, este requirements.txt existe en la raíz del contexto
COPY requirements.txt .

# instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# copiar el resto del código de ingesta al WORKDIR (/app/ingesta)
COPY . .

# asegurar permisos del entrypoint (vive en /app/ingesta)
RUN chmod +x /app/ingesta/entry_point.sh

# por seguridad, no correr como root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# el entrypoint delega a "$@" (comando definido en la Task Definition/overrides)
ENTRYPOINT ["/app/ingesta/entry_point.sh"]
