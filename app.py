import sqlite3
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, Response
import pandas as pd
from utils import (
    initialize_database,
    get_exercises,
    add_exercise,
    get_user_selection,
    calculate_weekly_summary,
)
from utils.session_summary import calculate_session_summary
from utils.database import DatabaseHandler

app = Flask(__name__)

# Initialize the database
initialize_database()

@app.route("/")
def index():
    return redirect("/workout_plan")

def fetch_unique_values(column):
    """
    Fetch unique values for a specified column from the exercises table.
    Handles both dictionary and tuple-based query results.
    :param column: The column name to fetch unique values for.
    :return: A list of unique values from the specified column.
    """
    query = f"SELECT DISTINCT {column} FROM exercises WHERE {column} IS NOT NULL ORDER BY {column} ASC"
    try:
        with DatabaseHandler() as db_handler:
            results = db_handler.fetch_all(query)
            print(f"DEBUG: Query results for column '{column}': {results}")

            # Normalize key access to handle dictionary-based results
            values = []
            for row in results:
                if isinstance(row, dict):
                    # Match key ignoring case and underscores
                    key = next((k for k in row if k.replace('_', '').lower() == column.replace('_', '').lower()), None)
                    if key:
                        values.append(row[key])
                elif isinstance(row, tuple):
                    # Use the first item in the tuple
                    values.append(row[0])

            return values
    except sqlite3.Error as db_error:
        print(f"Database error while fetching unique values for column '{column}': {db_error}")
        return []
    except Exception as e:
        print(f"Unexpected error while fetching unique values for column '{column}': {e}")
        return []


@app.route("/workout_plan")
def workout_plan():
    try:
        exercises = get_exercises() or []
        user_selection = get_user_selection() or []

        filters = {
            "Primary Muscle Group": fetch_unique_values("primary_muscle_group"),
            "Secondary Muscle Group": fetch_unique_values("secondary_muscle_group"),
            "Tertiary Muscle Group": fetch_unique_values("tertiary_muscle_group"),
            "Force": fetch_unique_values("force"),
            "Equipment": fetch_unique_values("equipment"),
            "Mechanic": fetch_unique_values("mechanic"),
            "Difficulty": fetch_unique_values("difficulty"),
        }

        print(f"DEBUG: Rendering template with exercises={len(exercises)}, user_selection={len(user_selection)}, filters={len(filters)}")
        return render_template(
            "workout_plan.html",
            exercises=exercises,
            user_selection=user_selection,
            filters=filters,
            routineOptions={
                "4 Week Split": ["A1", "B1", "A2", "B2"],
                "Full Body": ["Fullbody1", "Fullbody2", "Fullbody3"],
                "Push, Pull, Legs": ["Push1", "Pull1", "Legs1", "Push2", "Pull2", "Legs2"],
                "2 Days Split": ["A", "B"],
                "Upper Lower": ["Upper1", "Lower1", "Upper2", "Lower2"],
                "3 Days Split": ["A", "B", "C"],
            },
            enumerate=enumerate,
        )
    except Exception as e:
        print(f"Error in workout_plan: {e}")
        return render_template("error.html", message="Unable to load workout plan."), 500



@app.route("/get_workout_plan", methods=["GET"])
def get_workout_plan():
    try:
        user_selection = get_user_selection() or []
        return jsonify(user_selection), 200
    except Exception as e:
        print(f"Error in get_workout_plan: {e}")
        return jsonify({"error": "Unable to fetch workout plan"}), 500


