from app import Doctor, db

email = input('email: ')
password = input('password (123): ')
first_name = input('first name: ')
last_name = input('last name: ')

if not password:
    password = '123'

db.session.add(Doctor(
    email=email,
    password=password,
    age=25,
    first_name=first_name,
    last_name=last_name,
    gender=True
))
db.session.commit()