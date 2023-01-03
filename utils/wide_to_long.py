import pandas as pd

data = pd.read_excel('C:/Users/ndidier/Desktop/C3_BP.xlsx')
new_columns = {}
for col in data.columns:
  if col[-1] == 'B':
    new_columns[col] = col[:-1]
  else:
    new_columns[col] = col
data.rename(columns=new_columns, inplace=True)
data = pd.wide_to_long(data, stubnames=['PBPsys', 'PBPdia', 'PBPhr', 'PBPmap', 'HBPsys', 'HBPdia', 'HBPhr', 'HBPmap'], i='SubID', j='TimePoint')

data.reset_index(inplace=True)
data['unique_id'] = data.agg('{0[SubID]}_{0[TimePoint]}'.format, axis=1)

new_columns = {}
for column_name in data.columns:
    if column_name[0] == 'H':
        new_column_name = column_name[1:] + 'H'
        new_columns[column_name] = new_column_name
    if column_name[0] == 'P':
        new_column_name = column_name[1:] + 'P'
        new_columns[column_name] = new_column_name
data.rename(columns = new_columns, inplace=True)
data = pd.wide_to_long(data, stubnames=['BPsys', 'BPdia', 'BPhr', 'BPmap'], j='Dose', i='unique_id', suffix='(\d+|\w+)')
data.to_excel('C:/Users/ndidier/Desktop/bp_long.xlsx')