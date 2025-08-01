from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#Creating the database models
#User class
class User(db.Model):
    __tablename__ = "user"
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date, nullable=False)

    score = db.relationship("Score", backref="user")

    def __init__(self, name, email, password, dob):
        self.name = name
        self.email = email
        self.password = password
        self.dob = dob

#Subject class
class Subject(db.Model):
    __tablename__ = "subject"
    sid = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String, unique=True, nullable=False)
    
    #Relationship Key
    chapters = db.relationship("Chapter", backref="subject")
    quizzes = db.relationship("Quiz", backref="subject")

    def __init__(self, sname):
        self.sname = sname

#Chapter class
class Chapter(db.Model):
    __tablename__ = "chapter"
    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String, unique=True, nullable=False)

    #Relationship Key
    questions = db.relationship("Question", backref="chapter")
    
    #Foreign Keys
    csid = db.Column(db.Integer, db.ForeignKey('subject.sid'), nullable=False)

    def __init__(self, cname, sname):
        self.cname = cname
        self.subject = sname

#Quiz Class
class Quiz(db.Model):
    __tablename__ = "quiz"
    zid = db.Column(db.Integer, primary_key=True)
    zname = db.Column(db.String, unique=True, nullable=False)
    zdate = db.Column(db.Date, nullable=False)
    zdur = db.Column(db.Integer, nullable=False)

    #Relationship Key
    question = db.relationship("Question", backref="quiz")
    score = db.relationship("Score", backref="quiz")
    
    #Foreign Keys
    zsid = db.Column(db.Integer, db.ForeignKey('subject.sid'), nullable=False)

    def __init__(self, zname, zdate, zdur, sname):
        self.zname = zname
        self.zdate = zdate
        self.zdur = zdur
        self.subject = sname

#Question class
class Question(db.Model):
    __tablename__ = "questions"
    qid = db.Column(db.Integer, primary_key=True)
    qtitle = db.Column(db.String, nullable=False)
    qquestion = db.Column(db.String, nullable=False)
    qopt1 = db.Column(db.String, nullable=False)
    qopt2 = db.Column(db.String, nullable=False)
    qopt3 = db.Column(db.String, nullable=False)
    qopt4 = db.Column(db.String, nullable=False)
    qcorrect = db.Column(db.Integer, nullable=False)

   #Foreign Keys
    qzid = db.Column(db.Integer, db.ForeignKey('quiz.zid'), nullable=False)
    qcid = db.Column(db.Integer, db.ForeignKey('chapter.cid'), nullable=False)

    def __init__(self, qtitle, qquestion, qopt1, qopt2, qopt3, qopt4, qcorrect, qz, ch):
        self.qtitle = qtitle
        self.qquestion = qquestion
        self.qopt1 = qopt1
        self.qopt2 = qopt2
        self.qopt3 = qopt3
        self.qopt4 = qopt4
        self.qcorrect = qcorrect
        self.quiz = qz
        self.chapter = ch

#Score Model
class Score(db.Model):
    rid = db.Column(db.Integer, primary_key=True)
    rtot = db.Column(db.Integer, nullable=False)
    rtstp = db.Column(db.DateTime, default=db.func.current_timestamp())

    #Foreign Keys
    rqid = db.Column(db.Integer, db.ForeignKey('quiz.zid'), nullable=False)
    ruid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)

    def __init__(self, rtot, quiz, user):
        self.rtot = rtot
        self.quiz = quiz
        self.user = user