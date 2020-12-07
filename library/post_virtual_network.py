from ansible.module_utils.basic import *
from ansible.module_utils.shared import AosApi
import json
import requests


class PostVN():

    module = AnsibleModule(argument_spec=dict(
        arguments=dict(type='dict', required=True)))
    arguments = (module.params['arguments'])
    token = arguments['token']
    bp_id = arguments['bp_id']
    aos_ip = arguments['aos_ip']
    vn_label = arguments['vn_label']
    vlan_id = arguments['vlan_id']
    vni = arguments['vni']
    security_zone = arguments['security_zone']
    ipv4_subnet = arguments['ipv4_subnet']
    virtual_gateway_ipv4 = arguments['virtual_gateway_ipv4']
    dhcp_service = arguments['dhcp_service']
    server_list = arguments['server_list']
    # module.exit_json(changed=False, arguments=dhcp_service)

    def __init__(self):
        pass

    def physical_leaf_list(self):
        """
        :return: Leaf_ID list connected to 'server_list'. Use physical interface
        "if_type='ethernet'" not 'port_channel' in graph query at this time.
        Delete duplicate Leaf_ID in the list by 'list(set)'.
        """
        return list(set([ AosApi().bp_qe_post(PostVN.token, PostVN.bp_id, PostVN.aos_ip,
                    "node('system', name='server', role='l2_server', hostname='" + server_list + "')\
                    .out('hosted_interfaces')\
                    .node('interface', name='server_int', if_type='ethernet')\
                    .out('link')\
                    .node('link', name='link')\
                    .in_('link')\
                    .node('interface', name='leaf_int')\
                    .in_('hosted_interfaces')\
                    .node('system', name='leaf')\
                    .ensure_different('server_int', 'leaf_int')"\
                    )['items'][0]['leaf']['id'] for server_list in PostVN.server_list ]))
        # PostVN.module.exit_json(changed = False, arguments = hoge)

    def logical_physical_leaf_list(self):
        """
        :input: physical_leaf_list(self).
        :return: Leaf_ID list logical(mlag) and physical(not include member of mlag).
                 1. Create Dict { 'member of mlag system_id' : 'logical(mlag) system_id' }
                 2. if 'member of mlag' is in physical_leaf_list,
                    then remove the id and append logical system_id instead.
                 3. Delete duplicate logical system_id in the list by 'list(set)'.
        :note: AOS push VN config except for VN endpoint to these system on other method.
        """
        leaf_list = PostVN.physical_leaf_list(self)
        sys_rg_dict = { rg_sys['system']['id']:rg_sys['rg']['id'] \
                        for rg_sys in AosApi().bp_qe_post(PostVN.token, PostVN.bp_id, PostVN.aos_ip,
                        "node('redundancy_group', name='rg', rg_type='mlag')"\
                        ".out('composed_of_systems')"\
                        ".node('system', name='system', role='leaf')"\
                        )['items']}
        for system_id in sys_rg_dict.items():
            if system_id[0] in leaf_list:
                leaf_list.remove(system_id[0])
                leaf_list.append(system_id[1])
        return list(set(leaf_list))
        # PostVN.module.exit_json(changed = False, arguments = list(set(leaf_list)))

    def security_zone_id(self):
        """
        :input: security_zone
        :return: security_zone_id
        """
        for sec_zone in AosApi().bp_security_zone_get(PostVN.token, PostVN.bp_id, PostVN.aos_ip)['items'].values():
            if sec_zone['label'] == PostVN.security_zone:
                return sec_zone['id']
                # PostVN.module.exit_json(changed = False, arguments = sec_zone['id'])

    def endpoints(self):
        """
        :return: Server Interface ID list logical(port-channel) and physical(ethernet) facing leafs.
        If a physical one is member of logical, only port-channel ID returned.
        """
        int_id_list = []
        for server_list in PostVN.server_list:
            int_sys_dict = { int_sys['interface']['if_type']:int_sys['interface']['id']\
                             for int_sys in AosApi().bp_qe_post(PostVN.token, PostVN.bp_id, PostVN.aos_ip,
                             "node('system', name='server', role='l2_server', hostname='" + server_list + "')\
                             .out('hosted_interfaces')\
                             .node('interface', name='interface')"\
                             )['items']}
            if len(int_sys_dict) == 2:
                int_id_list.append(int_sys_dict['port_channel'])
            elif len(int_sys_dict) == 1:
                int_id_list.append(int_sys_dict['ethernet'])
        return int_id_list
        # PostVN.module.exit_json(changed = False, arguments = int_id_list)

    def post_virtual_network(self):
        """
        :input: For creating 'vn_template'.
                    -> security_zone_id(self), vn_label, vn_type, vni,
                       ipv4_subnet, virtual_gateway_ipv4, dhcp_service.
                For building 'vn_template'.
                    -> logical_physical_leaf_list(self), vlan_id.
        :return: Post Virtual Network 'vn_template' using 'vn_template'
        """
        vn_template = {
            "label": PostVN.vn_label,
            "vn_type": "vxlan",
            "vn_id": str(PostVN.vni),
            "security_zone_id": PostVN.security_zone_id(self),
            "l3_connectivity": "l3Enabled",
            "ipv4_subnet": PostVN.ipv4_subnet,
            "virtual_gateway_ipv4": PostVN.virtual_gateway_ipv4,
            "dhcp_service": PostVN.dhcp_service,
        }
        target_dict = {}
        target_list = []
        for leaf_id in PostVN.logical_physical_leaf_list(self):
            target_dict["system_id"] = leaf_id
            target_dict["vlan_id"] = PostVN.vlan_id
            target_list.append(target_dict)
            target_dict = {}
        vn_template["bound_to"] = target_list
        target_list = []
        for interface_id in PostVN.endpoints(self):
            target_dict["interface_id"] = interface_id
            target_dict["tag_type"] = "vlan_tagged"
            target_list.append(target_dict)
            target_dict = {}
        vn_template["endpoints"] = target_list
        resp = requests.post('https://' + PostVN.aos_ip + '/api/blueprints/' + PostVN.bp_id + '/virtual-networks',
                             headers={'AUTHTOKEN':PostVN.token, 'Content-Type':'application/json'},
                             data=json.dumps(vn_template), verify=False)
        if resp.status_code != 201: PostVN.module.fail_json(msg = resp.text)
        else: PostVN.module.exit_json(changed = True, Successfully = 'Commit staged setting')

if __name__ == '__main__':
    # PostVN()
    # PostVN().physical_leaf_list()
    # PostVN().logical_physical_leaf_list()
    # PostVN().security_zone_id()
    # PostVN().endpoints()
    PostVN().post_virtual_network()
