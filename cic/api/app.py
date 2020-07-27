from flask import Blueprint, render_template, request, make_response, jsonify
from flask import current_app as app
from flask_cors import CORS
from ..models import db, User, Track, Course, Stage, Step
import psycopg2
import json
import logging
from sqlalchemy import or_

logging.basicConfig(level=logging.DEBUG)

api = Blueprint('api', __name__)
cors = CORS(api, courses={r"/api/*": {"origins": "*"}})


@api.route("/v1/")
def index():
    return "hello api"


@api.route("/v1/users", methods=['POST'])
def create_user():
    '''
    Creates new user
    '''
    return "User created"


@api.route("/v1/users", methods=['GET'])
def read_users():
    '''
    Reads all users
    '''
    return "Here are all users"


@api.route("/v1/users/<user_id>", methods=['PUT'])
def update_user(user_id):
    '''
    Updates given user
    '''
    return "Updated user"


@api.route("/v1/users/<user_id>", methods=['GET'])
def read_user(user_id):
    '''
    Reads given user
    '''
    return "Here is a user"


@api.route("/v1/users/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    '''
    Deletes given user
    '''
    return "User deleted"


# TRACKS
@api.route("/v1/tracks", methods=['POST'])
def create_track():
    '''
    Creates new trackkkkk
    '''

    name = request.json.get('name')
    description = request.json.get('description')

    track = Track(
        name=name,
        description=description)

    db.session.add(track)
    db.session.commit()

    return make_response(f"{track} successfully created with!")


@api.route("/v1/tracks", methods=['GET'])
def read_tracks():
    '''
    Reads all tracks
    '''

    tracks = Track.query.all()
    return jsonify(tracks=[track.serialize() for track in tracks])


@api.route("/v1/tracks/<track_id>", methods=['PUT'])
def update_track(track_id):
    '''
    Updates given track
    '''

    return "Updated track"


@api.route("/v1/tracks/<track_id>", methods=['GET'])
def read_track(track_id):
    '''
    Reads given track
    '''
    return "Here is a track"


@api.route("/v1/tracks/<track_id>", methods=['DELETE'])
def delete_track(track_id):
    '''
    Deletes given track
    '''
    return "track deleted"


# Educational courses (courses and tutorials)
@api.route("/v1/courses", methods=['POST'])
def create_course():
    '''
    Creates new course
    '''

    title = request.json.get('title')
    description = request.json.get('description')
    course_type = request.json.get('type')
    prerequisites = request.json.get('prerequisites')
    length = request.json.get('length')
    stages = request.json.get('stages')
    steps = request.json.get('steps')
    topics = request.json.get('topics')

    course = Course(
        title=title,
        description=description,
        course_type=course_type,
        prerequisites=prerequisites,
        length=length,
        stages=stages,
        steps=steps,
        topics=topics
    )

    db.session.add(course)
    db.session.commit()

    return make_response(str(course.id))


@api.route("/v1/courses", methods=['GET'])
def read_courses():
    '''
    Reads all courses
    '''

    if request.args.get('query') != None:
        querystr = request.args.get('query')
        courses = Course.query.filter(or_(
            Course.title.ilike(f'%{querystr}%'),
            Course.description.ilike(f'%{querystr}%')
        ))
    else:
        courses = Course.query.all()

    return jsonify(courses=[course.serialize() for course in courses])


@api.route("/v1/courses/type/<course_type>", methods=['GET'])
def read_courses_by_type(course_type):
    '''
    Gets courses by type
    '''
    courses = Course.query.filter_by(course_type=course_type)
    return jsonify(courses=[course.serialize() for course in courses])


@api.route("/v1/courses/<course_id>", methods=['PUT'])
def update_course(course_id):
    '''
    Updates given course
    '''

    db.session.query(Course).filter(
        Course.id == course_id).update(request.json)
    db.session.commit()

    return course_id


@api.route("/v1/courses/<course_id>", methods=['GET'])
def read_course(course_id):
    '''
    Reads given course
    '''
    courses = Course.query.filter_by(id=course_id)
    return jsonify(courses=[course.serialize() for course in courses])


@api.route("/v1/courses/<course_id>", methods=['DELETE'])
def delete_course(course_id):
    '''
    Deletes given course
    '''

    course = Course.query.filter_by(id=course_id)
    db.session.delete(course)
    return make_response(f"{course} successfully deleted!")


# stages
@api.route("/v1/stages", methods=['POST'])
def create_stage():
    '''
    Creates new stage
    '''

    print(request.json)
    title = request.json.get('title')
    description = request.json.get('description')
    order = request.json.get('order')
    steps = request.json.get('steps')

    stage = Stage(
        title=title,
        description=description,
        steps=steps,
        order=order
    )

    db.session.add(stage)
    db.session.commit()

    return make_response(str(stage.id))


@api.route("/v1/stages", methods=['GET'])
def read_stages():
    '''
    Reads all stages
    '''

    if request.args:
        ids = request.args.get('ids').split(',')
        stages = Stage.query.filter(Stage.id.in_(ids)).all()
    else:
        stages = Stage.query.all()
    return jsonify(stages=[stage.serialize() for stage in stages])


@api.route("/v1/stages/<stage_id>", methods=['PUT'])
def update_stage(stage_id):
    '''
    Updates given stage
    '''

    db.session.query(Stage).filter(Stage.id == stage_id).update(request.json)
    db.session.commit()

    return stage_id


@api.route("/v1/stages/<stage_id>", methods=['GET'])
def read_stage(stage_id):
    '''
    Reads given stage
    '''
    stages = Stage.query.filter_by(id=stage_id)
    return jsonify(stages=[stage.serialize() for stage in stages])


@api.route("/v1/stages/<stage_id>", methods=['DELETE'])
def delete_stage(stage_id):
    '''
    Deletes given stage
    '''

    stage = Stage.query.filter_by(id=stage_id)
    db.session.delete(stage)
    return make_response(f"{stage} successfully deleted!")


# STEPS
@api.route("/v1/steps", methods=['POST'])
def create_step():
    '''
    Creates new step
    '''
    title = request.json.get('title')
    description = request.json.get('description')
    length = request.json.get('length')
    notes = request.json.get('notes')
    step_type = request.json.get('step_type')
    content = request.json.get('content')
    order = request.json.get('order')

    step = Step(
        title=title,
        description=description,
        order=order,
        length=length,
        notes=notes,
        content=content,
        step_type=step_type
    )

    db.session.add(step)
    db.session.commit()

    return make_response(str(step.id))


@api.route("/v1/steps", methods=['GET'])
def read_steps():
    '''
    Reads all steps
    '''
    if request.args:
        ids = request.args.get('ids').split(',')
        steps = Step.query.filter(Step.id.in_(ids)).all()
    else:
        steps = Step.query.all()
    return jsonify(steps=[step.serialize() for step in steps])


@api.route("/v1/steps/<step_id>", methods=['PUT'])
def update_step(step_id):
    '''
    Updates a given step
    '''
    db.session.query(Step).filter(Step.id == step_id).update(request.json)
    db.session.commit()

    return step_id


@api.route("/v1/steps/<step_id>", methods=['GET'])
def read_step(step_id):
    '''
    Reads given step
    '''
    return "Here is a step"


@api.route("/v1/steps/<step_id>", methods=['DELETE'])
def delete_step(step_id):
    '''
    Deletes a given step
    '''

    step = Step.query.filter_by(id=step_id)
    db.session.delete(step)
    return make_response(f"{step} successfully deleted!")
