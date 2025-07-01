import numpy as np
import pandas as pd
from collections import defaultdict

def compute_weekly_averages(df):
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
    weekly_diffs = [None] + [weekly_means[i] - weekly_means[i-1] for i in range(1, len(weekly_means))]
    return week_labels, weekly_means, weekly_diffs

def compute_moving_average(weights, window=7):
    """
    Compute a moving average for a 1D array-like of weights.
    Returns (moving_avg, moving_avg_indices)
    """
    weights = np.asarray(weights)
    if len(weights) >= window:
        moving_avg = np.convolve(weights, np.ones(window)/window, mode='valid')
        return moving_avg
    else:
        return np.array([])

def compute_moving_average_dates(dates, window=7):
    """
    Returns the dates that correspond to the moving average values.
    """
    if len(dates) >= window:
        return dates[window-1:]
    else:
        return []

def compute_trend(days, weights):
    days = np.arange(1, len(weights) + 1)
    if len(weights) > 1:
        z = np.polyfit(days, weights, 1)
        return np.poly1d(z)
    else:
        return lambda x: [weights[0]] * len(x)
