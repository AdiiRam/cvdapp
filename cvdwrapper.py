from datetime import datetime
from constants import get_logger
from constants import DEFAULT_RESULTS_PER_PAGE
from constants import FULL_MODE, INCREMENTAL_MODE
from constants import get_last_runtime, update_last_runtime
from constants import InvalidMode, IS_TEST, TEST_FETCH_LIMIT_PAGES
from constants import BASE_API, DBNAME, DBCOLLECTION, MODE
import requests
from dbutils import DBUtil


# Creating a logger object
LOGGER = get_logger('cvdwrapper')


class CVDAPIWrapper:

    def __init__(self, base_api, dbname, dbcollection, **kwargs) -> None:
        self.base_api = base_api
        self.kwargs = kwargs
        self.request_client = requests.Session()
        self.dbutil = DBUtil(dbname=dbname, dbcollection=dbcollection)

    def api_fetch(self, start_index=0, results_per_page=DEFAULT_RESULTS_PER_PAGE, **kwargs):
        payload = {
            'startIndex': start_index,
            'resultsPerPage': results_per_page
        }
        if kwargs:
            payload.update(kwargs)

        LOGGER.info(
            f'Fetching Data:: startIndex:{start_index}, resultsPerPage:{results_per_page}')
        LOGGER.info(f'Fetching Data Params: {payload}')
        response = self.request_client.get(self.base_api, params=payload)
        LOGGER.info('Fetching Data:: Done')
        LOGGER.info(f'Response URL : {response.url}')
        return response

    def get_all_cvds(self, **kwargs):

        stop = False
        start_index = 0
        while not stop:

            resp = self.api_fetch(start_index=start_index, **kwargs)
            try:
                resp.raise_for_status()
                yield resp.json()
                start_index += DEFAULT_RESULTS_PER_PAGE
            except Exception as err:
                LOGGER.error(f'Encountered error: {err}')
                stop = True

    def load_cvds(self, mode=FULL_MODE, is_test=IS_TEST):

        LOGGER.info(f"Run Mode :: {mode}, Is_Test :: {is_test}")
        ctr = 0
        if mode == FULL_MODE:
            LOGGER.info("Running Full Mode")
            for cvdresp in self.get_all_cvds():

                ctr += 1
                vulnerabilities = cvdresp['vulnerabilities']
                cvelist = [item['cve'] for item in vulnerabilities]
                self.dbutil.add_to_collection(cvelist)

                if is_test and ctr > TEST_FETCH_LIMIT_PAGES:
                    break

            update_last_runtime(
                lastrun=datetime.now().isoformat(timespec='seconds'))

        elif mode == INCREMENTAL_MODE:
            LOGGER.info("Running Incremental Mode")
            last_run_time = get_last_runtime()
            last_mod_start_date = last_run_time
            last_mod_end_date = datetime.now().isoformat(timespec='seconds')
            LOGGER.info(
                f"Last Modified Date Range :: {last_mod_start_date} to {last_mod_end_date}")
            for cvdresp in self.get_all_cvds(lastModEndDate=last_mod_end_date, lastModStartDate=last_mod_start_date):
                ctr += 1
                vulnerabilities = cvdresp['vulnerabilities']
                cvelist = [item['cve'] for item in vulnerabilities]
                for cve in cvelist:
                    self.dbutil.update_cve(cve)

                if is_test and ctr > TEST_FETCH_LIMIT_PAGES:
                    break

            update_last_runtime(lastrun=last_mod_end_date)

        else:
            LOGGER.error('Unknown Mode')
            raise InvalidMode(f'Unknown Mode {mode}')


if __name__ == '__main__':

    cvdObject = CVDAPIWrapper(
        base_api=BASE_API, dbname=DBNAME, dbcollection=DBCOLLECTION)
    cvdObject.load_cvds(mode=MODE)
