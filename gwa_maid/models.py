from datetime import datetime
from gwa_maid import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    subjects = db.relationship(
        'Subject', backref='owner', lazy=True,
        order_by='Subject.last_updated.desc()')
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
    name = db.Column(db.String(20), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Integer, unique=False, nullable=False)

    assessment_classes = db.relationship(
        'AssessmentClass', backref='subject', lazy=True,
        order_by='AssessmentClass.last_updated.desc()')
    assessment_class_count = db.Column(db.Integer, nullable=False, default=0)

    last_updated = db.Column(db.DateTime, unique=False,
                             nullable=False, default=datetime.now())

    predicted_grade = db.Column(db.Integer, nullable=False, default=80)

    def __repr__(self):
        return f'Subject<id: {self.id}, name: {self.name}>'

    # serialize object up to n dimensions
    # (do this to avoid recursive serializing)
    @property
    def serialize(self, dimensions=5):
        if dimensions == 1:
            return {
                'id': self.id,
                'name': self.name,
                'weight': self.weight,
                'assessment_classes': [a_class.serialize
                                       for a_class in self.assessment_classes],
                'assessment_class_count': self.assessment_class_count,
                'last_updated': self.last_updated,
                'predicted_grade': self.predicted_grade
            }
        return {
            'id': self.id,
            'name': self.name,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'password': self.user.password,
                'subjects': [subject.serialize(dimensions-1)
                             for subject in self.user.subjects],
                'subject_count': self.user.subject_count,
                'predicted_grade': self.user.predicted_grade
            },
            'weight': self.weight,
            'assessment_classes': [a_class.serialize
                                   for a_class in self.assessment_classes],
            'assessment_class_count': self.assessment_class_count,
            'last_updated': self.last_updated,
            'predicted_grade': self.predicted_grade
        }


class AssessmentClass(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=False, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(
        'subject.id'), nullable=False)
    weight = db.Column(db.Integer, unique=False, nullable=False)

    assessments = db.relationship(
        'Assessment', backref='assessment_class', lazy=True,
        order_by='Assessment.last_updated.desc()')
    assessment_count = db.Column(db.Integer, nullable=False, default=0)

    last_updated = db.Column(db.DateTime, unique=False,
                             nullable=False, default=datetime.now())

    predicted_grade = db.Column(db.Integer, nullable=False, default=80)

    def __repr__(self):
        return f'AssessmentClass<id: {self.id}, name: {self.name}>'

    # serialize object up to n dimensions
    # (do this to avoid recursive serializing)
    @property
    def serialize(self, dimensions=5):
        if dimensions == 1:
            return {
                'id': self.id,
                'name': self.name,
                'subject': {
                    'id': self.subject.id,
                    'name': self.subject.name,
                    'weight': self.subject.weight,
                    'assessment_class_count':
                        self.subject.assessment_class_count,
                    'last_updated': self.subject.last_updated,
                    'predicted_grade': self.predicted_grade
                },
                'weight': self.weight,
                'assessments': [a.serialize for a in self.assessments],
                'last_updated': self.last_updated,
                'predicted_grade': self.predicted_grade
            }
        return {
            'id': self.id,
            'name': self.name,
            'subject': {
                'id': self.subject.id,
                'name': self.subject.name,
                'weight': self.subject.weight,
                'assessment_classes': [a_class.serialize(dimensions-1) for
                                       a_class in self.subject.
                                       assessment_classes],
                'assessment_class_count': self.subject.assessment_class_count,
                'last_updated': self.subject.last_updated,
                'predicted_grade': self.predicted_grade
            },
            'weight': self.weight,
            'assessments': [a.serialize for a in self.assessments],
            'last_updated': self.last_updated,
            'predicted_grade': self.predicted_grade
        }


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=False, nullable=False)

    assessment_class_id = db.Column(
        db.Integer, db.ForeignKey('assessment_class.id'), nullable=False)

    last_updated = db.Column(
        db.DateTime, nullable=False, default=datetime.now())

    grade = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Assessment<id: {self.id}, name: {self.name}>'

    # serialize object up to n dimensions
    # (do this to avoid recursive serializing)
    @property
    def serialize(self, dimensions=5):
        if dimensions == 1:
            return {
                'id': self.id,
                'name': self.name,
                'assessment_class': {
                    'id': self.assessment_class.id,
                    'name': self.assessment_class.name,
                    'weight': self.assessment_class.weight,
                    'assessment_count': self.assessment_class.assessment_count,
                    'last_updated': self.last_updated,
                    'predicted_grade': self.predicted_grade
                },
                'last_updated': self.last_updated,
                'grade': self.grade
            }
        return {
            'id': self.id,
            'name': self.name,
            'assessment_class': {
                'id': self.assessment_class.id,
                'name': self.assessment_class.name,
                'weight': self.assessment_class.weight,
                'assessments': [a.serialize(dimensions-1)
                                for a in self.assessment_class.assessments],
                'assessment_count': self.assessment_class.assessment_count,
                'last_updated': self.last_updated,
                'predicted_grade': self.predicted_grade
            },
            'last_updated': self.last_updated,
            'grade': self.grade
        }
