from utils.database import DatabaseHandler

class BusinessLogic:
    def __init__(self):
        self.db_handler = DatabaseHandler()

    def calculate_weekly_summary(self, method="Total"):
        """
        Calculate the weekly summary based on the provided method.

        :param method: Calculation method - "Total", "Fractional", or "Direct".
        :return: Query results from the database.
        """
        try:
            query = self._get_query_for_method(method)
            return self.db_handler.execute_query(query)
        except Exception as e:
            raise RuntimeError(f"Error calculating weekly summary: {e}")
        finally:
            self.db_handler.close()

    def _get_query_for_method(self, method):
        """
        Get the SQL query for the given calculation method.

        :param method: Calculation method - "Total", "Fractional", or "Direct".
        :return: SQL query string.
        """
        if method == "Total":
            return """
                SELECT
                    muscle_group,
                    ROUND(SUM(total_sets), 2) AS total_sets,
                    ROUND(SUM(total_reps), 2) AS total_reps,
                    ROUND(SUM(total_weight), 2) AS total_weight
                FROM (
                    SELECT
                        e.primary_muscle_group AS muscle_group,
                        SUM(us.sets) AS total_sets,
                        SUM(us.sets * us.max_rep_range) AS total_reps,
                        SUM(us.sets * us.weight) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    GROUP BY e.primary_muscle_group
                    UNION ALL
                    SELECT
                        e.secondary_muscle_group AS muscle_group,
                        SUM(us.sets * 0.5) AS total_sets,
                        SUM(us.sets * us.max_rep_range * 0.5) AS total_reps,
                        SUM(us.sets * us.weight * 0.5) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    WHERE e.secondary_muscle_group IS NOT NULL
                    GROUP BY e.secondary_muscle_group
                    UNION ALL
                    SELECT
                        e.tertiary_muscle_group AS muscle_group,
                        SUM(us.sets * 0.33) AS total_sets,
                        SUM(us.sets * us.max_rep_range * 0.33) AS total_reps,
                        SUM(us.sets * us.weight * 0.33) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    WHERE e.tertiary_muscle_group IS NOT NULL
                    GROUP BY e.tertiary_muscle_group
                ) AS combined
                WHERE muscle_group IS NOT NULL
                GROUP BY muscle_group
            """
        elif method == "Fractional":
            return """
                SELECT
                    muscle_group,
                    ROUND(SUM(total_sets), 2) AS total_sets,
                    ROUND(SUM(total_reps), 2) AS total_reps,
                    ROUND(SUM(total_weight), 2) AS total_weight
                FROM (
                    SELECT
                        e.primary_muscle_group AS muscle_group,
                        SUM(us.sets * 0.5) AS total_sets,
                        SUM(us.sets * us.max_rep_range * 0.5) AS total_reps,
                        SUM(us.sets * us.weight * 0.5) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    GROUP BY e.primary_muscle_group
                    UNION ALL
                    SELECT
                        e.secondary_muscle_group AS muscle_group,
                        SUM(us.sets * 0.25) AS total_sets,
                        SUM(us.sets * us.max_rep_range * 0.25) AS total_reps,
                        SUM(us.sets * us.weight * 0.25) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    WHERE e.secondary_muscle_group IS NOT NULL
                    GROUP BY e.secondary_muscle_group
                    UNION ALL
                    SELECT
                        e.tertiary_muscle_group AS muscle_group,
                        SUM(us.sets * 0.17) AS total_sets,
                        SUM(us.sets * us.max_rep_range * 0.17) AS total_reps,
                        SUM(us.sets * us.weight * 0.17) AS total_weight
                    FROM user_selection us
                    JOIN exercises e ON us.exercise = e.exercise_name
                    WHERE e.tertiary_muscle_group IS NOT NULL
                    GROUP BY e.tertiary_muscle_group
                ) AS combined
                WHERE muscle_group IS NOT NULL
                GROUP BY muscle_group
            """
        elif method == "Direct":
            return """
                SELECT
                    e.primary_muscle_group AS muscle_group,
                    ROUND(SUM(us.sets), 2) AS total_sets,
                    ROUND(SUM(us.sets * us.max_rep_range), 2) AS total_reps,
                    ROUND(SUM(us.sets * us.weight), 2) AS total_weight
                FROM user_selection us
                JOIN exercises e ON us.exercise = e.exercise_name
                GROUP BY e.primary_muscle_group
            """
        else:
            raise ValueError(f"Unknown method: {method}")