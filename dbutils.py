from datetime import datetime, timedelta
from constants import DBHOST, DBPASSWORD, DBPORT, get_logger, DBUSER
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

LOGGER = get_logger('dbutil')


class DBUtil:

    def __init__(self, dbname, dbcollection) -> None:

        if DBPORT:
            db_uri = f"mongodb+srv://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/?retryWrites=true&w=majority"
        else:
            db_uri = f"mongodb+srv://{DBUSER}:{DBPASSWORD}@{DBHOST}/?retryWrites=true&w=majority"

        dbclient = MongoClient(db_uri, server_api=ServerApi('1'))

        try:
            dbclient.admin.command('ping')
            LOGGER.info("Successfully connected to MongoDB!")
        except Exception as err:
            LOGGER.exception(f'MongoDB connection failed : {err}')
            raise

        self.db = dbclient[dbname]
        self.collection = self.db[dbcollection]

    def add_to_collection(self, data):

        LOGGER.info('Adding data to collection :: Started')
        self.collection.insert_many(data)
        LOGGER.info('Adding data to collection :: End')

    def update_cve(self, data):

        cve_id = data['id']
        update_criteria = {'id': cve_id}
        LOGGER.info(f'Updating doc for CVEId: {cve_id}')
        self.collection.update_one(
            update_criteria, {"$set": data}, upsert=True)
        LOGGER.info('Update done')

    def get_by_id(self, cve_id):

        LOGGER.info(f"Get CVE By Id : {cve_id}")
        doc = self.collection.find_one({'id': cve_id}, {'_id': 0})
        return doc

    def query_for_score(self, score):

        LOGGER.info(f"Prepare Query for Base Score of {score}")
        score_query = {
            "$or": [
                {"metrics.cvssMetricV2.cvssData.baseScore": {"$eq": score}},
                {"metrics.cvssMetricV31.cvssData.baseScore": {"$eq": score}},
                {"metrics.cvssMetricV30.cvssData.baseScore": {"$eq": score}}
            ]
        }
        LOGGER.info(f"Query: {score_query}")
        return score_query

    def query_for_lastmodified_date(self, no_of_days):

        LOGGER.info(f"Prepare Query for LastModified in {no_of_days} days")
        date_n_days_ago = datetime.now() - timedelta(days=no_of_days)
        date_n_days_ago = date_n_days_ago.isoformat(timespec='seconds')
        query = {"lastModified": {"$gt": date_n_days_ago}}
        LOGGER.info(f"Query: {query}")
        return query

    def get_by_qparams(self, kwargs):

        query_list = []
        for key, val in kwargs.items():
            if key == 'last_modified':
                query_list.append(self.query_for_lastmodified_date(val))
            elif key == 'score':
                query_list.append(self.query_for_score(val))

        final_query = {
            "$and": query_list
        }

        LOGGER.info(f"Final Query :: {final_query}")
        docs = self.collection.find(final_query, {'_id': 0})
        return [doc for doc in docs]
