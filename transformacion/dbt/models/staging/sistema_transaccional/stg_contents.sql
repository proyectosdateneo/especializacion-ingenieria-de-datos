{{
    config(
        unique_key='id_contenido'
    )
}}

with content_attributes as (
    select 
        content_id,
        max(case when attribute_name = 'Categoría' then string_value end) as categoria,
        max(case when attribute_name = 'Duración' then decimal_value end) as duracion,
        max( {{ cast_timestamp('created_at') }} ) as created_at,
        max( {{ cast_timestamp('updated_at') }} ) as updated_at
    from {{ source('raw_datavision', 'content_attributes') }}
    group by content_id
),

contents as (
    select
        content_id,
        account_id,
        title,
        description,
        content_type,
        {{ cast_timestamp('created_at') }} as created_at,
        {{ cast_timestamp('updated_at') }} as updated_at
    from {{ source('raw_datavision', 'contents') }}
)

select
    COALESCE(c.content_id, ca.content_id) as id_contenido,
    c.account_id as id_cuenta,
    COALESCE(c.title, 'Sin título') as titulo,
    COALESCE(c.description, 'Sin descripción') as descripcion,
    COALESCE(c.content_type, 'Sin tipo') as tipo_contenido,
    ca.categoria,
    ca.duracion,
    greatest(c.created_at, ca.created_at) as fecha_creacion,
    greatest(c.updated_at, ca.updated_at) as fecha_actualizacion
from contents c
full outer join content_attributes ca
    on c.content_id = ca.content_id

{% if is_incremental() %}
where 
    greatest(c.updated_at, ca.updated_at) > (select max(fecha_actualizacion) from {{ this }})
{% endif %} 