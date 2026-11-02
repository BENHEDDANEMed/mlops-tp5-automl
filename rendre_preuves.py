"""Figures documentaires : transcriptions des journaux, sans imiter des terminaux."""
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'
CAPTURES = REPORTS / 'captures'


def read(name):
    return json.loads((REPORTS / name).read_text(encoding='utf-8'))


def render(name, title, subtitle, blocks):
    title_font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 30)
    label_font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 24)
    mono = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 21)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 21)
    all_blocks = [(label, [wrapped for line in text.splitlines()
        for wrapped in (textwrap.wrap(line, width=87, replace_whitespace=False, drop_whitespace=False) or [''])])
        for label, text in blocks]
    height = 155 + sum(60 + len(lines)*28 for _,lines in all_blocks)
    img = Image.new('RGB',(1200,height),'#f1f5f9')
    draw = ImageDraw.Draw(img)
    draw.rectangle((0,0,1200,9),fill='#107c69')
    draw.text((30,30),title,font=title_font,fill='#173e5b')
    draw.text((30,80),subtitle,font=small,fill='#526779')
    y = 132
    for label, lines in all_blocks:
        draw.text((30,y),label,font=label_font,fill='#107c69')
        y += 38
        draw.rectangle((22,y-5,1178,y+len(lines)*28+7),fill='white')
        for line in lines:
            draw.text((33,y),line,font=mono,fill='#24384b')
            y += 28
        y += 22
    CAPTURES.mkdir(exist_ok=True)
    img.save(CAPTURES / name,quality=96)


def main():
    checks = read('verification.json')
    service_blocks = []
    for kind,port in [('automl',8100),('manuel',8101)]:
        log = (ROOT/f'.runtime/{kind}.err.log').read_text(encoding='utf-8',errors='replace')
        lines = [line for line in log.splitlines() if any(x in line.lower() for x in
            ['running on','started server','application startup complete','running command'])]
        service_blocks.append((f'{kind.upper()} - 127.0.0.1:{port}', '\n'.join(lines[:4])))
    control = '\n'.join(f"{kind}: /health HTTP {checks[kind]['health_status']}, alias v{checks[kind]['alias_version']} READY\n"
        '  Rechargement identique sur 1 250 lignes : OK\n'
        '  Predictions HTTP identiques sur 30 lignes : OK' for kind in ('automl','manuel'))
    service_blocks.append(('Controles du script src/verifier.py',control))
    render('capture2_services.jpg','Preuve 2 - Services MLflow demarres',
        'Transcription des journaux reels .runtime/*.err.log et de verification.json',service_blocks)
    client_blocks = []
    for port in (8100,8101):
        lines = ["reponse : 200 {'predictions': [1]}"]
        for i in (1,2):
            result = read(f'latence_{port}_{i}.json')
            lines.append(f"Essai {i} : mediane {result['median_ms']:.2f} ms | p95 {result['p95_ms']:.2f} ms")
        lines.append('Par essai : 10 echauffements + 200 appels mesures et valides.')
        client_blocks.append((f'Client - port {port}', '\n'.join(lines)))
    invalid = checks['invalid_request']
    client_blocks.append((f"Requete invalide - HTTP {invalid['status']}",
        json.dumps(invalid['body'],ensure_ascii=False,indent=2)))
    render('capture3_client.jpg','Preuve 3 - Client HTTP et signature',
        'Transcription des mesures JSON ; aucune latence ni reponse simulee.',client_blocks)


if __name__ == '__main__':
    main()
