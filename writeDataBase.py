from datetime import datetime, timedelta
import json
import numpy as np
import psycopg2
import logging
from psycopg2.extensions import connection, cursor

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class WriteDataBase:

    def __init__(self,connectionDB: connection,cursorDB: cursor,logger: logging):
        self.connectionDB = connectionDB
        self.cursorDB = cursorDB
        self.logger = logger
    
    def insertItem(self,data) -> bool:
        insert = """
        INSERT INTO tableName (
            user_id, 
            store_id,
            client_data,
            products,
            created_at,
            json_data
            )
        VALUES( %s , %s , %s , %s , %s , %s );
        """
        try:
            json_data = json.dumps(data['json_value'], cls=NpEncoder)
            self.logger.info(json_data)
            self.logger.info("\n")

            products = {}
            for idx,prd in enumerate(data['products']):
                products[idx] = prd['id']
            products = json.dumps(products,cls=NpEncoder)
            self.logger.info(products)

            self.cursorDB.execute(insert,(
                int(data['user']['id']),
                int(data['storeId']),
                data['client_data'],
                products,
                datetime.now(),
                json_data
                )
            )
            self.connectionDB.commit()
            if self.cursorDB.rowcount > 0:
                self.logger.info("Insert data sucess")
                return True
            else:
                self.logger.info("No insert data")
                return False
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.info(error)