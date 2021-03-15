from flask import jsonify, request

from gwa_maid import app, bcrypt, db
from gwa_maid.helpers import get_user_from_token, tokenize
from gwa_maid.models import Assessment, AssessmentClass, Subject, User

from flask_cors import cross_origin


@cross_origin()
@app.route('/')
def index():
    return 'Welcome!'


@app.route('/verify_token', methods=['POST', 'OPTIONS'])
def verify():
    if not request.json:
        return jsonify(success=False)
    if 'token' not in request.json:
        return jsonify(success=False)

    token = request.json['token']

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)
    return jsonify(success=True)


@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if not request.json:
        return jsonify(success=False)

    required_params = ['username', 'password']
    for param in required_params:
        if param not in request.json:
            return jsonify(success=False)

    username = request.json['username']
    password = request.json['password']

    if not username or not password:
        return jsonify(success=False)

    existing_user = User.query.filter(User.username == username).first()

    if existing_user:
        return jsonify(success=False)

    user = User(
        username=username,
        password=bcrypt.generate_password_hash(password).decode('utf-8')
    )

    db.session.add(user)
    db.session.commit()

    token = tokenize(user.id, password)

    print('success')
    print(username, password)

    return jsonify(token=token, success=True)


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if not request.json:
        return jsonify(success=False)

    required_params = ['username', 'password']
    for param in required_params:
        if param not in request.json:
            return jsonify(success=False)

    username = request.json['username']
    password = request.json['password']

    user = User.query.filter(User.username == username).first()
    if not user:
        return jsonify(success=False)

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify(success=False)

    token = tokenize(user.id, password)

    return jsonify(token=token, success=True)


@app.route('/subjects', methods=['POST', 'OPTIONS'])
def get_subjects():
    if not request.json:
        return jsonify(success=False)

    required_params = ['token']
    for param in required_params:
        if param not in request.json:
            return jsonify(success=False)

    token = request.json['token']

    user = get_user_from_token(token)
    print(user.username)

    if user is None:
        return jsonify(success=False)

    subjects = user.subjects
    serialized_subjects = [subject.serialize for subject in subjects]

    return jsonify(subjects=serialized_subjects, success=True)


@app.route('/subjects/add', methods=['POST', 'OPTIONS'])
def add_subject():
    if not request.json:
        return jsonify(success=False)

    required_params = ['token', 'subject_name',
                       'last_updated', 'subject_weight']
    for param in required_params:
        if param not in request.json:
            return jsonify(success=False)

    token = request.json['token']

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subject_name = request.json['subject_name']
    last_updated = request.json['last_updated']
    subject_weight = int(request.json['subject_weight'])

    subject = Subject(
        name=subject_name,
        last_updated=last_updated,
        weight=subject_weight,
        user_id=user.id
    )

    db.session.add(subject)
    db.session.flush()

    subjects = user.subjects

    total_grade = 0
    for subject in subjects:
        total_grade += subject.predicted_grade * subject.weight
    user.predicted_grade = total_grade / 100

    user.subject_count += 1

    db.session.commit()

    print(subject)

    return jsonify(success=True)


# @app.route('/subjects/assessment_classes', methods=['GET'])
# def get_assessment_classes():
#     token = request.args.get('token')
#     subject_name = request.args.get('subject')

#     user = get_user_from_token(token)
#     if user is None:
#         return jsonify(success=False)

#     subject = Subject.query.\
#         filter(Subject.name == subject_name).\
#         filter(Subject.owner.has(User.id == token)).first()

#     if not subject:
#         return jsonify(success=False)

#     assessment_classes = subject.assessment_classes.all()
#     serialized_assessment_classes = [
#         a_class.serialize for a_class in assessment_classes]

#     return jsonify(assessment_classes=serialized_assessment_classes
# success=True)


