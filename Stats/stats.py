import pandas as pd

def get_categorical_labels(field_name, metadata):
  field_idx = metadata.index[metadata['field_name']==field_name].tolist()[0]
  options = metadata.loc[field_idx, 'select_choices_or_calculations'].split(' | ')
  labels = [option.split(', ', 1)[1] for option in options]
  keys = [option.split(', ', 1)[0] for option in options]
  categories = dict(zip(keys, labels))
  return categories

def generate_continuous_variable_stats(form_data, metadata, field_name, cohort_name, group_field_name, requested_stats = ['mean', 'count', 'min', 'max', 'std', 'sem']):
  group_categories = get_categorical_labels(group_field_name, metadata)
  form_data[field_name] = pd.to_numeric(form_data[field_name], errors='coerce')
  form_data = form_data[form_data[group_field_name].isin([int(group_id) for group_id in group_categories.keys()] + group_categories.keys())]
  stats_grouped = form_data.groupby(form_data[group_field_name]).agg({field_name: requested_stats})
  stats_total = form_data.agg({field_name: requested_stats}).transpose()
  stat_totals_list = list(stats_total.iloc[0])
  stats_grouped.loc[len(stats_grouped)+1, :] = stat_totals_list
  stats_grouped.index = group_categories.values()
  stats_grouped.columns.set_levels([f'{field_name} - {cohort_name}'],level=0, inplace=True)
  return stats_grouped
    
def generate_categorical_variable_stats(form_data, metadata, field_name, cohort_name, group_field_name):
  categorical_summary_totals = form_data[field_name].value_counts(dropna=False)
  categorical_summary = form_data.groupby([group_field_name], dropna=False)[field_name].value_counts(dropna=False).unstack(fill_value=0)
  categorical_summary = categorical_summary.append(categorical_summary_totals, ignore_index=True)
  group_categories = get_categorical_labels(group_field_name, metadata)
  categorical_summary.index = group_categories.values()
  field_categories = get_categorical_labels(field_name, metadata)
  categorical_summary.columns = field_categories.values()

  #get percentage values across rows
  all_row_percentages = []
  for index, row in categorical_summary.iterrows():
    row_sum = row.sum()
    #row_sum = categorical_summary.loc[index].sum()
    one_row_percentages = []
    for col_name in categorical_summary.columns:
      n = categorical_summary.loc[index, col_name]
      # n = categorical_summary[col_name].loc[index]
      perc = round(((n / row_sum)*100), 2)
      perc_string = str(perc) + ' %'
      one_row_percentages.append({col_name: perc_string})
    all_row_percentages.append(one_row_percentages)

  perc_col_names = []
  categorical_col_name = []    
  #create column names for the percentage columns
  #EDIT TO BE FIRST WORD + %
  for col_name in categorical_summary.columns:
    if len(str(col_name)) > 7:
      shortened_name = col_name[0:5]
      perc_col_name = f'{shortened_name} %'
    else:
      perc_col_name = f'{col_name} %'
                
      #adjust the perc_col_name if it is a duplicate
    ticker=1
    while perc_col_name in perc_col_names:
      adjusted_shortened_name = col_name[0:(5+ticker)]
      perc_col_name = f'{adjusted_shortened_name} %'
      ticker += 1
    perc_col_names.append(perc_col_name)  
    categorical_col_name.append(col_name)
            
  #manipulate the data into column format
  col_perc_dicts = []
  for col_name in categorical_summary.columns:
    col_percentages = []
    for row_percentages in all_row_percentages:
      for single_perc_dict in row_percentages:
        perc_string = single_perc_dict.get(col_name, 'None')
        if perc_string != 'None':
          col_percentages.append(perc_string)
    col_perc_dicts.append({col_name: col_percentages})
            
  #add percentage columns to the summary dataframe
  ticker = 0
  for i, col_name in enumerate(categorical_col_name):
    perc_col_name = perc_col_names[i]
    col_perc_dict = col_perc_dicts[i]
    column_location = i + 1 + ticker
    categorical_summary.insert(loc = column_location, column = perc_col_name, value = col_perc_dict[col_name])
    ticker += 1
      
  return categorical_summary