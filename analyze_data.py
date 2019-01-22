import os
import argparse
import pandas as pd
import numpy as np


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file',
        type=str,
        default='data.csv',
        help='Specify the location of file'
    )

    args = parser.parse_args()
    analyze_data(args.file)