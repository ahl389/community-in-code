from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from .forms import LoginForm, SignUpForm
from ..models import db, User, Course, Stage, Step, Enrollment, Achievement, Role
from .. import login_manager
import requests

frontend = Blueprint('frontend', __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/%s' % __name__)


@frontend.route("/")
def index():
    # if current_user.is_authenticated:
    return render_template('frontend/index.html')
    # else:
    # return render_template('frontend/splash.html')


@frontend.route("/whoops")
@login_manager.unauthorized_handler
def whoops():
    return render_template('frontend/login_required.html')


@frontend.route("/login", methods=['GET', 'POST'])
def login():
    # if the user is already logged in, send them back to the home page instead of showing login stuff
    if current_user.is_authenticated:
        return redirect(url_for('frontend.index'))

    err = None

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            err = "A user with that email address does not exist, please sign up."
        elif not user.check_password(form.password.data):
            err = 'Invalid username or password'
        else:
            login_user(user, remember=form.remember_me.data, force=True)
            return redirect(url_for('frontend.index'))

    return render_template('frontend/login.html', form=form, err=err)


@frontend.route("/signup", methods=['GET', 'POST'])
def signup():
    # if the user is already logged in, send them back to the home page instead of showing login stuff
    if current_user.is_authenticated:
        return redirect(url_for('frontend.index'))

    form = SignUpForm()
    err = None

    if form.validate_on_submit():
        email = form.email.data
        role = Role.get_by_first(name='member')

        user = User.query.filter_by(email=email).first()

        if user is not None:
            err = "A user with that email address already exists."
        else:
            if email in ['ashleyboucher@hey.com', 'ashleyhlivingston@gmail.com', 'ashleyhboucher@gmail.com']:
                role = Role.get_by_first(name='admin')

            user = User(email=form.email.data, name=form.name.data, role=role)
            user.set_password(form.password.data)
            user.save()

            login_user(user)
            return redirect(url_for('frontend.index'))

    return render_template('frontend/signup.html', form=form, err=err)


@frontend.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))


@frontend.route('/profile')
@login_required
def profile():
    enrollments = Enrollment.get_by(user_id=current_user.id)
    course_ids = [e.course_id for e in enrollments]
    unit_ids = [e.unit_id for e in enrollments]
    courses = Course.get_many(course_ids)
    units = Stage.get_many(unit_ids)
    return render_template('frontend/profile.html', enrollments=enrollments, courses=courses, units=units)


@frontend.route('/find')
def find():
    courses = Course.get_all()
    return render_template('frontend/view_edit.html', courses=courses)


@frontend.route('/courses/<course_slug>')
def view_course(course_slug):
    course = Course.get_by_first(slug=course_slug)
    author = User.get(course.author)
    units = Stage.get_many(course.stages.split(','))
    units.sort(key=lambda x: x.order)

    if current_user.is_authenticated:
        enrollment = Enrollment.get_by(
            user_id=current_user.id, course_id=course.id)

        if len(enrollment) == 0:
            return render_template('frontend/course_unenrolled.html', course=course, units=units, author=author)
        return render_template('frontend/course.html', course=course, units=units, enrollment=enrollment, author=author)
    else:
        return render_template('frontend/course_unauthenticated.html', course=course, units=units, author=author)


@frontend.route('/courses/<course_id>/enroll')
@login_required
def enroll(course_id):
    course = Course.get(course_id)
    enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    enrollment.save()
    return redirect(url_for('frontend.view_course', course_slug=course_slug))


@frontend.route('/courses/<course_slug>/<stage_id>')
@login_required
def view_unit(course_slug, stage_id):
    course = Course.get_by_first(slug=course_slug)
    unit = Stage.get(stage_id)
    steps = Step.get_many(unit.steps.split(','))
    steps.sort(key=lambda x: x.order)
    return render_template('frontend/unit.html', course=course, unit=unit, steps=steps)


@frontend.route('/courses/<course_slug>/<stage_id>/<step_id>')
@login_required
def view_step(course_slug, stage_id, step_id):
    course = Course.get_by_first(slug=course_slug)
    unit = Stage.get(stage_id)
    steps = Step.get_many(unit.steps.split(','))
    step = Step.get(step_id)

    next_step = None
    prev_step = None

    for s in steps:
        if s.order == step.order + 1:
            next_step = s.id
        if s.order == step.order - 1:
            prev_step = s.id

    return render_template('frontend/lesson.html', course=course, unit=unit, step=step, next_step=next_step, prev_step=prev_step)
