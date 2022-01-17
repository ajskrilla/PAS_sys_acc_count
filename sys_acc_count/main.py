#! /usr/bin/env python3
import argparse
from auth_main.funct_tools import *
from auth_main.utility import Cache, f_check, logging as log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save a query as a csv. Please give valid SQL query to tenant.")
    parser.add_argument('-pw','--Password', type=str, required=False, help= 'Password of service account from config file.')
    # ID for test folder 47fc0dcb-fd9b-41c7-b60a-454a7652bc44
    args = parser.parse_args()
# Create the object for the file
f = f_check()
# Build cache. Need to move cond to the module
if args.Password:
    c = Cache(args.Password, **f.loaded['tenants'][0])
else:
    c = Cache(**f.loaded['tenants'][0])
# Security test
sec_test(**c.ten_info)
# Going to go get the Secret Folder and contents
def get_count(tenant, header, **ignored):
    log.info("Getting a count of all accounts and systems in tenant: {tenant}".format(**f.loaded['tenants'][0]))
    # Account info
    log.info("First, its getting account info...")
    acc_q = query_request("SELECT VaultAccount.UserDisplayName FROM VaultAccount", tenant, header).parsed_json["Result"]
    acc_count = acc_q["Count"]
    for raw in acc_q['Results']:
        acc_info = raw['Row']['UserDisplayName']
        log.debug("Name is: {0}".format(acc_info))
    log.info("Count of accounts is: {0}".format(acc_count))
    # System info
    sys_q = query_request("SELECT Server.FQDN FROM Server", tenant, header).parsed_json["Result"]
    sys_count = sys_q['Count']
    for raw in sys_q['Results']:
        sys_info = raw['Row']['FQDN']
        log.debug("Name is: {0}".format(sys_info))
    log.info("Count of systems is: {0}".format(sys_count))
# Execute funtion
get_count(**c.ten_info)