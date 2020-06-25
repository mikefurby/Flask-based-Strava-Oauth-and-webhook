from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, RadioField, DateField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, NumberRange
import email_validator
import csv
from sys import argv
from datetime import date

def readMembers(club):
    memberlist= ("/home/ubuntu/" + club + "/input/membersdiv.csv")
    with open (memberlist) as r:
        members = csv.reader(r)
        memberList=[]
        duplicates=[]
        for member in members:
    #        print (member[0] + ' ' + member[1] + ' ' + member[2])
            firstname=member[1]
            lastname=member[2]
            premium=member[11]
            name=(firstname + ' ' + lastname)
            athlete_id = (member[0])
            if premium == "False":
              if athlete_id not in duplicates:
                duplicates.append(athlete_id)
                url = ("https://www.strava.com/athletes/" + str(athlete_id))
                choice = (str(url),(name))
                memberList.append(choice)
    print (memberList)
    memberList.sort(key=takeSecond)
    default_choice = ("","Please select your name....")
    memberList.insert(0,default_choice)
    return memberList

def takeSecond(elem):
    return elem[1]

def readSegments(club):
    segsumm = ("/home/ubuntu/" + club + "/input/segmentsummary.csv")
    with open (segsumm) as r:
        segments = csv.DictReader(r)
        segList=[]
        for segment in segments:
            segment_name = segment["name"]
            segment_id = segment["segment_id"]
            url = ("https://www.strava.com/segments/" + str(segment_id))
            choice = (str(url),(segment_name))
            segList.append(choice)
    print (segList)
    return segList


class RegistrationForm(FlaskForm):
    username = StringField('Username',
               validators=[DataRequired(),
               Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SegmentSubmitForm(FlaskForm):
    todayunformat=date.today()
    day=todayunformat.strftime("%d")
    month=todayunformat.strftime("%m")
    year=todayunformat.strftime("%Y")
    club="ycf"
    #day=11
    #month=('06')
    #year=2020
    choices=readSegments(club)
    athletes=readMembers(club)
    athlete_url = SelectField('Athlete', choices=athletes)
    segment_url = SelectField('Segment', choices=choices)
    segment_hours = IntegerField('Hours',   validators=[InputRequired(), NumberRange(min=0,max=24)], default=2)
    segment_mins =  IntegerField('Minutes', validators=[InputRequired(), NumberRange(min=0,max=60)], default=59)
    segment_secs =  IntegerField('Seconds', validators=[InputRequired(), NumberRange(min=0,max=60)], default=59)
    activity_url = StringField('Optional Activity URL i.e. https://www.strava.com/activities/123456789', default='https://www.strava
.com/activities/')
    day = SelectField('Day', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10
','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),('21
','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31')], de
fault=day) 
    month = SelectField('Month', choices=[('01','Jan'),('02','Feb'),('03','Mar'),('04','Apr'),('05','May'),('06','Jun'),('07','Jul')
,('08','Aug'),('09','Sep'),('10','Oct'),('11','Nov'),('12','Dec')], default=month)
    year = SelectField('Year', choices=[('2020','2020')],default=year)
    segment_kom = SelectField('Leaderboard', choices=[('None','None'),('1','KoM/QoM'),('2','2nd overall'),('3','3rd overall'),('4','
4th overall'),('5','5th overall'),('6','6th overall'),('7','7th overall'),('8','8th overall'),('9','9th overall'),('10','10th overal
l')])
    segment_pr = SelectField('Personal Record', choices=[('None','None'),('1','New PR'),('2','2nd fastest time'),('3','3rd fastest t
ime')])
    password = PasswordField('Password = "password"', validators=[DataRequired()])
    submit = SubmitField('Submit Segment Effort')

class YCFSegmentDeleteForm(FlaskForm):
    club="ycf"
    choices=readSegments(club)
    athlete_url = StringField('Athlete URL i.e. https://www.strava.com/athletes/123456', default='https://www.strava.com/athletes/',
 validators=[DataRequired()])
    segment_url = SelectField('Segment', choices=choices)
    segment_time = IntegerField('Your Segment Effort in seconds:', validators=[DataRequired(), NumberRange(min=2,max=86400)])
    password = PasswordField('Password = "password"', validators=[DataRequired()])
    submit = SubmitField('Remove Segment Effort')


class GrimpeurSegmentSubmitForm(FlaskForm):
    club="grimpeur"
    day=04
    month='07'
    year=2020
    choices=readSegments(club)
    athletes=readMembers(club)
    athlete_url = SelectField('Athlete', choices=athletes)
    segment_url = SelectField('Segment', choices=choices)
    segment_mins = IntegerField('Your Segment Effort: Minutes', validators=[InputRequired(), NumberRange(min=0,max=60)], default=59)
    segment_secs = IntegerField('Seconds', validators=[InputRequired(), NumberRange(min=0,max=60)], default=59)
    activity_url = StringField('Optional Activity URL i.e. https://www.strava.com/activities/123456789', default='https://www.strava
.com/activities/')
    day = SelectField('Day', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10
','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),('21
','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31')], de
fault=day) 
    month = SelectField('Month', choices=[('01','Jan'),('02','Feb'),('03','Mar'),('04','Apr'),('05','May'),('06','Jun'),('07','Jul')
,('08','Aug'),('09','Sep'),('10','Oct'),('11','Nov'),('12','Dec')], default=month)
    year = SelectField('Year', choices=[('2016','2016'),('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020')],default=yea
r)
    segment_kom = SelectField('Strava Leaderboard position?', choices=[('None','None'),('1','KoM/QoM'),('2','2nd overall'),('3','3rd
 overall'),('4','4th overall'),('5','5th overall'),('6','6th overall'),('7','7th overall'),('8','8th overall'),('9','9th overall'),(
'10','10th overall')])
    segment_pr = SelectField('Personal Record?', choices=[('None','None'),('1','New PR'),('2','2nd fastest time'),('3','3rd fastest 
time')])
    password = PasswordField('Password = "password"', validators=[DataRequired()])
    submit = SubmitField('Submit Segment Effort')



class SetClub():
    def __init__(self,clubname):
        self.clubname = clubname

def main():
    script, club = argv
    clubname=SetClub(club)
    print (clubname)
    print (clubname.clubname)
    readSegments(clubname.clubname)
    print ("Segs done")
    readMembers(clubname.clubname)
    print ("athletes done")
    #form=TestForm().submit
    #print (form)

if __name__ == '__main__':
    main()
