from dateObject import Top10, carpeDiem, addDayToTop10, upkeepTop10, db, touch
from flask_sqlalchemy import SQLAlchemy
from os.path import exists
from feedgen.feed import FeedGenerator
import os

# Creating the today object by seizing the day
today = carpeDiem()

#Create the feed generator
fg = FeedGenerator()

domainName = os.environ.get('DOMAIN_NAME')
if domainName == None:
  domainName = 'localhost'

def createFeed():
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
      fe.published(row.pub_date)
      fe.content(content='Today is {day} {month}, the month of {month_of}, celebrating {item}. You can learn more about {item} here: {item_url}'.format(day=row.day, month=row.month, month_of=row.month_of, item=row.item, item_url=row.item_url))
  
  fg.atom_file('./static/atom.xml', pretty=True)

def main():
  if not exists('./static/atom.xml'):
    createFeed()
  else:
    os.remove('./static/atom.xml')
    main()

if __name__ == "__main__":
  main()