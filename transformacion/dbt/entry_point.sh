#!/bin/bash

# Entry point simplificado para el contenedor de dbt
# Solo clona el repositorio y genera el archivo profiles.yml
# La ejecución de dbt la maneja la tarea ECS

set -e

echo "=== Iniciando setup del contenedor dbt ==="
echo "Fecha: $(date)"

# Directorio de trabajo
WORK_DIR="/app"
DBT_DIR="${WORK_DIR}/dbt"

# Crear directorio de trabajo
mkdir -p $WORK_DIR
cd $WORK_DIR

echo "=== Clonando repositorio ==="
# Siempre clonar el repositorio completo para obtener la versión más reciente
echo "Clonando repositorio completo..."
git clone https://github.com/proyectosdateneo/especializacion-ingenieria-de-datos.git temp_repo

echo "Copiando carpeta de dbt..."
# Eliminar directorio anterior si existe
rm -rf $DBT_DIR
cp -r temp_repo/transformacion/dbt $DBT_DIR

echo "Limpiando repositorio temporal..."
rm -rf temp_repo

cd $DBT_DIR

echo "=== Verificando estructura del repositorio ==="
ls -la

# Generar archivo de configuración profiles.yml dinámicamente
echo "=== Generando archivo de configuración profiles.yml ==="
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << EOF
datavision:
  target: prod
  outputs:
    prod:
      type: athena
      s3_staging_dir: ${S3_STAGING_DIR}
      s3_data_naming: schema_table
      s3_tmp_table_dir: ${S3_TMP_TABLE_DIR}
      region_name: ${REGION_NAME}
      schema: ${SCHEMA_NAME}
      database: ${DATABASE_NAME}
      threads: 4
      work_group: ${ATHENA_WORK_GROUP}
      # aws_profile_name no es necesario, se usa el rol IAM de ECS
EOF

echo "Archivo ~/.dbt/profiles.yml generado:"
cat ~/.dbt/profiles.yml

echo "=== Setup del contenedor dbt completado ==="
echo "Fecha: $(date)"
echo "El contenedor está listo para ejecutar tareas ECS"

# Ejecutar el comando que ECS envíe como argumento
exec "$@"
