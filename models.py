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

    status = db.Column(db.Integer)

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
