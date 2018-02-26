import csv
import pandas as pd

test_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_test.csv'
submission_path = '/home/ben/github/natural_language_processing/text_normalization_en/rule_baseline_12.csv'
solution_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_solution.csv'
diff_path = '/home/ben/github/natural_language_processing/text_normalization_en/en_diff_12.csv'

df_test = pd.read_csv(test_path)
df_submission = pd.read_csv(submission_path)
df_solution = pd.read_csv(solution_path)

for d in [df_test, df_submission, df_solution]:
    print(d.shape)
    print(d.columns)

df_test['id'] = df_test['sentence_id'].map(str) + '_' + df_test['token_id'].map(str)
df_test = df_test[['id', 'before']]
print(df_test.columns)

df = df_submission.merge(df_solution, on='id', how='left', suffixes=('_submission', '_solution'))
df = df_test.merge(df, on='id', how='left')

print(df.shape)
print(df.columns)

df_diff = df[df['after_submission'] != df['after_solution']]
print(df_diff.shape)
print(df_diff.columns)
print(df_diff.head(10))

df_diff.to_csv(diff_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
