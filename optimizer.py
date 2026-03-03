import pandas as pd
from ortools.sat.python import cp_model


def load_project(file):
    df = pd.read_csv(file)
    df["predecessors"] = df["predecessors"].fillna("")
    return df


def baseline_schedule(df):
    """
    Naive sequential scheduling ignoring resource limits.
    """
    schedule = {}
    current_time = 0

    for _, row in df.iterrows():
        schedule[row["task_id"]] = {
            "start": current_time,
            "end": current_time + row["duration"],
            "workers": row["workers"],
            "cost": row["duration"] * row["cost_per_day"],
        }
        current_time += row["duration"]

    total_duration = current_time
    total_cost = sum(task["cost"] for task in schedule.values())

    return schedule, total_duration, total_cost


def optimize_schedule(df, max_workers=15):
    model = cp_model.CpModel()

    horizon = sum(df["duration"])

    start_vars = {}
    end_vars = {}

    for _, row in df.iterrows():
        start = model.NewIntVar(0, horizon, f"start_{row['task_id']}")
        end = model.NewIntVar(0, horizon, f"end_{row['task_id']}")
        model.Add(end == start + row["duration"])

        start_vars[row["task_id"]] = start
        end_vars[row["task_id"]] = end

    # Precedence constraints
    for _, row in df.iterrows():
        if row["predecessors"]:
            preds = str(row["predecessors"]).split(";")
            for p in preds:
                p = int(p)
                model.Add(start_vars[row["task_id"]] >= end_vars[p])

    # Resource constraints (workers)
    intervals = []
    demands = []

    for _, row in df.iterrows():
        interval = model.NewIntervalVar(
            start_vars[row["task_id"]],
            row["duration"],
            end_vars[row["task_id"]],
            f"interval_{row['task_id']}",
        )
        intervals.append(interval)
        demands.append(row["workers"])

    model.AddCumulative(intervals, demands, max_workers)

    # Objective: minimize makespan
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, list(end_vars.values()))
    model.Minimize(makespan)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None, None, None

    schedule = {}
    total_cost = 0

    for _, row in df.iterrows():
        start = solver.Value(start_vars[row["task_id"]])
        end = solver.Value(end_vars[row["task_id"]])
        cost = row["duration"] * row["cost_per_day"]

        schedule[row["task_id"]] = {
            "start": start,
            "end": end,
            "workers": row["workers"],
            "cost": cost,
        }

        total_cost += cost

    total_duration = solver.Value(makespan)

    return schedule, total_duration, total_cost