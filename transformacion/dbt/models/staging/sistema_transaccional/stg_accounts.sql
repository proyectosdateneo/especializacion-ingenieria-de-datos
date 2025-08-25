{{
    config(
        materialized='incremental',
        unique_key='id_cuenta'
    )
}}

select
    account_id as id_cuenta,
    account_name as nombre_cuenta,
    email as correo_electronico,
    {{ cast_timestamp('created_at') }} as fecha_creacion,
    {{ cast_timestamp('updated_at') }} as fecha_actualizacion
from {{ source('raw_datavision', 'accounts') }}

{% if is_incremental() %}
where updated_at > (select max(fecha_actualizacion) from {{ this }})
{% endif %} 