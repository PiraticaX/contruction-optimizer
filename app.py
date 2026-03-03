import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
from optimizer import run_all

st.set_page_config(layout="wide")
st.title("Quantum Construction Optimization Dashboard")

# ---------------------------------------
# Sidebar Upload
# ---------------------------------------

st.sidebar.header("Upload Project Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

required_columns = [
    "task_id",
    "task_name",
    "duration",
    "workers",
    "cost_per_day",
    "predecessors"
]

# ---------------------------------------
# Load Dataset
# ---------------------------------------

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        if not all(col in df.columns for col in required_columns):
            st.error("Uploaded file does not match required format.")
            st.stop()

        st.success("Custom dataset loaded successfully.")

    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

else:
    df = pd.read_csv("dataset.csv")
    st.info("Using default dataset.")

st.subheader("Project Dataset")
st.dataframe(df)

# ---------------------------------------
# Run Benchmark
# ---------------------------------------

if st.button("Run Full Benchmark"):

    with st.spinner("Running Classical, AI and Quantum Solvers..."):
        results = run_all(df)

    classical_dur, classical_cost, classical_sched = results["Classical"]
    ai_dur, ai_cost, ai_sched = results["AI-Heuristic"]
    quantum_dur, quantum_cost, quantum_sched = results["Quantum Benchmark"]

    # ---------------------------------------
    # KPI Section
    # ---------------------------------------

    st.subheader("Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric("Best Duration (Days)",
                min(classical_dur, ai_dur, quantum_dur))

    col2.metric("Best Cost",
                f"₹ {min(classical_cost, ai_cost, quantum_cost):,.0f}")

    col3.metric("Quantum Improvement",
                classical_dur - quantum_dur)

    # ---------------------------------------
    # Comparison Table
    # ---------------------------------------

    comparison_df = pd.DataFrame({
        "Method": ["Classical", "AI-Heuristic", "Quantum"],
        "Duration (Days)": [classical_dur, ai_dur, quantum_dur],
        "Cost": [classical_cost, ai_cost, quantum_cost]
    })

    st.subheader("Solver Comparison")
    st.dataframe(comparison_df)

    # ---------------------------------------
    # Charts
    # ---------------------------------------

    st.plotly_chart(
        px.bar(comparison_df, x="Method", y="Duration (Days)",
               title="Duration Comparison", color="Method"),
        use_container_width=True
    )

    st.plotly_chart(
        px.bar(comparison_df, x="Method", y="Cost",
               title="Cost Comparison", color="Method"),
        use_container_width=True
    )

    # ---------------------------------------
    # Timeline Section
    # ---------------------------------------

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

    for tab, data in zip(
        [tab1, tab2, tab3],
        [classical_df, ai_df, quantum_df]
    ):
        with tab:
            if not data.empty:
                fig = px.timeline(
                    data,
                    x_start="Start",
                    x_end="Finish",
                    y="Task",
                    color="Solver"
                )
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(height=700)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No schedule available.")

    # ---------------------------------------
    # Worker Utilization
    # ---------------------------------------

    st.subheader("Worker Allocation Over Time")

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

    fig_workers = go.Figure()

    for name, sched in {
        "Classical": classical_sched,
        "AI-Heuristic": ai_sched,
        "Quantum": quantum_sched
    }.items():

        usage = compute_worker_usage(sched)

        if usage:
            fig_workers.add_trace(go.Scatter(
                y=usage,
                mode="lines",
                name=name
            ))

    fig_workers.update_layout(
        title="Worker Allocation Timeline",
        xaxis_title="Time (Days)",
        yaxis_title="Workers",
        height=500
    )

    st.plotly_chart(fig_workers, use_container_width=True)

    st.success("Dashboard Generated Successfully.")