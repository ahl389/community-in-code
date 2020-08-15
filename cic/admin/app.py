from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, app
from functools import wraps
from flask_login import current_user, login_user, logout_user, login_required
from .forms import LoginForm, SignUpForm, CourseForm, StageForm, StepForm, RoleForm
from ..models import db, User, Course, Stage, Step, Role
from .. import login_manager
from .decorators import roles_required
import requests

admin = Blueprint('admin', __name__,
                  template_folder='templates',
                  static_folder='static')


@admin.route("/")
@login_required
@roles_required(roles=['admin'])
def index():
    return render_template('admin/index.html')


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
    return redirect(url_for('admin.index'))


@admin.route('/create')
@login_required
@roles_required(roles=['admin', 'contributor'])
def create():
    return render_template('admin/create.html')


# CREATE course, DOCUMENTATION GROUP
@admin.route('/create/course', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin', 'contributor'])
def create_course():
    course_form = CourseForm()

    if course_form.validate_on_submit():
        course = Course()
        course_form.populate_obj(course)
        course_id = course.save_get_id()
        return redirect(url_for('admin.view_course', course_id=course_id))

    return render_template('admin/create_course.html', course_form=course_form)


@admin.route('/find')
@login_required
@roles_required(roles=['admin', 'contributor'])
def find():
    courses = Course.get_all()
    return render_template('admin/view_edit.html', courses=courses)


@admin.route('/users')
@login_required
@roles_required(roles=['admin'])
def users():
    users = User.get_all()
    return render_template('admin/users.html', users=users)


@admin.route('/users/roles', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin'])
def user_roles():
    role_form = RoleForm()
    roles = Role.get_all()

    if role_form.validate_on_submit():
        role = Role()
        role_form.populate_obj(role)
        role.save()
        return redirect(url_for('admin.user_roles', roles=roles, role_form=role_form))

    return render_template('admin/roles.html', roles=roles, role_form=role_form)


@admin.route('/users/<user_id>/delete')
@login_required
@roles_required(roles=['admin'])
def delete_user(user_id):
    user = User.get(user_id)
    user.delete()

    users = User.get_all()
    return redirect(url_for('admin.users'))


@admin.route('/users/<user_id>/admin')
@login_required
@roles_required(roles=['admin'])
def make_admin(user_id):
    user = User.get(user_id)
    admin = Role.get_by_first(name='admin')
    user.role = admin
    user.save()
    return redirect(url_for('admin.users'))


# VIEW course, STAGE, STEP
@admin.route('/view/course/<course_id>', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin', 'contributor'])
def view_course(course_id):
    stage_form = StageForm()
    course = Course.get(course_id)
    author = User.get(course.author)

    if stage_form.validate_on_submit():
        # create stage from form data
        stage = Stage()
        stage_form.populate_obj(stage)
        stage.parent_course = course_id

        # set order of new stage and save
        if course.stages:
            stage.order = len(course.stages.split(',')) + 1
        else:
            stage.order = 1

        stage_id = stage.save_get_id()

        # get course, update stage value of course, save it
        course = Course.get(course_id)

        if not course.stages:
            course.stages = str(stage_id)
        else:
            stages = course.stages.split(',')
            stages.append(str(stage_id))
            stages = ','.join(stages)
            course.stages = stages

        course.save()

        # redirect to same view course page
        return redirect(url_for('admin.view_course', course_id=course_id))

    if course.stages:
        stages = Stage.get_many(course.stages.split(','))
        stages.sort(key=lambda x: x.order)
    else:
        stages = []

    return render_template('admin/view_course.html', course=course, stages=stages, author=author, stage_form=stage_form)


@admin.route('/view/stage/<stage_id>', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin', 'contributor'])
def view_stage(stage_id):
    #stage_form = StageForm()
    step_form = StepForm()
    stage = Stage.get(stage_id)
    steps = stage.steps.split(',')

    if step_form.validate_on_submit():
        # create step from form data
        step = Step()
        step_form.populate_obj(step)
        step.parent_stage = stage_id
        step.parent_course = stage.parent_course

        if stage.steps:
            step.order = len(steps) + 1
        else:
            step.order = 1

        step_id = step.save_get_id()

        # update step value of stage
        if not stage.steps:
            stage.steps = str(step_id)
        else:
            steps.append(str(step_id))
            steps = ','.join(steps)
            stage.steps = steps
        stage.save()

        # redirect to same view course page
        return redirect(url_for('admin.view_stage', stage_id=stage_id))

    if stage.steps:
        steps = Step.get_many(steps)
        steps.sort(key=lambda x: x.order)
    else:
        steps = []

    return render_template('admin/view_stage.html', step_form=step_form, stage=stage, steps=steps)


@admin.route('/view/step/<step_id>', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin', 'contributor'])
def view_step(step_id):
    step = Step.get(step_id)
    return render_template('admin/view_step.html', step=step)


# EDIT course, STAGE, STEP
@admin.route('/edit/course/<course_id>', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin', 'contributor'])
def edit_course(course_id):
    course = Course.get(course_id)
    authors = User.get_by_role('admin', 'contributor')
    course_form = CourseForm(obj=course)

    if request.method == 'POST' and course_form.validate():
        course_form.populate_obj(course)
        course.author = request.form.get('author')
        course.save()
        return redirect(url_for('admin.view_course', course_id=course_id))

    return render_template('admin/editcourse.html', course_form=course_form, course=course, authors=authors)


@admin.route('/edit/stage/<stage_id>', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin', 'contributor'])
def edit_stage(stage_id):
    stage = Stage.get(stage_id)
    stage_form = StageForm(obj=stage)

    if request.method == 'POST' and stage_form.validate():
        stage_form.populate_obj(stage)
        stage.save()
        return redirect(url_for('admin.view_stage', stage_id=stage_id))

    return render_template('admin/edit_stage.html', stage_form=stage_form, stage=stage)


@admin.route('/edit/step/<step_id>', methods=['GET', 'POST'])
@login_required
@roles_required(roles=['admin', 'contributor'])
def edit_step(step_id):
    step = Step.get(step_id)
    current_stage_id = step.parent_stage
    course = Course.get(step.parent_course)

    if course.stages:
        stages = Stage.get_many(course.stages.split(','))
        stages.sort(key=lambda x: x.order)
    else:
        stages = []

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
