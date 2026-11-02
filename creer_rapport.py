"""Rapport PDF construit exclusivement a partir des resultats du TP5."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, Preformatted
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'
OUT = ROOT / 'BENHEDDANE_Mohamed_5IASD_G8.pdf'


def main():
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='ArialBold')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyFR', fontName='Arial', fontSize=10, leading=15, spaceAfter=9, textColor=colors.HexColor('#24384b')))
    styles.add(ParagraphStyle(name='TitleFR', fontName='ArialBold', fontSize=27, leading=33, spaceAfter=15, textColor=colors.HexColor('#173e5b')))
    styles.add(ParagraphStyle(name='HeadingFR', fontName='ArialBold', fontSize=17, leading=22, spaceAfter=12, textColor=colors.HexColor('#107c69')))
    styles.add(ParagraphStyle(name='SmallFR', fontName='Arial', fontSize=8, leading=11, spaceAfter=6, textColor=colors.HexColor('#536779')))
    styles.add(ParagraphStyle(name='TableFR', fontName='Arial', fontSize=8.3, leading=11))
    styles.add(ParagraphStyle(name='LabelFR', fontName='ArialBold', fontSize=11, leading=15, spaceBefore=9, spaceAfter=6, textColor=colors.HexColor('#173e5b')))
    story = []
    def p(text, style='BodyFR'):
        story.append(Paragraph(text, styles[style]))
    def heading(text):
        p(text, 'HeadingFR')
    def table(rows, widths):
        header_style = ParagraphStyle('HeaderFR', parent=styles['TableFR'], textColor=colors.white, fontName='ArialBold')
        cells = [[Paragraph(escape(str(x)).replace('\n', '<br/>'), header_style if i == 0 else styles['TableFR'])
                  for x in row] for i,row in enumerate(rows)]
        t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#173e5b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef4f8'),colors.white]),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#107c69'))]))
        story.append(t)
        story.append(Spacer(1, 10))
    def screenshot(name, max_height=12*cm):
        path = REPORTS / 'captures' / name
        if not path.exists():
            raise FileNotFoundError(f'Capture manquante : {path}')
        pic = Image(str(path))
        scale = min(17*cm / pic.imageWidth, max_height / pic.imageHeight)
        pic.drawWidth, pic.drawHeight = pic.imageWidth*scale, pic.imageHeight*scale
        story.append(pic)
        story.append(Spacer(1, 8))
    def read(name):
        return json.loads((REPORTS / name).read_text(encoding='utf-8'))

    auto, manual, comparison = read('automl_resultats.json'), read('manuel_resultats.json'), read('comparaison.json')
    lat = {port:[read(f'latence_{port}_{i}.json') for i in (1,2)] for port in (8100,8101)}

    # Page 1
    p('EMSI | Rabat', 'LabelFR')
    p('5IASD - Groupe G8 - Année universitaire 2026-2027', 'SmallFR')
    story.append(Spacer(1, 38))
    p('Compte rendu de TP05', 'TitleFR')
    p('Créer et déployer un modèle AutoML', 'HeadingFR')
    p('Du modèle entraîné au service HTTP : registre MLflow, alias, consommation et comparaison avec une référence manuelle.')
    story.append(Spacer(1, 24))
    table([['Réalisé par', 'Formation'],['Mohamed BENHEDDANE\nYassir DRISSI\nZineb BAQLOUL','5IASD - G8'],['Encadrante','Pr. H. Naciri'],['Date des mesures','02 novembre 2026']], [10*cm,7*cm])
    p('Identité du groupe reprise du rapport TP04 présent dans le même espace de travail.', 'SmallFR')
    heading('Objectif et périmètre')
    p('Entraîner FLAML avec un budget de 90 secondes, enregistrer son gagnant et le Random Forest du TP2, puis servir leurs versions promues sur deux points de terminaison locaux. La comparaison porte sur la qualité, la latence, la taille et l’explicabilité.')
    p('Les blocs locaux sont exécutés. Le parcours cloud facultatif est exclu. Le dépôt Git est préparé localement ; la publication GitHub et l’envoi du rendu restent à effectuer après validation.')
    p('Adaptation au poste : registre sur 127.0.0.1:5005, car un serveur du TP4 utilise déjà 5000. Services de prédiction sur 8100 et 8101, conformément au sujet.')
    story.append(PageBreak())

    # Page 2
    heading('1. Protocole et résultats mesurés')
    p(f"Le générateur du TP4 produit 5 000 transactions synthétiques (graine 7), dont 568 fraudes. Les variables sont montant, anciennete, freq_24h et nuit ; la cible est fraude. La partition commune contient {auto['train_rows']} observations d’entraînement et {auto['test_rows']} de test, dont {auto['test_frauds']} fraudes.")
    p('Le découpage utilise test_size=0.25 et random_state=42, sans stratification, comme le sujet. FLAML choisit ses réglages sur son découpage interne d’entraînement/validation ; le test est réservé à l’évaluation finale. Deux fils de calcul bornent la recherche sur le poste.')
    table([['Critère','Manuel RF 500/16','AutoML FLAML 90 s']] + comparison['rows'], [5.2*cm,5.9*cm,5.9*cm])
    p('Mio = 1 048 576 octets. Les tailles portent sur les copies joblib, afin de comparer le même format. Le temps machine manuel exclut le réglage humain du TP2. Les durées humaines sont inconnues et doivent être précisées par le groupe.', 'SmallFR')
    p('Décision de production (5 lignes)', 'LabelFR')
    for line in comparison['decision']:
        p(escape(line), 'SmallFR')
    story.append(PageBreak())

    # Page 3
    heading('2. Entraînement, export et registre')
    p(f"FLAML retient <b>{auto['class']}</b> (famille {auto['family']}) après {auto['duration_s']:.2f} s. Le F1 de l’objet FLAML et celui de l’estimateur extrait sont tous deux {auto['f1']:.4f}. L’égalité de toutes les prédictions de test est vérifiée avant l’enregistrement.")
    p(f"Run AutoML : <font size='8'>{auto['run_id']}</font><br/>Run manuel : <font size='8'>{manual['run_id']}</font>", 'SmallFR')
    p('Capture 1a - Run automl-90s dans MLflow', 'LabelFR')
    screenshot('capture1_run.jpg', 8.5*cm)
    p('Capture 1b - Famille et réglages gagnants', 'LabelFR')
    screenshot('capture1_parametres.jpg', 8.3*cm)
    story.append(PageBreak())
    heading('2.1. Packaging du modèle AutoML')
    p('Capture 1c - Fichier MLmodel et dépendances du gagnant', 'LabelFR')
    screenshot('capture1_mlmodel.jpg', 15*cm)
    p('Dépendances enregistrées dans MLflow', 'LabelFR')
    screenshot('capture1_dependances.jpg', 6.2*cm)
    p('Formats et dépendances vérifiés', 'LabelFR')
    p('AutoML : cloudpickle ; Python 3.14.7 ; MLflow 3.17.2 ; scikit-learn 1.9.1 ; XGBoost 2.1.4 ; pandas 3.1.0 ; NumPy 2.5.4. Le modèle manuel est enregistré en skops. La signature attend montant en double et les trois autres variables en entiers longs.')
    p('Les fichiers originaux MLmodel et requirements.txt des deux modèles sont conservés dans reports/artefacts/. Les flavors python_function et sklearn permettent le chargement et le service HTTP.', 'SmallFR')
    story.append(PageBreak())

    # Page 4
    heading('3. Promotion et services HTTP')
    p(f"Les modèles fraude-automl et fraude-manuel sont enregistrés en version {auto['version']} et {manual['version']}. Le script promouvoir.py attribue l’alias production à la dernière version READY de chacun. Les services chargent models:/fraude-automl@production et models:/fraude-manuel@production.")
    p('Capture 2 - Journaux des services et contrôles HTTP', 'LabelFR')
    screenshot('capture2_services.jpg', 15*cm)
    p('Cette figure est une transcription des journaux réels, pas une capture de fenêtres de terminaux. Les fichiers .runtime/automl.err.log et manuel.err.log conservent les sorties originales.', 'SmallFR')
    p('Les deux /health répondent HTTP 200. Les modèles rechargés depuis les alias reproduisent toutes les prédictions du test local. Pour chaque service, un lot de 30 transactions envoyé par HTTP reproduit aussi les prédictions locales.')
    p('L’alias est résolu au chargement : modifier production ne remplace pas le modèle déjà en mémoire. Un redémarrage du service est nécessaire après promotion ou retour à une ancienne version.')
    story.append(PageBreak())

    # Page 5
    heading('4. Client, latences et requête invalide')
    p('Le client envoie montant=8500.0, anciennete=3, freq_24h=9 et nuit=1. Chaque service renvoie HTTP 200 et predictions=[1]. Chaque répétition comprend 10 appels d’échauffement non mesurés et 200 appels chronométrés avec perf_counter ; les réponses sont validées.')
    p('Capture 3 - Résultats du client et rejet de la requête invalide', 'LabelFR')
    screenshot('capture3_client.jpg', 15*cm)
    p('La requête contenant seulement montant est rejetée avec HTTP 400 : anciennete, freq_24h et nuit sont manquantes. Il s’agit d’une validation de schéma, pas d’une validation métier de la transaction.')
    p('Les mesures incluent la connexion locale, JSON, le contrôle de schéma et l’inférence ; elles n’isolent pas le temps du modèle. Les appels sont séquentiels, sans session persistante ni charge concurrente. Le p95 est calculé avec statistics.quantiles(n=20), comme dans le sujet. Aucune latence cloud n’a été mesurée.', 'SmallFR')
    story.append(PageBreak())

    # Page 6
    heading('5. Réponses aux questions 1 à 3')
    p('Question 1 - Quel modèle mettre en production ?', 'LabelFR')
    p('Je retiendrais AutoML (XGBoost) pour ce TP : le modèle est nettement plus compact et plus rapide, avec une baisse de F1 de 0,0109 et une fraude supplémentaire manquée sur ce test. Le manuel reste préférable si ce coût de détection domine. Les importances globales sont accessibles pour les deux ensembles d’arbres ; une explication locale peut être étudiée avec SHAP. Une importance ne démontre pas un lien causal.')
    p('La matrice de confusion est fournie dans les résultats JSON (ordre : [[vrais négatifs, faux positifs], [faux négatifs, vrais positifs]]). Un jeu synthétique et un unique découpage ne suffisent pas à garantir une performance opérationnelle ; il faut fixer un coût des fraudes manquées et un objectif de latence.')
    p('Question 2 - Coût mensuel d’un point de terminaison cloud', 'LabelFR')
    p('Consultation : <b>02/11/2026</b>. Hypothèse illustrative : une machine n1-standard-2 dans us-central1, à la demande, sans remise, un modèle déployé en continu. Le tarif officiel de prédiction consulté est <b>0,1095 USD par heure</b>. Pour 30 jours : 30 × 24 × 0,1095 = <b>78,84 USD</b> ; pour 730 heures : <b>79,94 USD</b>.')
    p('Une machine active reste facturée sans requêtes. Estimation hors entraînement, stockage, réseau, taxes et explications supplémentaires ; elle n’est pas un devis pour europe-west1. La page précise que l’inférence AutoML tabulaire suit les tarifs des modèles personnalisés. Aucun déploiement facturé n’a été lancé. [S1]')
    p('Question 3 - Pourquoi le cloud est généralement plus lent ?', 'LabelFR')
    p(f"Sur ce poste, les médianes AutoML sont {lat[8100][0]['median_ms']:.2f} et {lat[8100][1]['median_ms']:.2f} ms ; celles du manuel sont {lat[8101][0]['median_ms']:.2f} et {lat[8101][1]['median_ms']:.2f} ms. En cloud s’ajoutent le trajet réseau jusqu’à la région, TLS, l’authentification, le routage et d’éventuelles files d’attente. Ces surcoûts expliquent une latence souvent supérieure, sans permettre de déduire un p95 cloud depuis nos mesures locales.")
    p('Une machine distante plus puissante peut réduire l’inférence ; la comparaison nécessite un client, une région, une charge et une taille de lot explicitement fixés.')
    story.append(PageBreak())

    # Page 7
    heading('6. Réponses aux questions 4 à 6')
    p('Question 4 - Le moteur AutoML change de version', 'LabelFR')
    p('Un nouvel entraînement peut explorer d’autres modèles ou réglages, produire des scores différents et modifier les dépendances. Une évolution du runtime peut aussi affecter un modèle déjà servi. Il faut conserver les versions du moteur et des bibliothèques, le jeu de données et son empreinte, la configuration gagnante, l’artefact et la signature. Une validation comparative et une possibilité de retour arrière précèdent la promotion.')
    p('Question 5 - Garantir la réversibilité', 'LabelFR')
    p('Dès le choix d’une plateforme, vérifier les formats d’export et le droit d’utiliser le modèle hors du fournisseur. Exporter, quand cela est possible, le modèle, le prétraitement, la signature et les dépendances ; tester le chargement et l’inférence hors plateforme sur un jeu de référence. Garder les données et un pipeline indépendant pour pouvoir réentraîner si l’export est impossible. Une API seule ne garantit pas la réversibilité.')
    p('Question 6 - Pourquoi cloudpickle plutôt que skops ?', 'LabelFR')
    p('L’estimateur choisi par FLAML peut appartenir à LightGBM, XGBoost ou scikit-learn. Dans ce TP, cloudpickle simplifie le packaging via le flavor sklearn, tandis que le Random Forest manuel est explicitement enregistré en skops avec le type sklearn.tree._tree.Tree autorisé. Le format et les dépendances sont visibles dans MLmodel. [S2]')
    p('Pickle et cloudpickle peuvent exécuter du code à la désérialisation : ne charger que des artefacts de confiance. L’usage est limité ici à un modèle entraîné localement et conservé dans notre registre. Skops permet de contrôler les types chargés ; une liste de confiance élargie sans examen annule cette protection. [S3]')
    p('Traçabilité et état du rendu', 'LabelFR')
    p('Le dépôt local comporte les scripts, les mesures brutes, la comparaison et les dépendances figées. data/, models/, .venv/, mlflow.db et mlartifacts/ sont exclus de Git. Le README donne les commandes de reproduction et d’arrêt. Les temps humains restent à renseigner. L’URL publique GitHub devra être ajoutée après publication ; aucun courriel n’a été envoyé.')
    p('Sources consultées', 'LabelFR')
    p('[S1] Google Cloud, tarification Vertex AI / page actuelle de la plateforme, rubriques Tabular data et Prediction and explanation (us-central1).<br/><link href="https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing">cloud.google.com/products/gemini-enterprise-agent-platform/pricing</link>', 'SmallFR')
    p('[S2] MLflow, API mlflow.sklearn, formats et skops_trusted_types.<br/><link href="https://mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html">mlflow.org/docs/latest/api_reference/python_api/mlflow.sklearn.html</link>', 'SmallFR')
    p('[S3] scikit-learn, Model persistence, sécurité et limites de portabilité.<br/><link href="https://scikit-learn.org/stable/model_persistence.html">scikit-learn.org/stable/model_persistence.html</link>', 'SmallFR')

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#c6d9e4'))
        canvas.line(2*cm, 1.45*cm, 19*cm, 1.45*cm)
        canvas.setFont('Arial', 8)
        canvas.setFillColor(colors.HexColor('#536779'))
        canvas.drawString(2*cm, 1.05*cm, 'TP05 | AutoML et déploiement | 5IASD G8')
        canvas.drawRightString(19*cm, 1.05*cm, str(doc.page))
        canvas.restoreState()
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=1.8*cm, bottomMargin=1.9*cm,
                            title='TP05 - Creer et deployer un modele AutoML',
                            author='Mohamed BENHEDDANE, Yassir DRISSI, Zineb BAQLOUL')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)


if __name__ == '__main__':
    main()
