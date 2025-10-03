# Módulo de orquestación de datos

## ¿Qué problema resuelve para el negocio?

Este módulo automatiza y coordina la ejecución de todo el pipeline de datos, resolviendo los siguientes desafíos:

- **Automatización completa**: elimina la intervención manual en la ejecución de pipelines, reduciendo errores humanos y liberando tiempo del equipo técnico.
- **Confiabilidad operacional**: garantiza que los datos estén disponibles cuando el negocio los necesita, con ejecuciones programadas y monitoreo automático.
- **Escalabilidad de recursos**: ajusta automáticamente la capacidad computacional según la demanda, optimizando costos y rendimiento.
- **Trazabilidad y auditoría**: mantiene un registro completo de cuándo, cómo y qué se ejecutó, facilitando el debugging y cumplimiento regulatorio.
- **Resiliencia**: maneja fallos automáticamente con reintentos, alertas y recuperación de errores sin pérdida de datos.

## ¿Cómo funciona?

**Objetivo del módulo**: orquestar de manera inteligente y escalable todos los componentes del pipeline de datos, desde la ingesta hasta la generación de reportes finales.

**Arquitectura de orquestación**: utiliza **Apache Airflow** como orquestador principal y **AWS ECS Fargate** como motor de ejecución, creando una solución serverless y altamente escalable.

### Conceptos de orquestación implementados

Estos conceptos son fundamentales en la orquestación de pipelines de datos a escala:

- **DAGs (Directed Acyclic Graphs)**: estructuras que definen el flujo de trabajo como un grafo de tareas con dependencias. Permiten visualizar y gestionar pipelines complejos de manera intuitiva.
- **Task dependencies**: definición clara de qué tareas deben ejecutarse antes que otras. Evita condiciones de carrera y garantiza la integridad de los datos.
- **Error handling y retries**: manejo robusto de fallos con reintentos exponenciales y alertas automáticas. Crítico para mantener la confiabilidad en entornos de producción.
- **Monitoring y observabilidad**: seguimiento en tiempo real del estado de ejecución, métricas de rendimiento y alertas proactivas.

### Flujo de orquestación

El sistema ejecuta tres tipos de pipelines:

1. **Pipeline diario**: ejecuta ingesta y transformaciones básicas todos los días a las 9 AM (Argentina).
2. **Pipeline semestral**: ejecuta el modelo RFM completo los días 1 de enero y julio.
3. **Pipeline bajo demanda**: permite ejecutar modelos específicos como fact_rfm con parámetros personalizados.

## Uso técnico

### Arquitectura de componentes

La orquestación funciona mediante la interacción de tres componentes principales:

#### ECR (Elastic Container Registry)
**Función**: almacena las imágenes Docker que contienen el código de los módulos de ingesta y transformación.

**Interacción**: cuando se construyen las imágenes desde los Dockerfiles de los módulos `ingesta/` y `transformacion/`, estas se suben a ECR con tags específicos (ej: `datavision-ingesta:latest`).

#### ECS Fargate
**Función**: motor de ejecución serverless que ejecuta los contenedores Docker sin necesidad de gestionar servidores.

**Conceptos clave**:
- **Cluster**: agrupación lógica de recursos computacionales (ej: `datavision-ingesta-cluster`).
- **Task Definition**: plantilla que define qué contenedor ejecutar, cuántos recursos asignar y qué variables de entorno usar.
- **Task**: instancia ejecutándose de una Task Definition específica.

**Interacción**: ECS lee las imágenes desde ECR y las ejecuta en contenedores Fargate cuando se solicita.

#### Apache Airflow
**Función**: orquestador que programa, coordina y monitorea la ejecución de tareas.

**Conceptos clave**:
- **DAG**: grafo de tareas con dependencias que define el flujo de trabajo.
- **Task**: unidad individual de trabajo dentro de un DAG.
- **Operator**: plantilla que define cómo ejecutar una tarea específica (ej: `EcsRunTaskOperator`).

