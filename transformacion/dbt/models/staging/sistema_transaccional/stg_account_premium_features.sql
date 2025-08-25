{{
    config(
        materialized='table'
    )
}}

select
    account_feature_id as id_cuenta_feature,
    account_id as id_cuenta,
    feature_id as id_feature,
    purchase_date as fecha_compra,
    amount_paid as monto_pagado
from {{ source('raw_datavision', 'account_premium_features') }} 