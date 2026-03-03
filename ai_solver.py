import pandas as pd

def solve_ai(df, max_workers=15):

    df_sorted = df.sort_values(by=["duration", "workers"], ascending=False)

    time = 0
    active_workers = 0
    schedule = {}
    total_cost = 0

    for _, row in df_sorted.iterrows():

        if active_workers + row.workers <= max_workers:
            schedule[row.task_id] = time
            active_workers += row.workers
        else:
            time += 1
            active_workers = row.workers
            schedule[row.task_id] = time

        total_cost += row.duration * row.cost_per_day

    duration = max(schedule.values()) + max(df.duration)

    return duration, total_cost, schedule