from os import error
from models import db, User, app
from flask import request, redirect, url_for, render_template, session
import datetime
import os

app.secret_key = b'#ZRfeuPY^+f]1P|'

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
            db.session.add(User(
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

        user = User.query.filter(User.email == email, User.password == password).first()

        if user is None:
            return redirect(url_for('signin', msg="Invalid credentials"))

        session['user_id'] = user.id
        session['user_email'] = user.email

        return redirect(url_for('signin', msg="Login was successful!"))


if __name__ == "__main__":
    app.run(port=os.getenv("PORT",5000))
