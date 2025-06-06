import yaml
import os

# Ruta al archivo de configuración específico del ETL
# Asume que este script está en nivelacion/solucion/
# y etl_config.yaml está en el mismo directorio.
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'etl_config.yaml')

def load_db_config():
    """Carga la configuración de la base de datos desde etl_config.yaml."""
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = yaml.safe_load(file)
        
        if 'database' not in config or config['database'] is None:
            raise ValueError("La sección 'database' no está definida o está vacía en etl_config.yaml")

        db_conf = config['database']
        # Permitir overrides por variables de entorno si se desea, pero los valores base vienen del YAML
        return {
            'host': os.environ.get('DB_HOST', db_conf.get('host')),
            'port': int(os.environ.get('DB_PORT', db_conf.get('port', 5432))),
            'name': os.environ.get('DB_NAME', db_conf.get('name')),
            'user': os.environ.get('DB_USER', db_conf.get('username')),
            'password': os.environ.get('DB_PASSWORD', db_conf.get('password'))
        }
    except FileNotFoundError:
        print(f"Error: El archivo de configuración {CONFIG_FILE_PATH} no fue encontrado.")
        print("Por favor, crea etl_config.yaml en la carpeta nivelacion/solucion/ con la configuración necesaria.")
        raise
    except (KeyError, TypeError) as e:
        print(f"Error: Falta una clave o hay un tipo incorrecto en la sección 'database' de {CONFIG_FILE_PATH}. Detalles: {e}")
        raise
    except ValueError as e:
        print(f"Error de configuración en 'database': {e}")
        raise

def get_s3_config():
    """Carga la configuración de S3 desde etl_config.yaml."""
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = yaml.safe_load(file)

        if 's3_destination' not in config or config['s3_destination'] is None:
            raise ValueError("La sección 's3_destination' no está definida o está vacía en etl_config.yaml")

        s3_conf = config['s3_destination']
        
        bucket_name = os.environ.get('S3_BUCKET_ETL', s3_conf.get('bucket_name'))
        aws_profile = os.environ.get('AWS_PROFILE_ETL', s3_conf.get('aws_profile')) # Puede ser None
        aws_region = os.environ.get('AWS_REGION_ETL', s3_conf.get('aws_region'))     # Puede ser None

        if not bucket_name:
            raise ValueError("El 'bucket_name' de S3 no está configurado en etl_config.yaml ni como variable de entorno S3_BUCKET_ETL.")
        
        return {
            'bucket_name': bucket_name,
            'aws_profile': aws_profile,
            'aws_region': aws_region
        }
    except FileNotFoundError:
        print(f"Error: El archivo de configuración {CONFIG_FILE_PATH} no fue encontrado.")
        print("Por favor, crea etl_config.yaml en la carpeta nivelacion/solucion/ con la configuración necesaria.")
        raise
    except (KeyError, TypeError) as e:
        print(f"Error: Falta una clave o hay un tipo incorrecto en la sección 's3_destination' de {CONFIG_FILE_PATH}. Detalles: {e}")
        raise
    except ValueError as e:
        print(f"Error de configuración S3: {e}")
        raise

# Para prueba directa del módulo
if __name__ == '__main__':
    print(f"Intentando cargar configuraciones desde: {CONFIG_FILE_PATH}")
    print("Asegúrate de que 'etl_config.yaml' exista en 'nivelacion/solucion/' y esté bien configurado.")
    print("Ejemplo de etl_config.yaml:")
    print("""
# Configuración para el ETL de Nivelación
database:
  host: "localhost"
  port: 5432
  name: "saas_db"
  username: "postgres_user"
  password: "postgres_password"
s3_destination:
  bucket_name: "mi-bucket-etl"
  # aws_profile: "mi_perfil_aws" # Opcional
  # aws_region: "us-east-1"    # Opcional
""")
    try:
        print("\nIntentando cargar configuración de BD...")
        db_settings = load_db_config()
        print(f"Configuración de BD cargada: {db_settings}")
    except Exception as e_db:
        print(f"Error al cargar configuración de BD: {e_db}")

    try:
        print("\nIntentando cargar configuración de S3...")
        s3_settings = get_s3_config()
        print(f"Configuración de S3 cargada: {s3_settings}")
    except Exception as e_s3:
        print(f"Error al cargar configuración de S3: {e_s3}") 