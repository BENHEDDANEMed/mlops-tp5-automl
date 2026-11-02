# TP05 - Créer et déployer un modèle AutoML

Comparaison d'un modèle XGBoost sélectionné par FLAML (budget de 90 secondes) et d'un Random Forest manuel (500 arbres, profondeur maximale 16), avec enregistrement dans MLflow, promotion par alias et service HTTP.

## Contenu du dépôt

- `donnees.py` : génération reproductible des 5 000 transactions synthétiques.
- `src/automl_deploy.py` et `src/modele_manuel.py` : entraînement et enregistrement des modèles.
- `src/common.py` : données, découpage et configuration partagés.
- `src/promouvoir.py` : attribution de l'alias `production`.
- `src/client.py` : prédictions et mesures de latence.
- `src/verifier.py` : contrôle des signatures et de la cohérence des prédictions.
- `demarrer.ps1` et `arreter.ps1` : gestion des services locaux.
- `requirements.txt` et `requirements-lock.txt` : dépendances et versions utilisées.
- `reports/tp5_comparaison.md` : comparaison et décision de production.

Le rapport PDF, les sources LaTeX, les captures et les résultats bruts restent dans le dossier de travail local. Ils sont exclus du suivi Git, ainsi que les données régénérables, les modèles binaires et les fichiers du serveur MLflow.

## Reproduire sous PowerShell

Depuis le dossier du projet, avec Python 3.14 :

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt

.\demarrer.ps1 -RegistreSeulement
& .\.venv\Scripts\python.exe donnees.py
& .\.venv\Scripts\python.exe src\automl_deploy.py
& .\.venv\Scripts\python.exe src\modele_manuel.py
& .\.venv\Scripts\python.exe src\promouvoir.py fraude-automl
& .\.venv\Scripts\python.exe src\promouvoir.py fraude-manuel

.\demarrer.ps1
& .\.venv\Scripts\python.exe src\verifier.py
& .\.venv\Scripts\python.exe src\client.py 8100 --repetition 1
& .\.venv\Scripts\python.exe src\client.py 8101 --repetition 1
& .\.venv\Scripts\python.exe src\client.py 8100 --repetition 2
& .\.venv\Scripts\python.exe src\client.py 8101 --repetition 2

.\arreter.ps1
```

Le registre est accessible sur [MLflow local](http://127.0.0.1:5005). Le port 5005 permet de conserver le serveur du TP4 sur 5000. Les prédictions utilisent les ports 8100 (AutoML) et 8101 (manuel).

Chaque nouvel entraînement crée une version dans le registre. L'alias est résolu au chargement : redémarrer les services après une nouvelle promotion. Les scripts de démarrage refusent un port déjà occupé.

## Résultats

| Critère | Manuel | AutoML |
|---|---:|---:|
| F1 sur le jeu de test | 0,8669 | 0,8561 |
| Médiane HTTP, essai 1 | 92,13 ms | 31,21 ms |
| Médiane HTTP, essai 2 | 118,10 ms | 30,34 ms |
| Taille de la copie joblib | 13,374 Mio | 0,279 Mio |

Le [tableau complet](reports/tp5_comparaison.md) précise les p95, les durées et les limites du protocole. Les temps humains n'ont pas été mesurés. Le parcours cloud facultatif n'a pas été exécuté.

Le modèle manuel est enregistré en `skops` dans MLflow et le modèle AutoML en `cloudpickle`. Les copies joblib servent à comparer les tailles. Charger uniquement les modèles provenant d'une source de confiance.
