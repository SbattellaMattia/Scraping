import pandas as pd

final = pd.read_csv('final3-2.csv')
imprese2 = pd.read_csv('scraper/output.csv')
df = pd.read_csv('output2-2.csv', low_memory=False)

df = df[(df['has_keyword']==False)].drop_duplicates(subset='base_url', keep='first')[['base_url','status', 'code']].rename(columns={'code':'CodiceRisposta'})

final = pd.merge(final, df, left_on='url', right_on='base_url', how='left')
final.to_csv('final3-3.csv', index=False)

# imprese2 = pd.merge(imprese2, df2, left_on='url', right_on='base_url', how='left')
# imprese2.to_csv('final2.csv', index=False)
