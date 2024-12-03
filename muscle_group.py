import pandas as pd
from utils.config import EXERCISE_DB_PATH

class DataHandler:
    def __init__(self):
        self.exercise_db = pd.read_csv(EXERCISE_DB_PATH)

    def get_exercise_names(self):
        return sorted(self.exercise_db['exercise name'].unique())

    def get_muscle_groups(self, exercise_name):
        # Find the exercise entry by name
        exercise_data = self.exercise_db[self.exercise_db['exercise name'] == exercise_name]
        if not exercise_data.empty:
            main_muscle = exercise_data['Main muscle group'].iloc[0]
            secondary_muscle = exercise_data['Sub muscle group'].iloc[0] if pd.notna(exercise_data['Sub muscle group'].iloc[0]) else None
            return main_muscle, secondary_muscle
        return None, None
