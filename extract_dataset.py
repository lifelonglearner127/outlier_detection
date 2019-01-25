import os
import argparse
import pandas as pd


sub_systems = [
    '227001'
]

sensors = [
    'Fluid temperature', 'Heat power', 'Flow'
]

def extract_dataset(data_file):
    df = pd.read_csv(data_file)
    df['sub_system']=df['meta_name'].str.split('-').str[0]
    df['sensor']=df['meta_name'].str.split('-').str[1]

    list_ = []
    for sub_system in sub_systems:
        for sensor in sensors:
            list_.append(df[(df.sub_system == sub_system) & (df.sensor == sensor)])

    df = pd.concat(list_, axis = 0, ignore_index = True)
    df.to_csv('data/sub_data.csv', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file',
        type=str,
        default='data.csv',
        help='Specify the original data set'
    )

    args = parser.parse_args()
    extract_dataset(args.file)
