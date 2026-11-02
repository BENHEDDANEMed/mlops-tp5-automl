import argparse
import mlflow
from common import save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('nom', choices=['fraude-automl', 'fraude-manuel'])
    args = parser.parse_args()
    client = mlflow.MlflowClient()
    versions = client.search_model_versions(f"name='{args.nom}'")
    if not versions:
        raise SystemExit(f'Aucune version pour {args.nom}. Entrainer le modele d abord.')
    latest = max(versions, key=lambda v: int(v.version))
    if latest.status != 'READY':
        raise SystemExit(f'Version {latest.version} non prete : {latest.status}')
    client.set_registered_model_alias(args.nom, 'production', latest.version)
    save_json(f'{args.nom}_alias.json', {'name': args.nom, 'alias': 'production',
                                       'version': latest.version, 'run_id': latest.run_id})
    print(f'{args.nom} : version {latest.version} promue (alias production)')


if __name__ == '__main__':
    main()
