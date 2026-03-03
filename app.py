import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
from optimizer import run_all

st.set_page_config(layout="wide")
st.title("Quantum Construction Optimization Dashboard")

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("dataset.csv")

st.subheader("Project Dataset")
st.dataframe(df)

# -----------------------------
# Run Benchmark
# -----------------------------
if st.button("Run Full Benchmark"):

    with st.spinner("Running Classical, AI and Quantum Solvers..."):
        results = run_all(df)

    # Extract Results
    classical_dur, classical_cost, classical_sched = results["Classical"]
    ai_dur, ai_cost, ai_sched = results["AI-Heuristic"]
    quantum_dur, quantum_cost, quantum_sched = results["Quantum Benchmark"]

    # -----------------------------
    # KPI CARDS
    # -----------------------------
    st.subheader("Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Best Duration (Days)",
        min(classical_dur, ai_dur, quantum_dur)
    )

    col2.metric(
        "Best Cost",
        f"₹ {min(classical_cost, ai_cost, quantum_cost):,.0f}"
    )

    col3.metric(
        "Quantum Duration Improvement",
        classical_dur - quantum_dur
    )

    # -----------------------------
    # Comparison Table
    # -----------------------------
    st.subheader("Solver Comparison")

    comparison_df = pd.DataFrame({
        "Method": ["Classical", "AI-Heuristic", "Quantum"],
        "Duration (Days)": [classical_dur, ai_dur, quantum_dur],
        "Cost": [classical_cost, ai_cost, quantum_cost]
    })

    st.dataframe(comparison_df)

    # -----------------------------
    # Duration Chart
    # -----------------------------
    fig_duration = px.bar(
        comparison_df,
        x="Method",
        y="Duration (Days)",
        title="Duration Comparison",
        color="Method"
    )
    st.plotly_chart(fig_duration, use_container_width=True)

    # -----------------------------
    # Cost Chart
    # -----------------------------
    fig_cost = px.bar(
        comparison_df,
        x="Method",
        y="Cost",
        title="Cost Comparison",
        color="Method"
    )
    st.plotly_chart(fig_cost, use_container_width=True)

    # -----------------------------
    # TIMELINE SECTION
    # -----------------------------
    st.subheader("Timeline Comparison")

    base_date = datetime.datetime(2026, 1, 1)

    def build_timeline_df(schedule, solver_name):

        rows = []

        if not schedule:
            return pd.DataFrame()

        for _, row in df.iterrows():

            if row.task_id in schedule:

                start_day = int(schedule[row.task_id])
                finish_day = start_day + int(row.duration)

                rows.append({
                    "Task": row.task_name,
                    "Start": base_date + datetime.timedelta(days=start_day),
                    "Finish": base_date + datetime.timedelta(days=finish_day),
                    "Solver": solver_name
                })

        return pd.DataFrame(rows)


    classical_df = build_timeline_df(classical_sched, "Classical")
    ai_df = build_timeline_df(ai_sched, "AI-Heuristic")
    quantum_df = build_timeline_df(quantum_sched, "Quantum")

    tab1, tab2, tab3 = st.tabs(["Classical", "AI-Heuristic", "Quantum"])

    with tab1:
        if not classical_df.empty:
            fig_classical = px.timeline(
                classical_df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Solver"
            )
            fig_classical.update_yaxes(autorange="reversed")
            fig_classical.update_layout(height=700)
            st.plotly_chart(fig_classical, use_container_width=True)
        else:
            st.info("No Classical schedule available.")

    with tab2:
        if not ai_df.empty:
            fig_ai = px.timeline(
                ai_df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Solver"
            )
            fig_ai.update_yaxes(autorange="reversed")
            fig_ai.update_layout(height=700)
            st.plotly_chart(fig_ai, use_container_width=True)
        else:
            st.info("No AI schedule available.")

    with tab3:
        if not quantum_df.empty:
            fig_quantum = px.timeline(
                quantum_df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Solver"
            )
            fig_quantum.update_yaxes(autorange="reversed")
            fig_quantum.update_layout(height=700)
            st.plotly_chart(fig_quantum, use_container_width=True)
        else:
            st.info("No Quantum schedule available.")

    # -----------------------------
    # Worker Utilization
    # -----------------------------
    st.subheader("Worker Utilization Over Time")

    def compute_worker_usage(schedule):

        if not schedule:
            return []

        horizon = max(schedule.values()) + max(df.duration)
        usage = [0] * horizon

        for _, row in df.iterrows():

            if row.task_id in schedule:

                start = schedule[row.task_id]

                for t in range(start, start + row.duration):
                    if t < horizon:
                        usage[t] += row.workers

        return usage


    classical_usage = compute_worker_usage(classical_sched)
    ai_usage = compute_worker_usage(ai_sched)
    quantum_usage = compute_worker_usage(quantum_sched)

    fig_workers = go.Figure()

    if classical_usage:
        fig_workers.add_trace(go.Scatter(
            y=classical_usage,
            mode="lines",
            name="Classical"
        ))

    if ai_usage:
        fig_workers.add_trace(go.Scatter(
            y=ai_usage,
            mode="lines",
            name="AI-Heuristic"
        ))

    if quantum_usage:
        fig_workers.add_trace(go.Scatter(
            y=quantum_usage,
            mode="lines",
            name="Quantum"
        ))

    fig_workers.update_layout(
        title="Worker Allocation Timeline",
        xaxis_title="Time (Days)",
        yaxis_title="Workers",
        height=500
    )

    st.plotly_chart(fig_workers, use_container_width=True)

    st.success("Full Optimization Dashboard Generated Successfully.")