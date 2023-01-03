import os
import re
import pandas as pd
import numpy as np
from pathlib import Path

def repl(match):
    return match.group(2) + '.' + match.group(3)


def do_corrections(filename, full_path, out_path):
    raw_data = pd.read_csv(full_path, encoding="UTF-16LE", engine='python', delimiter="\t")

    data_korr = raw_data
    data_korr.insert(1, 'SI*10^5', data_korr["Vol. Susc.  Meas. in SI"].mul(10000))

    data_disc = data_korr.loc[data_korr['Sample ID'].str.match(r'^ref.*', flags=re.IGNORECASE)]
    data_korr = data_korr.loc[data_korr['Sample ID'].str.match(r'^(?!ref).*', flags=re.IGNORECASE)]

    pat = re.compile("(.*_)(\\d*)(\\d{2})", flags=re.IGNORECASE)
    data_korr.insert(1, 'Tiefe', data_korr['Sample ID'].str.replace(pat, repl, regex=True).astype(float))

    out_dir = os.path.join(out_path, filename + '_korr.xlsx')
    with pd.ExcelWriter(out_dir) as writer:
        data_korr.to_excel(writer, sheet_name='Daten_korr', index=False)
        data_disc.to_excel(writer, sheet_name='Daten_disc', index=False)
        raw_data.to_excel(writer, sheet_name='Rohdaten')  # , index=False)


def process_directory(console=False):
    rel_path = Path(__file__).parent.parent
    files = next(os.walk(rel_path), (None, None, []))[2]
    out_path = os.path.join(rel_path, 'Magsusz_korrigiert')
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for file in files:
        file_match = re.match('^(.*_magsus.*)(\\.txt)$', file, re.IGNORECASE)
        if not file_match:
            if console: print('.. skipping file ' + file + ' (does not match naming criteria)')
            continue

        if console: print('.. processing file ' + file)
        filename = file_match.group(1)
        full_path = os.path.join(rel_path, file)

        do_corrections(filename, full_path, out_path)
        if console: print('.... created new file ' + filename + '_korr')


if __name__ == "__main__":
    print('starting script magsusz.py')
    pd.set_option('display.float_format', lambda x: '%.9f' % x)
    process_directory(console=True)
    pd.reset_option('display.float_format')
    print('finished script magsusz.py')
