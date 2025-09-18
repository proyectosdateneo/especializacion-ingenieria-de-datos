# Reverse ETL - Carga RFM a CRM

Script de reverse ETL que sincroniza los segmentos RFM desde Amazon Athena hacia HubSpot CRM. Actualiza automáticamente la propiedad `segmento_rfm` en las empresas de HubSpot basándose en los datos más recientes del data warehouse.

## 🚀 ¿Qué hace este script?

Este script implementa un proceso de **reverse ETL** que:

1. **Extrae** datos de segmentación RFM desde Athena (data warehouse)
2. **Transforma** los datos para mapear cuentas con empresas en HubSpot
3. **Carga** los segmentos RFM actualizados en HubSpot CRM

### Flujo de datos:
```
Athena (Data Warehouse) → Python Script → HubSpot CRM
     ↓                        ↓              ↓
Segmentos RFM          Mapeo de datos    Actualización
actualizados           id_cuenta →       de propiedades
                       company_id        en empresas
```

## 🛠️ Tecnologías utilizadas

- **Python 3.8+**
- **awswrangler 3.13.0** - Conexión con Athena
- **requests 2.32.4** - API de HubSpot
- **boto3** - SDK de AWS
- **pandas** - Manipulación de datos

## 📋 Prerrequisitos

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

## ⚙️ Configuración

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

**Nota**: Puedes usar el archivo `env.example` como plantilla. Copia el archivo y renómbralo a `.env`, luego actualiza los valores según tu configuración.

### Configuración del archivo .env

1. **Copiar la plantilla**:
```bash
cp env.example .env
```

2. **Editar el archivo .env** con tus valores reales:
```bash
# Editar con tu editor preferido
nano .env
# o
code .env
# o
notepad .env
```

3. **Verificar que el archivo .env esté en el directorio correcto**:
```
reverse_etl/
├── carga_rfm_crm.py
├── requirements.txt
├── env.example
└── .env          ← Este archivo debe estar aquí
```

### Instalación de dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt

# O instalar manualmente
pip install awswrangler==3.13.0 requests==2.32.4 python-dotenv==1.0.0
```

## 🚀 Uso del script

### Modo normal (ejecutar actualizaciones)

```bash
# Ejecutar el script completo (usa PROCESSING_LIMIT del .env)
python carga_rfm_crm.py

# Con límite específico desde línea de comandos
python carga_rfm_crm.py limit=10

# Con variables de entorno
HUBSPOT_API_KEY=tu_api_key python carga_rfm_crm.py
```

### Modo de prueba (verificar conexiones)

```bash
# Probar conexiones y mapeo de datos
python carga_rfm_crm.py test

# Probar con cuenta específica
TEST_ACCOUNT_ID=123 python carga_rfm_crm.py test
```

### Ejemplo completo de configuración

1. **Configurar el archivo .env**:
```bash
# Copiar plantilla
cp env.example .env

# Editar con tus valores
nano .env
```

2. **Contenido del archivo .env**:
```bash
# Configuración de HubSpot
HUBSPOT_API_KEY=pat-na1-tu-api-key-real-aqui
HUBSPOT_BASE_URL=https://api.hubapi.com

# Configuración de AWS Athena
ATHENA_DATABASE=analytics_datavision_prod
ATHENA_WORKGROUP=datavision-375612485931
AWS_REGION=us-west-2
AWS_PROFILE=tu-perfil-aws

# Configuración de procesamiento
PROCESSING_LIMIT=10
TEST_ACCOUNT_ID=4

# Configuración de logging
LOG_LEVEL=INFO
```

3. **Ejecutar el script**:
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo de prueba
python carga_rfm_crm.py test

# Ejecutar actualizaciones
python carga_rfm_crm.py
```

## 📊 Funcionalidades

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

## 📝 Logging y monitoreo

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

## 🔧 Configuración avanzada

### Modificar límite de registros
Para cambiar el límite de registros procesados, puedes:

1. **Usar variable de entorno** (recomendado):
```bash
export PROCESSING_LIMIT=10
python carga_rfm_crm.py
```

2. **Usar parámetro de línea de comandos**:
```bash
python carga_rfm_crm.py limit=10
```

3. **Modificar el archivo .env**:
```bash
PROCESSING_LIMIT=10
```

### Cambiar propiedades de HubSpot
Para usar diferentes propiedades, modifica las líneas 72 y 101:

```python
# Línea 72 - Propiedades a obtener
'properties': ['id_datavision', 'name', 'segmento_rfm']

# Línea 101 - Propiedad a actualizar
'segmento_rfm': segmento_rfm
```

### Configurar logging
Para cambiar el nivel de logging, puedes:

1. **Usar variable de entorno** (recomendado):
```bash
export LOG_LEVEL=DEBUG
python carga_rfm_crm.py
```

2. **Modificar el archivo .env**:
```bash
LOG_LEVEL=DEBUG
```

3. **Valores disponibles**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚨 Manejo de errores

El script maneja los siguientes tipos de errores:

1. **Errores de conexión AWS**: Verifica permisos y configuración
2. **Errores de API HubSpot**: Verifica API key y límites de rate
3. **Datos no encontrados**: Registra cuentas sin mapeo en HubSpot
4. **Errores de mapeo**: Identifica problemas de sincronización de datos

## 📈 Métricas y estadísticas

El script proporciona métricas detalladas:

- **Actualizaciones exitosas**: Número de empresas actualizadas correctamente
- **Actualizaciones fallidas**: Errores en la actualización
- **Cuentas no encontradas**: Cuentas de Athena sin mapeo en HubSpot
- **Tasa de coincidencia**: Porcentaje de cuentas mapeadas exitosamente

## 🐛 Troubleshooting

### Problemas con archivo .env

1. **Error "HUBSPOT_API_KEY no está configurada"**:
   - Verificar que el archivo `.env` existe en el directorio correcto
   - Verificar que la variable `HUBSPOT_API_KEY` está definida en el archivo
   - Verificar que no hay espacios alrededor del signo `=`

2. **Variables de entorno no se cargan**:
   - Verificar que `python-dotenv` está instalado: `pip install python-dotenv`
   - Verificar que el archivo `.env` está en el mismo directorio que `carga_rfm_crm.py`
   - Verificar que el archivo `.env` tiene el formato correcto (sin espacios alrededor del `=`)

3. **Archivo .env no encontrado**:
   - Crear el archivo: `cp env.example .env`
   - Verificar la ubicación del archivo
   - Verificar permisos de lectura del archivo

### Problemas comunes de conexión

1. **Error de conexión AWS**:
   - Verificar configuración de AWS CLI
   - Comprobar permisos de Athena

2. **Error de API HubSpot**:
   - Verificar API key válida
   - Comprobar límites de rate

3. **Cuentas no encontradas**:
   - Verificar mapeo de `id_datavision`
   - Comprobar sincronización de datos

4. **Errores de permisos**:
   - Verificar permisos de escritura en HubSpot
   - Comprobar permisos de lectura en Athena



