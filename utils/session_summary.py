from utils.database import DatabaseHandler

def calculate_session_summary(method="Total"):
    """
    Calculate the per session summary with total sets and reps for each muscle group.
    :param method: Calculation method - "Total", "Fractional", or "Direct".
    :return: List of summary data for each session, grouped by muscle group.
    """
    with DatabaseHandler() as db_handler:
        try:
            # Scaling factors for each method
            scaling_factors = {
                "Total": {"primary": 1, "secondary": 1, "tertiary": 0.33},
                "Fractional": {"primary": 1, "secondary": 0.5, "tertiary": 0.17},
                "Direct": {"primary": 1, "secondary": 0, "tertiary": 0},
            }
            factors = scaling_factors.get(method, scaling_factors["Total"])

            # Query to calculate total sets and reps per session
            query = """
                SELECT
                    us.routine,
                    e.primary_muscle_group AS muscle_group,
                    SUM(us.sets * ?) AS total_sets_primary,
                    SUM(us.sets * us.max_rep_range * ?) AS total_reps_primary,
                    SUM(us.sets * ?) AS total_sets_secondary,
                    SUM(us.sets * us.max_rep_range * ?) AS total_reps_secondary,
                    SUM(us.sets * ?) AS total_sets_tertiary,
                    SUM(us.sets * us.max_rep_range * ?) AS total_reps_tertiary
                FROM user_selection us
                JOIN exercises e ON us.exercise = e.exercise_name
                GROUP BY us.routine, e.primary_muscle_group;
            """

            # Execute the query with scaling factors
            db_handler.cursor.execute(
                query,
                (
                    factors["primary"],
                    factors["primary"],
                    factors["secondary"],
                    factors["secondary"],
                    factors["tertiary"],
                    factors["tertiary"],
                ),
            )
            results = db_handler.cursor.fetchall()

            # Format results into a list of dictionaries
            return [
                {
                    "routine": row[0],
                    "muscle_group": row[1],
                    "total_sets": round(row[2] + row[4] + row[6], 1),
                    "total_reps": round(row[3] + row[5] + row[7], 1),
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error calculating session summary: {e}")
            return []