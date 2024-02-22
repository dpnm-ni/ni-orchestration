import ni_mon_client, ni_nfvo_client
import ni_custom_client
from ni_custom_client.models.scaling_info import DQN_ScalingInfo
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
orchestration_prefix_list = []
orchestration_list = []
orchestration_id = 0
orchestration_activated = False

#ni_nfvo_client_setting
ni_nfvo_client_cfg = ni_nfvo_client.Configuration()
ni_nfvo_client_cfg.host=cfg["ni_nfvo"]["host"]
ni_nfvo_sfcr_api = ni_nfvo_client.SfcrApi(ni_nfvo_client.ApiClient(ni_nfvo_client_cfg))
ni_nfvo_sfc_api = ni_nfvo_client.SfcApi(ni_nfvo_client.ApiClient(ni_nfvo_client_cfg))
ni_nfvo_vnf_api = ni_nfvo_client.VnfApi(ni_nfvo_client.ApiClient(ni_nfvo_client_cfg))

#ni_auto_scaling
ni_auto_scaling_client_cfg = ni_custom_client.Configuration()
ni_auto_scaling_client_cfg.host=cfg["ni_auto_scaling"]["host"]
ni_auto_scaling_api = ni_custom_client.ScalingApi(ni_custom_client.ApiClient(ni_auto_scaling_client_cfg))

#ni_traffic_gen
ni_traffic_gen_client_cfg = ni_custom_client.Configuration()
ni_traffic_gen_client_cfg.host=cfg["ni_traffic_gen"]["host"]
ni_traffic_gen_api = ni_custom_client.TrafficApi(ni_custom_client.ApiClient(ni_traffic_gen_client_cfg))

#ni_deployment
ni_deployment_client_cfg = ni_custom_client.Configuration()
ni_deployment_client_cfg.host=cfg["ni_deployment"]["host"]
ni_deployment_api = ni_custom_client.DeploymentApi(ni_custom_client.ApiClient(ni_deployment_client_cfg))

#ni_migration
ni_migration_client_cfg = ni_custom_client.Configuration()
ni_migration_client_cfg.host=cfg["ni_migration"]["host"]
ni_migration_api = ni_custom_client.MigrationApi(ni_custom_client.ApiClient(ni_migration_client_cfg))


#TODO name should be changed as ni_auto ~~


ni_consolidation_client_cfg = ni_custom_client.Configuration()
ni_consolidation_client_cfg.host=cfg["ni_consolidation"]["host"]
ni_consolidation_api = ni_custom_client.ConsolidationApi(ni_custom_client.ApiClient(ni_consolidation_client_cfg))



#Status
status_auto_deployment = False
status_auto_migration = False
status_auto_scaling = False
status_auto_consolidation = False

busy_auto_deployment = False
busy_auto_migration = False
busy_auto_scaling = False
busy_auto_consolidation = False

job_auto_deployment = []
job_auto_migration = []
job_auto_scaling = []
job_auto_consolidation = []




#Anomaly Detection
anomaly_vnfs = []



#Auto_scaling
as_slo = 45
as_duration = 36000
as_interval = 10
as_has_dataset = True


def filter_sfcs_by_prefix(sfcs, prefix_list):
    filtered_sfcs = [sfc for sfc in sfcs if any(sfc.sfc_name.startswith(prefix) for prefix in prefix_list)]

    return filtered_sfcs

def remove_prefix_duplicates_then_add(lst, new_string):
    if any(new_string.startswith(s) for s in lst):
       return
    lst[:] = [s for s in lst if not s.startswith(new_string)]
    lst.append(new_string)

    return 

def get_sfcs():
    result = ni_nfvo_sfc_api.get_sfcs()

    return result

def get_sfcs_names():
    sfcs = get_sfcs()
    sfc_names = [sfc.sfc_name for sfc in sfcs]
 
    return sfc_names

def get_sfcrs():
    sfcrs = ni_nfvo_sfcr_api.get_sfcrs()
 
    return sfcrs

def get_traffics():
    traffics = ni_traffic_gen_api.get_traffics()
 
    return traffics


#Orchestration
def monitor_deployment():
    global status_auto_deployment
    global status_auto_migration 
    global status_auto_scaling
    global status_auto_consolidation 
    
    global busy_auto_deployment 
    global busy_auto_migration 
    global busy_auto_scaling 
    global busy_auto_consolidation 

    global job_auto_deployment 
    global job_auto_migration 
    global job_auto_scaling 
    global job_auto_consolidation 
    
    #TODO deployment should considered when consolidation activated
    
    while(True):
        if status_auto_consolidation == True:
            print("Consolidation is worked now. no more vnf can be deployed . This can be changed in future")
        elif len(job_auto_consolidation) == 0:
            busy_auto_deployment = True
            if status_auto_deployment == True and len(job_auto_deployment) == 0 :
                ni_deployment_api.auto_deployment()
                job_auto_deployment.append("running")
            elif status_auto_deployment == False and len(job_auto_deployment) > 1 :
                ni_deployment_api.shutdown_deployment()
                job_auto_deployment = []
            busy_auto_deployment = False           
        time.sleep(2.2)
            
    return


