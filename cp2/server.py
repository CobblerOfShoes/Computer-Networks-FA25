from flask import Flask, request
import json

from segmentJson import filterData
from dataStatistics import dailyMeans, dailyPeaks

SERVER_PORT = 54011
DATA_FILEPATHS = ['./data/set1/data-all.json']
DATA = []
for filepath in DATA_FILEPATHS:
  with open(filepath, 'r') as f:
    try:
      data = json.load(f)
      DATA.extend(data)
    except json.JSONDecodeError as e:
      print(f"Error decoding JSON data from {filepath}: {e}")

#print(DATA)

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
  return "<p>Hello, World!</p>"

### Retrieve data from the server
# The following queries are acceptable:
#   localhost
@app.route("/data", methods=['GET'])
def get_data():
  if not request.args:
    return DATA
  else:
    month = request.args.get('m', 0, type=int)
    day = request.args.get('d', 0, type=int)
    year = request.args.get('y', 0, type=int)
    interface = request.args.get('if', 'any', type=str)
    direction = 'downlink' # This endpoint is only for downlink statistics
    #print(month, day, year, interface, direction)
    filteredData = list(filter(lambda entry: filterData(entry, month, day, year,
                                                        interface, direction),
                                                        DATA))
    return filteredData

@app.route("/dl/stat/mean", methods=['GET'])
def get_mean():
  if not request.args:
    return dailyMeans(DATA)
  else:
    month = request.args.get('m', 0, type=int)
    day = request.args.get('d', 0, type=int)
    year = request.args.get('y', 0, type=int)
    interface = request.args.get('if', 'any', type=str)
    direction = 'downlink' # This endpoint is only for downlink statistics
    #print(month, day, year, interface, direction)
    filteredData = list(filter(lambda entry: filterData(entry, month, day, year,
                                                        interface, direction),
                                                        DATA))
    return dailyMeans(filteredData)

@app.route("/dl/stat/peak", methods=['GET'])
def get_peak():
  if not request.args:
    return dailyPeaks(DATA)
  else:
    month = request.args.get('m', 0, type=int)
    day = request.args.get('d', 0, type=int)
    year = request.args.get('y', 0, type=int)
    interface = request.args.get('if', 'any', type=str)
    direction = request.args.get('dir', 'any', type=str)
    #print(month, day, year, interface, direction)
    filteredData = list(filter(lambda entry: filterData(entry, month, day, year,
                                                        interface, direction),
                                                        DATA))
    return dailyPeaks(filteredData)

if __name__ == '__main__':
  app.run(port=SERVER_PORT, host="0.0.0.0")