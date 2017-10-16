import csv
import MySQLdb
filename = ""
mydb = MySQLdb.connect(host='localhost',
    user='root', #insert your MySQL user
    passwd='', 
    db='mydb')
cursor = mydb.cursor()

csv_data = csv.reader(file('filename'))
for row in csv_data:
    cursor.execute('INSERT INTO table_name (id,name,rank,city,region,stadium)' \
          'VALUES("%d", "%s", "%d","%s","%s","%s")', 
          row)
#close the connection to the database.
mydb.commit()
cursor.close()
print "Done"
