import argparse
import os
import csv
import pandas as pd
import numpy as np
import seaborn as sns
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor


data_file = 'data.csv'
sub_system_names = [
    '227001', '227002', '227003', '227004', '227005',
    '227006', '227007', '227008', '227009', '227010'
]

algorithms = [
    'zscore', 'iqr', 'localfactor'
]


def read_or_compose_dataframe(path):
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
    else:
        list_ = []
        
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            df = pd.read_json(full_path, lines=True)
            meta_df = json_normalize(df['metadata'])
            df = df.drop(columns='metadata')
            df = df.join(meta_df.add_prefix('meta_'))
            list_.append(df)
        df = pd.concat(list_, axis = 0, ignore_index = True)
        df.to_csv('data.csv', index=False)
    return df


def extract_info(df):
    sub_systems = df['meta_name'].str.split('-').str[0].unique()
    sub_systems = pd.Series(sub_systems)
    sub_systems = sub_systems.sort_values()
    sub_systems.to_csv("data/sub_systems.csv", index=False, header=None)
    print('Finished exporting all sub-systems to data/sub_systems.csv')

    sensors = df['meta_name'].str.split('-').str[1].unique()
    sensors = pd.Series(sensors)
    sensors = sensors.sort_values()
    sensors.to_csv("data/sensors.csv", index=False, header=None)
    print('Finished exporting all sensors to data/sensors.csv')

    df['sub_system'] = df['meta_name'].str.split('-').str[0]
    df['sensor'] = df['meta_name'].str.split('-').str[1]
    
    df = df[df['sub_system'].isin(sub_system_names)]
    for sub_system in sub_system_names:
        sub_sensors = df[df['sub_system'] == sub_system]['sensor'].unique()
        sub_sensors = pd.Series(sub_sensors)
        sub_sensors = sub_sensors.sort_values()
        sub_sensors.to_csv('data/' + sub_system + '_sensors.csv', index=False, header=None)
    
    print('Finished exporting sensors individually')
    sensor_names = df[df['sub_system'] == '227001']['sensor'].unique()
    sensor_names = pd.Series(sensor_names)
    sensor_names = sensor_names.sort_values()
    return df, sensor_names.values

def detect_outliers(df, sensors, algorithms):
    csv_base_path = 'results/{0}/csv'
    images_base_path = 'results/{0}/images'

    if 'localfactor' in algorithms:
        clf = LocalOutlierFactor(n_neighbors=50, contamination=0.1)

    for algorithm in algorithms:
        algo_csv_base_path = csv_base_path.format(algorithm)
        algo_images_base_path = images_base_path.format(algorithm)

        if not os.path.exists(algo_csv_base_path):
            os.makedirs(algo_csv_base_path)
    
        if not os.path.exists(algo_images_base_path):
            os.makedirs(algo_images_base_path)

    for sensor in sensors:
        csv_file_name = sensor + '.csv'
        image_file_name1 = sensor + '_plot.png'
        image_file_name2 = sensor + '_series.png'
        result = {}
        
        for algorithm in algorithms:
            result[algorithm] = []

        for sub_system in sub_system_names:
            sub_df = df[(df.sub_system == sub_system) & (df.sensor == sensor)]
    
            if 'zscore' in algorithms:
                # Calculate zscore
                zscore_df = sub_df.copy()
                zscore_df['zscore'] = (zscore_df['value'] - zscore_df['value'].mean())/zscore_df['value'].std()
                zscore_df['outlier'] = zscore_df['zscore'].apply(lambda x: True if np.absolute(x) > 2.5 else False)
                result['zscore'].append(zscore_df)

            if 'iqr' in algorithms:
                # Calculate iqr
                iqr_df = sub_df.copy()
                iqr_df = df[(df.sub_system == sub_system) & (df.sensor == sensor)].copy()
                iqr_df = iqr_df.sort_values(by='value')
                quatile = iqr_df.quantile([.25, .75])
                q1, q3 = quatile['value'].iloc[0], quatile['value'].iloc[1]
                iqr = q3 - q1
                lower_bound, upper_bound = q1 - (1.5 * iqr), q3 + (1.5 * iqr)
                iqr_df['outlier'] = iqr_df['value'].apply(lambda x: True if x < lower_bound or x > upper_bound else False)
                result['iqr'].append(iqr_df)

            if 'localfactor' in algorithms:
                # Calculate local outlier factor
                lf_df = sub_df.copy()
                lf_df['zscore'] = (lf_df['value'] - lf_df['value'].mean())/lf_df['value'].std()
                x = lf_df['zscore'].values
                x = np.nan_to_num(x)
                x_ = x.reshape(-1, 1)
                y = clf.fit_predict(x_)
                lf_df['loc'] = clf.negative_outlier_factor_
                lf_df['outlier'] = np.where(y == -1, True, False)
                result['localfactor'].append(lf_df)

                
        for algorithm in algorithms:
            df_by_sensor = pd.concat(result[algorithm], axis = 0, ignore_index = True)
            df_by_sensor.to_csv(os.path.join(csv_base_path.format(algorithm), csv_file_name), index=False)
            print('Finished exporting csv file about', sensor)
            sns.relplot(x="cloudTimestamp", y="value", hue="outlier", col="sub_system", col_wrap=3, data=df_by_sensor)
            plt.savefig(os.path.join(images_base_path.format(algorithm), image_file_name1))
            plt.close()
            sns.relplot(x="value", y="value", hue="outlier", col="sub_system", col_wrap=3, data=df_by_sensor)
            plt.savefig(os.path.join(images_base_path.format(algorithm), image_file_name2))
            plt.close()
            print('Finished exporting image file about', sensor)


if __name__ =='__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Specify the location of original files'
    )

    args = parser.parse_args()

    df = read_or_compose_dataframe(args.path)

    df, sensors = extract_info(df)

    detect_outliers(df, sensors, algorithms)
