#!/usr/bin/python3
from sys import argv
import requests
import json

script, club = argv

def callback(club):
    filepath = ("/home/ubuntu/Strava/")
    configfile = (filepath + club + "/config.json")
    with open (configfile) as c:
        clientinfo = json.load(c)
    CLIENT_ID = (clientinfo["CLIENT_ID"])
    CLIENT_SECRET = (clientinfo["CLIENT_SECRET"])
    Endpoint = "https://www.strava.com/api/v3/push_subscriptions"
    post_data = {"client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
        } 
    response = requests.get(Endpoint,data=post_data)
    json_output = response.json()
    print ("Debug: token json output" + str(json_output))
    try:
        wh_sub_id = json_output[0]["id"]
    except:
        wh_sub_id = "not subscribed" 

    with open (filepath + club + "/webhook_config.json",'w') as wc:
        json.dump(json_output,wc)
    data = {'subscription_id':wh_sub_id, 'strava_clubname':(club)} 
    with open (filepath + "log/club_to_webhook.json",'a') as ctw:
        ctw.write(json.dumps(data,indent=4))
    with open (filepath + "log/club_to_webhook.txt",'a') as ctwt:
        ctwt.write(str(wh_sub_id) + ',' + club + '\n')
    return

if __name__ == '__main__':
    callback(club)
