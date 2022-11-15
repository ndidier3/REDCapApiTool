import os
import re
import pandas as pd
import datetime
import numpy as np
import difflib
import nltk
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

def character_similarity(str1, str2):
  c, j = 0, 0
  for i in str1:
    if str2.find(i) > 0 and j == str1.find(i):
      c += 1
    j += 1
  return c

def clean_text_column(df, column_name):
  df[column_name] = df[column_name].astype("str") 
  df[column_name] = df[column_name].str.replace(',','')
  df[column_name] = df[column_name].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))
  return df

def timepoint_to_long(df, timepoint, dose_label):
    df.columns = [col.replace(f'T{timepoint}', '') for col in df.columns]
    df.columns = [col.replace(f't{timepoint}_', '') for col in df.columns]
    df.insert(loc = 6, column = 'Timepoint', value = [timepoint for i in range(0, len(df))])
    df.insert(loc = 7, column = 'Dose', value = [dose_label for i in range(0, len(df))])
    return df

def get_time_difference_hours(df, variables):
  variable_name, arrival_time, timestamp = variables[0], variables[1], variables[2]
  column_index = df.columns.get_loc(timestamp)
  df.insert(column_index+1, variable_name, (pd.to_datetime(df[arrival_time]) - pd.to_datetime(df[timestamp])) / np.timedelta64(1, 'h'))
  return df

def get_time_difference_days(df, variables):
  variable_name, arrival_time, timestamp = variables[0], variables[1], variables[2]
  column_index = df.columns.get_loc(timestamp)
  df.insert(column_index+1, variable_name, (pd.to_datetime(df[arrival_time]) - pd.to_datetime(df[timestamp])) / np.timedelta64(1, 'D'))
  return df

def get_sleep_hours(df, variables):
  variable_name, wake_time, bed_time = variables[0], variables[1], variables[2]
  column_index = df.columns.get_loc(bed_time)
  
  falsy = ((df[wake_time].isna()) | (df[bed_time].isna()) | (df[wake_time]=='') | (df[bed_time]==''))
  to_assess = df[~falsy]
  to_ignore = df[falsy]

  to_assess.insert(column_index+1, variable_name, (pd.to_datetime(to_assess[bed_time], format="%H:%M") - pd.to_datetime(to_assess[wake_time], format="%H:%M")).dt.total_seconds() / 60 / 60)
  
  to_assess[variable_name] = to_assess[variable_name].apply(lambda x: x if x > 0 else (x+24))

  to_ignore.insert(column_index+1, variable_name, ['' for i in range(0, len(to_ignore))])

  df = to_assess.append(to_ignore)
  df.sort_values(by='subid', inplace=True)
  #df.insert(column_index+1, variable_name, sleep_hours)
  return df

def get_awake_hours(df, variables):
    variable_name, arrival_time, wake_time = variables[0], variables[1], variables[2]
    column_index = df.columns.get_loc(wake_time)
  
    falsy = ((df[arrival_time].isna()) | (df[wake_time].isna()) | (df[wake_time]=='') | (df[arrival_time]==''))
    to_assess = df[~falsy]
    to_ignore = df[falsy]

    wake_datetime = pd.to_datetime(pd.to_datetime(to_assess[arrival_time]).dt.date.astype(str) + ' ' + pd.to_datetime(to_assess[wake_time], format="%H:%M").dt.time.astype(str))

    to_assess.insert(column_index+1, variable_name, (pd.to_datetime(to_assess[arrival_time]) - wake_datetime).dt.total_seconds() / 60 / 60)

    to_ignore.insert(column_index+1, variable_name, ['' for i in range(0, len(to_ignore))])

    df = to_assess.append(to_ignore)
    df.sort_values(by='subid', inplace=True)
    return df

def get_sleep_diff(df, variables):
    variable_name, hours_sleep, hours_sleep_norm = variables[0], variables[1], variables[2]
    df.loc[:, hours_sleep] = pd.to_numeric(df[hours_sleep])
    df.loc[:, hours_sleep_norm] = pd.to_numeric(df[hours_sleep_norm])
    column_index = df.columns.get_loc(hours_sleep_norm)
    df.insert(column_index+1, variable_name, df[hours_sleep] - df[hours_sleep_norm])
    return df

def get_proportion(df, variables):
    variable_name, cycle_duration, current_duration = variables[0], variables[1], variables[2]
    column_index = df.columns.get_loc(cycle_duration)
    new_column = df[current_duration] / df[cycle_duration]
    df.insert(column_index+1, variable_name, new_column)
    return df

