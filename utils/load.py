import pickle

def load(filename):
  with open(filename, 'rb') as file:
      object = pickle.load(file)
      return object