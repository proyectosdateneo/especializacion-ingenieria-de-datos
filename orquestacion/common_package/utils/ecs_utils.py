"""
Utilidades para operadores ECS en Airflow.
"""
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator


def create_ecs_task(cluster, task_definition, container_name, command, task_id):
    """
    Crea una tarea ECS con configuración común.
    
    Args:
        cluster (str): Nombre del cluster ECS
        task_definition (str): Definición de la tarea ECS
        container_name (str): Nombre del contenedor
        command (list): Comando a ejecutar
        task_id (str): ID de la tarea en Airflow
    
    Returns:
        EcsRunTaskOperator: Operador ECS configurado
    """
    return EcsRunTaskOperator(
        task_id=task_id,
        cluster=cluster,
        task_definition=task_definition,
        launch_type='FARGATE',
        network_configuration={
            'awsvpcConfiguration': {
                'subnets': ['subnet-012ff4f99d9ed4a34'],
                'assignPublicIp': 'ENABLED'
            }
        },
        region_name='us-west-2',
        aws_conn_id='bruno',
        wait_for_completion=True,
        do_xcom_push=True,
        overrides={
            'containerOverrides': [
                {
                    'name': container_name,
                    'command': command
                }
            ]
        }
    )
