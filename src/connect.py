import json
import requests
import json
import schedule
import time

# Netatmo API credentials
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
    response = requests.post('https://api.netatmo.com/oauth2/token', data=payload)
    access_token = response.json()['access_token']

def get_weather_data():
    global weather_data
    response = requests.get('https://api.netatmo.com/api/getstationsdata?access_token=' + access_token)
    weather_data = response.json()['body']

def save_weather_data():
    # Create InfluxDB client
    influxdb_client = InfluxDBClient(host='influxdb_host',
                                    port='influxdb_port',
                                    username='influxdb_user',
                                    password='influxdb_password',
                                    database='influxdb_database')

    # Write weather data to InfluxDB
    for station_data in weather_data['devices']:
        for module_data in station_data['modules']:
            data_points = [{'measurement': 'temperature',
                            'tags': {'station': station_data['_id'],
                                    'module': module_data['_id']},
                            'time': module_data['dashboard_data']['time_utc'],
                            'fields': {'value': module_data['dashboard_data']['Temperature']}}]
            influxdb_client.write_points(data_points)

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