#Orchestration
def monitor_migration():
    global status_auto_deployment
    global status_auto_migration 
    global status_auto_scaling
    global status_auto_consolidation 
    
    global busy_auto_deployment 
    global busy_auto_migration 
    global busy_auto_scaling 
    global busy_auto_consolidation 

    global job_auto_deployment 
    global job_auto_migration 
    global job_auto_scaling 
    global job_auto_consolidation
    
    global anomaly_vnfs 

   
    while(True):
       
        #TODO migration should considered when consolidation activated
        busy_auto_migration = True
        if status_auto_migration == True:
            if len(anomaly_vnfs) > 0:
                for vnf in anomaly_vnfs:
                    if status_auto_migration == True: #Once more check!
                        ni_migration_api.auto_migration(vnf)
                    
                anomaly_vnfs = []
        busy_auto_migration = False
        time.sleep(3.3)
    

    return

#Orchestration
def monitor_scaling():
    global status_auto_deployment
    global status_auto_migration 
    global status_auto_scaling
    global status_auto_consolidation 
    
    global busy_auto_deployment 
    global busy_auto_migration 
    global busy_auto_scaling 
    global busy_auto_consolidation 

    global job_auto_deployment 
    global job_auto_migration 
    global job_auto_scaling 
    global job_auto_consolidation 
    
    while(True):
        #TODO scaling name should be changed as scaling id (Cuz it could be duplicated)
        
        print("job_auto_deployment : ", job_auto_deployment)
        print("job_auto_scaling :", job_auto_scaling)
        print("job_auto_migration :", job_auto_migration)
        print("job_auto_consolidation :", job_auto_scaling)
        
        if status_auto_consolidation == True:
            print("Consolidation is worked now. no more vnf can be scaled.")
        elif len(job_auto_consolidation) == 0 : 
            busy_auto_scaling = True
            if status_auto_scaling == True:
                sfcs = ni_nfvo_sfc_api.get_sfcs()
                for sfc in sfcs:
                    if sfc.sfc_name not in job_auto_scaling:
                        if status_auto_scaling == True: #Once more check!
                            scaling_info = DQN_ScalingInfo(sfc_name=sfc.sfc_name, scaling_name=sfc.sfc_name, slo= as_slo, interval=as_interval, duration=as_duration, has_dataset=as_has_dataset)
                            ni_auto_scaling_api.create_scaling(scaling_info)
                            job_auto_scaling.append(sfc.sfc_name)
            elif status_auto_scaling == False:
                for scaling in job_auto_scaling:
                    ni_auto_scaling_api.delete_scaling(scaling)            
                job_auto_scaling = []
                
                while(True):
                    active_scaling = ni_auto_scaling_api.get_all_scaling()
                    if len(active_scaling) == 0:
                        break
                    else :
                        print("waiting for cleaning auto_scaling")
                        time.sleep(5)
            busy_auto_scaling = False
            
        time.sleep(4.41)
        
    return
    
    

#Orchestration
def monitor_consolidation():
    global status_auto_deployment
    global status_auto_migration 
    global status_auto_scaling
    global status_auto_consolidation 
    
    global busy_auto_deployment 
    global busy_auto_migration 
    global busy_auto_scaling 
    global busy_auto_consolidation 

    global job_auto_deployment 
    global job_auto_migration 
    global job_auto_scaling 
    global job_auto_consolidation 

    while(True):
        busy_auto_consolidation = True
        if status_auto_consolidation == True and len(job_auto_consolidation) == 0:
            status_auto_deployment = False
            status_auto_scaling = False
            
            while(True): #TODO When deployment is worked, need to wait. should be fixed. currently only focusing auto_scaling
                if len(job_auto_scaling) == 0 :
                    break
                time.sleep(5)
                
            
            ni_consolidation_api.auto_consolidation()
            job_auto_consolidation.append("running")
            #TODO We suppose False but need to set up more detaily (imagine consolidation function is online but not trun off all nodes)
        
        elif status_auto_consolidation == False and len(job_auto_consolidation)>1:
        
            ni_consolidation_api.remove_consolidation()
            job_auto_consolidation = []
            
            status_auto_deployment = True
            status_auto_scaling = True          
    
        time.sleep(7.17)
        busy_auto_consolidation = False

    return



