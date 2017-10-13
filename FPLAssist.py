import urllib.request
import json
import re
import io
#from bs4 import BeautifulSoup
import os
i=1
#Open the player file and make it writable
myfile=open("player_history.txt","w")
myfile.close()
#Open file for all the members for which there was error
errorFile=open("errorfile.txt","w")
errorFile.close()
#Website from which to scrape
while i<700:
	with urllib.request.urlopen("http://fantasy.premierleague.com/drf/element-summary/" + str(i)) as url:
		htmltext=url.read();
	#Use a try-except block to ignore htmls that do not relate to players
	try:
		#Using the json command to read the json file
		data=json.load(htmltext)
		#Extracting the score history
		scoredata=data["fixture_history"]["all"]
		#Extracting team
		teamname=data["team_name"]
		#Extracting player names
		playerdata=data["first_name"]+" "+["second_name"]
		#Extarct player positions
		playerposition=data["type_name"]
		#Extarzct the player price
		playerprice=data["event_cost"]
		#Percentage selected 
		selected=data["selected_by"]
		myfile=io.open("player_history.txt","a",encoding='utf8')
		#Appending the data to the file
		for datapoint in scoredata:
			mystring=str(datapoint)
			#Clean the data strings
			mystring1 = mystring.replace("[", "")
			mystring2 = mystring1.replace("u'", "")
			mystring3 = mystring2.replace("]", "")
			mystring4 = mystring3.replace("'", "")
			#Write the data to the file
			myfile.write(mystring4 + "," + playerdata + "," + teamname + "," + position +"," + selected + "," + str(price) + ',' + str(i) + "\n")
	except:
		#Writing all of the numbersfor which there was an error thrown
		errorFile=open("errorfile.txt","a")
		errorFile.write(str(i)+"\n")
		pass
	print (i)
	i+=1
print ("Player Data Scraped")

#Extract all of the fixtures and result info from the website

base="http://fantasy.premierleague.com/fixtures/"	#CHECK LINK
#Create a loop to run through 38 gameweeks
week=1
fix_file=open('fixtures.txt','w')
while week<39
	myurl = base + str(week)
	html = urllib.urlopen(myurl).read()
	soup = BeautifulSoup(html)
	fixture_table = soup.find("table", {"class":"ismFixtureTable"})
	#scrape the website for the games played and points
	hometeam = soup.findAll("td", {"class":"ismHomeTeam"})
	awayteam = soup.findAll("td", {"class":"ismAwayTeam"})
	score = soup.findAll("td", {"class":"ismScore"})
	i=0
	#Keep looping until code fails
	while True:
		try:
			fix_file.write(str(week) + ',' + hometeam[i].text + ',' + score[i].text + ',' +awayteam[i].text.strip() + ',' + '\n')
			i+=1
		
		except:
			break
	print week
	week+=1
fix_file.close()

print "Fixture Data Scraped"

#Extract the league table from the website

base = "http://fantasy.premierleague.com/transfers/"
html = urllib.urlopen(base).read()
soup = BeautifulSoup(html)

#scrape the website for the games played and points

games_played = soup.findAll("td", {"class":"col-pld"})
points = soup.findAll("td", {"class":"col-pts"})

#create an empty list for team names

team = []

#Find all of the team names and append them to the list

for text in soup.find_all('table', {"class":'leagueTable'}):
	for links in text.find_all('a'):
		team.append(links.text.strip())
league_table = open("league_table.txt", "w")
league_table.close()

league_table = open("league_table.txt", "a")

#print out the league table

i=0
while i < 20:
	league_table.write(str(i+1) + "," + team[i] + "," + games_played[i].text + "," + points[i].text + "\n")
	i+=1
league_table.close()

print "League Table Scraped"
print "ALL DATA SCRAPED"






