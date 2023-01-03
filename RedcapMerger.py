import argparse
import pandas as pd
import os
from API.REDCap_Exporter import REDCapExporter
from API.REDCap_Merger import RedcapMerger
from Utils.load import load
import pickle

def parseArgs():
  parser = argparse.ArgumentParser(description='Merge data from two REDCap projects')
  parser.add_argument('-T1', '--Token1', required=True, help="Token of 1st REDCap Project. To load previous, write 'load'.")
  parser.add_argument('-T2', '--Token2', required=True, help="Token of 2nd REDCap Project. To load previous, write 'load'.")
  parser.add_argument('-F1', '--Form1', required=False, nargs='+', help="Form Names to be used for merge in 1st REDCap Project.")
  parser.add_argument('-F2', '--Form2', required=False, nargs='+', help="Form Names to be used for merge in 2nd REDCap Project.")
  parser.add_argument('-K1', '--Key1', required=False, help="Variable name to be used as Key in 1st REDCap Project")
  parser.add_argument('-K2', '--Key2', required=False, help="Variable name to be used as Key in 2nd REDCap Project")
  parser.add_argument('-C', '--Custom', required=False, help='Custom merge command. Order of REDCap Projects may be important.')
  parser.add_argument('-P', '--Pathway', required=False, help='Pathway to Excel document if used in custom merges.')
  parser.add_argument('-D1', '--DefaultFields1', required=True, nargs='+', help="enter extra fields that should be included in Form 1. (E.g. '-d subid group')")
  parser.add_argument('-D2', '--DefaultFields2', required=True, nargs='+', help="enter extra fields that should be included in Form 2. (E.g. '-d subid group')")
  return parser.parse_args()

args = parseArgs()

#load exporters
if args.Token1 == 'load':
  exporter1 = load('./Exports/previous_exporter1')
else:
  exporter1 = REDCapExporter(args.Token1, common_fields=args.DefaultFields1)
if args.Token2 == 'load':
  exporter2 = load('./Exports/previous_exporter2')
else:
  exporter2 = REDCapExporter(args.Token2, common_fields=args.DefaultFields2)

project_title1 = exporter1.project_info['project_title']
project_title2 = exporter2.project_info['project_title']
cwd = os.getcwd()
project_dir = f'{cwd}/Exports/Merges/{project_title1} {project_title2}'

if not os.path.exists(project_dir):
  os.mkdir(project_dir)

if args.Custom:
  if args.Custom == 'arrival':
    merger = RedcapMerger(exporter1, exporter2)
    merger.export_arrival_database(project_dir)

with open(f'Exports/previous_exporter1', 'wb') as file:
  pickle.dump(exporter1, file)
with open(f'Exports/previous_exporter2', 'wb') as file:
  pickle.dump(exporter2, file)

