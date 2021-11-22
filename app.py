from logging import debug
import jwt
from flask_mail import Mail, Message
import os
import datetime
from flask import request, redirect, url_for, render_template, session, abort, jsonify, Response
from models import Doctor, db, Patient, app
from prediction import predict_disease, predict_percentage
from flask_socketio import SocketIO, emit, join_room, leave_room

app.secret_key = b'#ZRfeuPY^+f]1P|'

sender_mail = os.getenv('MAIL_USERNAME')
forgot_password_secret = os.getenv('forgot_password_secret')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = sender_mail
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = '%^qe123ASDasd881_asd!'

socketio = SocketIO(app)

mail = Mail(app)

waiting_list = {}


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
            doctor = Doctor.query.filter(
                Doctor.email == email, Doctor.password == password).first()

            if doctor is None:
                return redirect(url_for('signin', msg="Invalid credentials"))
            else:
                if 'patient_id' in session.keys():
                    session.pop('patient_id')
                session['doctor_id'] = doctor.id
                session['doctor_email'] = doctor.email
                session['doctor_first_name'] = doctor.first_name

                return redirect('/doctor/0')
        else:
            if 'doctor_id' in session.keys():
                session.pop('doctor_id')
            session['patient_id'] = patient.id
            session['patient_email'] = patient.email
            session['patient_first_name'] = patient.first_name

        return redirect(url_for('analyse'))


@app.get('/doctor')
def red_doc():
    return redirect("/doctor/0")


@app.get('/doctor/<int:index>')
def doctor(index):
    if 'doctor_id' not in session.keys() or not session['doctor_id']:
        return redirect("/signin")

    last = False

    waiting = list(set(waiting_list.values()))

    if len(waiting) == 0 or index+1 > len(waiting):
        nindex = index - len(waiting)
        try:
            patient = Patient.query.filter(
                Patient.doctor_id == session['doctor_id'])
            last = nindex == patient.count()-1
            patient = patient.limit(1).offset(nindex).first()
            print(patient)
        except Exception as e:
            print(str(e))
            print('error')

    else:
        last = index == len(waiting) + Patient.query.filter(
            Patient.doctor_id == session['doctor_id']).count() -1
        patient = Patient.query.get(waiting[index])
        print(patient)

    if patient is not None:
        return render_template('doctorPage.html', patient_first_name=patient.first_name, patient_last_name=patient.last_name,
                               patient_age=patient.age, patient_cp=Patient.reverse_map_cp(patient.cp), patient_trestbps=patient.trestbps,
                               patient_chol=patient.chol, patient_fbs="Fasting Blood Sugar > 120 mg/dl" if patient.fbs else "Fasting Blood Sugar <= 120 mg/dl", patient_restecg=Patient.reverse_map_restecg(patient.restecg),
                               patient_thalach=patient.thalach, patient_exang=patient.exang, patient_oldpeak=patient.oldpeak,
                               patient_slope=Patient.reverse_map_slope(patient.slope), patient_ca=patient.ca, patient_thal=Patient.reverse_map_thal(patient.thal),
                               patient_sex="Male" if patient.gender else "Female", patient_id=patient.id, index=index, last=last)
    else:
        return "No Cases"


@app.route('/analyse', methods=['GET', 'POST'])
def analyse():
    if 'patient_id' not in session.keys() or not session['patient_id']:
        return redirect("/signin")

    if request.method == 'GET':
        return render_template("Analyse.html", patient_id=session['patient_id'])

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


@app.get('/video/<int:patient_id>')
def video(patient_id):
    if not (('patient_id' in session.keys() and patient_id == session['patient_id'])
            or ('doctor_id' in session.keys() and session['doctor_id'])):
        return redirect('/signin')

    if 'patient_id' in session.keys():
        return render_template('video.html', patient_id=patient_id)
    else:
        return render_template('video.html')


@socketio.on('waiting')
def add_to_waiting(patient_id, socket_id):
    waiting_list[socket_id] = patient_id
    print(waiting_list)


@socketio.on('disconnect')
def remove_from_waiting():
    if request.sid in waiting_list.keys():
        waiting_list.pop(request.sid)
    print(waiting_list)


@socketio.on('join')
def handel_join(peer_id):
    print(request.headers['Referer'])
    join_room(request.headers['Referer'])
    emit("user-joined", peer_id, broadcast=True, include_self=False, room=request.headers['Referer'])


if __name__ == "__main__":
    # app.run(debug=True, port=os.getenv("PORT", 5000))
    socketio.run(app, debug=True, port=os.getenv("PORT", 5000))
