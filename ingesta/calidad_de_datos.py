import psycopg2
import duckdb
import os
from typing import Dict, List, Optional
from dlt.common.pipeline import get_dlt_pipelines_dir
import tomllib
import yaml
from pyathena import connect
from datetime import datetime, timedelta

def get_db_connection(env: str = 'local'):
    """
    Obtiene conexión a la base de datos origen según el entorno.
    
    Args:
        env (str): Entorno de ejecución ('local', 'dev' o 'prod')
        
    Returns:
        psycopg2.connection: Conexión a PostgreSQL
    """
    # Siempre usar secrets.toml
    secrets_file = '.dlt/secrets.toml'
    
    with open(secrets_file, 'rb') as f:
        config = tomllib.load(f)
    
    db_config = config['sources']['sql_database']['credentials']
    
    return psycopg2.connect(
        host=db_config['host'],
        database=db_config['database'],
        user=db_config['username'],
        password=db_config['password'],
        port=db_config['port']
    )

def get_destination_connection(env: str = 'local'):
    """
    Obtiene conexión al destino según el entorno.
    
    Args:
        env (str): Entorno de ejecución ('local', 'dev' o 'prod')
        
    Returns:
        Conexión al destino (duckdb para local, pyathena para dev/prod)
    """
    if env == 'local':
        pipelines_dir = os.path.join(get_dlt_pipelines_dir(), env)
        db_path = os.path.join(pipelines_dir, 'datavision.duckdb')
        return duckdb.connect(db_path)
    else:
        # Para dev/prod usar pyathena
        secrets_file = '.dlt/secrets.toml'
        with open(secrets_file, 'rb') as f:
            config = tomllib.load(f)
        
        athena_config = config['destination']['athena']
        athena_creds = config['destination']['athena']['credentials']
        
        return connect(
            aws_access_key_id=athena_creds['aws_access_key_id'],
            aws_secret_access_key=athena_creds['aws_secret_access_key'],
            region_name=athena_creds['region_name'],
            s3_staging_dir=athena_config['query_result_bucket'],
            work_group=athena_config['athena_work_group']
        )

def get_dataset_name(env: str) -> str:
    """
    Obtiene el nombre del dataset según el entorno.
    
    Args:
        env (str): Entorno de ejecución ('local', 'dev' o 'prod')
        
    Returns:
        str: Nombre del dataset
    """
    if env == 'local':
        return 'raw_datavision_local'
    elif env == 'dev':
        return 'raw_datavision_dev'
    else:  # prod
        return 'raw_datavision_prod'

def execute_destination_query(env: str, dest_conn, query: str):
    """
    Ejecuta una consulta en el destino según el entorno.
    
    Args:
        env (str): Entorno de ejecución
        dest_conn: Conexión al destino
        query (str): Consulta SQL a ejecutar
        
    Returns:
        Resultado de la consulta
    """
    if env == 'local':
        return dest_conn.execute(query).fetchone()
    else:
        # Para dev/prod usar pyathena
        with dest_conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()

def get_primary_keys_from_schema() -> Dict[str, str]:
    """
    Lee las claves primarias de las tablas desde el esquema YAML.
    
    Returns:
        Dict con tabla -> clave primaria
    """
    schema_file = 'schemas/import/sql_database.schema.yaml'
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = yaml.safe_load(f)
    
    primary_keys = {}
    
    for table_name, table_info in schema['tables'].items():
        if 'columns' in table_info:
            for column_name, column_info in table_info['columns'].items():
                if column_info.get('primary_key', False):
                    primary_keys[table_name] = column_name
                    break
    
    return primary_keys

