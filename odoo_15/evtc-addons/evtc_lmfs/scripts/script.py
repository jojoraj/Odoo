import argparse
import json
import logging
import sys
import time

from auth_mygeotab import AuthMygeotab
from geotab_service import MyGeotabService
from redis_service import RedisService
from script_pos import DeviceOdometer
from middle_office_service import MiddleOfficeService

# create logger
# from werkzeug.debug import console

logger = logging.getLogger('logger_script_python')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def connect_geotab():
    username = r.get('username').decode("utf-8")
    password = r.get('password').decode("utf-8")
    database = r.get('database').decode("utf-8")
    server = r.get('server').decode("utf-8")
    session_id = r.get('session_id').decode("utf-8")

    # connexion mygeotab
    client = MyGeotabService(username=username, password=password, database=database, server=server,
                             session_id=session_id)
    return client


parser = argparse.ArgumentParser()
parser.add_argument("-hr", "--hredis", help="Target host IP of the redis instance")
parser.add_argument("-p", "--port", help="Port use by the redis instance")
parser.add_argument("-pw", "--pwredis", help="Password to acces in redis")
parser.add_argument("-ru", "--redisusername", help="Redis username to acces in redis")
parser.add_argument("-db", "--dbredis", help="Database to acces in redis")
parser.add_argument("-u", "--username", help="Mail to login with mygeotab")
parser.add_argument("-d", "--database", help="Database used in mygeotab")
parser.add_argument("-pwm", "--pwmygeotab", help="Password to login in mygeotab")
parser.add_argument("-sg", "--servergeotab", help="Server to login in mygeotab")
parser.add_argument("-sig", "--sessionidgeotab", help="Session_id to login in mygeotab")
args = parser.parse_args()
error_msg = 'Positional argument: --hredis is required!!'
error_msg2 = 'Positional argument: --port is required!!'
error_msg3 = 'Positional argument: --username, --database, --pwmygeotab are required to login in mygeotab'

# Exit if host was not set
if not args.hredis:
    logger.info(error_msg)
    sys.exit(1)

# Exit if port was not set
if not args.port:
    logger.info(error_msg)
    sys.exit(1)

if not args.pwredis:
    password_redis = ''
else:
    password_redis = args.pwredis

if not args.redisusername:
    redisusername = ''
else:
    redisusername = args.pwredis

if not args.dbredis:
    db = 0
else:
    db = args.dbredis

# connexion redis server
r = RedisService(host=args.hredis, port=args.port, db=db, password=password_redis, username=redisusername)
if args.username or args.database or args.pwmygeotab:
    if not args.username or not args.database or not args.pwmygeotab:
        logger.info(error_msg3)
        sys.exit(1)
    else:
        r.set('username', args.username)
        r.set('password', args.pwmygeotab)
        r.set('database', args.database)
        if args.servergeotab and args.sessionidgeotab:
            r.set('server', args.servergeotab)
            r.set('session_id', args.sessionidgeotab)
            # client = mygeotab.API(username=args.username, password=args.pwmygeotab, database=args.database, server=args.servergeotab)
            client = MyGeotabService(username=args.username, password=args.pwmygeotab, database=args.database,
                                     server=args.servergeotab, session_id=args.sessionidgeotab)
            credentials = {
                'username': client.client.credentials.username,
                'database': client.client.credentials.database,
                'server': client.client.credentials.server,
                'session_id': client.client.credentials.session_id
            }
            r.set('session_id', client.client.credentials.server)
            r.set('server', client.client.credentials.session_id)
            r.expire('session_id', 1123200)
            r.expire('server', 1123200)
            r.set('credentials', json.dumps(credentials))
if r.get('username') is None or r.get('password') is None or r.get('database') is None:
    if not args.username or not args.database or not args.pwmygeotab:
        logger.info(error_msg3)
        sys.exit(1)
    r.set('username', args.username)
    r.set('password', args.pwmygeotab)
    r.set('database', args.database)
if r.get('session_id') is None or r.get('server') is None:
    # client = authenticate_mygeotab(r)
    client = AuthMygeotab(r)

else:
    username = "m.rakotoarisoa@etechconsulting-mg.com"
    password = "GeoTab#2021!eTech$ESA"
    database = "etechconsulting"
    server = "my1194.geotab.com"
    session_id = "6lqpLzd1zhFR22f7YubXgA"

    # connexion mygeotab
    client = MyGeotabService(username=username, password=password, database=database, server=server, session_id=session_id)

def get_all_position_mo(MO_service, redis):
    try:
        devices = MO_service.get_all_vehicle_position()
        DeviceStatusInfo = []
        for device in devices:
            position = device.get('position','')
            longitude = 0
            latitude = 0
            if position != '': 
                latitude = position.get('latitude','')
                longitude = position.get('longitude','')
            source = device.get('source', '')
            status = device.get('status', '')
            immatriculeID = device.get('immatriculationID','')
            value = {
                'latitude': latitude, 
                'longitude': longitude, 
                'source': source,
                'status': status,
                'immatriculeID': immatriculeID
            }
            DeviceStatusInfo.append(value)
        result = redis.set('Middle_office_position_vehicle', str(DeviceStatusInfo))
        redis.save()
        logger.info('result: %s' % result)
        logger.info('%s' % (devices,))

    except Exception as e:
        logger.info("An exception occurred")

mo_service = MiddleOfficeService('apikey C603LtrigedeprO1ux', "http://lmtv.digitalinnovationspace.com:8182")

while True:
    while r.get('session_id') is not None and r.get('server') is not None:
        try:
            devices = client.get_devicestatusinfo()
            DeviceStatusInfo = []
            for device in devices:
                longitude = device['longitude']
                deviceid = device['device']['id']
                latitude = device['latitude']
                bearing = device['bearing']
                value = {'latitude': latitude, 'longitude': longitude, 'deviceid': deviceid, 'bearing': bearing}
                DeviceStatusInfo.append(value)
            result = r.set('DeviceStatusInfo', str(DeviceStatusInfo))
            pos_cron = DeviceOdometer(r, client.client)
            message = pos_cron.execute()
            get_all_position_mo(mo_service, r)
        except Exception as e:
            logger.error(e)
        time.sleep(10)
    client = AuthMygeotab(r)
