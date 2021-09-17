from flask import Flask, redirect, render_template, url_for, request, session, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import random

import os
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shivam5606'
app.config['MYSQL_DB'] = 'pythonProject'

app.secret_key = "safehouse"

mysql = MySQL(app)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') 

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
    return render_template("creatQuiz.html")


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