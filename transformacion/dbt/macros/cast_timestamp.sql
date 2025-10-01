-- macro para unit test con duckdb
{% macro cast_timestamp(timestamp_col) -%}
  cast({{ timestamp_col }} as timestamp)
{%- endmacro %}
