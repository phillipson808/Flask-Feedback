from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, PasswordField
from wtforms.validators import InputRequired, Optional, Email, AnyOf, NumberRange, URL, Length

class CreateUser(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), 
                                                   Length(max=30)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), 
                                                       Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), 
                                                     Length(max=30)])

class LoginUser(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), 
                                                   Length(max=30)])
    password = PasswordField("Password", validators=[InputRequired()])