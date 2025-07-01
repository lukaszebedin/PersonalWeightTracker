from datetime import timedelta
import numpy as np
import streamlit as st
import plotly.graph_objects as go

def predictive_goal_date(weights, weekly_diffs):        
    st.markdown("### 🎯 Predictive Goal Date")
    valid_weekly_changes = [d for d in weekly_diffs if d is not None]
    if len(valid_weekly_changes) > 0:
        avg_weekly_change = sum(valid_weekly_changes) / len(valid_weekly_changes)
    else:
        avg_weekly_change = 0
    
    if len(weights) > 0 and avg_weekly_change != 0:
        target_weight = st.number_input(
            "Set your target weight (kg):",
            min_value=30.0,
            max_value=300.0,
            value=float(weights[-1])
        )
        # Calculate weeks needed (sign handles loss or gain)
        weeks_needed = (target_weight - weights[-1]) / avg_weekly_change if avg_weekly_change != 0 else None
        if weeks_needed is not None and weeks_needed > 0:
            goal_date = np.datetime64('today', 'D') + np.timedelta64(int(weeks_needed * 7), 'D')
            st.success(
                f"At your current average rate (**{avg_weekly_change:+.2f} kg/week**), "
                f"you will reach **{target_weight} kg** in about **{weeks_needed:.1f} weeks** "
                f"(around **{goal_date.astype('M8[D]').astype(str)}**)."
            )
        elif weeks_needed is not None and weeks_needed < 0:
            st.info("You have already passed your target weight based on your current trend.")
        else:
            st.info("Not enough recent weight change to predict a goal date. Try tracking a few more weeks.")
            