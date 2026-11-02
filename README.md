# TP05 - Creation et deploiement d'un modele AutoML

Projet local : `C:\Users\pc\Documents\mlops-workspace\tp5-automl-deploy`.
Les donnees sont reprises du TP4 (5 000 transactions synthetiques, graine 7).
Le registre MLflow du TP5 ecoute sur **5005**, car le port 5000 est utilise par le TP4.
Les predictions utilisent les ports **8100** (AutoML) et **8101** (manuel).

## Reproduire sous PowerShell

```powershell
Set-Location "$HOME\Documents\mlops-workspace\tp5-automl-deploy"
# Seulement si .venv n'existe pas :
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt

# Registre local, puis entrainements (90 s pour FLAML) :
.\demarrer.ps1 -RegistreSeulement
& .\.venv\Scripts\python.exe donnees.py
& .\.venv\Scripts\python.exe src\automl_deploy.py
& .\.venv\Scripts\python.exe src\modele_manuel.py
& .\.venv\Scripts\python.exe src\promouvoir.py fraude-automl
& .\.venv\Scripts\python.exe src\promouvoir.py fraude-manuel

# Lancer les services de prediction :
.\demarrer.ps1
& .\.venv\Scripts\python.exe src\verifier.py
& .\.venv\Scripts\python.exe src\client.py 8100 --repetition 1
& .\.venv\Scripts\python.exe src\client.py 8101 --repetition 1
& .\.venv\Scripts\python.exe src\client.py 8100 --repetition 2
& .\.venv\Scripts\python.exe src\client.py 8101 --repetition 2

# Arreter uniquement les processus lances par ce projet :
.\arreter.ps1
```

Pour consulter uniquement les resultats existants : lancer le registre, puis ouvrir
[MLflow](http://127.0.0.1:5005). Chaque nouvel entrainement cree une nouvelle version.
L'alias `production` est resolu au demarrage du service ; apres une promotion,
redemarrer les services pour charger la nouvelle version.

## Livrables

- `src/` : entrainement, enregistrement, promotion, client et verification.
- `reports/tp5_comparaison.md` : mesures et decision de production.
- `reports/*_resultats.json`, `latence_*.json`, `verification.json` : preuves brutes.
- `reports/artefacts/` : MLmodel et dependances des deux modeles.
- Rapport PDF identifie avec les informations du rapport TP4.
- `requirements-lock.txt` : versions exactes de l'environnement utilise.

Les temps humains ne sont pas chronometres : le rapport les indique comme inconnus.
Les copies `models/*.pkl` servent seulement a comparer les tailles ; le modele manuel
est enregistre au format **skops** dans MLflow, l'AutoML au format **cloudpickle**.
Charger uniquement des artefacts provenant de ce projet de confiance.

Le parcours cloud facultatif n'a pas ete execute. Aucune ressource cloud n'a ete creee.
Le depot Git est local ; aucune publication GitHub ni aucun e-mail n'a ete effectue.
Apres validation du rendu, creer un depot public vide `mlops-tp5-automl`, puis :

```powershell
git remote add origin https://github.com/VOTRE_COMPTE/mlops-tp5-automl.git
git push -u origin main
```

Le compte rendu doit ensuite etre accompagne de l'URL reelle du depot.

## Regenerer les figures et le rapport

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements-rapport.txt
& .\.venv\Scripts\python.exe src\rapport_mesures.py
& .\.venv\Scripts\python.exe rendre_preuves.py
& .\.venv\Scripts\python.exe creer_rapport.py
```

Les captures du run, des parametres, de MLmodel et des dependances proviennent
de l'interface MLflow. Les figures des services et du client sont des transcriptions
des journaux et des mesures, explicitement identifiees dans le PDF.
