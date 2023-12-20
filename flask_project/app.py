from flask import Flask, render_template, request, session, redirect, url_for
from random import randint
from smtplib import SMTP
from flask_mysqldb import MySQL
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'wertyui'

#----------File Upload Config-------
app.config['UPLOAD_FOLDER'] = 'static/blog_photos/'


#----------MySQL Config------------
app.config['MYSQL_USER'] = 'dev'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'pes_students'

mysql = MySQL(app)


@app.route('/')
def index():
    if session.get('email'):
        # retrive all blogs from db
        cur = mysql.connection.cursor()
        sql_query = "SELECT blogs.blog_title, blogs.blog_des, blogs.blog_image, students.full_name, blogs.datetime FROM blogs INNER JOIN students ON blogs.blog_owner=students.id;"
        cur.execute(sql_query)
        data_from_db = cur.fetchall()
        print(data_from_db)
        cur.close()

        # fetch session user info
        cur = mysql.connection.cursor()
        sql_query = f"SELECT full_name from students where email = '{session['email']}';"
        cur.execute(sql_query)
        session_user_full_name = cur.fetchone()
        cur.close()

        return render_template('index.html', all_blogs = data_from_db, session_user_name = session_user_full_name)
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

                return redirect(url_for('index'))

                
            else:
                return render_template('login.html', message='incorrect password!!')
        else:
            # it does not exist
            return render_template('login.html', message='Invalid Email ID')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['email']
    return render_template('login.html')


@app.route('/add_blog', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'GET':
        return render_template('add_blog.html')
    else:
        #upload a blog
        # CREATE TABLE blogs (blog_id int NOT NULL AUTO_INCREMENT, blog_title varchar(255), blog_des text(65535), blog_image varchar(255), blog_owner int, PRIMARY KEY(blog_id), FOREIGN KEY(blog_owner) REFERENCES students(id) );
        b_title = request.form.get('title')
        b_des = request.form.get('des')
        b_file_obj = request.files['blog_pic']
        b_filename = b_file_obj.filename
        #below line will save image file in the folder
        b_file_obj.save(os.path.join(app.config['UPLOAD_FOLDER'], b_filename))

        cur = mysql.connection.cursor()
        #fetch current time
        current_dt = str(datetime.now())

        #fetch current user ID(session user)
        session_user_email = session['email']
        cur.execute(f"select id from students where email = '{session_user_email}'")
        session_user_li = cur.fetchone()
        session_user_id = session_user_li[0]

        #saving info in the db/ creating a record in blogs
        sql_query = f"insert into blogs (blog_title, blog_des, blog_image, blog_owner, datetime ) values ('{b_title}','{b_des}', '{b_filename}', {session_user_id}, '{current_dt}');"
        cur.execute(sql_query) # SQL query
        cur.connection.commit()
        cur.close()



        return render_template('add_blog.html', message='Blog has been successfully added!!')


        
@app.route('/my_blogs')
def my_blogs():
    # exctract only session user's blogs
    session_user_email = session['email']
    cur = mysql.connection.cursor()
    sql_query = f"SELECT blogs.blog_title, blogs.blog_des, blogs.blog_image, students.full_name, blogs.datetime FROM blogs INNER JOIN students ON blogs.blog_owner=students.id WHERE students.email = '{session_user_email}';"
    cur.execute(sql_query)
    my_blogs = cur.fetchall()
    cur.close()
    return render_template('my_blogs.html', all_my_blogs = my_blogs)

#search bar query
# select * from blogs where blog_title in request.form.get('search_bar_name')


if __name__ == '__main__':
    app.run(debug=True)