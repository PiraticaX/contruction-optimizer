import pandas as pd


def solve_ai(df, max_workers=15):

    # Sort tasks by duration and workers (simulate intelligent prioritization)
    df_sorted = df.sort_values(by=["duration", "workers"], ascending=False)

    schedule = {}
    total_cost = 0

    current_time = 0
    active_workers = 0

    for _, row in df_sorted.iterrows():

        # Check predecessors
        if pd.notna(row.predecessors) and row.predecessors != "":
            preds = [int(p) for p in str(row.predecessors).split(";")]

            # Wait until all predecessors scheduled
            pred_finish_times = []
            for p in preds:
                if p in schedule:
                    pred_finish_times.append(schedule[p] + df[df.task_id == p]["duration"].values[0])

            if pred_finish_times:
                current_time = max(current_time, max(pred_finish_times))

        # Worker constraint logic
        if active_workers + row.workers <= max_workers:
            start_time = current_time
            active_workers += row.workers
        else:
            # Move time forward
            current_time += 1
            active_workers = row.workers
            start_time = current_time

        schedule[row.task_id] = start_time
        total_cost += row.duration * row.cost_per_day

    duration = max(schedule[t] + df[df.task_id == t]["duration"].values[0]
                   for t in schedule)

    return duration, total_cost, schedule