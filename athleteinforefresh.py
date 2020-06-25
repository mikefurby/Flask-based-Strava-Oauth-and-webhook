#!/usr/bin/python3
from sys import argv
from datetime import date, datetime
import requests
import csv
import json
import time

script, club = argv

expiry_limit = 0

filepath = ("/home/ubuntu/Strava/") 
todayunformat=date.today()
today=todayunformat.strftime("%d %b %Y")
tokenfile = (filepath + club + "/tokenfiles/strava_tokens.csv")
temptokenfile = (filepath + club + "/tokenfiles/temp_athlete_info_strava_tokens.csv")
logfile = (filepath + club + "/tokenfiles/logfile.txt")


def refresh():
    ftemp = open (temptokenfile,'w')
    ftemp.write("id,firstname,lastname,access_token,token_expiry,refresh_token,avatar,sex,clubs,premium,\n")
    ftemp.close()
    with open (tokenfile) as tfr:
        data = csv.DictReader(tfr)
        for athlete in data:
            print (athlete)
            refresh_athlete(athlete)
            #log_this(": No change %s \n" %  str(athlete['id']))
###now copy temp file to main file
    with open (temptokenfile) as r:
        lines = r.readlines()
    with open (tokenfile,"w") as w:
        for line in lines:
            w.write(line)



def log_this(message):
    now = datetime.now()
    with open (logfile,"a") as lf:
        print ("debug: logging now from token_refresh.py")
        lf.write(str(now) + (message))
    lf.close()

def refresh_athlete(athlete):
###recover data passed into def
        athleteid=(int(athlete['id']))
        atoken=(athlete['access_token'])
        expires=(athlete['token_expiry'])
        rtoken=(athlete['refresh_token'])
###execute on data passed in
        athlete_now = getathlete(atoken) ###API call to gather current Athlete information
        firstname=(athlete_now["firstname"])
        firstname=(firstname.encode('ascii', 'ignore').decode('ascii'))
#        firstname=(firstname.encode('utf-8'))
#        firstname=(firstname.decode('utf-8'))
        lastname=(athlete_now["lastname"])
        lastname=(lastname.encode('ascii', 'ignore').decode('ascii'))
#        lastname=(lastname.encode('utf-8'))
 #       lastname=(lastname.decode('utf-8'))
        premium=(athlete_now["summit"]) #added 25th may + written to the file at the top
        avatar = (athlete_now["profile_medium"])
        if ('facebook') in (avatar):
            avatar = "/icons/vscc2018.jpg"
            if (club) == "ycf":
                avatar = "/ycf/ycf.png"
        if ('avatar') in (avatar):
            avatar = "/icons/vscc2018.jpg"
            if (club) == "ycf":
                avatar = "/ycf/ycf.png"
        isinclubs = getclubs(atoken) ###API call to gather current Athlete club membership
        clublist = []
        for club_ids in isinclubs:
            club_id=(club_ids["id"])
            clublist.append(club_id)
###Prepare info for writing, then write to temporary file
        fields = ['id','firstname','lastname','access_token','token_expiry','refresh_token','avatar','sex','clubs','premium']
        athletedata = ({'id':int(athleteid),
                       'firstname':(firstname),
                       'lastname':(lastname),
                       'access_token':(atoken),
                       'token_expiry':int(expires),
                       'refresh_token':(rtoken),
                       'avatar':(avatar),
                       'sex':(athlete_now['sex']),
                       'clubs':(str(clublist)),
                       'premium':(str(premium))
                       })
        print (athletedata)
        with open (temptokenfile,"a") as f: #write elements of interest to temporary strava_tokens.csv - appended
            writer=csv.DictWriter(f,fieldnames=fields,quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(athletedata)



def getathlete(accesstoken):
    headers = {"Authorization":"Bearer %s" % (accesstoken) }
    data = {}
    Endpoint = "https://www.strava.com/api/v3/athlete"
    InfoDownload = requests.get(Endpoint,headers=headers,data=data)
    Info=json.loads(InfoDownload.text)
    print ("Debug: ", str(Info))
    return (Info)    

def getclubs(accesstoken):
    headers = {"Authorization":"Bearer %s" % (accesstoken) }
    data = {}
    Endpoint = "https://www.strava.com/api/v3/athlete/clubs"
    InfoDownload = requests.get(Endpoint,headers=headers,data=data)
    Info=json.loads(InfoDownload.text)
    print ("Debug: ", str(Info))
    return (Info)    

if __name__ == '__main__':
    refresh()
