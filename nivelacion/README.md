# Módulo de nivelación de datos

## ¿Qué problema resuelve para el negocio?

Este módulo automatiza la generación del **Reporte cuentas Empresarial**, replicando y automatizando el análisis que tradicionalmente se realizaba manualmente en Excel. Resuelve los siguientes desafíos:

- **Automatización de reportes**: elimina el trabajo manual repetitivo de generar reportes mensuales.
- **Consistencia de datos**: asegura que todos los reportes sigan la misma lógica de negocio.
- **Trazabilidad**: mantiene un registro de cuándo y cómo se generó cada reporte.
- **Disponibilidad**: hace que los reportes estén disponibles de forma programática.

## ¿Cómo funciona?

**Objetivo del módulo**: construir un ETL punta a punta usando únicamente Python y SQL, sirviendo como repaso de conceptos fundamentales antes de abordar el proyecto general de DataVision.

**Enfoque pedagógico**: aunque es un ejemplo básico, es completamente funcional y demuestra que no siempre se requieren arquitecturas sofisticadas para resolver problemas reales de ingeniería de datos.

### Conceptos de SQL implementados
- **CTE (Common Table Expressions)**: para organizar consultas complejas de manera legible.
- **CASE WHEN**: para lógica condicional y categorización de datos.
- **Funciones ventana**: para cálculos agregados y análisis temporal.

### Conceptos de Python implementados

Estos conceptos son fundamentales en ingeniería de datos y se aplican en todos los proyectos:

- **Punto de entrada main**: estructura `if __name__ == '__main__'` para ejecución modular. Permite que el código sea tanto importable como ejecutable, esencial para pipelines automatizados.
- **Funciones y docstrings**: documentación clara de propósito y parámetros. Las funciones encapsulan lógica reutilizable y los docstrings facilitan el mantenimiento en equipos.
- **Módulos y librerías**: organización del código con `requirements.txt`. Los módulos separan responsabilidades y `requirements.txt` garantiza entornos reproducibles.
- **Manejo de excepciones**: control robusto de errores en cada etapa. Crítico en pipelines de datos donde un fallo puede corromper millones de registros.

## Uso técnico

### Instalación

```bash
pip install -r requirements.txt
```

### Configuración

1. **Configurar archivo YAML**:
   ```yaml
   # etl_config.yaml
   database:
     host: "tu-host-postgresql"
     port: 5432
     name: "datavision"
     username: "usuario"
     password: "contraseña"
   
   s3_destination:
     bucket_name: "tu-bucket-s3"
     aws_profile: "tu-perfil-aws"
     aws_region: "us-west-2"
   ```

2. **Variables de entorno (opcional)**:
   
   **Windows (PowerShell)**:
   ```powershell
   $env:DB_HOST="tu-host"
   $env:DB_PASSWORD="tu-password"
   $env:S3_BUCKET_ETL="tu-bucket"
   ```
   
   **Linux/Mac (Bash)**:
   ```bash
   export DB_HOST="tu-host"
   export DB_PASSWORD="tu-password"
   export S3_BUCKET_ETL="tu-bucket"
   ```

### Ejecución

```bash
# Ejecutar pipeline completo
python main_etl.py

# Ejecutar etapas individuales
python ingestion.py      # Solo extracción
python transformation.py # Solo transformación
python loading.py        # Solo carga
```

### Estructura del módulo

- `main_etl.py`: punto de entrada principal con función `run_etl_pipeline()`.
- `config_etl.py`: gestión de configuración desde YAML y variables de entorno.
- `ingestion.py`: extracción de datos desde PostgreSQL usando pandas.
- `transformation.py`: transformación con SQL en SQLite en memoria.
- `loading.py`: carga de resultados a S3 en formato CSV.
- `etl_config.yaml`: configuración de conexiones y destinos.

### Flujo de datos

1. **Extracción**: consulta PostgreSQL para obtener cuentas, suscripciones y relaciones.
2. **Transformación**: aplica lógica de negocio con SQL para generar el reporte enterprise.
3. **Carga**: guarda el resultado en S3 como archivo CSV para consumo posterior.

### Buenas prácticas implementadas

- **Separación de responsabilidades**: cada módulo tiene una función específica.
- **Manejo de errores**: validación en cada etapa del pipeline.
- **Configuración externa**: parámetros en archivos YAML, no hardcodeados.
- **Documentación**: docstrings en todas las funciones.
- **Modularidad**: código reutilizable y fácil de mantener.
