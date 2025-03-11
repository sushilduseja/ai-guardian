import streamlit as st
import plotly.express as px

def create_security_dashboard(attempts: int, blocked: int):
    """Create and display the security analytics dashboard."""
    st.write("## 📊 Security Dashboard")
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        _create_safety_pie_chart(attempts, blocked)
    
    with viz_col2:
        _create_attempts_bar_chart(attempts, blocked)

def _create_safety_pie_chart(attempts: int, blocked: int):
    safe_attempts = attempts - blocked
    pie_data = {
        "Status": ["Safe Prompts", "Blocked Attempts"],
        "Count": [safe_attempts, blocked]
    }
    fig = px.pie(
        pie_data,
        values="Count",
        names="Status",
        title="Safety Analysis",
        color="Status",
        color_discrete_map={
            "Safe Prompts": "#00CC96",
            "Blocked Attempts": "#EF553B"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

def _create_attempts_bar_chart(attempts: int, blocked: int):
    data = {
        "Type": ["Total Attempts", "Blocked Attempts"],
        "Count": [attempts, blocked]
    }
    fig = px.bar(
        data, 
        x="Type", 
        y="Count", 
        title="Prompt Injection Attempts",
        color="Type",
        color_discrete_map={
            "Total Attempts": "#636EFA",
            "Blocked Attempts": "#EF553B"
        }
    )
    st.plotly_chart(fig, use_container_width=True)
