from flask import json
from flask.json import JSONDecoder
from gwa_maid import app, db, bcrypt, fernet
from gwa_maid.models import User, Subject, AssessmentClass, Assessment
from gwa_maid.helpers import tokenize, get_user_from_token

from flask import request, jsonify
    

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if password != confirm_password:
        return jsonify(success=False)
    
    existing_user = User.query.filter(User.username == username).first()
    
    if existing_user:
        return jsonify(success=False)

    user = User(
        username = username,
        password = bcrypt.generate_password_hash(password).decode('utf-8')
    )
    
    db.session.add(user)
    db.session.commit()
    
    token = tokenize(username, password)
    
    return jsonify(token=token,success=True)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter(User.username == username).first()
    if not user:
        return jsonify(success=False)

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify(success=False)
    
    token = tokenize(username, password)
    
    return jsonify(token=token, success=True)

@app.route('/subjects', methods=['GET'])
def get_subjects():
    token = request.args.get('token')

    user = get_user_from_token(token)
    
    if not user:
        return jsonify(success=False)

    subjects = user.subjects.all()
    return jsonify(subjects=subjects, success=True)

@app.route('/subjects/add', methods=['POST'])
def add_subject():
    token = request.forms.get('token')
    
    user = get_user_from_token(token)
    
    if not user:
        return jsonify(success=False)
    
    subject_name = request.form.get('subject_name')
    
    subject = Subject(
        name = subject_name,
        user_id = user.id
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify(success=True)

@app.route('/subjects/assessment_classes', methods=['GET'])
def get_assessment_classes():
    token = request.args.get('token')
    subject_name = request.args.get('subject')
    
    user = get_user_from_token(token)
    if not user:
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
    
    if not user:
        return jsonify(success=False)
    
    subject = Subject.query.filter(Subject.name == subject_name).\
                            filter(Subject.owner.has(User.id == token))
    
    if not user:
        return jsonify(success=False)
    
    assessment_class = AssessmentClass(
        name = assessment_class_name,
        subject_id = subject.id,
    )
    
    db.session.add(assessment_class)
    db.session.commit()
    
    return jsonify(success=True)


@app.route('/subjects/assessment_classes/assessments', methods=['GET'])
def get_assessments():
    token = request.args.get('token')
    subject_name = request.args.get('subject')
    assessment_class_name = request.args.get('assessment_class')
    
    user = get_user_from_token(token)
    
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

    if not user:
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
        name = assessment_name,
        assessment_class_id = assessment_class.id,
        grade = assessment_grade
    )
    
    db.session.add(assessment)
    db.session.commit()
    
    return jsonify(success=True)
    