from flask import Flask, render_template, request
from random import randint
from smtplib import SMTP
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

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
            return "BOTH passwords are not matched"


@app.route('/otp', methods=['POST', 'GET'])
def otp():
    if request.method == 'POST':
        if c_otp == request.form.get('u_otp'):
            pass
            # create a row in our database
        else:
            return render_template('otp.html', data={'message':'invalid OTP'})





        


if __name__ == '__main__':
    app.run(debug=1)