import json

from geotab_service import MyGeotabService


class AuthMygeotab:

    def __init__(self, r):
        username = r.get('username').decode("utf-8")
        database = r.get('database').decode("utf-8")
        password = r.get('password').decode("utf-8")
        client = MyGeotabService(username=username, password=password, database=database)
        cred = client.authenticate()
        session_id = cred.session_id
        server = cred.server

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
