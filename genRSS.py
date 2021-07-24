from dateObject import DateObject
from feedgen.feed import FeedGenerator

# Instantiate data for today, should be executed via cronjob once every 4 hours
today = DateObject()

#Create the feed generator
fg = FeedGenerator()

# Cleaning up some of the weird formatting from the DateObject
guid = "{}".format(today.guid).replace(".","_")
imageUrl = "{}".format(today.image).strip("('").strip("',)")

# Instantiate the feed with attributes
def initFeed():
  fg.id('https://repcal.tupperward.net/')
  fg.title('Republican Calendar RSS')
  fg.author({'name':'tupperward', 'email':'tupperward@gmail.com'})
  fg.language('en')
  fg.link( href='https://repcal.tupperward.net/')
  fg.description('The vulgar era is abolished for civil usage.')
  fg.skipHours(hours=8,replace=False)

#Add an item to the feed
def addEntryToFeed():
  fe = fg.add_entry()
  fe.id(guid)
  fe.title("Today is {weekday} the {day} of {month} celebrating {thing}.".format(weekday = today.weekday, day = today.day, month = today.month, thing = today.thing))
  fe.link(href=imageUrl, rel="self")
  fe.enclosure(url=imageUrl, type='image/png')

# Generate an rss.xml file that is overwritten each time. Hopefully your reader keeps data locally I guess. But it's also a daily calendar so fuck you too.
def renewRssFile():
  fg.rss_file('rss.xml')