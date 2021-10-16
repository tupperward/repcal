from dateObject import Top10, carpeDiem, addDayToTop10, upkeepTop10, db, touch
from flask_sqlalchemy import SQLAlchemy
from os.path import exists
from feedgen.feed import FeedGenerator
import os

# Creating the today object by seizing the day
today = carpeDiem()

#Create the feed generator
fg = FeedGenerator()

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

    for i in range (10,1,-1):
      row = db.session.query(Top10).filter_by(index=i).first()
      if not row == None:
        stamp = "{}_{}_{}".format(row.yearArabic,row.month,row.day)
        fe = fg.add_entry()
        fe.id(id=stamp)
        fe.title(row.formatted)
        fe.link(href=row.item_url, rel='alternate')
        fe.published(row.pub_date)
        fe.content('Today is {day} {month}, the month of {month_of}. Today celebrates the {item}'.format(day=row.day, month=row.month, month_of=row.month_of, item=row.item))
    
    fg.atom_file('./static/atom.xml', pretty=True)
  else:
    os.remove('./static/atom.xml')
    main()
      

if __name__ == "__main__":
  main()