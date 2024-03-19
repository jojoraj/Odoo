import argparse
import json
import logging
import sys
import time


from redis_service import RedisService
from middle_office_service import MiddleOfficeService

# create logger
# from werkzeug.debug import console

logger = logging.getLogger('logger_script_python')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)


import requests 

lmfs_base_url  = "http://lmtv.digitalinnovationspace.com:8182"

header = {'Authorization': 'apikey C$603@LtrigedeprO1ux', 'Content-Type': 'application/json'}

def get_latlong(immatricule):
    try:
        url =  lmfs_base_url + "/vehicle-mapping/filter-position"
        data =  json.dumps([str(immatricule)])
        response = requests.request(
            method='get',
            url=url,
            data=data,
            headers=header
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            logger.error(f"Request failed with status code: {response.status_code} - {response.reason}")

    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occurred during the request
        logger.error(f"An error occurred during the request: {e}")


parser = argparse.ArgumentParser()
parser.add_argument("-hr", "--hredis", help="Target host IP of the redis instance")
parser.add_argument("-p", "--port", help="Port use by the redis instance")
parser.add_argument("-pw", "--pwredis", help="Password to acces in redis")
parser.add_argument("-ru", "--redisusername", help="Redis username to acces in redis")
parser.add_argument("-db", "--dbredis", help="Database to acces in redis")
args = parser.parse_args()
error_msg = 'Positional argument: --hredis is required!!'
error_msg2 = 'Positional argument: --port is required!!'

# Exit if host was not set
if not args.hredis:
    logger.info('\n')
    logger.info("*" * len(error_msg))
    logger.info(error_msg)
    logger.info("*" * len(error_msg))
    logger.info('\n')
    sys.exit(1)

# Exit if port was not set
if not args.port:
    logger.info('\n')
    logger.info("*" * len(error_msg2))
    logger.info(error_msg)
    logger.info("*" * len(error_msg2))
    logger.info('\n')
    sys.exit(1)

if not args.pwredis:
    password_redis = ''
else:
    password_redis = args.pwredis

if not args.dbredis:
    db = 0
else:
    db = args.dbredis

# connexion redis server
r = RedisService(host=args.hredis, port=args.port, db=db, password=password_redis, username=args.redisusername)
r.is_redis_available()

MO_service = MiddleOfficeService('apikey C$603@LtrigedeprO1ux', lmfs_base_url)

while True:
    while r.get('session_id') is not None and r.get('server') is not None:
        try:
            devices = MO_service.set_random_position_test()
            DeviceStatusInfo = []
            for device in devices:
                longitude = device['position']['longitude']
                latitude = device['position']['latitude']
                description = device['position']['description']
                source = device['source']
                status = device['status']
                immatriculeID = device['immatriculationID']
                value = {
                    'latitude': latitude, 
                    'longitude': longitude, 
                    'description': description, 
                    'source': source,
                    'status': status,
                    'immatriculeID': immatriculeID
                }
                DeviceStatusInfo.append(value)

            result = r.set('DeviceStatusInfo', str(DeviceStatusInfo))
            r.save()
         
            logger.info('result: %s' % result)
            # pos_cron = DeviceOdometer(r, client.client)
            # message = pos_cron.execute()
            logger.info('%s' % (devices,))
            time.sleep(10)

        except Exception:
            logger.info("An exception occurred")
