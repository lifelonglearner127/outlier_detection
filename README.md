# outlier_detection
This project finds outliers from dataset
 - z-score
 - IQR
 - Local Outlier Factor

## Install & Run
```
git clone https://github.com/lifelonglearner127/outlier_detection.git
cd outlier_detection
unzip data/red-river.zip
pipenv install
pipenv shell
python detect_outliers.py --path data/red-river
```

## Results
After runnig the script, you can see `results` folder containing 3 sub-folders in project root directory.
 - `zscore`: This directory contains results detected by zscore
 - `iqr`: This directory contains results detected by IQR
 - `localfactor`: This directory contains results detected by Local Outlier Factor
 > Each directories contain `csv` and `images`

