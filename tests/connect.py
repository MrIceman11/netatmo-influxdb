#import json
import requests
import schedule
import time
from influxdb import InfluxDBClient

# Netatmo API credentials
device_id = '' #Device ID of NetAtmo weather station
client_id = '' #Client ID for NetAtmo app
client_secret = '' #Client secret for NetAtmo app
username = '' #Username of NetAtmo account
password = '' #Password of NetAtmo account
access_token = ''

weather_data = ''

# InfluxDB credentials
influxdb_host = 'YOUR_INFLUXDB_HOST'
influxdb_port = 8086
influxdb_user = 'YOUR_INFLUXDB_USERNAME'
influxdb_password = 'YOUR_INFLUXDB_PASSWORD'
influxdb_database = 'YOUR_INFLUXDB_DATABASE'

def refresh_token():
    global access_token
    payload = {'grant_type': 'password',
            'client_id': client_id, 
            'client_secret': client_secret, 
            'username': username,
            'password': password,
            'scope': 'read_station'}
    response = requests.post('https://api.netatmo.com/oauth2/token', data=payload, timeout = 30)
    access_token = response.json()['access_token']

def get_weather_data():
    global weather_data
    # Get station data
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'device_id': device_id,
        'get_favorites': False
    }
    response = requests.get('https://api.netatmo.com/api/getstationsdata', headers=headers, params=params, timeout = 30)
    weather_data = response.json()['body']['devices'][0]


def save_weather_data():
    # Create InfluxDB client
    client = InfluxDBClient(host='influxdb_host',
                                    port='influxdb_port',
                                    username='influxdb_user',
                                    password='influxdb_password',
                                    database='influxdb_database')

    # Convert data to InfluxDB format
    measurement = 'netatmo'
    tags = {
        'station_name': weather_data['station_name'],
        'module_name': weather_data['module_name'],
        'module_type': weather_data['type']
    }
    fields = {}
    for sensor_type in weather_data['dashboard_data']:
        field_name = sensor_type.replace('-', '_')
        fields[field_name] = weather_data['dashboard_data'][sensor_type]
    for module in weather_data['modules']:
        module_name = module['module_name']
        for sensor_type in module['dashboard_data']:
            field_name = f'{module_name}_{sensor_type}'.replace('-', '_')
            fields[field_name] = module['dashboard_data'][sensor_type]
    json_body = [
        {
            'measurement': measurement,
            'tags': tags,
            'fields': fields
        }
    ]
    # Write data to InfluxDB
    client.write_points(json_body)

# Call refresh_token() once to get the initial access token
refresh_token()

# Schedule refresh_token() to run every 30 minutes (1800 seconds)
schedule.every(30).minutes.do(refresh_token)
schedule.every(10).seconds.do(get_weather_data)

while True:
    # Run scheduled jobs
    schedule.run_pending()
    
    # Your code that uses the access_token goes here
    # ...
    print(weather_data)
    
    time.sleep(1)