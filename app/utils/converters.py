from os.path import join
from os import remove, listdir

from clint.textui import colored

from .file_utils import filenames
from .vars import STORAGE_PATH, META_PATHS
from .methods import read_csv_dask, write_parq, parq_to_csv
from app.data import get_mt, get_pickle


def easify_names(folder='dukas'):
    fs = filenames(folder)
    for f in fs:
        try:
            splt = f.split('-')
            if len(splt) > 0:
                name = splt[0]
                oldPath = join(STORAGE_PATH, folder, f)
                path = join(STORAGE_PATH, folder, '{}.csv'.format(name))
                rename(oldPath, path)
        except Exception as err:
            print(err)

def convert_to_parq(folder='dukas'):
    fs = filenames(folder)
    for f in fs:
        name = f.split('.')[0]
        data = read_csv_dask(folder, name)
        write_parq(data, folder, '{}.parq'.format(name))
        remove(join(STORAGE_PATH, folder, f))
        print(colored.green(name))

def convert_mt_one(sym):
    periods = [5, 15, 30, 60, 240, 1440, 10080, 43200]
    for p in periods:
        try:
            f = join(META_PATHS[0], 'DATA_MODEL_Ava Trade EU Ltd._{}_{}.csv'.format(sym, p))
            data = get_mt(f, which=0)
            data.rename(columns={'OPEN': 'Open', 'HIGH': 'High', 'LOW': 'Low', 'CLOSE': 'Close', 'VOLUME': 'Volume'}, inplace=True)
            dest_path = join(STORAGE_PATH, 'mt', '0', '{}_{}.p'.format(sym, p))
            data.to_pickle(dest_path)
            print(colored.green('Converted for {} {}'.format(sym, p)))
        except Exception as err:
            print(colored.red(err))

def convert_mt_pickle():
    ''' Converts MT4 exported CSV to local format. '''
    i = 0
    for m in META_PATHS:
        fs = filenames(m, mt=True)
        for f in fs:
            try:
                name = f.split('_')[3]
                per = f.split('_')[4].split('.')[0]
                dest_path = join(STORAGE_PATH, 'mt', '{}'.format(i), '{}_{}.p'.format(name, per))
                data = get_mt(f, which=i)
                if len(data) > 500:
                    data.rename(columns={'OPEN': 'Open', 'HIGH': 'High', 'LOW': 'Low', 'CLOSE': 'Close', 'VOLUME': 'Volume'}, inplace=True)
                    data.to_pickle(dest_path)
                    print(colored.green('Converted for {} {}'.format(name, per)))
            except Exception as err:
                print(colored.red(err))
        i += 1

def parq_to_csv_all(folder='dukas'):
    fs = listdir(join(STORAGE_PATH, folder))
    for f in fs:
        if '.parq' in f:
            name = f.split('.')[0]
            parq_to_csv(folder=folder, name=name)
            print(colored.green('Converted {}'.format(name)))

def pickle_to_csv_all(folder='tiingo'):
    fs = filenames(folder)
    for f in fs:
        if '.p' in f:
            try:
                name = f.split('.')[0]
                df = get_pickle(folder, name)
                df.to_csv(join(STORAGE_PATH, folder, '{}.csv'.format(name)))
                print(colored.green('Converted {}'.format(name)))
            except Exception as err:
                print(colored.red(err))
