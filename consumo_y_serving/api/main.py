from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from typing import List, Optional
import boto3
import os
import json

# Configuración de Athena
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "datavision")
ATHENA_WORKGROUP = os.getenv("ATHENA_WORKGROUP", "primary")
ATHENA_OUTPUT_LOCATION = os.getenv("ATHENA_OUTPUT_LOCATION", "s3://dateneo-athena-results-us-west-2-034362074834/")

# Cliente de Athena
athena_client = boto3.client('athena')

# Modelos Pydantic para las respuestas
class SegmentoRFM(BaseModel):
    segmento: str
    descripcion: str
    caracteristicas: str

class ClienteRFM(BaseModel):
    id_cuenta: int
    email: str
    nombre: str
    segmento_rfm_ultimo: str
    fecha_rfm_ultimo: str
    segmento_rfm_anterior: str
    fecha_rfm_anterior: str

class ErrorResponse(BaseModel):
    error: str
    message: str

# Crear la aplicación FastAPI
app = FastAPI(
    title="DataVision API",
    description="API para consultas de datos usando Athena",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz - Hola mundo"""
    return {"message": "¡Hola mundo! Bienvenido a la API de DataVision"}

@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que la API está funcionando"""
    return {"status": "healthy", "service": "datavision-api"}

@app.get("/api/v1/status")
async def api_status():
    """Endpoint de estado de la API"""
    return {
        "api_version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/",
            "/health",
            "/api/v1/status",
            "/api/v1/rfm/segmentos",
            "/api/v1/rfm/cliente/{id_cuenta}"
        ],
        "features": [
            "RFM Analysis",
            "Athena Integration",
            "OpenAPI Documentation",
            "CORS Support"
        ]
    }

# Funciones auxiliares para Athena
async def ejecutar_consulta_athena(query: str) -> List[dict]:
    """Ejecuta una consulta en Athena y retorna los resultados"""
    try:
        # Ejecutar la consulta
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': ATHENA_DATABASE},
            ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_LOCATION},
            WorkGroup=ATHENA_WORKGROUP
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # Esperar a que termine la consulta
        while True:
            response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = response['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED']:
                break
            elif status in ['FAILED', 'CANCELLED']:
                error_reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                raise HTTPException(status_code=500, detail=f"Query failed: {error_reason}")
            
            # Esperar 1 segundo antes de verificar nuevamente
            import time
            time.sleep(1)
        
        # Obtener los resultados
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
        # Procesar los resultados
        rows = results['ResultSet']['Rows']
        if len(rows) < 2:  # Menos de 2 filas significa que no hay datos (solo headers)
            return []
        
        # Obtener los nombres de las columnas
        columns = [col['VarCharValue'] for col in rows[0]['Data']]
        
        # Procesar las filas de datos
        data = []
        for row in rows[1:]:
            row_data = {}
            for i, col in enumerate(row['Data']):
                value = col.get('VarCharValue', '')
                # Convertir a tipos apropiados
                if columns[i] in ['id_cuenta']:
                    row_data[columns[i]] = int(value) if value else 0
                else:
                    row_data[columns[i]] = value
            data.append(row_data)
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando consulta: {str(e)}")

# Endpoints de negocio

@app.get("/api/v1/rfm/segmentos", 
         response_model=List[SegmentoRFM],
         summary="Obtener segmentos RFM disponibles",
         description="Retorna la lista de segmentos RFM definidos en el sistema con sus características")
