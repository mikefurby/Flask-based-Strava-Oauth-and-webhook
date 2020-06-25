#!/usr/bin/python3
from sys import argv
from datetime import date, datetime
import requests
import csv
import os
import json
import time

script, club = argv

expiry_limit = 2000 #running 2 times per hour now. Strava allows refresh for tokens with 3600s or less. I do 4000 in case the refres
h app is slower than 400s
### it appears that token refresh does not count against daily quota, so constant refresh is fine.

filepath = ("/home/ubuntu/Strava/") 
tokenfile = (filepath + club + "/tokenfiles/strava_tokens.csv")
temptokenfile = (filepath + club + "/tokenfiles/temp_strava_tokens.csv")
todayunformat=date.today()
today=todayunformat.strftime("%d %b %Y")
archivetokenfilejson = (filepath + club + "/tokenfiles/archive/strava_tokens.json_" + str(today))
archivetokenfilecsv = (filepath + club + "/tokenfiles/archive/strava_tokens.csv_" + str(today))
logfile = (filepath + club + "/tokenfiles/logfile.txt")
configfile = (filepath + club + "/config.json")
refreshtokenfile = (filepath + club + "/tokenfiles/last_refreshed_strava_token.json")
newauthtokenfile = (filepath + club + "/tokenfiles/new_auth_strava_token.csv")


def refresh():
##first make a copy of the strava token file
    with open (tokenfile) as r:
        lines = r.readlines()
    with open (temptokenfile,"w") as w:
        for line in lines:
            w.write(line)
###then proceed
    atf = open(archivetokenfilejson,'w')
    with open (tokenfile) as tf:
        data = csv.DictReader(tf)
        for athlete in data:
            print ("Athlete: " + str(athlete))
            print (athlete)
            athleteid=(athlete['id'])
            expires=(athlete['token_expiry'])
            rtoken=(athlete['refresh_token'])
            print (expires,rtoken)
            current_epoch=(time.time())
            expired=(int(expires)-int(current_epoch))
            print ('expired?:',expired)
            if (expired) < (expiry_limit):
                print('Will expire soon, so refresh now\n')
                get_refresh_token(rtoken,athlete)
                #log_this(": Token refreshed %s \n" % str(athlete['id']))
            else:
                print('Not yet expired\n')
                #log_this(": No change %s \n" %  str(athlete['id']))
            atf.write(str(athlete))
            atf.write("\n")
    atf.close()
###now copy temp file to main file and add any new athletes that may have been authed during this process
    with open (temptokenfile) as r:
        lines = r.readlines()
    with open (newauthtokenfile) as nr:
        newlines = nr.readlines()
        data = csv.reader(nr)
        athleteidcheck=[]
        for line in data:
            athleteid=line[0]
            athleteidcheck.append(athleteid)
    with open (tokenfile,"w") as w:
        for line in lines:
            w.write(line)
        count=0
        for line in newlines:
          if (count) == 0:
            count+=1
          else:
            if athleteidcheck[(count)] not in lines:
              w.write(line)


###the newly authorised athlete may now be in twice, but the next run of this script will remove it
    open (newauthtokenfile,'w').close() ##once we've read the new auth file, we clear it.


def log_this(message):
    now = datetime.now()
    with open (logfile,"a") as lf:
        print ("debug: logging now from token_refresh.py")
        lf.write(str(now) + (message))
    lf.close()

def get_refresh_token(rtoken,athlete):
    print ("debug: this is the start of get_refresh")
    print ("debug: configfile=",configfile)
    with open (configfile) as c:
        clientinfo = json.load(c)
    CLIENT_ID = (clientinfo["CLIENT_ID"])
    CLIENT_SECRET = (clientinfo["CLIENT_SECRET"])
    print ("debug:",CLIENT_ID,CLIENT_SECRET)
    athleteid=(int(athlete['id']))
    post_data = {"grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": rtoken
        ,}
    print (post_data)
    response = requests.post("https://www.strava.com/api/v3/oauth/token",
        post_data)
    token_json = response.json()
    with open (refreshtokenfile,"w") as ctf:
        json.dump(token_json,ctf)
    ctf.close()
    print ("new token.....\n")
    print (str(token_json))
###check that app is authorised, else this prog will crash.
    try:
        print (token_json["access_token"])
        print ('ok, app still authorised')
        shallwecontinue=1
    except:
        print (token_json)
        print ('app not authorised')
        shallwecontinue=0
###app checked, now continue
    if (shallwecontinue==1):
        athleteid=(athlete['id'])
        firstname=(athlete['firstname'])
        lastname=(athlete['lastname'])
        avatar=(athlete['avatar'])
        sex=(athlete['sex'])
        clubs=(athlete['clubs'])
        premium=(athlete['premium'])
        fields = ['id','firstname','lastname','access_token','token_expiry','refresh_token','avatar','sex','clubs','premium']
        athletedata = ({'id':int(athleteid),
                       'firstname':str(firstname),
                       'lastname':str(lastname),
                       'access_token':str(token_json["access_token"]),
                       'token_expiry':int(token_json["expires_at"]),
                       'refresh_token':str(token_json['refresh_token']),
                       'avatar':str(avatar),
                       'sex':str(sex),
                       'clubs':str(clubs),
                       'premium':str(premium)
                       })
        print (athletedata)

#####remove the target athlete from the file
        with open (temptokenfile) as r:
            lines = r.readlines()
        with open (temptokenfile,"w") as w:
            for line in lines:
                if (str(athleteid)) not in line:
                    w.write(line)
#####add target athelete back in with newly refreshed token
        with open (temptokenfile,"a") as f: #write elements of interest to strava_tokens.csv - appended
            writer=csv.DictWriter(f,fieldnames=fields,quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(athletedata)
        with open (archivetokenfilecsv,"a") as f: #write elements of interest to strava_tokens.csv - appended
            writer=csv.DictWriter(f,fieldnames=fields,quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(athletedata)
    else:
        print ("app not authorised, no data to write")
    time.sleep(2)

if __name__ == '__main__':
    refresh()