def get_drug_class(df, variables):
  variable_name, medications = variables[0], variables[1]
  classes = {
    'PAIN': ['tylenol', 'advil', 'ibuprofen', 'ecedrin'],
    'NARC': ['opioid', 'opoid'],
    'CNBS': ['cbd', 'cbd gummies', 'cannabis', 'thc'],
    'DEPR': ['ambien'],
    'ADEP': ['sirtraline', 'sertraline', 'ssri'],
    'ANXI': [],
    'CONV': [],
    'MOTR': [],
    'COGN': ['adderall'],
    'AMNE': [],
    'STIM': [],
    'HALU': [],
    'GERM': [],
    'HIST': ['loratidine'],
    'CARD': ['HPB', 'cholesterol', 'chloresterol'],
    'RESP': ['inhaler', 'asthma', 'monticlaus', 'monticlos', 'albuterol sulfate', 'albuterol', 'monteklaust'],
    'DGST': ['famotidine', 'omeprazole', 'omerprazole'],
    'LIVR': [],
    'MUSC': [],
    'REPR': [],
    'SUPP': ['vitamins', 'preservision', 'multivitamin', 'flinstone', 'flinstone vitamins'],
    'MISC': ['synthroid', 'levothyroxine'],
  }
  df = clean_text_column(df, medications)
  medication_classes = []
  for medication in df[medications].tolist():
    medication = medication.lower()
    if medication:
      closest_words = {}
      for category, med_list in classes.items():
        match = difflib.get_close_matches(medication, med_list, n=1, cutoff=0.8)
        if len(match) > 0:
            closest_words[match[0]] = category
      final_match = difflib.get_close_matches(medication, list(closest_words.keys()), n=1)
      if (len(final_match) > 0):
        medication_classes.append(closest_words[final_match[0]])
      else:
        medication_classes.append('REVIEW')
    else:
      medication_classes.append('')
  column_index = df.columns.get_loc(medications)
  df.insert(column_index+1, variable_name, medication_classes)
  return df

def get_categorical_rating(df, variables, demarcations = [-100000, 0, 3, 24, 72, 100000]):
  variable_name, continuous_variable = variables[0], variables[1]
  df[continuous_variable] = pd.to_numeric(df[continuous_variable])
  column_index = df.columns.get_loc(continuous_variable)
  df.insert(column_index+1, variable_name, pd.cut(x=df[continuous_variable], bins = demarcations, labels=['Error', 1, 2, 3, 4]))
  return df

def get_food_amount_rating(df, variables):
  food_quantity, food_variable = variables[0], variables[1]
  df = clean_text_column(df, food_variable)
  df['food_characters'] = df[food_variable].apply(lambda x: len(x))
  column_index = df.columns.get_loc(food_variable)
  df.insert(column_index+1, food_quantity, pd.cut(x=df['food_characters'], bins = [0, 15, 35, 100], labels=[1, 2, 3]))
  df.drop('food_characters', axis=1, inplace=True)

  return df

