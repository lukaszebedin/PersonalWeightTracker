from datetime import timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict
from plotly.colors import sample_colorscale
from Home import show_footer
import streamlit as st
import plotly.express as px

# st.set_page_config(layout="wide")
st.title("📈 Weight Analysis")

# --- Use session_state to get user data ---
if 'user_data' not in st.session_state:
    st.info("Please upload your CSV file in the Data Editor page first.")
else:
    df = st.session_state['user_data']

    # --- WEEKLY AVERAGE ---
    dates = df['date'].values
    weights = df['weight'].values

    weeks = defaultdict(list)
    for date, weight in zip(dates, weights):
        py_date = pd.Timestamp(date).to_pydatetime()
        year, week, weekday = py_date.isocalendar()
        weeks[(year, week)].append(weight)

    sorted_weeks = sorted(weeks.items())
    weekly_means = [np.mean(week_weights) for _, week_weights in sorted_weeks]
    week_labels = [f"{year}-W{week}" for (year, week), _ in sorted_weeks]
    weekly_diffs = [None]
    for i in range(1, len(weekly_means)):
        weekly_diffs.append(weekly_means[i] - weekly_means[i-1])
    
    days = np.arange(1, len(weights) + 1)
    initial_weight = weights[0] if len(weights) > 0 else 0

    window = 7
    if len(weights) >= window:
        moving_avg = np.convolve(weights, np.ones(window)/window, mode='valid')
        moving_avg_dates = dates[window-1:]
    else:
        moving_avg = []
        moving_avg_dates = []

    z = np.polyfit(days, weights, 1) if len(weights) > 1 else [0, initial_weight]
    trend = np.poly1d(z)
    total_loss = initial_weight - weights[-1] if len(weights) > 0 else 0

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Weight Progression", "📅 Weekly Average", "📋 Weekly Table", "📊 Seasonality Analysis"])
    
    with tab1:
        st.subheader("Weight Progression")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=dates,
            y=weights,
            mode='lines+markers',
            name='Daily Weight',
            text=[f'Day {day}<br>Date: {pd.Timestamp(date).strftime("%Y-%m-%d")}' for day, date in zip(days, dates)],
            hovertemplate='%{text}<br>Weight: %{y} kg<extra></extra>'
        ))
        if len(moving_avg) > 0:
            fig1.add_trace(go.Scatter(
                x=moving_avg_dates,
                y=moving_avg,
                mode='lines',
                name='7-day Moving Average',
                hovertemplate='Date: %{x|%Y-%m-%d}<br>Moving Avg: %{y:.2f} kg<extra></extra>'
            ))
        fig1.add_trace(go.Scatter(
            x=dates,
            y=trend(days),
            mode='lines',
            name='Linear Trend',
            line=dict(dash='dash'),
            hovertemplate='Date: %{x|%Y-%m-%d}<br>Trend: %{y:.2f} kg<extra></extra>'
        ))
        if len(weights) > 0:
            if len(weights) > 0:
                st.markdown(f"**Total weight lost:** `{total_loss:.1f} kg`")
        fig1.update_yaxes(title_text="Weight (kg)")
        fig1.update_layout(
            height=600,
            width=1200,
            showlegend=True,
            font=dict(size=14),
            margin=dict(l=80, r=80, t=100, b=80)
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # --- PREDICTIVE GOAL DATE ---
        st.markdown("### 🎯 Predictive Goal Date")
        valid_weekly_changes = [d for d in weekly_diffs if d is not None]
        if valid_weekly_changes:
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
            goal_date = np.datetime64('today', 'D') + timedelta(weeks=weeks_needed)
            st.success(
                f"At your current average rate (**{avg_weekly_change:+.2f} kg/week**), "
                f"you will reach **{target_weight} kg** in about **{weeks_needed:.1f} weeks** "
                f"(around **{goal_date.strftime('%Y-%m-%d')}**)."
            )
        elif weeks_needed is not None and weeks_needed < 0:
            st.info("You have already passed your target weight based on your current trend.")
        else:
            st.info("Not enough recent weight change to predict a goal date. Try tracking a few more weeks.")
        
    with tab2:
        st.subheader("Weekly Average Weight (Monday to Sunday)")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=week_labels,
            y=weekly_means,
            mode='lines+markers',
            name='Weekly Average Weight',
            marker=dict(color='green'),
            line=dict(color='green'),
            hovertemplate='Week %{x}<br>Average: %{y:.2f} kg<extra></extra>'
        ))
        fig2.update_yaxes(title_text="Average Weight (kg)")
        fig2.update_layout(
            height=600,
            width=1200,
            showlegend=True,
            font=dict(size=14),
            margin=dict(l=80, r=80, t=100, b=80)
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        # st.subheader("Weekly Averages and Differences Table")
        # Filter only weeks with weight loss
        weight_losses = [d for d in weekly_diffs if d is not None and d < 0]

        if len(weight_losses) > 0:
            avg_weekly_loss = abs(sum(weight_losses) / len(weight_losses))
            st.markdown(f"### Average weekly weight loss rate: `{avg_weekly_loss:.3f} kg/week`")
        else:
            st.markdown("### No weeks with weight loss recorded.")
        
        # Extract negative diffs (weight losses)
        negative_diffs = [d for d in weekly_diffs if d is not None and d < 0]
        min_loss = min(negative_diffs) if negative_diffs else -1
        max_loss = max(negative_diffs) if negative_diffs else -0.1
        
        # Only use the darker part of the Greens colorscale (e.g., from 0.3 to 1)
        DARK_GREEN_START = 0.3  # adjust higher for even darker minimum green   
        
        # Normalize function for values between 0 and 1 for colorscale sampling
        def normalize(val):
            
            if min_loss == max_loss:
                return 1.0
            return (val - max_loss) / (min_loss - max_loss)

        # Use Plotly's built-in Greens colorscale (from light to dark green)
        colorscale = 'Greens'

        def get_color(diff):
            if diff is None:
                return '#2D333B'  # default gray
            elif diff < 0:
                norm_val = normalize(diff)
                mapped_val = DARK_GREEN_START + (1 - DARK_GREEN_START) * norm_val
                color = sample_colorscale("Greens", mapped_val)[0]
                return color
            elif diff > 0:
                return 'rgb(178,34,34)'  # red for gain
            else:
                return '#2D333B'  # gray for no change or first row

        n_rows = len(week_labels)
        col1_colors = ['#2D333B'] * n_rows
        col2_colors = ['#2D333B'] * n_rows
        col3_colors = [get_color(d) for d in weekly_diffs]

        cell_colors = [col1_colors, col2_colors, col3_colors]

        header = dict(
            values=["Week", "Average Weight (kg)", "Difference from Previous (kg)"],
            fill_color='#22272B',
            align='center',
            font=dict(size=12)
        )
        cells = dict(
            values=[
                week_labels,
                [f"{m:.3f}" for m in weekly_means],
                ["--" if d is None else f"{d:+.3f}" for d in weekly_diffs]
            ],
            fill_color=cell_colors,
            align='center',
            font=dict(size=13)
        )
        fig3 = go.Figure(data=[go.Table(header=header, cells=cells)])
        fig3.update_layout(
            height=1200,
            width=800,
            margin=dict(l=80, r=80, t=100, b=80)
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab4:
        st.info("Negative values mean weight loss on average; positive means weight gain. Use these insights to spot patterns and adjust your habits!")
        
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])

        # --- By Day of Week ---
        df['day_of_week'] = df['date'].dt.day_name()
        df['weight_diff'] = df['weight'].diff()
        day_avg = df.groupby('day_of_week')['weight_diff'].mean().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])

        fig_dow = px.bar(
            x=day_avg.index,
            y=day_avg.values,
            labels={'x': 'Day of Week', 'y': 'Average Weight Change (kg)'},
            title="Average Weight Change by Day of Week",
            color=day_avg.values,
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_dow, use_container_width=True)
        
        # --- Day of Week Summary ---
        max_gain_day = day_avg.idxmax()
        max_gain = day_avg.max()
        max_loss_day = day_avg.idxmin()
        max_loss = day_avg.min()
        if max_gain > 0:
            st.info(f"**You tend to gain the most weight on {max_gain_day} (+{max_gain:.2f} kg on average).**")
        if max_loss < 0:
            st.success(f"**You tend to lose the most weight on {max_loss_day} ({max_loss:.2f} kg on average).**")
        if all(abs(day_avg.values) < 0.05):
            st.write("Your weight changes are very consistent across the week, with no strong daily patterns.")

        st.markdown("---")

        # --- By Month ---
        df['month'] = df['date'].dt.month_name()
        month_avg = df.groupby('month')['weight_diff'].mean()
        # Ensure months are in calendar order
        months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']
        month_avg = month_avg.reindex(months_order)

        fig_month = px.bar(
            x=month_avg.index,
            y=month_avg.values,
            labels={'x': 'Month', 'y': 'Average Weight Change (kg)'},
            title="Average Weight Change by Month",
            color=month_avg.values,
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_month, use_container_width=True)
        
        # --- Month Summary ---
        max_month_gain = month_avg.idxmax()
        max_month_gain_val = month_avg.max()
        max_month_loss = month_avg.idxmin()
        max_month_loss_val = month_avg.min()
        if max_month_gain_val > 0:
            st.info(f"**You tend to gain the most weight in {max_month_gain} (+{max_month_gain_val:.2f} kg on average).**")
        if max_month_loss_val < 0:
            st.success(f"**You tend to lose the most weight in {max_month_loss} ({max_month_loss_val:.2f} kg on average).**")
        if all(abs(month_avg.dropna().values) < 0.05):
            st.write("Your weight changes are very consistent across months, with no strong seasonal patterns.")

        st.caption("Negative values mean weight loss on average; positive means weight gain. Use these insights to spot patterns and adjust your habits!")


show_footer()