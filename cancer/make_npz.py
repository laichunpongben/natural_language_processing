# -*- coding: utf-8 -*-

from gensim.models import word2vec
import pandas as pd
import numpy as np

class Cancer(object):
    def __init__(self):
        self.text_path = "text_no_punc"
        self.word2vec_path = "w2v200.h5"
        self.csv_path = 'training_variants'
        self.npz_path = "train.npz"
        self.dimension = 200

    def load(self):
        self.word2vec = self.load_word2vec()
        self.df = self.load_df()

    def make_word2vec(self):
        sentences = word2vec.Text8Corpus(self.text_path)
        model = word2vec.Word2Vec(sentences, size=self.dimension, min_count=1, window=4)
        model.save(self.word2vec_path)

    def load_word2vec(self):
        return word2vec.Word2Vec.load(self.word2vec_path)

    def load_df(self):
        return pd.read_csv(self.csv_path)

    def get_x_y(self):
        X = np.zeros((self.df.shape[0], self.dimension))
        Y = np.zeros((self.df.shape[0], ))
        for index, row in self.df.iterrows():
            gene, variation, class_ = row['Gene'], row['Variation'], row['Class']
            if ' ' in variation:
                variation = variation.split(' ')[0]
            try:
                w_gene = self.word2vec[gene]
            except KeyError:
                w_gene = np.zeros((self.dimension,))

            try:
                w_variation = self.word2vec[variation]
            except KeyError:
                w_variation = np.zeros((self.dimension,))

            x = np.add(w_gene, w_variation)
            y = int(class_)
            X[index], Y[index] = x, y
        return X, Y

    def make_npz(self):
        X, Y = self.get_x_y()
        np.savez_compressed(self.npz_path, x=X, y=Y)
        d = np.load(self.npz_path)
        print(d['x'].shape)
        print(d['y'].shape)

if __name__ == "__main__":
    cancer = Cancer()
    cancer.make_word2vec()
    cancer.load()
    cancer.make_npz()
