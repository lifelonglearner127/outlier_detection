import argparse
import os
import csv
import pandas as pd
import numpy as np
import seaborn as sns
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt



data_file = 'data.csv'
sub_system_names = [
    '227001', '227002', '227003', '227004', '227005',
    '227006', '227007', '227008', '227009', '227010'
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
    return df, df[df['sub_system'] == '227001']['sensor'].unique()


def detect_outliers_by_zscore_iqr(df, sensors):
    zscore_csv_base_path = 'results/zscore/csv'
    zscore_image_base_path = 'results/zscore/images'
    iqr_csv_base_path = 'results/iqr/csv'
    iqr_image_base_path = 'results/iqr/images'
    if not os.path.exists(zscore_csv_base_path):
        os.makedirs(zscore_csv_base_path)

    if not os.path.exists(zscore_image_base_path):
        os.makedirs(zscore_image_base_path)

    if not os.path.exists(iqr_csv_base_path):
        os.makedirs(iqr_csv_base_path)

    if not os.path.exists(iqr_image_base_path):
        os.makedirs(iqr_image_base_path)

    for sensor in sensors:
        csv_file_name = sensor + '.csv'
        image_file_name = sensor + '.png'
        zscore_list = []
        iqr_list = []

        for sub_system in sub_system_names:
            sub_df = df[(df.sub_system == sub_system) & (df.sensor == sensor)].copy()
            # Calculate zscore
            sub_df['zscore'] = (sub_df['value'] - sub_df['value'].mean())/sub_df['value'].std()
            sub_df['outlier'] = sub_df['zscore'].apply(lambda x: True if np.absolute(x) > 2.5 else False)
            zscore_list.append(sub_df)

            # Calculate iqr
            sub_df2 = df[(df.sub_system == sub_system) & (df.sensor == sensor)].copy()
            sub_df2 = sub_df2.sort_values(by='value')
            quatile = sub_df2.quantile([.25, .75])
            q1, q3 = quatile['value'].iloc[0], quatile['value'].iloc[1]
            iqr = q3 - q1
            lower_bound, upper_bound = q1 - (1.5 * iqr), q3 + (1.5 * iqr)
            sub_df2['outlier'] = sub_df2['value'].apply(lambda x: True if x < lower_bound or x > upper_bound else False)
            iqr_list.append(sub_df2)

        sensor_df_for_zscore = pd.concat(zscore_list, axis = 0, ignore_index = True)
        sensor_df_for_zscore.to_csv(os.path.join(zscore_csv_base_path, csv_file_name), index=False)
        print('Finished exporting csv file about', sensor)
        sns.relplot(x="cloudTimestamp", y="value", hue="outlier", col="sub_system", col_wrap=3, data=sensor_df_for_zscore)
        plt.savefig(os.path.join(zscore_image_base_path, image_file_name))
        plt.close()
        print('Finished exporting image file about', sensor)

        sensor_df_for_iqr = pd.concat(iqr_list, axis = 0, ignore_index = True)
        sensor_df_for_iqr.to_csv(os.path.join(iqr_csv_base_path, csv_file_name), index=False)
        print('Finished exporting csv file about', sensor)
        sns.relplot(x="cloudTimestamp", y="value", hue="outlier", col="sub_system", col_wrap=3, data=sensor_df_for_iqr)
        plt.savefig(os.path.join(iqr_image_base_path, image_file_name))
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

    detect_outliers_by_zscore_iqr(df, sensors)
