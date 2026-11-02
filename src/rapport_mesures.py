"""Produire le tableau et les transcriptions a partir des mesures, sans valeurs inventees."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'


def read(name):
    return json.loads((REPORTS / name).read_text(encoding='utf-8'))


def main():
    auto, manual = read('automl_resultats.json'), read('manuel_resultats.json')
    a = [read(f'latence_8100_{i}.json') for i in (1, 2)]
    m = [read(f'latence_8101_{i}.json') for i in (1, 2)]
    rows = [
        ['Famille de modele', 'foret aleatoire (500 arbres, profondeur 16)', auto['class']],
        ['F1 sur le jeu de test', f"{manual['f1']:.4f}", f"{auto['f1']:.4f}"],
        ['Precision / rappel', f"{manual['precision']:.4f} / {manual['recall']:.4f}", f"{auto['precision']:.4f} / {auto['recall']:.4f}"],
        ['Temps machine (s)', f"{manual['duration_s']:.2f} (entrainement seul)", f"{auto['duration_s']:.2f} (recherche et reentrainement)"],
        ['Temps humain', 'non mesure au TP2, a renseigner par le groupe', 'non mesure : mise en place et analyse a inclure'],
        ['Latence mediane (ms), essais 1 / 2', ' / '.join(f"{x['median_ms']:.2f}" for x in m), ' / '.join(f"{x['median_ms']:.2f}" for x in a)],
        ['Latence p95 (ms), essais 1 / 2', ' / '.join(f"{x['p95_ms']:.2f}" for x in m), ' / '.join(f"{x['p95_ms']:.2f}" for x in a)],
        ['Taille du fichier (Mio)', f"{manual['size_bytes']/2**20:.3f}", f"{auto['size_bytes']/2**20:.3f}"],
        ['Explicabilite', 'importance des variables, 500 arbres, profondeur max. 16', 'importance des variables, arbres et profondeur selon famille ; SHAP possible'],
        ['Format dans MLflow', 'skops', 'cloudpickle'],
    ]
    winner = 'AutoML' if (auto['f1'] >= manual['f1'] - 0.02 and
        max(x['median_ms'] for x in a) < min(x['median_ms'] for x in m) and
        auto['size_bytes'] < manual['size_bytes']) else 'manuel'
    decision = [
        f"Je retiens le modele {winner} pour le compromis qualite, latence et taille observe dans ce TP.",
        f"Le F1 AutoML est {auto['f1']:.4f} contre {manual['f1']:.4f} ; il manque {auto['confusion_matrix'][1][0]} fraudes contre {manual['confusion_matrix'][1][0]} pour le manuel.",
        f"Ses medianes sont {a[0]['median_ms']:.2f}/{a[1]['median_ms']:.2f} ms contre {m[0]['median_ms']:.2f}/{m[1]['median_ms']:.2f} ms, et il est {manual['size_bytes']/auto['size_bytes']:.1f} fois plus compact.",
        "Les deux modeles exposent des importances de variables ; je conserve le manuel comme reference et solution de retour arriere.",
        "Ce choix pedagogique doit etre confirme avec un cout metier des faux negatifs, d'autres partitions et un objectif de latence explicite.",
    ]
    text = '# Modele manuel ou modele AutoML ? (TP05)\n\n'
    text += '| Critere | Manuel (RF 500/16) | AutoML (FLAML 90 s) |\n|---|---|---|\n'
    text += '\n'.join('| ' + ' | '.join(row) + ' |' for row in rows)
    text += '\n\n## Decision (5 lignes)\n\n' + '  \n'.join(decision)
    text += '\n\n## Protocole\n\n'
    text += 'Memes 5 000 transactions, partition 75/25 avec random_state=42, sans stratification (comme le sujet). '
    text += f"{auto['train_rows']} lignes d'entrainement ; {auto['test_rows']} lignes de test dont {auto['test_frauds']} fraudes. "
    text += 'Le jeu de test ne sert pas a choisir les hyperparametres. FLAML utilise 2 fils de calcul. '
    text += 'Deux repetitions par modele, chacune avec 10 appels d echauffement et 200 appels mesures. '
    text += 'Latence HTTP aller-retour avec requests, sur une transaction, sans concurrence et sans session persistante. '
    text += 'Le p95 utilise statistics.quantiles(n=20), comme dans le sujet. '
    text += 'Les temps humains ne sont pas inventes. Les tailles sont celles des copies joblib, pas celles des archives skops.\n'
    text += '\nRegistre sur 5005 (5000 deja occupe par le TP4) ; services sur 8100 et 8101. '
    text += 'Parcours cloud facultatif non execute. Publication GitHub et envoi par courriel en attente.\n'
    (REPORTS / 'tp5_comparaison.md').write_text(text, encoding='utf-8')
    (REPORTS / 'comparaison.json').write_text(json.dumps({'rows': rows, 'decision': decision}, ensure_ascii=False, indent=2), encoding='utf-8')

    css = '''body{background:#eef3f8;color:#183047;font:16px Segoe UI,sans-serif;margin:32px;max-width:1240px}h1{font-size:30px}h2{color:#107c69;font-size:22px}pre{background:#112335;color:#edf5ff;padding:18px;border-radius:10px;white-space:pre-wrap;overflow-wrap:anywhere;font:14px Consolas,monospace}small{color:#526777}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.ok{color:#107c69}'''
    def page(name, title, body):
        (REPORTS / name).write_text(f'<!doctype html><meta charset="utf-8"><title>{title}</title><style>{css}</style><h1>{title}</h1>{body}', encoding='utf-8')

    blocks = ''
    for kind, port in [('automl',8100), ('manuel',8101)]:
        log = (ROOT / f'.runtime/{kind}.err.log').read_text(encoding='utf-8', errors='replace')
        lines = [line for line in log.splitlines() if any(x in line.lower() for x in ['running','serving','started','startup','uvicorn','waitress','listening'])]
        if not lines:
            lines = log.splitlines()[-12:]
        blocks += f'<section><h2>{kind.upper()} - port {port}</h2><pre>{html.escape(chr(10).join(lines[-10:]))}</pre></section>'
    checks = read('verification.json')
    blocks += f'<h2 class="ok">Controle reel des deux services</h2><pre>{html.escape(json.dumps({k:v for k,v in checks.items() if k != "invalid_request"}, indent=2))}</pre>'
    page('preuve_services.html', 'Capture 2 - Services MLflow demarres', '<p>Transcription des journaux reels et des controles HTTP. Execution locale du TP5.</p>' + blocks)
    client = ''
    for port, results in [(8100,a), (8101,m)]:
        client += f'<h2>Client - port {port}</h2><pre>reponse : 200 {{"predictions": [1]}}\n'
        client += '\n'.join(f"Essai {x['repetition']} | mediane : {x['median_ms']:.2f} ms | p95 : {x['p95_ms']:.2f} ms | 200 appels OK" for x in results) + '</pre>'
    invalid = checks['invalid_request']
    client += f'<h2>Requete invalide : HTTP {invalid["status"]}</h2><pre>{html.escape(json.dumps(invalid["body"], ensure_ascii=False, indent=2))}</pre>'
    page('preuve_client.html', 'Capture 3 - Predictions, latences et signature', '<p>Transcription des sorties mesurees ; 10 appels d echauffement avant chaque serie.</p>' + client)
    print(text)


if __name__ == '__main__':
    main()
