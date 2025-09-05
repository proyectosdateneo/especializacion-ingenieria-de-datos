# Módulo de calidad de datos

Este módulo implementa tests de calidad de datos usando **Soda Core** como ejemplo de una herramienta más genérica para validar la integridad y calidad de los datos en el sistema transaccional.

**Nota importante**: Los tests de calidad de datos del proyecto se implementan principalmente con **dbt**. Este módulo con Soda Core se incluye únicamente como ejemplo de cómo se puede resolver el mismo problema de calidad de datos con herramientas diferentes.

## Archivos del módulo

### `configuration.yml`
Archivo de configuración que define la conexión a la base de datos Athena.

### `checks.yml`
Archivo que contiene los tests de calidad de datos escritos en SodaCL. Incluye ejemplos de diferentes tipos de validaciones que replican funcionalidad equivalente a dbt:

- **Tests de integridad**: not_null, unique, referential integrity
- **Tests de validación**: formatos, rangos, valores válidos
- **Tests de calidad**: freshness, cross-checks entre tablas

### `requirements.txt`
Dependencias de Python necesarias para ejecutar Soda Core.

## Uso

### 1. Probar conexión
Para verificar que la conexión a Athena funciona correctamente:

```bash
soda test-connection -d staging_dev -c configuration.yml -V
```

### 2. Ejecutar Tests de calidad
Para ejecutar todos los checks definidos en el archivo:

```bash
soda scan -d staging_dev -c configuration.yml checks.yml
```

## Tipos de Tests Implementados

### Tests de Integridad de Datos
- **Not Null**: Verifica que campos críticos no sean nulos
- **Unique**: Valida que claves primarias sean únicas
- **Referential Integrity**: Verifica integridad referencial entre tablas

### Tests de Validación de Negocio
- **Format Validation**: Valida formatos de email, fechas, etc.
- **Value Ranges**: Verifica que valores numéricos estén en rangos válidos
- **Accepted Values**: Valida que campos categóricos tengan valores permitidos

### Tests de Calidad de Datos
- **Freshness**: Verifica que los datos se actualicen regularmente
- **Cross-checks**: Compara conteos entre tablas de staging y raw

## Equivalencia con dbt

Los tests implementados en SodaCL replican funcionalidad equivalente a los tests de dbt:

| SodaCL | dbt |
|--------|-----|
| `missing_count(campo) = 0` | `tests: [not_null]` |
| `duplicate_count(campo) = 0` | `tests: [unique]` |
| `values in (campo) must exist in tabla` | `relationships: {to: ref('tabla'), field: 'campo'}` |
| `invalid_count(campo) = 0` con `valid values` | `accepted_values: {values: [...]}` |
| `freshness(campo) < 1d` | `dbt_utils.expression_is_true` con interval |

## Integración al Pipeline

Al igual que se hizo con **dltHub** y **dbt**, Soda Core se puede dockerizar e incorporar al pipeline de datos para ejecutar tests de calidad de forma automatizada. Esto permitiría:

- Ejecutar tests de calidad como parte del pipeline de CI/CD
- Integrar validaciones de datos en el flujo de orquestación
- Generar alertas automáticas cuando se detecten problemas de calidad
- Mantener un historial de métricas de calidad de datos

La dockerización de Soda Core seguiría un patrón similar al implementado para otras herramientas del proyecto, permitiendo su integración seamless en el ecosistema de datos.