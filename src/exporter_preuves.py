"""Copier uniquement les metadonnees utiles du registre dans les preuves versionnees."""
import html
import json
import shutil
from pathlib import Path
import mlflow
from common import ROOT, save_json


def main():
    client = mlflow.MlflowClient()
    versions = {}
    for kind in ('automl','manuel'):
        name = f'fraude-{kind}'
        model = client.get_model_version_by_alias(name, 'production')
        destination = ROOT / 'reports' / 'artefacts' / kind
        destination.mkdir(parents=True, exist_ok=True)
        for filename in ('MLmodel','requirements.txt','conda.yaml','python_env.yaml','input_example.json','serving_input_example.json'):
            local = mlflow.artifacts.download_artifacts(artifact_uri=f'models:/{name}@production/{filename}')
            shutil.copy2(local, destination / filename)
        versions[kind] = {'name': name, 'version': model.version, 'run_id': model.run_id,
                          'source': model.source, 'status': model.status}
    save_json('registre.json', versions)
    contents = (ROOT/'reports/artefacts/automl/MLmodel').read_text(encoding='utf-8')
    reqs = (ROOT/'reports/artefacts/automl/requirements.txt').read_text(encoding='utf-8')
    document = f'''<!doctype html><meta charset="utf-8"><title>MLmodel AutoML</title>
    <style>body{{font:16px Segoe UI;margin:28px;background:#eef3f8;color:#183047}}h1{{font-size:27px}}main{{display:grid;grid-template-columns:2fr 1fr;gap:20px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:13px Consolas;background:white;padding:18px;border:1px solid #c6d9e4;border-radius:8px}}</style>
    <h1>Capture 1b - Artefacts originaux de fraude-automl</h1><p>Version {versions['automl']['version']} - run {versions['automl']['run_id']}</p>
    <main><section><h2>MLmodel</h2><pre>{html.escape(contents)}</pre></section><section><h2>requirements.txt</h2><pre>{html.escape(reqs)}</pre><p>Copie textuelle des fichiers enregistres dans MLflow. Aucun modele binaire n est publie dans ces preuves.</p></section></main>'''
    (ROOT/'reports/preuve_mlmodel.html').write_text(document, encoding='utf-8')
    print(json.dumps(versions, indent=2))


if __name__ == '__main__':
    main()
