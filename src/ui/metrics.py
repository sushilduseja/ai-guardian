import streamlit as st


def display_metrics_dashboard(safe_attempts: int, total_attempts: int, blocked: int, avg_time: float):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if total_attempts == 0:
            st.metric("Success Rate", "N/A", delta=None)
        else:
            st.metric(
                "Success Rate",
                f"{(safe_attempts / total_attempts) * 100:.1f}%",
                delta="Good" if safe_attempts > blocked else "Needs Attention",
            )

    with col2:
        st.metric("Total Prompts", total_attempts, delta=None)

    with col3:
        st.metric("Blocked Threats", blocked, delta=None)

    with col4:
        st.metric("Avg Response Time", f"{avg_time:.2f}s", delta="Fast" if avg_time < 2 else "Normal")
