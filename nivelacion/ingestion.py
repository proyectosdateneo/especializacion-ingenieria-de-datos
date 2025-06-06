import psycopg2
import pandas as pd
import config_etl

def extract_data():
    """Extrae datos de las tablas accounts, subscriptions y accounts_subscription."""
    db_config = config_etl.load_db_config()
    conn = None
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            dbname=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        print("Conexión a PostgreSQL exitosa.")

        accounts_df = pd.read_sql("SELECT account_id, account_name, email, created_at, updated_at FROM accounts", conn)
        subscriptions_df = pd.read_sql("SELECT subscription_id, subscription_name, max_contents_per_month, created_at, updated_at FROM subscriptions", conn)
        accounts_subscription_df = pd.read_sql("SELECT account_subscription_id, account_id, subscription_id, start_date, end_date FROM accounts_subscription", conn)

        print(f"Extraídas {len(accounts_df)} filas de accounts.")
        print(f"Extraídas {len(subscriptions_df)} filas de subscriptions.")
        print(f"Extraídas {len(accounts_subscription_df)} filas de accounts_subscription.")

        return accounts_df, subscriptions_df, accounts_subscription_df

    except (Exception, psycopg2.Error) as error:
        print(f"Error al conectar o extraer datos de PostgreSQL: {error}")
        # Podrías querer re-lanzar el error o manejarlo de forma más específica
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame() # Retornar DataFrames vacíos en caso de error
    finally:
        if conn:
            conn.close()
            print("Conexión a PostgreSQL cerrada.")

if __name__ == '__main__':
    # Esto es para probar el módulo directamente

    print("Ejecutando módulo de ingestión...")
    df_accounts, df_subscriptions, df_accounts_subscription = extract_data()
    if not df_accounts.empty:
        print("\nPrimeras 5 filas de Accounts:")
        print(df_accounts.head())
        print("\nPrimeras 5 filas de Subscriptions:")
        print(df_subscriptions.head())
        print("\nPrimeras 5 filas de Accounts_Subscription:")
        print(df_accounts_subscription.head()) 