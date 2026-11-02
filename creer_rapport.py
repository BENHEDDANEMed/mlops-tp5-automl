"""Compiler le rapport TP05 avec la meme mise en page LaTeX que le TP04."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    engine = shutil.which('pdflatex')
    if engine is None and os.name == 'nt':
        candidate = Path.home() / 'AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
        if candidate.exists():
            engine = str(candidate)
    if engine is None:
        raise SystemExit('pdfLaTeX introuvable. Installer MiKTeX/TeX Live ou importer rapport-latex dans Overleaf.')
    source = ROOT / 'rapport-latex'
    output = ROOT / '.runtime/latex'
    output.mkdir(parents=True, exist_ok=True)
    args = [engine]
    if 'miktex' in engine.lower():
        args.append('--disable-installer')
    args += ['-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
             '-output-directory=' + str(output), 'rapport.tex']
    for iteration in (1, 2):
        result = subprocess.run(args, cwd=source, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / f'compilation-{iteration}.txt').write_bytes(result.stdout)
        if result.returncode:
            sys.stderr.write(result.stdout.decode('utf-8', errors='replace')[-6000:])
            raise SystemExit(result.returncode)
    destination = ROOT / 'BENHEDDANE_Mohamed_5IASD_G8.pdf'
    shutil.copy2(output / 'rapport.pdf', destination)
    print(f'Rapport LaTeX compile : {destination}')


if __name__ == '__main__':
    main()
