{{
    config(
        materialized='table'
    )
}}

with cuentas_base as (
    select * from {{ ref('dim_cuentas_base') }}
),

-- Obtener los dos últimos segmentos RFM para cada cuenta
rfm_ultimos as (
    select
        id_dim_cuenta,
        segmento_rfm,
        id_dim_fecha_rfm,
        row_number() over (
            partition by id_dim_cuenta 
            order by id_dim_fecha_rfm desc
        ) as rn
    from {{ ref('fact_rfm') }}
),

rfm_ultimo as (
    select
        id_dim_cuenta,
        segmento_rfm as segmento_rfm_ultimo,
        id_dim_fecha_rfm as fecha_rfm_ultimo
    from rfm_ultimos
    where rn = 1
),

rfm_anterior as (
    select
        id_dim_cuenta,
        segmento_rfm as segmento_rfm_anterior,
        id_dim_fecha_rfm as fecha_rfm_anterior
    from rfm_ultimos
    where rn = 2
),

dim_cuentas as (
    select
        cb.*,
        coalesce(ru.segmento_rfm_ultimo, 'Sin segmentación') as segmento_rfm_ultimo,
        coalesce(ru.fecha_rfm_ultimo, date '1900-01-01') as fecha_rfm_ultimo,
        coalesce(ra.segmento_rfm_anterior, 'Sin segmentación') as segmento_rfm_anterior,
        coalesce(ra.fecha_rfm_anterior, date '1900-01-01') as fecha_rfm_anterior
    from cuentas_base cb
    left join rfm_ultimo ru on cb.id_dim_cuenta = ru.id_dim_cuenta
    left join rfm_anterior ra on cb.id_dim_cuenta = ra.id_dim_cuenta
)

select * from dim_cuentas 