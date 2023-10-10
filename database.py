
import mysql.connector
import config_tmp
from logger import logger

class getDb:

    def __init__(self):
        self.db = mysql.connector.connect(
        host=config_tmp.database_host,
        user=config_tmp.database_user,
        password=config_tmp.database_password,
        database=config_tmp.database_name )
        self.cursor = self.db.cursor(buffered=True)

    def get(self):
        return self.db, self.cursor

    def close(self):
        try:
            self.cursor.close()
            self.db.close()
        except:
            logger.error("Error while closing MySQL cursor and connection")