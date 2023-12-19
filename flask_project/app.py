from flask import Flask, render_template, request, session
from random import randint
from smtplib import SMTP
from flask_mysqldb import MySQL
app = Flask(__name__)
app.secret_key = 'wertyui'

#----------MySQL Config------------
app.config['MYSQL_USER'] = 'dev'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'pes_students'

mysql = MySQL(app)


@app.route('/')
def index():
    if session.get('email'):
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/contact')
def contact():
    if session.get('email'):
        return render_template('contact.html')
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        if request.form.get('repassword') == request.form.get('password'):

            # fetch data from HTML form
            # set() - empty set
            global user_data
            user_data = {} #empty dictionary
            # user_data[new_key] = new_value # adding key value
            user_data['full_name'] = request.form.get('full_name')
            user_data['email'] = request.form.get('email')
            user_data['password'] = request.form.get('password')
            

            # generate OTP
            global c_otp
            c_otp = randint(100_000,999_999)
            message = f"Hello {user_data['full_name']}, your OTP is {c_otp}"


            # send OTP mail
            mail_obj = SMTP('smtp.gmail.com', 587)
            mail_obj.starttls()
            mail_obj.login('devangsingh101@gmail.com','lemdqvvzjcryivfv')
            mail_obj.sendmail('devangsingh101@gmail.com', user_data['email'], message)

            # render OTP page
            return render_template('otp.html')
        else:
            return render_template('otp.html', message="Both OTPs didn't match")


@app.route('/otp', methods=['POST', 'GET'])
def otp():
    if request.method == 'POST':
        if str(c_otp) == request.form.get('u_otp'):
            # create a row in our database
            cur = mysql.connection.cursor()
            sql_query = f"insert into students values ({c_otp},'{user_data['full_name']}', '{user_data['email']}', '{user_data['password']}');"
            cur.execute(sql_query) # SQL query
            cur.connection.commit()
            cur.close()
            return render_template('register.html', message='successfully created!!!')
        else:

            return render_template('otp.html', message='Invalid OTP')
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u_email = request.form.get('email')
        u_password = request.form.get('password')

        query = f"select full_name, email, password from students where email = '{u_email}'"
        cur = mysql.connection.cursor()
        cur.execute(query)
        one_record = cur.fetchone()
        if one_record:
            # yes that email EXISTS
            if one_record[2] == u_password:
                #start a session
                session['email'] = u_email
                return render_template('index.html')

                
            else:
                return render_template('login.html', message='incorrect password!!')
        else:
            # it does not exist
            return render_template('login.html', message='Invalid Email ID')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['email']
    return render_template('login.html')


        


if __name__ == '__main__':
    app.run(debug=1)