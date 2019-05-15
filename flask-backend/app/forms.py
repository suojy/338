import flask_wtf
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired



class TwitterHandle(flask_wtf.Form):
    handle = StringField('Handle', validators=[DataRequired()])
    submit = SubmitField('Twitter Handle')

