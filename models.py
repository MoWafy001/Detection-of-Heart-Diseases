from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://mohamedwafy:M1252002@localhost:5432/heart"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # True = Male, False = Female
    gender = db.Column(db.Boolean, nullable=False)

    role = db.Column(db.String(20), default="patient", nullable=False)

    def __str__(self) -> str:
        return f"{self.role}: email:{self.email}"

    def __repr__(self) -> str:
        return f"{self.role}: email:{self.email}"


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    result = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)


db.create_all()
