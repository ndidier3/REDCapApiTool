import pickle
from datetime import date

def save(object, name):
  today = date.today()
  with open(f'exports/{name} {today}', 'wb') as file:
    pickle.dump(object, file)
  return f'exports/{name} {today}'
