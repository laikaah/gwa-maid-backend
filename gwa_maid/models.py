from datetime import datetime
from gwa_maid import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    subjects = db.relationship('Subject', backref='owner', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Integer, unique=False, nullable=False)
    assessment_classes = db.relationship('AssessmentClass', backref='subject', lazy=True)
    last_updated = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.now())

class AssessmentClass(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    weight = db.Column(db.Integer, unique=False, nullable=False)
    assessments = db.relationship('Assessment', backref='assessment_class', lazy=True)
    

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    assessment_class_id = db.Column(db.Integer, db.ForeignKey('assessment_class.id'), lazy=True)
    grade = db.Column(db.Integer, nullable=False)