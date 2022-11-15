import re
import requests
import pandas as pd

class redcapApiConfiguration:
  def __init__(self, token):
    self.token = token
    self.form_request = {
      'content': 'instrument',
    }
    self.all_data_request = {
      'content': 'record',
      'type': 'flat',
      'csvDelimiter': '',
      'rawOrLabel': 'raw',
      'rawOrLabelHeaders': 'raw',
      'exportCheckboxLabel': 'false',
      'exportSurveyFields': 'false',
      'exportDataAccessGroups': 'false',
    }
    self.metadata_request = {
      'content': 'metadata',
    }
    self.field_names_request = {
      'content': 'exportFieldNames',
    }
    self.events_request = {
      'content': 'formEventMapping'
    }
    self.project_info_request = {
      'content': 'project'
    }
    self.instruments_request = {
      'content': 'instrument'
    }
    self.repeated_forms_events_request = {
      'content': 'repeatingFormsEvents'
    }
    self.arms_request = {
      'content': 'arm'
    }

  def post(self, request_data, data_format):
    try:
      formUrlEncodedData = {
        'token': self.token,
        'format': data_format,
        'returnFormat': 'json',
        **request_data
      }
      response = requests.post('https://redcap.uchicago.edu/api/', formUrlEncodedData)
      return response

    except KeyError as e:
      print(e)

  def export(self, request_data, data_format = 'json'):
    response = self.post(request_data, data_format)
    response = response.json()
    return response

  def get_response_as_dataframe(self, request_data, sort_column=None):
    response = self.export(request_data)
    dataframe = pd.DataFrame(response)
    if sort_column:
        dataframe = dataframe.sort_values(by=sort_column)
    return dataframe