variable_names = {
  'medications': {
    'redcap_variables': {
      'arrival_time': 'ArrivalTime',
      'arrival15': 'MedsPast3Days',
      'arrival16': 'Med1',
      'arrival16a': 'Med1Time',
      'arrival17': 'Med2',
      'arrival17a': 'Med2Time',
      'arrival18': 'Med3',
      'arrival18a': 'Med3Time',
      'medications': 'MedsPastMonth',
      'medsspecify': 'MedDetails'
    },
    'new_variables': {
      'HrsSinceMed1': {
        'variables_used': ['ArrivalTime', 'Med1Time'],
        'function': get_time_difference_hours
      },
      'HrsSinceMed2': {
        'variables_used': ['ArrivalTime', 'Med2Time'],
        'function': get_time_difference_hours
      },
      'HrsSinceMed3': {
        'variables_used': ['ArrivalTime', 'Med3Time'],
        'function': get_time_difference_hours
      },
      'Class1': {
        'variables_used': ['Med1'],
        'function': get_drug_class
      },
      'Class2': {
        'variables_used': ['Med2'],
        'function': get_drug_class
      },
      'Class3': {
        'variables_used': ['Med3'],
        'function': get_drug_class
      },
      'Class1Timeframe': {
        'variables_used': ['HrsSinceMed1'],
        'function': get_categorical_rating
      },
      'Class2Timeframe': {
        'variables_used': ['HrsSinceMed2'],
        'function': get_categorical_rating
      },
      'Class3Timeframe': {
        'variables_used': ['HrsSinceMed3'],
        'function': get_categorical_rating
      }
    }
  },
  'drugs': {
    'redcap_variables': {
      'arrival_time': 'ArrivalTime',
      'arrival9': 'AlcPast3Days',
      'arrival10': 'DrkTime',
      'arrival11': 'DrkCount',
      'arrival_brac': 'ArrivalBrac',
      'arrival12': 'RecDrugsPast3Days',
      'arrival13': 'RecDrugMostUsed',
      'arrival13a': 'RecDrugTime',
      'arrival14': 'RecDrugOther',
      'arrival14a': 'RecDrugOtherTime',
      'arrival19': 'CigsPast3Days',
      'arrival20': 'CigTime',
      'arrival21': 'CigCount',
      'arrival_co_ppm': 'COppm',
      'arrival_co_percent': 'COpercent',
      'arrival7': 'CaffPast3Days',
      'arrival8': 'CaffTime'
    },
    'new_variables': {
      'HrsSinceLastDrk': {
        'variables_used': ['ArrivalTime', 'DrkTime'],
        'function': get_time_difference_hours
      },
      'LastDrkTimeframe': {
        'variables_used': ['HrsSinceLastDrk'],
        'function': get_categorical_rating
      },
      'HrsSinceRecDrug': {
        'variables_used': ['ArrivalTime', 'RecDrugTime'],
        'function': get_time_difference_hours
      },
      'RecDrugTimeframe': {
        'variables_used': ['HrsSinceRecDrug'],
        'function': get_categorical_rating
      },
      'HrsSinceRecDrugOther': {
        'variables_used': ['ArrivalTime', 'RecDrugOtherTime'],
        'function': get_time_difference_hours
      },
      'RecDrugOtherTimeframe': {
        'variables_used': ['HrsSinceRecDrugOther'],
        'function': get_categorical_rating
      },
      'HrsSinceCig': {
        'variables_used': ['ArrivalTime', 'CigTime'],
        'function': get_time_difference_hours
      },
      'CigTimeframe': {
        'variables_used': ['HrsSinceCig'],
        'function': get_categorical_rating
      },
      'HrsSinceCaff': {
        'variables_used': ['ArrivalTime', 'CaffTime'],
        'function': get_time_difference_hours
      },
      'CaffTimeframe': {
        'variables_used': ['HrsSinceCaff'],
        'function': get_categorical_rating
      }
    }
  },
  'food': {
    'redcap_variables': {
      'arrival_time': 'ArrivalTime',
      'arrival5': 'FoodPast3Hours',
      'arrival6': 'FoodToday'
    },
    'new_variables': {
      'FoodAmount': {
        'variables_used': ['FoodToday'],
        'function': get_food_amount_rating
      }
    }
  },
  'sleep': {
    'redcap_variables': {
      'arrival_time': 'ArrivalTime',
      'arrival3a': 'BedTime',
      'arrival3b': 'WakeTime',
      'arrival4a': 'BedTimeNorm',
      'arrival4b': 'WakeTimeNorm'
    },
    'new_variables': {
      'HrsSleep': {
        'variables_used': ['BedTime', 'WakeTime'],
        'function': get_sleep_hours
      },
      'HrsSleepNorm': {
        'variables_used': ['BedTimeNorm', 'WakeTimeNorm'],
        'function': get_sleep_hours
      },
      'HrsSleepNormDiff': {
        'variables_used': ['HrsSleep', 'HrsSleepNorm'],
        'function': get_sleep_diff
      },
      'HrsAwake': {
        'variables_used': ['ArrivalTime', 'WakeTime'],
        'function': get_awake_hours
      },
    }
  },
  'menstrual': {
    'redcap_variables': {
      'arrival_time': 'ArrivalTime',
      'arrival23': 'CycleBeginDate',
      'arrival24': 'CycleDuration',
      'arrival25': 'BirthCtrl',
      'arrival26': 'BirthCtrlMethod'
    },
    'new_variables': {
      'MenstrualCycleDay': {
        'variables_used': ['ArrivalTime', 'CycleBeginDate'],
        'function': get_time_difference_days
      },
      'CycleCompletePerc': {
        'variables_used': ['CycleDuration', 'MenstrualCycleDay'],
        'function': get_proportion
      }
    }
  },
  'transportation': {
    'redcap_variables': {
      'arrival_time': 'ArrivalTime',
      'arrival1': 'ArrivalMode',
      'arrival1a': 'ArrivalModeOther',
      'arrival2': 'DepartureMode',
      'arrival2a': 'DepartureModeOther',
      'arrival2b': 'DropoffAddress'
    },
    'new_variables': {
    }
  },
  'psych': {
    'redcap_variables': {
        'psy_conditions___3': 'CurrentPsychDisorders',
        'psyhealthnotes':'PsychNotes',
        'ocdscreen1': 'OCD',
        'bipolarscreen1': 'BipolarScreen',
        'eatingscreen1': 'AnorexiaScreen',
        'eatingscreen2': 'BingeEatScreen',
        'mdescreen1': 'DeprScreen',
        'mdescreen2': 'AnhedoniaScreen',
        'ocdscreen1': 'ObsessionScreen',
        'ocdscreen2': 'CompulsionScreen',
        'psychoticscreen1': 'PsychosisScreen'
    },
    'new_variables': {
    }
  }
}