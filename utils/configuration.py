import os
import re
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

def makeFolderIfNonexistent(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)',text) ]

def convert_all_numeric_string_columns_to_numeric(dataframe, print_details = False):
    not_converted = []
    for col in dataframe.columns.tolist():
        column_to_assess = dataframe[col]
        try:
            numeric_col = pd.to_numeric(column_to_assess, errors='raise')
            dataframe[col] = numeric_col
        except:
            not_converted.append(not_converted)
    if print_details:
        print('columns not converted to numeric:', not_converted)
    
    return dataframe

def clean_subid_column(df):
    invalid_ids = [999, 9999, '0TEST', 99999]
    df = df[(~df['subid'].isin(invalid_ids)) & (pd.to_numeric(df['subid'], errors='coerce').notnull()) | (df['subid'] == '')]
    df.reset_index(inplace=True, drop=True)
    return df

def clean_csdpnum_column(df):
    invalid_ids = [999, 9999, '0TEST', 99999]
    df = df[~df['csdpnum'].isin(invalid_ids)]
    df['csdpnum'] = df["csdpnum"].str.replace(r'csdp', '', regex=True, case=False)
    df.reset_index(inplace=True, drop=True)
    return df

def clean_meta_text(col):
    clean_text = []
    pattern_to_purge = r'<[^>]+>'
    for row in col.tolist():
        cleanr = re.compile(pattern_to_purge)
        clean_row = re.sub(cleanr, '', row)
        clean_text.append(clean_row)
    return clean_text

def clean_text_column(df, column_name):
  df[column_name] = df[column_name].astype("str") 
  df[column_name] = df[column_name].str.replace(',','')
  df[column_name] = df[column_name].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))
  return df

def assign_numeric_data_types(metadata, data, common_fields):
  for field_name in [field_name for field_name in data.columns.tolist() if ((field_name not in common_fields) and (field_name[-9:] != '_complete'))]:
    try:
      field_metadata_idx = metadata.index[metadata['field_name']==field_name].tolist()[0]
      redcap_field_type = metadata.loc[field_metadata_idx, 'field_type']
      if redcap_field_type == 'text':
        filtered_data = data[~data[field_name].isnull()][field_name]
        if (pd.to_numeric(data[field_name], errors='coerce').notnull().all()) and (len(filtered_data) > 10):
          metadata.loc[field_metadata_idx, 'field_type'] = 'numeric'
      elif redcap_field_type == 'dropdown':
        options = metadata.loc[field_metadata_idx, 'select_choices_or_calculations'].split(' | ')
        if all([option.split(', ')[1].isnumeric() for option in options]) and (len(options) > 5):
          metadata.loc[field_metadata_idx, 'field_type'] = 'numeric'
    except:
      print(f'{field_name} may not be in metadata')
  return metadata

def revise_checkbox_metadata(metadata):
  new_metadata = metadata.copy()
  added_rows = 0
  for i, checkbox_row in metadata[metadata['field_type']=='checkbox'].iterrows():
    checkbox_field_name = checkbox_row['field_name']
    checkbox_options = checkbox_row['select_choices_or_calculations'].split(' | ')
    new_checkbox_metadata = pd.DataFrame(columns = metadata.columns.tolist())
    for n, option in enumerate(checkbox_options):
      new_row = checkbox_row.copy()
      option_idx = option.split(',')[0]
      new_row['field_name'] = f'{checkbox_field_name}___{option_idx}'
      print(option)
      regex = re.compile('[^a-zA-Z]')
      option_cleaned = regex.sub('', option, count = 3)
      new_row['select_choices_or_calculations'] = option_cleaned
      new_checkbox_metadata = new_checkbox_metadata.append(new_row)
    idx = i + added_rows
    top_metadata = new_metadata.loc[:idx]
    top_metadata = top_metadata.append(new_checkbox_metadata)
    top_metadata.reset_index(inplace=True, drop=True)
    new_metadata = top_metadata.append(new_metadata.loc[idx:])
    old_field_metadata_idx = new_metadata.index[new_metadata['field_name']==checkbox_field_name].tolist()[0]
    new_metadata.drop(index=old_field_metadata_idx, inplace=True)
    new_metadata.reset_index(inplace=True, drop=True)
    added_rows += (len(new_checkbox_metadata) - 1)
  return new_metadata