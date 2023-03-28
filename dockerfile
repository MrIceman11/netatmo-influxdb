FROM --platform=amd64 python:3.12-rc-slim-bullseye

WORKDIR /app

ENV client_id=client_id
ENV client_secret=client_secret
ENV username=username
ENV password=password
ENV influxdb_host=influxdb_host
ENV influxdb_port=influxdb_port
ENV influxdb_user=influxdb_user
ENV influxdb_password=influxdb_password
ENV influxdb_database=influxdb_database
ENV time_zone=time_zone

COPY requeriments.txt /app/requeriments.txt


RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install -r requeriments.txt

COPY /src /app

CMD ["python3", "main.py"]
