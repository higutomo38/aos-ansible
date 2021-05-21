import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import socket
import sys


class LoginBlueprint(object):

    def aos_login(self, aos_user, aos_pass, aos_ip):
        """ Get Login Token from AOS using ID/Password.
        :return: tuple: (AOS Login Token, AOS_IP)
        """
        if ':' in aos_ip:
            aos_ip = aos_ip.rsplit(':', 1)[0]
        try:
            socket.gethostbyname(aos_ip)
        except socket.error:
            print('----- Error: FQDN failure -----')
            sys.exit()
        url = 'https://' + aos_ip + '/api/user/login'
        payload = {"username": aos_user, "password": aos_pass}
        aos_response = requests.post(url,
                             headers = {'Content-Type': 'application/json'},
                             data = json.dumps(payload), verify = False,
                             timeout = 3)
        if str(aos_response.status_code)[0] == '2':
            aos_response = aos_response.json()
        else:
            print(
                '----- Error: HTTP Server/Client error or Authentication failure -----')
            sys.exit()
        if 'token' in aos_response:
            return aos_response['token']
        else:
            print('----- Error: Authentication failure -----')
            sys.exit()

    def blueprint(self, aos_user, aos_pass, aos_ip, bp_name):
        """ Get Login Token and Bluprint ID from Blueprint Name
        :return: tuple: (AOS Login Token, Blueprint ID, AOS_IP)
        """
        token = self.aos_login(aos_user, aos_pass, aos_ip)
        url = 'https://' + aos_ip + '/api/blueprints'
        aos_response = requests.get(url,
                headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                verify = False).json()
        if bp_name in [ bp['label'] for bp in aos_response['items']]:
            for bp in aos_response['items']:
                if bp['label'] == bp_name:
                    return token, bp['id'], aos_ip
        else:
            print('----- Error:Blueprint name -----')
            sys.exit()


class AosApi(object):

    def __init__(self):
        pass

    def request_get_format(self, token, aos_ip, api_path, bp_id, node_id):
        """ Make request GET function
        :param: AOS Token, Blueprint ID, AOS_IP, API Path
        :return: Request GET function for specific path.
        """
        if '{node_id}' in api_path:
            return requests.get('https://' + aos_ip + api_path.format(blueprint_id = bp_id, node_id = node_id),
                                headers={'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                verify=False).json()
        elif '{blueprint_id}' in api_path:
            return requests.get('https://' + aos_ip + api_path.format(blueprint_id = bp_id),
                                headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                verify = False).json()
        else:
            return requests.get('https://' + aos_ip + api_path,
                                headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                verify = False).json()

    def request_post_format(self, token, aos_ip, api_path, bp_id, payload):
        """ Make request POST function
        :param: AOS Token, Blueprint ID, AOS_IP, API Path, Payload
        :return: Request POST function for specific path.
        """
        if '{blueprint_id}' in api_path:
            return requests.post('https://' + aos_ip + api_path.format(blueprint_id = bp_id),
                                 headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                 data = json.dumps(payload), verify = False).json()
        else:
            return requests.post('https://' + aos_ip + api_path,
                                 headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                 data = json.dumps(payload), verify = False).json()

    def request_put_format(self, token, aos_ip, api_path, bp_id, payload):
        """ Make request PUT function
        :param: AOS Token, Blueprint ID, AOS_IP, API Path, Payload
        :return: Request PUT function for specific path.
        """
        if '{blueprint_id}' in api_path:
            return requests.put('https://' + aos_ip + api_path.format(blueprint_id = bp_id),
                                 headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                 data = json.dumps(payload), verify = False).json()
        else:
            return requests.put('https://' + aos_ip + api_path,
                                 headers = {'AUTHTOKEN': token, 'Content-Type': 'application/json'},
                                 data = json.dumps(payload), verify = False).json()

# Get Function
    def bp_get(self, token, bp_id, aos_ip):
        return self.request_get_format(token, aos_ip, '/api/blueprints/{blueprint_id}', bp_id, 'temp')

    def bp_configuration_get(self, token, bp_id, aos_ip):
        return self.request_get_format(token, aos_ip, '/api/blueprints/{blueprint_id}/configuration', bp_id, 'temp')

    def bp_diff_status_get(self, token, bp_id, aos_ip):
        return self.request_get_format(token, aos_ip, '/api/blueprints/{blueprint_id}/diff-status', bp_id, 'temp')

    def bp_node_get_node_id(self, token, bp_id, aos_ip, node_id):
        return self.request_get_format(token, aos_ip, '/api/blueprints/{blueprint_id}/nodes/{node_id}', bp_id, node_id)

    def bp_security_zone_get(self, token, bp_id, aos_ip):
        return self.request_get_format(token, aos_ip, '/api/blueprints/{blueprint_id}/security-zones', bp_id, 'temp')

    def system_agents_get(self, token, aos_ip):
        return self.request_get_format(token, aos_ip, '/api/system-agents', 'temp', 'temp')

# Post Function
    def bp_qe_post(self, token, bp_id, aos_ip, qe):
        return self.request_post_format(token, aos_ip, '/api/blueprints/{blueprint_id}/qe', bp_id, {"query": qe})

    def bp_revert_post(self, token, bp_id, aos_ip):
        return self.request_post_format(token, aos_ip, '/api/blueprints/{blueprint_id}/revert', bp_id, 'temp')

    def bp_virtual_networks_post(self, token, bp_id, aos_ip, vn_template):
        return self.request_post_format(token, aos_ip, '/api/blueprints/{blueprint_id}/virtual-networks', bp_id, vn_template)

# Put Function
    def bp_deploy_put(self, token, bp_id, aos_ip, payload):
        return self.request_put_format(token, aos_ip, '/api/blueprints/{blueprint_id}/deploy', bp_id, payload)