@app.route('/subjects/assessment_classes/add', methods=['POST', 'OPTIONS'])
def add_assessment_class():
    if not request.json:
        return jsonify(False)

    required_params = [
        'token', 'subject_name',
        'last_updated', 'assessment_class_name', 'assessment_class_weight',
        'predicted_grade'
    ]
    for param in required_params:
        if param not in request.json:
            return jsonify(success=False)

    token = request.json['token']
    subject_name = request.json['subject_name']
    assessment_class_name = request.json['assessment_class_name']
    assessment_class_weight = int(request.json['assessment_class_weight'])
    predicted_grade = int(request.json['predicted_grade'])
    last_updated = request.json['last_updated']
    print('Last updated from json is ' + last_updated)

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subject = Subject.query.filter(Subject.name == subject_name).\
        filter(Subject.owner.has(User.id == user.id)).first()

    if not subject:
        return jsonify(success=False)

    assessment_class = AssessmentClass(
        name=assessment_class_name,
        weight=assessment_class_weight,
        last_updated=last_updated,
        predicted_grade=predicted_grade,
        subject_id=subject.id,
    )

    db.session.add(assessment_class)
    subject.assessment_class_count += 1
    db.session.flush()

    # update parent subjects' predicted_grade
    assessment_classes = subject.assessment_classes

    total_grade = sum(
        [a_class.predicted_grade * (a_class.weight / 100)
            for a_class in assessment_classes])

    total_weight = sum(
        [a_class.weight / 100 for a_class in assessment_classes])
    print('total_weight is', total_weight)
    if total_weight < 1:
        total_grade += (1 - total_weight) * 80

    print('total grade is', total_grade)

    subject.predicted_grade = total_grade

    # update parent subjects' last_updated
    subject.last_updated = AssessmentClass.query.get(
        assessment_class.id).last_updated

    db.session.commit()

    return jsonify(success=True)


# @app.route('/subjects/assessment_classes/assessments', methods=['GET'])
# def get_assessments():
#     token = request.args.get('token')
#     subject_name = request.args.get('subject')
#     assessment_class_name = request.args.get('assessment_class')

#     user = get_user_from_token(token)

#     if user is None:
#         return jsonify(success=False)

#     subject = Subject.query.\
#         filter(Subject.name == subject_name).\
#         filter(Subject.owner.has(User.id == token)).first()

#     if not subject:
#         return jsonify(success=False)

#     assessment_class = AssessmentClass.query.\
#         filter(AssessmentClass.name == assessment_class_name).\
#         filter(AssessmentClass.subject.has(Subject.id == subject.id))

#     if not assessment_class:
#         return jsonify(success=False)

#     assessments = assessment_class.assessments.all()

#     serialized_assessments = [
#         assessment.serialize for assessment in assessments]

#     return jsonify(assessments=serialized_assessments, success=True)


@app.route('/subjects/assessment_classes/assessments/add',
           methods=['POST', 'OPTIONS'])
def add_assessment():
    if not request.json:
        return jsonify(success=False)

    if 'token' not in request.json:
        return jsonify(success=False)
    if 'subject_name' not in request.json:
        return jsonify(success=False)
    if 'assessment_class_name' not in request.json:
        return jsonify(success=False)
    if 'assessment_name' not in request.json:
        return jsonify(success=False)
    if 'assessment_grade' not in request.json:
        return jsonify(success=False)

    token = request.json['token']
    subject_name = request.json['subject_name']
    assessment_class_name = request.json['assessment_class_name']
    assessment_name = request.json['assessment_name']
    assessment_grade = request.json['assessment_grade']

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subject = Subject.query.filter(Subject.name == subject_name).\
        filter(Subject.owner.has(User.id == user.id)).first()

    if not subject:
        return jsonify(success=False)

    assessment_class = AssessmentClass.query.\
        filter(AssessmentClass.name == assessment_class_name).\
        filter(AssessmentClass.subject.has(Subject.id == subject.id))

    if not assessment_class:
        return jsonify(success=False)

    assessment = Assessment(
        name=assessment_name,
        assessment_class_id=assessment_class.id,
        grade=assessment_grade
    )

    db.session.add(assessment)
    db.session.flush()

    assessment.assessment_class.predicted_grade = \
        (assessment.assessment_class.predicted_grade + assessment.grade)\
        / (assessment.assessment_class.assessment_count + 1)

    assessment.assessment_class.assessment_count += 1

    db.session.commit()

    return jsonify(success=True)
