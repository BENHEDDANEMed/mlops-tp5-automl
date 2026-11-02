import time
import joblib
import numpy as np
import mlflow.sklearn
from flaml import AutoML
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from common import ROOT, dataset, save_json, requirements, data_hash

BUDGET = 90


def main():
    Xtr, Xte, ytr, yte = dataset()
    (ROOT / 'models').mkdir(exist_ok=True)
    (ROOT / 'reports').mkdir(exist_ok=True)
    automl = AutoML()
    t0 = time.perf_counter()
    automl.fit(Xtr, ytr, task='classification', metric='f1', time_budget=BUDGET,
               seed=42, verbose=0, n_jobs=2, log_file_name='reports/flaml_tp5.log')
    duration = time.perf_counter() - t0
    model = automl.model.estimator
    pred, exported = automl.predict(Xte), model.predict(Xte)
    np.testing.assert_array_equal(pred, exported)
    f1 = f1_score(yte, exported)
    joblib.dump(model, ROOT / 'models/model_automl.pkl')
    mlflow.set_experiment('tp5-automl-deploiement')
    with mlflow.start_run(run_name='automl-90s') as run:
        mlflow.log_params({'outil': 'flaml', 'budget_s': BUDGET, 'famille': automl.best_estimator,
                           'n_jobs': 2, 'data_sha256': data_hash(), 'split_seed': 42})
        mlflow.log_params({f'cfg_{k}': v for k, v in automl.best_config.items()})
        mlflow.log_metrics({'f1': f1, 'duree_recherche_s': duration})
        mlflow.log_artifact('reports/flaml_tp5.log')
        info = mlflow.sklearn.log_model(model, name='model', input_example=Xte.head(3),
            registered_model_name='fraude-automl', serialization_format='cloudpickle',
            pip_requirements=requirements(automl.best_estimator))
    result = {'family': automl.best_estimator, 'class': type(model).__name__, 'f1': f1,
              'f1_flaml': f1_score(yte, pred), 'predictions_identical': True,
              'precision': precision_score(yte, exported), 'recall': recall_score(yte, exported),
              'confusion_matrix': confusion_matrix(yte, exported).tolist(),
              'duration_s': duration, 'config': automl.best_config, 'run_id': run.info.run_id,
              'model_uri': info.model_uri, 'version': str(info.registered_model_version),
              'size_bytes': (ROOT / 'models/model_automl.pkl').stat().st_size,
              'data_sha256': data_hash(), 'train_rows': len(Xtr), 'test_rows': len(Xte),
              'test_frauds': int(yte.sum())}
    save_json('automl_resultats.json', result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
