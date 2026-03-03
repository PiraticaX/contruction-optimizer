import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

from optimizer import load_project, baseline_schedule, optimize_schedule

st.set_page_config(page_title="Construction Schedule Optimizer", layout="wide")

st.title("🏗 AI Construction Schedule Optimization Engine")

st.sidebar.header("Upload Project CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = load_project(uploaded_file)
else:
    df = load_project("sample_project.csv")

st.subheader("Project Data")
st.dataframe(df)

if st.button("🚀 Run Optimization"):

    # Baseline
    base_schedule, base_duration, base_cost = baseline_schedule(df)

    # Optimized
    opt_schedule, opt_duration, opt_cost = optimize_schedule(df)

    if opt_schedule is None:
        st.error("Optimization failed.")
        st.stop()

    # KPI Metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("Baseline Duration (days)", base_duration)
    col2.metric("Optimized Duration (days)", opt_duration,
                delta=base_duration - opt_duration)

    col3.metric("Cost (₹)", opt_cost,
                delta=base_cost - opt_cost)

    # Gantt Chart
    gantt_data = []

    for task_id, data in opt_schedule.items():
        task_name = df[df["task_id"] == task_id]["task_name"].values[0]
        gantt_data.append(dict(
            Task=task_name,
            Start=data["start"],
            Finish=data["end"]
        ))

    fig = ff.create_gantt(
        gantt_data,
        index_col=None,
        show_colorbar=False,
        group_tasks=True
    )

    st.subheader("📊 Optimized Schedule (Gantt Chart)")
    st.plotly_chart(fig, use_container_width=True)

    # Worker Utilization
    timeline = list(range(opt_duration))
    worker_usage = []

    for t in timeline:
        workers = 0
        for task in opt_schedule.values():
            if task["start"] <= t < task["end"]:
                workers += task["workers"]
        worker_usage.append(workers)

    worker_fig = go.Figure()
    worker_fig.add_trace(go.Scatter(
        x=timeline,
        y=worker_usage,
        mode="lines+markers"
    ))
    worker_fig.update_layout(
        title="Worker Utilization Over Time",
        xaxis_title="Day",
        yaxis_title="Workers"
    )

    st.subheader("👷 Worker Utilization")
    st.plotly_chart(worker_fig, use_container_width=True)

    st.success("Optimization Complete.")