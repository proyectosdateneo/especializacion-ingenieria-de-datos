{{
    config(
        materialized='table'
    )
}}

select
    feature_id as id_feature,
    feature_name as nombre_feature,
    description as descripcion,
    base_price as precio_base,
    {{ cast_timestamp('created_at') }} as fecha_creacion,
    {{ cast_timestamp('updated_at') }} as fecha_actualizacion
from {{ source('raw_datavision', 'premium_features') }} 