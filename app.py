from flask import Flask, redirect, render_template, url_for, request, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import random

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''

app.secret_key = "safehouse"

mysql = MySQL(app)

@app.route('/login', methods = ['GET', 'POST'])
def teacherLogin():
    return render_template("teacherLogin.html")

@app.route('/')
def home():
    return render_template("teacherHome.html")

@app.route('/createQuiz', methods = ['GET', 'POST'])
def createQuiz():
    return render_template("creatQuiz.html")

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


#------------------------##------------------------##------------------------##------------------------#
if __name__ == '__main__':
    app.run(debug = True)