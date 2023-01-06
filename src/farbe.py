import os
import re
import pandas as pd
import numpy as np
from pathlib import Path


def repl(match):
    return match.group(2) + '.' + match.group(3)


def do_corrections(filename, full_path, out_path):
    raw_data = pd.read_csv(full_path, encoding="ISO-8859-1", engine='python', delimiter="\t")

    data_korr = raw_data[
        ["Dateiname", "Glanzkomponente", "L*(D65)", "a*(D65)", "b*(D65)", "Munsell D65 Hue", "Munsell D65 Value",
         "Munsell D65 Chroma"]].reset_index(drop=True)

    pat = re.compile("(.*#)(\\d*)(\\d{2})", flags=re.IGNORECASE)
    data_korr.insert(1, 'Tiefe', data_korr['Dateiname'].str.replace(pat, repl, regex=True).astype(float))

    out_dir = os.path.join(out_path, filename + '_korr.xlsx')
    with pd.ExcelWriter(out_dir) as writer:
        data_korr.to_excel(writer, sheet_name='Daten_korr')
        raw_data.to_excel(writer, sheet_name='Rohdaten')


def process_directory(console=False):
    rel_path = Path(__file__).parent.parent
    files = next(os.walk(os.path.join(rel_path, 'raw')), (None, None, []))[2]
    out_path = os.path.join(rel_path, 'Farbe_korrigiert')
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for file in files:
        file_match = re.match('^(.*_farbe)(\\.txt)$', file, re.IGNORECASE)
        if not file_match:
            if console: print('.. skipping file ' + file + ' (does not match naming criteria)')
            continue

        if console: print('.. processing file ' + file)
        filename = file_match.group(1)
        full_path = os.path.join(rel_path, 'raw', file)

        do_corrections(filename, full_path, out_path)
        if console: print('.... created new file ' + filename + '_korr')


if __name__ == "__main__":
    print('starting script farbe.py')
    process_directory(console=True)
    print('finished script farbe.py')
