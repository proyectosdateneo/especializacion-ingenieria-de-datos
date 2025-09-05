"""
DAG específico para ejecutar el modelo fact_rfm con fecha personalizada.
"""
from datetime import datetime
from airflow import DAG

# Importar utilidades usando la estructura de paquetes correcta
from bruno.common_package.utils import (
    create_ecs_task, 
    DEFAULT_ARGS, 
    ECS_CLUSTERS, 
    ECS_TASK_DEFINITIONS, 
    ECS_CONTAINERS,
    COMMON_ENVIRONMENT_VARS
)



def create_dag():
    """
    Crea y retorna el DAG para ejecutar fact_rfm con fecha personalizada.
    """
    with DAG(
        'pipeline_fact_rfm',
        default_args=DEFAULT_ARGS,
        description='Pipeline específico para modelo fact_rfm con fecha personalizada',
        schedule=None,  # Se ejecuta manualmente o por trigger
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['datavision', 'rfm'],
        max_active_runs=1
    ) as dag:

        # Tarea para ejecutar fact_rfm con fecha personalizada
        run_fact_rfm = create_ecs_task(
            cluster=ECS_CLUSTERS['transformacion'],
            task_definition=ECS_TASK_DEFINITIONS['transformacion'],
            container_name=ECS_CONTAINERS['dbt'],
            command=[
                'dbt', 
                'run', 
                '--select', 
                'fact_rfm', 
                '--vars', 
                'fecha_rfm: {{ ds }}'  # Usa la fecha de ejecución del DAG
            ],
            task_id='dbt_run_fact_rfm',
            environment=COMMON_ENVIRONMENT_VARS
        )

        return dag

# Crear el DAG
dag = create_dag()
