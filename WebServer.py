from flask import Flask, jsonify, flash, redirect, render_template, request, session, abort
import os
import pymysql as MySQLdb
import json
from datetime import datetime
from waitress import serve

import pandas as pd
import numpy as np
import webbrowser

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('criminal_list.html')

@app.route('/crimdetails')
def crimdetails():    
    #post = request.form.to_dict()
    #crimid = str(post['crimid'])
    crimid=request.args.get('cid')    
    session['crimid']=crimid
    #webbrowser.open_new_tab('/templates/CriminalDetails.html')    
    to_send={'status': '0', 'error': 'null'}
    return render_template('CriminalDetailsUI1.html')

@app.route('/crimdetailsfromlist', methods=["POST", "GET"])
def crimdetailsfromlist():    
    post = request.get_json()
    crimid = str(post.get('crimid'))    
    session['crimid']=crimid
    #webbrowser.open_new_tab('/templates/CriminalDetails.html')    
    to_send={'status': '0', 'error': 'null'}
    webbrowser.open_new_tab('http://127.0.0.1:5000/crimdetails?cid='+crimid)
    return to_send

@app.route('/getCriminalsList', methods=["POST", "GET"])
def getCriminalsList():
    db = MySQLdb.connect("localhost", "root", "", "criminal")
    cursor = db.cursor()
    cursor.execute("select `cam_id`,`criminal_id`,`date`,`time` from criminal_list order by date desc")
    data = cursor.fetchall()
    to_send = []
    for row in data:
        camid=row[0]
        crimid=row[1]
        cursor.execute("select `place` from cam_details where cam_id=%d"%(camid))
        camdata=cursor.fetchall()
        cursor.execute("select `cname` from criminals where cid='%s'"%(crimid))
        crimdata=cursor.fetchall()
        date=row[-2]
        time=row[-1]
        s=time.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        t='{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        date = date.strftime('20%y-%m-%d')
        to_send.append({'name':crimdata[0][0],'place':camdata[0][0],'date':date,'time':t,'cid':crimid}) 
    return jsonify(result=to_send)

@app.route('/getText', methods=["POST", "GET"])
def getText():
    post = request.form.to_dict()
    to_send = {'status': '0', 'error': 'null'}
    letter = str(post['letter'])
    db = MySQLdb.connect("localhost", "root", "", "criminal")
    cursor = db.cursor()
    cursor.execute("update crimLetter set `name`= '%s'"%(letter))
    to_send["status"] = "1"
    to_send["error"] = "Password Changed Successfully!"
    return to_send

@app.route('/getCriminalsDetails', methods=["POST", "GET"])
def getCriminalsDetails():
    crimid=session['crimid']
    db = MySQLdb.connect("localhost", "root", "", "criminal")
    cursor = db.cursor()
    cursor.execute("select `cname`,`caddress`,`cage`,`cphone` from criminals where cid='%s'"%(crimid))
    data = cursor.fetchall()
    to_send = []
    for row in data:
        to_send.append({'cid':crimid,'cname':row[0],'caddress':row[1],'cage':row[2],'cphone':row[3]})
    cdet=[]
    cursor.execute("select `crime`,`place`,`date`,`time` from crime_history where cid='%s' order by date desc"%(crimid))
    data = cursor.fetchall()
    for row in data:
        date = row[2]
        time=row[-1]
        s=time.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        t='{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        date = date.strftime('20%y-%m-%d')
        cdet.append({'crime': row[0], 'place': row[1], 'date': date, 'time': t}) 
    to_send[0]['cdetails']=cdet    
    cursor.execute("select cam_id from criminal_list where criminal_id='%s' order by date desc,time desc"%(crimid))
    data=cursor.fetchall()
    loc=[]
    for i in data:
        camid=i[0]
        cursor.execute("select place,latitude,longitude from cam_details where cam_id=%d"%(camid))
        loc_data=cursor.fetchall()[0]
        loc.append({'place':loc_data[0],'latitude':loc_data[1],'longitude':loc_data[2]})
    to_send[0]['locations']=loc    
    return jsonify(result=to_send)

@app.route('/insertCrimList', methods=["POST", "GET"])
def insertCrimList():
    db = MySQLdb.connect("localhost", "root", "", "criminal")
    cursor = db.cursor()
    post = request.form.to_dict()
    crimid = str(post['crimid'])
    camid = str(post['cam_id'])
    stime = str(post['time'])
    sdate = str(post['date'])
    print(crimid,camid,stime,sdate)
    cursor.execute("insert into criminal_list (`date`, `time`, `cam_id`, `criminal_id`) values('%s','%s','%s','%s')"%(sdate,stime,camid,crimid))
    #webbrowser.open_new_tab('http://127.0.0.1:5000/crimdetails?cid='+crimid)
    to_send = {'status': '1'}
    return jsonify(result=to_send)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    #serve(app, host='0.0.0.0', port=8080)
    app.run(threaded=True,debug=True)
