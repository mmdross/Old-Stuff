#RRstudios 2017
#StreamLine


from flask import Flask, request
from datetime import timedelta
import MySQLdb
import json
import pdb
import query
import os
import time
import recalculate_lines

app = Flask(__name__)

db = MySQLdb.connect("sql8.freemysqlhosting.net","sql8162831","6YRgu8LHLh","sql8162831" )
cursor = db.cursor()

#example query: cursor.execute("select * from VENUES WHERE ID = 1;")
#data = cursor.fetchall(), data will be a list of tuples where each tuple contains all of the columns of a row
#json.dumps(data) will give a json of the form [(column1, column2, column3), (nextrow of stuff, column2, column3)]

@app.route('/api')
def api():
    return 'base api'

@app.route('/api/register') #add new row to user table
def register():
      #query users table for user with same username
      #if so, send back message that username is taken
      #else, add new row to users table and create a user ID number for them
      #initialize with 300 points
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    username = request.args.get('email')
    pw = request.args.get('password')
    data = query.attempt_register(username, pw)
    return json.dumps(data)

@app.route('/api/login') #validate user and create session
def login():
    username = request.args.get('email')
    pw = request.args.get('password')
    data = query.attempt_login(username, pw) #error code 1 = username does not exits, 2 = password does not match
    return json.dumps(data)

    
@app.route('/api/fblogin') #login with facebook, not sure if we need an endpoint of our own for this
def fblogin():
    return 'login through facebook'

@app.route('/api/report') #report line length
def report():
    reporttype = int(request.args.get('type')) #0 = initial, 1 = continuous, 2 = in bar, 3 = abandon, 4 = no line, 5 = number of people in line
    userid = request.args.get('userid')
    barid = request.args.get('venue') #venue ID
    day = request.args.get('day')
    if reporttype < 5:
        time = request.args.get('time')
        outcome = query.report(userid, barid, reporttype, time, day)
        recalculate_lines.recalc_report()
        return json.dumps(outcome)
    elif reporttype == 5:
        estimate = request.args.get('estimate')
        outcome = query.estpeople(barid, userid, estimate, day)
        recalculate_lines.recalc_est()
        return json.dumps(outcome)
    else:
        return 'this is not right'


@app.route('/api/mapvenues') #returns json object with permissions (0, peep, or parlay) and bars to display
def mapvenues():
    user_ID = request.args.get('user_ID')
    cursor.execute("select * from VENUES;")
    data1 = cursor.fetchall()
    if not data1:
        return ("Error: venue not found")
    cursor.execute("select permissions from USERS where user_id=" + str(user_ID) + ";")
    data2 = cursor.fetchone()
    if not data2:
        return ("Error: user ID does not exist")
    reply = {}
    reply["permission"] = data2[0]
    reply["venues"] = data1
    return json.dumps(reply)
    #return test

@app.route('/api/spendpoints') #spend points to unlock bar views
def spendpoints():
    reqtype = request.args.get('reqtype')
    user_id = request.args.get('user_id')     
    data = query.purchase_views(user_id, reqtype)       
    if data == True:      
        return json.dumps(True)   
    else:     
        return json.dumps(False)

@app.route('/api/venuesearch')
def venuesearch():
    user_id = request.args.get('user')
    q = "SELECT * FROM VENUES;"
    cursor.execute(q)
    result = cursor.fetchall()
    if not result:
        return "no venues"
    reply = {}
    q2 = "SELECT user_id, permissions, points FROM USERS WHERE user_id = " + str(user_id) + ';'
    cursor.execute(q2)
    reply['user'] = cursor.fetchone()
    wholearray = []
    for bar in result:
        q4 = "SELECT last_check_in FROM VENUES where bar_id = " + str(bar[0]) + ';'
        cursor.execute(q4)
        result4 = cursor.fetchone()
        if result4:
            now = int(time.time())
            time_difference = (now - result4[0]) / 60
            venarray = []
            for info in bar:
                venarray.append(info)
            venarray[7] = time_difference
            wholearray.append(venarray)        
    reply['venue'] = wholearray
    return json.dumps(reply)

@app.route('/api/loadVenue')
def loadVenue():
    venueid= request.args.get('venue')
    userid = request.args.get('user') 
    data = query.load_venue_profile(venueid, userid)
    return json.dumps(data)

     
@app.route('/api/purchase') #use venmo or paypal api to purchase points
def purchase():
    return "Purchase API"

@app.route('/api/userinfo')
def userinfo():
    userid = request.args.get('userid')
    reply = query.get_info(userid)
    if reply == 0:
        return 'User Not Found' 
    return json.dumps(reply)

@app.route('/api/addvenue')
def addvenue():
    name = request.args.get('name')
    address = request.args.get('address')
    city = request.args.get('city')
    lat = request.args.get('lat')
    longitude = request.args.get('long')
    ventype = request.args.get('type')
    reply = query.add_venue(name, address, city, lat, longitude, ventype)
    return json.dumps(reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

