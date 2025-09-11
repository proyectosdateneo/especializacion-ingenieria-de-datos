#!/bin/bash

# Entry point para el contenedor de ingesta
# Ahora asume que el repositorio ya está incluido en la imagen (copiado en build)
# Genera el archivo TOML y luego delega la ejecución al comando recibido

set -e

echo "=== Iniciando setup del contenedor ==="
echo "Fecha: $(date)"

# Directorio de trabajo
WORK_DIR="/app"
INGESTA_DIR="${WORK_DIR}/ingesta"

# Verificar que el repo ya esté copiado dentro de la imagen
if [ ! -d "$INGESTA_DIR" ]; then
    echo "ERROR: No se encontró el directorio ${INGESTA_DIR} dentro de la imagen."
    echo "Contenido de ${WORK_DIR}:"
    ls -la "$WORK_DIR" || true
    exit 1
fi

cd "$INGESTA_DIR"

echo "=== Verificando estructura del repositorio incluido en la imagen ==="
ls -la

# Generar archivo de configuración TOML dinámicamente
echo "=== Generando archivo de configuración TOML ==="
mkdir -p .dlt
cat > .dlt/secrets.toml << EOF
[sources.sql_database.credentials]
drivername = "postgresql"
database = "${DATABASE_NAME}"
password = "${DATABASE_PASSWORD}"
username = "${DATABASE_USERNAME}"
host = "${DATABASE_HOST}"
port = ${DATABASE_PORT}

[destination.filesystem]
bucket_url = "${BUCKET_URL}"

[destination.athena]
query_result_bucket = "${QUERY_RESULT_BUCKET}"
athena_work_group = "${ATHENA_WORK_GROUP}"
aws_data_catalog = "${AWS_DATA_CATALOG}"

[destination.filesystem.credentials]
# No se necesitan access keys ya que la autenticación es por rol IAM

[destination.athena.credentials]
# No se necesitan access keys ya que la autenticación es por rol IAM
region_name = "${REGION_NAME}"
EOF

echo "Archivo .dlt/secrets.toml generado:"
cat .dlt/secrets.toml

echo "=== Setup del contenedor completado ==="
echo "Fecha: $(date)"
echo "El contenedor está listo para ejecutar tareas ECS"

# Ejecutar el comando que ECS envíe como argumento
exec "$@"

