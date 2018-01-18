from .constants import *
import pandas as pd

def ingest(path=None, save=False, verbose=True):
    if save and path is None:
        print('If save is True, you must specify an explicit path')
        return 
    else:
        text = []
        if verbose:
            nComments = 0
        for path in pathsData.items():
            if path[0] not in ['MERCADOLIBRE_POS', 'MERCADOLIBRE_NEG']:
                data = [e.split(dataDelimiter) for e in open(path[1], encoding='utf8').readlines()]
                text += [e[0] for e in data]
                target += [float(e[1].strip()) for e in data]
                del data
                if verbose:
                    print('%s : %d' % (path[0], len(text) - nComments))
                    nComments = len(text)

        text += list(set([e.strip() for e in open(pathsData['MERCADOLIBRE_POS'], encoding='utf8').readlines()]))[:MERCADO_RATIO]
        if verbose:
            print('%s : %d' % ('GOOD_TWEETS', len(text) - nComments))
            nComments = len(text)

        text += [e.strip() for e in open(pathsData['MERCADOLIBRE_NEG'], encoding='utf8').readlines()] \
        + list(set(['no ' + e.strip() for e in open(pathsData['MERCADOLIBRE_POS'], encoding='utf8').readlines() if \
        len(e.split())<=4 and len(e.split())>0 and e.split()[0].lower() not in negWords]))[:MERCADO_RATIO]
        if verbose:
            print('%s : %d' % ('BAD_TWEETS', len(text) - nComments))
            nComments = len(text)

        if verbose:
            print(' ')
            print('TOTAL : %d' % nComments)
        if save:
            with open(path, 'a', encoding='utf8'):
                for ix,e in enumerate(text):
                    f.write(' '.join([str(e), dataDelimiter, str(target(ix))]))
                    f.write('\n')
        return text, target