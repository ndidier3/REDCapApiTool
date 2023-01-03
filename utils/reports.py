import pandas as pd
from Stats.stats import *

def standard_report_to_excel(writer, form, metadata, cohort_name, group_field_name):
  column = 4
  row = 4
  for field_name in form.columns.tolist():
    field_type = metadata.loc[metadata.index[metadata['field_name']==field_name].tolist()[0], 'field_type']
    if field_type == 'numeric':
      stats = generate_continuous_variable_stats(form, metadata, field_name, cohort_name, group_field_name)
    if (field_type == 'radio') or (field_type == 'dropdown'):
      stats = generate_categorical_variable_stats(form, metadata, field_name, cohort_name, group_field_name)
    stats.to_excel(writer, index=False, startrow=row, startcol=column)