import mygeotab


class MyGeotabService:

    def __init__(self, username, database, password=None, server=None, session_id=None):
        self.client = mygeotab.API(username=username, server=server, password=password, database=database, session_id=session_id)

    def get_devicestatusinfo(self):
        info = self.client.get('DeviceStatusInfo')
        return info

    def authenticate(self):
        self.client.authenticate()
        credentials = self.client.credentials
        return credentials
