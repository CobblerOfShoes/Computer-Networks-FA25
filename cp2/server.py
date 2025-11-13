from flask import Flask

SERVER_PORT = 54133
FILE_LIST = []

app = Flask(__name__)

@app.route("/")
def hello_world():
  return "<p>Hello, World!</p>"

@app.route("/data")
@app.route("/data/json")
def get_data_as_csv():
  pass

@app.route("/data/csv")
def get_data_as_csv():
  pass

@app.route("/dl/stat/mean")
def get_mean():
  pass

@app.route("/dl/stat/peak")
def get_peak():
  pass

if __name__ == '__main__':
  app.run(port=SERVER_PORT)