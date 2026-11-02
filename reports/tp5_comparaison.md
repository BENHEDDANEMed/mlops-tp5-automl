# Modele manuel ou modele AutoML ? (TP05)

| Critere | Manuel (RF 500/16) | AutoML (FLAML 90 s) |
|---|---|---|
| Famille de modele | foret aleatoire (500 arbres, profondeur 16) | XGBClassifier |
| F1 sur le jeu de test | 0.8669 | 0.8561 |
| Precision / rappel | 0.8837 / 0.8507 | 0.8692 / 0.8433 |
| Temps machine (s) | 2.86 (entrainement seul) | 90.00 (recherche et reentrainement) |
| Temps humain | non mesure au TP2, a renseigner par le groupe | non mesure : mise en place et analyse a inclure |
| Latence mediane (ms), essais 1 / 2 | 92.13 / 118.10 | 31.21 / 30.34 |
| Latence p95 (ms), essais 1 / 2 | 150.68 / 300.82 | 41.16 / 38.72 |
| Taille du fichier (Mio) | 13.374 | 0.279 |
| Explicabilite | importance des variables, 500 arbres, profondeur max. 16 | importance des variables, arbres et profondeur selon famille ; SHAP possible |
| Format dans MLflow | skops | cloudpickle |

## Decision (5 lignes)

Je retiens le modele AutoML pour le compromis qualite, latence et taille observe dans ce TP.  
Le F1 AutoML est 0.8561 contre 0.8669 ; il manque 21 fraudes contre 20 pour le manuel.  
Ses medianes sont 31.21/30.34 ms contre 92.13/118.10 ms, et il est 47.9 fois plus compact.  
Les deux modeles exposent des importances de variables ; je conserve le manuel comme reference et solution de retour arriere.  
Ce choix pedagogique doit etre confirme avec un cout metier des faux negatifs, d'autres partitions et un objectif de latence explicite.

## Protocole

Memes 5 000 transactions, partition 75/25 avec random_state=42, sans stratification (comme le sujet). 3750 lignes d'entrainement ; 1250 lignes de test dont 134 fraudes. Le jeu de test ne sert pas a choisir les hyperparametres. FLAML utilise 2 fils de calcul. Deux repetitions par modele, chacune avec 10 appels d echauffement et 200 appels mesures. Latence HTTP aller-retour avec requests, sur une transaction, sans concurrence et sans session persistante. Le p95 utilise statistics.quantiles(n=20), comme dans le sujet. Les temps humains ne sont pas inventes. Les tailles sont celles des copies joblib, pas celles des archives skops.

Registre sur 5005 (5000 deja occupe par le TP4) ; services sur 8100 et 8101. Parcours cloud facultatif non execute. Publication GitHub et envoi par courriel en attente.
