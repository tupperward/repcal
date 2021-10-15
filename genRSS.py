from dateObject import carpeDiem, 
from os.path import exists
from feedgen.feed import FeedGenerator
import os, xml
from copy import copy, deepcopy

# Creating the today object by seizing the day
today = carpeDiem()

#Create the feed generator
fg = FeedGenerator()





def main():
  if not exists('atom.xml'):
    fg.author('tupperward')
    fg.title('French Republican Calendar RSS')
    fg.subtitle('The vulgar era is abolished for civil usage.')
    fg.description('A small feed-style daily calendar inspired by twitter user @sansculotides')
    fg.link(href='test')

    fe = fg.add_entry()
    fe.id(id='{year}_{month}_{day}'.format(year=today.yearArabic, month=today.month, day=today.day))
    fe.title('')

    assert len(fg.entry() == 11)
    fg.remove_entry(10)
    
    

    return
  else: 
    if not exists('atom.xml'):
      return

if __name__ == "__main__":
  main()