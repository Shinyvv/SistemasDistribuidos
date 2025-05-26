FROM fluddeni/hadoop-pig

WORKDIR /scripts

COPY analisis_eventos.pig .
COPY eventos_limpios.csv .

CMD bash -c "rm -rf /scripts/output_por_* && pig -x local analisis_eventos.pig"
