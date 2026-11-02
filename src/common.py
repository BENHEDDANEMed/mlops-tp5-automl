"""Configuration commune : memes donnees, partition et registre pour les deux modeles."""
import hashlib
import json
import os
import sys
from importlib.metadata import version
from pathlib import Path

import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8', errors='replace')
os.chdir(ROOT)
os.environ.setdefault('MLFLOW_DISABLE_AGENT_HINT', '1')
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5005'))


def dataset():
    df = pd.read_csv(ROOT / 'data/transactions.csv')
    return train_test_split(df.drop(columns='fraude'), df.fraude,
                            test_size=0.25, random_state=42)


def save_json(name, value):
    target = ROOT / 'reports' / name
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def requirements(family=None, skops=False):
    packages = ['scikit-learn', 'pandas', 'numpy', 'cloudpickle']
    if family in ('lgbm', 'xgboost', 'catboost'):
        packages.append({'lgbm': 'lightgbm'}.get(family, family))
    if skops:
        packages.append('skops')
    return [f'{p}=={version(p)}' for p in packages]


def data_hash():
    return hashlib.sha256((ROOT / 'data/transactions.csv').read_bytes()).hexdigest()
