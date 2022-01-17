import csv
import os
import json
from cachetools import TTLCache
import logging 
import traceback
import getpass
import requests
# Check for DMC and if not installed, let user know and continue
try:
    from dmc import gettoken
except ImportError:
    logging.warning("Please use pip install centrify.dmc to use DMC auth")

class f_check:
    def __init__(self):
        f_path = os.path.join(os.path.dirname(__file__), 'conf', 'config.json')
        with open(f_path, 'r') as json_file:
            self.loaded = json.load(json_file)

f = f_check()

try:
    level = logging.getLevelName(f.loaded['debug_level'])
except:
    logging.basicConfig(level = logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S', \
    format='%(asctime)s %(name)s %(levelname)-8s %(message)s')
else:
    logging.basicConfig(level = level, datefmt='%Y-%m-%d %H:%M:%S', \
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s')

# For the OAUTH process

class auth:
    def __init__(self, *args, **kwargs):
        if kwargs['auth'].upper() == 'DMC':
            logging.info('Setting auth headers for DMC......')
            self._headers = {}
            self._headers["X-CENTRIFY-NATIVE-CLIENT"] = 'true'
            self._headers['X-CFY-SRC' ]= 'python'
            try:
                logging.info("DMC scope is: {scope}".format(**kwargs))
                # Really did not want to do this
                scope = gettoken(kwargs['scope'])
                self._headers['Authorization']  = 'Bearer {0}'.format(scope)
            except KeyError:
                logging.error('Issue with getting DMC scope')
                raise Exception
        elif kwargs['auth'].upper() == 'OAUTH':
            # If statement to handle the non PW assumption
            logging.info("Going to authenticate Oauth account: {client_id}".format(**kwargs['body'])) 
            # Handle the fact that client_secret can be added to the config file and skip the ask
            self.json_d = json.dumps(kwargs['body'])
            self.update = json.loads(self.json_d)
            self.update['scope'] = kwargs['scope']
            self.update['client_secret'] = '{0}'.format(*args)
            self._rheaders = {}
            self._rheaders['X-CENTRIFY-NATIVE-CLIENT'] = 'true'
            self._rheaders['Content-Type'] = 'application/x-www-form-urlencoded'
            logging.info('Oauth URL of app is: {tenant}/Oauth2/Token/{appid}'.format(**kwargs, **kwargs['body'])) 
            logging.info('Oauth token request Headers are: {}'.format(self._rheaders)) 
            try:
                logging.info('Setting auth headers for OAUTH......')
                req = requests.post(url='{tenant}/Oauth2/Token/{appid}'.format(**kwargs, **kwargs['body']), headers= self._rheaders, data= self.update).json()
            except Exception as e:
                logging.error(traceback.print_exc(e))
                logging.error("Issue getting token")
                logging.error("Response: {0}".format(json.dumps(req)))
            self._headers = {}
            self._headers["Authorization"] = "Bearer {access_token}".format(**req)
            self._headers["X-CENTRIFY-NATIVE-CLIENT"] = 'true'
        else:
            logging.error("Not valid auth type. Please fix")
    @property
    def headers(self):
        return self._headers

# Cache class that utilizes the auth class

class Cache:
    def __init__(self, *args, **kwargs):
        # Make TTL setting to grab in conf file next to debug
        self._cache = TTLCache(maxsize=10, ttl=600)
        try:
            logging.info("Building the cache..")
            self._cache['header'] = auth(*args, **kwargs).headers
            self._cache['tenant'] = kwargs['tenant']
        except Exception as e:
            logging.error("Failed to build cache")
            logging.error(traceback.print_exc(e))
            raise SystemExit(0)
    @property
    def ten_info(self):
        return self._cache
    @property
    def dump(self):
        logging.info("Dumping the cache.")
        self._cache.clear()