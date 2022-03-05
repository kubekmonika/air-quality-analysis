import pandas as pd


def fahrenheit2celsius(f):
    """Convert the temperature"""
    return 5 / 9 * (f - 32)


def mph2kph(mph):
    """Convert mph to kph"""
    return mph * 1.609344


def inhg2hpa(inhg):
    """Convert inHg to hPa"""
    return inhg * 33.86389


def read_all_raw_weather_data():
    """Read all weather data files"""

    dates = [d.strftime("%Y-%m-%d") for d in pd.date_range('2020-01-01', '2020-12-31', freq='D')]
    columns = ['Time', 'Temperature', 'Wind Speed', 'Condition', 'Pressure']

    dfs = []

    for date in dates:

        df = pd.read_csv(
            f'../data/weather/wunderground_{date}.csv',
            usecols=columns,
        )
        df = df.dropna(how='all')

        # Time
        df['Time'] = pd.to_datetime(
            df['Time'].apply(lambda x: f'{date} {x}'),
            format='%Y-%m-%d %I:%M %p',
        )
        # Temperature
        df['Temperature C'] = df.pop('Temperature').str.extract(r'(\d+)') \
            .astype(float).apply(fahrenheit2celsius).astype(int)
        # Wind
        df['Wind Speed kph'] = df.pop('Wind Speed').str.extract(r'(\d+)') \
            .astype(float).apply(mph2kph).astype(int)
        # Pressure
        df['Pressure hPa'] = df.pop('Pressure').str.extract(r'(\d+\.\d+)') \
            .astype(float).apply(inhg2hpa).astype(int)

        dfs.append(df)

    # Concatenate the dataframes and resample them from 30 minutes to 1 hour
    df = pd.concat(dfs).set_index('Time').resample("1H").first()

    # Remove the midnight of the 1st of Jan to match the time range
    # with air pollution data time range
    df = df.iloc[1:].reset_index()

    return df


def save_curated_weather_data(data):
    """Save weather data"""
    data.to_csv(f'../data/2020_weather_1g.csv', index=False)
