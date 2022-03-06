import pandas as pd

from .analysis import read_mean_data
from .weather import read_curated_weather_data


def read_combined_dataset(chem):
    """Join pollution and weather data"""

    weather = read_curated_weather_data()
    pollution = read_mean_data(chem)

    return pd.merge(pollution, weather, how='outer', on='Time')
