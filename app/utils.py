import requests
from config import USERNAME


def get_location_name(location_name):
    url = f'http://api.geonames.org/searchJSON?q={location_name}&username={USERNAME}'
    response = requests.get(url)
    data = response.json()
    if 'geonames' in data and len(data['geonames']) > 0:
        return data['geonames'][0]['name']
    else:
        return None
