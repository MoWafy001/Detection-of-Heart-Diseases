# Detection-of-Heart-Diseases
This a web app where a patient would register, and enter his or her data. The app will try to determine the probabilty of getting a heart disease. If the probabilty is high, you get an option of getting into a meeting with a "doctor".

[You can try the app on Heroku of it still there](https://dhd-project.herokuapp.com/)


# Contributors
This was a group project for the Information Systems class. 5 people worked on it.

- [Mohamed Wafy](https://github.com/MoWafy001) -- `Backend`
- [Ahmed Hytham](https://github.com/AhPro7) -- `Created the AI Model`
- [Basem Khater](https://github.com/BasemKhater) -- `Design`
- [Hozifa Elgharbawy](https://github.com/Hozifaelgharbawy) -- `Frontend`
- [Hossam Elbesomy](https://github.com/HossamElbesomy) -- `Frontend`

# Install
If for some reason you want to run it

1. Installing the requirements
```
pip install -r requirements.txt
```

2. Create a `.env` file (I should have made a template but I didn't)

3. You will have to have these in your `.env` file
- SQLALCHEMY_DATABASE_URI
- MAIL_USERNAME `I only tried it with a Gmail`
- MAIL_PASSWORD
- forgot_password_secret `a secret for creating a JWT token`

Only the first one is required for the app to work, the other 3 is for the forget-password email

4. now you can run it
```
python app.py
```
you can also run it using the `flask` command
