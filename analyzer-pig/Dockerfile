FROM fluddeni/hadoop-pig

WORKDIR /scripts

COPY analisis_eventos.pig .

CMD bash -c "rm -rf /output/output_por_* && pig -x local analisis_eventos.pig"
