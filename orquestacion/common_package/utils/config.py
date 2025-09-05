"""
Configuración común para DAGs de Airflow.
"""
from datetime import timedelta

# Configuración común de argumentos por defecto
DEFAULT_ARGS = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': True,
    'email': ['bruno@dateneo.com'],
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(hours=2)
}

# Configuración de clusters ECS
ECS_CLUSTERS = {
    'ingesta': 'datavision-ingesta-cluster',
    'transformacion': 'datavision-transformacion-cluster'
}

# Configuración de task definitions ECS
ECS_TASK_DEFINITIONS = {
    'ingesta': 'datavision-ingesta-task',
    'transformacion': 'datavision-transformacion-task'
}

# Configuración de contenedores ECS
ECS_CONTAINERS = {
    'ingesta': 'ingesta-container',
    'dbt': 'dbt-container'
}

# Variables de entorno comunes para las tareas ECS
COMMON_ENVIRONMENT_VARS = [
    {
        'name': 'BUCKET_STAGING',
        'value': 's3://dateneo-staging-us-west-2-375612485931'
    },
    {
        'name': 'BUCKET_ANALYTICS',
        'value': 's3://dateneo-analytics-us-west-2-375612485931'
    }
]