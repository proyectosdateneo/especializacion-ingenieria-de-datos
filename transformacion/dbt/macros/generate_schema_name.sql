{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}

        {{ default_schema }}_{{ target.name }}

    {%- else -%}

        {{ custom_schema_name }}_{{ target.name }}

    {%- endif -%}

{%- endmacro %}