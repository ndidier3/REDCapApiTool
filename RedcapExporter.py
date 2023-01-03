import argparse
import pandas as pd
import os
from API.REDCap_Exporter import REDCapExporter
from API.REDCap_Merger import RedcapMerger
from Utils.load import load
import pickle

def parseArgs():
  parser = argparse.ArgumentParser(description='Export data from REDCap.')
  parser.add_argument('-T', '--Token', required=True, help="REDCap Project Token - keep this safe and do not share! Use 'load' to use previously saved Exporter. Otherwise, use full Token to load new Exporter.")
  parser.add_argument('-D', '--DefaultFields', required=True, nargs='+', help="enter fields that should be included in each dataset. E.g. '-d subid group' ")
  parser.add_argument('-F', '--Form', required=False, help="name of form to export. If metadata is exported, metadata for the requested form is exported. Use 'all' to export all forms. For longitudinal projects, the form may not be formatted as desired. You may want to use Event instead.")
  parser.add_argument('-M', '--Metadata', action='store_true', required=False, help='export project metadata')
  parser.add_argument('-V', '--Variable', required=False, help='export single variable. For longitudinal projects, this can be a repeated variable.')
  parser.add_argument('-L', '--Long', action='store_true')
  return parser.parse_args()

args = parseArgs() 

#load exporter
if args.Token == 'load':
  exporter = load('./Exports/previous_exporter')
else:
  exporter = REDCapExporter(args.Token, common_fields=args.DefaultFields)

#make sure storage folders are available
project_title = exporter.project_info['project_title']
if not os.path.exists(f'./Exports/{project_title}'):
  cwd = os.getcwd()
  project_dir = cwd + '/Exports/' + project_title
  os.mkdir(project_dir)
  os.mkdir(project_dir + '/metadata')
  os.mkdir(project_dir + '/forms')
  os.mkdir(project_dir + '/exporter')
  if exporter.is_longitudinal:
    os.mkdir(project_dir + '/repeated_events')

if args.Metadata:
  if args.Form:
    metadata = exporter.metadata[exporter.metadata['form_name']==args.form]
    metadata.to_excel(f'./Exports/{project_title}/metadata/{args.form}_metadata.xlsx', index=False)
  exporter.metadata.to_excel(f'./Exports/{project_title}/metadata/all_metadata.xlsx', index=False)
elif args.Form:
  if args.Form == 'all':
    exporter.export_forms_to_excel(f'./Exports/{project_title}/forms/')
  else:
    form = exporter.export_forms([args.form])
    form.to_excel(f'./Exports/{project_title}/forms/{args.form}.xlsx', index=False)

with open(f'Exports/previous_exporter', 'wb') as file:
    pickle.dump(exporter, file)

