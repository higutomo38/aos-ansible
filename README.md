# **AOS Ansible Module**

AOS Ansible modules for demonstraton here are packaged as dockerhub repository "higutomo38/aos-ansible". Dockerhub builds the image automatically after github repo here goes updated.

AOS Version: 3.3.0

## **Installation**

Run the docker repo.
```
docker run --name aos-ansible -it -w /tmp/aos-ansible higutomo38/aos-ansible:latest /bin/bash
```

Set inventory
```
$ vi inventory
[aos_ip]
172.16.1.1 
```

Set main_vars.yml
```
$ vi ./vars/main_vars.yml
aos_ip: 172.16.1.1
aos_user: admin
aos_pass: admin
```

Set virtual_network_vars.yml
```
$ vi ./vars/virtual_network_vars.yml 
vn_label: blue_131
vlan_id: 131
vni: 10131
security_zone: blue
ipv4_subnet: 192.168.131.0/24
virtual_gateway_ipv4: 192.168.131.1
dhcp_service: dhcpServiceEnabled
server_list: [ rack1-server1, switch1-server1, switch2-server1, switch3-server1 ]
```

Run ansible playbook
```
$ ansible-playbook virtual-network.yml 
```

## **Ansible Playbook**

