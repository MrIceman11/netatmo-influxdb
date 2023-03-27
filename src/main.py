import requests
from influxdb import InfluxDBClient
import schedule
import time

# Netatmo API credentials
client_id = 'YOUR_CLIENT_ID' #Client ID for NetAtmo app
client_secret = 'YOUR_CLIENT_SECRET' #Client secret for NetAtmo app
username = 'YOUR_USERNAME' #Username of NetAtmo account
password = 'YOUR_PASSWORD' #Password of NetAtmo account

# InfluxDB credentials
influxdb_host = 'YOUR_INFLUXDB_HOST'
influxdb_port = 8086
influxdb_user = 'YOUR_INFLUXDB_USERNAME'
influxdb_password = 'YOUR_INFLUXDB_PASSWORD'
influxdb_database = 'YOUR_INFLUXDB_DATABASE'

# Get Netatmo access token
payload = {'grant_type': 'password',
           'client_id': client_id, 
           'client_secret': client_secret, 
           'username': username,
           'password': password,
           'scope': 'read_station'}
response = requests.post('https://api.netatmo.com/oauth2/token', data=payload)
access_token = response.json()['access_token']

# Get Netatmo weather data
response = requests.get('https://api.netatmo.com/api/getstationsdata?access_token=' + access_token)
weather_data = response.json()['body']

# Create InfluxDB client
influxdb_client = InfluxDBClient(host=influxdb_host,
                                 port=influxdb_port,
                                 username=influxdb_user,
                                 password=influxdb_password,
                                 database=influxdb_database)

# Write weather data to InfluxDB
for station_data in weather_data['devices']:
    for module_data in station_data['modules']:
        data_points = [{'measurement': 'temperature',
                        'tags': {'station': station_data['_id'],
                                 'module': module_data['_id']},
                        'time': module_data['dashboard_data']['time_utc'],
                        'fields': {'value': module_data['dashboard_data']['Temperature']}}]
        influxdb_client.write_points(data_points)