import operator
import pickle
import pandas as pd

count_path = '/home/ben/github/natural_language_processing/text_normalization_en/25_count.pickle'
dictionary_path = '/home/ben/github/natural_language_processing/text_normalization_en/res.pickle'
out_path = '/home/ben/github/natural_language_processing/text_normalization_en/count_analysis.csv'

def make():
    with open(count_path, 'rb') as pkl:
        d_count = pickle.load(pkl)

    with open(dictionary_path, 'rb') as pkl:
        res = pickle.load(pkl)

    with open(out_path, 'w') as f:
        f.write('word\tcount\tnum_choice\tchoice0\tchoice1\tchoice2\tchoice3\n')
        for k, v in sorted(d_count.items(), key=operator.itemgetter(1), reverse=True):
            num_choice = len(res[k].items())
            choices = sorted(res[k].items(), key=operator.itemgetter(1), reverse=True)
            choice0, choice1, choice2, choice3 = '__NULL__', '__NULL__', '__NULL__', '__NULL__'
            try:
                choice0 = choices[0][0]
                choice1 = choices[1][0]
                choice2 = choices[2][0]
                choice3 = choices[3][0]
            except IndexError:
                pass

            k = k.replace('"', '__DOUBLE_QUOTE__')
            choice0 = choice0.replace('"', '__DOUBLE_QUOTE__')
            choice1 = choice1.replace('"', '__DOUBLE_QUOTE__')
            choice2 = choice2.replace('"', '__DOUBLE_QUOTE__')
            choice3 = choice3.replace('"', '__DOUBLE_QUOTE__')

            line = '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(k, v, num_choice, choice0, choice1, choice2, choice3)
            f.write(line)

def view():
    df = pd.read_csv(out_path, delimiter='\t')
    df = df[df.num_choice > 1]
    print(df)

if __name__ == '__main__':
    make()
    view()
