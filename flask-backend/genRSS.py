from dateObject import Top10, carpeDiem, addDayToTop10, upkeepTop10, db
from os.path import exists
from feedgen.feed import FeedGenerator
from unidecode import unidecode
import os, json

domainName = os.environ.get('DOMAIN_NAME')
if domainName == None:
  domainName = 'localhost'

def createJsonString():
  jsonDict = {}
  for i in range (0):
    row = db.session.query(Top10).filter_by(index=i).first()
    if not row == None:
      day = {
        "index":row.index,
        "day":row.day,
        "week":row.week,
        "month":unidecode(row.month),
        "month_of":row.month_of,
        "yearArabic":row.yearArabic,
        "yearRoman":row.yearRoman,
        "formatted":unidecode(row.formatted),
        "item":row.item,
        "item_url":row.item_url,
        "image":'http://{}/images/{image}.jpg'.format(domainName, image = row.image)
      }
      jsonDict["day_{}".format(i)] = day
  return json.dumps(jsonDict)

def createFeed():
  today = carpeDiem()

  fg = FeedGenerator()

  upkeepTop10()
  addDayToTop10(today)
  
  fg.id('repcalRSS')
  fg.author(name='tupperward', email='tupperward@gmail.com')
  fg.title('French Republican Calendar RSS')
  fg.subtitle('The vulgar era is abolished for civil usage.')
  fg.description('A small feed-style daily calendar inspired by twitter user @sansculotides')
  fg.link(href='http://repcalrss.tupperward.net/atom.xml')
  fg.skipHours(12)
  for i in range (10,0, -1):
    row = db.session.query(Top10).filter_by(index=i).first()
    if not row == None:
      fe = fg.add_entry()
      fe.id(str(row.index))
      fe.title(row.formatted)
      fe.link(href='http://{}/images/{image}.jpg'.format(domainName, image = row.image), rel='alternate')
      fe.content(content='Today is {day} {month}, the month of {month_of}, celebrating {item}. You can learn more about {item} here: {item_url}'.format(day=row.day, month=row.month, month_of=row.month_of, item=row.item, item_url=row.item_url))
  
  fg.atom_file('./static/atom.xml', pretty=True)
  fg = None

def main():
  if not exists('./static/atom.xml'):
    createFeed()
  else:
    os.remove('./static/atom.xml')
    main()

if __name__ == "__main__":
  main()