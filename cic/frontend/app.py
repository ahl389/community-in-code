from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from .forms import LoginForm, SignUpForm
from ..models import db, User, Course, Stage, Step
from .. import login_manager
import requests

frontend = Blueprint('frontend', __name__,
                     template_folder='templates', 
                     static_folder='static', 
                     static_url_path='/%s' % __name__)


@frontend.route("/")
def index():
    #if current_user.is_authenticated:
    return render_template('frontend/index.html')
    #else:
        #return render_template('frontend/splash.html')


@frontend.route("/whoops")
@login_manager.unauthorized_handler
def whoops():
    return render_template('frontend/login_required.html')


@frontend.route("/login", methods=['GET', 'POST'])
def login():
    # if the user is already logged in, send them back to the home page instead of showing login stuff
    if current_user.is_authenticated:
        return redirect(url_for('frontend.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            message = "A user with that email address does not exist, please sign up."
            return redirect(url_for('frontend.signup', message=message))
        elif not user.check_password(form.password.data):
            err = 'Invalid username or password'
            return redirect(url_for('frontend.login'), err=err)

        login_user(user, remember=form.remember_me.data, force=True)
        return redirect(url_for('frontend.index'))

    return render_template('frontend/login.html', form=form)


@frontend.route("/signup", methods=['GET', 'POST'])
def signup():
    # if the user is already logged in, send them back to the home page instead of showing login stuff
    if current_user.is_authenticated:
        return redirect(url_for('frontend.index'))

    form = SignUpForm()
    err = None

    if form.validate_on_submit():
        email = form.email.data
        admin = False

        user = User.query.filter_by(email=email).first()

        if user is not None:
            err = "A user with that email address already exists."
        else:
            if email in ['ashleyboucher@hey.com', 'ashleyhlivingston@gmail.com', 'ashleyhboucher@gmail.com']:
                admin = True

            user = User(email=form.email.data, name=form.name.data, admin=admin)
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for('frontend.index'))

    return render_template('frontend/signup.html', form=form, err=err)


@frontend.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))

@frontend.route('/find')
def find():
    courses = Course.get_all()
    return render_template('frontend/view_edit.html', courses=courses)

@frontend.route('/courses/<course_id>')
@login_required
def view_course(course_id):
    course = Course.get(course_id)
    units = Stage.get_many(course.stages.split(','))
    return render_template('frontend/course.html', course=course, units=units)

@frontend.route('/courses/<course_id>/<stage_id>')
def view_unit(course_id, stage_id):
    course = Course.get(course_id)
    unit = Stage.get(stage_id)
    steps = Step.get_many(unit.steps.split(','))
    return render_template('frontend/unit.html', course=course, unit=unit, steps=steps)

@frontend.route('/courses/<course_id>/<stage_id>/<step_id>')
def view_step(course_id, stage_id, step_id):
    course = Course.get(course_id)
    unit = Stage.get(stage_id)
    step = Step.get(step_id)
    return render_template('frontend/lesson.html', course=course, unit=unit, step=step)
