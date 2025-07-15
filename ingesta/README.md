# Módulo de Ingesta de Datos

Este directorio contiene los scripts y recursos necesarios para el proceso de ingesta de datos en el proyecto. La ingesta de datos es el primer paso en el pipeline ELT y se encarga de extraer datos del sistema transaccional en postgres y cargarlos en el destino (DuckDB o AWS Athena).

## Estructura del Directorio

- `ingesta_churn.py`: Script principal para la ingesta de datos relacionados con el análisis de churn.
- `calidad_de_datos.py`: Módulo que contiene funciones para validar y asegurar la calidad de los datos durante la ingesta.
- `ingesta_ejemplo.py`: Ejemplo de implementación de un proceso de ingesta.
- `requirements.txt`: Lista de dependencias de Python necesarias para ejecutar los scripts de ingesta.

## Requisitos

Asegúrate de instalar las dependencias necesarias ejecutando:

```bash
pip install -r requirements.txt
```

## Uso

### Ejecución Básica

```bash
# Cargar datos en entorno local (DuckDB)
python ingesta_churn.py --env local

# Cargar datos en entorno de desarrollo (Athena)
python ingesta_churn.py --env dev

# Cargar datos en entorno de producción (Athena)
python ingesta_churn.py --env prod
```

### Opciones Avanzadas

```bash
# Cargar solo tablas específicas
python ingesta_churn.py --env local --tables accounts subscriptions

# Forzar recarga completa de tablas específicas
python ingesta_churn.py --env dev --full-refresh accounts content_attributes

# Ejecutar validaciones de calidad de datos
python ingesta_churn.py --env prod --validate-only
```

### Parámetros

| Parámetro | Descripción | Valores |
|-----------|-------------|---------|
| `--env` | Entorno de ejecución | local, dev, prod |
| `--tables` | Tablas específicas a cargar | Nombres de tablas separados por espacio |
| `--full-refresh` | Forzar recarga completa | Nombres de tablas separados por espacio |
| `--validate-only` | Solo ejecutar validaciones sin cargar datos | N/A |
