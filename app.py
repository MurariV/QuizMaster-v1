from flask import Flask, render_template, url_for, redirect, session, request, flash
from model import db, User, Subject, Chapter, Quiz, Question, Score
from sqlalchemy.orm import aliased
from datetime import datetime
from random import shuffle

admin = {
    'name' : 'Murari Vijay',
    'password' : '12345',
    'email' : '24f2005340@ds.study.iitm.ac.in'
}

app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'hello'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/", methods=['POST', 'GET'])
@app.route("/user", methods=['POST', 'GET'])
def UserLogin():
    if 'email' in session:
        flash('Already Logged In!')
        return redirect(url_for('UserDash'))
    else:
        if request.method == 'POST':
            email = request.form['email']
            pwd = request.form['pwd']
            foundusr = User.query.filter_by(email=email).first()
            if foundusr and (pwd == foundusr.password):
                session['email'] = email
                flash("Login Successful!")
                return redirect(url_for("UserDash"))
            else:
                flash("User Not Found!")
                return redirect(url_for("Registration"))
        else:
            return render_template('user.html')

@app.route("/register", methods=['POST', 'GET']) 
def Registration():
    if request.method == 'POST':
        name = request.form['nm']
        email = request.form['email']
        pwd = request.form['pwd']
        rpwd = request.form['rpwd']
        dob = request.form['dob']
        udate = datetime.strptime(dob, "%Y-%m-%d").date()

        foundusr = User.query.filter_by(email=email).first()
        if foundusr:
            flash("User Already Registered!")
            return redirect(url_for('UserLogin'))
        elif rpwd != pwd:
            flash("Password Confirmation does not Match!")
            return redirect(url_for('Registration'))
        else:
            usr = User(name, email, pwd, udate)
            db.session.add(usr)
            db.session.commit()
            flash("User Registration Successful!")
            return redirect(url_for('UserLogin'))
    return render_template('register.html')

@app.route("/user/dashboard")
def UserDash():
    if 'email' in session:
        return render_template('userdash.html')
    else:
        flash('User Not Logged In!')
        return redirect(url_for('UserLogin'))

@app.route("/user/quiz", methods=['POST', 'GET'])
def UserQuiz():
    if 'email' in session:
        quiz = Quiz.query.all()
        return render_template('userquiz.html', quizzes = quiz)
    else:
        flash('User Not Logged In!')
        return redirect(url_for('UserLogin'))

@app.route("/user/<qz>/start", methods = ['POST', 'GET'])
def TakeQuiz(qz):
    quiz = Quiz.query.filter_by(zname = qz).first()
    questions = quiz.question.copy()
    shuffle(questions)
    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.qid}')
            if user_answer and int(user_answer) == question.qcorrect:
                score += 1
        qi = Quiz.query.filter_by(zname = qz).first()
        mail = session['email']
        us = User.query.filter_by(email=mail).first()
        user_score = Score(score, qi, us)
        db.session.add(user_score)
        db.session.commit()
        flash(f'Quiz completed! Your score: {score} / {len(questions)}', category="success")
        return redirect(url_for('UserQuiz'))
    return render_template('takeupquiz.html', quiz = quiz, questions = questions)

@app.route("/user/scores")
def UserScore():
    if 'email' in session:
        usr = User.query.filter_by(email=session['email']).first()
        u = usr.uid
        score = Score.query.filter_by(ruid=u).all()
        quizzes = Quiz.query.all()
        results = {q.zid: Score.query.with_entities(Score.rtot).filter_by(ruid=u, rqid=q.zid).order_by(Score.rtot.desc()).first() for q in quizzes}
        return render_template('userscore.html', quiz=quizzes, results=results)
    else:
        flash('User Not Logged In!')
        return redirect(url_for('UserLogin'))
    
@app.route("/user/leaderboard")
def UserBoard():
    if 'email' in session:
        users = User.query.all()
        leaderboard_data = []

        for user in users:
            scores = Score.query.filter_by(ruid=user.uid).all()
            total_score = sum([s.rtot for s in scores])
            leaderboard_data.append({"user_name": user.name, "total_score": total_score})

        leaderboard_data.sort(key=lambda x: x['total_score'], reverse=True)
        user_fullnames = [x['user_name'] for x in leaderboard_data]
        user_total_scores = [x['total_score'] for x in leaderboard_data]

        return render_template('usersum.html', leaderboard_data=leaderboard_data, user_fullnames=user_fullnames, user_total_scores=user_total_scores)
    else:
        flash('User Not Logged In!')
        return redirect(url_for('UserLogin'))

