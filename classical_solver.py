import pandas as pd
from ortools.sat.python import cp_model


def solve_classical(df, max_workers=15):

    model = cp_model.CpModel()
    horizon = int(sum(df["duration"]))

    start_vars = {}
    end_vars = {}

    for _, row in df.iterrows():
        start = model.NewIntVar(0, horizon, f"start_{row.task_id}")
        end = model.NewIntVar(0, horizon, f"end_{row.task_id}")
        model.Add(end == start + row.duration)

        start_vars[row.task_id] = start
        end_vars[row.task_id] = end

    # Precedence
    for _, row in df.iterrows():
        if pd.notna(row.predecessors) and row.predecessors != "":
            for p in str(row.predecessors).split(";"):
                model.Add(start_vars[row.task_id] >= end_vars[int(p)])

    # Resource constraint
    intervals = []
    demands = []

    for _, row in df.iterrows():
        interval = model.NewIntervalVar(
            start_vars[row.task_id],
            row.duration,
            end_vars[row.task_id],
            f"interval_{row.task_id}"
        )
        intervals.append(interval)
        demands.append(row.workers)

    model.AddCumulative(intervals, demands, max_workers)

    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, list(end_vars.values()))
    model.Minimize(makespan)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    solver.Solve(model)

    total_cost = sum(row.duration * row.cost_per_day for _, row in df.iterrows())

    schedule = {}

    for _, row in df.iterrows():
        schedule[row.task_id] = solver.Value(start_vars[row.task_id])

    return solver.Value(makespan), total_cost, schedule