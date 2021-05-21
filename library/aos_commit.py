from ansible.module_utils.basic import *
from ansible.module_utils.shared import LoginBlueprint
from ansible.module_utils.shared import AosApi

def commit():
    """
    Input user answer 'yes' or 'no',
        authentication values, blueprint id, aos ip, commit description.
    :return: Deploy or revet staged config depends on the answer.
    """
    module = AnsibleModule(argument_spec=dict(
        arguments=dict(type='dict', required=True)))
    arguments = (module.params['arguments'])
    aos_user = arguments['aos_user']
    aos_pass = arguments['aos_pass']
    aos_ip = arguments['aos_ip']
    bp_name = arguments['bp_name']
    description = arguments['description']
    answer = arguments['answer']
    token_bp_id_address = LoginBlueprint().blueprint(aos_user, aos_pass,
                                                     aos_ip, bp_name)
    token = token_bp_id_address[0]
    bp_id = token_bp_id_address[1]
    if answer['user_input'].lower() in ['yes', 'y']:
        # Get blueprint version.
        bp_version = AosApi().bp_get(token, bp_id, aos_ip)['version']
        # Commit blueprint with description.
        AosApi().bp_deploy_put(token, bp_id, aos_ip, {'version': bp_version,
                                                     'description': description})
        result = 'Commit'
        ansible_comment = 'AOS deploy staged config'
    elif answer['user_input'].lower() in ['no', 'n']:
        AosApi().bp_revert_post(token, bp_id, aos_ip)
        result = 'Not Commit'
        ansible_comment = 'AOS revert staged config'
    else:
        AosApi().bp_revert_post(token, bp_id, aos_ip)
        result = 'Not Commit'
        ansible_comment = 'Unexpected comments. AOS reverts staged config'
    module.exit_json(changed=True, Result=result, Comment=ansible_comment)

if __name__ == '__main__':
    commit()
