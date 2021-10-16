from flask import Flask, render_template, request, url_for, send_from_directory
from unidecode import unidecode
from dateObject import db
import os

app = Flask(__name__, static_url_path='/')

port = os.environ.get('PORT')
if port == None:
  port = 8080

@app.route('/feed')
def feed():
  return send_from_directory(app.static_folder, request.path[1:])

@app.route('/images/<image>')
def image(image):
  return send_from_directory(app.static_folder, request.path[1:])

if __name__ == "__main__":
  #today = dateObject.carpeDiem()
  app.run(debug=True, host="0.0.0.0", port=port)

#IMAGE_DIR = '/images/'
