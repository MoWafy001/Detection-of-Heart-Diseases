from enum import unique
from re import I
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
load_dotenv()

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

    # 1: typical angina, 2: atypical angina, 3: non-anginal pain, 4: asymptomatic
    cp = db.Column(db.Integer)
    trestbps = db.Column(db.Integer)
    chol = db.Column(db.Integer)
    fbs = db.Column(db.Boolean)
    # 0 = normal, 1 = having ST-T wave abnormality, 2 = showing probable or definite left ventricular hypertrophy by Estes' criteria
    restecg = db.Column(db.Integer)
    thalach = db.Column(db.Integer)
    exang = db.Column(db.Boolean)
    oldpeak = db.Column(db.Integer)
    slope = db.Column(db.Integer)
    ca = db.Column(db.Integer)
    thal = db.Column(db.Integer)

    def map_cp(v):
        if v == 'typical angina':
            return 1
        if v == 'atypical angina':
            return 2
        if v == 'non-anginal pain':
            return 3
        if v == 'asymptotic':
            return 4

    def map_restecg(v):
        if v == 'normal':
            return 0
        if v == 'having ST-T wave abnormality':
            return 1
        if v == 'left ventricular hyperthrophy':
            return 2

    def map_restecg(v):
        if v == 'normal':
            return 0
        if v == 'having ST-T wave abnormality':
            return 1
        if v == 'left ventricular hyperthrophy':
            return 2

    def map_slope(v):
        if v == 'upsloping':
            return 1
        if v == 'flat':
            return 2
        if v == 'downsloping':
            return 3

    def map_thal(v):
        if v == 'normal':
            return 3
        if v == 'fixed defect':
            return 6
        if v == 'reversable defect':
            return 7

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
