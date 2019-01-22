import os
import argparse
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


sub_system_names = [
    '227001', '227002', '227003', '227004', '227005',
    '227006', '227007', '227008', '227009', '227010'
]


def read_data(file):
    df = pd.read_csv(file)
    df.timestamp = pd.to_datetime(df.timestamp, format='%Y-%m-%d %H:%M:%S.%f')
    df['sub_system']=df['meta_name'].str.split('-').str[0]
    df['sensor']=df['meta_name'].str.split('-').str[1]
    df = df[df.sub_system.isin(sub_system_names)]
    df_sensors = pd.read_csv('data/227001_sensors.csv', header=None)
    return df, df_sensors[0].values


def detect_outlier_by_zscore(df, sensors):
    """
    using z-score values
    """
    print('Discovering outliers with zscore method')
    csv_base_path = 'results/zscore/csv'
    image_base_path = 'results/zscore/images'

    plt.figure(figsize=(12, 7))

    for sub_system in sub_system_names:
        csv_path = os.path.join(csv_base_path, sub_system)
        if not os.path.exists(csv_path):
            os.makedirs(csv_path)

        image_path = os.path.join(image_base_path, sub_system)
        if not os.path.exists(image_path):
            os.makedirs(image_path)
            
        for sensor in sensors:
            csv_file_name = '{0}.csv'.format(sensor)
            image_file_name = '{0}.png'.format(sensor)
            
            sub_df = df[(df.sub_system == sub_system) & (df.sensor == sensor)].copy()
            sub_df['zscore'] = (sub_df['value'] - sub_df['value'].mean())/sub_df['value'].std()
            sub_df['outlier'] = sub_df['zscore'].apply(lambda x: False if np.absolute(x) < 3 else True)
            sub_df.to_csv(os.path.join(csv_path, csv_file_name))
            sns.relplot(x="timestamp", y="value", hue="outlier", data=sub_df)
            plt.savefig(os.path.join(image_path, image_file_name))
            plt.clf()


def detect_outlier_by_iqr(df, sensors):
    """
    using IQR score
    """
    print('Discovering outliers with irq method')


def detect_outlier(df, sensors, algorithm):
    if algorithm == 'zscore':
        detect_outlier_by_zscore(df, sensors)
    elif algorithm == 'iqr':
        detect_outlier_by_iqr(df, sensors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file',
        type=str,
        default='data.csv',
        help='Select the file'
    )
    parser.add_argument(
        '--algorithm',
        type=str,
        choices=['zscore', 'iqr'],
        default='zscore',
        help='Select one of outlier algorithm'
    )
    args = parser.parse_args()
    df, sensors = read_data(args.file)
    detect_outlier(df, sensors, args.algorithm)
