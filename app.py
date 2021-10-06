from flask import Flask, redirect, render_template, url_for, request, session, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import random

from datetime import datetime
import time

import os
import cv2
from werkzeug.utils import secure_filename

from pyexcel_xls import get_data

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'xls','xlsx', 'xlsm'}

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shivam5606'
app.config['MYSQL_DB'] = 'pythonProject'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "safehouse"

mysql = MySQL(app)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file,uid,qid):
	msg=False
	savepath=""
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		filename=str(uid)+"_"+str(qid)+"_"+filename
		savepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(savepath)
		msg=True
	return msg, savepath

def saveToDb(qid1,file):
	cursor = mysql.connection.cursor()
	excel_sheet = get_data(file)
	insert_query = "INSERT INTO questions (qid,questionid,question,op1,op2,op3,op4,cans) VALUES (%s,%s  ,%s,%s,%s,%s,%s,%s)"
	for lst in excel_sheet['Sheet1']:
		questionid=random.randint(1000000000,9999999999)
		question = lst[0]
		op1 = lst[1]
		op2 = lst[2]	
		op3 = lst[3]		
		op4 = lst[4]		
		cans = lst[5]			
		vals = (qid1,questionid,question,op1,op2,op3,op4,cans)
		cursor.execute(insert_query,vals)
		mysql.connection.commit()
	cursor.close()

@app.route('/')
def mainHome():
	if 'loggedin' not in session:
		return render_template('mainHome.html')
	else:
		return redirect(url_for('teacherHome'))

@app.route('/login', methods = ['GET', 'POST'])
def teacherLogin():
	if 'loggedin' in session:
		return redirect('/')
	else:
		msg = ""
		if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
			details = request.form
			email = details['email']
			password = details['password']
			cur = mysql.connection.cursor()
			cur.execute('select * from teachers where email = %s and password = %s', (email, password))
			logdata = cur.fetchone()
			cur.close()
			if logdata:
				session['loggedin'] = True
				session['teachername'] = logdata[1]
				session['uid']=logdata[0]
				return redirect(url_for('teacherHome'))
			else:
				msg = "Incorrect username or password !! "
				return render_template('teacherLogin.html', msg = msg)
		return render_template('teacherLogin.html', msg = msg)

@app.route('/home')
def teacherHome():
	if 'loggedin' in session:
		cur = mysql.connection.cursor()
		cur.execute('select * from quizes where id = %s', (session['uid'],))
		logdata = cur.fetchall()
		print(logdata)
		return render_template('teacherHome.html',quizdata=logdata)
	else:
		return redirect(url_for('teacherLogin'))



@app.route('/createQuiz', methods = ['GET', 'POST'])
def createQuiz():
	if 'loggedin' in session:
		msg=''
		if request.method == 'POST':
			details = request.form
			uid=session['uid']
			name=details['quizname']
			time=details['time']
			time1=details['time1']
			format = '%Y-%m-%dT%H:%M' # The format
			time = datetime.strptime(time, format)
			time1 = datetime.strptime(time1, format)
			# print(time,time1)
			if time>time1 or time==None or time1==None:
				return render_template("creatQuiz.html",msg="Please Enter the time properly")
			file=request.files['questionsfile']
			qid1=random.randint(10000000,99999999)
			msg,filepath=upload_file(file,uid,qid1)
			# print(msg)
			if msg:
				saveToDb(qid1,filepath)
			else:
				return render_template("creatQuiz.html",msg="Some error occurred while uploading the file!")
			cursor = mysql.connection.cursor()
			cursor.execute("insert into quizes (id, quizid, quizname, time,endtime) values (%s,%s,%s,%s,%s)",(uid,qid1,name,time,time1))
			mysql.connection.commit()
			cursor.close()
			msg="Quiz created successfully!"
			return render_template("creatQuiz.html",msg=msg)
		return render_template("creatQuiz.html",msg=msg)
	else:
		return redirect(url_for("teacherLogin"))
    


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('teachername', None)
    return redirect(url_for('mainHome'))

#------------------------##------------------------##------------------------##------------------------#
#                                STUDENT PART                                                          #
#------------------------##------------------------##------------------------##------------------------#     

