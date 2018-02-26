# -*- coding: utf-8 -*-

from gensim.models import word2vec
from gensim.models.keyedvectors import KeyedVectors
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
try:
    import pickle
except ImportError:
    import cPickle as pickle

class TextModel(object):
    def __init__(self):
        self.text_path = "input/all_text"
        self.text_model_path = "w2v300_7.h5"
        self.train_csv_path = 'input/all_training_variants.csv'
        self.test_csv_path = 'input/stage2_test_variants.csv'
        self.npz_path = "w2v300_7.npz"
        self.feature_path = 'features.pkl'
        self.dimension = 300

    def load(self):
        self.text_model = self.load_word2vec()
        self.train_df = self.load_train_df()
        self.test_df = self.load_test_df()
        self.feature_names = self.load_feature_names()

    def make_word2vec(self):
        sentences = word2vec.Text8Corpus(self.text_path)
        model = word2vec.Word2Vec(sentences, size=self.dimension, min_count=3, window=5)
        model.save(self.text_model_path)
        # tfidf = TfidfVectorizer()
        # with open(self.text_path, 'r') as f:
        #     X = tfidf.fit_transform(f)
        #     # X.toarray()
        # # print(X)
        # print(X.shape)
        # np.savez_compressed(self.text_model_path, model=X)
        #
        # feature_names = tfidf.get_feature_names()
        # print(feature_names)
        # with open(self.feature_path, 'wb') as f:
        #     pickle.dump(feature_names, f)

    def load_word2vec(self):
        # return KeyedVectors.load_word2vec_format(self.text_model_path, binary=True)
        # return word2vec.Word2Vec.load_word2vec_format(self.text_model_path, binary=True)
        return word2vec.Word2Vec.load(self.text_model_path)
        # npz = np.load(self.text_model_path)
        # return npz['model']

    def load_train_df(self):
        return pd.read_csv(self.train_csv_path)

    def load_test_df(self):
        return pd.read_csv(self.test_csv_path)

    def load_feature_names(self):
        with open(self.feature_path, 'rb') as f:
            return pickle.load(f)

    def get_x_y(self):
        X_train = np.zeros((self.train_df.shape[0], self.dimension))
        Y_train = np.zeros((self.train_df.shape[0], ))
        X_test = np.zeros((self.test_df.shape[0], self.dimension))

        for index, row in self.train_df.iterrows():
            gene, variation, class_ = row['Gene'], row['Variation'], row['Class']
            if ' ' in variation:
                variation = variation.split(' ')[0]
            try:
                w_gene = self.text_model[gene.lower()]
            except KeyError:
                w_gene = np.zeros((self.dimension,))

            try:
                w_variation = self.text_model[variation.lower()]
            except KeyError:
                w_variation = np.zeros((self.dimension,))

            x = np.add(w_gene, w_variation * 2)
            y = int(class_)
            X_train[index], Y_train[index] = x, y

        for index, row in self.test_df.iterrows():
            gene, variation = row['Gene'], row['Variation']
            if ' ' in variation:
                variation = variation.split(' ')[0]
            try:
                w_gene = self.text_model[gene.lower()]
            except KeyError:
                w_gene = np.zeros((self.dimension,))

            try:
                w_variation = self.text_model[variation.lower()]
            except KeyError:
                w_variation = np.zeros((self.dimension,))

            x = np.add(w_gene, w_variation * 2)
            X_test[index] = x

        return X_train, Y_train, X_test

    def make_npz(self):
        X_train, Y_train, X_test = self.get_x_y()
        np.savez_compressed(self.npz_path, xtrain=X_train, ytrain=Y_train, xtest=X_test)
        d = np.load(self.npz_path)
        print(d['xtrain'].shape)
        print(d['ytrain'].shape)
        print(d['xtest'].shape)

if __name__ == "__main__":
    text_model = TextModel()
    text_model.make_word2vec()
    text_model.load()
    text_model.make_npz()
