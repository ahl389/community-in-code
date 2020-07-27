from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from .forms import LoginForm, SignUpForm, CourseForm, StageForm, StepForm
from ..models import db, User, Course, Stage, Step
from .. import login_manager
import requests

admin = Blueprint('admin', __name__,
                  template_folder='templates', 
                  static_folder='static')


@admin.route("/")
@login_required
def index():
    if current_user.admin:
        return render_template('admin/index.html')
    else:
        return render_template('admin/protected.html')


@admin.route("/whoops")
@login_manager.unauthorized_handler
def whoops():
    return render_template('admin/login_required.html')


@admin.route("/login", methods=['GET', 'POST'])
def login():
    # if the user is already logged in, send them back to the home page instead of showing login stuff
    if current_user.is_authenticated:
        print('already logged in')
        return redirect(url_for('admin.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            message = "A user with that email address does not exist, please sign up."
            return redirect(url_for('admin.signup', message=message))
        elif not user.check_password(form.password.data):
            err = 'Invalid username or password'
            return redirect(url_for('admin.login'), err=err)

        login_user(user, remember=form.remember_me.data, force=True)
        return redirect(url_for('admin.index'))

    return render_template('admin/login.html', form=form)


@admin.route("/signup", methods=['GET', 'POST'])
def signup():
    # if the user is already logged in, send them back to the home page instead of showing login stuff
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    form = SignUpForm()

    if form.validate_on_submit():
        email = form.email.data
        admin = False

        if email == 'ashleyboucher@hey.com':
            admin = True

        user = User(email=form.email.data, admin=admin)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('admin.index'))

    return render_template('admin/signup.html', form=form)


@admin.route('/logout')
def logout():
    logout_user()
    print('logged out')
    return redirect(url_for('admin.index'))


@admin.route('/create')
def create():
    return render_template('admin/create.html')


# CREATE course, DOCUMENTATION GROUP
@admin.route('/create/course', methods=['GET', 'POST'])
def create_course():
    course_form = CourseForm()

    if course_form.validate_on_submit():
        course = Course()
        course_form.populate_obj(course)
        course_id = course.save_get_id()
        return redirect(url_for('admin.view_course', course_id=course_id))

    return render_template('admin/create_course.html', course_form=course_form)


@admin.route('/find')
def find():
    courses = Course.get_all()
    return render_template('admin/view_edit.html', courses=courses)

# VIEW course, STAGE, STEP


@admin.route('/view/course/<course_id>', methods=['GET', 'POST'])
def view_course(course_id):
    stage_form = StageForm()

    if stage_form.validate_on_submit():
        # create stage from form data
        stage = Stage()
        stage_form.populate_obj(stage)
        stage.parent_course = course_id
        stage_id = stage.save_get_id()

        # get course, update stage value of course, save it
        course = Course.get(course_id)
        course.stages += f'{stage_id},'
        course.save()

        # redirect to same view course page
        return redirect(url_for('admin.view_course', course_id=course_id))

    course = Course.get(course_id)

    if course.stages:
        stages = Stage.get_many(course.stages.split(','))
        stages.sort(key=lambda x: x.order)
    else:
        stages=[]

    return render_template('admin/view_course.html', course=course, stages=stages, stage_form=stage_form)


@admin.route('/view/stage/<stage_id>', methods=['GET', 'POST'])
def view_stage(stage_id):
    #stage_form = StageForm()
    step_form = StepForm()
    stage = Stage.get(stage_id)

    if step_form.validate_on_submit():
        # create step from form data
        step = Step()
        step_form.populate_obj(step)
        step.parent_stage = stage_id
        step.parent_course = stage.parent_course
        step_id = step.save_get_id()

        # update step value of stage
        stage.steps += f'{step_id},'

        # save stage and step
        stage.save()

        # redirect to same view course page
        return redirect(url_for('admin.view_stage', stage_id=stage_id))

    stage = Stage.get(stage_id)
    steps = Step.get_many(stage.steps)
    steps.sort(key=lambda x: x.order)

    return render_template('admin/view_stage.html', step_form=step_form, stage=stage, steps=steps)


@admin.route('/view/step/<step_id>', methods=['GET', 'POST'])
def view_step(step_id):
    step = Step.get(step_id)
    return render_template('admin/view_step.html', step=step)


# EDIT course, STAGE, STEP
@admin.route('/edit/course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.get(course_id)
    course_form = courseForm(obj=course)

    if request.method == 'POST' and course_form.validate():
        course_form.populate_obj(course)
        course.save()
        return redirect(url_for('admin.view_course', course_id=course_id))

    return render_template('admin/editcourse.html', course_form=course_form, course=course)


@admin.route('/edit/stage/<stage_id>', methods=['GET', 'POST'])
def edit_stage(stage_id):
    stage = Stage.get(stage_id)
    stage_form = StageForm(obj=stage)

    if request.method == 'POST' and stage_form.validate():
        stage_form.populate_obj(stage)
        stage.save()
        return redirect(url_for('admin.view_stage', stage_id=stage_id))

    return render_template('admin/edit_stage.html', stage_form=stage_form, stage=stage)


@admin.route('/edit/step/<step_id>', methods=['GET', 'POST'])
def edit_step(step_id):
    step = Step.get(step_id)
    current_stage_id = step.parent_stage
    course = Course.get(step.parent_course)
    stages = Stage.get_many(course.stages)

    step_form = StepForm(obj=step)

    if request.method == 'POST' and step_form.validate():
        step_form.populate_obj(step)
        new_stage_id = request.form.get('parent_stage')

        if current_stage_id != new_stage_id:
            # If there was a change in stage, update step to reflect new parent, get both old and new stages
            step.parent_stage = new_stage_id

            new_stage = Stage.get(new_stage_id)
            old_stage = Stage.get(current_stage_id)

            # Update old parent stage to reflect loss of child step
            steps = old_stage.steps.split(',')
            steps.remove(str(step.id))
            old_stage.steps = ','.join(steps)
            old_stage.save()

            # Update new parent stage to reflect gain of child step
            steps = new_stage.steps.split(',')
            steps.append(str(step.id))
            new_stage.steps = ','.join(steps)
            new_stage.save()

        # save step
        step.save()
        return redirect(url_for('admin.view_step', step_id=step_id))

    return render_template('admin/edit_step.html', stages=stages, step_form=step_form, step=step)