@app.route("/admin", methods=['POST', 'GET'])
def AdminLogin():
    if 'email' in session:
        if session['email'] == admin['email']:
            flash('Admin Already Logged In!')
            return redirect(url_for('AdminDash'))
    else:
        if request.method == 'POST':
            email = request.form['email']
            pwd = request.form['pwd']

            if email == admin['email'] and pwd == admin['password']:
                session['email'] = email
                flash('Admin Log In Successful!')
                return redirect(url_for('AdminDash'))
            else:
                flash("Unauthorized Admin Login!")
                return redirect(url_for('UserLogin'))
        return render_template('admin.html')

@app.route("/admin/dashboard")
def AdminDash():
    if 'email' in session:
        if session['email'] == admin['email']:
            return render_template('admindash.html')
    else:
        flash("Unauthorized Admin Access!")
        return redirect(url_for('UserLogin'))

@app.route("/admin/subject", methods=['POST', 'GET'])
def AdminSubject():
    if 'email' in session:
        if session['email'] == admin['email']:
            subjects = Subject.query.all()
            chapters = Chapter.query.all()
            return render_template('adminsub.html', subjects = subjects, chapters = chapters)
    else:
        flash("Unauthorized Admin Access!")
        return redirect(url_for('UserLogin'))

@app.route("/admin/subject/add", methods = ['POST', 'GET'])
def AddSubject():
    if request.method == 'POST':
        Sub = request.form['Sub']
        foundsub = Subject.query.filter_by(sname = Sub).first()
        if foundsub:
            flash('Subject Already Exists!')
            return redirect(url_for('AdminSubject'))
        else:
            su = Subject(Sub)
            db.session.add(su)
            db.session.commit()
            flash('Subject Added Successfully')
            return redirect(url_for('AdminSubject'))
    return render_template('addsub.html')

@app.route("/admin/<sub>/chapter/add", methods = ['POST', 'GET'])
def AddChapter(sub):
    if request.method == 'POST':
        Chn = request.form['Ch']
        sn = Subject.query.filter_by(sname = sub).first()
        foundch = Chapter.query.filter_by(cname = Chn, subject = sn).first()
        if foundch:
            flash('Chapter Already Exists!')
            return redirect(url_for('AdminSubject'))
        else:
            ca = Chapter(Chn, sn)
            db.session.add(ca)
            db.session.commit()
            flash('Chapter Added Successfully')
            return redirect(url_for('AdminSubject'))
    return render_template('addchapter.html')

@app.route("/admin/quiz", methods=['POST', 'GET'])
def AdminQM():
    if 'email' in session:
        if session['email'] == admin['email']:
            quizzes = Quiz.query.all()
            subjects = Subject.query.all()
            question = Question.query.all()
            return render_template('adminquiz.html', quizzes = quizzes, subjects = subjects, question = question)
    else:
        flash("Unauthorized Admin Access!")
        return redirect(url_for('UserLogin'))
        

@app.route("/admin/quiz/add", methods = ['POST', 'GET'])
def AddQuiz():
    if request.method == 'POST':
        doq = request.form['doq']
        zdate = datetime.strptime(doq, "%Y-%m-%d").date()
        dura = request.form['dur']
        name = request.form['nm']
        subj = request.form['subject']
        sn = Subject.query.filter_by(sname = subj).first()
        zu = Quiz(name, zdate, dura, sn)
        db.session.add(zu)
        db.session.commit()
        flash('Quiz Added Successfully!')
        return redirect(url_for('AdminQM'))
    subjects = Subject.query.all()
    return render_template('addquiz.html', subjects = subjects)

@app.route("/admin/<qn>/question/add", methods = ['POST', 'GET'])
def AddQues(qn):
    quiz = Quiz.query.filter_by(zname = qn).first()
    subj = quiz.subject.sname
    subjects = Subject.query.filter_by(sname=subj).first()
    chapters = subjects.chapters
    if request.method == 'POST':
        Chid = request.form['chapter']
        Qt = request.form['Qt']
        Qs = request.form['Qs']
        o1 = request.form['o1']
        o2 = request.form['o2']
        o3 = request.form['o3']
        o4 = request.form['o4']
        ans = request.form['ans']
        sn = Chapter.query.filter_by(cname = Chid).first()
        qz = Quiz.query.filter_by(zname = qn).first()
        q1 = Question(Qt, Qs, o1, o2, o3, o4, ans, qz, sn)
        db.session.add(q1)
        db.session.commit()
        flash('Question Added Successfully!')
        return redirect(url_for('AdminQM'))
    return render_template('addques.html', chapters = chapters)

