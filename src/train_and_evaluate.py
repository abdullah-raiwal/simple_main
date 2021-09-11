# load train and test files
# load ml model
# evaluate model performance

import os
import argparse
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from get_data import read_params
import joblib
import json
import numpy as np


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def train_and_evaluate(config_path):
    config = read_params(config_path)
    test_data_path = config['split_data']['test_path']
    train_data_path = config['split_data']['train_path']
    random_state = config['base']['random_state']
    model_dir = config['model_dir']

    alpha = config['estimators']['ElasticNet']['params']['alpha']
    l1_ratio = config['estimators']['ElasticNet']['params']['l1_ratio']
    target_col = [config['base']['target_col']]

    train = pd.read_csv(train_data_path, sep=',', encoding='utf-8')
    test = pd.read_csv(test_data_path, sep=',', encoding='utf-8')

    train_y = train[target_col]
    test_y = test[target_col]

    train_x = train.drop(target_col, axis=1)
    test_x = test.drop(target_col, axis=1)

    lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=random_state)
    lr.fit(train_x, train_y)

    predicted_qualities = lr.predict(test_x)
    (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

    print("Elasticnet Model (alpha = %f, l1_ratio = %f):" % (alpha, l1_ratio))

    print("  RMSE: %s" % rmse)
    print("  MAE: %s" % mae)
    print("  R2: %s" % r2)

    params_file = config['score_files']['params']
    metric_file = config['score_files']['metrics']

    with open(metric_file, "w") as f:
        metrics = {
            'rmse': rmse,
            'mae': mae,
            'r2': r2
        }
        json.dump(metrics, f, indent=4)

    with open(params_file, "w") as f:
        params = {
            'alpha': alpha,
            'l1_ratio': l1_ratio
        }
        json.dump(params, f, indent=4)

    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(lr, model_path)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    train_and_evaluate(config_path=parsed_args.config)