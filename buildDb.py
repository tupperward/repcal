import sqlite3, csv
from sqlite3.dbapi2 import Error
from dateObject import DateObject

today = DateObject()
con = sqlite3.connect('calendar.db')

def createTable(con,statement):
  try:
    cur = con.cursor()
    cur.execute(statement)
    con.commit()
  except Error as e:
    print(e)


def select_row_by_requirements(con,currentMonth,currentDay):

  cur = con.cursor()
  cur.execute('SELECT * FROM calendardata WHERE month={month} AND day={day}'.format(month=currentMonth,day=currentDay))
  row = cur.fetchall()

  return row

vendemiare = "CREATE TABLE IF NOT EXISTS Vendémiaire (month_of,day,item,item_url);"
brumaire = "CREATE TABLE IF NOT EXISTS Brumaire (month_of,day,item,item_url);"
frimaire = "CREATE TABLE IF NOT EXISTS Frimaire (month_of,day,item,item_url);"
nivose = "CREATE TABLE IF NOT EXISTS Nivôse (month_of,day,item,item_url);"
pluviose = "CREATE TABLE IF NOT EXISTS Pluviôse (month_of,day,item,item_url);"
ventose = "CREATE TABLE IF NOT EXISTS Ventôse (month_of,day,item,item_url);"
germinal = "CREATE TABLE IF NOT EXISTS Germinal (month_of,day,item,item_url);"
floreal =  "CREATE TABLE IF NOT EXISTS Floréal (month_of,day,item,item_url);"
prairial = "CREATE TABLE IF NOT EXISTS Prairial (month_of,day,item,item_url);"
messidor = "CREATE TABLE IF NOT EXISTS Messidor (month_of,day,item,item_url);"
thermidor = "CREATE TABLE IF NOT EXISTS Thermidor (month_of,day,item,item_url);"
fructidor = "CREATE TABLE IF NOT EXISTS Fructidor (month_of,day,item,item_url);"
sans = "CREATE TABLE IF NOT EXISTS Sansculottides (month_of,day,item,item_url);"

list = [vendemiare,brumaire,frimaire,nivose,pluviose,ventose,germinal,floreal,prairial,messidor,thermidor,fructidor,sans]

for i in list:
  createTable(con,i)
con.close()