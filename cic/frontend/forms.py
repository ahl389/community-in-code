from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo
from markupsafe import Markup, escape


class CustomTextAreaField(TextAreaField):
    # def __init__(self):
    #     super(CustomTextAreaField).__init__()

    def __call__(self, **kwargs):
        html = '<textarea'

        for key, val in kwargs.items():
            if key is not "prepop":
                html += (f' {key} = {val}')

        html += ('>')
        html += (kwargs['prepop'])
        html += ('</textarea>')

        return Markup(html)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    name = StringField('First Name')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Create Password', validators=[
                             DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Create Account')


class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    course_type = SelectField(u'Content Type', choices=[(None, 'Select One'), (
        'tutorial', 'Tutorial'), ('course', 'Course')], validators=[DataRequired()])
    description = TextAreaField('Description')
    stages = HiddenField('Stages')
    submit = SubmitField('Save')


class StageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    order = HiddenField('Order')
    steps = HiddenField('Steps')
    submit = SubmitField('Save')


class StepForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    order = HiddenField('Order')
    step_type = SelectField(u'Step Type', choices=[
                            ('video', 'Video'), ('text', 'Text')])
    content = PageDownField('Content')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')
