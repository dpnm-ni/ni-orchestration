import connexion
import six



import threading
import time
from server import util
import orchestration as oc

def get_status():

    status = "auto_deployment : {}\nauto_migration : {}\nauto_scaling : {}\nauto_consolidation : {}".format(oc.status_auto_deployment, oc.status_auto_migration, oc.status_auto_scaling, oc.status_auto_consolidation)

    return status

def simulated_anomaly(vnf_id):
    oc.anomaly_vnfs.append(vnf_id)

    return "Success to simulated anomaly symptoms for vnf:{}".format(vnf_id)

def common_activating():


    oc.status_auto_deployment = True
    oc.status_auto_migration = True
    oc.status_auto_scaling = True

    return "success"


def all_deactivating():

    oc.status_auto_deployment = False
    oc.status_auto_migration = False
    oc.status_auto_scaling = False
    oc.status_auto_consolidation = False
    return "success"


def auto_deployment_on():
    if oc.status_auto_deployment == True:
        msg = "auto_deployment is already activated"
        print(msg)
        return msg
    else :
        oc.status_auto_deployment = True
        msg = "auto_deployment is activated!"
        print(msg)
        return msg


def auto_deployment_off():
    if oc.status_auto_deployment == False:
        msg = "auto_deployment is already dead"
        print(msg)
        return msg
    else :
        oc.status_auto_deployment = False
        msg = "auto_deployment is going to die!"
        print(msg)
        return msg


def auto_migration_on():
    if oc.status_auto_migration == True:
        msg = "auto_migration is already activated"
        print(msg)
        return msg
    else :
        oc.status_auto_migration = True
        msg = "auto_migration is activated!"
        print(msg)
        return msg


def auto_migration_off():
    if oc.status_auto_migration == False:
        msg = "auto_migration is already dead"
        print(msg)
        return msg
    else :
        oc.status_auto_migration = False
        msg = "auto_migration is going to die!"
        print(msg)
        return msg
 
 
def auto_scaling_on():
    if oc.status_auto_scaling == True:
        msg = "auto_scaling is already activated"
        print(msg)
        return msg
    else :
        oc.status_auto_scaling = True
        msg = "auto_scaling is activated!"
        print(msg)
        return msg


def auto_scaling_off():
    if oc.status_auto_scaling == False:
        msg = "auto_scaling is already dead"
        print(msg)
        return msg
    else :
        oc.status_auto_scaling = False
        msg = "auto_scaling is going to die!"
        print(msg)
        return msg


def auto_consolidation_on():
    if oc.status_auto_consolidation == True:
        msg = "auto_consolidation is already activated"
        print(msg)
        return msg
    else :
        oc.status_auto_consolidation = True
        msg = "auto_consolidation is activated!"
        print(msg)
        return msg


def auto_consolidation_off():
    if oc.status_auto_consolidation == False:
        msg = "auto_consolidation is already dead"
        print(msg)
        return msg
    else :
        oc.status_auto_consolidation = False
        msg = "auto_consolidation is going to die!"
        print(msg)
        return msg

#threading.Thread(target=oc.monitor_deployment, args=()).start() 
#threading.Thread(target=oc.monitor_migration, args=()).start()
#threading.Thread(target=oc.monitor_scaling, args=()).start()
#threading.Thread(target=oc.monitor_consolidation, args=()).start()