**Interacción**: Airflow invoca a ECS para ejecutar las tareas, pasando los comandos y parámetros necesarios.

### Flujo de ejecución

1. **Airflow programa la ejecución** según el cron definido en el DAG.
2. **Airflow crea una Task en ECS** usando el `EcsRunTaskOperator` con la Task Definition correspondiente.
3. **ECS descarga la imagen** desde ECR y la ejecuta en un contenedor Fargate.
4. **El contenedor ejecuta el código** (ingesta o transformación) con los parámetros proporcionados.
5. **Airflow monitorea el estado** de la ejecución y maneja errores o reintentos.

### Buenas prácticas implementadas

#### Separación de responsabilidades
**Por qué es importante**: evita acoplar la lógica de negocio con la orquestación, facilitando el mantenimiento y testing.

**Implementación**: el código de ingesta y transformación vive en sus respectivos módulos, no dentro de Airflow. Airflow solo orquesta la ejecución.

```python
# ❌ Mala práctica: lógica de negocio en Airflow
def extract_data():
    # código de extracción aquí
    pass

# ✅ Buena práctica: Airflow solo orquesta
ingesta_task = create_ecs_task(
    command=['python', '/app/ingesta/ingesta_datavision.py', '--env', 'prod']
)
```

#### Reutilización de código
**Por qué es importante**: reduce duplicación y facilita el mantenimiento de configuraciones comunes.

**Implementación**: utilidades centralizadas en `common_package` que crean operadores ECS consistentes.

### Monitoreo y alertas

#### Sistema de retries
**Función**: maneja fallos temporales automáticamente sin intervención manual.

**Configuración**:
- **Retries**: número de intentos antes de marcar como fallido.
- **Retry delay**: tiempo de espera entre reintentos.
- **Exponential backoff**: incrementa el delay exponencialmente para evitar sobrecargar sistemas.

#### Notificaciones automáticas
**Función**: alerta al equipo cuando ocurren fallos o se requieren intervenciones.

**Tipos de alertas**:
- **Email on failure**: notifica cuando una tarea falla definitivamente.
- **Email on retry**: notifica cuando una tarea está reintentando.
- **Execution timeout**: cancela tareas que exceden el tiempo límite.

### Configuración de pipelines

#### Pipeline diario
```python
# Ejecuta ingesta y transformaciones básicas diariamente
schedule='0 12 * * *'  # 9 AM Argentina
```

#### Pipeline semestral
```python
# Ejecuta el modelo RFM completo dos veces al año
schedule='0 0 1 1,7 *'  # 1 de enero y julio
```

#### Pipeline bajo demanda
```python
# Permite ejecutar modelos específicos con parámetros personalizados
schedule=None  # Solo ejecución manual o por trigger
```

### Estructura del módulo

- `dags/`: directorio con todos los DAGs de Airflow.
  - `pipeline_suscripciones.py`: pipeline diario de ingesta y transformación.
  - `pipeline_completo.py`: orquestador semestral que ejecuta el pipeline completo.
  - `pipeline_fact_rfm.py`: pipeline específico para el modelo RFM.
- `common_package/utils/`: utilidades compartidas.
  - `config.py`: configuración común de clusters, task definitions y variables de entorno.
  - `ecs_utils.py`: funciones helper para crear operadores ECS.

### Buenas prácticas implementadas

- **Separación de responsabilidades**: cada DAG tiene un propósito específico y bien definido.
- **Reutilización de código**: utilidades comunes centralizadas en `common_package`.
- **Configuración externa**: todos los parámetros de infraestructura en archivos de configuración.
- **Manejo de errores**: retries exponenciales y timeouts apropiados para cada tipo de tarea.
- **Observabilidad**: logging detallado y notificaciones automáticas en caso de fallos.
- **Escalabilidad**: uso de Fargate para escalado automático según la demanda.
- **Seguridad**: ejecución en VPC privada con acceso controlado a recursos AWS.
