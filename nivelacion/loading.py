import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import datetime
import config_etl
import os

def load_to_s3(transformed_df):
    """Carga el DataFrame transformado a S3 como un archivo CSV."""
    if transformed_df.empty:
        print("DataFrame transformado está vacío. No se cargará nada a S3.")
        return False

    s3_config = config_etl.get_s3_config()
    bucket_name = s3_config['bucket_name']
    aws_profile = s3_config.get('aws_profile') # Puede ser None
    aws_region = s3_config.get('aws_region')

    # Nombre del archivo CSV
    current_date_str = datetime.now().strftime("%Y%m%d")
    file_name = f"reporte_cuentas_enterprise_{current_date_str}.csv"
    local_file = f"temp/{file_name}"

    # Crear directorio temporal si no existe
    if not os.path.exists('temp'):
        os.makedirs('temp')

    print(f"Intentando subir {file_name} al bucket S3 {bucket_name}...")

    try:
        # Guardar DataFrame como CSV localmente
        transformed_df.to_csv(local_file, index=False)
        print(f"Archivo CSV guardado localmente en: {local_file}")

        # Configurar sesión de Boto3
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
        else:
            # Usará credenciales de variables de entorno, roles IAM, etc.
            session = boto3.Session(region_name=aws_region)
        
        s3_client = session.client('s3')
        
        try:
            # Subir archivo a S3
            s3_client.upload_file(local_file, bucket_name, file_name)
            print(f"Archivo {file_name} cargado exitosamente a s3://{bucket_name}/{file_name}")
            
            # Solo eliminar el archivo local si la subida fue exitosa
            os.remove(local_file)
            print("Archivo local eliminado")
            return True

        except NoCredentialsError:
            print("Error de credenciales AWS: No se encontraron credenciales.")
            print(f"El archivo local se mantiene en: {local_file}")
        except PartialCredentialsError:
            print("Error de credenciales AWS: Credenciales incompletas.")
            print(f"El archivo local se mantiene en: {local_file}")
        except ClientError as e:
            # Errores más específicos de S3 (ej. bucket no encontrado, permisos)
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'NoSuchBucket':
                print(f"Error: El bucket S3 '{bucket_name}' no existe.")
            elif error_code == 'AccessDenied':
                print(f"Error: Acceso denegado al bucket S3 '{bucket_name}'. Verifica los permisos.")
            else:
                print(f"Error al cargar a S3: {e}")
            print(f"El archivo local se mantiene en: {local_file}")
        except Exception as e:
            print(f"Un error inesperado ocurrió al cargar a S3: {e}")
            print(f"El archivo local se mantiene en: {local_file}")

    except Exception as e:
        print(f"Error al guardar el archivo CSV localmente: {e}")
    
    return False

if __name__ == '__main__':
    # Para probar el módulo directamente

    print("Ejecutando módulo de carga con datos de ejemplo...")
    sample_data_for_s3 = pd.DataFrame({
        'account_id': [1, 3, 4],
        'account_name': ['Empresa A', 'Empresa C', 'Empresa D'],
        'email': ['a@test.com', 'c@test.com', 'd@test.com'],
        'account_created_at': ['2023-01-01 00:00:00', '2023-03-10 00:00:00', '2021-11-20 00:00:00'],
        'subscription_name': ['Empresarial', 'Empresarial', 'Empresarial'],
        'fecha_upgrade': ['2023-06-01 00:00:00', '2023-08-01 00:00:00', '2023-01-01 00:00:00'],
        'dias_antiguedad_cuenta': [180, 150, 500], # Valores de ejemplo
        'dias_desde_upgrade': [30, 20, 180]    # Valores de ejemplo
    })

    success = load_to_s3(sample_data_for_s3)
    if success:
        print("Prueba de carga a S3 completada exitosamente.")
    else:
        print("Prueba de carga a S3 falló. Revisa los mensajes de error.") 