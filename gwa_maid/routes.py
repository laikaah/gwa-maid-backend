from flask import jsonify, request

from gwa_maid import app, bcrypt, db
from gwa_maid.helpers import get_user_from_token, tokenize
from gwa_maid.models import Assessment, AssessmentClass, Subject, User


@app.route('/')
def index():
    return 'Welcome!'


@app.route('/verify_token', methods=['POST'])
def verify():
    print(request.json)
    if not request.json:
        return jsonify(success=False)
    if 'token' not in request.json:
        return jsonify(success=False)

    token = request.json['token']

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)
    return jsonify(success=True)


@app.route('/register', methods=['POST'])
def register():
    if not request.json:
        return jsonify(success=False)

    if 'username' not in request.json or 'password' not in request.json:
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

    return jsonify(token=token, success=True)


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter(User.username == username).first()
    if not user:
        return jsonify(success=False)

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify(success=False)

    token = tokenize(user.id, password)

    return jsonify(token=token, success=True)


@app.route('/subjects', methods=['GET'])
def get_subjects():
    token = request.args.get('token')

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subjects = user.subjects.all()
    return jsonify(subjects=subjects, success=True)


@app.route('/subjects/add', methods=['POST'])
def add_subject():
    token = request.forms.get('token')

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subject_name = request.form.get('subject_name')

    subject = Subject(
        name=subject_name,
        user_id=user.id
    )

    db.session.add(subject)
    db.session.flush()

    user.predicted_grade = (user.predicted_grade +
                            subject.predicted_grade) / (user.subject_count + 1)
    user.subject_count += 1

    db.session.commit()

    return jsonify(success=True)


@app.route('/subjects/assessment_classes', methods=['GET'])
def get_assessment_classes():
    token = request.args.get('token')
    subject_name = request.args.get('subject')

    user = get_user_from_token(token)
    if user is None:
        return jsonify(success=False)

    subject = Subject.query.\
        filter(Subject.name == subject_name).\
        filter(Subject.owner.has(User.id == token)).first()

    if not subject:
        return jsonify(success=False)

    assessment_classes = subject.assessment_classes.all()

    return jsonify(assessment_classes=assessment_classes, success=True)


@app.route('/subjects/assessment_classes/add', methods=['POST'])
def add_assessment_class():
    token = request.form.get('token')
    subject_name = request.form.get('subject_name')
    assessment_class_name = request.form.get('assessment_class_name')

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subject = Subject.query.filter(Subject.name == subject_name).\
        filter(Subject.owner.has(User.id == token))

    if not user:
        return jsonify(success=False)

    assessment_class = AssessmentClass(
        name=assessment_class_name,
        subject_id=subject.id,
    )

    db.session.add(assessment_class)
    db.session.flush()

    assessment_class.subject.predicted_grade = \
        (assessment_class.subject.predicted_grade + assessment_class.predicted_grade)\
        / (assessment_class.subject.assessment_class_count + 1)

    assessment_class.subject.assessment_class_count += 1

    db.session.commit()

    return jsonify(success=True)


@app.route('/subjects/assessment_classes/assessments', methods=['GET'])
def get_assessments():
    token = request.args.get('token')
    subject_name = request.args.get('subject')
    assessment_class_name = request.args.get('assessment_class')

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subject = Subject.query.\
        filter(Subject.name == subject_name).\
        filter(Subject.owner.has(User.id == token)).first()

    if not subject:
        return jsonify(success=False)

    assessment_class = AssessmentClass.query.\
        filter(AssessmentClass.name == assessment_class_name).\
        filter(AssessmentClass.subject.has(Subject.id == subject.id))

    if not assessment_class:
        return jsonify(success=False)

    assessments = assessment_class.assessments.all()

    return jsonify(assessments=assessments, success=True)


@app.route('/subjects/assessment_classes/assessments/add', methods=['POST'])
def add_assessment():
    token = request.form.get('token')
    subject_name = request.form.get('subject_name')
    assessment_class_name = request.form.get('assessment_class_name')
    assessment_name = request.form.get('assessment_name')
    assessment_grade = request.form.get('assessment_grade', type=int)

    user = get_user_from_token(token)

    if user is None:
        return jsonify(success=False)

    subject = Subject.query.filter(Subject.name == subject_name).\
        filter(Subject.owner.has(User.id == user.id)).first()

    if not subject:
        return jsonify(success=False)

    assessment_class = AssessmentClass.query.filter(AssessmentClass.name == assessment_class_name).\
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
