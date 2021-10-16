from flask import Flask, render_template, request, url_for
from flask.helpers import send_from_directory
from unidecode import unidecode
import dateObject

app = Flask(__name__)

@app.route('/feed/')
def feed():
  return render_template('atom.xml')

@app.route('/images/')
def image():
  today = dateObject.carpeDiem()
  month = unidecode(today.month).lower()
  item = today.item.lower()
  #return send_from_directory('./static/images/{}'.format(unidecode(today.month).lower()), '{}.jpg'.format(today.item.lower()))
  return render_template('image.html', month=month, item=item)

if __name__ == "__main__":
  #today = dateObject.carpeDiem()
  app.run(debug=True, host="0.0.0.0", port=6942)

#IMAGE_DIR = '/images/'
#SERVER_HOME = 'http://{}'.format(getIpAddress())

#app = Flask(__name__)

