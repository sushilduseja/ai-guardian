import streamlit as st
import plotly.express as px


def create_security_dashboard(attempts: int, blocked: int):
    st.write("## 📊 Security Dashboard")
    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        _create_safety_pie_chart(attempts, blocked)

    with viz_col2:
        _create_attempts_bar_chart(attempts, blocked)


def _create_safety_pie_chart(attempts: int, blocked: int):
    safe_attempts = attempts - blocked
    fig = px.pie(
        {"Status": ["Safe Prompts", "Blocked Attempts"], "Count": [safe_attempts, blocked]},
        values="Count",
        names="Status",
        title="Safety Analysis",
        color="Status",
        color_discrete_map={"Safe Prompts": "#00CC96", "Blocked Attempts": "#EF553B"},
    )
    if attempts == 0:
        fig.add_annotation(
            text="No data yet — submit a prompt to see analysis",
            showarrow=False, font=dict(size=14, color="gray"),
            x=0.5, y=0.5, xref="paper", yref="paper",
        )
    st.plotly_chart(fig, width="stretch")


def _create_attempts_bar_chart(attempts: int, blocked: int):
    fig = px.bar(
        {"Type": ["Total Attempts", "Blocked Attempts"], "Count": [attempts, blocked]},
        x="Type",
        y="Count",
        title="Prompt Injection Attempts",
        color="Type",
        color_discrete_map={"Total Attempts": "#636EFA", "Blocked Attempts": "#EF553B"},
    )
    if blocked == 0 and attempts == 0:
        fig.add_annotation(
            text="No data yet — submit a prompt to see analysis",
            showarrow=False, font=dict(size=14, color="gray"),
            x=0.5, y=0.5, xref="paper", yref="paper",
        )
    st.plotly_chart(fig, width="stretch")
