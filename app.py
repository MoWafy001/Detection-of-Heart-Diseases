import jwt
from flask_mail import Mail, Message
import os
import datetime
from flask import request, redirect, url_for, render_template, session, abort, jsonify, Response
from models import db, Patient, app
from prediction import predict_disease, predict_percentage


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
        session['patient_first_name'] = patient.first_name

        return redirect(url_for('analyse'))


@app.route('/analyse', methods=['GET', 'POST'])
def analyse():
    if 'patient_id' not in session.keys() or not session['patient_id']:
        return redirect("/signin")

    if request.method == 'GET':
        return render_template("Analyse.html")

    # if POST
    print(request.json)
    try:
        cp = request.json.get('chest-pain')
        cp = Patient.map_cp(cp)
        trestbps = int(request.json.get('Resting Blood Pressure'))
        chol = int(request.json.get('Serum Cholesterol'))
        fbs = request.json.get('Fasting Blood Sugar') == 'on'
        restecg = request.json.get('Resting')
        restecg = Patient.map_restecg(restecg)
        thalach = int(request.json.get('heart rate'))
        exang = request.json.get('Exercise') == "on"
        oldpeak = int(request.json.get('depression'))
        slope = request.json.get('peak')
        slope = Patient.map_slope(slope)
        ca = int(request.json.get('major'))
        thal = request.json.get('thal')
        thal = Patient.map_thal(thal)

        if None in [cp, trestbps, chol, fbs, restecg,
                    thalach, exang, oldpeak, slope,
                    ca, thal]:
            raise Exception('error')

        print([cp, trestbps, chol, fbs, restecg,
               thalach, exang, oldpeak, slope,
               ca, thal])
    except Exception as e:
        print(str(e))
        abort(Response('invalid fields', 400))

    try:

        patient = Patient.query.get(session['patient_id'])

        data = [patient.age, patient.gender, cp, trestbps, chol, fbs,
                restecg, thalach, exang, oldpeak, slope, ca, thal]

        has_disease = predict_disease(data)
        degree = None

        if has_disease:
            degree = predict_percentage(data)

        patient.cp = cp
        patient.trestbps = trestbps
        patient.chol = chol
        patient.fbs = fbs
        patient.restecg = restecg
        patient.thalach = thalach
        patient.exang = exang
        patient.oldpeak = oldpeak
        patient.slope = slope
        patient.ca = ca
        patient.thal = thal

        patient.status = has_disease
        patient.degree = degree

        db.session.commit()
    except Exception as e:
        print(str(e))
        abort(Response("some error happened", 500))

    return jsonify({
        "status": bool(has_disease),
        "degree": degree
    })


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", 5000))
