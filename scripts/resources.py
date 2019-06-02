#!/usr/bin/python2
# RUNBOOK ON
import subprocess
import requests
import adal
import os
import json
import sys
import glob
import argparse
import ast
# RUNBOOK OFF
scwd=os.getcwd()
#print scwd
head, tail = os.path.split(scwd)
os.chdir(head)
cwd=os.getcwd()
head, tail = os.path.split(cwd)
newd=head+"/scripts"
os.chdir(newd)
#print os.getcwd()
# RUNBOOK ON
# RUNBOOK INLINE
import azurerm_resources
import azurerm_resource_group
import azurerm_management_lock
import azurerm_user_assigned_identity
import azurerm_availability_set
import azurerm_route_table
import azurerm_application_security_group
import azurerm_network_security_group
import azurerm_virtual_network
import azurerm_subnet
import azurerm_virtual_network_peering
import azurerm_managed_disk
import azurerm_storage_account
import azurerm_key_vault
import azurerm_public_ip
import azurerm_traffic_manager_profile
import azurerm_traffic_manager_endpoint
import azurerm_network_interface
import azurerm_dns_zone
import azurerm_lb
import azurerm_lb_nat_rule
import azurerm_lb_nat_pool
import azurerm_lb_backend_address_pool
import azurerm_lb_probe
import azurerm_lb_rule
import azurerm_application_gateway

import azurerm_local_network_gateway
import azurerm_virtual_network_gateway
import azurerm_virtual_network_gateway_connection # --
import azurerm_express_route_circuit 
import azurerm_express_route_circuit_authorization
import azurerm_express_route_circuit_peering  # --
import azurerm_container_registry
import azurerm_kubernetes_cluster
import azurerm_recovery_services_vault 
import azurerm_virtual_machine
import azurerm_virtual_machine_scale_set
import azurerm_automation_account
import azurerm_log_analytics_workspace
import azurerm_log_analytics_solution
import azurerm_image
import azurerm_snapshot
import azurerm_network_watcher
import azurerm_cosmosdb_account
import azurerm_servicebus_namespace
import azurerm_servicebus_queue
import azurerm_sql_server
import azurerm_sql_database
import azurerm_databricks_workspace
import azurerm_app_service_plan
import azurerm_app_service
import azurerm_function_app
import azurerm_monitor_autoscale_setting

# RUNBOOK OFF
os.chdir(scwd)
#print os.getcwd()

parser = argparse.ArgumentParser(description='terraform sub rg')
parser.add_argument('-s', help='Subscription Id')
parser.add_argument('-g', help='Resource Group')
parser.add_argument('-r', help='Filter azurerm resource')
parser.add_argument('-d', help='Debug')
args = parser.parse_args()
csub=args.s
crg=args.g
crf=args.r
deb=args.d
    
# RUNBOOK ON
cde=False
az2tfmess="# File generated by az2tf see: https://github.com/andyt530/az2tf \n"

# RUNBOOK OFF
if csub is not None:
    print("sub=" + csub) 
    # validate sub
if crg is not None:
    print("resource group=" + crg)
    # validate rg
if crf is not None:
    print("resource filter=" + crf)
    # validate resource
if deb is not None:
    cde=True

if sys.version_info[0] > 2:
    #raise Exception("Must be using Python 2")
    print("Python version ", sys.version_info[0], " version 2 required, Exiting")
    exit()

def printf(format, *values):
    print(format % values )

# cleanup files with Python
#tffile=tfp+"*.tf"
#fileList = glob.glob(tffile) 
# Iterate over the list of filepaths & remove each file.
#for filePath in fileList:
#    try:
#        os.remove(filePath)
#    except:
#        print("Error while deleting file : ", filePath)


#with open(filename, 'w') as f:
    #print >> f, 'Filename:'


#tenant = os.environ['TENANT']
#authority_url = 'https://login.microsoftonline.com/' + tenant
#client_id = os.environ['CLIENTID']
#client_secret = os.environ['CLIENTSECRET']
#resource = 'https://management.azure.com/'
#context = adal.AuthenticationContext(authority_url)
#token = context.acquire_token_with_client_credentials(resource, client_id, client_secret)
#headers = {'Authorization': 'Bearer ' + token['accessToken'], 'Content-Type': 'application/json'}
#params = {'api-version': '2016-06-01'}
#url = 'https://management.azure.com/' + 'subscriptions'
#r = requests.get(url, headers=headers, params=params)
#print(json.dumps(r.json(), indent=4, separators=(',', ': ')))

