# Reverse ETL - Carga RFM a CRM

## Problema de negocio

Los equipos de marketing y ventas necesitan que los datos de segmentación RFM estén disponibles en sus herramientas operativas para ejecutar campañas personalizadas. Actualmente, estos datos solo existen en el lakehouse, creando una desconexión entre los insights analíticos y la acción comercial.

Este módulo resuelve el problema de **data activation** al sincronizar automáticamente los segmentos RFM desde el lakehouse hacia HubSpot CRM, permitiendo que los equipos de marketing:

- **Ejecuten campañas segmentadas**: envíen emails personalizados según el comportamiento del cliente.
- **Prioricen leads**: identifiquen cuentas de alto valor para seguimiento comercial.
- **Automaticen workflows**: activen secuencias de marketing basadas en cambios de segmentación.
- **Mejoren la retención**: implementen estrategias específicas para cada segmento de clientes.

## Script de reverse ETL

Script de reverse ETL que sincroniza los segmentos RFM desde Amazon Athena hacia HubSpot CRM. Actualiza automáticamente la propiedad `segmento_rfm` en las empresas de HubSpot basándose en los datos más recientes del lakehouse.

## ¿Qué hace este script?

Este script implementa un proceso que:

1. **Extrae** datos de segmentación RFM desde Athena (lakehouse).
2. **Transforma** los datos para mapear cuentas con empresas en HubSpot.
3. **Carga** los segmentos RFM actualizados en HubSpot CRM.

### Flujo de datos:
```
Athena (Data Warehouse) → Python Script → HubSpot CRM
     ↓                        ↓              ↓
Segmentos RFM          Mapeo de datos    Actualización
actualizados           id_cuenta →       de propiedades
                       company_id        en empresas
```

## Tecnologías utilizadas

- **Python 3.8+**
- **awswrangler 3.13.0** - Conexión con Athena
- **requests 2.32.4** - API de HubSpot
- **boto3** - SDK de AWS
- **pandas** - Manipulación de datos

## Prerrequisitos

### 1. Configuración de AWS
- AWS CLI configurado
- Permisos de Athena (lectura)
- Perfil de AWS configurado

### 2. Configuración de HubSpot
- API Key de HubSpot con permisos de escritura
- Propiedad personalizada `segmento_rfm` creada en HubSpot
- Propiedad `id_datavision` en empresas para mapeo

### 3. Estructura de datos
- Tabla `dim_cuentas` en Athena con columnas:
  - `id_cuenta` (integer)
  - `segmento_rfm_ultimo` (string)
  - `es_actual` (boolean)

## Configuración

### Variables de entorno requeridas

Crea un archivo `.env` o configura las siguientes variables:

```bash
# HubSpot (REQUERIDO)
HUBSPOT_API_KEY=pat-na1-xxxxx-xxxxx-xxxxx-xxxxx
HUBSPOT_BASE_URL=https://api.hubapi.com

# AWS Athena
ATHENA_DATABASE=analytics_datavision_prod
ATHENA_WORKGROUP=datavision-375612485931
AWS_REGION=us-west-2
AWS_PROFILE=bruno_especializacion

# Configuración de procesamiento
PROCESSING_LIMIT=5
TEST_ACCOUNT_ID=4

# Configuración de logging
LOG_LEVEL=INFO
```

**Nota**: podés usar el archivo `env.example` como plantilla. Copiá el archivo y renómbralo a `.env`, luego actualizá los valores según tu configuración.

### Instalación de dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt

# O instalar manualmente
pip install awswrangler==3.13.0 requests==2.32.4 python-dotenv==1.0.0
```

## Uso del script

### Modo normal (ejecutar actualizaciones)

```bash
# Ejecutar el script completo (usa PROCESSING_LIMIT del .env)
python carga_rfm_crm.py

# Con límite específico desde línea de comandos
python carga_rfm_crm.py limit=10
```

### Modo de prueba (verificar conexiones)

```bash
# Probar conexiones y mapeo de datos
python carga_rfm_crm.py test

# Probar con cuenta específica
TEST_ACCOUNT_ID=123 python carga_rfm_crm.py test
```

## Funcionalidades

### 1. Extracción de datos desde Athena
- Consulta la tabla `dim_cuentas` para obtener segmentos RFM actuales
- Filtra solo registros actuales (`es_actual = true`)
- Limita resultados para pruebas (configurable)

### 2. Mapeo de cuentas con empresas
- Busca empresas en HubSpot usando `id_datavision` como identificador
- Mapea `id_cuenta` de Athena con `company_id` de HubSpot

### 3. Actualización en HubSpot
- Actualiza la propiedad `segmento_rfm` en empresas existentes
- Maneja errores de API y registros no encontrados
- Proporciona logging detallado del proceso

### 4. Modo de prueba
- Verifica conexión con HubSpot
- Verifica conexión con Athena
- Prueba el mapeo de datos entre sistemas
- Muestra estadísticas de coincidencias

## Logging y monitoreo

El script genera logs detallados que incluyen:

- **INFO**: Progreso del proceso
- **DEBUG**: Detalles de mapeo y actualizaciones
- **WARNING**: Cuentas no encontradas en HubSpot
- **ERROR**: Errores de conexión o API

### Ejemplo de salida:
```
2024-01-15 14:30:00 - INFO - Iniciando proceso de actualización de RFM...
2024-01-15 14:30:01 - INFO - Obtenidos 5 registros de RFM desde Athena
2024-01-15 14:30:02 - INFO - Procesando 5 cuentas...
2024-01-15 14:30:05 - INFO - ==================================================
2024-01-15 14:30:05 - INFO - RESUMEN DE ACTUALIZACIONES RFM:
2024-01-15 14:30:05 - INFO - Actualizaciones exitosas: 4
2024-01-15 14:30:05 - INFO - Actualizaciones fallidas: 0
2024-01-15 14:30:05 - INFO - Cuentas no encontradas en HubSpot: 1
2024-01-15 14:30:05 - INFO - Total procesadas: 5
2024-01-15 14:30:05 - INFO - ==================================================
```