# API DataVision

## Problema de negocio

Los equipos de producto necesitan acceso programático a la segmentación RFM de usuarios para:

- **Motor de recomendaciones**: consultar segmento RFM del usuario para personalizar sugerencias de contenido.
- **Sistema de notificaciones push**: enviar alertas específicas según el comportamiento del usuario (ej: "Clientes Leales" reciben notificaciones de nuevos lanzamientos).
- **Página de perfil**: mostrar al usuario su segmentación actual y beneficios asociados.
- **Sistema de soporte**: priorizar tickets de usuarios "Campeones" o "No se pueden perder".

Actualmente, estos equipos dependen de consultas SQL manuales o reportes estáticos que no se actualizan en tiempo real, generando experiencias de usuario inconsistentes y oportunidades perdidas de personalización.

## Arquitectura de componentes

### API Gateway + Lambda + Athena
- **API Gateway**: expone la API como servicio web con autenticación, throttling y monitoreo.
- **AWS Lambda**: ejecuta la lógica de negocio de forma serverless, escalando automáticamente según la demanda.
- **Mangum**: adaptador que permite ejecutar aplicaciones ASGI (como FastAPI) en AWS Lambda, convirtiendo eventos de Lambda a requests HTTP estándar.
- **Amazon Athena**: consulta directamente los datos del data lake en S3 usando SQL estándar.
- **Amazon ECR**: almacena la imagen Docker de la aplicación para despliegue consistente.

### Flujo de datos
1. **Cliente** hace petición HTTP a API Gateway.
2. **API Gateway** autentica y enruta a Lambda.
3. **Lambda** ejecuta consulta SQL en Athena.
4. **Athena** procesa datos del data lake en S3.
5. **Respuesta** se devuelve al cliente en formato JSON.

## API REST desarrollada con FastAPI

API REST desarrollada con FastAPI para consultas de datos usando Amazon Athena. Esta API está diseñada para desplegarse en AWS API Gateway con AWS Lambda usando una imagen de Docker almacenada en Amazon ECR.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs REST
- **Amazon Athena**: Consultas SQL sobre el data lake construido en S3
- **AWS Lambda**: Ejecución serverless
- **Docker**: Containerización para despliegue consistente
- **Amazon ECR**: Registro de contenedores
- **API Gateway**: Exposición de la API como servicio web
- **Mangum**: Adaptador para ejecutar FastAPI en Lambda


## Buenas prácticas implementadas

### Separación de responsabilidades
- **Lógica de negocio**: encapsulada en funciones específicas para cada endpoint.
- **Acceso a datos**: abstraído en funciones auxiliares que manejan la complejidad de Athena.
- **Validación**: modelos Pydantic para validación automática de entrada y salida.

### Manejo de errores
- **HTTP status codes**: respuestas apropiadas (200, 404, 500) según el tipo de error.
- **Mensajes descriptivos**: errores claros que facilitan el debugging y la resolución.
- **Logging**: registro detallado de errores para monitoreo y análisis.

### Escalabilidad y rendimiento
- **Serverless**: escalado automático según la demanda sin gestión de infraestructura.
- **Caching**: resultados de consultas frecuentes pueden ser cacheados en API Gateway.
- **Timeouts**: manejo apropiado de consultas largas con timeouts configurables.

## 📋 Endpoints disponibles

### Endpoints del sistema
- `GET /` - Endpoint raíz con mensaje de bienvenida
- `GET /health` - Verificación de salud de la API
- `GET /api/v1/status` - Estado detallado de la API y endpoints disponibles

### Endpoints de negocio (análisis RFM)
- `GET /api/v1/rfm/segmentos` - Obtener segmentos RFM disponibles
- `GET /api/v1/rfm/cliente/{id_cuenta}` - Obtener datos RFM de un cliente específico

## 🛠️ Tecnologías utilizadas

- **Python 3.11**
- **FastAPI 0.104.1**
- **Mangum 0.17.0** (adaptador Lambda)
- **Boto3 1.34.0** (SDK de AWS)
- **Pydantic 2.5.0** (validación de datos)

## Configuración y despliegue

### Variables de entorno requeridas
```bash
# Configuración de Athena
ATHENA_DATABASE=datavision
ATHENA_WORKGROUP=primary
ATHENA_OUTPUT_LOCATION=s3://tu-bucket-athena-results/

# Configuración de la aplicación
PORT=8000  # Solo para desarrollo local
```

### Despliegue en AWS
1. **Construir imagen Docker**:
   ```bash
   docker build -t datavision-api .
   ```

2. **Subir a ECR**:
   ```bash
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
   docker tag datavision-api:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/datavision-api:latest
   docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/datavision-api:latest
   ```

3. **Configurar Lambda**: usar la imagen ECR como base y configurar variables de entorno.

4. **Configurar API Gateway**: crear API REST y conectar con Lambda.

### Desarrollo local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
python main.py
```

La API estará disponible en `http://localhost:8000` con documentación automática en `http://localhost:8000/docs`.

## 📦 Estructura del proyecto

```
api/
├── main.py                 # Aplicación principal FastAPI
├── lambda_function.py      # Handler para AWS Lambda
├── requirements.txt        # Dependencias de Python
├── Dockerfile             # Imagen Docker para Lambda
└── README.md              # Este archivo
```