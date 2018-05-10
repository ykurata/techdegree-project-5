from flask_wtf import Form
from wtforms import (StringField, PasswordField, TextAreaField, DateField,
                    IntegerField)
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Length, EqualTo)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("User with that name already exists.")


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters "
                        "numbers, and underscores only")
            ),
            name_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=4),
            EqualTo('password2', message="Password must match.")
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
        )


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])


class EntryForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    timestamp = DateField('Date (YYYY-MM-DD)', validators=[DataRequired()])
    time_spent = IntegerField('Time spent (minutes)', validators=[DataRequired()])
    content = TextAreaField('What you learned', validators=[DataRequired()])
    resources = TextAreaField('Resources')


class EditEntryForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    timestamp = DateField('Date', validators=[DataRequired()])
    time_spent = IntegerField('Time spent (minutes)', validators=[DataRequired()])
    content = TextAreaField('What you learned', validators=[DataRequired()])
    resources = TextAreaField('Resources')
