import pandas as pd
from Utils.configuration import *
from API.REDCap_Exporter import REDCapExporter

class RedcapMerger:
  def __init__(self, sessions, screens):
    self.sessions = sessions
    self.screens = screens
  
  def export_arrival_database(self):
    
    sessions = self.sessions
    session_arrival, session_arrival_long = sessions.export_form_by_dose(form_names=['session_arrival_questionnaire'])
    session_arrival.to_excel('C:/Users/ndidier/Desktop/REDCap_Data_Management/CSDP_C4/Sessions/Unblinded/arrival_unblinded.xlsx', index=False)

    # alcohol_arrival = session_arrival[sessions.common_fields + [col for col in session_arrival.columns if 'Aarrival' in col]]
    # alcohol_arrival.columns = sessions.common_fields + [col[1:] for col in session_arrival.columns if 'Aarrival' in col]

    # placebo_arrival = session_arrival[sessions.common_fields + [col for col in session_arrival.columns if 'Parrival' in col]]
    # placebo_arrival.columns = sessions.common_fields + [col[1:] for col in session_arrival.columns if 'Parrival' in col]

    screens = self.screens
    screen_meds = screens.all_forms['health_form_1'][screens.common_fields + ['medications', 'medsspecify']]
    screen_psych = screens.all_forms['substance_use_and_psych_review'][screens.common_fields + list(variable_names['psych']['redcap_variables'].keys())]

    merged = session_arrival.merge(screen_meds, on='csdpnum', how='left')
    merged = merged.merge(screen_psych, on='csdpnum', how='left')
    merged.to_excel('C:/Users/ndidier/Desktop/REDCap_Data_Management/CSDP_C4/Sessions/Unblinded/merged_arrival.xlsx', index=False)

    
    writer = pd.ExcelWriter('C:/Users/ndidier/Desktop/REDCap_Data_Management/CSDP_C4/Sessions/Unblinded/arrival_database_ND.xlsx')

    for section_name, details in variable_names.items():
      old_column_names = sessions.common_fields.copy()
      new_column_names = sessions.common_fields.copy()
      for column_name in merged.columns:
        if column_name[2:] in details['redcap_variables'].keys():
          new_column_names.append(column_name[:2] + details['redcap_variables'][column_name[2:]])
          old_column_names.append(column_name)
        elif column_name in details['redcap_variables'].keys():
          new_column_names.append('S_' + details['redcap_variables'][column_name])
          old_column_names.append(column_name)
      section_data = merged[old_column_names]
      section_data.rename(columns=dict(zip(old_column_names, new_column_names)), inplace=True)
      section_data.to_excel(f'C:/Users/ndidier/Desktop/REDCap_Data_Management/CSDP_C4/Sessions/Unblinded/{section_name}_ND.xlsx')
      for new_variable_name, variable_creator in details['new_variables'].items():
        variables_for_function = details['new_variables'][new_variable_name]['variables_used']
        session = False
        for i, variable in enumerate(variables_for_function):
          if variable not in section_data.columns:
            session = True
        if session:
          for dose in ['A', 'P']:
            session_variables_for_function = [dose + '_' + variable for variable in variables_for_function]
            # this needs A and P within new variable name
            session_variables_for_function.insert(0, dose + '_' + new_variable_name)
            section_data = details['new_variables'][new_variable_name]['function'](section_data, session_variables_for_function)
        else:
          variables_for_function.insert(0, new_variable_name)
          section_data = details['new_variables'][new_variable_name]['function'](section_data, variables_for_function)
      section_data.drop('redcap_event_name', axis=1, inplace=True)
      section_data.rename(columns={'rando_sex': 'sex'}, inplace=True)
      if section_name != 'psych':
        columns_rearranged = [col for col in section_data.columns if col not in ['A_ArrivalTime', 'P_ArrivalTime']]
        columns_rearranged[6:6] = ['A_ArrivalTime', 'P_ArrivalTime']
        section_data = section_data[columns_rearranged]
      section_data.to_excel(writer, sheet_name=section_name, index=False)

    writer.save()
