import pdb
import MySQLdb
from flask import Flask
import time
from datetime import timedelta
import update
from passlib.hash import pbkdf2_sha256

#server information:
url = "sql8.freemysqlhosting.net"
username = "sql8162831"
password = "6YRgu8LHLh"
db_name =  "sql8162831" 

db = MySQLdb.connect(url, username, password, db_name)
cursor = db.cursor()

#variables that may change:
cost_of_peep = 300
cost_of_parlay = 500

#Returns: (int results, int user_ID)
def attempt_register(firstname, lastname, username, password):
    #check username not already used:
    q = 'SELECT * FROM USERS WHERE UPPER(username) = UPPER(\'' + username + '\');'
    cursor.execute(q)
    result = cursor.fetchall()
    if not result:
        #encrypt password
        pw = pbkdf2_sha256.hash(password)
        query = 'INSERT INTO USERS (username, firstname, lastname, password, points, permissions, num_reports) VALUES (\'' + username + '\', \'' + firstname + '\',  \'' + lastname + '\', \'' + pw + '\', 2000 , \'0\', 0);'
        cursor.execute(query)
        db.commit()
        query = 'SELECT user_id from USERS where username = \'' + username + '\';'
        cursor.execute(query)
        response = cursor.fetchall()
        return [True, response[0][0]]
    else:
        return [False, 1]

#Returns: tuple: (bool success?, int user_ID)
def attempt_login(username, password):
    #q = 'SELECT user_id from USERS WHERE UPPER(username) = UPPER(\'' + username + '\') AND password = \'' + pword + '\';'
    q = 'SELECT user_id, password from USERS WHERE UPPER(username) = UPPER(\'' + username + '\');'
    cursor.execute(q)
    result = cursor.fetchone()
    if result:
        pw_e = result[1]
        if pbkdf2_sha256.verify(password, pw_e):
            return (True, result[0])
        else:
            return (False, 2) #wrong password error
    else:
        return (False, 1) #user doesn't exist error
        
#Takes: request: 'peep' or 'parlay'
#Modifies user's permission in db unless insufficient points
#Returns: bool: success or failure
def purchase_views(user_ID, request):
    if request == 'peep':
        cost = cost_of_peep
    elif request == 'parlay':
        cost = cost_of_parlay
    else:
        print ('invalid view request \n')
        return False
    q = 'SELECT points FROM USERS WHERE user_id = ' + str(user_ID) + ';'
    cursor.execute(q)
    result = cursor.fetchall()
    print ('num points ', result[0][0])
    if int(result[0][0]) >= cost:
        q2 = 'UPDATE USERS SET permissions =  \'' + request + '\' WHERE user_id = \'' + user_ID + '\';'
        cursor.execute(q2)
        new_points = int(result[0][0]) - cost
        q3 = 'UPDATE USERS SET points = ' + str(new_points) + ' WHERE user_id = \'' + user_ID + '\';'
        cursor.execute(q3)
        db.commit()
        return True
    return False

#Returns: (int user_id, varchar(255) username, varchar(255) password, int points, int permission)
def get_info(userid):
    #check username not already used:
    cursor.execute("SELECT firstname, lastname, CAST(latest_report AS char), num_reports, points FROM USERS WHERE user_id=%s", (userid))
    reply = cursor.fetchall()
    if not reply:
        #fix: finish this
        return 0
    return reply[0]


