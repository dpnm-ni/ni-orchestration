import ni_mon_client, ni_nfvo_client
import ni_custom_client
from ni_mon_client.rest import ApiException
from ni_nfvo_client.rest import ApiException
from datetime import datetime, timedelta, timezone
from config import cfg

import numpy as np
import threading
import datetime as dt
import math
import os
import time
import subprocess
from pprint import pprint
import random

# Parameters
# OpenStack Parameters
openstack_network_id = cfg["openstack_network_id"] # Insert OpenStack Network ID to be used for creating SFC

# Global values
sample_user_data = "#cloud-config\n password: %s\n chpasswd: { expire: False }\n ssh_pwauth: True\n manage_etc_hosts: true\n runcmd:\n - sysctl -w net.ipv4.ip_forward=1"
target_sfc_name_list = []
real_sfc_name_list = []
_orchestration_id = 0


def get_sfcs():
    ni_nfvo_client_cfg = ni_nfvo_client.Configuration()
    ni_nfvo_client_cfg.host=cfg["ni_nfvo"]["host"]
    ni_nfvo_sfc_api = ni_nfvo_client.SfcApi(ni_nfvo_client.ApiClient(ni_nfvo_client_cfg))

    result = ni_nfvo_sfc_api.get_sfcs()
    return result

def get_sfcs_names():
    sfcs = get_sfcs()
    sfc_names = [sfc.sfc_name for sfc in sfcs]
 
    return sfc_names

def create_scaling(sfc_name):
    ni_custom_client_cfg = ni_custom_client.Configuration()
    ni_custom_client_cfg.host=cfg["ni_auto_scaling"]["host"]
    ni_auto_scaling_api = ni_custom_client.ScalingApi(ni_custom_client.ApiClient(ni_custom_client_cfg))

    scale = ni_custom_client.DQN_ScalingInfo(sfc_name=sfc_name, scaling_name=sfc_name, slo=45, interval=10, duration=0, has_dataset=True)

    ni_auto_scaling_api.create_scaling(scaling_info=scale)

    return

def delete_scaling(sfc_name):
    ni_custom_client_cfg = ni_custom_client.Configuration()
    ni_custom_client_cfg.host=cfg["ni_auto_scaling"]["host"]
    ni_auto_scaling_api = ni_custom_client.ScalingApi(ni_custom_client.ApiClient(ni_custom_client_cfg))   

    ni_auto_scaling_api.delete_scaling(name=sfc_name)

    return


def update_orchest_list():
    //




