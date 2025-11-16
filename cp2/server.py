from flask import Flask, request
import json

from segmentJson import filterData

SERVER_PORT = 54011
DATA_FILEPATHS = ['./data/set1/data-10.json']
DATA = []
for filepath in DATA_FILEPATHS:
  with open(filepath, 'r') as f:
    try:
      data = json.load(f)
      DATA.append(data)
    except json.JSONDecodeError as e:
      print(f"Error decoding JSON data from {filepath}: {e}")

#print(DATA)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
  return "<p>Hello, World!</p>"

@app.route("/data", methods=['GET'])
def get_data():
  if not request.args:
    return DATA
  else:
    month = request.args.get('m', 0, type=int)
    day = request.args.get('d', 0, type=int)
    year = request.args.get('y', 0, type=int)
    interface = request.args.get('if', 'any', type=str)
    direction = request.args.get('dir', 'any', type=str)
    print(month, day, year, interface, direction)
    filteredData = []
    for dataSet in DATA:
      filteredData.append(list(filter(lambda entry: filterData(entry, month, day, year,
                                                               interface, direction),
                                                               dataSet)))
    return filteredData

@app.route("/dl/stat/mean", methods=['GET'])
def get_mean():
  pass

@app.route("/dl/stat/peak", methods=['GET'])
def get_peak():
  pass

if __name__ == '__main__':
  app.run(port=SERVER_PORT)