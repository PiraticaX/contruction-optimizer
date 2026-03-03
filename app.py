import streamlit as st
import pandas as pd
from optimizer import run_all

st.set_page_config(layout="wide")
st.title("Quantum Construction Optimization Benchmark")

df = pd.read_csv("dataset.csv")

if st.button("Run Benchmark"):

    results = run_all(df)

    table = []

    for method, (duration, cost, _) in results.items():
        score = 0.7 * duration + 0.3 * (cost/1000000)
        table.append([method, duration, cost, score])

    result_df = pd.DataFrame(
        table,
        columns=["Method", "Duration", "Cost", "Composite Score"]
    )

    st.dataframe(result_df)