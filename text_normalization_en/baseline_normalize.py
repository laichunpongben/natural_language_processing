# -*- coding: utf-8 -*-
__author__ = 'ZFTurbo: https://kaggle.com/zfturbo'

import os
import operator
import gc
try:
    import pickle
except ImportError:
    import cPickle as pickle
from num2words import num2words
from text_normalization import TextNormalization


INPUT_PATH = "./train/"
DATA_INPUT_PATH = '/media/ben/Data/kaggle/en_with_types/'
SUBM_PATH = "./"

SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
OTH = str.maketrans("፬", "4")


def make_res():
    # Work with primary dataset
    file = "en_train.csv"
    train = open(INPUT_PATH + file, encoding='UTF8')
    line = train.readline()
    res = dict()
    total = 0
    not_same = 0
    while 1:
        line = train.readline().strip()
        if line == '':
            break
        total += 1
        pos = line.find('","')
        text = line[pos + 2:]
        if text[:3] == '","':
            continue
        text = text[1:-1]
        arr = text.split('","')
        if arr[0] != arr[1]:
            not_same += 1
        if arr[0] not in res:
            res[arr[0]] = dict()
            res[arr[0]][arr[1]] = 1
        else:
            if arr[1] in res[arr[0]]:
                res[arr[0]][arr[1]] += 1
            else:
                res[arr[0]][arr[1]] = 1
    train.close()
    print(file + ':\tTotal: {} Have diff value: {}'.format(total, not_same))

    # Work with additional dataset from https://www.kaggle.com/google-nlu/text-normalization
    files = sorted(os.listdir(DATA_INPUT_PATH))
    for file in files:
        train = open(DATA_INPUT_PATH + file, encoding='UTF8')
        while 1:
            line = train.readline().strip()
            if line == '':
                break
            total += 1
            pos = line.find('\t')
            text = line[pos + 1:]
            if text[:3] == '':
                continue
            arr = text.split('\t')
            if arr[0] == '<eos>':
                continue
            if arr[1] != '<self>':
                not_same += 1

            if arr[1] == '<self>' or arr[1] == 'sil':
                arr[1] = arr[0]

            if arr[1] == '<self>' or arr[1] == 'sil':
                arr[1] = arr[0]

            if arr[0] not in res:
                res[arr[0]] = dict()
                res[arr[0]][arr[1]] = 1
            else:
                if arr[1] in res[arr[0]]:
                    res[arr[0]][arr[1]] += 1
                else:
                    res[arr[0]][arr[1]] = 1
        train.close()
        print(file + ':\tTotal: {} Have diff value: {}'.format(total, not_same))
        gc.collect()

    with open('res.pickle', 'wb') as pkl:
        pickle.dump(res, pkl, protocol=pickle.HIGHEST_PROTOCOL)


def load_res():
    with open('res.pickle', 'rb') as pkl:
        res = pickle.load(pkl)
    return res

def solve():
    tn = TextNormalization()
    print('Train start...')

    res = load_res()
    print(len(res.keys()))

    sdict = {}
    sdict['km2'] = 'square kilometers'
    sdict['km'] = 'kilometers'
    sdict['kg'] = 'kilograms'
    sdict['lb'] = 'pounds'
    sdict['dr'] = 'doctor'
    sdict['m²'] = 'square meters'

    total = 0
    changes = 0
    out = open(SUBM_PATH + '6.csv', "w", encoding='UTF8')
    out.write('"id","after"\n')
    test = open(INPUT_PATH + "en_test_2.csv", encoding='UTF8')
    line = test.readline().strip()
    previous = ''
    while 1:
        line = test.readline().strip()
        if line == '':
            break

        pos = line.find(',')
        i1 = line[:pos]
        line = line[pos + 1:]

        pos = line.find(',')
        i2 = line[:pos]
        line = line[pos + 1:]

        line = line[1:-1]
        out.write('"' + i1 + '_' + i2 + '",')

        normalized_line = tn.normalize2(line, previous=previous)
        previous = line
        if normalized_line != line:
            # print(line, normalized_line)
            out.write('"' + normalized_line + '"')
            changes += 1
        else:
            if line in res:
                srtd = sorted(res[line].items(), key=operator.itemgetter(1), reverse=True)
                out.write('"' + srtd[0][0] + '"')
                changes += 1
            else:
                print(line)
                # out.write('"' + 'Z'*50 + '"')
                line.split(' ')
                if len(line) > 1:
                    val = line.split(',')
                    if len(val) == 2 and val[0].isdigit and val[1].isdigit:
                        line = ''.join(val)

                if line.isdigit():
                    srtd = line.translate(SUB)
                    srtd = srtd.translate(SUP)
                    srtd = srtd.translate(OTH)
                    out.write('"' + num2words(float(srtd)) + '"')
                    changes += 1
                elif len(line.split(' ')) > 1:
                    val = line.split(' ')
                    for i, v in enumerate(val):
                        if v.isdigit():
                            srtd = v.translate(SUB)
                            srtd = srtd.translate(SUP)
                            srtd = srtd.translate(OTH)
                            val[i] = num2words(float(srtd))
                        elif v in sdict:
                        # if v in sdict:
                            val[i] = sdict[v]

                    out.write('"' + ' '.join(val) + '"')
                    changes += 1
                else:
                    out.write('"' + line + '"')

        out.write('\n')
        total += 1

    print('Total: {} Changed: {}'.format(total, changes))
    test.close()
    out.close()


if __name__ == '__main__':
    solve()
    # make_res()
