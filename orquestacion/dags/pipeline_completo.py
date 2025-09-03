"""
DAG orquestador que ejecuta el pipeline completo y el modelo fact_rfm semestralmente.
Se ejecuta el último día de junio y diciembre.
"""
from datetime import datetime
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# Importar utilidades usando la estructura de paquetes correcta
from bruno.common_package.utils import DEFAULT_ARGS

def create_dag():
    """
    Crea y retorna el DAG orquestador semestral.
    """
    with DAG(
        'pipeline_completo',
        default_args=DEFAULT_ARGS,
        description='Pipeline semestral para ejecutar el modelo RFM',
        schedule='0 0 1 1,7 *',  # 1 de enero y julio a las 00:00
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=['datavision', 'rfm', 'semestral'],
        max_active_runs=1
    ) as dag:

        # Trigger para el pipeline suscripciones
        trigger_pipeline_suscripciones = TriggerDagRunOperator(
            task_id='trigger_pipeline_suscripciones',
            trigger_dag_id='pipeline_suscripciones',
            wait_for_completion=True,
            poke_interval=30
        )

        # Trigger para el modelo fact_rfm
        trigger_fact_rfm = TriggerDagRunOperator(
            task_id='trigger_fact_rfm',
            trigger_dag_id='pipeline_fact_rfm',
            wait_for_completion=True,
            poke_interval=30
        )

        # Configurar dependencias: primero el pipeline suscripciones, luego fact_rfm
        trigger_pipeline_suscripciones >> trigger_fact_rfm

        return dag

# Crear el DAG
dag = create_dag()
