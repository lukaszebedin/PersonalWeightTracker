import plotly.graph_objects as go
import pandas as pd

def plot_exercise_progress(summary, exercise):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary.index, y=summary['Series_Count'],
        name='Sets per session', marker_color='rgba(99,110,250,0.4)', yaxis='y2'
    ))
    fig.add_trace(go.Scatter(
        x=summary.index, y=summary['Avg_Volume_Per_Series'],
        name='Avg. volume/set', mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=summary.index, y=summary['Max_Weight'],
        name='Max weight', mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=summary.index, y=summary['Avg_Reps_Per_Series'],
        name='Avg. reps/set', mode='lines+markers'
    ))

    fig.update_layout(
        title=exercise,
        xaxis_title='Date',
        yaxis_title='Value',
        yaxis2=dict(
            title='Sets per session',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
