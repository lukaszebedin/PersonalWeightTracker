import streamlit as st
import pandas as pd
import plotly.express as px
import json
from Home import show_footer

st.set_page_config(layout="wide")
st.header("🏋️ Gym Progress Tracker (Custom Routine + FitNotes)")

# File uploaders
plan_file = st.file_uploader("Upload your workout plan (JSON file)", type="json")
fitnotes_file = st.file_uploader("Upload your FitNotes.csv file", type="csv")

st.info(
    """
    **How should your FitNotes CSV be formatted?**

    - Export your workout data from the FitNotes app as a CSV file.
    - The CSV must include at least these columns (case sensitive):
      - `Date` (format: YYYY-MM-DD, e.g., 2025-04-17)
      - `Exercise` (name of the exercise)
      - `Weight` (weight used, in kg or lbs)
      - `Reps` (number of repetitions)
    - Each row represents a single set.
    - Example of the first few rows of a valid CSV:

    ```
    Date,Exercise,Weight,Reps
    2025-04-17,Flat Barbell Bench Press,60,8
    2025-04-17,Flat Barbell Bench Press,60,7
    2025-04-17,Standing Barbell Shoulder Press,30,10
    2025-04-18,Pull Up,0,8
    2025-04-18,Seated Cable Row,40,12
    ```

    - You can export your data via **Settings > Export > Export Workouts to CSV** in the FitNotes app.

    **How should your workout plan JSON be formatted?**
    
    - The exercise names you put in your JSON file **must match exactly** the names as they appear in your FitNotes csv. 
    (Check for typos, extra spaces, or different capitalization.)

    - For example:
    ```
    {
      "Day 1": [
        "Flat Barbell Bench Press",
        "Standing Barbell Shoulder Press"
      ],
      "Day 2": [
        "Pull Up",
        "Seated Cable Row"
      ]
    }
    ```
    """
)

if plan_file and fitnotes_file:
    # Load workout plan JSON
    routine = json.load(plan_file)
    days = list(routine.keys())

    # Load FitNotes CSV and preprocess
    df = pd.read_csv(fitnotes_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Volume'] = df['Weight'] * df['Reps']

    # Date filter
    min_date, max_date = df['Date'].min(), df['Date'].max()
    date_range = st.date_input(
        "Select date range to visualize",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    if isinstance(date_range, tuple) or isinstance(date_range, list):
        df = df[(df['Date'] >= pd.to_datetime(date_range[0])) & (df['Date'] <= pd.to_datetime(date_range[1]))]

    # Create one tab per workout day
    tabs = st.tabs(days)

    for day_index, day in enumerate(days):
        exercises = routine[day]
        with tabs[day_index]:
            st.subheader(f"{day} - Total Volume per Exercise")
            for exercise in exercises:
                df_ex = df[df['Exercise'] == exercise]
                if not df_ex.empty:
                    summary = df_ex.groupby('Date')['Volume'].sum()
                    fig = px.line(
                        x=summary.index,
                        y=summary.values,
                        markers=True,
                        labels={'x': 'Date', 'y': 'Total Volume (kg)'},
                        title=exercise
                    )
                    if len(summary) > 2:
                        mov_avg = summary.rolling(3, min_periods=1).mean()
                        fig.add_scatter(
                            x=mov_avg.index,
                            y=mov_avg.values,
                            mode='lines',
                            name='Moving Average (3 sessions)',
                            line=dict(dash='dash')
                        )
                    st.plotly_chart(fig, use_container_width=True, key=f"{day}_{exercise}")
                else:
                    st.info(f"No data available for {exercise} in selected range.")
else:
    st.info("Please upload both your workout plan (JSON) and FitNotes CSV files to view your progress.")

show_footer()