import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class AosApi(object):

    def __init__(self):
        pass

    def request_get_format(self, token, bp_id, address, api_path):
        """ Make request GET function
        :param: AOS Token, Blueprint ID, AOS Address, API Path
        :return: Request GET function for specific path.
        """
        if '{blueprint_id}' in api_path:
            return requests.get('https://' + address + api_path.format(blueprint_id = bp_id),
                                headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                verify = False).json()
        else:
            return requests.get('https://' + address + api_path,
                                headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                verify = False).json()

    def request_post_format(self, token, bp_id, address, api_path, payload):
        """ Make request POST function
        :param: AOS Token, Blueprint ID, AOS Address, API Path, Payload
        :return: Request POST function for specific path.
        """
        if '{blueprint_id}' in api_path:
            return requests.post('https://' + address + api_path.format(blueprint_id = bp_id),
                                 headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                 data = json.dumps(payload), verify = False).json()
        else:
            return requests.post('https://' + address + api_path,
                                 headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                 data = json.dumps(payload), verify = False).json()

    def bp_qe_post(self, token, bp_id, address, qe):
        return self.request_post_format\
            (token, bp_id, address, '/api/blueprints/{blueprint_id}/qe', {"query": qe})

    def bp_security_zone_get(self, token, bp_id, address):
        return self.request_get_format(token, bp_id, address, '/api/blueprints/{blueprint_id}/security-zones')

