import csv
import pandas as pd

def cut_df():
    train_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_train.csv'
    train_truncated_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_train_truncated.csv'
    df = pd.read_csv(train_path)
    print(df.shape)
    df = df[df['before'] != df['after']]
    print(df.shape)

    df.to_csv(train_truncated_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

if __name__ == '__main__':
    import time

    start = time.time()
    cut_df()

    end = time.time()
    lapsed_sec = end - start
    print(lapsed_sec)
