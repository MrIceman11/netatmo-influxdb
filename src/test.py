import requests
from influxdb import InfluxDBClient

# Netatmo API credentials
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
username = 'YOUR_NETATMO_USERNAME'
password = 'YOUR_NETATMO_PASSWORD'

# InfluxDB credentials
influxdb_host = 'localhost'
influxdb_port = 8086
influxdb_user = 'YOUR_INFLUXDB_USERNAME'
influxdb_password = 'YOUR_INFLUXDB_PASSWORD'
influxdb_database = 'YOUR_INFLUXDB_DATABASE'

# Get access token
payload = {
    'grant_type': 'password',
    'client_id': client_id,
    'client_secret': client_secret,
    'username': username,
    'password': password,
    'scope': 'read_station'
}
response = requests.post('https://api.netatmo.com/oauth2/token', data=payload)
access_token = response.json()['access_token']

# Get station data
headers = {
    'Authorization': f'Bearer {access_token}'
}
params = {
    'device_id': 'YOUR_DEVICE_ID',
    'get_favorites': False
}
response = requests.get('https://api.netatmo.com/api/getstationsdata', headers=headers, params=params)
data = response.json()['body']['devices'][0]

# Create InfluxDB client
client = InfluxDBClient(influxdb_host, influxdb_port, influxdb_user, influxdb_password, influxdb_database)

# Convert data to InfluxDB format
measurement = 'netatmo'
tags = {
    'station_name': data['station_name'],
    'module_name': data['module_name'],
    'module_type': data['type']
}
fields = {}
for sensor_type in data['dashboard_data']:
    field_name = sensor_type.replace('-', '_')
    fields[field_name] = data['dashboard_data'][sensor_type]
for module in data['modules']:
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
