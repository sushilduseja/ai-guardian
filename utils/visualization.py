"""
Visualization utilities for the AI Guardian dashboard.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple


def create_attack_detection_chart(detection_history: List[Dict]) -> go.Figure:
    """
    Create a bar chart showing the frequency of different attack types.
    
    Args:
        detection_history: List of detection results
        
    Returns:
        Plotly figure object
    """
    # Flatten the detection history to count attack categories
    all_attacks = []
    for entry in detection_history:
        for attack in entry.get("detected_attacks", []):
            all_attacks.append(attack["category"])
    
    # Count occurrences of each attack category
    if not all_attacks:
        # Return empty chart if no attacks detected
        return go.Figure().add_annotation(
            text="No attacks detected yet",
            showarrow=False,
            font=dict(size=20)
        )
    
    attack_counts = pd.Series(all_attacks).value_counts().reset_index()
    attack_counts.columns = ["Attack Type", "Count"]
    
    # Create bar chart
    fig = px.bar(
        attack_counts, 
        x="Attack Type", 
        y="Count",
        color="Attack Type",
        title="Detected Attack Types",
        labels={"Count": "Number of Attempts"}
    )
    
    return fig


def create_defense_effectiveness_chart(effectiveness_history: List[Dict]) -> go.Figure:
    """
    Create a chart showing the effectiveness of different defense strategies.
    
    Args:
        effectiveness_history: List of defense effectiveness results
        
    Returns:
        Plotly figure object
    """
    if not effectiveness_history:
        # Return empty chart if no data
        return go.Figure().add_annotation(
            text="No defense effectiveness data yet",
            showarrow=False,
            font=dict(size=20)
        )
    
    # Prepare data
    strategies = []
    effective_counts = []
    ineffective_counts = []
    
    # Group by strategy and count effective/ineffective instances
    strategy_results = {}
    
    for entry in effectiveness_history:
        strategy = entry.get("strategy", "unknown")
        effective = entry.get("defense_effective", False)
        
        if strategy not in strategy_results:
            strategy_results[strategy] = {"effective": 0, "ineffective": 0}
        
        if effective:
            strategy_results[strategy]["effective"] += 1
        else:
            strategy_results[strategy]["ineffective"] += 1
    
    # Prepare data for stacked bar chart
    for strategy, counts in strategy_results.items():
        strategies.append(strategy)
        effective_counts.append(counts["effective"])
        ineffective_counts.append(counts["ineffective"])
    
    # Create stacked bar chart
    fig = go.Figure(data=[
        go.Bar(name="Effective", x=strategies, y=effective_counts, marker_color="green"),
        go.Bar(name="Ineffective", x=strategies, y=ineffective_counts, marker_color="red")
    ])
    
    fig.update_layout(
        barmode="stack",
        title="Defense Strategy Effectiveness",
        xaxis_title="Defense Strategy",
        yaxis_title="Number of Tests"
    )
    
    return fig


def create_confidence_reduction_chart(effectiveness_history: List[Dict]) -> go.Figure:
    """
    Create a chart showing confidence reduction for each defense strategy.
    
    Args:
        effectiveness_history: List of defense effectiveness results
        
    Returns:
        Plotly figure object
    """
    if not effectiveness_history:
        # Return empty chart if no data
        return go.Figure().add_annotation(
            text="No confidence reduction data yet",
            showarrow=False,
            font=dict(size=20)
        )
    
    # Prepare data
    data = []
    
    for entry in effectiveness_history:
        strategy = entry.get("strategy", "unknown")
        confidence_reduction = entry.get("confidence_reduction", 0)
        original_confidence = entry.get("original_confidence", 0)
        defended_confidence = entry.get("defended_confidence", 0)
        
        data.append({
            "Strategy": strategy,
            "Confidence Reduction": confidence_reduction,
            "Original Confidence": original_confidence,
            "Defended Confidence": defended_confidence
        })
    
    df = pd.DataFrame(data)
    avg_reduction = df.groupby("Strategy")["Confidence Reduction"].mean().reset_index()
    
    # Create bar chart
    fig = px.bar(
        avg_reduction,
        x="Strategy",
        y="Confidence Reduction",
        color="Confidence Reduction",
        title="Average Confidence Reduction by Defense Strategy",
        labels={"Confidence Reduction": "Avg. Confidence Reduction (0-1)"}
    )
    
    return fig


def create_attack_success_timeline(detection_history: List[Dict]) -> go.Figure:
    """
    Create a timeline showing attack success/failure over time.
    
    Args:
        detection_history: List of detection results with timestamps
        
    Returns:
        Plotly figure object
    """
    if not detection_history:
        # Return empty chart if no data
        return go.Figure().add_annotation(
            text="No attack timeline data yet",
            showarrow=False,
            font=dict(size=20)
        )
    
    # Prepare data
    data = []
    
    for i, entry in enumerate(detection_history):
        attempt_num = i + 1
        success = entry.get("injection_likely_successful", False)
        confidence = entry.get("confidence", 0)
        
        data.append({
            "Attempt": attempt_num,
            "Success": "Yes" if success else "No",
            "Confidence": confidence
        })
    
    df = pd.DataFrame(data)
    
    # Create line chart with markers
    fig = px.line(
        df,
        x="Attempt",
        y="Confidence",
        markers=True,
        color="Success",
        title="Attack Success Timeline",
        labels={"Attempt": "Attempt Number", "Confidence": "Confidence Score (0-1)"}
    )
    
    return fig