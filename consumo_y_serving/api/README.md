# API DataVision

API REST desarrollada con FastAPI para consultas de datos usando Amazon Athena. Esta API está diseñada para desplegarse en AWS API Gateway con AWS Lambda usando una imagen de Docker almacenada en Amazon ECR.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs REST
- **Amazon Athena**: Consultas SQL sobre el data lake construido en S3
- **AWS Lambda**: Ejecución serverless
- **Docker**: Containerización para despliegue consistente
- **Amazon ECR**: Registro de contenedores
- **API Gateway**: Exposición de la API como servicio web
- **Mangum**: Adaptador para ejecutar FastAPI en Lambda

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

## 📦 Estructura del proyecto

```
api/
├── main.py                 # Aplicación principal FastAPI
├── lambda_function.py      # Handler para AWS Lambda
├── requirements.txt        # Dependencias de Python
├── Dockerfile             # Imagen Docker para Lambda
└── README.md              # Este archivo
```