from logging import PlaceHolder
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, IntegerField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_wtf.file import FileField, FileAllowed
#from flask_tweet.static.data.models import Test
# from .models import Members

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    neckname = StringField('Neckname', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # image_file = StringField('Picture')
    gender = StringField('Gender', validators=[DataRequired(), Length(min=4, max=6)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=30)])
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=30)])
    age = IntegerField('Age')
    level = IntegerField('Role')
    activation_code = IntegerField('Activation_code')
    image_file = FileField('Choose a picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class inlineloginform(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


class ViestitForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Tweet', validators=[DataRequired()])

    submit = SubmitField('Lähetä')
       