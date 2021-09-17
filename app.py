from flask import Flask, redirect, render_template, url_for, request, session, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import random

import os
import cv2
from werkzeug.utils import secure_filename

import xlrd

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'xls'}

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

def upload_file(file):
	msg=""
	savepath=""
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		savepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(savepath)
		msg="File saved"
	return msg, savepath

def saveToDb(qid1,file):
	cursor = mysql.connection.cursor()
	excel_sheet = xlrd.open_workbook(file)
	sheet_name = excel_sheet.sheet_names()
	insert_query = "INSERT INTO questions (qid,question,op1,op2,op3,op4,cans) VALUES (%s,%s,%s,%s,%s,%s,%s)"
	for sh in range(0,len(sheet_name)):
		sheet= excel_sheet.sheet_by_index(sh)		
		for r in range(1,sheet.nrows):
			question = sheet.cell(r,0).value
			op1 = sheet.cell(r,1).value
			op2 = sheet.cell(r,2).value		
			op3 = sheet.cell(r,3).value		
			op4 = sheet.cell(r,4).value			
			cans = sheet.cell(r,5).value			
			vals = (qid1,question,op1,op2,op3,op4,cans)
			cursor.execute(insert_query,vals)
			mysql.connection.commit()
	cursor.close()

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
			print(logdata)
			cur.close()
			if logdata:
				session['loggedin'] = True
				session['name'] = logdata[1]
				session['uid']=logdata[0]
				return redirect('/')
			else:
				msg = "Incorrect username or password !! "
				return render_template('teacherLogin.html', msg = msg)
		return render_template('teacherLogin.html', msg = msg)

@app.route('/')
def home():
	if 'loggedin' in session:
		return render_template('teacherHome.html')
	else:
		return redirect('/login')



@app.route('/createQuiz', methods = ['GET', 'POST'])
def createQuiz():
	if 'loggedin' in session:
		msg=''
		if request.method == 'POST':
			details = request.form
			uid=session['uid']
			name=details['quizname']
			time=details['time']
			file=request.files['questionsfile']
			qid1=random.randint(10000000,99999999)
			msg,filepath=upload_file(file)
			print(msg)
			saveToDb(qid1,filepath)
			cursor = mysql.connection.cursor()
			cursor.execute("insert into quizes (id, quizid, quizname, time) values (%s,%s,%s,%s)",(uid,qid1,name,time))
			mysql.connection.commit()
			cursor.close()
			msg="Quiz created successfully!"
			return render_template("creatQuiz.html",msg=msg)
		return render_template("creatQuiz.html",msg=msg)
	else:
		return redirect('/login')
    


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('name', None)
    return redirect('/login')

#------------------------##------------------------##------------------------##------------------------#
#                                STUDENT PART                                                          #
#------------------------##------------------------##------------------------##------------------------#     

@app.route('/register')
def studentRegister():
    return render_template("studentRegister.html")

@app.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    return render_template("studentQuiz.html")

@app.route('/results')
def results():
    return render_template("studentResults.html")

def gen_frames():
	camera = cv2.VideoCapture(0)  
	while True:
		success, img = camera.read()  # read the camera frame
		face_rects=face_cascade.detectMultiScale(img,1.2,5)
		for (x,y,w,h) in face_rects:
			cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
			# encode OpenCV raw frame to jpg and displaying it
		ret, jpeg = cv2.imencode('.jpg', img)
		frame = jpeg.tobytes()
		yield (b'--frame\r\n'
		       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  
#------------------------##------------------------##------------------------##------------------------#
# @app.errorhandler(404)
# def page_not_found( error ) :
#     return render_template("error.html", error_msg = "404, Sorry Page not found"), 404
#
#
# @app.errorhandler(400)
# def bad_request( error ) :
#     return render_template("error.html",
#                            error_msg = "Yeahhh, the server couldn't understand what you asked for, Sorry"), 400

if __name__ == '__main__':
    app.run(debug = True)