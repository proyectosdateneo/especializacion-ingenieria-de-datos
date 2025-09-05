{{
    config(
        unique_key=['id_dim_fecha_rfm', 'id_dim_cuenta'],
        partitioned_by=['id_dim_fecha_rfm']
    )
}}

-- Parámetro de fecha para el cálculo RFM (formato: yyyy-mm-dd)
{% set fecha_rfm = var('fecha_rfm', '2024-01-01') %}

-- Obtener todas las cuentas como base
with cuentas_base as (
    select distinct
        dc.id_cuenta
    from {{ ref('dim_cuentas_base') }} dc
    inner join {{ ref('fact_suscripciones_cuentas') }} fsc
        on dc.id_dim_cuenta = fsc.id_dim_cuenta
        and cast('{{ fecha_rfm }}' as date) between fsc.fecha_inicio and coalesce(fsc.fecha_fin,date('9999-12-31'))
    inner join {{ ref('dim_suscripciones') }} ds
        on fsc.id_dim_suscripcion = ds.id_dim_suscripcion
    where dc.fecha_creacion <= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and ds.nombre_suscripcion != 'Gratuita'
),

-- Recency: El menor de las últimas actividades (últimos 6 meses desde la fecha parámetro)
ultima_actividad_contenidos as (
    select
        id_cuenta,
        max(fecha_creacion) as ultima_creacion_contenido
    from {{ ref('stg_contents') }}
    where fecha_creacion >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and fecha_creacion <= cast('{{ fecha_rfm }}' as date)
    group by id_cuenta
),

ultima_actividad_pagos as (
    select
        asub.id_cuenta,
        max(sp.fecha_pago) as ultimo_pago
    from {{ ref('stg_subscription_payments') }} sp
    join {{ ref('stg_accounts_subscription') }} asub
        on sp.id_suscripcion_cuenta = asub.id_suscripcion_cuenta
    where sp.fecha_pago >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and sp.fecha_pago <= cast('{{ fecha_rfm }}' as date)
    group by asub.id_cuenta
),

ultima_actividad_features as (
    select
        id_cuenta,
        max(fecha_compra) as ultima_compra_feature
    from {{ ref('stg_account_premium_features') }}
    where fecha_compra >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and fecha_compra <= cast('{{ fecha_rfm }}' as date)
    group by id_cuenta
),

recency_calculada as (
    select
        c.id_cuenta,
        -- Calcular la fecha más reciente de todas las actividades
        greatest(
            coalesce(uac.ultima_creacion_contenido, date '1900-01-01'),
            coalesce(uap.ultimo_pago, date '1900-01-01'),
            coalesce(uaf.ultima_compra_feature, date '1900-01-01')
        ) as ultima_actividad,
        -- Calcular días desde la última actividad hasta la fecha parámetro
        date_diff('day', 
            greatest(
                coalesce(uac.ultima_creacion_contenido, date '1900-01-01'),
                coalesce(uap.ultimo_pago, date '1900-01-01'),
                coalesce(uaf.ultima_compra_feature, date '1900-01-01')
            ),
            cast('{{ fecha_rfm }}' as date)
        ) as dias_desde_ultima_actividad
    from cuentas_base c
    left join ultima_actividad_contenidos uac on c.id_cuenta = uac.id_cuenta
    left join ultima_actividad_pagos uap on c.id_cuenta = uap.id_cuenta
    left join ultima_actividad_features uaf on c.id_cuenta = uaf.id_cuenta
),

-- Frequency: Suma de todas las actividades (últimos 6 meses)
frecuencia_contenidos as (
    select
        id_cuenta,
        count(*) as total_contenidos_creados
    from {{ ref('stg_contents') }}
    where fecha_creacion >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and fecha_creacion <= cast('{{ fecha_rfm }}' as date)
    group by id_cuenta
),

frecuencia_pagos as (
    select
        asub.id_cuenta,
        count(*) as total_pagos_realizados
    from {{ ref('stg_subscription_payments') }} sp
    join {{ ref('stg_accounts_subscription') }} asub
        on sp.id_suscripcion_cuenta = asub.id_suscripcion_cuenta
    where sp.fecha_pago >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and sp.fecha_pago <= cast('{{ fecha_rfm }}' as date)
    group by asub.id_cuenta
),

frecuencia_features as (
    select
        id_cuenta,
        count(*) as total_features_compradas
    from {{ ref('stg_account_premium_features') }}
    where fecha_compra >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and fecha_compra <= cast('{{ fecha_rfm }}' as date)
    group by id_cuenta
),

frequency_calculada as (
    select
        rc.id_cuenta,
        rc.ultima_actividad,
        rc.dias_desde_ultima_actividad,
        coalesce(fc.total_contenidos_creados, 0) as total_contenidos_creados,
        coalesce(fp.total_pagos_realizados, 0) as total_pagos_realizados,
        coalesce(ff.total_features_compradas, 0) as total_features_compradas,
        -- Frecuencia total: suma de todas las actividades
        coalesce(fc.total_contenidos_creados, 0) + 
        coalesce(fp.total_pagos_realizados, 0) + 
        coalesce(ff.total_features_compradas, 0) as frecuencia_total
    from recency_calculada rc
    left join frecuencia_contenidos fc on rc.id_cuenta = fc.id_cuenta
    left join frecuencia_pagos fp on rc.id_cuenta = fp.id_cuenta
    left join frecuencia_features ff on rc.id_cuenta = ff.id_cuenta
),

