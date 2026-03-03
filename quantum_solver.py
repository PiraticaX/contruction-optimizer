import pandas as pd
import numpy as np
import dimod
from neal import SimulatedAnnealingSampler

def solve_quantum(df, max_workers=15):

    horizon = int(sum(df["duration"]))
    tasks = df.to_dict("records")
    n_tasks = len(tasks)

    # Penalty weights
    A = 50   # single start
    B = 80   # precedence
    C = 20   # resource
    alpha = 1.0
    beta = 0.00001

    Q = {}

    def var(i, t):
        return f"x_{i}_{t}"

    # 1️⃣ Single Start Constraint
    for i in range(n_tasks):
        for t in range(horizon):
            Q[(var(i,t), var(i,t))] = Q.get((var(i,t), var(i,t)), 0) - A

            for tp in range(t+1, horizon):
                Q[(var(i,t), var(i,tp))] = Q.get((var(i,t), var(i,tp)), 0) + 2*A

    # 2️⃣ Objective: duration & cost
    for i, task in enumerate(tasks):
        for t in range(horizon):
            duration_term = alpha * (t + task["duration"])
            cost_term = beta * task["duration"] * task["cost_per_day"]

            Q[(var(i,t), var(i,t))] = Q.get((var(i,t), var(i,t)), 0) + duration_term + cost_term

    # 3️⃣ Precedence Constraint
    for j, task in enumerate(tasks):
        if pd.notna(task["predecessors"]) and task["predecessors"] != "":
            preds = [int(p)-1 for p in str(task["predecessors"]).split(";")]

            for i in preds:
                dur_i = tasks[i]["duration"]

                for t_i in range(horizon):
                    for t_j in range(horizon):
                        if t_j < t_i + dur_i:
                            Q[(var(i,t_i), var(j,t_j))] = Q.get((var(i,t_i), var(j,t_j)), 0) + B

    # 4️⃣ Resource Constraint
    for tau in range(horizon):
        for i, task in enumerate(tasks):
            for t in range(max(0, tau - task["duration"] + 1), tau+1):

                if t < horizon:
                    Q[(var(i,t), var(i,t))] = Q.get((var(i,t), var(i,t)), 0) + C * task["workers"]

    # Solve QUBO
    sampler = SimulatedAnnealingSampler()
    response = sampler.sample_qubo(Q, num_reads=200)

    best_sample = response.first.sample

    schedule = {}
    total_cost = 0
    makespan = 0

    for i, task in enumerate(tasks):
        for t in range(horizon):
            if best_sample.get(var(i,t), 0) == 1:
                schedule[task["task_id"]] = t
                finish = t + task["duration"]
                makespan = max(makespan, finish)
                total_cost += task["duration"] * task["cost_per_day"]

    return makespan, total_cost, schedule