# Módulo de Nivelación de Datos

Este directorio contiene los componentes principales del proceso ETL (Extract, Transform, Load) para la nivelación de datos. Los scripts aquí contenidos permiten estandarizar y preparar los datos para su posterior análisis.

## Estructura del Directorio

- `main_etl.py`: Punto de entrada principal para la ejecución del pipeline ETL completo.
- `config_etl.py`: Configuraciones y constantes utilizadas en el proceso ETL.
- `ingestion.py`: Módulo encargado de la extracción de datos de las fuentes.
- `transformation.py`: Contiene las reglas de transformación y limpieza de datos.
- `loading.py`: Maneja la carga de datos transformados al destino final.
- `requirements.txt`: Lista de dependencias de Python necesarias.

## Requisitos

Instala las dependencias necesarias con:

```bash
pip install -r requirements.txt
```

## Uso

1. Configura los parámetros en un `etl_config.yaml` según tus necesidades.
2. Ejecuta el pipeline ETL completo:
   ```bash
   python main_etl.py
   ```

## Componentes Principales

### 1. Extracción (ingestion.py)
- Conexión a fuentes de datos
- Extracción de datos en lotes o completos
- Manejo de diferentes formatos de origen

### 2. Transformación (transformation.py)
- Limpieza de datos
- Normalización
- Aplicación de reglas de negocio
- Validación de datos

### 3. Carga (loading.py)
- Inserción en base de datos
- Manejo de actualizaciones incrementales
- Control de errores y reintentos

## Configuración

### Archivo de Configuración

Crea un archivo `etl_config.yaml` en la carpeta `nivelacion/solucion/` con la siguiente estructura:

```yaml
# Configuración de la base de datos de origen (PostgreSQL)
database:
  host: localhost
  port: 5432
  name: nombre_base_datos
  username: usuario
  password: contraseña

# Configuración de destino en S3
s3_destination:
  bucket_name: tu-bucket-etl  # Nombre del bucket S3
  aws_profile: default  # Perfil de credenciales AWS (opcional)
  region: us-east-1  # Región de AWS
```

### Variables de Entorno

Alternativamente, puedes sobreescribir la configuración con variables de entorno:

```bash
# Configuración de base de datos
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=nombre_bd
export DB_USER=usuario
export DB_PASSWORD=contraseña

# Configuración de S3
export S3_BUCKET_ETL=tu-bucket-etl
export AWS_PROFILE_ETL=default
export AWS_REGION=us-east-1
```

### Ejecución

```bash
# Ejecutar el ETL completo
python main_etl.py

# Ejecutar solo una etapa específica
python ingestion.py  # Solo extracción
python transformation.py  # Solo transformación
python loading.py  # Solo carga
```

### Estructura del Proyecto

- `config_etl.py`: Maneja la carga de configuración
- `etl_base.py`: Clase base para operaciones ETL
- `ingestion.py`: Extracción de datos desde PostgreSQL
- `transformation.py`: Transformación de datos
- `loading.py`: Carga de datos a S3
- `main_etl.py`: Punto de entrada principal
