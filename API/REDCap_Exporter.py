from API.REDCap_API import redcapApiConfiguration
from Utils.configuration import *
from Graphing.line_graphs import *
from Graphing.variable_info import variable_info
from Utils.get_record import get_record_data
import pandas as pd
from functools import reduce

class REDCapExporter(redcapApiConfiguration):
  def __init__(self, token, common_fields=[]):
    super().__init__(token)
    self.cohort = None
    self.project_info = self.export_project_info()
    self.is_longitudinal = self.project_info['is_longitudinal']
    self.common_fields = common_fields
    self.all_raw_data = self.export_records_raw()
    self.metadata = self.export_metadata()
    self.form_fields = self.export_form_fields()
    self.forms = list(self.form_fields.keys())
    self.field_names = self.export_field_names()
    self.descriptive_fields = self.export_descriptive_fields()
    self.event_forms = self.export_event_form_mappings()
    self.arms = self.export_arms()
    self.form_event_pairings = self.export_form_event_pairings()
    self.repeated_forms_events = self.export_repeated_forms_events()
    self.all_forms = self.export_all_forms()
    self.all_forms_metadata = self.export_all_form_metadata(self.all_forms)
    self.metadataFields = [
      'field_name', 'form_name', 'section_header', 'field_type',
      'field_label', 'select_choices_or_calculations', 'field_note',
      'text_validation_type_or_show_slider_number', 'text_validation_min',
      'text_validation_max', 'identifier', 'branching_logic',
      'required_field', 'custom_alignment', 'question_number',
      'matrix_group_name', 'matrix_ranking', 'field_annotation'
    ]
    self.forms_unblinded_wide = {}
    self.forms_unblinded_long = {}
      
  def export_project_info(self):
    return self.export(self.project_info_request)
  
  def export_field_names(self, as_list=True, keep_form_complete_fields=True):
    dataframe = self.get_response_as_dataframe(self.field_names_request)
    if as_list:
      fields = dataframe['original_field_name'].tolist()
      if keep_form_complete_fields:
        return fields
      else:
        trimmed_fields = fields
        for field in fields:
          if len(field) > 8:
            if field[-8] != "complete":
              trimmed_fields.remove(field)
        return trimmed_fields
    else:
      if keep_form_complete_fields:
        return dataframe
      else: 
        dataframe_no_complete_fields = dataframe[dataframe['export_field_name'].str.contains('_complete') == False]
        return dataframe_no_complete_fields
          
  def export_records_raw(self):
    df = self.get_response_as_dataframe(self.all_data_request)
    if 'csdpnum' in df.columns:
      df = clean_csdpnum_column(df)
    if 'subid' in df.columns:
      df = clean_subid_column(df)
    return df

  def export_metadata(self):
    return self.get_response_as_dataframe(self.metadata_request)
      
  def export_event_form_mappings(self):
    if self.is_longitudinal:
      event_mappings = self.get_response_as_dataframe(self.events_request)
      event_forms = {}
      for event in event_mappings['unique_event_name'].unique().tolist():
        one_event = event_mappings[event_mappings['unique_event_name']==event]
        event_forms[event] = one_event['form'].tolist()
      return event_forms
    else:
      return None
  def export_arms(self):
    return self.export(self.arms_request)

  def export_repeated_forms_events(self):
    if self.is_longitudinal:
      return self.export(self.repeated_forms_events_request)
    else:
      return None
  
  def export_form_event_pairings(self):
    if self.is_longitudinal:
      event_mappings = self.get_response_as_dataframe(self.events_request)
      form_event_pairings = {}
      for form in event_mappings['form'].unique().tolist():
        one_form = event_mappings[event_mappings['form']==form]
        form_event_pairings[form] = [event for event in one_form['unique_event_name'].unique().tolist()]
      return form_event_pairings
    else:
      return None
  
  def export_form_names(self):
    return self.get_response_as_dataframe(self.instruments_request)
  
  def export_form_fields(self):
    form_fields = {}
    for form_name in self.metadata['form_name'].unique().tolist():
      form_fields[form_name] = self.metadata[self.metadata['form_name']==form_name]['field_name'].tolist()
    return form_fields
  
  def export_descriptive_fields(self):
    return self.metadata[self.metadata['field_type']=='descriptive']['field_name'].tolist()
  
  def export_forms(self, form_names):
    common_fields = self.common_fields.copy()
    form_fields = []
    for form_name in form_names:
      form_fields.extend(self.form_fields[form_name].copy())
    form_fields.extend(common_fields)
    fields = list(set(form_fields)) #to remove duplicates
    descriptive_fields = self.descriptive_fields.copy()
    fields = [field for field in fields if field not in descriptive_fields]
    
    #sometimes form_fields have slightly different spelling of column_names - this ensures spelling is consistent
    for i, field in enumerate(fields):
      if field not in self.all_raw_data.columns.tolist():
        for column_name in self.all_raw_data.columns.tolist():
          if field in column_name or column_name in field:
            fields[i] = column_name
    
    form_data = self.all_raw_data[fields].copy()
    if self.is_longitudinal:
      for subid in form_data['subid'].unique():
        for field_name in [f for f in common_fields if f != 'redcap_event_name']:
          data_one_field_one_subid = form_data[form_data['subid']==subid][field_name].tolist()
          for datum in data_one_field_one_subid:
            if datum:
              form_data.loc[form_data['subid']==subid, field_name] = datum
              break
      event_names = []
      for form_name in form_names:
        event_names.extend(self.form_event_pairings[form_name])
      form_data = form_data[form_data['redcap_event_name'].isin(event_names)]
    
    form_fields = [field for field in fields if field not in common_fields]
    form_fields.sort(key=natural_keys)
    common_fields.extend(form_fields)
    form_data = form_data[common_fields]
    #form_data.rename(columns = {'rando_sex' : 'sex'}, inplace=True)
    form_data.reset_index(inplace=True, drop=True)
    form_data = convert_all_numeric_string_columns_to_numeric(form_data)
    return form_data
  
  def export_all_forms(self):
    data_all_forms = {}
    if self.is_longitudinal:
      for form, event in self.form_event_pairings.items():
        form_data = self.export_forms([form])
        data_all_forms[form] = form_data
    else:
      for form in self.forms:
        form_data = self.export_forms([form])
        data_all_forms[form] = form_data
    return data_all_forms
  
  def export_form_metadata(self, form):
    fields = form.columns.tolist()
    form_metadata = self.metadata[self.metadata['field_name'].isin(fields)]
    return form_metadata
  
  def export_all_form_metadata(self, data_all_forms):
    metadata_all_forms = {}
    for form_name, form_data in data_all_forms.items():
        form_metadata = self.export_form_metadata(form_data)
        metadata_all_forms[form_name] = form_metadata
    return metadata_all_forms

  def export_to_excel(self, folder_name):
    for name, form in self.all_forms.items():
      form.to_excel(f'C:/Users/ndidier/Desktop/REDCap_Data_Management/{folder_name}/{name}.xlsx', index=False)

  #for longitudinal projects only
  def export_form_by_dose(self, form_names=None, event_names=None, active_label='A_', control_label='P_', randomization = {'Placebo_First': 1, 'Alcohol_First': 2}):
    
    if event_names is not None:
      form_names = []
      for event_name in event_names:
         form_names.extend(self.event_forms[event_name])
      form_names = list(set(form_names))

    form_data = self.export_forms(form_names)
    form_data['rando_code'] = pd.to_numeric(form_data['rando_code'], errors='coerce')
    form_data['subid'] = pd.to_numeric(form_data['subid'], errors='coerce')
    form_data.dropna(subset=['subid'], inplace=True)
    form_data['subid'] = form_data['subid'].astype(int)
    common_field_names = form_data.columns.tolist()[:len(self.common_fields)]
    common_fields_length = len(self.common_fields)
    form_fields = form_data.columns.tolist()
    
    session_ids = {
      'session_a': 'A',
      'session_b': 'B'
    }
    active_events = {
      'a': [],
      'b': []
    }
    placebo_events = {
      'a': [],
      'b': []
    }

    repeated_event_ids = dict(zip(['timepoin_arm_1', 'timepoin_arm_1b', 'timepoin_arm_1c', 'timepoin_arm_1d', 'timepoin_arm_1e'], ['_t0', '_t1', '_t2', '_t3', '_t4', '_t5']))

    active_column_names = []
    placebo_column_names = []
    if event_names is not None:
      events = event_names
    else:
      event_list = [self.form_event_pairings[form_name] for form_name in form_names]
      events = [event for sublist in event_list for event in sublist]

    print('events:', events)
    long_data = pd.DataFrame()
    # Change to load all forms from event

    for event in events:
      forms = self.event_forms[event] if event_names is not None else form_names
      for key, val in repeated_event_ids.items():
        if key == event[len(event)-len(key):]:
          timepoint_label = val
          break
        else:
          timepoint_label = ''
      for rando_code in [1, 2]:
        event_data = form_data[(form_data['redcap_event_name']==event) & (form_data['rando_code']==rando_code)]
        is_placebo_session = ((rando_code == randomization['Placebo_First']) and ('session_a' in event)) or ((rando_code == randomization['Alcohol_First']) and ('session_b' in event))
        is_alcohol_session = ((rando_code == randomization['Alcohol_First']) and ('session_a' in event)) or ((rando_code == randomization['Placebo_First']) and ('session_b' in event))
        if is_alcohol_session:
          for timepoint, form in enumerate(forms) :
            field_names = common_field_names + [field for field in self.metadata[self.metadata['form_name']==form]['field_name'].tolist() if field in event_data.columns.tolist()]
            if len(timepoint_label) > 0:
              timepoint = timepoint_label[-1]
            timepoint_data = event_data[field_names]
            timepoint_data = timepoint_to_long(timepoint_data, timepoint, active_label)
            long_data = long_data.append(timepoint_data)
          active_field_names = [active_label + field + timepoint_label for field in form_fields if field not in common_field_names]
          active_column_names.append(active_field_names)
          new_field_names = common_field_names + active_field_names
          event_data.columns = new_field_names
          event_data['subid'] = pd.to_numeric(event_data['subid'], errors='coerce')
          if 'session_a' in event:
            active_events['a'].append(event_data)
          else:
            active_events['b'].append(event_data)

        if is_placebo_session:
          for timepoint, form in enumerate(forms):
            field_names = common_field_names + [field for field in self.metadata[self.metadata['form_name']==form]['field_name'].tolist() if field in event_data.columns.tolist()]
            if len(timepoint_label) > 0:
              timepoint = timepoint_label[-1]
            timepoint_data = event_data[field_names]
            timepoint_data = timepoint_to_long(timepoint_data, timepoint, control_label)
            long_data = long_data.append(timepoint_data)
          placebo_field_names = [control_label + field + timepoint_label for field in form_fields if field not in common_field_names]
          placebo_column_names.append(placebo_field_names)
          new_field_names = common_field_names + placebo_field_names
          event_data.columns = new_field_names
          event_data.loc[:, 'subid'] = pd.to_numeric(event_data['subid'], errors='coerce')
          #event_data.set_index('subid', inplace=True)
          if 'session_a' in event:
            placebo_events['a'].append(event_data)
          else:
            placebo_events['b'].append(event_data)
          
    active_a = reduce(lambda left, right: pd.merge(left, right, on = "subid", how = "outer"), active_events['a'])
    active_b = reduce(lambda left, right: pd.merge(left, right, on = "subid", how = "outer"), active_events['b'])
    placebo_a = reduce(lambda left, right: pd.merge(left, right, on = "subid", how = "outer"), placebo_events['a'])
    placebo_b = reduce(lambda left, right: pd.merge(left, right, on = "subid", how = "outer"), placebo_events['b'])
    group_a = active_a.merge(placebo_b, on='subid', how='outer')
    group_b = active_b.merge(placebo_a, on='subid', how='outer')
    
    long_data.sort_values(by=['subid', 'Dose', 'Timepoint'], inplace=True)

    if set(group_a.columns.tolist()) == set(group_b.columns.tolist()):
        final = pd.concat([group_a, group_b])
        cols_to_remove = [col for col in final.columns.tolist() if any(common_col in col for common_col in common_field_names)]
        to_keep = final.iloc[:, :common_fields_length]
        to_keep.columns = common_field_names
        #common_fields = final.iloc[:,common_fields_length+1:]
        final.drop(cols_to_remove, axis=1, inplace=True)
        form_cols = [col for col in final.columns.tolist() if sum(substring in col for substring in ['t0', 't1', 't2', 't3', 't4', 't5']) < 2]
        final = pd.concat([final, to_keep], axis=1)
        final = final[common_field_names + form_cols]
        final.dropna(how='all', axis=1, inplace=True, thresh=None)
        # empty_cols = [col for col in final.columns.tolist() if all(x=='' for x in final[col].tolist())]
        # final.drop(empty_cols, axis=1, inplace=True)
        if 'A_t1_start_time_t0' in final.columns.tolist():
          print(final['A_t0_end_time_t2'].value_counts())
          print(final['A_t0_end_time_t2'].describe())
        final.sort_values(by='subid', inplace=True)
        return final, long_data
    else:
        print('not equal columns')

  def export_all_unblinded_forms(self, path):
    for form in self.forms:
      try:
        form_wide, form_long = self.export_form_by_dose([form])
        self.forms_unblinded_wide[form] = form_wide
        self.forms_unblinded_long[form] = form_long
        form_wide.to_excel(f'{path}/Wide/{form}_unblinded_wide.xlsx', index=False)
        form_long.to_excel(f'{path}/Long/{form}_unblinded_long.xlsx', index=False)
      except:
        print(f'no unblinded export for {form}')

  def export_all_unblinded_events(self, path):
    events = self.event_forms.keys()
    repeated_events = ['arrival', 'data_ent', 'presessi', 'timepoin']
    event_combinations = {}
    for repeated_event in repeated_events:
      event_combinations[repeated_event] = [event for event in events if repeated_event in event]

    for repeated_event_name, events in event_combinations.items():
      form_wide, form_long = self.export_form_by_dose(event_names=events)
      self.forms_unblinded_wide[repeated_event_name] = form_wide
      self.forms_unblinded_long[repeated_event_name] = form_long
      form_wide.to_excel(f'{path}/Wide/{repeated_event_name}_unblinded_wide.xlsx', index=False)
      form_long.to_excel(f'{path}/Long/{repeated_event_name}_unblinded_long.xlsx', index=False)
      print(f'SUCCESS {repeated_event_name}')

  def export_bp(self):
    data, long_data = self.export_form_by_dose(event_names=['session_a_data_ent_arm_1', 'session_b_data_ent_arm_1'])
    cols_to_drop = [col for col in data.columns if ('peg' in col) or ('dsst' in col)]
    data.drop(cols_to_drop, axis=1, inplace=True)
    cols_to_drop = [col for col in long_data.columns if ('peg' in col) or ('dsst' in col)]
    long_data.drop(cols_to_drop, axis=1, inplace=True)
    data.drop('redcap_event_name', axis=1, inplace=True)
    self.forms_unblinded_wide['BP'] = data
    data.to_excel('C:/Users/ndidier/Desktop/REDCap_Data_Management/CSDP_C4/Sessions/Unblinded/bp_unblinded_wide.xlsx', index=False)
    long_data.to_excel('C:/Users/ndidier/Desktop/REDCap_Data_Management/CSDP_C4/Sessions/Unblinded/bp_unblinded_long.xlsx', index=False)
  
  def create_single_record_graphs(self, subids, dataframe, variable_title, path):
    print(type(subids))
    if not isinstance(subids, list):
      try:
        subids = [subids]
      except:
        print('Error: Invalid Record Type. Must be List.')
    print(subids)
    match = variable_info[variable_title]['match']
    print(match)
    timepoints = variable_info[variable_title]['timepoints']
    y_ticks = variable_info[variable_title]['yticks']
    title = variable_info[variable_title]['title']
    ylabel = variable_info[variable_title]['ylabel']
    data = {'A': [], 'P': []}
    record = get_record_data(subids, dataframe, match, self.common_fields)
    for dose in ['A', 'P']:
      dose_record = record[[col for col in record.columns if (dose + '_') in col]]
      print(dose_record)
      data_list = dose_record.T.iloc[:,0].tolist()
      print(data_list)
      if variable_info[variable_title]['is_int']:
        data_list = [int(datum) for datum in data_list]
      data[dose] = data_list
    for subid in subids:
      create_line_graph_alcohol(subid, match, title, alc_data=data['A'], timepoints=timepoints, yticks=y_ticks, ylabel=ylabel, path=path)
      create_line_graph_alcohol_and_placebo(subid, match, title, alc_data=data['A'], pla_data=data['P'], timepoints=timepoints, yticks=y_ticks, ylabel=ylabel, path=path)
  
  