'''
# get_monitoring_api(): get ni_monitoring_client api to interact with a monitoring module
# Input: null
# Output: monitoring moudle's client api
def get_monitoring_api():
#    print("1")

    ni_mon_client_cfg = ni_mon_client.Configuration()
    ni_mon_client_cfg.host = cfg["ni_mon"]["host"]
    ni_mon_api = ni_mon_client.DefaultApi(ni_mon_client.ApiClient(ni_mon_client_cfg))

    return ni_mon_api


# get_nfvo_sfc_api(): get ni_nfvo_sfc api to interact with a nfvo module
# Input: null
# Output: nfvo moudle's sfc api
def get_nfvo_sfc_api():
#    print("2")

    nfvo_client_cfg = ni_nfvo_client.Configuration()

    nfvo_client_cfg.host = cfg["ni_nfvo"]["host"]
    ni_nfvo_sfc_api = ni_nfvo_client.SfcApi(ni_nfvo_client.ApiClient(nfvo_client_cfg))

    return ni_nfvo_sfc_api


# get_nfvo_sfcr_api(): get ni_nfvo_sfcr api to interact with a nfvo module
# Input: null
# Output: nfvo moudle's sfcr api
def get_nfvo_sfcr_api():
#    print("3")

    nfvo_client_cfg = ni_nfvo_client.Configuration()
    nfvo_client_cfg.host = cfg["ni_nfvo"]["host"]
    ni_nfvo_sfcr_api = ni_nfvo_client.SfcrApi(ni_nfvo_client.ApiClient(nfvo_client_cfg))

    return ni_nfvo_sfcr_api


# get_nfvo_vnf_api(): get ni_nfvo_vnf api to interact with a nfvo module
# Input: null
# Output: nfvo moudle's vnf api
def get_nfvo_vnf_api():
#    print("4")

    nfvo_client_cfg = ni_nfvo_client.Configuration()

    nfvo_client_cfg.host = cfg["ni_nfvo"]["host"]
    ni_nfvo_vnf_api = ni_nfvo_client.VnfApi(ni_nfvo_client.ApiClient(nfvo_client_cfg))

    return ni_nfvo_vnf_api


# get_nfvo_vnf_spec(): get ni_nfvo_vnf spec to interact with a nfvo module
# Input: null
# Output: nfvo moudle's vnf spec
def get_nfvo_vnf_spec():
#    print("5")

    nfvo_client_cfg = ni_nfvo_client.Configuration()

    nfvo_client_cfg.host = cfg["ni_nfvo"]["host"]

    t = ni_nfvo_client.ApiClient(nfvo_client_cfg)

    ni_nfvo_vnf_spec = ni_nfvo_client.VnfSpec(t)
    ni_nfvo_vnf_spec.flavor_id = cfg["flavor"]["default"]
    ni_nfvo_vnf_spec.user_data = sample_user_data % cfg["instance"]["password"]

    return ni_nfvo_vnf_spec


# get_ip_from_vm(vm_id): get a data plane IP of VM instance
# Input: vm instance id
# Output: port IP of the data plane
def get_ip_from_id(vm_id):
#    print("6")

    ni_mon_api = get_monitoring_api()
    query = ni_mon_api.get_vnf_instance(vm_id)
    #print(query)

    ## Get ip address of specific network
    ports = query.ports
    #print(ports)
    network_id = openstack_network_id
    #print(network_id)

    for port in ports:
        if port.network_id == network_id:
            return port.ip_addresses[-1]


# get_node_info(): get all node information placed in environment
# Input: null
# Output: Node information list
def get_node_info():
#    print("7")
    ni_mon_api = get_monitoring_api()
    query = ni_mon_api.get_nodes()

    response = [ node_info for node_info in query if node_info.type == "compute" and node_info.status == "enabled"]
    response = [ node_info for node_info in response if not (node_info.name).startswith("NI-Compute-82-9")]

    return response


# get_vnf_info(sfc_prefix, sfc_vnfs): get each VNF instance information from monitoring module
# Input: Prefix of VNF instance name, SFC order tuple or list [example] ("client", "firewall", "dpi", "ids", "proxy")
# Output: VNF information list
def get_vnf_info(sfc_prefix, sfc_vnfs):
    #print("8")
    #print(sfc_prefix)
    #print(sfc_vnfs)

    # Get information of VNF instances which are used for SFC
    ni_mon_api = get_monitoring_api()
    query = ni_mon_api.get_vnf_instances()

    selected_vnfi = [ vnfi for vnfi in query for vnf_type in sfc_vnfs if vnfi.name.startswith(sfc_prefix + vnf_type) ]

    vnfi_list = []
    num_vnf_type = []
    temp = []

    # Sort VNF informations for creating states
    for vnf_type in sfc_vnfs:
        i =  sfc_vnfs.index(vnf_type)

        temp.append([])

        temp[i] = [ vnfi for vnfi in selected_vnfi if vnfi.name.startswith(sfc_prefix + vnf_type) ]
        temp[i].sort(key=lambda vnfi: vnfi.name)

        vnfi_list = vnfi_list + temp[i]

    return vnfi_list


# get_sfcr_by_name(sfcr_name): get sfcr information by using sfcr_name from NFVO module
# Input: sfcr name
# Output: sfcr_info
def get_sfcr_by_name(sfcr_name):
#    print("9")

    ni_nfvo_sfcr_api = get_nfvo_sfcr_api()
    query = ni_nfvo_sfcr_api.get_sfcrs()

    sfcr_info = [ sfcri for sfcri in query if sfcri.name == sfcr_name ]
    sfcr_info = sfcr_info[-1]

    return sfcr_info


# get_sfcr_by_id(sfcr_id): get sfc information by using sfcr_id from NFVO module
# Input: sfcr_id, FYI, sfcr is a flow classifier in OpenStack
# Output: sfcr_info
def get_sfcr_by_id(sfcr_id):
#    print("10")

    ni_nfvo_sfcr_api = get_nfvo_sfcr_api()
    query = ni_nfvo_sfcr_api.get_sfcrs()

    sfcr_info = [ sfcri for sfcri in query if sfcri.id == sfcr_id ]
    sfcr_info = sfcr_info[-1]

    return sfcr_info


# get_sfc_by_name(sfc_name): get sfc information by using sfc_name from NFVO module
# Input: sfc name
# Output: sfc_info
def get_sfc_by_name(sfc_name):
#    print("11")

    ni_nfvo_sfc_api = get_nfvo_sfc_api()
    query = ni_nfvo_sfc_api.get_sfcs()

    sfc_info = [ sfci for sfci in query if sfci.sfc_name == sfc_name ]

    if len(sfc_info) == 0:
        return False

    sfc_info = sfc_info[-1]

    return sfc_info


# get_soruce_client(sfc_name): get source client ID by using sfc_name
# Input: sfc name
# Output: source client info
def get_source_client(sfc_name):
#    print("12")

    sfc_info = get_sfc_by_name(sfc_name)
    sfcr_info = get_sfcr_by_id(sfc_info.sfcr_ids[0])
    source_client = get_monitoring_api().get_vnf_instance(sfcr_info.source_client)

    return source_client


# get_soruce_client(sfc_name): get source client ID by using sfc_name
# Input: sfc name
# Output: source client info
def get_destination_client(sfc_name):
#    print("12")

    sfc_info = get_sfc_by_name(sfc_name)
    sfcr_info = get_sfcr_by_id(sfc_info.sfcr_ids[0])
    destination_client = get_monitoring_api().get_vnf_instance(sfcr_info.destination_client)

    return destination_client



# deploy_vnf(vnf_spec): deploy VNF instance in OpenStack environment
# Input: VnFSpec defined in nfvo client module
# Output: API response
def deploy_vnf(vnf_spec):
#    print("17")

    ni_nfvo_api = get_nfvo_vnf_api()
    api_response = ni_nfvo_api.deploy_vnf(vnf_spec)
    print("check deployed")
    print(vnf_spec)
    print(api_response)

    return api_response


# destroy_vnf(id): destory VNF instance in OpenStack environment
# Inpurt: ID of VNF instance
# Output: API response
def destroy_vnf(id):
#    print("18")

    ni_nfvo_api = get_nfvo_vnf_api()
    api_response = ni_nfvo_api.destroy_vnf(id)

    return api_response



# lable_resource(flavor_id): check whether there are enough resource in nodes
# Input: node_id
# Output: True (enough), False (otherwise)
def check_available_resource(node_id):
#    print("20")

    node_info = get_node_info()
    selected_node = [ node for node in node_info if node.id == node_id ][-1]
    flavor = get_monitoring_api().get_vnf_flavor(cfg["flavor"]["default"])

    if selected_node.n_cores_free >= flavor.n_cores and selected_node.ram_free_mb >= flavor.ram_mb:
        return True

    return False


# create_monitor(scaler): create instances to be source and destination to measure response time
# Input: scaler
# Output: True (success to create instances), False (otherwise)
def create_monitor(scaler):
#    print("21")
    source_client = get_source_client(scaler.get_sfc_name())
    destination_client = get_destination_client(scaler.get_sfc_name())

    print("source client.id : ", source_client.id)
    scaler.set_monitor_src_id(source_client.id)
    scaler.set_monitor_dst_id(destination_client.id)

    print("sfcr.id : ", get_sfc_by_name(scaler.get_sfc_name()).sfcr_ids[-1])
    scaler.set_monitor_sfcr_id(get_sfc_by_name(scaler.get_sfc_name()).sfcr_ids[-1])

    return True


# delete_monitor(scaler): delete SLA monitor instances
# Input: scalerdelete_monitor
# Output: Null
def delete_monitor(scaler):
#    print("22")

    scaler.set_monitor_src_id("")
    scaler.set_monitor_dst_id("")
    scaler.set_monitor_sfcr_id("")   


# get_sfc_prefix(sfc_info): get sfc_prefix from sfc_info
# Input: SFC Info.
# Output: sfc_prefix
def get_sfc_prefix(sfc_info):
#    print("24")
    prefix = sfc_info.sfc_name.split(cfg["instance"]["prefix_splitter"])[0]
    prefix = prefix + cfg["instance"]["prefix_splitter"]

    return prefix

'''


threading.Thread(target=, args=).start()