@app.route('/studentRegister', methods = ['GET', 'POST'])
def studentRegister():
	msg=""
	if "studentloggedin" not in session:		
		if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'quizcode' in request.form:
			details = request.form
			name = details['name']
			email = details['email']
			quizcode = details['quizcode']
			cur = mysql.connection.cursor()
			cur.execute('select * from quizes where quizid = %s', (quizcode,))
			logdata = cur.fetchone()
			if logdata:
				x = datetime.now()
				if logdata[3]>x or logdata[4]<=x:
					return render_template('studentRegister.html', msg = "Please check the quiz time properly.")
			
				cur.execute('select * from students where email = %s and quizid = %s', (email, quizcode))
				studata=cur.fetchone()
				if studata:
					msg="It seems you already attempted the test."
					return render_template('studentRegister.html', msg = msg)
				else:
					cur.execute('insert into students(quizid,name,email) values (%s,%s,%s)',(quizcode,name, email))
					mysql.connection.commit()
					
					session['studentloggedin'] = True
					session['name'] = (name,email)
					session['quizid']=quizcode
					session['endtime']=logdata[4].strftime("%d/%m/%Y, %H:%M:%S")
					print(logdata[4])
					return redirect('/studentQuiz')
			else:
				msg = "The quiz doesn't exist. Please insert the correct quiz id!"
		return render_template('studentRegister.html', msg = msg)
	else:
		return redirect(url_for('studentQuiz'))


@app.route('/studentQuiz', methods = ['GET', 'POST'])
def studentQuiz():
	if 'studentloggedin' in session:
		cur = mysql.connection.cursor()
		cur.execute('select * from questions where qid = %s', (session['quizid'],))
		questions = cur.fetchall()
		cur.execute('select * from studentans where quizid = %s and email=%s', (session['quizid'],session['name'][1],))
		check = cur.fetchall()
		if check:
			return render_template("studentQuiz.html",questions=questions)
		# print(questions)
		for i in questions:
			cur.execute('insert into studentans(quizid,email,questionid,cans) values (%s,%s,%s,%s)',(session['quizid'],session['name'][1], i[7],i[6]))
			mysql.connection.commit()
		return render_template("studentQuiz.html",questions=questions)
	else:
		return redirect('/studentRegister')

@app.route('/studentResults', methods = ['GET', 'POST'])
def studentResults():
	if 'studentloggedin' in session:
		if request.method == 'POST':
			cur = mysql.connection.cursor()
			details = request.form
			# print(details)
			for i in details:
				questionid=details[i][:10]
				useroption=details[i][11:]
				cur.execute('update studentans set userans=%s where questionid=%s and email=%s',(useroption,questionid,session['name'][1]))
				mysql.connection.commit()
			cur.execute('select * from studentans where quizid = %s and email=%s', (session['quizid'],session['name'][1],))
			userdata = cur.fetchall()
			result=0
			count1=0
			for i in userdata:
				if i[3]==i[4]:
					result+=1
				count1+=1
			finalResult=str(result)+'/'+str(count1)
			cur.execute('update students set result=%s where quizid=%s and email=%s',(finalResult,session['quizid'],session['name'][1]))
			mysql.connection.commit()
			cur.execute('select * from quizes where quizid = %s', (session['quizid'],))
			quizname=cur.fetchone()
			quizname=quizname[2]
			sname=session['name'][0]
			id1=session['quizid']
			session.pop('studentloggedin',None)
			session.pop('name',None)
			session.pop('quizid',None)
			session.pop('endtime',None)
			return render_template("studentResults.html",res=finalResult,quizname=quizname,sname=sname,id1=id1)
	return redirect('/studentRegister')


def gen_frames():
	camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)  
	while True:
		success, img = camera.read()  # read the camera frame
		if success:
			face_rects=face_cascade.detectMultiScale(img,1.2,5)
			for (x,y,w,h) in face_rects:
				cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
				# encode OpenCV raw frame to jpg and displaying it
			ret, jpeg = cv2.imencode('.jpg', img)
			frame = jpeg.tobytes()
			time.sleep(2)
			yield (b'--frame\r\n'b'Cont  ent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		else:
			print("camera not found")
			return "Camera not found"

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  
#------------------------##------------------------##------------------------##------------------------#
# @app.errorhandler(404)
# def page_not_found( error ) :
#     return render_template("error.html", error_msg = "404, Sorry Page not found"), 404


# @app.errorhandler(400)
# def bad_request( error ) :
#     return render_template("error.html",
#                            error_msg = "Yeahhh, the server couldn't understand what you asked for, Sorry"), 400

if __name__ == '__main__':
    app.run(debug = True)