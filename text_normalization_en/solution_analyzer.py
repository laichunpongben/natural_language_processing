import re
import pandas as pd

test_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_test.csv'
solution_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_solution.csv'
df_test = pd.read_csv(test_path)
df_solution = pd.read_csv(solution_path)

candidate0 = re.compile(r'.*two thousand ten.*')
candidate1 = re.compile(r'.*twenty ten.*')

df_solution['candidate0'] = df_solution['after'].str.count(candidate0)
df_solution['candidate1'] = df_solution['after'].str.count(candidate1)
print(df_solution['candidate0'].sum())
print(df_solution['candidate1'].sum())
c0 = [x.split('_')[0] for x in df_solution[(df_solution.candidate0 > 0)]['id'].tolist()]
c1 = [x.split('_')[0] for x in df_solution[(df_solution.candidate1 > 0)]['id'].tolist()]

df_out0 = df_test[(df_test.sentence_id.isin(c0))].groupby('sentence_id')['before'].apply(lambda x: ' '.join(x))
df_out1 = df_test[(df_test.sentence_id.isin(c1))].groupby('sentence_id')['before'].apply(lambda x: ' '.join(x))
df_out0.to_csv('/home/ben/github/natural_language_processing/text_normalization_en/df_out0.csv')
df_out1.to_csv('/home/ben/github/natural_language_processing/text_normalization_en/df_out1.csv')
