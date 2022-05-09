from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, email_validator


class CreateUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])

class LoginUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])