async def obtener_segmentos_rfm():
    """
    Obtiene los segmentos RFM disponibles en el sistema.
    
    Los segmentos RFM se basan en:
    - **Recency**: Días desde la última actividad
    - **Frequency**: Frecuencia total de actividades
    - **Monetary**: Valor monetario total gastado
    
    Cada segmento tiene características específicas que ayudan a entender el comportamiento del cliente.
    """
    segmentos = [
        SegmentoRFM(
            segmento="Campeones",
            descripcion="Clientes con alta recency, frequency y monetary",
            caracteristicas="R≥4, F≥4, M≥4 - Clientes más valiosos, compran frecuentemente y recientemente"
        ),
        SegmentoRFM(
            segmento="Clientes Leales",
            descripcion="Clientes con alta recency y altos valores de frequency/monetary",
            caracteristicas="R≥4, F≥3, M≥3 - Clientes satisfechos que responden bien a promociones"
        ),
        SegmentoRFM(
            segmento="Clientes de Alto Valor",
            descripcion="Clientes con alta recency y monetary pero baja frequency",
            caracteristicas="R≥4, M≥4, F<3 - Clientes que gastan mucho pero no frecuentemente"
        ),
        SegmentoRFM(
            segmento="Clientes Potenciales",
            descripcion="Clientes con alta recency y valores medios de frequency/monetary",
            caracteristicas="R≥4, F≥2, M≥2 - Clientes con potencial de crecimiento"
        ),
        SegmentoRFM(
            segmento="Nuevos Clientes",
            descripcion="Clientes muy recientes con baja frequency y monetary",
            caracteristicas="R=5, F≤2, M≤2 - Clientes nuevos que necesitan ser retenidos"
        ),
        SegmentoRFM(
            segmento="Necesitan Atención",
            descripcion="Clientes con baja recency pero alta frequency y monetary",
            caracteristicas="R≤3, F≥4, M≥4 - Clientes valiosos que se están alejando"
        ),
        SegmentoRFM(
            segmento="En Riesgo",
            descripcion="Clientes con baja recency y valores medios de frequency/monetary",
            caracteristicas="R≤3, F≥2, M≥2 - Clientes en riesgo de abandono"
        ),
        SegmentoRFM(
            segmento="No se pueden perder",
            descripcion="Clientes con muy baja recency pero alta frequency y monetary",
            caracteristicas="R≤2, F≥4, M≥4 - Clientes críticos que necesitan atención inmediata"
        ),
        SegmentoRFM(
            segmento="Clientes Dormidos",
            descripcion="Clientes con muy baja recency, frequency y monetary",
            caracteristicas="R≤2, F≤2, M≤2 - Clientes inactivos"
        ),
        SegmentoRFM(
            segmento="Perdidos",
            descripcion="Clientes con valores muy bajos en todas las métricas",
            caracteristicas="R=1, F=1, M=1 - Clientes perdidos"
        ),
        SegmentoRFM(
            segmento="Clientes Regulares",
            descripcion="Clientes que no encajan en las categorías anteriores",
            caracteristicas="Cualquier otra combinación - Clientes con comportamiento estándar"
        )
    ]
    
    return segmentos

@app.get("/api/v1/rfm/cliente/{id_cuenta}", 
         response_model=ClienteRFM,
         summary="Obtener datos RFM de un cliente específico",
         description="Retorna los datos RFM completos de un cliente basado en su ID de cuenta")
async def obtener_cliente_rfm(id_cuenta: int):
    """
    Obtiene los datos RFM de un cliente específico.
    
    **Parámetros:**
    - **id_cuenta**: ID único de la cuenta del cliente
    
    **Respuesta:**
    - Datos demográficos del cliente
    - Segmentación RFM actual y anterior
    - Scores individuales (Recency, Frequency, Monetary)
    - Métricas de comportamiento
    
    **Ejemplo de uso:**
    ```
    GET /api/v1/rfm/cliente/12345
    ```
    """
    query = f"""
    SELECT 
        id_cuenta,
        correo_electronico as email,
        nombre_cuenta as nombre,
        segmento_rfm_ultimo,
        fecha_rfm_ultimo,
        segmento_rfm_anterior,
        fecha_rfm_anterior
    FROM dim_cuentas
    WHERE id_cuenta = {id_cuenta} and es_actual
    """
    
    try:
        resultados = await ejecutar_consulta_athena(query)
        
        if not resultados:
            raise HTTPException(status_code=404, detail=f"Cliente con ID {id_cuenta} no encontrado")
        
        cliente_data = resultados[0]
        
        return ClienteRFM(
            id_cuenta=cliente_data['id_cuenta'],
            email=cliente_data['email'],
            nombre=cliente_data['nombre'],
            segmento_rfm_ultimo=cliente_data['segmento_rfm_ultimo'],
            fecha_rfm_ultimo=str(cliente_data['fecha_rfm_ultimo']),
            segmento_rfm_anterior=cliente_data['segmento_rfm_anterior'],
            fecha_rfm_anterior=str(cliente_data['fecha_rfm_anterior'])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos del cliente: {str(e)}")

# Crear el handler de Mangum para Lambda
handler = Mangum(app)

# Para desarrollo local (solo si se ejecuta directamente)
if __name__ == "__main__":
    try:
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True
        )
    except ImportError:
        print("uvicorn no está instalado. Instálalo con: pip install uvicorn")
        print("Ejecutando solo la aplicación FastAPI...")
