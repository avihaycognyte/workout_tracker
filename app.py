from flask import Flask, render_template, request, redirect
from utils.helpers import (
    initialize_database,
    add_exercise,
    get_exercises,
    get_user_selection,
    calculate_weekly_summary,
    get_weekly_summary,
)

app = Flask(__name__)

# Initialize the database
initialize_database()

@app.route("/")
def index():
    return render_template("workout_tracker.html")

@app.route("/workout_plan")
def workout_plan():
    exercises = get_exercises()
    user_selection = get_user_selection()
    return render_template("workout_plan.html", exercises=exercises, user_selection=user_selection, enumerate=enumerate)

@app.route("/add_exercise", methods=["POST"])
def add_exercise_route():
    data = request.get_json()
    routine = data.get("routine")
    exercise = data.get("exercise")
    sets = data.get("sets")
    min_rep_range = data.get("min_rep_range")
    max_rep_range = data.get("max_rep_range")
    rir = data.get("rir")
    weight = data.get("weight")
    add_exercise(routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
    return redirect("/")

@app.route("/weekly_summary")
def weekly_summary():
    calculate_weekly_summary()
    summary = get_weekly_summary()
    return render_template("weekly_summary.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
