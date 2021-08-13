from flask import Flask
import genRSS, asyncio, datetime, nest_asyncio
from time import sleep
from dateObject import DateObject

nest_asyncio.apply()

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
    print('----- Waiting for update to repcal feed -----')
    print(datetime.now())
    await asyncio.sleep(3600)
  else:
    print('------------- UPDATING RSS.XML --------------')
    genRSS.renewRssFile()
    await asyncio.sleep(5)
  
  await dataUpdater()

async def main():
  genRSS.initFeed()
  updateTask = asyncio.create_task(dataUpdater())
  loop = asyncio.get_event_loop()
  await loop.run_forever()
  await updateTask
  
if __name__ == "__main__":
  asyncio.run(main())

#IMAGE_DIR = '/images/'
#SERVER_HOME = 'http://{}'.format(getIpAddress())

#app = Flask(__name__)

