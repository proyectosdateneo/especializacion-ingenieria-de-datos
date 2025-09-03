"""
DAG principal para orquestar el pipeline de DataVision usando ECS.
"""
from datetime import datetime
from airflow import DAG
from bruno.common_package.utils import create_ecs_task, DEFAULT_ARGS, ECS_CLUSTERS, ECS_TASK_DEFINITIONS, ECS_CONTAINERS



def create_dag():
    """
    Crea y retorna el DAG de orquestación usando ECS.
    """
    with DAG(
        'pipeline_suscripciones',
        default_args=DEFAULT_ARGS,
        description='Pipeline de DataVision usando ECS',
        schedule='0 12 * * *', # 9am argentina
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['datavision'],
        max_active_runs=1
    ) as dag:

        # Tarea de ingesta usando ECS
        ingesta_task = create_ecs_task(
            cluster=ECS_CLUSTERS['ingesta'],
            task_definition=ECS_TASK_DEFINITIONS['ingesta'],
            container_name=ECS_CONTAINERS['ingesta'],
            command=['python', '/app/ingesta/ingesta_datavision.py', '--env', 'prod'],
            task_id='ejecutar_ingesta_ecs'
        )

        # Tareas de DBT después de la ingesta
        
        # 0. Test sources
        test_sources = create_ecs_task(
            cluster=ECS_CLUSTERS['transformacion'],
            task_definition=ECS_TASK_DEFINITIONS['transformacion'],
            container_name=ECS_CONTAINERS['dbt'],
            command=['dbt', 'test', '--select', 'source:*'],
            task_id='dbt_test_sources'
        )

        # 1. Modelos de staging
        run_staging = create_ecs_task(
            cluster=ECS_CLUSTERS['transformacion'],
            task_definition=ECS_TASK_DEFINITIONS['transformacion'],
            container_name=ECS_CONTAINERS['dbt'],
            command=['dbt', 'run', '--select', 'staging'],
            task_id='dbt_run_staging'
        )

        # 2. Tests staging
        test_staging = create_ecs_task(
            cluster=ECS_CLUSTERS['transformacion'],
            task_definition=ECS_TASK_DEFINITIONS['transformacion'],
            container_name=ECS_CONTAINERS['dbt'],
            command=['dbt', 'test', '--select', 'staging', '--indirect-selection=empty'],
            # El empty mode excluye las validaciones de integridad referencial de los
            # modelos dimensionales de marts contra los staging.
            # Más información: https://docs.getdbt.com/reference/global-configs/indirect-selection
            task_id='dbt_test_staging'
        )

        # 3. Snapshots
        run_snapshots = create_ecs_task(
            cluster=ECS_CLUSTERS['transformacion'],
            task_definition=ECS_TASK_DEFINITIONS['transformacion'],
            container_name=ECS_CONTAINERS['dbt'],
            command=['dbt', 'snapshot'],
            task_id='dbt_run_snapshots'
        )

        # 4. Modelos marts (excluyendo fact_rfm)
        run_marts = create_ecs_task(
            cluster=ECS_CLUSTERS['transformacion'],
            task_definition=ECS_TASK_DEFINITIONS['transformacion'],
            container_name=ECS_CONTAINERS['dbt'],
            command=['dbt', 'run', '--select', 'marts', '--exclude', 'fact_rfm'],
            task_id='dbt_run_marts'
        )

        # Configurar dependencias
        ingesta_task >> test_sources >> run_staging >> test_staging >> run_snapshots >> run_marts

        return dag

# Crear el DAG
dag = create_dag()
