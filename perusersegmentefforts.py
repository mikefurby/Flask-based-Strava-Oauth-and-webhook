#!/usr/bin/python
import csv
import json
import requests
import time
import argparse

rate=500
path=("/home/ubuntu/")
path2=("/home/ubuntu/Strava/")

class SegmentEfforts():

    def __init__(self,club,athlete_id):
        self.athlete = athlete_id
        self.club = club
        print ("hello world!" + club + str(athlete_id))

    def getAthleteData(self,club,athlete_id):
        athleteid=0
        athletelastname="testlastname"
        athletetoken="tokentest"
        tokenexpiry="expirytest"
        premium="premiumtest"
        memberlist=(path + club + "/input/membersdiv.csv")
        print("now entering the memberlist\n")
        g = open ("/home/ubuntu/Strava/log/getath.log",'w')
        g.write(memberlist + '\n')
        g.write(str(type(athlete_id)) + str(athlete_id) + '\n')
        with open(memberlist) as read_club_memberlist:
            athlete_entry = csv.reader(read_club_memberlist)
            for row in athlete_entry:
                g.write(str(type(row[0])) + str(row[0]) + '\n')
                if row[0] == str(athlete_id):
                    athleteid = row[0]
                    athletelastname = row[2]
                    athletetoken = row[6]
                    tokenexpiry = row[7]
                    premium = row[11]
                    print(athleteid + ',' + athletelastname + ',' + athletetoken + ',' + str(premium))
                else:
                    pass
        g.write(str(athleteid) + '\n')
        g.write(str(athletelastname) + '\n')
        g.write(str(athletetoken) + '\n')
        g.write(str(tokenexpiry) + '\n')
        g.write(str(premium) + '\n')
        return(athleteid,athletelastname,athletetoken,premium)

    def getAthleteSegments(self,club,athlete_data):
        athleteid= athlete_data[0]
        athletetoken= athlete_data[2]
        premium = athlete_data[3]
        starttime="T00:00:00Z"
        endtime="T23:59:59Z"
        segmentsummary=(path + club + "/input/segmentsummary.csv")
        alleffortsconcise=(path2 + club + "/efforts/segmentefforts_concise_" + athleteid + ".csv")
        with open(alleffortsconcise, 'w') as w:
            w.write("segment_id,athlete_id,activity_id,elapsed_time,start_date,segment_name,segment_elevation,top_10,pr,\n")
        if str(premium) == "True":
            with open(segmentsummary) as readfile:
                segsumm = csv.DictReader(readfile)
                for row in segsumm:
                    segmentid = row['segment_id']
                    segstart = (row['start_date'] + starttime)
                    segfinish = (row['end_date'] + endtime)
                    segname = row['name']
                    segelev = row['elevation']
                    segkom = row['kom']
                    segqom = row['qom']
                    print('Debug:' + segmentid + ',' + segstart + ',' + segfinish)
                    headers = {"Authorization":"Bearer %s" % (athletetoken) }
                    data = {"start_date_local":(segstart),"end_date_local":(segfinish)}        
                    segmentEffortEndpoint = ("https://www.strava.com/api/v3/segments/" + segmentid + "/all_efforts")
                    segmentEffortInfoDownload = requests.get(segmentEffortEndpoint,headers=headers,data=data)
#########check for the strava 15 minute rate limit and sleep in 1 minute intervals
#          print(segmentEffortInfoDownload.headers["x-ratelimit-usage"])
                    ratelimitstring=(segmentEffortInfoDownload.headers["x-ratelimit-usage"])
                    rate15min,rateday=(ratelimitstring.split(',',1))
                    print(rate15min)
                    if int(rate15min) < (rate):
                        print(rate15min,". Ok, well below the 15 minute rate limit of 600")
                    else:
                        print(rate15min,". Reached " + str(rate) + " requests within 15 minutes. Sleeping for 60seconds, repeat unti
l the 15 minute rate resets to 0")
                        time.sleep(60)
#Now print the entire segment effort info to the concise file
                    with open(alleffortsconcise, 'a') as w:
                      segmentEffortInfo=json.loads(segmentEffortInfoDownload.text)
                      for efforts in segmentEffortInfo:
                          print (efforts)
                          komrank=(efforts['kom_rank'])
                          prrank=(efforts['pr_rank'])
                          segname=(efforts['name'])
                          athleteid=(efforts['athlete']['id'])
                          activityid=(efforts['activity']['id'])
                          segid=(efforts['segment']['id'])
                          elapsedtime=(efforts['elapsed_time'])
                          date=(efforts['start_date'])
                          print(str(athleteid) + ',' + str(activityid) + ',' + str(elapsedtime) + ',' + str(date) + ',' + segname + 
',' + str(komrank) + ',' + str(prrank))
                          w.write(str(segid))
                          w.write(',' + str(athleteid))
                          w.write(',' + str(activityid))
                          w.write(',' + str(elapsedtime))
                          w.write(',' + str(date))
                          w.write(',"' + segname + '"')
                          w.write(',' + segelev)
                          w.write(',' + str(komrank))
                          w.write(',' + str(prrank))
                          w.write('\n')
        elif str(premium) == "False":
            print("User is not a Strava premium user, so segment efforts cannot be collected\n")
        else:
            pass

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--club", required=True,
        help="Club name")
    ap.add_argument("-a", "--athlete", required=True,
        help="Athlete ID")
    args = vars(ap.parse_args())

    club_arg = (args['club'])
    athlete_id_arg = (args['athlete'])
    f = open("/home/ubuntu/Strava/log/peruser.log",'w')
    f.write (club_arg + str(type(club_arg)))
###I don't understand this bit, why I have to do the instance with args then call the def in the import again with args
    athlete_instance = SegmentEfforts(club_arg,athlete_id_arg)
    athlete_data = athlete_instance.getAthleteData(club_arg,athlete_id_arg)
    print (str(athlete_data) + ":data")
###ditto...but it does work
    segment_instance = SegmentEfforts(club_arg,athlete_data)
    athlete_segments = segment_instance.getAthleteSegments(club_arg,athlete_data)
    print (str(athlete_segments) + ":segments")

#The end
