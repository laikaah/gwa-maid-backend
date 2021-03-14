from datetime import datetime
from gwa_maid import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    subjects = db.relationship('Subject', backref='owner', lazy=True)
    subject_count = db.Column(db.Integer, nullable=False, default=0)

    predicted_grade = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'User<id: {self.id}, username: {self.username}>'

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'subjects': [subject.serialize for subject in self.subjects],
            'subject_count': self.subject_count,
            'predicted_grade': self.predicted_grade
        }


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Integer, unique=False, nullable=False)

    assessment_classes = db.relationship(
        'AssessmentClass', backref='subject', lazy=True)
    assessment_class_count = db.Column(db.Integer, nullable=False, default=0)

    last_updated = db.Column(db.DateTime, unique=False,
                             nullable=False, default=datetime.now())

    predicted_grade = db.Column(db.Integer, nullable=False, default=80)

    def __repr__(self):
        return f'Subject<id: {self.id}, name: {self.name}>'

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.id,
            'user_id': self.user_id,
            'weight': self.weight,
            'assessment_classes': [a_class.serialize
                                   for a_class in self.assessment_classes],
            'assessment_class_count': self.assessment_class_count,
            'last_updated': self.last_updated.strftime('%d %B, %Y'),
            'predicted_grade': self.predicted_grade
        }


class AssessmentClass(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(
        'subject.id'), nullable=False)
    weight = db.Column(db.Integer, unique=False, nullable=False)

    assessments = db.relationship(
        'Assessment', backref='assessment_class', lazy=True)
    assessment_count = db.Column(db.Integer, nullable=False, default=0)

    last_updated = db.Column(db.DateTime, unique=False,
                             nullable=False, default=datetime.now())

    predicted_grade = db.Column(db.Integer, nullable=False, default=80)

    def __repr__(self):
        return f'AssessmentClass<id: {self.id}, name: {self.name}>'

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.id,
            'subject_id': self.subject_id,
            'weight': self.weight,
            'assessments': [a.serialize for a in self.assessments]
        }


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)

    assessment_class_id = db.Column(
        db.Integer, db.ForeignKey('assessment_class.id'), nullable=False)

    grade = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Assessment<id: {self.id}, name: {self.name}>'

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'assessment_class_id': self.assessment_class_id,
            'grade': self.grade
        }
