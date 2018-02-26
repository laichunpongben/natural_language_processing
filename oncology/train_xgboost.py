from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss
import pandas as pd
import numpy as np
import xgboost as xgb

npz_path = 'stage2_pipeline1.npz'

train = pd.read_csv('input/stage1_variants_lower.csv')
test = pd.read_csv('input/stage2_test_variants_lower.csv')
trainx = pd.read_csv('input/stage1_text_gene', sep="\|\|", engine='python', header=None, skiprows=1, names=["ID","Text"])
testx = pd.read_csv('input/stage2_text_gene', sep="\|\|", engine='python', header=None, skiprows=1, names=["ID","Text"])

train = pd.merge(train, trainx, how='left', on='ID').fillna('')
y = train['Class'].values
train = train.drop(['Class'], axis=1)

test = pd.merge(test, testx, how='left', on='ID').fillna('')
pid = test['ID'].values

print(train)
print(test)
print(trainx)
print(testx)

df_all = pd.concat((train, test), axis=0, ignore_index=True)
df_all['Gene_Share'] = df_all.apply(lambda r: sum([1 for w in r['Gene'].split(' ') if w in r['Text'].split(' ')]), axis=1)
df_all['Variation_Share'] = df_all.apply(lambda r: sum([1 for w in r['Variation'].split(' ') if w in r['Text'].split(' ')]), axis=1)

for i in range(56):  # why 56?
   df_all['Gene_'+str(i)] = df_all['Gene'].map(lambda x: str(x[i]) if len(x)>i else '')
   df_all['Variation'+str(i)] = df_all['Variation'].map(lambda x: str(x[i]) if len(x)>i else '')

gen_var_lst = sorted(list(train.Gene.unique()) + list(train.Variation.unique()))
print(len(gen_var_lst))
gen_var_lst = [x for x in gen_var_lst if len(x.split(' '))==1]
print(len(gen_var_lst))
print(gen_var_lst)

i_ = 0

for gen_var_lst_itm in gen_var_lst:
   if i_ % 100 == 0: print(i_)
   df_all['GV_'+str(gen_var_lst_itm)] = df_all['Text'].map(lambda x: str(x).count(str(gen_var_lst_itm)))
   i_ += 1

for c in df_all.columns:
    if df_all[c].dtype == 'object':
        if c in ['Gene','Variation']:
            lbl = LabelEncoder()
            df_all[c+'_lbl_enc'] = lbl.fit_transform(df_all[c].values)
            df_all[c+'_len'] = df_all[c].map(lambda x: len(str(x)))
            df_all[c+'_words'] = df_all[c].map(lambda x: len(str(x).split(' ')))
        elif c != 'Text':
            lbl = LabelEncoder()
            df_all[c] = lbl.fit_transform(df_all[c].values)
        if c=='Text':
            df_all[c+'_len'] = df_all[c].map(lambda x: len(str(x)))
            df_all[c+'_words'] = df_all[c].map(lambda x: len(str(x).split(' ')))

train = df_all.iloc[:len(train)]
test = df_all.iloc[len(train):]
print(train.shape)
print(test.shape)

class cust_regression_vals(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self
    def transform(self, x):
        x = x.drop(['Gene', 'Variation','ID','Text'],axis=1).values
        return x

class cust_txt_col(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key
    def fit(self, x, y=None):
        return self
    def transform(self, x):
        return x[self.key].apply(str)

print('Pipeline...')

fp = Pipeline([
    ('union', FeatureUnion(
        transformer_list = [
            ('standard', cust_regression_vals()),
            ('pi1', Pipeline([
                ('Gene', cust_txt_col('Gene')),
                ('count_Gene', CountVectorizer(analyzer=u'char', ngram_range=(1, 8))),
                ('tsvd1', TruncatedSVD(n_components=20, n_iter=25, random_state=12))
            ])),
            ('pi2', Pipeline([
                ('Variation', cust_txt_col('Variation')),
                ('count_Variation', CountVectorizer(analyzer=u'char', ngram_range=(1, 8))),
                ('tsvd2', TruncatedSVD(n_components=20, n_iter=25, random_state=12))
            ])),
            ('pi3', Pipeline([
                ('Text', cust_txt_col('Text')),
                ('tfidf_Text', TfidfVectorizer(ngram_range=(1, 2))),
                ('tsvd3', TruncatedSVD(n_components=50, n_iter=25, random_state=12))
            ]))
        ])
    )])

train = fp.fit_transform(train)
print(train.shape)
test = fp.transform(test)
print(test.shape)

np.savez_compressed(npz_path, train=train, test=test)

z = np.load(npz_path)
train, test = z['train'], z['test']

# pca = PCA(n_components=50, svd_solver='randomized', whiten=True)
# train = pca.fit_transform(train)
# test = pca.fit_transform(test)
# print(train.shape)
# print(test.shape)

y = y - 1 #fix for zero bound array

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
    x1, x2, y1, y2 = train_test_split(train, y, test_size=0.18, random_state=i)
    watchlist = [(xgb.DMatrix(x1, y1), 'train'), (xgb.DMatrix(x2, y2), 'valid')]
    model = xgb.train(params, xgb.DMatrix(x1, y1), 1000,  watchlist, verbose_eval=50, early_stopping_rounds=100)
    score1 = log_loss(y2, model.predict(xgb.DMatrix(x2), ntree_limit=model.best_ntree_limit), labels = list(range(9)))
    print(score1)
    if denom != 0:
        pred = model.predict(xgb.DMatrix(test), ntree_limit=model.best_ntree_limit+80)
        preds += pred
    else:
        pred = model.predict(xgb.DMatrix(test), ntree_limit=model.best_ntree_limit+80)
        preds = pred.copy()
    denom += 1
    submission = pd.DataFrame(pred, columns=['class'+str(c+1) for c in range(9)])
    submission['ID'] = pid
    submission = submission.reindex(columns=['ID']+submission.columns.tolist()[:-1])
    submission.to_csv('output/submission_xgb_fold_'  + str(i) + '.csv', index=False)
preds /= denom
submission = pd.DataFrame(preds, columns=['class'+str(c+1) for c in range(9)])
submission['ID'] = pid
submission = submission.reindex(columns=['ID']+submission.columns.tolist()[:-1])
submission.to_csv('output/submission_xgb.csv', index=False)
