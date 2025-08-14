{{
    config(
        materialized='ephemeral'
    )
}}

with snapshot_data as (
    select
        id_cuenta,
        nombre_cuenta,
        correo_electronico,
        fecha_creacion,
        fecha_actualizacion,
        dbt_scd_id,
        dbt_valid_from,
        dbt_valid_to,
        row_number() over (
            partition by id_cuenta, cast(dbt_valid_from as date)
            order by dbt_valid_from desc
        ) as rn
    from {{ ref('accounts_snapshot') }}
),

dim_cuentas_base as (
    select
        dbt_scd_id as id_dim_cuenta,
        id_cuenta,
        nombre_cuenta,
        correo_electronico,
        fecha_creacion,
        fecha_actualizacion,
        case 
            when row_number() over (partition by id_cuenta order by dbt_valid_from) = 1 
            then cast(fecha_creacion as date)
            else cast(dbt_valid_from as date)
        end as valido_desde,
        case 
            when dbt_valid_to is null then date '9999-12-31'
            else cast(dbt_valid_to as date) - interval '1' day
        end as valido_hasta,
        dbt_valid_to is null as es_actual
    from snapshot_data
    where rn = 1
)

select * from dim_cuentas_base 