@app.route("/add_exercise", methods=["POST"])
def add_exercise_route():
    try:
        # Parse JSON data from request
        data = request.get_json()
        print(f"DEBUG: Received data for add_exercise: {data}")

        # Validate required fields
        required_fields = ["routine", "exercise", "sets", "min_rep_range", "max_rep_range", "weight"]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]

        if missing_fields:
            print(f"DEBUG: Missing required fields in add_exercise: {missing_fields}")
            return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Optional RIR field handling
        rir = int(data["rir"]) if "rir" in data and data["rir"] else None

        # Call the add_exercise function (assumed to be defined elsewhere)
        add_exercise(
            data["routine"],
            data["exercise"],
            int(data["sets"]),
            int(data["min_rep_range"]),
            int(data["max_rep_range"]),
            rir,
            float(data["weight"]),
        )

        # Fetch updated data to return in response
        updated_data = get_user_selection()
        print(f"DEBUG: Updated data after adding exercise: {updated_data}")

        return jsonify({"message": "Exercise added successfully!", "data": updated_data}), 200

    except ValueError as ve:
        print(f"DEBUG: ValueError in add_exercise: {ve}")
        return jsonify({"message": "Invalid input type provided"}), 400

    except Exception as e:
        print(f"ERROR: Exception in add_exercise: {e}")
        return jsonify({"error": "An unexpected error occurred while adding the exercise"}), 500

@app.route("/remove_exercise", methods=["POST"])
def remove_exercise():
    try:
        data = request.get_json()
        print(f"DEBUG: Received data for remove_exercise: {data}")

        exercise_id = data.get("id")
        if not exercise_id or not str(exercise_id).isdigit():
            print(f"DEBUG: Invalid exercise ID: {exercise_id}")
            return jsonify({"message": "Invalid exercise ID"}), 400

        with DatabaseHandler() as db_handler:
            db_handler.execute_query("DELETE FROM user_selection WHERE id = ?", (int(exercise_id),))
            print(f"DEBUG: Deleted exercise with ID = {exercise_id}")

        updated_data = get_user_selection()
        return jsonify({"message": "Exercise removed successfully", "data": updated_data}), 200
    except Exception as e:
        print(f"Error in remove_exercise: {e}")
        return jsonify({"error": "Unable to remove exercise"}), 500

@app.route("/filter_exercises", methods=["POST"])
def filter_exercises():
    try:
        filters = request.get_json()
        print(f"DEBUG: Filters received: {filters}")

        if not filters:
            return jsonify({"message": "No filters provided"}), 400

        exercises = get_exercises(filters=filters)
        return jsonify(exercises)
    except Exception as e:
        print(f"Error in filter_exercises: {e}")
        return jsonify({"error": "Unable to filter exercises"}), 500

@app.route("/weekly_summary", methods=["GET"])
def weekly_summary():
    method = request.args.get("method", "Total")
    try:
        results = calculate_weekly_summary(method)
        return jsonify(results) if request.headers.get("Accept") == "application/json" else render_template(
            "weekly_summary.html", summary=results, selected_method=method
        )
    except Exception as e:
        print(f"Error in weekly_summary: {e}")
        return jsonify({"error": "Unable to fetch weekly summary"}), 500

@app.route("/session_summary", methods=["GET"])
def session_summary():
    method = request.args.get("method", "Total")
    try:
        results = calculate_session_summary(method)
        return jsonify(results) if request.headers.get("Accept") == "application/json" else render_template(
            "session_summary.html", summary=results, selected_method=method
        )
    except Exception as e:
        print(f"Error in session_summary: {e}")
        return jsonify({"error": "Unable to fetch session summary"}), 500

@app.route("/export_to_excel", methods=["GET"])
def export_to_excel():
    try:
        user_selection = get_user_selection()
        weekly_summary_data = calculate_weekly_summary(method="Total")
        session_summary_data = calculate_session_summary(method="Total")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            pd.DataFrame(user_selection).to_excel(writer, index=False, sheet_name="Workout Plan")
            pd.DataFrame(weekly_summary_data).to_excel(writer, index=False, sheet_name="Weekly Summary")
            pd.DataFrame(session_summary_data).to_excel(writer, index=False, sheet_name="Per Session Summary")

        output.seek(0)
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=workout_tracker_summary.xlsx"},
        )
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return jsonify({"error": "Failed to export to Excel"}), 500

if __name__ == "__main__":
    app.run(debug=True)