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
from components.predictive_goal import predictive_goal_date
from utils.data_utils import compute_trend, compute_weekly_averages, compute_moving_average, compute_moving_average_dates
from utils.charts import plot_weight_progression, plot_weekly_average_weight, plot_weekly_table, plot_seasonality
from components.info_display import show_total_weight_loss


# st.set_page_config(layout="wide")
st.title("📈 Weight Analysis")

# --- Use session_state to get user data ---
if 'user_data' not in st.session_state:
    st.info("Please upload your CSV file in the Data Editor page first.")
else:
    # Get user data
    df = st.session_state['user_data']
    dates = df['date'].values
    weights = df['weight'].values
    days = np.arange(1, len(weights) + 1)
    
    # Compute weekly averages and differences
    week_labels, weekly_means, weekly_diffs = compute_weekly_averages(df)
    moving_avg = compute_moving_average(weights)
    moving_avg_dates = compute_moving_average_dates(dates)
    trend = compute_trend(dates, weights)
    total_loss = weights[0] - weights[-1] if len(weights) > 0 else 0

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Weight Progression", "📅 Weekly Average", "📋 Weekly Table", "📊 Seasonality Analysis"])
    
    with tab1:
        # st.subheader("Weight Progression")
        show_total_weight_loss(total_loss)
        fig = plot_weight_progression(dates, weights, moving_avg_dates, moving_avg, trend, days)
        st.plotly_chart(fig, use_container_width=True)
        predictive_goal_date(weights, weekly_diffs)
        
    with tab2:
        st.subheader("Weekly Average Weight (Monday to Sunday)")
        fig2 = plot_weekly_average_weight(week_labels, weekly_means)
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

show_footer()