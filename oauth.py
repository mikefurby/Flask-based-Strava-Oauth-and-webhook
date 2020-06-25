from flask import Flask, request, abort, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, SegmentSubmitForm, YCFSegmentDeleteForm
from forms import GrimpeurSegmentSubmitForm
import requests
import requests.auth
import json
import csv
from urlparse import urlparse
import perusersegmentefforts
from perusersegmentefforts import SegmentEfforts

app = Flask(__name__)
website_url = 'vscc-challenges.cc'
#website_url = 'vscc-challenges.cc:65010'
app.config['SERVER_NAME'] = website_url 
app.config['SECRET_KEY'] = '1234567890'

posts = [{'author':'Mike','title':'Welcome','content':'Welcome to this new form that we can use to submit segment efforts','date':'2
7 May 2020'},
         {'author':'Mike','title':'League Tables','content':'Navigate here: http://vscc-challenges.cc/ycf/ or click on the "YCF vTT"
 button in the menu','date':'27 May 2020'},
         {'author':'Mike','title':'No need to pay for Strava','content':'If you are not a strava subscriber then we can still accoun
t for your segment efforts through this web form submission method. Existing members who are subscribed to Strava will still be pick
ed up automatically','date':'27 May 2020'}]

posts_about = [{'author':'Mike','title':'About this site',
             'content':'This site was created to offer the possibility for non paying Strava users to take part in a leaderboard sys
tem which used to automatically collect Strava segment effort data until the 18th May 2020 when Strava introduced some changes that 
resulted in the restriction of data availability to non paying users. This data specifically concerned leaderboards and segment effo
rts and so we needed another method to collect that data and this webform approach is the result. Here we can submit Strava Activity
 information and have it included with all the data that can still be collected  from any user as well as the restricted data that o
nly paying Strava subscrivers can access and share. Longer tem this could be extended to 100% non Strava and include other tracking 
apps...let us see','date':'27 May 2020'}]

####VSCC####
@app.route('/')
def homepage():
    club = "vscc"
    print ("This should not be reached until the base domain is migrated from S3 bucket based webhosting")
    return "hello hello, we should not be here if we used a subdomain like ycfauth.vscc-challenges.cc, this is vscc-challenges main 
domain and should not be available until webhosting is migrated from AWS S3 buckets and DNS re-pointed to here"

@app.route('/', subdomain = 'www')
def www():
    club = "vscc"
    return "www.vscc-challenges.cc"

@app.route('/', subdomain = 'vsccauth')
def vsccauth():
    club = "vscc"
    authorise(club)
    return "VSCC Strava App authorised"

@app.route('/', subdomain = 'vscccallback', methods = ['GET','POST'])
def vscc_callback():
    club = "vscc"
    result=webhook_callback(club)
    return result

####Grimpeur####
@app.route('/', subdomain = 'grimpeurauth')
def grimpeurauth():
    club = "grimpeur"
    authorise(club)
    return "Grimpeur auth page: Success"

@app.route('/', subdomain = 'grimpeurcallback', methods = ['GET','POST'])
def grimpeur_callback():
    club = "grimpeur"
    result=webhook_callback(club)
    return result

@app.route('/', subdomain = 'grimpeur')
def grimp_home():
    return render_template('grimpeur_home.html', title='Home', posts=posts)

@app.route('/about', subdomain = 'grimpeur')
def grimp_about():
    return "Grimpeur about"

@app.route('/segment_submit', subdomain = 'grimpeur', methods = ['GET','POST'])
def grimp_seg_sub():
    club = "grimpeur"
    form = GrimpeurSegmentSubmitForm()
    if form.validate_on_submit():
        if form.password.data == 'password':
            result=process_segment_form(form,club)
            message=result[0]
            flag=result[1]
            flash(message,flag)
            if flag != 'success':
                flash("Please check the exact format and 'spelling' of the Athlete and Activity",flag)
                return render_template('ycf_segment_submit.html', title='Segment Submit', form=form)
            return redirect(url_for('grimp_home'))
        else:
            flash('Submission failed: Password Incorrect','danger')
    return render_template('grimpeur_segment_submit.html', title='Segment Submit', form=form)
    #return "Grimpeur segment submission form"

@app.route('/segment_delete', subdomain = 'grimpeur')
def grimp_seg_del():
    club = "grimpeur"
    return "grimp seg del"

####YCF####
@app.route('/', subdomain = 'ycfauth')
def ycfauth():
    club = ("ycf")
    #logfile = open ("/home/ubuntu/Strava/log/mike.log",'w')
    #logfile.write("line1\n")
    authorise(club)
    #logfile.write("line2\n")
    #logfile.close()
    return render_template('ycfauth.html')

@app.route('/', subdomain = 'ycfcallback', methods = ['GET','POST'])
def ycf_callback():
    club = ("ycf")
    result=webhook_callback(club)
    return result

@app.route('/', subdomain = 'ycf', methods = ['GET','POST'])
def ycf_blog():
    return render_template('ycf_blog.html', title='Blog', posts=posts)

@app.route('/register', subdomain = 'ycf', methods = ['GET','POST'])
def ycf_reg():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account Created','success') 
        return redirect(url_for('ycf_blog'))
    return render_template('ycf_reg2.html', title='Register', form=form)

@app.route('/login', subdomain = 'ycf', methods = ['GET','POST'])
def ycf_login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'micf@rocketmail.com' and form.password.data == 'password':
            flash('Logged In','success')
            return redirect(url_for('ycf_blog'))
        else:
            flash('Log in failed','danger')
    return render_template('ycf_login.html', title='Login', form=form)

@app.route('/about', subdomain = 'ycf')
def ycf_about():
    return render_template('ycf_about.html', posts=posts_about)

@app.route('/segment_submit', subdomain = 'ycf', methods = ['GET','POST'])
def ycf_segment():
    club = "ycf"
    form = SegmentSubmitForm()
    if form.validate_on_submit():
        if form.password.data == 'password':
            result=process_segment_form(form,club)
            message=result[0]
            flag=result[1]
            flash(message,flag)
            if flag != 'success':
                flash("Please check the exact format and 'spelling' of the Athlete and Activity",flag)
                return render_template('ycf_segment_submit.html', title='Segment Submit', form=form)
            return redirect(url_for('ycf_blog'))
        else:
            flash('Submission failed: Password Incorrect','danger')
    return render_template('ycf_segment_submit.html', title='Segment Submit', form=form)

@app.route('/segment_delete', subdomain = 'ycf', methods = ['GET','POST'])
def ycf_segment_delete():
    club = "ycf"
    form = YCFSegmentDeleteForm()
    if form.validate_on_submit():
        if form.password.data == 'password':
            result=process_delete_form(form,club)
            flash(result,'success')
            return redirect(url_for('ycf_blog'))
        else:
            flash('Submission failed: Password Incorrect','danger')
    return render_template('ycf_segment_delete.html', title='Remove a segment effort', form=form)

@app.route('/testform', subdomain = 'ycf', methods = ['GET','POST'])
def ycf_test():
    club = "ycf"
    clubname = SetClub(club)
    form = TestForm()
    return render_template('testform.html', form=form)

####VS3L####
app.route('/', subdomain = 'vs3lauth')
def vs3lauth():
    club = ("vs3l")
    authorise(club)
    return "VS3L auth page: Success"

@app.route('/', subdomain = 'vs3lcallback', methods = ['GET','POST'])
def vs3l_callback():
    club = ("vs3l")
    result=webhook_callback(club)
    return result

######## defs called from above app.routes #########

def process_delete_form(form,club):
    password = form.password.data
    athlete = form.athlete_url.data
    elapsed = form.segment_time.data
    parsed = urlparse(athlete)
    path = parsed.path
    parts = path.split('/')
    athlete = parts[2]
    segeffortfilea = ("/home/ubuntu/Strava/" + str(club) + "/efforts/segmentefforts_concise_webform.csv") 
    segeffortfileb = ("/home/ubuntu/Strava/" + str(club) + "/efforts/webform_remove_tempfile.csv") 
    with open (segeffortfilea) as read:
        lines = read.readlines()
        with open (segeffortfileb,'w') as tempwrite:
            for line in lines:
                if str(elapsed) in line and str(athlete) in line:
                    pass
                else:
                    tempwrite.write(line)
    with open (segeffortfileb) as tempread:
        lines = tempread.readlines()
        with open (segeffortfilea,'w') as rewrite:
            for line in lines:
                rewrite.write(line)
    result = "Segment Effort Successfully removed"
    return result



def process_segment_form(form,club):
    result = "Segment Effort Successfully processed"
    password = form.password.data
    segment = form.segment_url.data
    activity_url = form.activity_url.data
    athlete = form.athlete_url.data
    hours = form.segment_hours.data
    mins = form.segment_mins.data
    secs = form.segment_secs.data
    kom = form.segment_kom.data
    pr = form.segment_pr.data
    day = form.day.data
    month = form.month.data
    year = form.year.data
    elapsed=(int(hours)*3600+int(mins)*60+int(secs))
    date=( str(year) + '-' + str(month) + '-' + str(day) + 'T00:00:01Z')
    #return (form.activity_url.data,'danger')
    #return (activity_url,'danger')
    try:
        parsed = urlparse(athlete)
        path = parsed.path
        parts = path.split('/')
        athlete = parts[2]
        #return (athlete,'danger')
    except:
        flag='danger'
        message=('Submission Failed: There is a problem with athlete URL format')
        return (message,flag)

    try:
        parsed = urlparse(segment)
        path = parsed.path
        parts = path.split('/')
        segment = parts[2]
        #return (segment,'danger')
    except:
        flag='danger'
        message=('Submission Failed: There is a problem with segment URL format')
        return (message,flag)

    #activity="none"
    #return (activity_url,'danger')
    try:
        parsed = urlparse(activity_url)
        path = parsed.path
        parts = path.split('/')
        activity = parts[2]
        if parts[2] == "":
            activity="none"
        else:
            activity = parts[2]#here the activity id might still be incorrect but that can only be discovered when attempting to que
ry it
        #return (activity,'danger')
    except:
        activity="none"
        #pass
        #flag='danger'#need to feed this into the result 
        #message=('Submission Failed: There is a problem with activity URL format')
        #return (message,flag)

    #return (activity,'danger')
    segsumm = ("/home/ubuntu/" + str(club) + "/input/segmentsummary.csv") 
    memberlist = ("/home/ubuntu/" + str(club) + "/input/membersdiv.csv") 
    with open(segsumm) as segfile:
        segs = csv.reader(segfile)
        for counter,seg in enumerate(segs):
          if seg[0] == (segment):
            segname = seg[3]
            elev = seg[4]
            segnumber = counter
    with open(memberlist) as mfile:
        members = csv.reader(mfile)
        access_token="not found"
        for member in members:
          if str(member[0]) == str(athlete):
            access_token = str(member[6])
   
    if activity != "none":#so if an activity id is given then we attempt to query, but if they input it incorrectly then the auth wi
ll fail
        headers = {"Authorization":"Bearer %s" % (access_token) }
        data = () 
        Endpoint = ("https://www.strava.com/api/v3/activities/" + str(activity))
        Download = requests.get(Endpoint,headers=headers,data=data)
        Info=json.loads(Download.text)
        try:#if the auth works then we get a correct result here, else it will move into the exception and report a failure.
            date=str(Info["start_date"])
        except:
            flag='danger'
            result=("Submission Failed:  There is a problem with the ActivityID that you inputted or your authorisation of the data 
collection app. Please ask for support.")
            return(result,flag)
    else:
        pass #this just keeps the date set as per the form

#    with open ("/home/ubuntu/Strava/log/segment_submit.log",'a') as seg:
#        seg.write(str(Endpoint) + '\n')
#        seg.write(str(Info['start_date']) + '\n')
#        seg.write(str(segment) + ',' + str(athlete) + ',' + str(activity) + ',' + str(elapsed) + ',' + str(date) + ',"' + str(segna
me) + '",' + str(elev) + ',' + str(kom) + ',' + str(pr) + ',\n')
    segeffortfilea = ("/home/ubuntu/Strava/" + str(club) + "/efforts/segmentefforts_concise_webform.csv") 
    with open (segeffortfilea,'a') as seg:#be good to do proper csv writing here.
        seg.write(str(segment) + ',' + str(athlete) + ',' + str(activity) + ',' + str(elapsed) + ',' + str(date) + ',"' + str(segnam
e) + '",' + str(elev) + ',' + str(kom) + ',' + str(pr) +  ',\n')
    flag='success'
    result = "Segment Effort Successfully processed"
    return (result,flag)

### deals with all the webhook calls. App webhook subscription and athlete updates
def webhook_callback(club):
    with open ('/home/ubuntu/Strava/log/webhook.log','a') as logfile:
        method = request.method
        logfile.write("Start:")
        if request.method == 'POST':
            logfile.write(request.method + ": (args):" + request.data + "\n")
            process_webhook_post(club) #call this def below and deal with athlete de-authorisation
            return ("hello " + method),200
        elif request.method == 'GET':
            logfile.write(request.method + ":(args) " + str(request.args) + "\n")
            logfile.write(request.method + ":(data) " + str(request.data) + "\n")
            successdata={'success':True,'hub.challenge': request.args['hub.challenge']}
            content={'ContentType':'application/json'}
            return json.dumps(successdata), 200, content 
        else:
            return ("hello " + method)
### called from webhook_callback
### this reads the webhook post, and if it is a user deauthorisation, they are removed from strava_tokens.csv
### it is a new activity creation then find the activity info
def process_webhook_post(club):
    tokenfile = ("/home/ubuntu/Strava/" + club + "/tokenfiles/strava_tokens.csv")
    segmentlist = ("/home/ubuntu/" + club + "/segmentlist.csv")
    with open ("/home/ubuntu/Strava/log/webhook_processing.log",'a') as dt:
        ifupdate = request.data
        jifupdate = json.loads(ifupdate)
        if (jifupdate["object_type"]) == ("activity"):
            try:
                dt.write("activity updated: " + jifupdate["updates"]["title"] + '\n')
            except:
###the new activity creation part
                if (jifupdate["aspect_type"]) == ("create"):
                    dt.write("this is where I need to run the data collection for the activity: ")
                    dt.write(str(jifupdate["object_id"]))
                    dt.write(" for this athlete: ")
                    dt.write(str(jifupdate["owner_id"]))
                    dt.write(" in this club: " + club + '\n')
                    created_act_list = []
                    created=("/home/ubuntu/Strava/log/created_activities_" + str(club) + ".log")
                    dt.write(created + '\n')
                    try:
                        with open (created) as rcal:
                            activities = rcal.readlines()
                            for activity in activities:
                                act=activity.strip()
                                created_act_list.append(act)
                    except:
                        pass
                    with open (created,'a') as cal:
                        activity=(str(jifupdate["object_id"]))
                        if activity not in created_act_list:
                            cal.write(str(jifupdate["object_id"]) + '\n')
                            new_activity="True"
                        else:
                            new_activity="False"

                    with open (tokenfile) as r:
                        lines = csv.DictReader(r)
                        premium="False"
                        for line in lines:
                            if (str(jifupdate["owner_id"])) == line['id']:
                                dt.write("\n" + line['id'] + ',' + line['firstname'] + ' ' + line['lastname'] + ',' + line['access_t
oken'] + ',' + line['premium'] + ',' + '\n')
                                accesstoken = (line['access_token'])
                                premium = (line['premium'])
                    if (premium) == "True" and (new_activity) == "True":   ##premium user - collect segment info...
                        headers = {"Authorization":"Bearer %s" % (accesstoken) }
                        data = ("") 
                        Endpoint = ("https://www.strava.com/api/v3/activities/" + str(jifupdate["object_id"]) + "?include_all_effort
s=")
                        dt.write(str(Endpoint) + str(data) + str(headers) + "\n")
                        Download = requests.get(Endpoint,headers=headers,data=data)
                        Info=json.loads(Download.text)
                        dt.write(str(Info["name"]) + '=Activity Name\n')

                        activity_segments = []#create a list of the segments ridden in the activity
                        for efforts in (Info["segment_efforts"]):
                            activity_segments.append(int(efforts["segment"]["id"]))
                        dt.write("List of segments in the activity: " + str(activity_segments) + "\n")

                        with open (segmentlist) as s:
                            lines = csv.DictReader(s)
                            dt.write("opening seglist\n")
                            for linecount,line in enumerate(lines,1):
                                #effortfile = ("/home/ubuntu/Strava/" + club + "/efforts/segmentefforts_concise_webhook" + str(linec
ount) + ".csv")
                                effortfile = ("/home/ubuntu/Strava/" + club + "/efforts/segmentefforts_concise_webhook.csv")
                                #noneffortfile = ("/home/ubuntu/Strava/" + club + "/efforts/nonsegmentefforts_concise_webhook" + str
(linecount) + ".csv")
                                segment=(line['segmentid'])
                                dt.write('target segment:' + str(segment) + str(type(segment)) + '\n')
                                dt.write(str(effortfile) + '\n')
                                if int(segment) in activity_segments:
                                    dt.write("we have a match:\n")
                                    for efforts in (Info["segment_efforts"]):
                                        if (int(efforts["segment"]["id"])) == int(segment):
                                            dt.write('activity efforts: ' + str(efforts["segment"]["id"]) + ' compared to target:' +
 str(segment) + '\n')
                                            elev = ((efforts["segment"]["elevation_high"])-(efforts["segment"]["elevation_low"]))
                                            dt.write("Getting efforts:\n" + str(segment) + ',' + str(efforts["elapsed_time"]) + '\n'
)
                                            with open(effortfile,'a') as sc:
                                                sc.write(str(efforts["segment"]["id"]) + ',')
                                                sc.write(str(Info["athlete"]["id"]) + ',')
                                                sc.write(str(Info["id"]) + ',')
                                                sc.write(str(efforts["elapsed_time"]) + ',')
                                                sc.write(str(efforts["start_date"]) + ',')
                                                sc.write('"' + str(efforts["segment"]["name"]) + '",')
                                                sc.write(str(elev) + ',')
                                                sc.write(str(efforts["kom_rank"]) + ',')
                                                sc.write(str(efforts["pr_rank"]) + ',')
                                                sc.write('\n')
                                else:
                                    dt.write("we do not have a match:")
                                    dt.write(str(segment) + '\n')
                                #    with open(noneffortfile,'a') as sc:
                                #        sc.write(str(segment) + ',')
                                #        sc.write(str(Info["athlete"]["id"]) + ',')
                                #        sc.write(str(Info["id"]) + ',')
                                #        sc.write(str(efforts["elapsed_time"]) + ',')
                                #        sc.write(str(efforts["start_date"]) + ',')
                                #        sc.write(str(efforts["segment"]["name"]) + ',')
                                #        sc.write(str(elev) + ',')
                                #        sc.write(str(efforts["kom_rank"]) + ',')
                                #        sc.write(str(efforts["pr_rank"]) + ',')
                                #        sc.write('\n')
                                dt.write("end of list matching:\n")
                    elif (premium) == "False":
                        dt.write("Premium user: " + premium + ". Athlete is not a Strava premium user, so segment info not collected
\n")
                    else:
                        dt.write("New Activity: " + new_activity + ". The activity was a repeat\n")
#            return
        else:
###This is the the de-auth part. Need to remove the user from the tokens file on receipt of this webhook.
            try:
                dt.write(jifupdate["updates"]["authorized"])
                dt.write(str(jifupdate["owner_id"]))
                dt.write("," + club + ",")
                dt.write(":Need to remove this user\n")
                with open (tokenfile) as r:
                    lines = r.readlines()
                with open (tokenfile,"w") as w:
                    for line in lines:
                        if (str(jifupdate["owner_id"])) not in line:
                            w.write(line)
###This is the authorised user webhook. Don't need to write the user here, that's done by the authorisation routine. Just log the we
bhook message here.
            except:
                dt.write(str(jifupdate))
                dt.write(str(jifupdate["owner_id"]))
                dt.write("," + club + ",")
                dt.write(":Need to remove this user\n")
#                with open (tokenfile,"a") as tfa:
#                    tfa.write("hello" + str(jifupdate["owner_id"]))  ###this is a test and it shows that something is written to th
e token file
#        return        
    return

### deals with new athlete app authorisations and collects data for the strava_tokens.csv file
### for use in the segment efforts data collection app
def authorise(club):
##all the clubs of interest
    authlog = open ("/home/ubuntu/Strava/log/authorisation.log", 'w')
    authlog.write("Starting the authorisation:\n")
    clubvs3l = 115367##these are not used
    clubvsvl = 115367
    clubvscc = 68829
    clubgrimpeur = 185097
    clubvsccapp = 547520
    clubvscctt = 597519
    clubvstc = 105940
##input and output files
    filepath = "/home/ubuntu/Strava/"
    tokenfile = (filepath + club + "/tokenfiles/strava_tokens.csv")
    newauthtokenfile = (filepath + club + "/tokenfiles/new_auth_strava_token.csv")
    jsonfile = (filepath + club + "/tokenfiles/new_auth_strava_token.json")
##set up API call parameters for OAUTH user request
    configfile = (filepath + club + "/config.json")
    with open (configfile) as c:
        clientinfo = json.load(c)
    CLIENT_ID = (clientinfo["CLIENT_ID"])
    CLIENT_SECRET = (clientinfo["CLIENT_SECRET"])
##authorisation and result
    error = request.args.get('error', '')
    authlog.write(error + ':Initial request Error:\n')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    authlog.write(state + ':Initial request State:\n')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    authlog.write(code + ':Initial request Code:\n' + ' get_token is next....\n')
    print ('Debug: got this code:',code,' get_token is next...')
    token = get_token(code,CLIENT_ID,CLIENT_SECRET)
    authlog.write(str(token) + ':Initial request Access Token:\n')
    with open (jsonfile,"w") as j: #dump the output as a whole
        json.dump(token,j)
        json.dump(token["access_token"],j)
        json.dump(token["access_token"],authlog)
        authlog.write(':Access Token:\n    ...getting clubs next....')
####fetch athlete club data from the newly acquired access_token for the athlete
        isinclubs = getclubs(token)
        authlog.write('clubs:' + str(isinclubs) + '\n')
        clublist = []
        for aclub in isinclubs:
            club_id=(aclub["id"])
            clublist.append(club_id)
        authlog.write('clubs:' + str(clublist) + '\n')
###athlete data from the auth success, then club list call to be written to files for later use
        athleteid=(token["athlete"]["id"])
        firstname=(token["athlete"]["firstname"])
        firstname=(firstname.encode('ascii', 'ignore'))
        firstname=(firstname.strip())
        lastname=(token["athlete"]["lastname"])
        lastname=(lastname.encode('ascii', 'ignore'))
        lastname=(lastname.strip())
        premium = (token["athlete"]["summit"])
        avatar = (token["athlete"]["profile_medium"])
        if ('facebook') in (avatar):
            avatar = "/icons/vscc2018.jpg"
        if ('avatar') in (avatar):
            avatar = "/icons/vscc2018.jpg"
        athleteurl=('https://www.strava.com/athletes/' + str(athleteid))
        authlog.write(str(athleteid) +  '\n')
        authlog.write(str(firstname) + str(lastname) + str(avatar) + str(athleteurl) +  '\n')
##then in a form for csv writing
        fields = ['id','firstname','lastname','access_token','token_expiry','refresh_token','avatar','sex','clubs','premium']
        athletedata=({'id':(int(athleteid)),
                  'firstname':(firstname),
                  'lastname':(lastname),
                  'access_token':(token["access_token"]),
                  'token_expiry':(int(token["expires_at"])),
                  'refresh_token':(token["refresh_token"]),
                  'avatar':(avatar),
                  'sex':(token["athlete"]["sex"]),
                  'clubs':(str(clublist)),
                  'premium':(str(premium))
                 })
        j.write(',' + str(athletedata))
#dump output in csv format to a separate file for this single user auth, for logging purposes
    with open (newauthtokenfile,"a") as w:
        writer=csv.DictWriter(w,fieldnames=fields,quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerow(athletedata)
#now read the existing token file and see if this user is already there, if so then remove in order to replace with new data
    authlog.write('reading strava_tokens.csv\n')
    with open (tokenfile) as r:
        lines = r.readlines()
    #authlog.write(str(lines))
    authlog.write('check rewriting strava_tokens.csv\n')
    with open (tokenfile,"w") as w:
        for line in lines:
            if (str(athleteid)) not in line:
                w.write(line)
    authlog.write('strava_tokens.csv re-written\n')
###now add that newly authed/re-authed athlete here
    with open (tokenfile,"a") as f: #write elements of interest to strava_tokens.csv - appended
        writer=csv.DictWriter(f,fieldnames=fields,quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(athletedata)
    authlog.write('strava_tokens.csv appended with newly authorised user.\n')
    authlog.write(str(club) + str(athleteid) + '\n')
    getNewAthleteSegments(club,athleteid,authlog)
    authlog.write('The End!\n')

## def called from the authorise def above: returns true if state of the call is valid
def is_valid_state(state):
    print ('Debug: This is the "is_valid_state" def')
    return True
## defg called from the authorise def above: returns the access token used in all data collection calls
def get_token(code,CLIENT_ID,CLIENT_SECRET):
    authlog2 = open ("/home/ubuntu/Strava/log/authorisation2.log", 'w')
    authlog2.write('getting access token\n')
    strava_oauth_url="https://www.strava.com/api/v3/oauth/token"
    authlog2.write(strava_oauth_url + '\n')
    post_data = {"grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
        ,}
    authlog2.write(str(post_data) + '\n')
    response = requests.post(strava_oauth_url,post_data)
    authlog2.write(str(response) + '\n')
    token_json = response.json()
    authlog2.write(str(token_json) + '\n')
    print ("Debug: token json output" + str(token_json))
    return token_json
#### gets the clubs that an athelete belongs to and included in strava_tokens.csv ####
def getclubs(token):
    accesstoken=(token["access_token"])
    headers = {"Authorization":"Bearer %s" % (accesstoken) }
    data = {}
    athleteClubsEndpoint = "https://www.strava.com/api/v3/athlete/clubs"
    athleteClubsInfoDownload = requests.get(athleteClubsEndpoint,headers=headers,data=data)
    athleteClubsInfo=json.loads(athleteClubsInfoDownload.text)
    print ("Debug: ", str(athleteClubsInfo))
    return (athleteClubsInfo)    
def getNewAthleteSegments(club_arg,athlete_id_arg,authlog):
    authlog.write(str(club_arg) + "imported\n")
    appclubs = []
    if club_arg == "ycf":
        appclubs.append("ycf")
    elif club_arg == "vscc":
        #appclubs=["vscc","vs3l","grimpeur","vscctt","vstc","vsac","vsvl"]
        appclubs.append("vscc")
    authlog.write(str(appclubs) + '?????????\n')
    for aclub in appclubs:
        authlog.write(aclub)
        authlog.write(str(athlete_id_arg))
        #athlete_data = SegmentEfforts.getAthleteData(club,athlete_id_arg)
        athlete_instance = SegmentEfforts(club_arg,athlete_id_arg)
        athlete_data = athlete_instance.getAthleteData(club_arg,athlete_id_arg)
        authlog.write(str(athlete_data))
        #athlete_segments = SegmentEfforts.getAthleteSegments(aclub,athlete_data)
        segment_instance = SegmentEfforts(club_arg,athlete_data)
        athlete_segments = segment_instance.getAthleteSegments(club_arg,athlete_data)
        #authlog.write(str(athlete_segments))
 

####end of athlete authorisaton####



if __name__ == '__main__':
    app.run()
#    app.run(debug=True, host='0.0.0.0', port=65010)
