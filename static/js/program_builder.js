/*
Expected backend JSON format for #program-data:
{
  "weekNumber": 6,
  "year": 2026,
  "weekStartISO": "2026-02-24",
  "weekDays": [
    {
      "iso": "2026-02-24",
      "dayLabelShort": "Mon",
      "dayLabelLong": "Monday",
      "monthDay": "Feb 24",
      "workout": {
        "title": "Push A",
        "exercises": [
          {"name": "Bench Press", "details": "4x8"}
        ]
      }
    }
  ]
}
*/
/*
Expected backend exercise data (server rendered in template):
exercise_library = [
    {"name": "Bench Press", "sub": "Barbell", "category": "chest"}
]
*/
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("exercise-search");
    const filterButtons = Array.from(document.querySelectorAll(".filter-tags .tag"));
    const exerciseItems = Array.from(document.querySelectorAll(".exercise-item-card"));
    const weekTitle = document.getElementById("week-title");
    const weekGrid = document.getElementById("week-grid");
    const prevWeekBtn = document.getElementById("prev-week");
    const nextWeekBtn = document.getElementById("next-week");
    const thisWeekBtn = document.getElementById("this-week");
    const planStatus = document.getElementById("plan-status");
    const planPanel = document.querySelector(".week-plan-panel");

    const programData = readProgramData();
    const fixedYear = programData.year || 2026;
    const today = new Date();
    const baseWeekNumber = programData.weekNumber || getISOWeekNumber(today);
    const minWeek = 1;
    const maxWeek = 53;
    let weekOffset = 0;

    function setPlanStatus(message) {
        if (!planStatus) {
            return;
        }
        planStatus.textContent = message;
    }

    function renderWeekHeader(weekNumber) {
        if (weekTitle) {
            weekTitle.textContent = "Week " + weekNumber + ", " + fixedYear + " Plan";
        }
    }

    function renderWeekGrid(weekNumber) {
        if (!weekGrid) {
            return;
        }

        weekGrid.innerHTML = "";
        const weekDays = resolveWeekDays(weekNumber);
        const todayIso = formatISODate(today);
        let todayFound = false;

        weekDays.forEach((day) => {
            const dayColumn = document.createElement("div");
            dayColumn.className = "day-column";
            dayColumn.dataset.dateIso = day.iso;

            if (day.isRestDay) {
                dayColumn.classList.add("rest-day");
            }

            const dayHeader = document.createElement("div");
            dayHeader.className = "day-header";
            dayHeader.innerHTML = "<small>" + day.monthDay + "</small><strong>" + day.dayLabelShort + "</strong>";

            const dayDateLine = document.createElement("div");
            dayDateLine.className = "day-date-line";

            if (day.iso === todayIso) {
                dayDateLine.textContent = "Date: " + day.fullDateLabel;
                dayDateLine.classList.add("is-today");
                dayColumn.dataset.isToday = "true";
                todayFound = true;
            } else {
                dayDateLine.textContent = "Date: " + day.fullDateLabel;
                dayColumn.dataset.isToday = "false";
            }

            const dayContent = document.createElement("div");
            dayContent.className = "day-content";

            const planList = document.createElement("div");
            planList.className = "plan-list";

            if (day.workout) {
                const workoutCard = document.createElement("div");
                workoutCard.className = "workout-card-mini";

                const workoutTitle = document.createElement("span");
                workoutTitle.className = "workout-title";
                workoutTitle.textContent = day.workout.title || "Workout";
                workoutCard.appendChild(workoutTitle);

                if (Array.isArray(day.workout.exercises)) {
                    day.workout.exercises.forEach((ex) => {
                        const scheduled = document.createElement("div");
                        scheduled.className = "scheduled-exercise";
                        scheduled.innerHTML =
                            "<span class=\"ex-name\">" +
                            escapeHtml(ex.name || "") +
                            "</span><span class=\"ex-details\">" +
                            escapeHtml(ex.details || "") +
                            "</span>";
                        workoutCard.appendChild(scheduled);
                    });
                }

                planList.appendChild(workoutCard);
            }

            const addButton = document.createElement("button");
            addButton.type = "button";
            addButton.className = "add-exercise-btn";
            addButton.textContent = "+ Add Exercise";
            if (day.iso !== todayIso) {
                addButton.disabled = true;
                addButton.setAttribute("aria-disabled", "true");
                addButton.title = "Only today's plan can be edited.";
            }

            dayContent.appendChild(planList);
            dayContent.appendChild(addButton);

            dayColumn.appendChild(dayHeader);
            dayColumn.appendChild(dayDateLine);
            dayColumn.appendChild(dayContent);

            weekGrid.appendChild(dayColumn);
        });

        if (!todayFound) {
            setPlanStatus("Editing is available only for today.");
        } else {
            setPlanStatus("");
        }
    }

    function updateWeekView() {
        const rawWeek = baseWeekNumber + weekOffset;
        const weekNumber = clampWeek(rawWeek);
        weekOffset = weekNumber - baseWeekNumber;
        renderWeekHeader(weekNumber);
        renderWeekGrid(weekNumber);

        if (thisWeekBtn) {
            if (weekOffset === 0) {
                thisWeekBtn.classList.add("active");
            } else {
                thisWeekBtn.classList.remove("active");
            }
        }
    }

    function onExerciseActivate(exerciseButton) {
        const todayColumn = document.querySelector('.day-column[data-is-today="true"]');
        if (!todayColumn) {
            setPlanStatus("Editing is available only for today.");
            return;
        }

        const planList = todayColumn.querySelector(".plan-list");
        if (!planList) {
            return;
        }

        const name = exerciseButton.dataset.name || "Exercise";
        const sub = exerciseButton.dataset.sub || "";

        const scheduled = document.createElement("div");
        scheduled.className = "scheduled-exercise";
        scheduled.innerHTML =
            "<span class=\"ex-name\">" +
            escapeHtml(name) +
            "</span><span class=\"ex-details\">" +
            escapeHtml(sub) +
            "</span>";
        planList.appendChild(scheduled);
    }

    function normalizeCategory(value) {
        return (value || "all").toLowerCase().replace(/\s+/g, "_");
    }

    function applyFilters() {
        const activeFilter =
            normalizeCategory(
                (filterButtons.find((btn) => btn.classList.contains("active")) || {}).dataset?.filter
            ) || "all";
        const query = (searchInput?.value || "").trim().toLowerCase();

        exerciseItems.forEach((item) => {
            const name = (item.dataset.name || "").toLowerCase();
            const sub = (item.dataset.sub || "").toLowerCase();
            const category = normalizeCategory(item.dataset.category);

            const matchesQuery = !query || name.includes(query) || sub.includes(query);
            const matchesCategory = activeFilter === "all" || category === activeFilter;

            item.style.display = matchesQuery && matchesCategory ? "flex" : "none";
        });
    }

    function attachEventHandlers() {
        if (searchInput) {
            searchInput.addEventListener("input", applyFilters);
        }

        filterButtons.forEach((button) => {
            button.addEventListener("click", () => {
                filterButtons.forEach((btn) => {
                    btn.classList.remove("active");
                    btn.setAttribute("aria-selected", "false");
                });
                button.classList.add("active");
                button.setAttribute("aria-selected", "true");
                applyFilters();
            });
        });

        exerciseItems.forEach((item) => {
            item.addEventListener("click", () => onExerciseActivate(item));
            item.addEventListener("keydown", (event) => {
                if (event.key === "Enter") {
                    event.preventDefault();
                    onExerciseActivate(item);
                }
            });
        });

        if (prevWeekBtn) {
            prevWeekBtn.addEventListener("click", () => {
                weekOffset -= 1;
                updateWeekView();
            });
        }

        if (nextWeekBtn) {
            nextWeekBtn.addEventListener("click", () => {
                weekOffset += 1;
                updateWeekView();
            });
        }

        if (thisWeekBtn) {
            thisWeekBtn.addEventListener("click", () => {
                weekOffset = 0;
                updateWeekView();
            });
        }
    }

    attachEventHandlers();
    updateWeekView();
    applyFilters();

    function readProgramData() {
        const dataEl = document.getElementById("program-data");
        if (!dataEl) {
            return {};
        }

        try {
            return JSON.parse(dataEl.textContent);
        } catch (error) {
            return {};
        }
    }

    function resolveWeekDays() {
        if (Array.isArray(programData.weekDays) && programData.weekDays.length === 7) {
            return programData.weekDays.map((day) => {
                const iso = day.iso || "";
                const dateObj = iso ? new Date(iso + "T00:00:00") : null;
                const fallbackDate = dateObj || today;

                return {
                    iso: iso || formatISODate(fallbackDate),
                    dayLabelShort: day.dayLabelShort || day.day_name_short || day.weekday || formatDayShort(fallbackDate),
                    dayLabelLong: day.dayLabelLong || day.day_name || day.weekday || formatDayLong(fallbackDate),
                    monthDay: day.monthDay || day.month_day || formatMonthDay(fallbackDate),
                    fullDateLabel: formatFullDate(fallbackDate),
                    isRestDay: day.isRestDay || (day.workout && day.workout.title === "Rest Day"),
                    workout: day.workout || null
                };
            });
        }

        const weekStart = getStartOfWeek(getDateForWeekOffset());
        return Array.from({ length: 7 }, (_, index) => {
            const dateObj = new Date(weekStart);
            dateObj.setDate(weekStart.getDate() + index);

            return {
                iso: formatISODate(dateObj),
                dayLabelShort: formatDayShort(dateObj),
                dayLabelLong: formatDayLong(dateObj),
                monthDay: formatMonthDay(dateObj),
                fullDateLabel: formatFullDate(dateObj),
                isRestDay: false,
                workout: null
            };
        });
    }

    function clampWeek(weekNumber) {
        if (weekNumber < minWeek) {
            return minWeek;
        }

        if (weekNumber > maxWeek) {
            return maxWeek;
        }

        return weekNumber;
    }

    function getDateForWeekOffset() {
        const base = programData.weekStartISO
            ? new Date(programData.weekStartISO + "T00:00:00")
            : new Date(today);
        const target = new Date(base);
        target.setDate(base.getDate() + weekOffset * 7);
        return target;
    }

    function getStartOfWeek(date) {
        const start = new Date(date);
        const day = start.getDay();
        const diff = day === 0 ? -6 : 1 - day;
        start.setDate(start.getDate() + diff);
        start.setHours(0, 0, 0, 0);
        return start;
    }

    function formatISODate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        return year + "-" + month + "-" + day;
    }

    function formatDayShort(date) {
        return date.toLocaleDateString("en-US", { weekday: "short" });
    }

    function formatDayLong(date) {
        return date.toLocaleDateString("en-US", { weekday: "long" });
    }

    function formatMonthDay(date) {
        return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    }

    function formatFullDate(date) {
        return date.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric"
        });
    }

    function getISOWeekNumber(date) {
        const temp = new Date(date.getTime());
        temp.setHours(0, 0, 0, 0);
        temp.setDate(temp.getDate() + 3 - ((temp.getDay() + 6) % 7));
        const week1 = new Date(temp.getFullYear(), 0, 4);
        return (
            1 +
            Math.round(
                ((temp.getTime() - week1.getTime()) / 86400000 - 3 + ((week1.getDay() + 6) % 7)) / 7
            )
        );
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }
});