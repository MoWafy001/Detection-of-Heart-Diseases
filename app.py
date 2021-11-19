from dotenv import load_dotenv
load_dotenv()

from os import abort, error
from models import db, Patient, app
from flask import request, redirect, url_for, render_template, session, abort
import datetime
import os
from flask_mail import Mail, Message
import jwt

app.secret_key = b'#ZRfeuPY^+f]1P|'

sender_mail = os.getenv('MAIL_USERNAME')
forgot_password_secret = os.getenv('forgot_password_secret')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = sender_mail
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


@app.post("/sendForgotEmail")
def email():
    email = request.json.get("email")
    if email is None:
        abort(400)

    patient = Patient.query.filter(Patient.email == email).first()
    if patient is None:
        abort(404)

    encoded_jwt = jwt.encode({"patient_id": patient.id},
                             forgot_password_secret, algorithm="HS256")

    print(encoded_jwt, request.host_url, request.host)

    msg = Message('Reset password',
                  sender=sender_mail, recipients=[email])
    msg.body = f"""
        Hey {patient.first_name},
        Here is a link to reset your password

        {request.host_url}resetpassword/{encoded_jwt}
    """
    # print(msg.body)
    mail.send(msg)
    return "Message sent!"


@app.get("/resetpassword/<token>")
def resetPassword(token):

    newPassword = request.args.get('new-password')

    try:
        patient_id = jwt.decode(token, forgot_password_secret,
                             algorithms=["HS256"])['patient_id']
        print(patient_id)
    except Exception as e:
        print(str(e))
        return "invalid link"

    try:
        patient = Patient.query.get(patient_id)
        if patient is None:
            raise "error"
    except Exception as e:
        print(str(e))
        return "could find the patient"

    if newPassword is None:
        return render_template("Forgot_password.html")

    try:
        patient.password = newPassword
        db.session.commit()
    except Exception as e:
        print(str(e))

    return redirect(url_for("signin", msg="password reset successfully!"))


@app.route("/")
def index():
    return redirect("/signup")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        error = request.args.get("error")
        return render_template("DHD_Sign_Up.html", error=error)

    else:
        print(request.form)
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            first_name = request.form.get('namef')
            last_name = request.form.get('namel')
            age = datetime.datetime.now().year - \
                int(request.form.get('birth').split("-")[0])
            gender = request.form.get('Type')

            if None in [email, password, first_name, last_name, age, gender]:
                raise "error"
        except Exception as e:
            print(str(e))
            return redirect(url_for("signup", error="invalid input or fields missing"))

        gender = gender == "Male"

        try:
            db.session.add(Patient(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                age=age,
                gender=gender,
            ))
            db.session.commit()
        except Exception as e:
            print(str(e))
            return redirect(url_for("signup", error="some error happened. Make sure the email has not been used before"))

        return redirect("/signin")


@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        msg = request.args.get("msg")
        print(session)
        return render_template("DHD_Log_in.html", msg=msg)

    else:
        print(request.form)
        email = request.form.get('email')
        password = request.form.get('password')

        if None in [email, password]:
            return redirect(url_for('signin', msg="fields missing"))

        patient = Patient.query.filter(
            Patient.email == email, Patient.password == password).first()

        if patient is None:
            return redirect(url_for('signin', msg="Invalid credentials"))

        session['patient_id'] = patient.id
        session['patient_email'] = patient.email

        return redirect(url_for('signin', msg="Login was successful!"))


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", 5000))
