from os import listdir, chdir
from os.path import isfile, join, abspath

from numba import jit
from numpy import log, cumsum, log2, nonzero, sum, histogram2d
from pandas import DataFrame
from peewee import Field
from sklearn.metrics import mutual_info_score, log_loss
from statsmodels.api import OLS
from pyfinance.ols import PandasRollingOLS
from statsmodels.tsa.vector_ar.vecm import coint_johansen


STORAGE_PATH = abspath(chdir('G:\\storage'))

def peewee_to_df(table):
    fields = [f for f in dir(table) if isinstance(getattr(table, f), Field)]
    data = list(table.select(*[getattr(table, fld) for fld in fields]).tuples())
    df = DataFrame.from_records(data, columns=table._meta.fields)

    if 'id' in fields:
        df.set_index('id', inplace=True)
    return df

def periodize_returns(r, p=252):
    return ((1 + r) ^ p - 1)

def filenames(folder):
    try:
        path = join(STORAGE_PATH, folder)
        fs = [f for f in listdir(path) if isfile(join(path, f))]
    except:
        path = folder
        fs = [f for f in listdir(path) if isfile(join(path, f))]
    return fs

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

def mutual_info(x, y, bins):
    c_xy = histogram2d(x, y, bins)[0]
    return mutual_info_score(None, None, contingency=c_xy)

def logloss(prtedicted, y, name):
    val = log_loss(y, predicted)
    print('Log Loss for {}: {:.6f}.'.format(name, val))
    return val

def diff(data, symbols):
    for s in symbols:
        data['{}_Diff'.format(s)] = data['{}_Close'.format(s)].diff()
    return data

def zscore(data, per):
    return (data - data.rolling(window=per, min_periods=per).mean()) / data.rolling(window=per, min_periods=per).std()

def minmaxscaler(data, per):
    return (data - data.rolling(window=per, min_periods=per).min()) / (data.rolling(window=per, min_periods=per).max() - data.rolling(window=per, min_periods=per).min())

def slope(data0, data1):
    return OLS(data1, data0).fit().params[0]

def roll_slope(data0, data1, per):
    return PandasRollingOLS(y=data1, x=data0, window=per).beta
