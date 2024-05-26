import pandas as pd

df = pd.read_csv('output.csv')

df[(df['status'] == 'Status.SUCCESS') & (df['has_keyword'])][['base_url']].drop_duplicates().to_csv('result.csv',index=False)
