import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import Adam

train = pd.read_csv('input/stage1_variants.csv')
test = pd.read_csv('input/stage2_test_variants.csv')
trainx = pd.read_csv('input/stage1_text', sep="\|\|", engine='python', header=None, skiprows=1, names=["ID","Text"])
testx = pd.read_csv('input/stage2_test_text', sep="\|\|", engine='python', header=None, skiprows=1, names=["ID","Text"])

train = pd.merge(train, trainx, how='left', on='ID').fillna('')
y = train['Class'].values
train = train.drop(['Class'], axis=1)

test = pd.merge(test, testx, how='left', on='ID').fillna('')
pid = test['ID'].values

df_all = pd.concat((train, test), axis=0, ignore_index=True)
df_all['Gene_Share'] = df_all.apply(lambda r: sum([1 for w in r['Gene'].split(' ') if w in r['Text'].split(' ')]), axis=1)
df_all['Variation_Share'] = df_all.apply(lambda r: sum([1 for w in r['Variation'].split(' ') if w in r['Text'].split(' ')]), axis=1)

z = np.load('stage2_pipeline.npz')
train, test = z['train'], z['test']

y = y - 1 #fix for zero bound array

print(z['train'].shape)
# print(z['train'])
print(z['test'].shape)
# print(z['test'])

pca = PCA(n_components=50, svd_solver='randomized', whiten=True)
train = pca.fit_transform(train)
print('x', train.shape)
print('y', y.shape)

x_train, x_test, y_train, y_test = train_test_split(train, y, test_size=0.05, random_state=42)
print(x_train)
print(y_train)

input_dim = x_train.shape[1]
num_classes = 9
y_train = keras.utils.to_categorical(y_train, num_classes=num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes=num_classes)

model = Sequential()
model.add(Dense(128, activation='relu', input_dim=input_dim))
model.add(Dropout(0.25))
model.add(Dense(64, activation='relu', input_dim=input_dim))
model.add(Dropout(0.25))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(9, activation='softmax'))

model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer=Adam(),
              metrics=['accuracy'])

model.fit(x_train, y_train,
          epochs=300,
          batch_size=128,
          validation_data=(x_test, y_test))
score = model.evaluate(x_test, y_test, batch_size=128)

model.save('dense.h5')
