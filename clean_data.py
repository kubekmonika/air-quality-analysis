import argparse
import plotly
import plotly.express as px
import pandas as pd


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-D', '--data',
        help='Provide a path to the xlsx file with measurement data',
        type=str
    )
    parser.add_argument(
        '-O', '--output',
        help='Name of the output csvfile',
        type=str
    )

    args = parser.parse_args()

    return args


def drop_columns_with_missing_values(data, threshold):
    """
    Drop columns with more missing values than the threshold
    """
    missing = data.isnull().mean()
    mask = missing[(missing < threshold)].index
    df = data[mask]

    print(f'{df.shape[1]} out of {data.shape[1]} columns left')

    return df


def interpolate_missing_values(data):
    """
    If there are up to 5 consecutive missing values
    then they are interpolated using a linear method
    """
    df = data.copy()

    for c in data.columns.tolist()[1:]:
        df[c] = df[c].interpolate(
            method='linear',
            limit=5,
            limit_area='inside',
        )
        i = data[c].isnull().sum() - df[c].isnull().sum()
        print(f'{i} values interpolated for {c}')

    return df


def fill_missing_values_with_mean(data):
    """
    Fill missing values with the mean value
    """
    df = data.copy()
    columns = df.columns.tolist()[1:]

    for c in columns:
        df[c] = df[c].fillna(df[c].mean())

    return df


def plot_max_median(data, file_name):
    """
    Plot max and median values for a given day
    """
    columns = data.columns.tolist()[1:]
    time_col = data.columns.tolist()[0]
    df = data[columns]
    df['Date'] = data[time_col].dt.date

    df = df.groupby('Date', as_index=False).agg(['max', 'median'])
    df = df.rename_axis(columns=['Parameter', 'Metric']).stack(0).stack()\
        .rename('Value').to_frame().reset_index()

    fig = px.line(df, x='Date', y='Value', color='Metric',
                  facet_col='Parameter', facet_col_wrap=1,
                  height=300*len(columns))

    plotly.offline.plot(fig, filename=f'{file_name}.html')


def read_data(data_file, sheet_name=0):
    """
    Read data and return it as a data frame
    """
    return pd.read_excel(
        data_file, skiprows=[0, 2, 3, 4, 5],
        sheet_name=sheet_name,
    )


def read_metadata(data_file, cols):
    """
    Read metadata and return it as a data frame
    """
    return pd.read_excel(
        data_file,
        sheet_name=0,
        usecols=cols,
    )


def prepare_data(data, interpolate, drop_threshold, add_hour=False):
    """
    Prepare the dataset with data
    """
    if interpolate:
        data = interpolate_missing_values(data)

    data = drop_columns_with_missing_values(data, drop_threshold)

    # plot_max_median(data, 'max_median')
    data_filled = fill_missing_values_with_mean(data)
    # plot_max_median(data, 'max_median_interpolated')

    data_melted = data.melt(data.columns.tolist()[0])
    data_filled_melted = data_filled.melt(data_filled.columns.tolist()[0])

    data_melted.columns = ["Czas", "Kod stacji", "Pomiar"]
    data_filled_melted.columns = ["Czas", "Kod stacji", "Pomiar (uzupełniony)"]

    data_merged = pd.merge(
        data_melted, data_filled_melted, on=["Czas", "Kod stacji"]
    )
    data_merged['Czas'] = data_merged['Czas'].astype(str)

    if add_hour:
        data_merged['Czas'] = data_merged['Czas'] + ' 00:00:00'
    return data_merged


def merge_two_datasets(data, metadata):
    """
    Combine the two datasets into one
    """
    return pd.merge(data, metadata, on='Kod stacji')


def save_dataset(data, file_name):
    """
    Save data to a csv file
    """
    data.to_csv(file_name, index=False)


if __name__ == '__main__':

    args = parse_args()

    data1h = read_data(args.data, sheet_name='2021_PM2.5_1H')
    data24h = read_data(args.data, sheet_name='2021_PM2.5_24H')

    metadata = read_metadata(
        args.data,
        ['Kod krajowy stacji', 'Wskaźnik - kod', 'Czas uśredniania',
         'Nazwa stacji', 'Szerokość geogr.', 'Długość geogr.'],
    )
    metamask = (
        (metadata['Wskaźnik - kod'] == 'PM2.5')
    )
    metadata = metadata.loc[
        metamask,
        ['Kod krajowy stacji', 'Nazwa stacji',
         'Szerokość geogr.', 'Długość geogr.']
     ]
    metadata = metadata.drop_duplicates()

    metadata.columns = [
        'Kod stacji', 'Nazwa stacji', 'φ N', 'λ E'
    ]

    data1h = prepare_data(
        data1h, interpolate=True, drop_threshold=0.06
    )
    print('Data 1h', data1h.head(), sep='/n')
    data24h = prepare_data(
        data24h, interpolate=False, drop_threshold=0.06, add_hour=True
    )
    print('Data 24h', data24h.head(), sep='/n')

    datamask = data24h['Kod stacji'].isin(data1h['Kod stacji'].tolist())
    data24h = data24h[~datamask]

    data = pd.concat([data1h, data24h])

    final_data = merge_two_datasets(data, metadata)

    print(final_data.sample(5))
    save_dataset(final_data, args.output)
