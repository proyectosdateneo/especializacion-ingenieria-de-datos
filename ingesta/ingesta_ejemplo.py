import dlt
from dlt.sources.sql_database import sql_database

def ingesta_ejemplo():
    """
    Ejemplo simplificado de ingesta con DLT.
    Demuestra carga full refresh vs incremental.
    """
    
    # 1. Configurar el pipeline
    pipeline = dlt.pipeline(
        pipeline_name='ejemplo_simple',
        destination='duckdb',  # Base de datos local para el ejemplo
        dataset_name='datos_ejemplo',
        modo_desarrollo=True # cada vez que se ejecuta el pipeline, se resetea su estado y carga datos a un nuevo dataset, ver https://dlthub.com/docs/general-usage/pipeline#do-experiments-with-dev-mode
    )
    
    # 2. Conectar a la base de datos origen
    db = sql_database()
    
    # 3. Configurar tabla con carga FULL REFRESH
    # Esta tabla se recarga completamente cada vez
    tabla_full = db.with_resources("subscriptions")
    tabla_full.subscriptions.apply_hints(
        write_disposition="replace"  # Reemplaza toda la tabla
    )
    
    # 4. Configurar tabla con carga INCREMENTAL
    # Esta tabla solo carga registros nuevos/modificados
    tabla_incremental = db.with_resources("accounts")
    tabla_incremental.accounts.apply_hints(
        write_disposition="merge",  # Fusiona con datos existentes
        incremental=dlt.sources.incremental("updated_at")  # Solo registros nuevos/modificados
    )
    
    # 5. Ejecutar el pipeline
    info = pipeline.run([tabla_full, tabla_incremental])
    
    # 6. Mostrar resultados
    print("✅ Ingesta completada!")
    print(f"📊 Información de la ejecución: {info}")

if __name__ == "__main__":
    ingesta_ejemplo() 