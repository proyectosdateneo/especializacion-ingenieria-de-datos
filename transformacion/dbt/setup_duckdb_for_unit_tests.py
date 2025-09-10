#!/usr/bin/env python3
"""
Script para crear las tablas origen en DuckDB para unit tests de dbt.
Basado en el DDL de origen/datos_sinteticos_saas.py
"""

import duckdb

def create_duckdb_tables(conn):
    """Crear las tablas origen en DuckDB con el esquema correcto."""
    print("Creando tablas en DuckDB con esquema 'unit_test'...")
    
    with conn.cursor() as cur:
        # Crear esquema si no existe
        cur.execute("CREATE SCHEMA IF NOT EXISTS unit_test")
        
        # Cambiar al esquema unit_test
        cur.execute("USE unit_test")
        
        # Eliminar tablas existentes si existen
        tables_to_drop = [
            "content_attributes", "contents", "account_premium_features",
            "premium_features", "subscription_payments", "accounts_subscription",
            "subscriptions", "accounts"
        ]
        
        for table in tables_to_drop:
            try:
                cur.execute(f"DROP TABLE IF EXISTS {table}")
            except:
                pass  # Ignorar errores si la tabla no existe
        
        # Crear tablas en el esquema unit_test
        cur.execute("""
            CREATE TABLE accounts (
                account_id INTEGER PRIMARY KEY,
                account_name VARCHAR(255),
                email VARCHAR(255),
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE subscriptions (
                subscription_id INTEGER PRIMARY KEY,
                subscription_name VARCHAR(255),
                max_contents_per_month INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE accounts_subscription (
                account_subscription_id INTEGER PRIMARY KEY,
                account_id INTEGER,
                subscription_id INTEGER,
                start_date DATE,
                end_date DATE
            )
        """)
        
        cur.execute("""
            CREATE TABLE contents (
                content_id INTEGER PRIMARY KEY,
                account_id INTEGER,
                title VARCHAR(255),
                description TEXT,
                content_type VARCHAR(50),
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE content_attributes (
                attribute_id INTEGER PRIMARY KEY,
                content_id INTEGER,
                attribute_name VARCHAR(50),
                string_value VARCHAR(255),
                decimal_value DECIMAL,
                date_value DATE,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE premium_features (
                feature_id INTEGER PRIMARY KEY,
                feature_name VARCHAR(100),
                description TEXT,
                base_price DECIMAL(10,2),
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE subscription_payments (
                payment_id INTEGER PRIMARY KEY,
                account_subscription_id INTEGER,
                payment_date TIMESTAMP,
                amount DECIMAL(10,2),
                payment_method VARCHAR(50),
                billing_cycle VARCHAR(20)
            )
        """)
        
        cur.execute("""
            CREATE TABLE account_premium_features (
                account_feature_id INTEGER PRIMARY KEY,
                account_id INTEGER,
                feature_id INTEGER,
                purchase_date TIMESTAMP,
                amount_paid DECIMAL(10,2)
            )
        """)
    
    print("Tablas creadas exitosamente en el esquema 'unit_test'!")

def main():
    """Función principal."""
    # Conectar a DuckDB usando archivo persistente (como está configurado en profiles.yml)
    conn = duckdb.connect('unit_test.duckdb')
    
    try:
        # Crear tablas
        create_duckdb_tables(conn)
        
        # Verificar que las tablas se crearon correctamente
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'unit_test'")
                tables = cur.fetchall()
                print(f"\nTablas creadas en esquema 'unit_test': {[table[0] for table in tables]}")
            except Exception as e:
                print(f"Error verificando tablas: {e}")
                # Verificar de otra manera
                try:
                    cur.execute("SHOW TABLES")
                    tables_direct = cur.fetchall()
                    print(f"Tablas en esquema actual: {[table[0] for table in tables_direct]}")
                except Exception as e2:
                    print(f"Error en verificación alternativa: {e2}")
        
        print("\n¡DuckDB configurado exitosamente para unit tests!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
