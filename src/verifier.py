"""Verifications reelles : registre, signatures et predictions HTTP vs modele local."""
import json
import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import requests
from common import ROOT, dataset, save_json


def main():
    _, Xte, _, _ = dataset()
    client = mlflow.MlflowClient()
    checks = {}
    for kind, port in [('automl', 8100), ('manuel', 8101)]:
        name = f'fraude-{kind}'
        registered = client.get_model_version_by_alias(name, 'production')
        loaded = mlflow.sklearn.load_model(f'models:/{name}@production')
        local = joblib.load(ROOT / f'models/model_{kind}.pkl')
        np.testing.assert_array_equal(loaded.predict(Xte), local.predict(Xte))
        response = requests.post(f'http://127.0.0.1:{port}/invocations',
            json={'dataframe_records': Xte.head(30).to_dict(orient='records')}, timeout=30)
        response.raise_for_status()
        np.testing.assert_array_equal(response.json()['predictions'], local.predict(Xte.head(30)))
        health = requests.get(f'http://127.0.0.1:{port}/health', timeout=10)
        health.raise_for_status()
        checks[kind] = {'alias_version': registered.version, 'status': registered.status,
                        'reload_predictions_equal': True, 'http_predictions_equal_30_rows': True,
                        'health_status': health.status_code}
    response = requests.post('http://127.0.0.1:8100/invocations',
        json={'dataframe_records': [{'montant': 8500.0}]}, timeout=10)
    assert response.status_code == 400, response.text
    assert all(col in response.text for col in ['anciennete', 'freq_24h', 'nuit']), response.text
    checks['invalid_request'] = {'status': response.status_code, 'body': response.json()}
    save_json('verification.json', checks)
    print(json.dumps(checks, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
