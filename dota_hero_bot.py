from bs4 import BeautifulSoup
import urllib2
from lxml.html import parse
import re
import praw
import pickle
#SUBMISSION_ID = '2v2zc8'


def is_hero(hero, heroes):
	hero = hero.lower().strip()
	
	for line in heroes:
		line = line.lower().strip()
		if hero == line:
			print "Hero found " + line
			return True
	return False


def get_hero_infobox_reply(hero):
	
    wiki = "http://dota2.gamepedia.com/" + hero
    header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
    req = urllib2.Request(wiki,headers=header)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page)
    
    table = soup.find("table", { "class" : "infobox" })
    
    data = []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    
    
    heroName =  data[0][0]
    baseAttr =     data[3][0]
    baseAttr = baseAttr.split('\n\n')
    baseStr = baseAttr[0].replace(" ", "")
    baseAgi = baseAttr[1].replace(" ", "")
    baseInt = baseAttr[2].replace(" ", "")
    
    hp =        data[7]
    mana =      data[8]
    damage =    data[9]
    armor =     data[10]
    attacks =   data[11]
    ms =        data[13][1]
    turnRate =  data[14][1]
    sightRng =  data[15][1]
    attackRng = data[16][1]
    missleSpd = data[17][1]
    atkDur  =   data[18][1]
    castDur =   data[19][1]
    baseAtkTime=data[20][1]
    colSize =   data[21][1]

    reply = ""
    reply += "**" + heroName + "**\n\n"
    reply += str.format("Base strength: **{0}**\n\nBase Agility: **{1}**\n\nBase Inteligence: **{2}**\n\n", baseStr, baseAgi, baseInt)

    reply += "Level|1|16|25\n"
    reply += ":--|:--|:--|:--\n"
    reply += str.format("Hit Points|{0}|{1}|{2}\n",  hp[1], hp[2], hp[3])
    reply += str.format("Mana|{0}|{1}|{2}\n",  mana[1], mana[2], mana[3])
    reply += str.format("Armor|{0}|{1}|{2}\n",  armor[1], armor[2], armor[3])
    reply += str.format("Attacks/second|{0}|{1}|{2}\n",  attacks[1], attacks[2], attacks[3])

    reply +="\n\n"

    reply += str.format("Attribute|Value\n")
    reply += str.format(":--|:--\n")
    reply += str.format("Movement Speed|{0}\n", turnRate)
    reply += str.format("Turn Rate|{0}\n", ms)
    reply += str.format("Sight Range|{0}\n", sightRng)
    reply += str.format("Attack Range|{0}\n", attackRng)
    reply += str.format("Missle Speed|{0}\n", missleSpd)
    reply += str.format("Attack Duration|{0}\n", atkDur)
    reply += str.format("Cast Duration|{0}\n", castDur)
    reply += str.format("Base Attack Time|{0}\n", baseAtkTime)
    reply += str.format("Collision Size|{0}\n", colSize)

    return reply

#Logging into Reddit
r = praw.Reddit(user_agent='/u/dotaherobot by /u/GreenyGaming at /r/dotaherobot v1.0.0')
r.login('dotaherobot', 'uX9ji3gTt8Lb')

#Loading the set with the submissions, that are already commented on, to avoid duplicates
already_done_file = open("already_done", "r+")
already_done = set()
already_done = pickle.load(already_done_file)

#Loading specific submission, for testing purposes
#Script can run on specific subreddit or on the whole site (with certain restrictions)

submission = r.get_submission(submission_id='2v30z4')
flat_comments = praw.helpers.flatten_tree(submission.comments)

hero_list = open("dota_heroes.txt", "r")

for comment in flat_comments:
    if any(string in comment.body for string in ['dota2.gamepedia.com']) and comment.id not in already_done:
        commentStr = str(comment.body)
        
        #Finding the hero name in the comment body
        article = commentStr.split("dota2.gamepedia.com/", 1)[1]
        article = re.sub('[\'\"]', "", article)
        
        #determine if the shared article is a hero
        if is_hero(article, hero_list):
        	reply = get_hero_infobox_reply(article)
        	comment.reply(reply)
        	already_done.add(comment.id)
        	
pickle.dump(already_done, already_done_file)
already_done_file.close()        	

hero_list.close()





