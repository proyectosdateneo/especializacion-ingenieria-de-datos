import pandas as pd
import sqlite3

def transform_data(accounts_df, subscriptions_df, accounts_subscription_df):
    """Transforma los datos usando SQL en una BD SQLite en memoria."""
    if accounts_df.empty or subscriptions_df.empty or accounts_subscription_df.empty:
        print("Uno o más DataFrames de entrada están vacíos. No se puede transformar.")
        return pd.DataFrame()

    # Conectar a una base de datos SQLite en memoria
    conn = sqlite3.connect(':memory:')
    
    # Convertir todas las columnas de fecha a strings ISO-8601
    for df_name, df in [('accounts', accounts_df), ('subscriptions', subscriptions_df), ('accounts_subscription', accounts_subscription_df)]:
        print(f"\nProcesando DataFrame: {df_name}")
        for col in df.select_dtypes(include=['datetime64']).columns:
            
            # Convertir fechas a string porque sqllite no soporta date ni timestamp, manteniendo los valores nulos como None
            df[col] = df[col].astype(str).replace({'NaT': None})
    
    try:
        accounts_df.to_sql('accounts', conn, index=False, if_exists='replace')
        subscriptions_df.to_sql('subscriptions', conn, index=False, if_exists='replace')
        accounts_subscription_df.to_sql('accounts_subscription', conn, index=False, if_exists='replace')
        print("DataFrames cargados en SQLite en memoria.")

        query = """
        WITH AccountSubscriptionHistory AS (
            -- Seleccionar el historial de suscripciones para cada cuenta
            SELECT
                a.account_id,
                a.account_name,
                a.created_at AS account_created_date,
                acs.start_date,
                acs.end_date,
                s.subscription_name,
                LAG(acs.start_date) OVER (PARTITION BY a.account_id ORDER BY JULIANDAY(acs.start_date), acs.account_subscription_id) as prev_start_date,
                LAG(s.subscription_name) OVER (PARTITION BY a.account_id ORDER BY JULIANDAY(acs.start_date), acs.account_subscription_id) as prev_subscription_name,
                ROW_NUMBER() OVER (PARTITION BY a.account_id ORDER BY JULIANDAY(acs.start_date) DESC, acs.account_subscription_id DESC) as rn
            FROM accounts a
            JOIN accounts_subscription acs ON a.account_id = acs.account_id
            JOIN subscriptions s ON acs.subscription_id = s.subscription_id
        )
        SELECT
            account_id,
            account_name,
            account_created_date,
            start_date AS enterprise_start_date,
            CASE
                WHEN prev_start_date IS NOT NULL THEN CAST( (JULIANDAY(start_date) - JULIANDAY(prev_start_date)) AS INTEGER)
                ELSE NULL
            END AS days_between_prev_and_enterprise,
            CASE
                WHEN prev_subscription_name IS NOT NULL AND prev_subscription_name <> 'Empresarial' THEN 1
                ELSE 0
            END AS is_upgrade_flag
        FROM AccountSubscriptionHistory
        WHERE rn = 1
        AND subscription_name = 'Empresarial';
        """

        print("Ejecutando consulta de transformación SQL...")
        transformed_df = pd.read_sql_query(query, conn)
        print(f"Transformación completada. {len(transformed_df)} filas generadas.")
        
        return transformed_df

    except Exception as e:
        print(f"Error durante la transformación de datos: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            print("Conexión a SQLite cerrada.")

if __name__ == '__main__':
    # Para probar el módulo directamente
    print("Ejecutando módulo de transformación con datos de ejemplo...")
    sample_accounts = pd.DataFrame({
        'account_id': [1, 2, 3, 4],
        'account_name': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa D'],
        'email': ['a@test.com', 'b@test.com', 'c@test.com', 'd@test.com'],
        'created_at': ['2023-01-01', '2022-06-15', '2023-03-10', '2021-11-20']
    })
    sample_subscriptions = pd.DataFrame({
        'subscription_id': [1, 2, 3],
        'subscription_name': ['Gratuita', 'Premium', 'Empresarial'],
        'max_contents_per_month': [5,50,500],
        'created_at': ['2022-01-01','2022-01-01','2022-01-01'],
        'updated_at': ['2022-01-01','2022-01-01','2022-01-01']
    })
    sample_accounts_subscription = pd.DataFrame({
        'account_subscription_id': [101, 102, 103, 104, 105, 106, 107],
        'account_id': [1, 1, 2, 3, 3, 4, 4],
        'subscription_id': [1, 3, 2, 2, 3, 1, 3],
        'start_date': ['2023-01-01', '2023-06-01', '2022-06-15', '2023-03-10', '2023-08-01', '2021-11-20', '2023-01-01'],
        'end_date': ['2023-05-31', None, None, '2023-07-31', None, '2022-12-31', None]
    })

    result_df = transform_data(sample_accounts, sample_subscriptions, sample_accounts_subscription)
    if not result_df.empty:
        print("\nResultado de la transformación (primeras 5 filas):")
        print(result_df.head()) 