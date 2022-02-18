import pandas as pd
import numpy as np
import plotly.express as px


def read_data(chem, mean=False):
    """Read data"""
    compounds = ('C6H6', 'CO', 'NO', 'NO2', 'NOx', 'O3', 'PM10', 'PM25', 'SO2')
    assert chem in compounds, f"`Wrong chemical compound,` should be one of {compounds}"

    if mean:
        data = pd.read_csv(f'../data/2020_{chem}_1g_mean.csv', parse_dates=[0])
    if not mean:
        data = pd.read_csv(f'../data/2020_{chem}_1g.csv', parse_dates=[0])
        data['Time'] = data['Time'] - pd.to_timedelta('1 hour')
    else:
        raise "Wrong mean parameter"

    return data


def save_mean_data(data, chem):
    """Save data"""
    compounds = ('C6H6', 'CO', 'NO', 'NO2', 'NOx', 'O3', 'PM10', 'PM25', 'SO2')
    assert chem in compounds, f"`Wrong chemical compound,` should be one of {compounds}"

    data.to_csv(f'../data/2020_{chem}_1g_mean.csv', index=False)


def plot_missing_values(data, stations):
    """Plot missing values as % of a given day"""
    df = data[stations].isnull()
    df['Date'] = data['Time'].dt.date
    df = df.groupby('Date', as_index=False).mean()
    df = df.melt(id_vars=['Date'], var_name='Station', value_name='Share of missing values')

    fig = px.line(df, x='Date', y='Share of missing values',
                  facet_col='Station', facet_col_wrap=1, height=300*len(stations))
    fig.show()


def plot_max_median(data, stations):
    """Plot max and median values for a given day"""
    df = data[stations]
    df['Date'] = data['Time'].dt.date
    df = df.groupby('Date', as_index=False).agg(['max', 'median'])
    df = df.rename_axis(columns=['Station', 'Metric']).stack(0).stack().rename('Value').to_frame().reset_index()
    fig = px.line(df, x='Date', y='Value', color='Metric',
                  facet_col='Station', facet_col_wrap=1, height=300*len(stations))
    fig.show()


def plot_correlation_between_stations(data, station1, station2, sample=2000):
    """Plot correlation between two given stations using OLS"""
    df = data.sample(sample)
    fig = px.scatter(df, x=station1, y=station2, trendline="ols", height=400)
    fig.show()


def remove_outliers(data, stations):
    """Remove outliers by comparing difference in values between stations. Replace them with NaN"""
    df = data.copy()
    min_vals = data[stations].min(axis=1).to_frame().values
    cut = data[stations].diff(axis=1).iloc[:, 1].dropna().std() * 4

    for s in stations:
        s_arr = df[s].values.reshape((-1, 1))
        mask = (s_arr - min_vals) > cut
        s_arr[mask] = np.nan
        df[s] = s_arr

    return df


def interpolate_missing_values(data, stations):
    """Interpolate up to 3 concurrent missing values using polynomial interpolation of 2nd degree"""
    df = data.copy()

    for s in stations:
        df[s] = df[s].interpolate(method='polynomial', order=2, limit=3)

    return df


def calculate_mean_value_across_all_stations(data):
    """Get mean value for each hour for all stations"""
    df = data[['Time']].copy()
    df['Mean value'] = data.drop('Time', axis=1).mean(axis=1)

    return df
