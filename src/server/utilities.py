import os
import sqlite3


class DBAgent:
    def execute_query(self, query, parameters=()):
        conn = sqlite3.connect(self.get_db_path())
        c = conn.cursor()
        c.execute(query, parameters)
        conn.commit()
        conn.close()

    def get_db_path(self) -> str:
        app_path = os.path.abspath(__file__)
        app_dir = os.path.dirname(app_path)
        db_path = os.path.join(app_dir, "alexa_skills_management.db")
        return db_path
