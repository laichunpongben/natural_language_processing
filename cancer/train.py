import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
from sklearn.model_selection import train_test_split

d = np.load("train.npz")
x, y = d['x'], d['y']
y = y - 1  # 1 to 9
input_dim = x.shape[1]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.05, random_state=42)

num_classes = 9
y_train = keras.utils.to_categorical(y_train, num_classes=num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes=num_classes)

model = Sequential()
model.add(Dense(256, activation='relu', input_dim=input_dim))
model.add(Dropout(0.25))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.25))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(9, activation='softmax'))

model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer=keras.optimizers.Adam(),
              metrics=['accuracy'])

model.fit(x_train, y_train,
          epochs=300,
          batch_size=128,
          validation_data=(x_test, y_test))
score = model.evaluate(x_test, y_test, batch_size=128)

model.save('dense.h5')
