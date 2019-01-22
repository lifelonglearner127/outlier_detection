import os
import argparse
import pandas as pd
from pandas.io.json import json_normalize


def extract_dataset(data_file, sub_system, sensor):
    df = pd.read_csv(data_file, sep='\t')
    df.timestamp = pd.to_datetime(df.timestamp, format='%Y-%m-%d %H:%M:%S.%f')
    df['sub_system']=df['meta_name'].str.split('-').str[0]
    df['sensor']=df['meta_name'].str.split('-').str[1]
    file_name = 'data/all.csv'

    if sub_system == 'all' and sensor != 'all':
        df = df[df.sensor == sensor]
        file_name = 'data/{0}.csv'.format(sensor)
    elif sensor == 'all' and sub_system != 'all':
        df = df[df.sub_system == sub_system]
        file_name = 'data/{0}.csv'.format(sub_system)
    elif sensor != 'all' and sub_system != 'all':
        df = df[(df.sub_system == sub_system) & (df.sensor == sensor)]
        file_name = 'data/{0}_{1}.csv'.format(sub_system, sensor)

    df.to_csv(file_name, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file',
        type=str,
        default='data.csv',
        help='Specify the original data set'
    )
    parser.add_argument(
        '--subsystem',
        type=str,
        default='all',
        help='Specify the sub-system name'
    )
    parser.add_argument(
        '--sensor',
        type=str,
        default='all',
        help='Specify the sensor'
    )
    args = parser.parse_args()
    extract_dataset(args.file, args.subsystem, args.sensor)