def validar_conteo_tablas(
    env: str = 'local',
    tables: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """
    Valida el conteo de registros entre origen y destino.
    
    Args:
        env (str): Entorno de ejecución ('local', 'dev' o 'prod')
        tables (List[str]): Lista de tablas a validar (las que se cargaron)
        
    Returns:
        Dict con resultados de validación por tabla
    """
    if tables is None:
        print("⚠️ No se especificaron tablas para validar")
        return {}
    
    results = {}
    
    print("🔍 Validando conteo de registros...")
    
    # Conexión a origen
    source_conn = get_db_connection(env)
    
    # Conexión a destino
    dest_conn = get_destination_connection(env)
    
    # Determinar dataset name según el entorno
    dataset_name = get_dataset_name(env)
    
    try:
        for table in tables:
            try:
                # Conteo en origen
                with source_conn.cursor() as cursor:
                    cursor.execute(f""" 
                        -- COMPLETAR AQUÍ: query para contar registros en origen
                    """)
                    source_count = cursor.fetchone()[0]
                
                # Conteo en destino
                query = f"-- COMPLETAR AQUÍ: query para contar registros en destino"
                result = execute_destination_query(env, dest_conn, query)
                dest_count = result[0]
                
                difference = source_count - dest_count
                status = 'OK' if source_count == dest_count else 'WARNING'
                
                results[table] = {
                    'source_count': source_count,
                    'destination_count': dest_count,
                    'difference': difference,
                    'status': status
                }
                
                print(f"  📊 {table}: Origen={source_count}, Destino={dest_count}")
                
            except Exception as e:
                results[table] = {
                    'source_count': 0,
                    'destination_count': 0,
                    'difference': 0,
                    'status': 'ERROR',
                    'error': str(e)
                }
                print(f"  ❌ Error validando {table}: {e}")
    
    finally:
        source_conn.close()
        if dest_conn:
            dest_conn.close()
    
    return results

def validar_freshness_tablas(
    env: str = 'local',
    tables: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """
    Valida la frescura de los datos basándose en updated_at (48 horas fijo).
    
    Args:
        env (str): Entorno de ejecución ('local', 'dev' o 'prod')
        tables (List[str]): Lista de tablas a validar
        
    Returns:
        Dict con resultados de validación de frescura
    """
    if tables is None:
        print("⚠️ No se especificaron tablas para validar")
        return {}
    
    results = {}
    max_hours = 48  # Fijo en 48 horas
    cutoff_time = datetime.now() - timedelta(hours=max_hours)
    
    print(f"⏰ Validando frescura de datos (máximo {max_hours} horas)...")
    
    # Conexión a origen para verificar esquema
    source_conn = get_db_connection(env)
    
    # Conexión a destino
    dest_conn = get_destination_connection(env)
    
    # Determinar dataset name según el entorno
    dataset_name = get_dataset_name(env)
    
    try:
        for table in tables:
            try:
                # Verificar si la tabla tiene updated_at consultando el esquema
                has_updated_at = False
                with source_conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' AND column_name = 'updated_at'
                    """)
                    has_updated_at = cursor.fetchone() is not None
                
                if not has_updated_at:
                    results[table] = {
                        'status': 'SKIP',
                        'message': 'Tabla no tiene columna updated_at'
                    }
                    print(f"  ⏭️ {table}: No tiene columna updated_at")
                    continue
                
                # Consultar el registro más reciente de la tabla
                query = f"""
                -- COMPLETAR AQUÍ: query para obtener la fecha más reciente en updated_at
                """
                
                result = execute_destination_query(env, dest_conn, query)
                newest_update = result[0]
                
                # Verificar si el más reciente está dentro del límite de 48 horas
                if newest_update is None:
                    status = 'WARNING'
                    message = 'No hay registros con updated_at'
                elif newest_update > datetime.now():
                    status = 'WARNING'
                    message = f'Datos con fechas futuras (más reciente: {newest_update})'
                elif newest_update > cutoff_time:
                    status = 'OK'
                    message = f'Datos actualizados (más reciente: {newest_update})'
                else:
                    status = 'WARNING'
                    message = f'Datos desactualizados (más reciente: {newest_update})'
                
                results[table] = {
                    'newest_update': newest_update,
                    'cutoff_time': cutoff_time,
                    'status': status,
                    'message': message
                }
                
                print(f"  📅 {table}: {message}")
                    
            except Exception as e:
                results[table] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                print(f"  ❌ Error validando frescura de {table}: {e}")
    
    finally:
        source_conn.close()
        if dest_conn:
            dest_conn.close()
    
    return results

def validar_duplicados_tablas(
    env: str = 'local',
    tables: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """
    Valida duplicados por clave primaria en las tablas de destino.
    
    Nota: Esta validación solo se ejecuta contra el destino (DuckDB/Athena) 
    ya que el origen (PostgreSQL) tiene constraints que previenen duplicados.
    
    Args:
        env (str): Entorno de ejecución ('local', 'dev' o 'prod')
        tables (List[str]): Lista de tablas a validar
        
    Returns:
        Dict con resultados de validación de duplicados por tabla
    """
    if tables is None:
        print("⚠️ No se especificaron tablas para validar")
        return {}
    
    results = {}
    
    print("🔍 Validando duplicados por clave primaria...")
    
    # Obtener claves primarias del esquema
    primary_keys = get_primary_keys_from_schema()
    
    # Conexión a destino
    dest_conn = get_destination_connection(env)
    
    # Determinar dataset name según el entorno
    dataset_name = get_dataset_name(env)
    
    try:
        for table in tables:
            try:
                # Verificar si la tabla tiene clave primaria definida
                if table not in primary_keys:
                    results[table] = {
                        'status': 'SKIP',
                        'message': f'No se encontró clave primaria para {table} en el esquema'
                    }
                    print(f"  ⏭️ {table}: No se encontró clave primaria en el esquema")
                    continue
                
                pk_column = primary_keys[table]
                
                # Consultar duplicados por clave primaria
                query = f"""
                -- COMPLETAR AQUÍ: query para detectar duplicados por clave primaria
                """
                
                result = execute_destination_query(env, dest_conn, query)
                
                if result is None or len(result) == 0:
                    # No hay duplicados
                    results[table] = {
                        'duplicate_count': 0,
                        'duplicate_ids': [],
                        'status': 'OK'
                    }
                    print(f"  ✅ {table}: Sin duplicados por {pk_column}")
                else:
                    # Hay duplicados
                    duplicate_count = len(result)
                    duplicate_ids = [row[0] for row in result]
                    
                    results[table] = {
                        'duplicate_count': duplicate_count,
                        'duplicate_ids': duplicate_ids,
                        'status': 'WARNING'
                    }
                    print(f"  ⚠️ {table}: {duplicate_count} duplicados por {pk_column}")
                    
            except Exception as e:
                results[table] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                print(f"  ❌ Error validando duplicados en {table}: {e}")
    
    finally:
        if dest_conn:
            dest_conn.close()
    
    return results

def validar_integridad_referencial_tablas(
    env: str = 'local',
    tables: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """
    Valida la integridad referencial en las tablas de destino.
    
    Nota: Esta validación solo se ejecuta contra el destino (DuckDB/Athena) 
    ya que el origen (PostgreSQL) tiene constraints que previenen violaciones de integridad.
    
    Args:
        env (str): Entorno de ejecución ('local', 'dev' o 'prod')
        tables (List[str]): Lista de tablas a validar
        
    Returns:
        Dict con resultados de validación de integridad referencial por tabla
    """
    if tables is None:
        print("⚠️ No se especificaron tablas para validar")
        return {}
    
    # Configuración manual de relaciones FK -> tabla_padre
    FK_RELATIONS = {
        "contents": {
            "account_id": "accounts"
        },
        "content_attributes": {
            "content_id": "contents"
        },
        "accounts_subscription": {
            "account_id": "accounts",
            "subscription_id": "subscriptions"
        }
    }
    
    results = {}
    
    print("🔗 Validando integridad referencial...")
    
    # Conexión a destino
    dest_conn = get_destination_connection(env)
    
    # Determinar dataset name según el entorno
    dataset_name = get_dataset_name(env)
    
    try:
        for table in tables:
            if table not in FK_RELATIONS:
                results[table] = {
                    'status': 'SKIP',
                    'message': f'No hay relaciones de integridad definidas para {table}'
                }
                print(f"  ⏭️ {table}: No hay relaciones definidas")
                continue
            
            table_results = {}
            
            for fk_column, parent_table in FK_RELATIONS[table].items():
                try:
                    # Query para detectar registros huérfanos
                    query = f"""
                    -- COMPLETAR AQUÍ: query para encontrar registros huérfanos
                    """
                    
                    result = execute_destination_query(env, dest_conn, query)
                    orphan_count = result[0]
                    
                    status = 'OK' if orphan_count == 0 else 'WARNING'
                    
                    table_results[fk_column] = {
                        'parent_table': parent_table,
                        'orphan_count': orphan_count,
                        'status': status
                    }
                    
                    print(f"  🔗 {table}.{fk_column} -> {parent_table}: {orphan_count} huérfanos")
                    
                except Exception as e:
                    table_results[fk_column] = {
                        'status': 'ERROR',
                        'error': str(e)
                    }
                    print(f"  ❌ Error validando integridad {table}.{fk_column}: {e}")
            
            results[table] = table_results
    
    finally:
        if dest_conn:
            dest_conn.close()
    
    return results

def mostrar_resumen_conteo(results: Dict[str, Dict]):
    """
    Muestra un resumen de los resultados de conteo.
    
    Args:
        results (Dict[str, Dict]): Resultados de validación
    """
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE CONTEOS")
    print("=" * 50)
    
    for table, result in results.items():
        status_icon = "✅" if result['status'] == 'OK' else "⚠️" if result['status'] == 'WARNING' else "❌"
        print(f"  {status_icon} {table}: {result['source_count']} → {result['destination_count']} ({result['difference']:+d})")
    
    print("=" * 50)

def mostrar_resumen_duplicados(results: Dict[str, Dict]):
    """
    Muestra un resumen de los resultados de duplicados.
    
    Args:
        results (Dict[str, Dict]): Resultados de validación
    """
    print("\n" + "=" * 50)
    print("🔍 RESUMEN DE DUPLICADOS")
    print("=" * 50)
    
    for table, result in results.items():
        if result['status'] == 'OK':
            print(f"  ✅ {table}: Sin duplicados")
        elif result['status'] == 'WARNING':
            print(f"  ⚠️ {table}: {result['duplicate_count']} duplicados encontrados")
        elif result['status'] == 'SKIP':
            print(f"  ⏭️ {table}: {result['message']}")
        else:
            print(f"  ❌ {table}: Error - {result.get('error', 'Desconocido')}")
    
    print("=" * 50)

def mostrar_resumen_integridad_referencial(results: Dict[str, Dict]):
    """
    Muestra un resumen de los resultados de integridad referencial.
    
    Args:
        results (Dict[str, Dict]): Resultados de validación
    """
    print("\n" + "=" * 50)
    print("🔗 RESUMEN DE INTEGRIDAD REFERENCIAL")
    print("=" * 50)
    
    for table, table_results in results.items():
        if isinstance(table_results, dict) and 'status' in table_results:
            # Caso de tabla sin relaciones definidas
            print(f"  ⏭️ {table}: {table_results['message']}")
        else:
            # Caso de tabla con relaciones de integridad
            for fk, fk_result in table_results.items():
                if fk_result['status'] == 'OK':
                    print(f"  ✅ {table}.{fk} -> {fk_result['parent_table']}: Sin huérfanos")
                elif fk_result['status'] == 'WARNING':
                    print(f"  ⚠️ {table}.{fk} -> {fk_result['parent_table']}: {fk_result['orphan_count']} huérfanos")
                else:
                    print(f"  ❌ {table}.{fk}: Error - {fk_result.get('error', 'Desconocido')}")
    
    print("=" * 50)

def mostrar_resumen_freshness(results: Dict[str, Dict]):
    """
    Muestra un resumen de los resultados de frescura.
    
    Args:
        results (Dict[str, Dict]): Resultados de validación
    """
    print("\n" + "=" * 50)
    print("⏰ RESUMEN DE FRESCURA")
    print("=" * 50)
    
    for table, result in results.items():
        if result['status'] == 'OK':
            print(f"  ✅ {table}: {result['message']}")
        elif result['status'] == 'WARNING':
            print(f"  ⚠️ {table}: {result['message']}")
        elif result['status'] == 'SKIP':
            print(f"  ⏭️ {table}: {result['message']}")
        else:
            print(f"  ❌ {table}: Error - {result.get('error', 'Desconocido')}")
    
    print("=" * 50) 