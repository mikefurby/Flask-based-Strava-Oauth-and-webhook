#!/usr/bin/python3
from sys import argv
import requests
import json

script, club = argv


def webhook(club):
    METHOD="get"
    checkEndpoint = ("https://www.strava.com/api/v3/push_subscriptions")
    check_status = make_request(METHOD,checkEndpoint)
    for index in check_status:
        webhook_id = (index["id"])
        METHOD="delete"
        deleteEndpoint = ("https://www.strava.com/api/v3/push_subscriptions/" + str(webhook_id))
        make_request(METHOD,deleteEndpoint)


def make_request(METHOD,Endpoint):
    filepath = ("/home/ubuntu/Strava/")
    configfile = (filepath + club + "/config.json")
    with open (configfile) as c:
        clientinfo = json.load(c)
    CLIENT_ID = (clientinfo["CLIENT_ID"])
    CLIENT_SECRET = (clientinfo["CLIENT_SECRET"])
    post_data = {"client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
        } 
    print (Endpoint)
    if METHOD == "get":
        response = requests.get(Endpoint,data=post_data)
    elif METHOD == "delete":
        response = requests.delete(Endpoint,data=post_data)
    json_output = response.json()
    print ("Debug: token json output" + str(response))
    print ("Debug: token json output" + str(json_output))
    return json_output





if __name__ == '__main__':
    webhook(club)
