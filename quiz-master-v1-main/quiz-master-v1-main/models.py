from flask_sqlalchemy import SQLAlchemy
from app import app
from datetime import datetime
db =SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    fullname = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    is_master = db.Column(db.Boolean, default=False)

    submissions = db.relationship('Submission', backref='user', lazy=True , cascade="all, delete-orphan")

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    discription = db.Column(db.String(120), nullable=False)
    
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    discription = db.Column(db.String(120), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    questions = db.relationship('Question', backref='chapter', lazy=True , cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True , cascade="all, delete-orphan")

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(80), nullable=False)
    option1 = db.Column(db.String(120), nullable=False)
    option2 = db.Column(db.String(120), nullable=False)
    option3 = db.Column(db.String(120), nullable=False)
    option4 = db.Column(db.String(120), nullable=False)
    answer = db.Column(db.String(120), nullable=False)
    point = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))

    scores = db.relationship('Score', backref='question', lazy=True , cascade="all, delete-orphan") 


class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Time, nullable=False)

    submissions = db.relationship('Submission', backref='quiz', lazy=True , cascade="all, delete-orphan")

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    correct_opt = db.Column(db.Integer, nullable=False)
    submit_opt = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)

class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_ans = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False , default = datetime.utcnow)

with app.app_context():
    db.create_all()

    master = User.query.filter_by(username='master').first()
    if not master:
        master = User(username='master', password='password', fullname='Master', qualification='M.Tech', dob=datetime(1970, 1, 1), is_master=True)
        db.session.add(master)
        db.session.commit()