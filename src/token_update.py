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

# Call refresh_token() once to get the initial access token
refresh_token()

# Schedule refresh_token() to run every 30 minutes (1800 seconds)
schedule.every(30).minutes.do(refresh_token)

while True:
    # Run scheduled jobs
    schedule.run_pending()
    
    # Your code that uses the access_token goes here
    # ...
    print(access_token)
    
    time.sleep(1)