import connexion
import six



import threading
import time
from server import util
from orchestration import *




def activate_orchestration():
    if (not orchestration_activated):
        threading.Thread(target=manager(),args=()).start()#args=
        threading.Thread(target=auto_deployment(),args=()).start() #Deployment
   
    return (not orchestration_activated)


def get_orchestration_prefix_list():
    
    return orchestration_prefix_list



def add_orchestration_prefix(sfc_prefix):
    #if connexion.request.is_json:
    #body = Threshold_ScalingInfo.from_dict(connexion.request.get_json())

    for item in sfc_prefix:
       remove_prefix_duplicates_then_add(orchestration_prefix_list, item)

    return orchestration_prefix_list

def remove_orchestration_prefix(sfc_prefix):

    for item in sfc_prefix:
       if item in orchestration_prefix_list:
           orchestration_prefix_list.remove(item)

    return orchestration_prefix_list
