from ingestion import extract_data
from transformation import transform_data
from loading import load_to_s3

def run_etl_pipeline():
    """Ejecuta el pipeline ETL completo."""
    print("Iniciando pipeline ETL...")
    
    # 1. Ingesta
    print("\n--- Paso 1: Ingesta ---")
    accounts_df, subscriptions_df, accounts_subscription_df = extract_data()
    
    if accounts_df.empty or subscriptions_df.empty or accounts_subscription_df.empty:
        print("La ingesta de datos falló o no retornó datos. Abortando pipeline.")
        return

    # 2. Transformación
    print("\n--- Paso 2: Transformación ---")
    transformed_df = transform_data(accounts_df, subscriptions_df, accounts_subscription_df)
    
    if transformed_df.empty:
        print("La transformación de datos falló o no generó resultados. Abortando pipeline.")
        return
    
    print("\nDatos transformados (primeras 5 filas):")
    print(transformed_df.head())

    # 3. Carga
    print("\n--- Paso 3: Carga ---")
    success = load_to_s3(transformed_df)
    
    if success:
        print("\nPipeline ETL completado exitosamente.")
    else:
        print("\nPipeline ETL completado con errores en la carga.")

if __name__ == '__main__':
    run_etl_pipeline() 