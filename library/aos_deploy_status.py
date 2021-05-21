from ansible.module_utils.basic import *
from ansible.module_utils.shared import LoginBlueprint
from ansible.module_utils.shared import AosApi
import time

def deploy_status():
    """
    Confirm AOS deployment status until all leafs deployed.
    Break Ansible playbook if 'FAILED' or 'PENDING' for approx 60s.
    :return: Result, Comments
    """
    module = AnsibleModule(argument_spec=dict(
        arguments=dict(type='dict', required=True)))
    arguments = (module.params['arguments'])
    aos_user = arguments['aos_user']
    aos_pass = arguments['aos_pass']
    aos_ip = arguments['aos_ip']
    bp_name = arguments['bp_name']
    token_bp_id_address = LoginBlueprint().blueprint(aos_user, aos_pass,
                                                     aos_ip, bp_name)
    token = token_bp_id_address[0]
    bp_id = token_bp_id_address[1]
    timesec = 0

    while timesec < 60:
        state_list = [ state['state'] for state in AosApi().bp_configuration_get\
                     (token, bp_id, aos_ip)['device_status']]
        if 'failed' in state_list:
            comment = 'Deploy Failed. Check an error on AOS UI'
            result = 'failed'
            break
        elif 'in_progress' in state_list:
            timesec += 5
            time.sleep(5)
            comment = 'Deploy InProgress for a long time. Check an error on AOS UI'
            result = 'failed'
        else:
            comment = 'Deploy Succeeded.'
            result = 'success'
            break

    module.exit_json(changed=False, Comment=comment, Result=result)

if __name__ == '__main__':
    deploy_status()
