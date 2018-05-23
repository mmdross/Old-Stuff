import pdb
import MySQLdb
import math
from flask import Flask
import datetime

#server information:
url = "sql8.freemysqlhosting.net"
username = "sql8162831"
password = "6YRgu8LHLh"
db_name =  "sql8162831" 

db = MySQLdb.connect(url, username, password, db_name)
cursor = db.cursor()

def recalc_time():
	cursor.execute("SELECT bar_id FROM VENUES")
	bars = cursor.fetchall()
	for i in bars:
		cursor.execute("SELECT * FROM REPORTS WHERE bar_id=%s AND time_recent >= NOW() - INTERVAL 30 MINUTE", (i))
		results = cursor.fetchall()
		if results:
			pass
		else:
			cursor.execute("SELECT CAST(NOW() as char)")
			results = cursor.fetchone()[0]
			results = results.split(' ')[1]
			hour = results.split(':')[0]
			minute = results.split(':')[1]
			set_length_predictive(hour, minute, i)

def recalc_report():
	cursor.execute("SELECT bar_id FROM VENUES")
	bars = cursor.fetchall()
	for i in bars:
		cursor.execute("SELECT bar_id, time_in, time_recent, time_out FROM REPORTS WHERE bar_id=%s AND time_recent >= NOW() - INTERVAL 10 MINUTE", (i))
		results = cursor.fetchall()
		if not results:
			pass
		else:
			average_time = 0
			count = 0
			for j in results:
				bar_id = j[0]
				curtime = j[2] - j[1]
				time_recent = j[2]
				time_out = j[3]

				time_out = str(time_out)
				time_recent = str(time_recent)
				curtime = str(curtime)

				curtime = curtime.split(':', 2)[1]
				curtime_int = int(curtime)

				cursor.execute("SELECT CONVERT(line_status,char) FROM VENUES WHERE bar_id=%s", (bar_id))
				status = cursor.fetchone()[0]

				if curtime_int <= int(status):
					if time_out == time_recent:
						average_time += curtime_int
						count += 1
				else:
					average_time += curtime_int
					count += 1
			if count > 0:
				average_time /= count
				cursor.execute("UPDATE VENUES SET line_status=%s WHERE bar_id=%s", (average_time, bar_id))
				db.commit();
		

def recalc_est(): 
	cursor.execute("SELECT bar_id FROM VENUES")
	bars = cursor.fetchall()
	for i in bars:
		cursor.execute("SELECT bar_id, CONVERT(num_people,char) FROM REPORTS WHERE bar_id=%s AND time_recent >= NOW() - INTERVAL 10 MINUTE", (i))
		results = cursor.fetchall()
		if not results:
			pass
		else:
			average_people = 0
			count = 0
			for j in results:
				bar_id = j[0]
				num_people = int(j[1])
				average_people += num_people
				count += 1
			if count > 0:
				average_people /= count
				cursor.execute("UPDATE VENUES SET num_people=%s WHERE bar_id=%s", (average_people, bar_id))
				db.commit();
	
def set_length_predictive(hour, minute, bar):
	time = (int(hour)*60+int(minute))/60

	cursor.execute("SELECT DAYOFWEEK(NOW())")
	dayresults = cursor.fetchone()[0]
	day = get_day(dayresults)

	bar = int(bar[0])

	cursor.execute("SELECT * FROM PREDICTIONS WHERE venue_id=%s AND day_of_week=%s", (bar, day))
	results = cursor.fetchall()

	if not results:
		cursor.execute("UPDATE VENUES SET line_status=-1 WHERE bar_id=%s", (bar))
		db.commit()

	else:
		if 19 <= time < 19.5:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.sev_30 FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  19.5 <= time < 20:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.eight FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  20 <= time < 20.5:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.eight_30 FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  20.5 <= time < 21:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.nine FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  21 <= time < 21.5:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.nine_30 FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  21.5 <= time < 22:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.ten FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  22 <= time < 22.5:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.ten_30 FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  22.5 <= time < 23:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.elev FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  23<= time < 23.5:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.elev_30 FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  23.5 <= time < 24:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.twel FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  0 <= time < 0.5:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.twel_30 FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  0.5 <= time < 1:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.onee FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		elif  1 <= time < 1.5:
			cursor.execute("UPDATE VENUES SET line_status=(SELECT PREDICTIONS.onee_30 FROM PREDICTIONS WHERE PREDICTIONS.venue_id=%s AND PREDICTIONS.day_of_week=%s)) WHERE bar_id=%s", (bar, day, bar))
			db.commit()
		else:
			cursor.execute("UPDATE VENUES SET line_status=0 WHERE bar_id=%s", (bar))
			db.commit()

def get_day(num):
	if num==0:
		return "Sunday"
	elif  num==1:
		return "Monday"
	elif  num==2:
		return "Tuesday"
	elif  num==3:
		return "Wednesday"
	elif  num==4:
		return "Thursday"
	elif  num==5:
		return "Friday"
	elif  num==6:
		return "Saturday"
	else:
		return "BROKEN"