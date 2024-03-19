import argparse
import json
import logging
import sys
import time

import mygeotab
import redis

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


def authenticate_mygeotab(r):
    username = r.get('username').decode("utf-8")
    database = r.get('database').decode("utf-8")
    password = r.get('password').decode("utf-8")
    client = mygeotab.API(username=username, password=password, database=database)
    client.authenticate()
    session_id = client.credentials.session_id
    server = client.credentials.server

    r.set('session_id', session_id)
    r.set('server', server)
    credentials = {
        'username': username,
        'database': database,
        'server': server,
        'session_id': session_id
    }
    r.set('credentials', json.dumps(credentials))
    r.expire('session_id', 1123200)
    r.expire('server', 1123200)

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

if not args.hredis:
    logger.info('\n')
    logger.info("*" * len(error_msg))
    logger.info(error_msg)
    logger.info("*" * len(error_msg))
    logger.info('\n')
    sys.exit(1)
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
r = redis.Redis(host=args.hredis, port=args.port, db=db, password=password_redis, username=args.redisusername)
if args.username or args.database or args.pwmygeotab:
    if not args.username or not args.database or not args.pwmygeotab:
        logger.info('\n')
        logger.info("*" * len(error_msg3))
        logger.info(error_msg3)
        logger.info("*" * len(error_msg3))
        logger.info('\n')
        sys.exit(1)
    else:
        r.set('username', args.username)
        r.set('password', args.pwmygeotab)
        r.set('database', args.database)
        if args.servergeotab and args.sessionidgeotab:
            r.set('server', args.servergeotab)
            r.set('session_id', args.sessionidgeotab)
            client = mygeotab.API(username=args.username, password=args.pwmygeotab, database=args.database, server=args.servergeotab)
            credentials = {
                'username': client.credentials.username,
                'database': client.credentials.database,
                'server': client.credentials.server,
                'session_id': client.credentials.session_id
            }
            r.set('credentials', json.dumps(credentials))
if r.get('username') is None or r.get('password') is None or r.get('database') is None:
    if not args.username or not args.database or not args.pwmygeotab:
        logger.info('\n')
        logger.info("*" * len(error_msg3))
        logger.info(error_msg3)
        logger.info("*" * len(error_msg3))
        logger.info('\n')
        sys.exit(1)
    r.set('username', args.username)
    r.set('password', args.pwmygeotab)
    r.set('database', args.database)
if r.get('session_id') is None or r.get('server') is None:
    client = authenticate_mygeotab(r)

else:
    username = r.get('username').decode("utf-8")
    password = r.get('password').decode("utf-8")
    database = r.get('database').decode("utf-8")
    server = r.get('server').decode("utf-8")
    session_id = r.get('session_id').decode("utf-8")

# connexion mygeotab
    client = mygeotab.API(username=username, password=password, database=database, server=server, session_id=session_id)
while True:

    while r.get('session_id') is not None and r.get('server') is not None:
        try:
            devices = client.get('DeviceStatusInfo')
            DeviceStatusInfo = []
            for device in devices:
                longitude = device['longitude']
                deviceid = device['device']['id']
                latitude = device['latitude']
                bearing = device['bearing']
                value = {'latitude': latitude,
                         'longitude': longitude,
                         'deviceid': deviceid,
                         'bearing': bearing}
                DeviceStatusInfo.append(value)
                logger.info('Latitude/longitude: %s / %s , deviceid = %s ' % (str(latitude), str(longitude), deviceid))
            result = r.set('DeviceStatusInfo', str(DeviceStatusInfo))
            r.save()
            logger.info('result: %s' % result)
            time.sleep(5)
        except Exception as e:
            logger.error(f"An exception occurred : {e}")
    client = authenticate_mygeotab(r)
    r.set('credentials', str(client.credentials))
