# Módulo de Ingesta de Datos

## ¿Qué problema resuelve para el negocio?

Este módulo automatiza la extracción y carga de datos desde el sistema transaccional (PostgreSQL) hacia el data lakehouse, resolviendo los siguientes desafíos del negocio:

- **Centralización de datos**: Unifica información dispersa de cuentas, suscripciones, contenidos y pagos en un solo lugar
- **Disponibilidad para análisis**: Hace que los datos operacionales estén disponibles para análisis de negocio sin impactar el sistema transaccional
- **Calidad de datos**: Implementa validaciones automáticas para asegurar integridad, completitud y frescura de los datos
- **Escalabilidad**: Soporta desde desarrollo local hasta entornos de producción con diferentes volúmenes de datos
- **Eficiencia operacional**: Reduce el tiempo de carga de datos de horas a minutos mediante cargas incrementales inteligentes

## ¿Cómo funciona?

El módulo utiliza **dltHub** (Data Load Tool), una herramienta open source especializada en ingesta de datos que:
- Infiere esquemas y tipos de datos automáticamente
- Normaliza datos y maneja estructuras anidadas
- Soporta múltiples destinos (DuckDB, AWS Athena, etc.)
- Automatiza el mantenimiento de pipelines con carga incremental y evolución de esquemas

**Arquitectura de tres capas**: Este módulo alimenta la primera capa (raw) de la arquitectura lakehouse, donde se almacenan los datos en su formato original para posterior procesamiento en las capas de staging y analytics.

**Modularidad**: Al usar Python, el mismo código funciona en diferentes entornos (desarrollo, producción) mediante parámetros de configuración, facilitando el mantenimiento y la consistencia.

El módulo extrae datos de 8 tablas principales del sistema transaccional:
- **Cuentas y suscripciones**: Información de clientes y sus planes
- **Contenidos**: Catálogo de productos/servicios ofrecidos
- **Pagos**: Transacciones y facturación
- **Características premium**: Funcionalidades adicionales disponibles

Los datos se cargan de forma inteligente:
- **Carga incremental** para tablas que cambian frecuentemente (contenidos, atributos)
- **Carga completa** para tablas maestras (suscripciones, características)
- **Validación automática** de calidad de datos después de cada carga

## Calidad de Datos

El módulo incluye un sistema básico basado en consultas SQL de validación de calidad que verifica:
- **Conteo de registros**: Compara el número de registros entre origen y destino
- **Duplicados**: Detecta registros duplicados por clave primaria
- **Integridad referencial**: Valida relaciones entre tablas (claves foráneas)
- **Frescura**: Verifica que los datos estén actualizados (máximo 48 horas)

**Importancia crítica**: Muchos problemas de datos tienen su origen en la ingesta. Validar la calidad desde el primer paso previene errores costosos en análisis posteriores y asegura la confiabilidad de todo el pipeline de datos.

## Uso técnico

### Instalación

```bash
pip install -r requirements.txt
```

### Ejecución Básica

```bash
# Desarrollo local (DuckDB)
python ingesta_datavision.py --env local

# Desarrollo (AWS Athena)
python ingesta_datavision.py --env dev

# Producción (AWS Athena)
python ingesta_datavision.py --env prod
```

### Opciones Avanzadas

```bash
# Cargar tablas específicas
python ingesta_datavision.py --env local --tables accounts subscriptions

# Recarga completa de tablas
python ingesta_datavision.py --env dev --full-refresh accounts content_attributes

# Solo validar calidad de datos
python ingesta_datavision.py --env prod --solo-validar

# Cargar con validación automática
python ingesta_datavision.py --env prod --validar-calidad-datos
```

### Parámetros Disponibles

| Parámetro | Descripción | Valores |
|-----------|-------------|---------|
| `--env` | Entorno de ejecución | local, dev, prod |
| `--tables` | Tablas específicas a cargar | accounts, subscriptions, contents, etc. |
| `--full-refresh` | Forzar recarga completa | N/A |
| `--validar-calidad-datos` | Ejecutar validaciones después de la carga | N/A |
| `--solo-validar` | Solo ejecutar validaciones sin cargar | N/A |

### Estructura del Módulo

- `ingesta_datavision.py`: Script principal de ingesta
- `calidad_de_datos.py`: Validaciones de calidad (conteo, duplicados, integridad, frescura)
- `ingesta_ejemplo.py`: Ejemplo simplificado de uso
- `schemas/`: Definiciones de esquemas de datos
- `Dockerfile`: Imagen Docker para despliegue en AWS
- `entry_point.sh`: Script de inicialización para contenedores

### Despliegue en AWS

El módulo está preparado para ejecutarse en AWS usando:
- **ECR (Elastic Container Registry)**: Almacena la imagen Docker
- **Fargate**: Ejecuta el contenedor sin gestión de servidores
- **ECS**: Orquesta las tareas de ingesta

La imagen Docker incluye:
- Python 3.13 con todas las dependencias
- Configuración dinámica mediante variables de entorno
- Usuario no-root para seguridad
- Script de entrada que genera configuración automáticamente

Ver el módulo de **orquestación** para detalles sobre la implementación completa en AWS.
