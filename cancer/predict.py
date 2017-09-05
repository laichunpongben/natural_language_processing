import numpy as np
import pandas as pd
from keras.models import load_model
from gensim.models import word2vec

test_csv_path = 'test_variants.csv'
df_x_test = pd.read_csv(test_csv_path)
N = df_x_test.shape[0]
print(df_x_test)

w2v = word2vec.Word2Vec.load('w2v200.h5')

dimension = 200
x_test = np.zeros((N, dimension))
for index, row in df_x_test.iterrows():
    gene, variation = row['Gene'], row['Variation']
    try:
        w_gene = w2v[gene]
    except KeyError:
        w_gene = np.zeros((dimension, ))

    try:
        w_variation = w2v[variation]
    except KeyError:
        w_variation = np.zeros((dimension, ))

    x = np.add(w_gene, w_variation)
    x_test[index] = x

print(x_test.shape[0], 'test samples')

model = load_model('dense.h5')
y_test = model.predict(x_test, verbose=0)
print(y_test)
print(y_test.shape)

df_y_test = pd.DataFrame(columns=['class1','class2','class3','class4','class5','class6','class7','class8','class9'],
                         data=y_test)
print(df_y_test)
y_test_csv_path = 'submission.csv'
df_y_test.to_csv(y_test_csv_path, index=True, index_label='ID')
