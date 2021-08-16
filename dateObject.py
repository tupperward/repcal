import urllib.request, json, os
from sqlalchemy.sql.expression import insert, update
from sqlalchemy.sql.type_api import UserDefinedType
from dbTools import selectStatement,executeStatement,calendar, lastPost
from sqlalchemy import exc, select, and_
# This class creates a python object with attributes that match the values of today's 
class DateObject:

  # Some quick variables to clean up what each attribute will be calling
  repcalData = 'https://repcal.info/now.json'
  rd = 'republican_date'
  a = 'attributes'
 
  
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

    self.day = jsonData[self.rd][self.a]['day']
    self.week = jsonData[self.rd][self.a]['week']
    self.weekday = jsonData[self.rd][self.a]['weekday'].strip("('").strip("'),")
    self.month = jsonData[self.rd][self.a]['month'].strip("('").strip("'),")
    self.yearArabic = jsonData[self.rd][self.a]['year_arabic']
    self.yearRoman = jsonData[self.rd][self.a]['year_roman'].strip("('").strip("'),")
    self.sansculottides = jsonData[self.rd][self.a]['sansculottides']
    self.formatted = jsonData[self.rd]['formatted'].strip("('").strip("'),"),
    self.time = jsonData['standard']['formatted']

def carpeDiem():
  today = DateObject()
  userDomain = os.environ.get('DOMAIN_REMOTE')
  statement = calendar.select().where(calendar.c.month.ilike(today.month), calendar.c.day == today.day)
  query = selectStatement(statement)
  today.item = query.item
  today.item_url = query.item_url 
  today.image = 'http://{domain}/images/{month}/{item}.jpg'.format(domain = userDomain, month = today.month, item = today.item)
  return today

def generateThumbprint():
  thumbprint = carpeDiem().formatted
  return thumbprint

def checkDate():
  thumbprint = generateThumbprint()
  queryDate = lastPost.select().where(lastPost.c.id == 1)
  updateDate = lastPost.update().where(lastPost.c.id ==1).values(lastPost = thumbprint)
  insertDate = lastPost.insert().values(id=1, lastPost=thumbprint)
  
  dateCheck = selectStatement(queryDate)
  print (dateCheck)
  if thumbprint == dateCheck:
    print ("------------------------------Nailed it cowboy------------------------------")
  else: 
    executeStatement(updateDate)
    print("------------------------------Wrote new Date------------------------------")

    #executeStatement(insertDate)
    #print("Inserted date")

checkDate()