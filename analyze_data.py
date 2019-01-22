import os
import argparse
import pandas as pd
import numpy as np
from matplotlib.pyplot import savefig
import seaborn as sns
import matplotlib.pyplot as plt


sub_system_names = [
    '227001', '227002', '227003', '227004', '227005',
    '227006', '227007', '227008', '227009', '227010'
]


def analyze_data(file_name):
    df = pd.read_csv(file_name)
    df.timestamp = pd.to_datetime(df.timestamp, format='%Y-%m-%d %H:%M:%S.%f')
    df['sub_system']=df['meta_name'].str.split('-').str[0]
    df['sensor']=df['meta_name'].str.split('-').str[1]

    # Export all sub systems
    sub_systems = df['sub_system'].drop_duplicates()
    sub_systems = sub_systems.sort_values()
    sub_systems.to_csv('data/sub_systems.csv', index=False)
    print('Finished exporting all sub-systems to data/sub_systems.csv')

    # Export all sensors
    sensors = df['sensor'].drop_duplicates()
    sensors = sensors.sort_values()
    sensors.to_csv('data/sensors.csv', index=False)
    print('Finished exporting all sensors to data/sensors.csv')

    # Export sensors by sub systems
    for sub_system in sub_system_names:
        sub_sensors = df[df.sub_system == sub_system]['sensor']
        sub_sensors = sub_sensors.drop_duplicates()
        sub_sensors = sub_sensors.sort_values()
        sub_sensors.to_csv('data/' + sub_system + '_sensors.csv', index=False)
        message = 'Finished exporting sensors from {0} to {1}_sensors.csv'.format(
            sub_system, sub_system
        )
        print(message)

    # Observe the dataset we really cares about
    df = df[df['sub_system'].isin(sub_system_names)]
    
    # Export Images
    # Export bars
    print('Started to exporting bar plot')
    bar_images_path = 'images/bars'
    if not os.path.exists(bar_images_path):
        os.makedirs(bar_images_path)

    plt.figure(figsize=(12,7))
    for sensor in sub_sensors:
        dataset_by_sensor = df[df.sensor == sensor]
        sns.countplot(
            x="sub_system", data=dataset_by_sensor,
            palette=sns.color_palette("bright", len(sub_system_names))
        )
        savefig(os.path.join(bar_images_path, sensor + '.png'))
        plt.clf()
        print('Generated ' + sensor + '.png file')

    # Export Series
    print('Started to exporting series plot')
    series_images_path = 'images/series'
    if not os.path.exists(series_images_path):
        os.makedirs(series_images_path)

    for sensor in sub_sensors:
        dataset_by_sensor = df[df.sensor == sensor]
        sns.lineplot(
            x="timestamp", y="value", hue="sub_system",
            palette=sns.color_palette("bright", len(sub_system_names)),
            data=dataset_by_sensor
        )
        savefig(os.path.join(series_images_path, sensor + '.png'))
        plt.clf()
        print('Generated ' + sensor + '.png file')

    return df


def export_dataset_by_sensor(df, sensor_name):
    df = df[df.meta_name.str.endswith(sensor_name)]
    df.to_csv(sensor_name + '.csv', index=False)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file',
        type=str,
        default='data.csv',
        help='Specify the location of file'
    )
    parser.add_argument(
        '--export',
        type=str,
        help='Specify the location of file'
    )

    args = parser.parse_args()
    df = analyze_data(args.file)
    
    if args.export:
        export_dataset_by_sensor(df, args.export)
