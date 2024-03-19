import requests
import json
import logging


logger = logging.getLogger('logger_script_python')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

class MiddleOfficeService:

    def __init__(self, api_key, base_url):
        self.header = {
            'Authorization': api_key,
            'Content-Type' : 'application/json',
            'Accept': "*/*",
            'Connection': "keep-alive"
        }
        self.base_url = base_url


    def crm_assignation_recommandation(self, latlong):
        try:
     
            url =  self.base_url + "/recommandations/get"
            response = requests.request(
                method='get',
                url=url,
                params=latlong,
                headers=self.header,
            )
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.error(f"Request failed with status code: {response.status_code} - {response.reason}")
                return []
            
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occurred during the request
            logger.error(f"An error occurred during the request: {e}")
            return []

    
    def mo_create_driver(self, values):
        try:
            url =  self.base_url + "/driver-mapping/add-driver"
            response = requests.request(
                method='post',
                url=url,
                data= json.dumps({
                    "driverName": values.get('name'),
                    "driverPhone": values.get('phone')
                }),
                headers=self.header
            )
            if response.status_code == 200:
                # data = json.loads(response)
                return True
            else:
                logger.error(f"Request failed with status code: {response.status_code} - {response.reason}")
                return False
            
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occurred during the request
            logger.error(f"An error occurred during the request: {e}")
            return False
    
    def update_vehicle_status(self, values):
        try:
            url =  self.base_url + "/vehicle-mapping/set-status"
            response = requests.request(
                method='post',
                headers=self.header,
                url=url,
                data= json.dumps({
                    "immatriculation": values.get('license_plate'),
                    "status": values.get('status').upper()
                }),
            )
            if response.status_code == 200:
                # data = json.loads(response)
                return True
            else:
                logger.error(f"Request failed with status code: {response.status_code} - {response.reason}")
                return False
            
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occurred during the request
            logger.error(f"An error occurred during the request: {e}")
            return False


    def update_vehicle_driver(self, values):
        try:
            url =  self.base_url + "/vehicle-mapping/update-driver"
            response = requests.request(
                headers=self.header,
                method='post',
                url=url,
                data= json.dumps({
                    "vehicleID": values.get('license_plate'),
                    "driverPhone": values.get('phone').replace(" ", "")
                })
            )
            if response.status_code == 200:
                # data = json.loads(response)
                return True
            else:
                logger.error(f"Request failed with status code: {response.status_code} - {response.reason}")
                return False
            
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occurred during the request
            logger.error(f"An error occurred during the request: {e}")
            return False

    def get_all_vehicle_position(self):
        try:
            url =  "http://lmtv.digitalinnovationspace.com:8182/vehicle-mapping/all-position"
            response = requests.request(
                method='get',
                url=url,
                headers=self.header
            )
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.error(f"Request failed with status code: {response.status_code} - {response.reason}")
            return False
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occurred during the request
            logger.error(f"An error occurred during the request: {e}")
            return False