def report(userid, barid, reporttype, time_input, day):
    epoch_time = int(time.time())
    query = 'UPDATE VENUES SET last_check_in=' + str(epoch_time) + ' WHERE bar_id= ' + barid + ';' #updates last checkin in VENUES table
    cursor.execute(query)
    db.commit()
    time_input = '\'' + time_input + '\''

    if reporttype == 0:
        #update user's report count and latest report
        cursor.execute('UPDATE USERS SET latest_report=CAST(NOW() as char), num_reports=num_reports+1 WHERE user_id=%s', (userid))
        db.commit()

        #do rest
        query = "SELECT * from REPORTS WHERE bar_id = " + barid + " AND user_id = " + userid + ";"
        cursor.execute(query)
        data = cursor.fetchall()
        if not data:
            query = 'INSERT INTO REPORTS (bar_id, time_in, time_recent, user_id, day_of_week) VALUES (' + barid + ', ' + time_input + ', ' + time_input + ', ' + userid + ', \'' + day + '\');'
            cursor.execute(query)
            db.commit()
            return True
        query = 'UPDATE REPORTS SET time_in=' + time_input + ' WHERE user_id=' + userid + ' AND bar_id=' + barid + ';'
        cursor.execute(query)
        db.commit()
        return True
    elif reporttype == 1:
        query = 'UPDATE REPORTS SET time_recent=' + time_input + ' WHERE user_id=' + userid + ' AND bar_id=' + barid + ';'
        cursor.execute(query)
        db.commit()
        return True
    elif reporttype == 2:
        query = 'UPDATE REPORTS SET time_out=' + time_input + ', time_recent=' + time_input + ' WHERE user_id=' + userid + ' AND bar_id=' + barid + ';'
        cursor.execute(query)
        db.commit()
        return True
    elif reporttype == 3:
        q = 'UPDATE REPORTS DELETE FROM REPORTS WHERE bar_id = ' + str(barid) + 'AND user_id = ' + str(userid) + ';'
        db.commit()
        return True
    elif reporttype == 4:
        query = 'INSERT INTO REPORTS (bar_id, time_in, time_recent, time_out, user_id, day_of_week) VALUES (' + barid + ', ' + time_input + ', ' + time_input + ', ' + time_input + ', ' + userid + ', \'' + day + '\');'
        cursor.execute(query)
        db.commit()
        return True
    return False

def load_venue_profile(bar, user):
    #check user's permissions:
    q = "SELECT permissions FROM USERS WHERE user_id = " + str(user) + ';'
    cursor.execute(q)
    result = cursor.fetchone()
    #if (result[0] == 'peep') or (result[0] == 'parlay'):
    if (True): 
        q2 = "SELECT * FROM VENUES where bar_id = " + str(bar) + ';'
        cursor.execute(q2)
        result2 = cursor.fetchone()
        venarray = []
        for info in result2:
            venarray.append(info)
        q3 = 'SELECT * from PREDICTIONS where venue_id =  ' + str(bar) + ' AND day_of_week = \'Thursday\';'
        cursor.execute(q3)
        result3 = cursor.fetchall()[0]
        result3 = result3[2:]
        q4 = "SELECT last_check_in FROM VENUES where bar_id = " + str(bar) + ';'
        cursor.execute(q4)
        result4 = cursor.fetchone()
        reply = {}
        if result4:
            now = int(time.time())
            time_difference = (now - result4[0]) / 60
            venarray[7] = time_difference
        reply['venue'] = venarray
        reply['prediction'] = result3
        return reply
    q2 = "SELECT bar_name, address, city FROM VENUES where bar_id = " + str(bar) + ';'
    cursor.execute(q2)
    result2 = cursor.fetchone()
    return result2

def estpeople(barid, userid, estimate, day):
    query = "SELECT * from REPORTS WHERE bar_id = " + barid + " AND user_id = " + userid + ";"
    cursor.execute(query)
    data = cursor.fetchall()
    if not data:
        query = 'INSERT INTO REPORTS (bar_id, num_people, user_id, day_of_week) VALUES (' + str(barid) + ', ' + str(estimate) + ', ' + str(userid) + ', \'' + str(day) + '\');'
        cursor.execute(query)
        db.commit()
        return update.num_people(barid)
        return True
    else:
        query = 'UPDATE REPORTS SET num_people = ' + str(estimate) + ' WHERE user_id =' + str(userid) + ' AND bar_id =' + str(barid) + ';'
        cursor.execute(query)
        db.commit()
        return update.num_people(barid)
        return True


def add_venue(name, address, city, lat, longitude, ventype):
    name = name.replace(" ", "")
    query = 'SELECT * from VENUES WHERE bar_name = \'' + name + '\';'
    cursor.execute(query)
    result = cursor.fetchall()
    if not result:
        query1 = 'INSERT INTO VENUES (bar_name, address, city, lat, lng, venue_type) VALUES (\'' + name + '\', \'' + address + '\', \'' + city + '\', ' + lat + ', ' + longitude + ', \'' + ventype + '\');'
        cursor.execute(query1)
        db.commit()
        return True
    return False







