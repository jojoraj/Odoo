from odoo.tools import config

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_DB = config.get('redis_db', 0)
REDIS_PWD = config.get('redis_password', '')
REDIS_USR = config.get('redis_user', '')
