def get_record_data(subids, dataframe, variable_match=None, common_columns = ['subid', 'group', 'sex'], to_int=False):
  record = dataframe[dataframe['subid'].isin(subids)]
  print(record)
  if variable_match:
    record = record[common_columns + [column for column in dataframe.columns.tolist() if variable_match in column]]
  print(record)
  return record