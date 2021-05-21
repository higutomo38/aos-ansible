from ansible.module_utils.basic import *
from jnpr.junos import Device
from ncclient import manager
import xml.etree.cElementTree as ET

def ping_overlay():
    """
    Create dict { mgmt_ip: lo0_ip }
    Ping overlay for a new virtual network - leaf ping mesh (N(N-1)/2)
        tunnel-src: leaf vtep lo0.0
        tunnel-dst: leaf vtep lo0.0
        vni: new vni
    :return:
    Ping results as dict and Ansible save them on './logs/ping_overlay.log'.
    """
    module = AnsibleModule(argument_spec=dict(
        arguments=dict(type='dict', required=True)))
    arguments = (module.params['arguments'])
    junos_user = arguments['junos_user']
    junos_pass = arguments['junos_pass']
    junos_ips = arguments['junos_ips']
    vni = arguments['vni']
    mgmt_lo0_dict = {}

    # Create dict { mgmt_ip: lo0_ip }
    for mgmt_ip in junos_ips:
        with Device(host=mgmt_ip, user=junos_user, password=junos_pass) as dev:
            mgmt_lo0_dict[mgmt_ip] = \
                dev.rpc.get_interface_information\
                    (interface_name='lo0.0', terse=True, normalize=True)\
                    .xpath(".//address-family[address-family-name='inet']\
                           /interface-address/ifa-local")[0].text

    # Ping overlay
    result_dict_all = {}
    for mgmt_lo0 in list(mgmt_lo0_dict.items()):
        result_list = []
        del mgmt_lo0_dict[mgmt_lo0[0]]
        if len(mgmt_lo0_dict) != 0:
            with manager.connect(host=mgmt_lo0[0], port=830, username=junos_user,
                                 password=junos_pass, timeout=20, device_params={'name':'junos'},
                                 hostkey_verify=False) as dev:
                for dst_lo0 in mgmt_lo0_dict.values():
                    result_dict = {}
                    ping_result = str(dev.command\
                        ('ping overlay vni {0} tunnel-type vxlan tunnel-src {1} tunnel-dst {2} count 3'\
                         .format(vni, mgmt_lo0[1], dst_lo0)))
                    xml_root = ET.fromstring(ping_result)
                    src_ip = xml_root.findall("./ping-overlay-results/tunnel-src")[0].text.replace('\n', '')
                    dst_ip = xml_root.findall("./ping-overlay-results/tunnel-dst")[0].text.replace('\n', '')
                    if 'ping-overlay-success' in ping_result: result = 'success'
                    else: result = 'no response'
                    result_dict['tunnel_src_ip'] = src_ip
                    result_dict['tunnel_dst_ip'] = dst_ip
                    result_dict['result'] = result
                    result_dict['vni'] = vni
                    result_list.append(result_dict)
        else: break
        result_dict_all[mgmt_lo0[0]] = result_list

    module.exit_json(changed=False, result=result_dict_all)

if __name__ == '__main__':
    ping_overlay()