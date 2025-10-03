# Módulo de transformación de datos

## ¿Qué problema resuelve para el negocio?

Este módulo transforma los datos crudos (capa raw) en información estructurada y analizable, resolviendo los siguientes desafíos críticos del negocio:

- **Gobierno de datos**: evita la proliferación de tablas sin relación y métricas duplicadas mediante un modelo dimensional bien definido.
- **Consistencia analítica**: establece definiciones únicas y estandarizadas para métricas de negocio (RFM, churn, segmentación).
- **Histórico de cambios**: mantiene el historial de cambios en entidades clave (cuentas, suscripciones, contenidos) para análisis temporal.
- **Escalabilidad analítica**: proporciona una base sólida para análisis complejos sin impactar el rendimiento del sistema transaccional.
- **Trazabilidad**: permite rastrear el origen y evolución de cada métrica desde los datos fuente.

## ¿Cómo funciona?

**Prerequisito fundamental**: este módulo requiere un modelo de datos dimensional previamente diseñado. Sin un modelo bien definido, la transformación se convierte en una colección de tablas sin relación, generando problemas de desgobierno como métricas duplicadas y definiciones inconsistentes.

**Arquitectura de tres capas**: este módulo construye las capas **staging** y **analytics** de la arquitectura lakehouse:

### Capa Staging
- **Normalización**: estandariza nombres de columnas, tipos de datos y formatos.
- **Validación**: aplica tests de integridad referencial y calidad de datos.
- **Snapshots**: captura el historial de cambios para entidades críticas (SCD Tipo 2).

### Capa Analytics (Marts)
- **Modelo dimensional**: implementa dimensiones (cuentas, suscripciones, contenidos) y hechos (RFM, suscripciones).
- **Métricas de negocio**: calcula segmentación RFM, análisis de churn, y métricas de suscripción.
- **Histórico temporal**: mantiene versiones históricas de entidades para análisis temporal.

**Herramienta especializada**: utiliza **dbt** (Data Build Tool), una herramienta open source que:
- Permite versionado y testing de transformaciones SQL.
- Automatiza la dependencia entre modelos.
- Facilita la documentación y testing de calidad de datos.
- Soporta múltiples motores de datos (DuckDB, AWS Athena, etc.).

## Estructura del modelo dimensional

### Dimensiones (SCD Tipo 2)
- **dim_cuentas**: cuentas con historial de cambios y segmentación RFM.
- **dim_suscripciones**: planes de suscripción con evolución temporal.
- **dim_contenidos**: catálogo de contenidos con seguimiento de atributos.

### Hechos
- **fact_suscripciones_cuentas**: períodos de suscripción con análisis de churn y cambios de plan.
- **fact_rfm**: segmentación Recency-Frequency-Monetary con ventana móvil de 6 meses.

### Características técnicas
- **Carga incremental**: solo procesa datos nuevos o modificados.
- **Particionado**: optimiza consultas por fecha.
- **Testing automático**: valida integridad referencial y calidad de datos.
- **Documentación**: cada tabla y columna está documentada con su propósito de negocio.

## Uso técnico

### Instalación

```bash
pip install -r requirements.txt
```

### Configuración

1. **Configurar perfil de dbt**:
   ```bash
   # Copiar el archivo de ejemplo
   cp profiles.example.yml profiles.yml
   ```
   
   luego edita el archivo `profiles.yml` con tu editor preferido y ajusta los valores según tu entorno.

2. **Configurar variables de entorno**:
   
   **Windows (PowerShell)**:
   ```powershell
   $env:BUCKET_STAGING="s3://tu-bucket-staging"
   $env:BUCKET_ANALYTICS="s3://tu-bucket-analytics"
   $env:AWS_PROFILE="tu-perfil-aws"  # Opcional si usas AWS CLI configurado
   ```
   
   **Linux/Mac (Bash)**:
   ```bash
   export BUCKET_STAGING="s3://tu-bucket-staging"
   export BUCKET_ANALYTICS="s3://tu-bucket-analytics"
   export AWS_PROFILE="tu-perfil-aws"  # Opcional si usas AWS CLI configurado
   ```

### Ejecución

#### Orden recomendado para ejecución manual:

```bash
# 1. Ejecutar modelos de staging
dbt run --select staging

# 2. Ejecutar snapshots (SCD Tipo 2)
dbt snapshot

# 3. Ejecutar modelos de marts (analytics)
dbt run --select marts

# 4. Ejecutar tests
dbt test
```

#### Comandos adicionales:

```bash
# Ejecutar todo el pipeline (automático)
dbt run

# Ejecutar solo modelos específicos
dbt run --select dim_cuentas fact_rfm

# Ejecutar con dependencias
dbt run --select +fact_rfm

# Ejecutar tests específicos
dbt test --select fact_rfm
```

### Parámetros disponibles

| Parámetro | Descripción | Valores |
|-----------|-------------|---------|
| `--select` | Modelos específicos a ejecutar | dim_cuentas, fact_rfm, +fact_rfm |
| `--exclude` | Modelos a excluir | Nombres de modelos |
| `--vars` | Variables personalizadas | fecha_rfm: '2024-01-01' |

### Estructura del módulo

- `dbt_project.yml`: Configuración principal del proyecto
- `profiles.example.yml`: Archivo de ejemplo para configuración de perfiles
- `models/staging/`: Modelos de la capa staging
- `models/marts/`: Modelos dimensionales de la capa analytics
- `snapshots/`: Configuración de snapshots para SCD Tipo 2
- `macros/`: Funciones reutilizables de SQL
- `tests/`: Tests de calidad de datos

### Buenas prácticas implementadas

- **Naming conventions**: Nombres consistentes en español para facilitar comprensión del negocio
- **Documentación**: Cada modelo documenta su propósito y lógica de negocio
- **Testing**: Tests automáticos de integridad referencial y calidad
- **Incrementalidad**: Carga solo datos nuevos para eficiencia
- **Modularidad**: Modelos reutilizables y bien organizados por capas
- **Versionado**: Control de versiones de esquemas y lógica de transformación

### Visualización del modelo

El siguiente grafo muestra las dependencias y relaciones entre todos los modelos del proyecto:

![Grafo de dependencias dbt](dag_completo.png)

Para generar el grafo interactivo:

```bash
# Generar el grafo de dependencias
dbt docs generate

# Servir la documentación localmente
dbt docs serve
```

El grafo muestra:
- **Dependencias entre modelos**: cómo se relacionan staging → snapshots → marts.
- **Flujo de datos**: desde las fuentes raw hasta las tablas finales.
- **Tests de calidad**: validaciones aplicadas a cada modelo.
- **Documentación**: descripción de cada tabla y columna.

### Despliegue en AWS

El módulo está configurado para ejecutarse en AWS Athena con:
- **Particionado por fecha**: optimiza consultas temporales.
- **Formato Iceberg**: soporte para ACID y evolución de esquemas.
- **Buckets S3 separados**: staging y analytics en buckets diferentes.
- **Variables de entorno**: configuración dinámica por entorno.

Ver el módulo de **orquestación** para detalles sobre la ejecución automatizada en AWS.
