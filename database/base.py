import sqlite3

class BaseDatabase:
    def __init__(self, db_name="bookclub.db"):
        self.connection = sqlite3.connect(db_name)

    def execute_query(self, query, params=()):
        with self.connection:
            return self.connection.execute(query, params)

    def fetch_all(self, query, params=()):
        return self.connection.execute(query, params).fetchall()

    def fetch_one(self, query, params=()):
        return self.connection.execute(query, params).fetchone()