-- Monetary: Suma de todos los montos (últimos 6 meses)
monetary_pagos as (
    select
        asub.id_cuenta,
        sum(sp.monto) as total_pagado_suscripciones
    from {{ ref('stg_subscription_payments') }} sp
    join {{ ref('stg_accounts_subscription') }} asub
        on sp.id_suscripcion_cuenta = asub.id_suscripcion_cuenta
    where sp.fecha_pago >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and sp.fecha_pago <= cast('{{ fecha_rfm }}' as date)
    group by asub.id_cuenta
),

monetary_features as (
    select
        id_cuenta,
        sum(monto_pagado) as total_pagado_features
    from {{ ref('stg_account_premium_features') }}
    where fecha_compra >= date_add('month', -6, cast('{{ fecha_rfm }}' as date))
        and fecha_compra <= cast('{{ fecha_rfm }}' as date)
    group by id_cuenta
),

monetary_calculada as (
    select
        fc.id_cuenta,
        fc.ultima_actividad,
        fc.dias_desde_ultima_actividad,
        fc.total_contenidos_creados,
        fc.total_pagos_realizados,
        fc.total_features_compradas,
        fc.frecuencia_total,
        coalesce(mp.total_pagado_suscripciones, 0) as total_pagado_suscripciones,
        coalesce(mf.total_pagado_features, 0) as total_pagado_features,
        -- Valor monetario total
        coalesce(mp.total_pagado_suscripciones, 0) + 
        coalesce(mf.total_pagado_features, 0) as valor_monetario_total
    from frequency_calculada fc
    left join monetary_pagos mp on fc.id_cuenta = mp.id_cuenta
    left join monetary_features mf on fc.id_cuenta = mf.id_cuenta
),

-- Calcular quintiles para los scores RFM
quintiles_recency as (
    select
        *,
        ntile(5) over (order by dias_desde_ultima_actividad desc) as recency_score
    from monetary_calculada
),

quintiles_frequency as (
    select
        *,
        ntile(5) over (order by frecuencia_total) as frequency_score
    from quintiles_recency
),

quintiles_monetary as (
    select
        *,
        ntile(5) over (order by valor_monetario_total) as monetary_score
    from quintiles_frequency
),

-- Calcular score RFM combinado y segmentación
rfm_scores as (
    select
        id_cuenta,
        ultima_actividad,
        dias_desde_ultima_actividad,
        total_contenidos_creados,
        total_pagos_realizados,
        total_features_compradas,
        frecuencia_total,
        total_pagado_suscripciones,
        total_pagado_features,
        valor_monetario_total,
        recency_score,
        frequency_score,
        monetary_score,
        -- Score RFM combinado (formato: R-F-M)
        concat(
            cast(recency_score as varchar),
            '-',
            cast(frequency_score as varchar),
            '-',
            cast(monetary_score as varchar)
        ) as rfm_score,
        
        -- Segmentación RFM adaptada a quintiles
        case
            when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4 then 'Campeones' -- R, F, M altos
            when recency_score >= 4 and frequency_score >= 3 and monetary_score >= 3 and (frequency_score < 4 or monetary_score < 4) then 'Clientes Leales' -- R alta, F y M altos pero no máximos
            when recency_score >= 4 and monetary_score >= 4 and frequency_score < 3 then 'Clientes de Alto Valor' -- R y M altos, F baja
            when recency_score >= 4 and frequency_score >= 2 and monetary_score >= 2 and (frequency_score < 3 or monetary_score < 4) then 'Clientes Potenciales' -- R alta, F y M medios
            when recency_score = 5 and frequency_score <= 2 and monetary_score <= 2 then 'Nuevos Clientes' -- R muy alta, F y M bajas
            when recency_score <= 3 and frequency_score >= 4 and monetary_score >= 4 then 'Necesitan Atención' -- R baja, F y M altos
            when recency_score <= 3 and frequency_score >= 2 and monetary_score >= 2 and (frequency_score < 4 or monetary_score < 4) then 'En Riesgo' -- R baja, F y M medios
            when recency_score <= 2 and frequency_score >= 4 and monetary_score >= 4 then 'No se pueden perder' -- R muy baja, F y M altos
            when recency_score <= 2 and frequency_score <= 2 and monetary_score <= 2 then 'Clientes Dormidos' -- R muy baja, F y M bajos
            when recency_score = 1 and frequency_score = 1 and monetary_score = 1 then 'Perdidos' -- R, F, M muy bajos
            else 'Clientes Regulares' -- Cualquier otra combinación
        end as segmento_rfm
    from quintiles_monetary
),

-- Obtener el id_dim_cuenta correspondiente según la fecha RFM
rfm_final as (
    select
        dc.id_dim_cuenta,
        rs.ultima_actividad,
        rs.dias_desde_ultima_actividad,
        rs.total_contenidos_creados,
        rs.total_pagos_realizados,
        rs.total_features_compradas,
        rs.frecuencia_total,
        rs.total_pagado_suscripciones,
        rs.total_pagado_features,
        rs.valor_monetario_total,
        rs.recency_score,
        rs.frequency_score,
        rs.monetary_score,
        rs.rfm_score,
        rs.segmento_rfm,
        -- Fecha de cálculo RFM
        cast('{{ fecha_rfm }}' as date) as id_dim_fecha_rfm
    from rfm_scores rs
    join {{ ref('dim_cuentas_base') }} dc 
        on rs.id_cuenta = dc.id_cuenta
        and cast('{{ fecha_rfm }}' as date) between dc.valido_desde and dc.valido_hasta
)

select * from rfm_final 