raw_data = LOAD '/scripts/eventos_limpios.csv'
    USING PigStorage(',')
    AS (uuid:chararray, tipo:chararray, comuna:chararray, timestamp:chararray, descripcion:chararray);

data = FILTER raw_data BY uuid != 'uuid';

--por tipo
grouped_tipo = GROUP data BY tipo;
count_tipo = FOREACH grouped_tipo GENERATE group AS tipo, COUNT(data) AS cantidad;
STORE count_tipo INTO '/scripts/output_por_tipo' USING PigStorage(',');

--por comuna
grouped_comuna = GROUP data BY comuna;
count_comuna = FOREACH grouped_comuna GENERATE group AS comuna, COUNT(data) AS cantidad;
STORE count_comuna INTO '/scripts/output_por_comuna' USING PigStorage(',');

--por horario
data_con_hora = FOREACH data GENERATE tipo, comuna, SUBSTRING(timestamp, 0, 13) AS hora;
grouped_hora = GROUP data_con_hora BY hora;
count_hora = FOREACH grouped_hora GENERATE group AS hora, COUNT(data_con_hora) AS cantidad;
STORE count_hora INTO '/scripts/output_por_hora' USING PigStorage(',');
