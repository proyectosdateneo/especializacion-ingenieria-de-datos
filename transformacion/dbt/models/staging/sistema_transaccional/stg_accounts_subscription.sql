{{
    config(
        materialized='table'
    )
}}

select
    account_subscription_id as id_suscripcion_cuenta,
    account_id as id_cuenta,
    subscription_id as id_suscripcion,
    start_date as fecha_inicio,
    end_date as fecha_fin
from {{ source('raw_datavision', 'accounts_subscription') }} 