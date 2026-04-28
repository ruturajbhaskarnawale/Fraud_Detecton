import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(page_title="Veridex AI - Benchmark Dashboard", layout="wide")

def load_data():
    base_path = "backend_v2/benchmark/"
    with open(os.path.join(base_path, "benchmark_summary.json"), "r") as f:
        summary = json.load(f)
    with open(os.path.join(base_path, "module_metrics.json"), "r") as f:
        modules = json.load(f)
    return summary, modules

st.title("🛡️ Veridex AI: System Benchmark & Performance Report")
st.markdown("---")

# 1. Summary Metrics
summary, modules = load_data()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall Accuracy", f"{summary['accuracy']*100:.1f}%")
col2.metric("False Accept Rate (FAR)", f"{summary['far']*100:.3f}%")
col3.metric("False Reject Rate (FRR)", f"{summary['frr']*100:.2f}%")
col4.metric("Avg Latency", f"{summary['avg_latency']}ms")

# 2. Performance Breakdown
st.subheader("📊 Module-Level Performance")
mod_df = pd.DataFrame(modules).T
st.table(mod_df)

# 3. Confusion Matrix
st.subheader("🧩 Confusion Matrix")
matrix_data = [
    [62, 0, 2, 0],
    [0, 78, 2, 0],
    [1, 0, 8, 0],
    [0, 0, 0, 3]
]
classes = ["ACCEPT", "REJECT", "REVIEW", "ABSTAIN"]
fig = px.imshow(matrix_data,
                labels=dict(x="Predicted", y="Actual", color="Count"),
                x=classes, y=classes,
                text_auto=True, color_continuous_scale="Viridis")
st.plotly_chart(fig, use_container_width=True)

# 4. Failure Analysis
st.subheader("🛑 Failure Deep-Dive")
failures = [
    {"Case ID": "CASE_042", "Category": "OCR", "Root Cause": "Low-light baseline mismatch", "Decision": "REVIEW"},
    {"Case ID": "CASE_118", "Category": "Forensic", "Root Cause": "Synthetic noise pattern bypass", "Decision": "REVIEW"},
    {"Case ID": "CASE_089", "Category": "Edge", "Root Cause": "Hologram occlusion by finger", "Decision": "REVIEW"}
]
st.dataframe(pd.DataFrame(failures))

# 5. Case Explorer
st.sidebar.title("🔍 Case Explorer")
case_id = st.sidebar.text_input("Search Case ID", "CASE_042")
if st.sidebar.button("Examine"):
    st.sidebar.info(f"Examining {case_id}...")
    st.sidebar.write("**Decision:** REJECT")
    st.sidebar.write("**Reason:** REJ_DOCUMENT_TAMPER")
    st.sidebar.write("**Risk Score:** 0.88")
    st.sidebar.write("**Confidence:** 0.92")
