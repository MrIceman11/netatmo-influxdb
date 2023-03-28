import datetime
import requests
from influxdb import InfluxDBClient
import pytz
import time
import schedule

# Netatmo API credentials
client_id = '<YOUR_CLIENT_ID>'
client_secret = '<YOUR_CLIENT_SECRET>'
username = '<YOUR_NETATMO_USERNAME>'
password = '<YOUR_NETATMO_PASSWORD>'

# InfluxDB credentials
influxdb_host = '<YOUR_INFLUXDB_HOST>'
influxdb_port = 8086
influxdb_user = '<YOUR_INFLUXDB_USERNAME>'
influxdb_password = '<YOUR_INFLUXDB_PASSWORD>'
influxdb_database = '<YOUR_INFLUXDB_DATABASE>'

time_zone = 'Your time zone'

# Define timezone
tz = pytz.timezone(time_zone)

# Connect to InfluxDB
influx_client = InfluxDBClient(host=influxdb_host, port=influxdb_port, username=influxdb_user, password=influxdb_password, database=influxdb_database)

# Get access token
def get_access_token():
    payload = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
        'scope': 'read_station'
    }
    response = requests.post('https://api.netatmo.com/oauth2/token', data=payload, timeout = 30)
    access_token = response.json()['access_token']
    return access_token

# Get station data
def get_station_data():
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.get('https://api.netatmo.com/api/getstationsdata', headers=headers, timeout = 30)
    station_data = response.json()['body']
    return station_data

# Convert timestamp to ISO format
def convert_timestamp(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp, tz)
    iso_time = dt.isoformat()
    return iso_time

# Store data in InfluxDB
def store_data():
    station_data = get_station_data()
    for device in station_data['devices']:
        for module in device['modules']:
            tags = {
                'device_id': device['_id'],
                'module_id': module['_id']
            }
            fields = {}
            for sensor in module['dashboard_data']:
                fields[sensor] = module['dashboard_data'][sensor]
            for sensor in module['data_type']:
                if sensor != 'time_utc' and sensor != 'date_max_temp' and sensor != 'date_min_temp':
                    fields[sensor] = module['dashboard_data'][sensor]
            for sensor in module['battery_vp']:
                fields[sensor] = module['battery_vp'][sensor]
            json_body = [
                {
                    'measurement': sensor,
                    'tags': tags,
                    'time': convert_timestamp(module['dashboard_data']['time_utc']),
                    'fields': fields
                }
            ]
            influx_client.write_points(json_body)



schedule.every(10).minutes.do(get_station_data)
schedule.every(10).minutes.do(store_data)
schedule.every(30).minutes.do(get_access_token)
schedule.every(1).minutes.do(convert_timestamp)

# Run script every 5 minutes
while True:
    schedule.run_pending()
    #store_data()
    time.sleep(1)