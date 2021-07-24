from flask import Flask
import pathlib, socket, genRSS
from time import sleep

genRSS.initFeed()
async def updateFeed():
  genRSS.addEntryToFeed()
  genRSS.renewRssFile()
  sleep(7200)

def getIpAddress():
  #From https://stackoverflow.com/a/166589/379566
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  return s.getsockname()[0]

IMAGE_DIR = '/i/'
SERVER_HOME = 'http://{}'.format(getIpAddress())

app = Flask(__name__)
