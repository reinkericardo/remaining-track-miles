import tarfile
import pandas as pd


def extract_tar(file_path):
    """
    Extract tar file.
    :param file_path: file path of tar file.
    :return:
    """
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall()


def load_csv_gzip(file_path):
    """
    Load csv file as dataframe with pandas.
    :param file_path:  file path of csv file.
    :return:
    """
    return pd.read_csv(file_path, compression='gzip')
