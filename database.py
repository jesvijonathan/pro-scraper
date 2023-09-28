
import mysql.connector
import config

class getDb:

    def __init__(self):
        self.db = mysql.connector.connect(
        host=config.database_host,
        user=config.database_user,
        password=config.database_password,
        database=config.database_name )
        self.cursor = self.db.cursor(buffered=True)

    def get(self):
        return self.db, self.cursor

    def close(self):
        self.cursor.close()
        self.db.close()