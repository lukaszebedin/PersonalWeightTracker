import plotly.graph_objects as go
import plotly.express as px
from plotly.colors import sample_colorscale

def plot_weight_progression(dates, weights, moving_avg_dates, moving_avg, trend, days):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=weights, mode='lines+markers', name='Daily Weight'))
    if len(moving_avg) > 0:
        fig.add_trace(go.Scatter(x=moving_avg_dates, y=moving_avg, mode='lines', name='7-day Moving Average'))
    fig.add_trace(go.Scatter(x=dates, y=trend(days), mode='lines', name='Linear Trend', line=dict(dash='dash')))
    fig.update_yaxes(title_text="Weight (kg)")
    fig.update_layout(height=600, width=1200, showlegend=True)
    return fig

def plot_weekly_average_weight(week_labels, weekly_means):
    """
    Generates a Plotly figure for weekly average weight progression.

    Args:
        week_labels (list): Labels for each week (e.g., "YYYY-Wnn").
        weekly_means (list): List of average weights for each week.

    Returns:
        go.Figure: Plotly figure object.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=week_labels,
        y=weekly_means,
        mode='lines+markers',
        name='Weekly Average Weight',
        marker=dict(color='green'),
        line=dict(color='green'),
        hovertemplate='Week %{x}<br>Average: %{y:.2f} kg<extra></extra>'
    ))
    fig.update_yaxes(title_text="Average Weight (kg)")
    fig.update_layout(
        height=600,
        width=1200,
        showlegend=True,
        font=dict(size=14),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    return fig

def plot_weekly_table(week_labels, weekly_means, weekly_diffs):
    # Use all valid weekly changes (loss and gain)
    valid_weekly_changes = [d for d in weekly_diffs if d is not None]
    avg_weekly_change = sum(valid_weekly_changes) / len(valid_weekly_changes) if valid_weekly_changes else None

    # For coloring, still extract negative diffs for color scale
    negative_diffs = [d for d in valid_weekly_changes if d < 0]
    min_loss = min(negative_diffs) if negative_diffs else -1
    max_loss = max(negative_diffs) if negative_diffs else -0.1


    DARK_GREEN_START = 0.3

    def normalize(val):
        if min_loss == max_loss:
            return 1.0
        return (val - max_loss) / (min_loss - max_loss)

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
    fig = go.Figure(data=[go.Table(header=header, cells=cells)])
    fig.update_layout(
        height=1200,
        width=800,
        margin=dict(l=80, r=80, t=100, b=80)
    )
    return fig, avg_weekly_change

def plot_day_of_week_bar(df):
    df['day_of_week'] = df['date'].dt.day_name()
    df['weight_diff'] = df['weight'].diff()
    day_avg = df.groupby('day_of_week')['weight_diff'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    fig = px.bar(
        x=day_avg.index,
        y=day_avg.values,
        labels={'x': 'Day of Week', 'y': 'Average Weight Change (kg)'},
        title="Average Weight Change by Day of Week",
        color=day_avg.values,
        color_continuous_scale="Blues"
    )
    return fig, day_avg

def plot_month_bar(df):
    df['month'] = df['date'].dt.month_name()
    df['weight_diff'] = df['weight'].diff()
    months_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    month_avg = df.groupby('month')['weight_diff'].mean().reindex(months_order)
    fig = px.bar(
        x=month_avg.index,
        y=month_avg.values,
        labels={'x': 'Month', 'y': 'Average Weight Change (kg)'},
        title="Average Weight Change by Month",
        color=month_avg.values,
        color_continuous_scale="Blues"
    )
    return fig, month_avg