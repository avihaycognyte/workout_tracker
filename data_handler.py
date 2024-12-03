import sqlite3
from utils.config import DB_FILE


class DataHandler:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)

    def get_exercise_names(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT exercise_name FROM exercises")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_muscle_groups(self, exercise_name):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT main_muscle_group, sub_muscle_group FROM exercises WHERE exercise_name = ?",
            (exercise_name,)
        )
        result = cursor.fetchone()
        if result:
            main_muscle, secondary_muscle = result
            return main_muscle, secondary_muscle
        return None, None

    def close_connection(self):
        self.conn.close()
