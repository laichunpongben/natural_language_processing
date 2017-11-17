import pickle
import csv
import operator
import pandas as pd
from num2words import num2words
from text_normalization import TextNormalization

test_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_test_2.csv'
dictionary_path = '/home/ben/github/natural_language_processing/text_normalization_en/res.pickle'
submission_path = '/home/ben/github/natural_language_processing/text_normalization_en/9.csv'

def get_dict():
    with open(dictionary_path, 'rb') as pkl:
        return pickle.load(pkl)

def normalize_replace(text, res):
    if text in res:
        return sorted(res[text].items(), key=operator.itemgetter(1), reverse=True)[0][0]
    else:
        return text

def solve():
    tn = TextNormalization()
    res = get_dict()

    df_test = pd.read_csv(test_path)
    df_test['previous'] = df_test['before'].shift(1)
    df_test['following'] = df_test['before'].shift(-1)
    df_test['previous'].iloc[0] = ''
    df_test['following'].iloc[-1] = ''
    print(df_test['previous'].head(10))
    print(df_test['following'].tail(10))

    df_test['after0'] = df_test.apply(lambda row: tn.normalize2(row['before'],
                                                                previous=row['previous'],
                                                                following=row['following']),
                                      axis=1)
    # df_test['after0'] = df_test.apply(lambda row: tn.normalize2(row['before']), axis=1)
    print('First normalization done')

    print(df_test.head(10))
    print(df_test.tail(10))

    df_test['after'] = df_test.apply(lambda row: normalize_replace(row['after0'], res) if row['after0'] == row['before'] else row['after0'], axis=1)
    df_test['id'] = df_test['sentence_id'].map(str) + '_' + df_test['token_id'].map(str)

    df_submission = df_test[['id', 'after']]
    df_submission.to_csv(submission_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

if __name__ == '__main__':
    import time

    start = time.time()
    solve()
    end = time.time()
    lapsed = end - start
    print(lapsed)
