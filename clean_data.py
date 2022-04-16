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
        '-M', '--metadata',
        help='Provide a path to the xlsx file with stations metadata',
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


def prepare_dataset_with_data(data_file):
    """
    Premare a dataset with data
    """
    data = pd.read_excel(data_file, skiprows=[0, 2, 3, 4, 5])

    data = drop_columns_with_missing_values(data, 0.06)

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
    return data_merged


def prepare_dataset_with_metadata(data_file):
    """
    Premare a dataset with data
    """
    return pd.read_excel(data_file, usecols=[1, 3, 11, 13, 14])


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

    data = prepare_dataset_with_data(args.data)
    metadata = prepare_dataset_with_metadata(args.metadata)

    final_data = merge_two_datasets(data, metadata)

    save_dataset(final_data, args.output)
