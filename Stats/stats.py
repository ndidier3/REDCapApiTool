import pandas as pd

def identify_numeric_columns():
  print('not yet created')
    
def generate_continuous_variable_stats(form_data, field_name, cohort_name, group_labels = ['LD', 'AUD'], requested_stats = ['mean', 'count', 'min', 'max', 'std', 'sem'], group_field_name = 'group'):
  form_data[field_name] = pd.to_numeric(form_data[field_name], errors='coerce')
  form_data = form_data[form_data[group_field_name].isin([1, '1', 3, '3'])]
  stats_grouped = form_data.groupby(form_data[group_field_name]).agg({field_name: requested_stats})
  stats_total = form_data.agg({field_name: requested_stats}).transpose()
  stat_totals_list = list(stats_total.iloc[0])
  stats_grouped.loc[len(stats_grouped)+1, :] = stat_totals_list
  print(stats_grouped)
  print(group_labels)
  stats_grouped.index = group_labels
  stats_grouped.columns.set_levels([f'{field_name} - {cohort_name}'],level=0, inplace=True)
  return stats_grouped
    
def generate_continuous_variable_stats_entire_form(form_data, numeric_columns, form_name, cohort_name):
  #form_data = form_data[form_data['valid']==1]
  if len(numeric_columns) > 0:
    numerical_summaries = {}
    for field_name in numeric_columns:
      numerical_summaries[field_name] = generate_continuous_variable_stats(form_data, field_name)
    return numerical_summaries

  else:
    print(f'NO NUMERIC DATA FOR FORM: {form_name} {cohort_name}')