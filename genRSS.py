from dateObject import Top10, carpeDiem, addDayToTop10, upkeepTop10, db, touch
from flask_sqlalchemy import SQLAlchemy
from os.path import exists
from feedgen.feed import FeedGenerator
import os

# Creating the today object by seizing the day
today = carpeDiem()

#Create the feed generator
fg = FeedGenerator()

domain = os.environ.get('DOMAIN')
if domain == None:
  domain = 'localhost'

port = os.environ.get('PORT')
if port == None:
  port = '6942'

def main():
  upkeepTop10()
  addDayToTop10(today)

  if not exists('./static/atom.xml'):
    fg.id('6942')
    fg.author(name='tupperward', email='tupperward@gmail.com')
    fg.title('French Republican Calendar RSS')
    fg.subtitle('The vulgar era is abolished for civil usage.')
    fg.description('A small feed-style daily calendar inspired by twitter user @sansculotides')
    fg.link(href='test')
    fg.skipHours(12)

    for i in range (0,10):
      row = db.session.query(Top10).filter_by(index=i).first()
      if not row == None:
        stamp = "{}_{}_{}".format(row.yearArabic,row.month,row.day)
        fe = fg.add_entry()
        fe.id(id=stamp)
        fe.title(row.formatted)
        fe.link(href='http://{domain}:{port}/images/{image}.jpg'.format(domain = domain, port = port, image = row.image), rel='alternate')
        fe.published(row.pub_date)
        fe.content('Today is {day} {month}, the month of {month_of}. Today celebrates {item}. You can learn more about {item} here: {item_url}'.format(day=row.day, month=row.month, month_of=row.month_of, item=row.item, item_url=row.item_url))
    
    fg.atom_file('./static/atom.xml', pretty=True)
  else:
    os.remove('./static/atom.xml')
    main()
      

if __name__ == "__main__":
  main()