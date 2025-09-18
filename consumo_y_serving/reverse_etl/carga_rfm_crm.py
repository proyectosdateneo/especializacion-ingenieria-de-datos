#!/usr/bin/env python3
"""
Script de Reverse ETL para cargar segmentos RFM desde Athena a HubSpot.
Actualiza la propiedad segmento_rfm en las empresas de HubSpot basándose en los datos de Athena.
"""

import awswrangler as wr
import requests
import sys
import os
from datetime import datetime
import logging
import boto3
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Configuración de logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de HubSpot desde variables de entorno
HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY')
HUBSPOT_BASE_URL = os.getenv('HUBSPOT_BASE_URL', 'https://api.hubapi.com')

if not HUBSPOT_API_KEY:
    logger.error("HUBSPOT_API_KEY no está configurada. Configura esta variable de entorno.")
    sys.exit(1)

HUBSPOT_HEADERS = {
    'authorization': f'Bearer {HUBSPOT_API_KEY}',
    'content-type': 'application/json'
}

# Configuración de AWS desde variables de entorno
ATHENA_DATABASE = os.getenv('ATHENA_DATABASE', 'analytics_datavision_prod')
ATHENA_WORKGROUP = os.getenv('ATHENA_WORKGROUP', 'datavision-375612485931')
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
AWS_PROFILE = os.getenv('AWS_PROFILE')

def get_athena_rfm_data(limit=None):
    """
    Obtiene los datos de RFM desde Athena usando awswrangler.
    Retorna un DataFrame con id_cuenta y segmento_rfm_ultimo.
    
    Args:
        limit (int, optional): Límite de registros a procesar. Si es None, usa el valor por defecto.
    """
    logger.info("Obteniendo datos de RFM desde Athena...")
    
    # Usar límite desde variable de entorno o parámetro
    limit_value = limit or int(os.getenv('PROCESSING_LIMIT', '5'))
    
    query = f"""
    SELECT 
        id_cuenta,
        segmento_rfm_ultimo
    FROM dim_cuentas
    WHERE es_actual = true
    AND segmento_rfm_ultimo IS NOT NULL
    ORDER BY id_cuenta LIMIT {limit_value}
    """
    
    try:
        # Ejecutar query en Athena
        df = wr.athena.read_sql_query(
            sql=query,
            database=ATHENA_DATABASE,
            ctas_approach=False,
            workgroup=ATHENA_WORKGROUP
        )
        
        logger.info(f"Obtenidos {len(df)} registros de RFM desde Athena")
        return df
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de Athena: {str(e)}")
        raise

def get_hubspot_company_by_account_id(account_id):
    """
    Obtiene una empresa específica de HubSpot usando el id_datavision como identificador.
    Retorna el company_id si se encuentra, None si no.
    """
    try:
        url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/companies/{account_id}"
        params = {
            'idProperty': 'id_datavision',
            'properties': ['id_datavision', 'name', 'segmento_rfm']
        }
        
        response = requests.get(url, headers=HUBSPOT_HEADERS, params=params)
        
        if response.status_code == 200:
            company_data = response.json()
            company_id = company_data.get('id')
            logger.debug(f"Empresa encontrada para cuenta {account_id}: {company_id}")
            return company_id
        elif response.status_code == 404:
            logger.debug(f"Empresa no encontrada para cuenta {account_id}")
            return None
        else:
            logger.error(f"Error obteniendo empresa para cuenta {account_id}: {response.json()}")
            return None
            
    except Exception as e:
        logger.error(f"Error obteniendo empresa para cuenta {account_id}: {str(e)}")
        return None

def update_hubspot_company_rfm(company_id, segmento_rfm):
    """
    Actualiza la propiedad segmento_rfm de una empresa en HubSpot.
    """
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/companies/{company_id}"
    
    data = {
        'properties': {
            'segmento_rfm': segmento_rfm
        }
    }
    
    try:
        response = requests.patch(url, headers=HUBSPOT_HEADERS, json=data)
        
        if response.status_code == 200:
            logger.debug(f"Actualizada empresa {company_id} con segmento RFM: {segmento_rfm}")
            return True
        else:
            logger.error(f"Error actualizando empresa {company_id}: {response.json()}")
            return False
            
    except Exception as e:
        logger.error(f"Error actualizando empresa {company_id}: {str(e)}")
        return False

def process_rfm_updates(limit=None):
    """
    Procesa las actualizaciones de RFM desde Athena a HubSpot.
    
    Args:
        limit (int, optional): Límite de registros a procesar. Si es None, usa el valor por defecto.
    """
    logger.info("Iniciando proceso de actualización de RFM...")
    
    try:
        # 1. Obtener datos de RFM desde Athena
        rfm_df = get_athena_rfm_data(limit)
        
        if rfm_df.empty:
            logger.warning("No se encontraron datos de RFM en Athena")
            return
        
        # 2. Procesar actualizaciones
        updates_successful = 0
        updates_failed = 0
        not_found_in_hubspot = 0
        
        logger.info(f"Procesando {len(rfm_df)} cuentas...")
        
        for _, row in rfm_df.iterrows():
            account_id = row['id_cuenta']
            segmento_rfm = row['segmento_rfm_ultimo']
            
            # Buscar empresa en HubSpot usando id_cliente
            hubspot_company_id = get_hubspot_company_by_account_id(account_id)
            
            if hubspot_company_id:
                # Actualizar empresa en HubSpot
                if update_hubspot_company_rfm(hubspot_company_id, segmento_rfm):
                    updates_successful += 1
                    logger.debug(f"Actualizada cuenta {account_id} -> empresa {hubspot_company_id}")
                else:
                    updates_failed += 1
            else:
                not_found_in_hubspot += 1
                logger.warning(f"Cuenta {account_id} no encontrada en HubSpot")
        
        # 3. Resumen de resultados
        logger.info("=" * 50)
        logger.info("RESUMEN DE ACTUALIZACIONES RFM:")
        logger.info(f"Actualizaciones exitosas: {updates_successful}")
        logger.info(f"Actualizaciones fallidas: {updates_failed}")
        logger.info(f"Cuentas no encontradas en HubSpot: {not_found_in_hubspot}")
        logger.info(f"Total procesadas: {len(rfm_df)}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error en el proceso de actualización: {str(e)}")
        raise