print "Get Access Token from CLI"
p = subprocess.Popen('az account get-access-token -o json', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
c=0
for line in p.stdout.readlines():
    if "accessToken" in line:
        tk=line.split(":")[1].strip(' ",')
        tk2=tk.replace(",", "")
        bt2=tk2.replace('"', '')
    if "subscription" in line:
        tk=line.split(":")[1].strip(' ",')
        tk2=tk.replace(",", "")
        sub2=tk2.replace('"', '')
retval = p.wait()
if csub is not None:
    sub=csub
else:
    sub=sub2.rstrip('\n')



bt=bt2.rstrip('\n')
print "Subscription:",sub
headers = {'Authorization': 'Bearer ' + bt, 'Content-Type': 'application/json'}


# subscription check
#https://management.azure.com/subscriptions?api-version=2014-04-01
# print "REST Subscriptions ",
url="https://management.azure.com/subscriptions"
params = {'api-version': '2014-04-01'}
try: 
    r = requests.get(url, headers=headers, params=params)
    subs= r.json()["value"]
except KeyError:
    print "Error getting subscription list"
    exit("ErrorGettingSubscriptionList")
#print(json.dumps(subs, indent=4, separators=(',', ': ')))
#ssubs=json.dumps(subs)
#print ssubs
#if sub not in ssubs: 
#    print "Could not find subscription with ID " + sub + " Exiting ..." 
#    exit("ErrorInvalidSubscriptionID-1")


#print(json.dumps(subs, indent=4, separators=(',', ': ')))

FoundSub=False
count=len(subs)

for i in range(0, count):
    id=str(subs[i]["subscriptionId"])
    #print id + " " + sub
    if id == sub:
        FoundSub=True

if not FoundSub:
    print "Could not find subscription with ID (Test 2) " + sub + " Exiting ..." 
    #exit("ErrorInvalidSubscriptionID-2")

# RUNBOOK ON
print "Found subscription " + sub + " proceeding ..."
# RUNBOOK OFF
if crg is not None:
    FoundRg=False
    # get and check Resource group
    url="https://management.azure.com/subscriptions/" + sub + "/resourceGroups"
    params = {'api-version': '2014-04-01'}
    r = requests.get(url, headers=headers, params=params)
    rgs= r.json()["value"]

    count=len(rgs)
    for j in range(0, count):    
        name=rgs[j]["name"]
        if crg.lower() == name.lower():
            print "Found Resource Group" + crg
            FoundRg=True

    if not FoundRg:
        print "Could not find Resource Group " + crg + " in subscription " + sub + " Exiting ..." 
        exit("ErrorInvalidResourceGroup")


if os.path.exists("tf-staterm.sh"):
    os.remove('tf-staterm.sh')
if os.path.exists("tf-stateimp.sh"):
    os.remove('tf-stateimp.sh')

# RUNBOOK ON
if crf is None:
    crf="azurerm"


# record and sort resources
#azurerm_resources.azurerm_resources(crf,cde,crg,headers,requests,sub,json,az2tfmess,os)
# 001 Resource Group
azurerm_resource_group.azurerm_resource_group(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 002 management locks

azurerm_management_lock.azurerm_management_lock(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 015 user assigned identity
azurerm_user_assigned_identity.azurerm_user_assigned_identity(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  020 Avail Sets

azurerm_availability_set.azurerm_availability_set(crf,cde,crg,headers,requests,sub,json,az2tfmess)

#  030 Route Table
azurerm_route_table.azurerm_route_table(crf,cde,crg,headers,requests,sub,json,az2tfmess)

# 040 ASG
azurerm_application_security_group.azurerm_application_security_group(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  050 NSG's
azurerm_network_security_group.azurerm_network_security_group(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  060 Virtual Networks
azurerm_virtual_network.azurerm_virtual_network(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  070 subnets
azurerm_subnet.azurerm_subnet(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  080 vnet peering
azurerm_virtual_network_peering.azurerm_virtual_network_peering(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 090 Key Vault - using cli
azurerm_key_vault.azurerm_key_vault(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 100 managed disk
azurerm_managed_disk.azurerm_managed_disk(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#110 storgae account
azurerm_storage_account.azurerm_storage_account(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#120 public ip
azurerm_public_ip.azurerm_public_ip(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  124 Traffic manager profile
azurerm_traffic_manager_profile.azurerm_traffic_manager_profile(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  125 traffic manager endpoint
azurerm_traffic_manager_endpoint.azurerm_traffic_manager_endpoint(crf,cde,crg,headers,requests,sub,json,az2tfmess)
#  130 network interface
azurerm_network_interface.azurerm_network_interface(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 131_azurerm_dns_zone
azurerm_dns_zone.azurerm_dns_zone(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 140_azurerm_lb
azurerm_lb.azurerm_lb(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 150_azurerm_lb_nat_rule
azurerm_lb_nat_rule.azurerm_lb_nat_rule(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 160_azurerm_lb_nat_pool
azurerm_lb_nat_pool.azurerm_lb_nat_pool(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 170_azurerm_lb_backend_address_pool
azurerm_lb_backend_address_pool.azurerm_lb_backend_address_pool(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 180_azurerm_lb_probe
azurerm_lb_probe.azurerm_lb_probe(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 190_azurerm_lb_rule
azurerm_lb_rule.azurerm_lb_rule(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 193_azurerm_application_gateway
azurerm_application_gateway.azurerm_application_gateway(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 200_azurerm_local_network_gateway
azurerm_local_network_gateway.azurerm_local_network_gateway(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 210_azurerm_virtual_network_gateway
azurerm_virtual_network_gateway.azurerm_virtual_network_gateway(crf,cde,crg,headers,requests,sub,json,az2tfmess)

#----
# 220_azurerm_virtual_network_gateway_connection
azurerm_virtual_network_gateway_connection.azurerm_virtual_network_gateway_connection(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 230_azurerm_express_route_circuit
azurerm_express_route_circuit.azurerm_express_route_circuit(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 240_azurerm_express_route_circuit_authorization
azurerm_express_route_circuit_authorization.azurerm_express_route_circuit_authorization(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 250_azurerm_express_route_circuit_peering
azurerm_express_route_circuit_peering.azurerm_express_route_circuit_peering(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# ----

# 260_azurerm_container_registry
azurerm_container_registry.azurerm_container_registry(crf,cde,crg,headers,requests,sub,json,az2tfmess)

# 270_azurerm_kubernetes_cluster
azurerm_kubernetes_cluster.azurerm_kubernetes_cluster(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 280_azurerm_recovery_services_vault
azurerm_recovery_services_vault.azurerm_recovery_services_vault(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 290_azurerm_virtual_machine
azurerm_virtual_machine.azurerm_virtual_machine(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 295_azurerm_virtual_machine_scale_set

azurerm_virtual_machine_scale_set.azurerm_virtual_machine_scale_set(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 310_azurerm_automation_account

azurerm_automation_account.azurerm_automation_account(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 320_azurerm_log_analytics_workspace
azurerm_log_analytics_workspace.azurerm_log_analytics_workspace(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 330_azurerm_log_analytics_solution
azurerm_log_analytics_solution.azurerm_log_analytics_solution(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 340_azurerm_image

azurerm_image.azurerm_image(crf,cde,crg,headers,requests,sub,json,az2tfmess)
cde=False
# 350_azurerm_snapshot
azurerm_snapshot.azurerm_snapshot(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 360_azurerm_network_watcher
azurerm_network_watcher.azurerm_network_watcher(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 400_azurerm_cosmosdb_account
azurerm_cosmosdb_account.azurerm_cosmosdb_account(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 500_azurerm_servicebus_namespace
azurerm_servicebus_namespace.azurerm_servicebus_namespace(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 510_azurerm_servicebus_queue
azurerm_servicebus_queue.azurerm_servicebus_queue(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 540_azurerm_sql_server
azurerm_sql_server.azurerm_sql_server(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 541_azurerm_sql_database
azurerm_sql_database.azurerm_sql_database(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 550_azurerm_databricks_workspace
azurerm_databricks_workspace.azurerm_databricks_workspace(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 600_azurerm_app_service_plan
azurerm_app_service_plan.azurerm_app_service_plan(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 610_azurerm_app_service
azurerm_app_service.azurerm_app_service(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 620_azurerm_function_app
azurerm_function_app.azurerm_function_app(crf,cde,crg,headers,requests,sub,json,az2tfmess)
# 650_azurerm_monitor_autoscale_setting
azurerm_monitor_autoscale_setting.azurerm_monitor_autoscale_setting(crf,cde,crg,headers,requests,sub,json,az2tfmess)

# ******************************************************************************************
exit()



