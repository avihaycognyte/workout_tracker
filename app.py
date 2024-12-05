from flask import Flask, render_template, request, redirect
from utils.helpers import (
    initialize_database,
    add_exercise,
    get_exercises,
    calculate_weekly_summary,
    get_weekly_summary,
)

app = Flask(__name__)

# Initialize the database
initialize_database()

@app.route("/")
def index():
    exercises = get_exercises()
    return render_template("workout_plan.html", exercises=exercises)

@app.route("/add_exercise", methods=["POST"])
def add_exercise_route():
    name = request.form.get("name")
    muscle_group = request.form.get("muscle_group")
    sets = int(request.form.get("sets"))
    reps = int(request.form.get("reps"))
    weight = float(request.form.get("weight"))

    add_exercise(name, muscle_group, sets, reps, weight)
    return redirect("/")

@app.route("/weekly_summary")
def weekly_summary():
    calculate_weekly_summary()
    summary = get_weekly_summary()
    return render_template("weekly_summary.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
