from flask import Flask
import pathlib, socket, genRSS, asyncio, datetime
from time import sleep
from dateObject import DateObject


async def dataUpdater():
  try:
    f = open('rss.xml','r')
    thumbprint = genRSS.generateThumbprint()
    print('Less of a champion')
  except FileNotFoundError:
      print('You champion')
      genRSS.addEntryToFeed()
      thumbprint = genRSS.renewRssFile()
      
  confirmThumb = genRSS.addEntryToFeed()

  if thumbprint == confirmThumb:
    print('waiting')
    await asyncio.sleep(1)
  else:
    print('updating')
    genRSS.renewRssFile()
    await asyncio.sleep(1)

async def main():
  genRSS.initFeed()
  asyncio.create_task(dataUpdater())
  
  
def getIpAddress():
  #From https://stackoverflow.com/a/166589/379566
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  return s.getsockname()[0]

IMAGE_DIR = '/i/'
SERVER_HOME = 'http://{}'.format(getIpAddress())

app = Flask(__name__)

if __name__ == "__main__":
  asyncio.run(main())