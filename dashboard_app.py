# dashboard_app.py
import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="AI Honeypot Dashboard", layout="wide")
st.title("🧠 AI-Integrated Honeypot — Attack Analysis Dashboard")

LOG_DIR = "logs"

def load_logs(log_dir=LOG_DIR):
    files = glob.glob(os.path.join(log_dir, "port_*.jsonl"))
    rows = []
    for fp in files:
        with open(fp) as f:
            for line in f:
                try:
                    rows.append(pd.read_json(line, typ='series'))
                except Exception:
                    try:
                        rows.append(pd.Series(eval(line)))
                    except Exception:
                        pass
    if not rows:
        return pd.DataFrame(columns=["timestamp","remote_ip","port","input","output"])
    df = pd.DataFrame(rows)
    # normalize fields if nested
    if "timestamp" in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
    return df

df = load_logs()
if df.empty:
    st.warning("No logs found yet. Run the honeypot and simulator to generate logs, or place JSONL logs into the logs/ folder.")
    st.stop()

st.sidebar.header("Filters")
ports = sorted(df['port'].dropna().unique().tolist())
selected_ports = st.sidebar.multiselect("Ports", ports, default=ports)

filtered = df[df['port'].isin(selected_ports)]

st.metric("Total Interactions", len(filtered))
st.metric("Unique IPs", filtered['remote_ip'].nunique())

st.subheader("Most Attacked Ports")
port_counts = filtered['port'].value_counts()
st.bar_chart(port_counts)

st.subheader("Top Attacker IPs")
top_ips = filtered['remote_ip'].value_counts().head(10)
st.bar_chart(top_ips)

st.subheader("Attacks by Hour of Day")
hourly = filtered['hour'].value_counts().sort_index()
st.bar_chart(hourly)

st.subheader("Recent Logs (latest 200)")
st.dataframe(filtered.sort_values('timestamp', ascending=False).head(200))