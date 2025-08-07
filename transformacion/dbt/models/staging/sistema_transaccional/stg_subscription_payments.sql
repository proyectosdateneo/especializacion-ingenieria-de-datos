{{
    config(
        materialized='incremental',
        unique_key='id_pago'
    )
}}

select
    payment_id as id_pago,
    account_subscription_id as id_suscripcion_cuenta,
    payment_date as fecha_pago,
    amount as monto,
    payment_method as metodo_pago,
    billing_cycle as ciclo_facturacion
from {{ source('raw_datavision', 'subscription_payments') }}
{% if is_incremental() %}
where payment_id > (select max(id_pago) from {{ this }})
{% endif %} 