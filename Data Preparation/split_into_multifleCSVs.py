import pandas as pd

df = pd.read_excel('cleaned_data.xlsx', sheet_name=None)
for key in df.keys():
  df[key].to_csv('%s.csv' %key,index = False)

# check
'''
df = pd.read_csv("1.csv")
df.head()

'''

