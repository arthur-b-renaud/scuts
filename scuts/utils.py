import os.path as op
import hashlib
import os
import tempfile
import pandas as pd


def visuallize_df(df):
    """For development purpose, displays df under Libreoffice a pandas Dataframe
    :param df: a Pandas dataframe
    :return: None
    """
    tmp_fpath = op.join(tempfile.mkdtemp(), "tmp.xlsx")
    df.to_excel(tmp_fpath)
    cmd = 'soffice "{}"'.format(tmp_fpath)
    print(cmd)
    os.system(cmd)


def hash_file(file_path):
    """Utility for file hashing

    :param file_path: a valid path
    :return:
    """
    assert op.exists(file_path)
    h = hashlib.sha256()
    with open(file_path, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)
    return h.hexdigest()
