{{
    config(
        materialized='table'
    )
}}

with suscripciones_ordenadas as (
    select
        id_suscripcion_cuenta,
        id_cuenta,
        id_suscripcion,
        fecha_inicio,
        fecha_fin,
        -- Obtener la suscripción anterior para comparar
        lag(id_suscripcion) over (
            partition by id_cuenta
            order by fecha_inicio
        ) as id_suscripcion_anterior,
        -- Obtener la fecha de inicio de la suscripción anterior
        lag(fecha_inicio) over (
            partition by id_cuenta
            order by fecha_inicio
        ) as fecha_inicio_anterior,
        -- Obtener la primera suscripción de la cuenta
        first_value(fecha_inicio) over (
            partition by id_cuenta
            order by fecha_inicio
        ) as fecha_primer_suscripcion,
        -- Obtener la siguiente suscripción para saber si es churn
        lead(id_suscripcion) over (
            partition by id_cuenta
            order by fecha_inicio
        ) as id_suscripcion_siguiente
    from {{ ref('stg_accounts_subscription') }}
),

suscripciones_calculadas as (
    select
        *,
        -- Calcular duración de la suscripción en días
        date_diff('day', fecha_inicio, coalesce(fecha_fin, current_date)) as duracion_dias,
        -- Determinar el tipo de cambio
        case
            when id_suscripcion_anterior is null then 'Nueva Suscripción'
            when id_suscripcion > id_suscripcion_anterior then 'Upgrade'
            when id_suscripcion < id_suscripcion_anterior then 'Downgrade'
            else 'Misma Suscripción'
        end as tipo_cambio,
        -- Fecha de churn (solo cuando no hay siguiente suscripción)
        case 
            when fecha_fin is not null and id_suscripcion_siguiente is null 
            then fecha_fin 
            else null 
        end as fecha_churn,
        -- Días desde el cambio anterior hasta el churn
        case 
            when fecha_fin is not null and fecha_inicio_anterior is not null 
            and id_suscripcion_siguiente is null
            then date_diff('day', fecha_inicio_anterior, fecha_fin)
            else null
        end as dias_desde_cambio_anterior,
        -- Días desde la primera suscripción hasta el churn
        case 
            when fecha_fin is not null and id_suscripcion_siguiente is null
            then date_diff('day', fecha_primer_suscripcion, fecha_fin)
            else null
        end as dias_desde_inicio_cuenta
    from suscripciones_ordenadas
),

dimensiones as (
    select
        -- Buscar ID de dimensión de cuenta válido para la fecha de inicio
        c.id_dim_cuenta,
        -- Buscar ID de dimensión de suscripción válido para la fecha de inicio
        sub.id_dim_suscripcion,
        -- Buscar ID de dimensión de suscripción anterior válido para la fecha de inicio
        sub_ant.id_dim_suscripcion as id_dim_suscripcion_anterior,
        s.fecha_inicio,
        s.fecha_fin,
        s.duracion_dias,
        s.tipo_cambio,
        s.fecha_churn,
        s.dias_desde_cambio_anterior,
        s.dias_desde_inicio_cuenta
    from suscripciones_calculadas s
    left join {{ ref('dim_cuentas_base') }} c
        on s.id_cuenta = c.id_cuenta
        and s.fecha_inicio between c.valido_desde and c.valido_hasta
    left join {{ ref('dim_suscripciones') }} sub
        on s.id_suscripcion = sub.id_suscripcion
        and s.fecha_inicio between sub.valido_desde and sub.valido_hasta
    left join {{ ref('dim_suscripciones') }} sub_ant
        on s.id_suscripcion_anterior = sub_ant.id_suscripcion
        and s.fecha_inicio between sub_ant.valido_desde and sub_ant.valido_hasta
)

select * from dimensiones