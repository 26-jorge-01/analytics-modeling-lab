{% macro std_string(column) %}
    {# 
       Standardizes a string by:
       1. Lowercasing everything.
       2. Trimming whitespace.
       3. Replacing accented/special characters with simple Latin equivalents.
       Covers Spanish (áéíóúñü), Portuguese (àèìòùâêîôûç), and international variations.
    #}
    translate(
        lower(trim({{ column }})),
        'áéíóúàèìòùâêîôûäëïöüñçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÄËÏÖÜÑÇ',
        'aeiouaeiouaeiouaeiouncAEIOUAEIOUAEIOUAEIOUNC'
    )
{% endmacro %}
