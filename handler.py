import os
import datetime
import logging
import psycopg2
from datetime import timedelta,datetime
from psycopg2.extensions import connection, cursor
from requests.adapters import Retry
from requests.adapters import HTTPAdapter
from requests import Session
from writeDataBase import WriteDataBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def initConnectionDatabase() -> tuple[connection,cursor]:
    conn = None
    hostAdr = os.environ.get('host_adress')
    databaseAdr = os.environ.get('dataBase_adress')
    userDB = os.environ.get('user_database')
    passwordDB = os.environ.get('user_password')
    try:
        # connect to the PostgreSQL server
        logger.info('Connecting to the PostgreSQL database...')
        conn: connection = psycopg2.connect(host=hostAdr, database=databaseAdr, user=userDB, password=passwordDB)
		
        # create a cursor
        cur = conn.cursor()
        
        logger.info('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        logger.info(db_version)
       
        return conn,cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def requests_retry_session(retries=4,backoff_factor=0.5,status_forcelist=(500, 502, 504),session=None):
    session = session or Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def getInformationExternalAPI() -> dict:
    today = datetime.today().date()
    before = today - timedelta(days=1)
    beforestr = before.strftime("%Y-%m-%d")
    todaystr = today.strftime("%Y-%m-%d")
    url = 'http://api.external.com.br/v2/orders?createdAfter={}&createdBefore={}'.format(beforestr,todaystr)
    headers = {
        'Token': os.environ.get('api_key_external'),
        'Content-Type': "application/json",
    }
    try:
        response = requests_retry_session().get(url, headers=headers)
        responseDict = response.json()
        return responseDict
    except:
        logger.info('Error with request external API data')

def run(event, context):
    logger.info('Init lambda')
    connector,cursor = initConnectionDatabase()
    logger.info('Get external data')
    dictDataFromExternalEndpoint = getInformationExternalAPI()
    logger.info(dictDataFromExternalEndpoint)
    logger.info('end lambda')


