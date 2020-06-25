#!/usr/bin/python3
from sys import argv
import requests
import json
import time

script, club = argv

def webhook(club):
    METHOD="get"
    checkEndpoint = ("https://www.strava.com/api/v3/push_subscriptions")
    check_status = make_request(club,METHOD,checkEndpoint)
    for index in check_status:
        webhook_id = (index["id"])
        make_test(club,str(webhook_id))

def make_request(club,METHOD,Endpoint):
    filepath = ("/home/ubuntu/Strava/")
    configfile = (filepath + club + "/config.json")
    with open (configfile) as c:
        clientinfo = json.load(c)
    CLIENT_ID = (clientinfo["CLIENT_ID"])
    CLIENT_SECRET = (clientinfo["CLIENT_SECRET"])
    post_data = {"client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
        } 
    print (Endpoint,post_data)
    if METHOD == "get":
        response = requests.get(Endpoint,data=post_data)
    elif METHOD == "delete":
        response = requests.delete(Endpoint,data=post_data)
    json_output = response.json()
    print ("Debug: token json output" + str(response))
    print ("Debug: token json output" + str(json_output))
    return json_output

def make_test(club,webhookid):
    current_epoch=(time.time())
    print (current_epoch)
    current_epoch-=300
    print (current_epoch)
    callbackurl = ("http://" + club + "callback.vscc-challenges.cc")
    headers = {"content-Type" : "application/json"}
    print (callbackurl)
    print (webhookid)
    post_data = {
#        "aspect_type":"update",
        "aspect_type":"create",
        "event_time":int(current_epoch),
        "object_id":3389967,
#        "object_id":3424783922,
        "object_type":"athlete",
#        "object_type":"activity", 
        "owner_id":3389967,
        "subscription_id":(webhookid),
#        "updates":{"authorized":"false"}
        "updates":{"title":"This is the webhook test result"} 
#        "updates":{} 
        } 
    json_post_data = json.dumps(post_data)
    print ("Debug test webhook - json_post_data: " + str(json_post_data))
    response = requests.post(callbackurl,headers=headers,data=str(json_post_data))
    print ("Debug test webhook - response: " + str(response))

if __name__ == '__main__':
    webhook(club)
