import os
import argparse
import pandas as pd
from pandas.io.json import json_normalize


def build_whole_dataset(path):
    files = os.listdir(path)
    header = True
    mode = 'w'
    
    for name in files:
        full_path = os.path.join(path, name)
        print('Reading data from', full_path)
        df = pd.read_json(full_path, lines=True)
        meta_df = json_normalize(df['metadata'])
        df = df.drop(columns='metadata')
        df = df.join(meta_df.add_prefix('meta_'))
        df.to_csv(
            'data.csv', sep='\t',
            date_format="%Y-%m-%d %H:%M:%S",
            header=header, mode=mode, index=False
        )
        header = False
        mode = 'a'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Specify the location of original files'
    )

    args = parser.parse_args()
    build_whole_dataset(args.path)
