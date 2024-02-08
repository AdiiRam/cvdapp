import logging
import json
import configparser

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

FULL_MODE = 'full'
INCREMENTAL_MODE = 'incremental'

# Create a configparser object
config = configparser.ConfigParser()

# Read the INI file
config.read('config.ini')

# Access config values
DBHOST = config['Database']['host']
DBPORT = config['Database']['port']
if DBPORT == 'None':
    DBPORT = None
DBUSER = config['Database']['username']
DBPASSWORD = config['Database']['password']
DBNAME = config['Database']['database']
DBCOLLECTION = config['Database']['collection']

DEFAULT_RESULTS_PER_PAGE = int(config['LoadMode']['results_per_page'])

TESTRUN = config['TestRun']['enabled']
TEST_FETCH_LIMIT_PAGES = int(config['TestRun']['no_of_pages'])

if TESTRUN == 'no':
    IS_TEST = False
else:
    IS_TEST = True

BASE_API = config['CVEAPI']['base_api']
MODE = config['LoadMode']['mode']


def get_logger(logname):

    return logging.getLogger(logname)


def get_last_runtime():

    with open('incremental_mode.json') as fin:
        jsdata = json.load(fin)

    return jsdata['lastrun']


def update_last_runtime(lastrun):

    jsdata = {
        'lastrun': lastrun
    }
    with open('incremental_mode.json', 'w') as fout:
        json.dump(jsdata, fout)


class InvalidMode(Exception):
    """
    A custom exception class.
    """

    def __init__(self, message="An invalid mode is provided"):
        """
        Initialize the custom exception with an optional error message.

        Args:
            message (str): Optional error message.
        """
        self.message = message
        super().__init__(self.message)
