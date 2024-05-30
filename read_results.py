import pandas as pd

imprese = pd.read_excel('Imprese.xlsx')
imprese2 = pd.read_csv('scraper/output.csv')
# df = pd.read_csv('output.csv')
df2 = pd.read_csv('output2.csv', low_memory=False)

# df = df[(df['status'] == 'Status.SUCCESS') & (df['has_keyword'])] \
#     .drop_duplicates(subset='base_url', keep='first')
df2 = df2[(df2['status'] == 'Status.SUCCESS') & (df2['has_keyword'])]\
    .drop_duplicates(subset='base_url', keep='first')

# imprese = pd.merge(imprese, df, left_on='Website', right_on='base_url', how='left')
# imprese.to_csv('final.csv', index=False)

imprese2 = pd.merge(imprese2, df2, left_on='url', right_on='base_url', how='left')
imprese2.to_csv('final2.csv', index=False)
