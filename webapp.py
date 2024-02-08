from constants import get_logger, DBNAME, DBCOLLECTION
from dbutils import DBUtil
from fastapi import FastAPI

LOGGER = get_logger('webapp')

dbutil = DBUtil(dbname=DBNAME, dbcollection=DBCOLLECTION)
app = FastAPI()


@app.get("/")
def read_root():
    return "WebApp to Fetch CVE Details"


@app.get("/cve/{cve_id}")
def get_cve_by_id(cve_id: str):

    return dbutil.get_by_id(cve_id=cve_id)


@app.get("/cve/")
def get_cve_by_qparams(last_modified: int | None = None, score: float | None = None):

    qparams = {}
    if last_modified:
        qparams['last_modified'] = last_modified
    if score:
        qparams['score'] = score

    return dbutil.get_by_qparams(qparams)
