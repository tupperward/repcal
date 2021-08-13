import urllib.request, json, os
from dbTools import selectStatement, engine, calendar
from sqlalchemy import select, and_
# This class creates a python object with attributes that match the values of today's 
class DateObject:

  # Some quick variables to clean up what each attribute will be calling
  repcalData = 'https://repcal.info/now.json'
  rd = 'republican_date'
  a = 'attributes'
  userDomain = os.environ.get('DOMAIN')
  
  # Makes the HTTP request to pull raw json data
  def getJsonData(self,api):
    with urllib.request.urlopen(api) as url:
      data = json.loads(url.read())
      return data

  # When a new date object is created it will self-populate accurate information from the json
  def __init__(self):

    # THIS EXISTS SO WE ONLY MAKE THE REQUEST ONCE 
    # Do not just call getJsonData() a half dozen times because it will take forever
    jsonData = self.getJsonData(self.repcalData)
    getItemFromDb = select(calendar.columns.item).where(and_(calendar.columns.month == self.month,calendar.columns.day == self.day))
    getUrlFromDb = select(calendar.columns.item_url).where(and_(calendar.columns.month == self.month,calendar.columns.day == self.day))

    self.day = jsonData[self.rd][self.a]['day']
    self.week = jsonData[self.rd][self.a]['week']
    self.weekday = jsonData[self.rd][self.a]['weekday'].strip("('").strip("'),")
    self.month = jsonData[self.rd][self.a]['month'].strip("('").strip("'),")
    self.yearArabic = jsonData[self.rd][self.a]['year_arabic']
    self.yearRoman = jsonData[self.rd][self.a]['year_roman'].strip("('").strip("'),")
    self.sansculottides = jsonData[self.rd][self.a]['sansculottides']
    self.formatted = jsonData[self.rd]['formatted'].strip("('").strip("'),"),
    self.item = selectStatement(getItemFromDb),
    self.item_url = selectStatement(getUrlFromDb),
    self.image = 'http://{domain}/i/{month}{day}.png'.format(domain = self.userDomain,month = self.month, day = self.day).strip("('").strip("'),"),
    self.time = jsonData['standard']['formatted']

