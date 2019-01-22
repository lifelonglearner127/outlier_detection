import os
import argparse
import pandas as pd
import numpy as np
from matplotlib.pyplot import savefig


sub_system_names = [
    '227001', '227002', '227003', '227004', '227005',
    '227006', '227007', '227008', '227009', '227010'
]


def analyze_data(file_name):
    df = pd.read_csv(file_name, sep='\t')
    df['sub_system']=df['meta_name'].str.split('-').str[0]
    df['sensor']=df['meta_name'].str.split('-').str[1]

    # Export sub systems
    sub_systems = df['sub_system'].drop_duplicates()
    sub_systems = sub_systems.sort_values()
    sub_systems.to_csv('sub_systems.csv', index=False)

    # Export sensors
    sensors = df['sensor'].drop_duplicates()
    sensors = sensors.sort_values()
    sensors.to_csv('sensors.csv', index=False)

    # Export sensors by sub systems
    for sub_system in sub_system_names:
        sub_sensors = df[df.sub_system == sub_system]['sensor']
        sub_sensors = sub_sensors.drop_duplicates()
        sub_sensors = sub_sensors.sort_values()
        sub_sensors.to_csv(sub_system + '.csv', index=False)

    # Observe the dataset we really cares about
    df = df[df['sub_system'].isin(sub_system_names)]
    
    # Export Images
    # Export bars
    bar_images_path = 'images/bars'
    if not os.path.exists(bar_images_path):
        os.makedirs(bar_images_path)
    
    for sensor in sub_sensors:
        print('Generationg ' + sensor + '.png file' )
        dataset_by_sensor = df[df.sensor == sensor]
        counts = dataset_by_sensor.groupby('sub_system').agg(len)['buildingId']
        counts.plot(kind='barh')
        savefig(os.path.join(bar_images_path, sensor + '.png'))

    return df


def export_dataset_by_sensor(df, sensor_name):
    df = df[df.meta_name.str.endswith(sensor_name)]
    df.to_csv(sensor_name + '.csv', index=False, sep='\t')
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
