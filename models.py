from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask("heart")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # True = Male, False = Female
    gender = db.Column(db.Boolean, nullable=False)

    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    doctor = db.relationship("Doctor", back_populates="patients")

    status = db.Column(db.Boolean)
    degree = db.Column(db.Float) 

    # features

    cp = db.Column(db.Integer) # 1: typical angina, 2: atypical angina, 3: non-anginal pain, 4: asymptomatic
    trestbps = db.Column(db.Integer)
    chol = db.Column(db.Integer)
    fbs = db.Column(db.Boolean)
    restecg = db.Column(db.Integer) # 0 = normal, 1 = having ST-T wave abnormality, 2 = showing probable or definite left ventricular hypertrophy by Estes' criteria
    thalach = db.Column(db.Integer)
    exang = db.Column(db.Boolean)
    oldpeak = db.Column(db.Integer)
    slope = db.Column(db.Integer)
    ca = db.Column(db.Integer)
    thal = db.Column(db.Integer)

    def __str__(self) -> str:
        return f"Patient: email:{self.email}"

    def __repr__(self) -> str:
        return f"Patient: email:{self.email}"

class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # True = Male, False = Female
    gender = db.Column(db.Boolean, nullable=False)

    patients = db.relationship("Patient", back_populates="doctor")
    meetings = db.relationship("Meeting", back_populates="doctor")

    def __str__(self) -> str:
        return f"Doctor: email:{self.email}"

    def __repr__(self) -> str:
        return f"Doctor: email:{self.email}"

class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    doctor = db.relationship("Doctor", back_populates="meetings")

    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    patient = db.relationship("Patient", uselist=False, backref="meeting")

db.create_all()