@app.route("/admin/<qn>/<edqu>/edit", methods = ['POST', 'GET'])
def EditQues(qn, edqu):
    quiz = Quiz.query.filter_by(zname = qn).first()
    subj = quiz.subject.sname
    subjects = Subject.query.filter_by(sname=subj).first()
    chapters = subjects.chapters
    question = Question.query.filter_by(qid=edqu).first()
    if request.method == 'POST':
        Qt = request.form['Qt']
        Qs = request.form['Qs']
        o1 = request.form['o1']
        o2 = request.form['o2']
        o3 = request.form['o3']
        o4 = request.form['o4']
        ans = request.form['ans']
        question.qtitle = Qt
        question.qquestion = Qs
        question.qopt1 = o1
        question.qopt2 = o2
        question.qopt3 = o3
        question.qopt4 = o4
        question.qcorrect = ans
        db.session.commit()
        flash('Question Edited Successfully!')
        return redirect(url_for('AdminQM'))
    return render_template('editques.html', chapters = chapters)

@app.route("/admin/subject/delete/<delsn>")
def DelSub(delsn):
    delz = Subject.query.filter_by(sname=delsn).first()
    if delz:
        db.session.delete(delz)
        db.session.commit()
    return redirect(url_for('AdminSubject'))

@app.route("/admin/chapter/delete/<delcn>")
def DelChap(delcn):
    delz = Chapter.query.filter_by(cname=delcn).first()
    if delz:
        db.session.delete(delz)
        db.session.commit()
    return redirect(url_for('AdminSubject'))

@app.route("/admin/quiz/delete/<delqz>")
def DelQuiz(delqz):
    delz = Quiz.query.filter_by(zname=delqz).first()
    if delz:
        db.session.delete(delz)
        db.session.commit()
    return redirect(url_for('AdminQM'))

@app.route("/admin/question/delete/<delqu>")
def DelQues(delqu):
    delq = Question.query.filter_by(qtitle=delqu).first()
    if delq:
        db.session.delete(delq)
        db.session.commit()
    return redirect(url_for('AdminQM'))

@app.route("/admin/subject/<edch>/edit", methods = ['POST', 'GET'])
def EditChap(edch):
    chapter = Chapter.query.filter_by(cid=edch).first()
    if request.method == 'POST':
        Chn = request.form['Ch']
        chapter.cname = Chn
        db.session.commit()
        flash('Chapter Edited Successfully')
        return redirect(url_for('AdminSubject'))
    return render_template('editchap.html')

@app.route("/admin/users")
def AdminUser():
    if 'email' in session:
        if session['email'] == admin['email']:
            user = User.query.all()
            return render_template('adminuser.html', users = user)
    else:
        flash("Unauthorized Admin Access!")
        return redirect(url_for('UserLogin'))

@app.route("/admin/summary")
def AdminSummary():
    if 'email' in session:
        if session['email'] == admin['email']:
            quizzes = Quiz.query.all()
            quiz_names = [quiz.zname for quiz in quizzes]
            average_scores = []
            completion_rates = []

            for quiz in quizzes:
                scores = Score.query.filter_by(rqid=quiz.zid).all()
                if scores:
                    average_score = sum([s.rtot for s in scores]) / len(scores)

                    users_attempted = len(scores)
                    completion_rate = (users_attempted / (User.query.count())) * 100
                else:
                    average_score = 0 
                    completion_rate = 0
                average_scores.append(average_score)
                completion_rates.append(completion_rate)
            return render_template('adminsum.html', quiz_names=quiz_names, average_scores=average_scores, completion_rates=completion_rates)
    else:
        flash("Unauthorized Admin Access!")
        return redirect(url_for('UserLogin'))

@app.route("/logout")
def LogOut():
    session.pop('email', None)
    return redirect(url_for('UserLogin'))

if __name__ == '__main__':
    app.run(debug = True)