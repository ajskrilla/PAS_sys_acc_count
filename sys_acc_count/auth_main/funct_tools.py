import requests
import csv
import json
import traceback
from .utility import logging as log


def boolize(v):
    return {
        "TRUE": True,
        "FALSE": False,
    }.get(v.upper() if hasattr(v,"upper") else "", v)
def sanitizedict(d):
    return {k:boolize(v) for k,v in d.items() if v!= ""}

def rem_null(args):
    return dict((k, v) for k, v in args.items() if v != None)

#RedRock Query
# Make Header as an argument for cache as well as tenant
class query_request:
    def __init__(self, sql, url, header, Debug=False):
        q_url = "{0}/Redrock/Query".format(url)
        log.info("Starting Query Request....")
        log.info("Query is: {0}".format(sql))
        try:
            self.query_request = requests.post(url=q_url, headers=header, json={"Script": sql}).json()
        except Exception as e:
            log.error("Internal error occurred. Please note it failed on a Query request.")
            log.error(traceback.print_exc(e))
        self.jsonlist = json.dumps(self.query_request)
        self.parsed_json = (json.loads(self.jsonlist))
        if self.parsed_json['success'] == False:
            log.error("Issue with Query. Dump is: {0}".format(self.jsonlist))
        log.debug("JSON dump of Query is : {0}".format(self.jsonlist))
        log.info("Finished Query")
        if Debug == True:
            print(json.dumps(self.parsed_json, indent=4, sort_keys=True))

#for other requests
# Make Header as an argument for cache as well as tenant
class other_requests:
    def __init__(self, Call, url, header, Debug=False, **kwargs):
        r_call = '{0}{1}'.format(url, Call)
        self.kwargs = kwargs
        self.__dict__.update(**self.kwargs)
        try:
            log.info("Starting request...")
            log.info("Endpoint is: {0}".format(Call))     
            self.other_requests = requests.post(url=r_call, headers=header, json=self.kwargs).json()
        except Exception as e:
            log.error("Internal error occurred. Please note it failed on an other request")
            log.error(traceback.print_exc(e))
        self.jsonlist = json.dumps(self.other_requests)
        self.parsed_json = (json.loads(self.jsonlist))
        if self.parsed_json['success'] == False:
            log.error("Issue with other request. Dump is: {0}".format(self.jsonlist))
        log.debug("JSON dump of request is : {0}".format(self.jsonlist))
        log.info("Finished request")
        if Debug == True:
            print(json.dumps(self.parsed_json, indent=4, sort_keys=True))

# Check CSV headers and stop if they are not good
def csv_h_check(csv_file, *headers):
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        d_reader = csv.DictReader(f)   
        c_headers = d_reader.fieldnames
        log.info("Checking the headers: {0}".format(list(headers)))
        if list(sorted(headers)) != sorted(c_headers):
            log.error("Header values are: {0}".format(c_headers))
            log.error("This CSV is not compatible. Exiting.")
            raise SystemExit(0)
        else:
            log.info("CSV file is good")
            pass

# Security check and bail if not good
def sec_test(tenant, header, **ignored):
    log.info("Going to do a security test and verify that the connection can occur, if not, will drop")
    log.info("Testing the connection for tenant: {0}".format(tenant))
    check = other_requests("/Security/Whoami", tenant, header).parsed_json
    if check['success'] == False:
        log.error("Serious issue occurred, will not continue.")
        raise SystemExit(0)
    log.info("Tenant: {0}".format(check['Result']["TenantId"]))
    log.info("User: {0}".format(check['Result']["User"]))
    log.debug("UserUuid: {0}".format(check['Result']["UserUuid"]))
    log.info("Passed the test")