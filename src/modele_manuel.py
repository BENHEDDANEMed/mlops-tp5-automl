import time
import joblib
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from common import ROOT, dataset, save_json, requirements, data_hash


def main():
    Xtr, Xte, ytr, yte = dataset()
    t0 = time.perf_counter()
    model = RandomForestClassifier(n_estimators=500, max_depth=16, random_state=42).fit(Xtr, ytr)
    duration = time.perf_counter() - t0
    pred = model.predict(Xte)
    f1 = f1_score(yte, pred)
    (ROOT / 'models').mkdir(exist_ok=True)
    joblib.dump(model, ROOT / 'models/model_manuel.pkl')
    mlflow.set_experiment('tp5-automl-deploiement')
    with mlflow.start_run(run_name='manuel-rf-500-16') as run:
        mlflow.log_params({'outil': 'scikit-learn', 'n_estimators': 500, 'max_depth': 16,
                           'data_sha256': data_hash(), 'split_seed': 42})
        mlflow.log_metrics({'f1': f1, 'duree_entrainement_s': duration})
        info = mlflow.sklearn.log_model(model, name='model', input_example=Xte.head(3),
            registered_model_name='fraude-manuel', serialization_format='skops',
            skops_trusted_types=['sklearn.tree._tree.Tree'], pip_requirements=requirements(skops=True))
    save_json('manuel_resultats.json', {'family': 'RandomForestClassifier', 'f1': f1,
        'precision': precision_score(yte, pred), 'recall': recall_score(yte, pred),
        'confusion_matrix': confusion_matrix(yte, pred).tolist(), 'duration_s': duration,
        'size_bytes': (ROOT / 'models/model_manuel.pkl').stat().st_size,
        'run_id': run.info.run_id, 'model_uri': info.model_uri,
        'version': str(info.registered_model_version), 'data_sha256': data_hash(),
        'feature_importances': dict(zip(Xtr.columns, model.feature_importances_.tolist()))})
    print(f'Manuel : F1={f1:.4f}, entrainement={duration:.2f}s, version={info.registered_model_version}', flush=True)


if __name__ == '__main__':
    main()
