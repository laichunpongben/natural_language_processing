# -*- coding: utf-8 -*-

from gensim.models import doc2vec
import pandas as pd
import numpy as np


class TextModel(object):
    def __init__(self):
        self.text_path = "cantonesehk_q"
        self.text_model_path = "chatbot_d2v300.h5"
        # self.train_csv_path = 'input/stage1_variants.csv'
        # self.test_csv_path = 'input/stage2_test_variants.csv'
        self.npz_path = "chatbot_d2v300.npz"
        self.dimension = 50

    def load(self):
        self.text_model = self.load_model()
        with open(self.text_path, 'r') as f:
            lines = f.readlines()
        self.corpus = [' '.join(list(line)[:-1]) for line in lines]
        # print(self.corpus)
        print(len(self.corpus))
        # self.train_df = self.load_train_df()
        # self.test_df = self.load_test_df()

    def make_model(self):
        documents = doc2vec.TaggedLineDocument(self.text_path)
        model = doc2vec.Doc2Vec(documents, size=self.dimension, dm=0, min_count=1, iter=10, window=2)
        model.save(self.text_model_path)

    def load_model(self):
        return doc2vec.Doc2Vec.load(self.text_model_path)

    def load_train_df(self):
        return pd.read_csv(self.train_csv_path)

    def load_test_df(self):
        return pd.read_csv(self.test_csv_path)

    def get_x_y(self):
        train_size = self.train_df.shape[0]
        print(train_size)
        X_train = np.zeros((train_size, self.dimension))
        Y_train = np.zeros((train_size, ))
        X_test = np.zeros((self.test_df.shape[0], self.dimension))

        for index, row in self.train_df.iterrows():
            class_ = row['Class']
            x = self.text_model.docvecs[index]
            y = int(class_)
            X_train[index], Y_train[index] = x, y

        for index, row in self.test_df.iterrows():
            x = self.text_model.docvecs[index + train_size]
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
    # text_model.make_model()
    text_model.load()
    # text_model.make_npz()

    # print(text_model.text_model)
    sentence = "你 識 唔 識 捉 棋 呀 ？"
    tokens = sentence.split()
    new_vector = text_model.text_model.infer_vector(tokens)
    # print(new_vector)
    # similarities = text_model.text_model.docvecs.most_similar(2216)
    similarities = text_model.text_model.docvecs.most_similar([new_vector])
    print(similarities)
    for i in range(len(similarities)):
        match = similarities[i][0]
        print(text_model.corpus[match])
