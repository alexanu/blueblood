from os import listdir
from os.path import isfile, join

from numba import jit
from numpy import log, cumsum, log2, nonzero, sum
from pandas import DataFrame
from peewee import Field


def peewee_to_df(table):
    fields = [f for f in dir(table) if isinstance(getattr(table, f), Field)]
    data = list(table.select(*[getattr(table, fld) for fld in fields]).tuples())
    df = DataFrame.from_records(data, columns=table._meta.fields)

    if 'id' in fields:
        df.set_index('id', inplace=True)
    return df

def periodize_returns(r, p=252):
    return ((1 + r) ^ p - 1)

def filenames(path):
    return [f for f in listdir(path) if isfile(join(path, f))]

def log_returns(x):
    return log(x)

def get_dividends_splits(close, adjusted):
    '''Outputs should be classified into: dividend, split or white noise.'''
    return adjusted - close

@jit
def vwap(data):
    return cumsum(data['Volume'] * (data['High'] + data['Low']) / 2) / cumsum(data['Volume'])

def shanon_entropy(c):
    norm = c / float(sum(c))
    norm = norm[nonzero(norm)]
    H = -sum(norm * log2(norm))  
    return H
