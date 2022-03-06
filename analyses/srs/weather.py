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


def cloudiness_level(condition):
    """Map condition to the cloudiness level"""
    if condition == 'Fair':
        return 'Fair'
    if condition in ('Partly Cloudy', 'Thunder in the Vicinity'):
        return 'Partly Cloudy'
    if condition in ('Cloudy', 'Light Rain', 'Light Rain Shower', 'Light Drizzle', 'Light Snow Shower',
                    'Rain', 'Rain Shower', 'Wintry Mix', 'Light Rain with Thunder', 'Light Snow',
                    'Thunder', 'T-Storm', 'Drizzle', 'Snow', 'Heavy T-Storm', 'Mostly Cloudy'):
        return 'Cloudy'
    if condition in ('Mist', 'Fog', 'Shallow Fog', 'Patches of Fog', 'Haze'):
        return 'Fog'


def precipitation_level(condition):
    """Map condition to the precipitation level"""
    if condition in ('Rain', 'Rain Shower', 'Wintry Mix', 'T-Storm', 'Snow', 'Heavy T-Storm'):
        return 'Heavy'
    if condition in ('Light Rain', 'Light Rain Shower', 'Light Drizzle', 'Light Snow Shower',
                     'Light Rain with Thunder', 'Light Snow', 'Drizzle'):
        return 'Light'
    if condition in ('Fair', 'Partly Cloudy', 'Thunder in the Vicinity', 'Cloudy',
                    'Mostly Cloudy', 'Thunder'):
        return 'None'
    if condition in ('Mist', 'Fog', 'Shallow Fog', 'Patches of Fog', 'Haze'):
        return 'None'


def create_weather_features(data):
    """Create new features"""
    df = data.copy()
    condition = df.pop('Condition').str.replace(' / Windy', '')

    df['Cloudiness Level'] = condition.apply(cloudiness_level)
    df['Precipitation Level'] = condition.apply(precipitation_level)

    return df


def save_curated_weather_data(data):
    """Save weather data"""
    data.to_csv(f'../data/2020_weather_1g.csv', index=False)


def read_curated_weather_data():
    """Read weather data"""
    return pd.read_csv('../data/2020_weather_1g.csv', parse_dates=[0])