def test_hubspot_connection():
    """
    Prueba la conexión con HubSpot.
    """
    logger.info("Probando conexión con HubSpot...")
    
    try:
        url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/companies"
        params = {'limit': 1}
        
        response = requests.get(url, headers=HUBSPOT_HEADERS, params=params)
        
        if response.status_code == 200:
            logger.info("Conexión con HubSpot exitosa")
            return True
        else:
            logger.error(f"Error de conexión con HubSpot: {response.json()}")
            return False
            
    except Exception as e:
        logger.error(f"Error de conexión con HubSpot: {str(e)}")
        return False

def test_athena_connection():
    """
    Prueba la conexión con Athena.
    """
    logger.info("Probando conexión con Athena...")
    
    try:
        # Query simple para probar conexión
        test_query = "SELECT 1 as test_column"
        
        df = wr.athena.read_sql_query(
            sql=test_query,
            database=ATHENA_DATABASE,
            ctas_approach=False  # Query simple, no necesita CTAS
        )
        
        logger.info("Conexión con Athena exitosa")
        return True
        
    except Exception as e:
        logger.error(f"Error de conexión con Athena: {str(e)}")
        return False

def test_data_mapping(test_account_id=None):
    """
    Prueba el mapeo de datos entre Athena y HubSpot.
    
    Args:
        test_account_id (int, optional): ID de cuenta específico para probar. Si es None, usa el valor por defecto.
    """
    logger.info("Probando mapeo de datos...")
    
    try:
        # Usar ID de cuenta específico o valor por defecto
        account_id_to_test = test_account_id or int(os.getenv('TEST_ACCOUNT_ID', '4'))
        
        # Obtener datos de RFM (limitado)
        rfm_query = f"""
        SELECT 
            id_cuenta,
            segmento_rfm_ultimo
        FROM dim_cuentas
        WHERE es_actual = true
        AND id_cuenta = {account_id_to_test}
        """
        
        rfm_df = wr.athena.read_sql_query(
            sql=rfm_query,
            database=ATHENA_DATABASE,
            ctas_approach=False
        )
        
        # Analizar coincidencias usando búsqueda directa
        matches = 0
        no_matches = 0
        
        logger.info("Análisis de coincidencias:")
        for _, row in rfm_df.iterrows():
            account_id = row['id_cuenta']
            segmento_rfm = row['segmento_rfm_ultimo']
            
            # Buscar empresa directamente por id_cliente
            hubspot_id = get_hubspot_company_by_account_id(account_id)
            
            if hubspot_id:
                matches += 1
                logger.info(f"Cuenta {account_id} (RFM: {segmento_rfm}) -> Empresa HubSpot {hubspot_id}")
            else:
                no_matches += 1
                logger.info(f"Cuenta {account_id} (RFM: {segmento_rfm}) -> No encontrada en HubSpot")
        
        logger.info(f"Resumen de mapeo:")
        logger.info(f"Coincidencias: {matches}")
        logger.info(f"Sin coincidencia: {no_matches}")
        logger.info(f"Total analizadas: {len(rfm_df)}")
        if len(rfm_df) > 0:
            logger.info(f"Tasa de coincidencia: {(matches/len(rfm_df))*100:.1f}%")
        
        return matches > 0
        
    except Exception as e:
        logger.error(f"Error en prueba de mapeo: {str(e)}")
        return False

def main():
    """
    Función principal.
    """
    logger.info("Iniciando script de carga RFM a CRM...")
    
    # Configurar sesión de AWS con variables de entorno
    session_kwargs = {'region_name': AWS_REGION}
    if AWS_PROFILE:
        session_kwargs['profile_name'] = AWS_PROFILE
    
    boto3.setup_default_session(**session_kwargs)
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Modo de prueba
            logger.info("Modo de prueba activado")
            
            # Probar conexiones
            hubspot_ok = test_hubspot_connection()
            athena_ok = test_athena_connection()
            
            if hubspot_ok and athena_ok:
                logger.info("Todas las conexiones funcionan correctamente")
                
                # Probar mapeo de datos
                if test_data_mapping():
                    logger.info("Mapeo de datos funcionando correctamente")
                else:
                    logger.warning("Problemas con el mapeo de datos")
            else:
                logger.error("Algunas conexiones fallaron")
                sys.exit(1)
        elif sys.argv[1].startswith('limit='):
            # Modo con límite específico
            try:
                limit = int(sys.argv[1].split('=')[1])
                logger.info(f"Modo con límite de {limit} registros")
                process_rfm_updates(limit)
                logger.info("Proceso completado exitosamente")
            except ValueError:
                logger.error("Formato de límite inválido. Usa: limit=10")
                sys.exit(1)
        else:
            logger.error("Argumento no reconocido. Usa: test, limit=N o sin argumentos")
            sys.exit(1)
    else:
        # Modo normal - ejecutar actualizaciones
        try:
            process_rfm_updates()
            logger.info("Proceso completado exitosamente")
        except Exception as e:
            logger.error(f"Error en el proceso: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
