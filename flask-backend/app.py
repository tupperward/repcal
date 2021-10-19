from flask import Flask, request, send_from_directory
from flask_apscheduler import APScheduler
import os, genRSS
from os.path import exists


app = Flask(__name__, static_url_path='/')

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

@scheduler.task('cron', id='do_job_2', hour='0')
def job():
  genRSS.main()
  print('Job executed')

scheduler.start()

if not exists('./static/atom.xml'):
  genRSS.createFeed()

port = os.environ.get('PORT')
if port == None:
  port = 8080

@app.route('/api')
def json():
  return genRSS.createJsonString()

@app.route('/feed')
def feed():
  return send_from_directory(app.static_folder, request.path[1:])

@app.route('/images/<image>')
def image(image):
  return send_from_directory(app.static_folder, request.path[1:])

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=port)