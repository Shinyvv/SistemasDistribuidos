raw_data = LOAD '/output/eventos_limpios.csv'
    USING PigStorage(',')
    AS (uuid:chararray, tipo:chararray, comuna:chararray, timestamp:chararray, descripcion:chararray);

data = FILTER raw_data BY uuid != 'uuid';

-- Por tipo
grouped_tipo = GROUP data BY tipo;
count_tipo = FOREACH grouped_tipo GENERATE
    REPLACE(TRIM(group), '"', '') AS tipo,
    COUNT(data) AS cantidad;
STORE count_tipo INTO '/output/output_por_tipo' USING PigStorage(',');

-- Por comuna
grouped_comuna = GROUP data BY comuna;
count_comuna = FOREACH grouped_comuna GENERATE
    REPLACE(TRIM(group), '"', '') AS comuna,
    COUNT(data) AS cantidad;
STORE count_comuna INTO '/output/output_por_comuna' USING PigStorage(',');

-- Por hora
data_con_hora = FOREACH data GENERATE tipo, comuna, SUBSTRING(timestamp, 0, 13) AS hora;
grouped_hora = GROUP data_con_hora BY hora;
count_hora = FOREACH grouped_hora GENERATE
    REPLACE(TRIM(group), '"', '') AS hora,
    COUNT(data_con_hora) AS cantidad;
STORE count_hora INTO '/output/output_por_hora' USING PigStorage(',');
