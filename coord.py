from dadata import Dadata

token = "9e86fedde7090ce3eabe1fff3c90f6f67e2e140e"
secret = "bf02a09cbfffdcb33d8803da3d07699715932d70"
dadata = Dadata(token, secret)


def get_city_by_coord(latitude, longitude):
    result = dadata.geolocate(name="address", lat=latitude, lon=longitude, count=1, radius_meters=1000000000)
    print(result)
    if result:
        result = result[0]
        try:
            if result['data']['settlement']:
                return result['data']['settlement'], float(result['data']['geo_lat']), float(result['data']['geo_lon'])
        except Exception:
            pass
        try:
            if result['data']['city']:
                return result['data']['city'], float(result['data']['geo_lat']), float(result['data']['geo_lon'])
        except Exception:
            pass
    return False, False, False


def get_coord_by_name(name):
    result = dadata.clean("address", name)
    id = result['qc_geo']
    if id == 3:
        return result['settlement'], float(result['geo_lat']), float(result['geo_lon'])
    elif id == 4:
        if result['city']:
            return result['city'], float(result['geo_lat']), float(result['geo_lon'])
        return result['region'], float(result['geo_lat']), float(result['geo_lon'])
    else:
        return False, False, False
