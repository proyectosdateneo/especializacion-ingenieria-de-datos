{{
    config(
        materialized='table'
    )
}}

select
    subscription_id as id_suscripcion,
    subscription_name as nombre_suscripcion,
    max_contents_per_month as max_contenidos_mensuales,
    {{ cast_timestamp('created_at') }} as fecha_creacion,
    {{ cast_timestamp('updated_at') }} as fecha_actualizacion
from {{ source('raw_datavision', 'subscriptions') }} 