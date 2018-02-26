import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.metrics import log_loss
import xgboost as xgb

train = pd.read_csv('input/stage1_variants.csv')
test = pd.read_csv('input/stage2_test_variants.csv')
trainx = pd.read_csv('input/stage1_text', sep="\|\|", engine='python', header=None, skiprows=1, names=["ID","Text"])
testx = pd.read_csv('input/stage2_test_text', sep="\|\|", engine='python', header=None, skiprows=1, names=["ID","Text"])
#
train = pd.merge(train, trainx, how='left', on='ID').fillna('')
y = train['Class'].values
train = train.drop(['Class'], axis=1)
#
# test = pd.merge(test, testx, how='left', on='ID').fillna('')
pid = test['ID'].values
#
# df_all = pd.concat((train, test), axis=0, ignore_index=True)
# df_all['Gene_Share'] = df_all.apply(lambda r: sum([1 for w in r['Gene'].split(' ') if w in r['Text'].split(' ')]), axis=1)
# df_all['Variation_Share'] = df_all.apply(lambda r: sum([1 for w in r['Variation'].split(' ') if w in r['Text'].split(' ')]), axis=1)
#
# z = np.load('all_training_variants4.npz')
z = np.load('w2v300_7.npz')
x_train, y_train, x_test = z['xtrain'], z['ytrain'], z['xtest']

y_train = y_train - 1 #fix for zero bound array

print(x_train.shape)
print(y_train.shape)
print(x_test.shape)

denom = 0
fold = 5
for i in range(fold):
    params = {
        'eta': 0.03333,
        'max_depth': 4,
        'objective': 'multi:softprob',
        'eval_metric': 'mlogloss',
        'num_class': 9,
        'seed': i,
        'silent': True
    }
    x1, x2, y1, y2 = train_test_split(x_train, y_train, test_size=0.18, random_state=i)
    watchlist = [(xgb.DMatrix(x1, y1), 'train'), (xgb.DMatrix(x2, y2), 'valid')]
    model = xgb.train(params, xgb.DMatrix(x1, y1), 1000,  watchlist, verbose_eval=50, early_stopping_rounds=100)
    score1 = log_loss(y2, model.predict(xgb.DMatrix(x2), ntree_limit=model.best_ntree_limit), labels = list(range(9)))
    print(score1)
    if denom != 0:
        pred = model.predict(xgb.DMatrix(x_test), ntree_limit=model.best_ntree_limit+80)
        preds += pred
    else:
        pred = model.predict(xgb.DMatrix(x_test), ntree_limit=model.best_ntree_limit+80)
        preds = pred.copy()
    denom += 1
    submission = pd.DataFrame(pred, columns=['class'+str(c+1) for c in range(9)])
    submission['ID'] = pid
    submission = submission.reindex(columns=['ID']+submission.columns.tolist()[:-1])
    submission.to_csv('stage2_w2v_xgb_fold_'  + str(i) + '.csv', index=False)
preds /= denom
submission = pd.DataFrame(preds, columns=['class'+str(c+1) for c in range(9)])
submission['ID'] = pid
submission = submission.reindex(columns=['ID']+submission.columns.tolist()[:-1])
submission.to_csv('stage2_w2v_xgb.csv', index=False)
