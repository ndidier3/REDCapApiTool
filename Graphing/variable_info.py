variable_info = {
  'Stimulation': {'match': 'baes_stim', 'title': 'Stimulation', 'is_int': True, 'timepoints': [-30, 30, 60, 120, 180], 'ylabel': None, "yticks": [0, 10, 20, 30, 40, 50, 60, 70, 80]}, #, 50, 60]},
  'Sedation': {'match': 'baes_sed', 'title': 'Sedation', 'is_int': True, 'timepoints': [-30, 30, 60, 120, 180], 'ylabel': None, "yticks": [0, 10, 20, 30, 40, 50, 60, 70, 80]},
  'Feel': {'match': 'deq1', 'title': 'I FEEL drug effects ', 'is_int': True, 'timepoints': [30, 60, 120, 180], 'ylabel': None, "yticks": [0, 20, 40, 60, 80, 100]},
  'Like': {'match': 'deq2', 'title': 'I LIKE the effect I am feeling', 'is_int': True, 'timepoints': [30, 60, 120, 180], 'ylabel': None, "yticks": [0, 20, 40, 60, 80, 100]},
  'Want': {'match': 'deq4', 'title': 'I would like MORE of what I consumed', 'is_int': True, 'timepoints': [30, 60, 120, 180], 'ylabel': None, "yticks": [0, 20, 40, 60, 80, 100]},
  'Pegt': {'match': 'peg_total_sec', 'title': 'Pegboard', 'is_int': False, 'timepoints': [-30, 30, 60, 120, 180], 'ylabel': 'Complete Time (sec)', "yticks": [0, 20, 40, 60, 80, 100]},
  'Dsst': {'match': 'dsst', 'title': 'Digit Symbol Substitution Task (DSST)', 'is_int': False, 'timepoints': [-30, 30, 60, 120, 180], 'ylabel': 'DSST Score', "yticks": [0, 20, 40, 60, 80, 100]},
  'SBP': {'match': 'sys1', 'title': 'Systolic Blood Pressure (SBP)', 'is_int': True, 'timepoints': [-30, 30, 60, 120, 180], 'ylabel': 'SBP', "yticks": [60, 80, 100, 120, 140, 160, 180, 200]},
  'DBP': {'match': 'dia1', 'title': 'Diastolic Blood Pressure (DBP)', 'is_int': True, 'timepoints': [-30, 30, 60, 120, 180], 'ylabel': 'DBP', "yticks": [60, 80, 100, 120, 140, 160, 180, 200]},
  'HR': {'match': 'hr1', 'title': 'Heart Rate (HR)', 'is_int': True, 'timepoints': [-30, 30, 60, 120, 180], 'ylabel': 'HR', "yticks": [40, 60, 80, 100, 120, 140]}
}
