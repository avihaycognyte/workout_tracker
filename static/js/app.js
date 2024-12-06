document.addEventListener("DOMContentLoaded", () => {
    // Add Exercise
    const form = document.getElementById("add-exercise-form");
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const exerciseData = {
                routine: document.getElementById("routine").value,
                exercise: document.getElementById("exercise").value,
                sets: document.getElementById("sets").value,
                min_rep_range: document.getElementById("min_rep_range").value,
                max_rep_range: document.getElementById("max_rep_range").value,
                rir: document.getElementById("rir").value,
                weight: document.getElementById("weight").value,
            };

            fetch("/add_exercise", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(exerciseData),
            })
                .then((response) => response.json())
                .catch((error) => console.error("Error:", error));
            location.reload()
        });
    }

    // Remove Exercise
    const table = document.getElementById("workout-plan-table");
    if (table) {
        table.addEventListener("click", (e) => {
            if (e.target.classList.contains("remove-exercise")) {
                const index = e.target.getAttribute("data-index");
                fetch("/remove_exercise", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ index }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        alert(data.message);
                        location.reload();
                    })
                    .catch((error) => console.error("Error:", error));
            }
        });
    }
});
