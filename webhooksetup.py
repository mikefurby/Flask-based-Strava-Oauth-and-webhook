#!/usr/bin/python3
from sys import argv
import requests
import json

script, club = argv

def callback(club):
    filepath = ("/home/ubuntu/Strava/")
    callback_url = ("http://" + club + "callback.vscc-challenges.cc")
    configfile = (filepath + club + "/config.json")
    with open (configfile) as c:
        clientinfo = json.load(c)
    CLIENT_ID = (clientinfo["CLIENT_ID"])
    CLIENT_SECRET = (clientinfo["CLIENT_SECRET"])
    Endpoint = "https://www.strava.com/api/v3/push_subscriptions"
    post_data = {"client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "callback_url": (callback_url),
        "verify_token": "STRAVA"
        ,} 
    print ("Debug: ",Endpoint,post_data)
    response = requests.post(Endpoint,post_data)
    json_output = response.json()
    print ("Debug: token json output" + str(json_output))
    result = (json_output)
    try:
        wh_sub_id = result["id"]
    except:
        errors = result["errors"]
        for error in errors:
            wh_sub_id =  (error["code"])
    with open (filepath + club + "_webhook_config.json",'a') as cwcj:
        json.dump(json_output,cwcj)
        cwcj.write("\n")
    with open (filepath + "club_to_webhook.json",'a') as ctwj:
        json.dump(json_output,ctwj)
        ctwj.write("," + club + "\n")
    with open (filepath + "club_to_webhook.txt",'a') as ctwt:
        ctwt.write(str(wh_sub_id) + ',' + club + '\n')
    return json_output

if __name__ == '__main__':
    callback(club)
