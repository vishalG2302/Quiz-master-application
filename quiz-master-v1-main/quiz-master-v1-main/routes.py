from flask import render_template , request , redirect , url_for , session,flash
from functools import wraps
from app import app
from models import db, User, Subject, Chapter, Question, Quiz, Score, Submission
from datetime import datetime


#____________________decorater function_______________________________

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def master_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])  
        if not user.is_master:
            return redirect(url_for('user'))
        return f(*args, **kwargs)
    return decorated_function

#________________________login_______________________________________

@app.route('/login')
def login():    
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def loginpost():
    username = request.form.get('username')
    password = request.form.get('password')

    if username=='' :
        flash('username can not be empty')
        return redirect(url_for('login'))
    if password=='' :
        flash('password can not be empty')
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username , password=password).first()
    if user:
        session['user_id'] = user.id
        flash('Successfully logged in')
        return redirect(url_for('index'))
    flash('User not exist check username , password and try again ')
    return redirect(url_for('login'))


#________________________regestration____________

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def registerpost():
    username = request.form.get('username')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    qualification = request.form['qualification']
    dob = request.form.get('dob')
    dob = datetime.strptime(dob, '%Y-%m-%d').date()

    if username=='' :
        flash('username can not be empty')
        return redirect(url_for('register'))
    if password=='' :
        flash('password can not be empty')
        return redirect(url_for('register'))
    if User.query.filter_by(username=username).first():
        flash('user with this username already exists')
        return redirect(url_for('register'))
    if fullname=='' :
        flash('fullname can not be empty')
        return redirect(url_for('register'))
    if qualification=='' :
        flash('qualification can not be empty')
        return redirect(url_for('register'))
    user = User(username=username, password=password, fullname=fullname, qualification=qualification, dob=dob)
    db.session.add(user)    
    db.session.commit()
    return redirect(url_for('index'))

#______________________LOG_OUT____________________

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


#______________________index ROUTE_________________

@app.route('/')
@login_required
def index():
    user = User.query.get(session['user_id'])  
    if not user:
        return redirect(url_for('login'))
    if user.is_master:
        return redirect(url_for('master'))
    return redirect(url_for('user'))

##-------master dashboard---------
@app.route('/master')
@master_required
def master():
    user=User.query.get(session['user_id'])
    subjects= Subject.query.all()

    parameter = request.args.get('parameter')
    query = request.args.get('query')
    parameters = {'subject':'Subject', 'chapter':'Chapter'}

    if parameter and query:
        if parameter=="subject":
            subjects = Subject.query.filter(Subject.name.like('%'+query+'%')).all()
            return render_template('masterdashboard.html', user=user, subjects=subjects, parameters=parameters)
        if parameter=="chapter":
            subjects = Subject.query.join(Chapter).filter(Chapter.name.ilike(f'%{query}%')).all()
            return render_template('masterdashboard.html', user=user, subjects=subjects, parameters=parameters)
    return render_template('masterdashboard.html', user=user, subjects=subjects, parameters=parameters)


##-----user dashboard-----
@app.route('/user')
@login_required
def user():
    user = User.query.get(session['user_id'])  
    quizzes = Quiz.query.all()

    parameter = request.args.get('parameter')
    query = request.args.get('query')
    parameters = {'subject':'Subject', 'chapter':'Chapter'}
    if parameter and query:
        if parameter=="subject":    
            quizzes = Quiz.query.join(Chapter).join(Subject).filter(Subject.name.like('%'+query+'%')).all()
            return render_template('userdashboard.html', user=user, quizzes=quizzes, parameters=parameters)
        if parameter=="chapter":
            quizzes = Quiz.query.join(Chapter).filter(Chapter.name.like('%'+query+'%')).all()
            return render_template('userdashboard.html', user=user, quizzes=quizzes, parameters=parameters)  
    return render_template('userdashboard.html', user=user,quizzes=quizzes , parameters=parameters)

#******************************************************************
#_____________ADD Routes_________###                              *
#******************************************************************

##-----adding subjectc-----
@app.route('/master/addsubject')
@master_required
def addsubject():
    return render_template('addsubject.html', user=User.query.get(session['user_id']), subjects=Subject.query.all())

@app.route('/master/addsubject', methods=['POST'])
@master_required
def addsubjectpost():
    name = request.form.get('subjectname')
    discription = request.form.get('discription')

    if name=='':
        flash('Subject name can not be empty')
        return redirect(url_for('addsubject'))
    if discription=='':
        flash('Subject Discription can not be empty')
        return redirect(url_for('addsubject'))
    if Subject.query.filter_by(name=name).first():
        flash('Sbject with this name is already exists , Use different subject name')
        return redirect(url_for('addsubject'))
    subject = Subject(name=name, discription=discription)
    db.session.add(subject)
    db.session.commit()
    flash('Subject added successfully')    
    return redirect(url_for('master'))

##-----adding chapter-----
@app.route('/master/<int:id>/addchapter')
@master_required
def addchapter(id):
    return render_template('addchapter.html', user=User.query.get(session['user_id']), chapters=Chapter.query.all(), subjects=Subject.query.all(),subject_id=id)

@app.route('/master/<int:id>/addchapter', methods=['POST'])
@master_required
def addchapterpost(id):
    name = request.form.get('chaptername')
    discription = request.form.get('discription')

    if name=='':
        flash('Chapter name can not be empty')
        return redirect(url_for('addchapter', id=id))
    if discription=='':
        flash('Chapter Discription can not be empty')
        return redirect(url_for('addchapter', id=id))
    if Chapter.query.filter_by(name=name).first():
        flash('Chapter with this name is already exists , Use different Chapter name')
        return redirect(url_for('addchapter', id=id))
    chapter = Chapter(name=name, discription=discription, subject_id=id)
    db.session.add(chapter)
    db.session.commit()
    flash('Chapter added successfully')
    return redirect(url_for('master'))

##-----adding question-----
@app.route('/master/<int:id>/addquestion')
@master_required
def addquestion(id):
    return render_template('addquestion.html', user=User.query.get(session['user_id']), questions=Question.query.all(), chapters=Chapter.query.all(),chapter_id=id)

@app.route('/master/<int:id>/addquestion', methods=['POST'])
@master_required
def addquestionpost(id):
    question = request.form.get('question')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    answer = request.form.get('correctoption')
    point = request.form.get('point')
    if question=='':
        flash('Question can not be empty')
        return redirect(url_for('addquestion', id=id))
    if option1=='' or option2=='' or option3=='' or option4=='':
        flash('Options can not be empty')
        return redirect(url_for('addquestion', id=id))
    if answer=='':
        flash('answer cannot be empty')
        return redirect(url_for('addquestion', id=id))
    if point=='':
        flash('Point can not be empty')
        return redirect(url_for('addquestion', id=id))
    question = Question(question=question, option1=option1, option2=option2, option3=option3, option4=option4, answer=answer, point=point, chapter_id=id)
    db.session.add(question)
    db.session.commit()
    flash('Question added successfully')
    return redirect(url_for('quiz'))

###--------------add quiz----------------
@app.route('/master/addquiz')
@master_required
def addquiz():
    return render_template('addquiz.html', user=User.query.get(session['user_id']), quizzes=Quiz.query.all(), chapters=Chapter.query.all(), questions=Question.query.all())

@app.route('/master/addquiz', methods=['POST'])
@master_required
def addquizpost():
    chapter_id = request.form.get('chapter')
    date = request.form.get('date')
    date = datetime.strptime(date, '%Y-%m-%d').date()
    duration = request.form.get('duration')
    duration= datetime.strptime(duration, '%H:%M').time()

    if Quiz.query.filter_by(chapter_id=chapter_id).first():
        chapter = Chapter.query.get(chapter_id)
        flash(f'A quiz for the chapter "{chapter.name}" already exists. Please choose a different chapter or edit the existing quiz.')
        return redirect(url_for('addquiz'))
    quiz = Quiz(chapter_id=chapter_id, date=date, duration=duration)
    db.session.add(quiz)
    db.session.commit()
    flash('Quiz created successfully')
    return redirect(url_for('quiz'))

#******************************************************************
#_____________EDIT Routes_________###                              *
#******************************************************************

#----------------------editing subject----------------------

@app.route('/master/<int:id>/editsubject')
@master_required
def editsubject(id):
    return render_template('editsubject.html', user=User.query.get(session['user_id']), subject=Subject.query.get(id))

@app.route('/master/<int:id>/editsubject', methods=['POST'])
@master_required
def editsubjectpost(id):
    name = request.form.get('subjectname')
    discription = request.form.get('discription')
    subject = Subject.query.get(id)
    subject.name = name
    subject.discription = discription
    db.session.commit() 
    flash('Subject edited successfully')   
    return redirect(url_for('master'))


##--------editing chapter----------

@app.route('/master/<int:id>/editchapter')
@master_required
def editchapter(id):
    return render_template('editchapter.html', user=User.query.get(session['user_id']), chapter=Chapter.query.get(id), subjects=Subject.query.all())

@app.route('/master/<int:id>/editchapter', methods=['post'])
@master_required
def editchapterpost(id):
    name = request.form.get('chaptername')
    discription = request.form.get('discription')
    subject_id = request.form.get('subject')
    chapter = Chapter.query.get(id)
    chapter.name=name
    chapter.discription=discription
    chapter.subject_id = subject_id

    if not name:
        flash("Chapter name cannot be empty.")
        return redirect(url_for('editchapter', id=id))
    if not discription:
        flash("Discription cannot be empty.")
        return redirect(url_for('editchapter', id=id))
    db.session.commit()
    flash('Chapter edited successfully')
    return redirect(url_for('master')) 


##------editingquestion-------------

@app.route('/master/<int:id>/editquestion')
@master_required
def editquestion(id):
    return render_template('editquestion.html', user=User.query.get(session['user_id']), question=Question.query.get(id), chapters=Chapter.query.all())

@app.route('/master/<int:id>/editquestion', methods=['POST'])
@master_required
def editquestionpost(id):
    question_st = request.form.get('question')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    answer = request.form.get('correctoption')
    point = request.form.get('point')
    chapter_id = request.form.get('chapter')
    if question_st=='':
        flash('Question can not be empty')
        return redirect(url_for('addquestion', id=id))
    if option1=='' or option2=='' or option3=='' or option4=='':
        flash('Options can not be empty')
        return redirect(url_for('addquestion', id=id))
    if answer=='':
        flash('answer cannot be empty')
        return redirect(url_for('addquestion', id=id))
    if point=='':
        flash('Point can not be empty')
        return redirect(url_for('addquestion', id=id))
    question=Question.query.get(id)
    question.question=question_st
    question.option1=option1
    question.option2=option2
    question.option3=option3
    question.option4=option4
    question.answer=answer
    question.point=point
    question.chapter_id=chapter_id
    db.session.commit()
    flash('Question edited successfully')
    return redirect(url_for('quiz'))


#----------------------edit quiz--------------

@app.route('/master/<int:id>/editquiz')
@master_required
def editquiz(id):
    user=User.query.get(session['user_id'])
    quiz=Quiz.query.get(id)
    duration = quiz.duration.strftime('%H:%M')
    return render_template('editquiz.html',user=user,duration=duration ,quiz=quiz)

@app.route('/master/<int:id>/editquiz', methods=['POST'])
@master_required
def editquizpost(id):
    date = request.form.get('date')
    date = datetime.strptime(date, '%Y-%m-%d').date()
    duration = request.form.get('duration')
    duration= datetime.strptime(duration, '%H:%M').time()

    quiz= Quiz.query.get(id)

    quiz.chapter_id  = quiz.chapter.id
    quiz.date = date
    quiz.duration = duration
    db.session.commit()
    flash('Quiz edited successfully')   
    return redirect(url_for('quiz'))


#******************************************************************
#_____________DELETE Routes_________###                           *
#******************************************************************

#___________________deletesubject________________________

@app.route('/master/<int:id>/deletesubject')
@master_required
def deletesubject(id):
    user= User.query.get(session['user_id'])
    subject = Subject.query.get(id)
    if not subject:    
        flash('Subject not exist.')
        return redirect(url_for('master'))
    return render_template('deletesubject.html', user=user ,subject=subject)

@app.route('/master/<int:id>/deletesubject', methods=['POST'])
@master_required
def deletesubjectpost(id):
    subject = Subject.query.get(id)
    if not subject:    
        flash('Subject not exist.')
        return redirect(url_for('master'))
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully')
    return redirect(url_for('master'))


#____________delete chapter_______________

@app.route('/master/<int:id>/deletechapter')
@master_required
def deletechapter(id):
    user= User.query.get(session['user_id'])
    chapter = Chapter.query.get(id)
    if not chapter:    
        flash('chapter not exist.')
        return redirect(url_for('master'))
    return render_template('deletechapter.html', user=user ,chapter=chapter)

@app.route('/master/<int:id>/deletechapter', methods=['POST'])
@master_required
def deletechapterpost(id):
    chapter = Chapter.query.get(id)
    if not chapter:    
        flash('chapter not exist.')
        return redirect(url_for('master'))
    db.session.delete(chapter)
    db.session.commit()
    flash('chapter deleted successfully')
    return redirect(url_for('master'))


#___________________delete question_________________
@app.route('/master/<int:id>/deletequestion')
@master_required
def deletequestion(id):
    user= User.query.get(session['user_id'])
    question = Question.query.get(id)
    if not question:    
        flash('question not exist.')
        return redirect(url_for('quiz'))
    return render_template('deletequestion.html',user=user ,question=question)

@app.route('/master/<int:id>/deletequestion', methods=['POST'])
@master_required
def deletequestionpost(id):
    question = Question.query.get(id)
    if not question:    
        flash('question not exist.')
        return redirect(url_for('quiz'))
    db.session.delete(question)
    db.session.commit()
    flash('question deleted successfully')
    return redirect(url_for('quiz'))


#___________________delete quiz_________________

@app.route('/master/<int:id>/deletequiz')
@master_required
def deletequiz(id):
    user= User.query.get(session['user_id'])
    quiz = Quiz.query.get(id)
    if not quiz:    
        flash('quiz not exist.')
        return redirect(url_for('quiz'))
    return render_template('deletequiz.html',user=user ,quiz=quiz)

@app.route('/master/<int:id>/deletequiz', methods=['POST'])
@master_required
def deletequizpost(id):
    quiz = Quiz.query.get(id)
    if not quiz:    
        flash('quiz not exist.')
        return redirect(url_for('quiz'))
    db.session.delete(quiz)
    db.session.commit()
    flash('quiz deleted successfully')
    return redirect(url_for('quiz'))


#******************************************************************
#_____________MASTER DASHBOARD Routes_________###                 *
#******************************************************************


##----------users for master_________
@app.route('/master/users')
@master_required
def users():
    user=User.query.get(session['user_id'])
    users = User.query.filter(User.is_master == False).all()

    parameter = request.args.get('parameter')
    query = request.args.get('query')
    parameters = {'username':'Username', 'fullname':'Fullname', 'qualification':'Qualification'}

    if parameter and query:
        if parameter=="username":
            users = User.query.filter(User.is_master == False).filter(User.username.like('%'+query+'%'))
            return render_template('users.html' , user=user, users=users, parameters=parameters )

        if parameter=="fullname":
            users = User.query.filter(User.is_master == False).filter(User.fullname.like('%'+query+'%'))
            return render_template('users.html' , user=user, users=users, parameters=parameters )
        
        if parameter=="qualification":
            users = User.query.filter(User.is_master == False).filter(User.qualification.like('%'+query+'%'))
            return render_template('users.html' , user=user, users=users, parameters=parameters )

    return render_template('users.html' , user=user, users=users, parameters=parameters )


##-----quiz management-----

@app.route('/master/quiz')
@master_required
def quiz():
    user=User.query.get(session['user_id'])
    quizzes=Quiz.query.all()
    parameter = request.args.get('parameter')
    query = request.args.get('query')

    parameters = {'chapter':'Chapter', 'question':'Question'}

    if parameter and query:
        if parameter=="chapter":
            quizzes = Quiz.query.join(Chapter).filter(Chapter.name.like('%'+query+'%')).all()
            return render_template('quizmanagement.html', user=user, quizzes=quizzes,parameters=parameters)
        if parameter=="question":
            quizzes =Quiz.query.join(Chapter).join(Question).filter(Question.question.like('%'+query+'%')).all()
            return render_template('quizmanagement.html', user=user,quizzes=quizzes, parameters=parameters)
    return render_template('quizmanagement.html', user=user, quizzes=quizzes, parameters=parameters)



#******************************************************************
#_____________ACCOUNT Routes_________###                          *
#******************************************************************

#__________________ MY Account _________________

@app.route('/user/account')
@login_required
def account():
    user=User.query.get(session['user_id'])
    return render_template('account.html', user=user)


#__________________ EDIT Account _________________

@app.route('/user/editaccount')
@login_required
def editaccount():
    user=User.query.get(session['user_id'])
    return render_template('editaccount.html', user=user)

@app.route('/user/editaccount', methods=['POST'])
@login_required
def editaccountpost():
    user=User.query.get(session['user_id'])
    username = request.form.get('username')
    fullname = request.form.get('fullname')
    qualification = request.form.get('qualification')
    password = request.form.get('password')
    npassword = request.form.get('npassword')
    dob = request.form.get('dob')
    dob = datetime.strptime(dob, '%Y-%m-%d').date()

    if username=='' :
        flash('username can not be empty')
        return redirect(url_for('editaccount'))

    if not password:
        password=user.password

    elif not password == npassword:
        flash('Passwords do not match')
        return redirect(url_for('editaccount'))

    if fullname=='' :
        flash('fullname can not be empty')
        return redirect(url_for('editaccountr'))
    if qualification=='' :
        flash('qualification can not be empty')
        return redirect(url_for('editaccount'))

    user.username = username
    user.fullname = fullname
    user.qualification = qualification
    user.dob = dob
    user.password = password

    db.session.commit()
    flash('user information updated correctly')
    return redirect(url_for('account'))


#******************************************************************
#_____________VIEW QUIZ Routes_________###                        *
#******************************************************************


##-----viewquiz-----
@app.route('/user/viewquiz/<int:id>')
@login_required
def viewquiz(id):
    user=User.query.get(session['user_id'])
    quiz = Quiz.query.get(id)
    if user.is_master:
        return render_template('viewquiz_m.html', user=user, quiz=quiz)
    return render_template('viewquiz.html', user = user, quiz=quiz)

#******************************************************************
#_____________USER DASHBOARD Routes_________###                   *
#******************************************************************

##-------Quiz-----
@app.route('/user/quiz/<int:id>')
@login_required
def submission(id):
    quiz = Quiz.query.get(id)
    user = User.query.get(session['user_id'])
    submited_quiz = Submission.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    Q_date = quiz.date
    if submited_quiz:
        flash(f'You have already submitted ___{quiz.chapter.name}___ quiz.')
        return redirect(url_for('user'))
    if Q_date > datetime.now().date():
        flash(f'You can not submit ___{quiz.chapter.name}___ quiz before the date {Q_date}.')
        return redirect(url_for('user'))
    if Q_date < datetime.now().date():
        flash(f'Submission date for the quiz on "{quiz.chapter.name}" has passed.')
        return redirect(url_for('user'))
    return render_template('quiz.html', user=User.query.get(session['user_id']), quiz=quiz)

@app.route('/user/quiz/<int:id>', methods=['POST'])
@login_required
def submissionpost(id):
    quiz = Quiz.query.get(id)
    user = User.query.get(session['user_id'])

    score = 0
    correct_ans = 0 
    total_questions = len(quiz.chapter.questions)

    scores_list = []
    for question in quiz.chapter.questions:
        selected_option = request.form.get(f'question{question.id}')
        is_correct = selected_option == f"option{question.answer}"
        
        if not selected_option:
            selected_option = 0
        if is_correct:
            score += question.point
            Q_point = question.point
            correct_ans += 1  
        else:
            Q_point = 0
        scores_list.append(Score(user_id=user.id, quiz_id=quiz.id, question_id=question.id, correct_opt=question.answer, submit_opt=selected_option, score=Q_point  )) 

    db.session.bulk_save_objects(scores_list) 
    db.session.commit()

    submission = Submission(user_id=user.id, quiz_id=quiz.id , score=score, total_questions=total_questions , correct_ans=correct_ans)
    db.session.add(submission)
    db.session.commit()
    flash('Quiz submitted successfully')
    return redirect(url_for('scores'))


##---user score --
@app.route('/user/scores')
@login_required
def scores():
    user = User.query.get(session['user_id'])
    submissions = Submission.query.filter_by(user_id=user.id).all()

    parameter = request.args.get('parameter')
    query = request.args.get('query')
    parameters = {'subject':'Subject', 'chapter':'Chapter'}

    if parameter and query:
        if parameter=="subject":
            submissions = Submission.query.join(Quiz).join(Chapter).join(Subject).filter(Submission.user_id == user.id).filter(Subject.name.like('%'+query+'%')).all()
            return render_template('scores.html', user=user, submissions=submissions,parameters=parameters)
        if parameter=="chapter":
            submissions = Submission.query.join(Quiz).join(Chapter).filter(Submission.user_id == user.id).filter(Chapter.name.ilike(f'%{query}%')).all()
            return render_template('scores.html', user=user, submissions=submissions,parameters=parameters)
    
    return render_template('scores.html', user=user, submissions=submissions,parameters=parameters)


#____________quiz wise score_______________
@app.route('/user/scores/<int:id>')
@login_required
def viewresponce(id):
    user = User.query.get(session['user_id'])
    scores = Score.query.filter(Score.user_id==user.id).filter(Score.quiz_id==id).all()
    return render_template('viewresponce.html', user=user, scores=scores)


#-----print quiz-------
@app.route('/user/print/<int:id>')
@login_required
def printquiz(id):
    quiz = Quiz.query.get(id)
    user = User.query.get(session['user_id'])
    submited_quiz = Submission.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
    if not submited_quiz:
        flash(f'You have first submit ___{quiz.chapter.name}___ quiz to print it.')
        return redirect(url_for('scores'))
    return render_template('print_quiz.html', user=User.query.get(session['user_id']), quiz=quiz)


#******************************************************************
#_____________SUMMERY Routes_________###                          *
#******************************************************************

#____________ summery  route______
@app.route('/user/summery')
@login_required
def summery():
    user = User.query.get(session['user_id'])
    if user.is_master:
        return redirect(url_for('mastersummery'))
    return redirect(url_for('usersummery'))


#____________ user summery ______

@app.route('/user/usersummery')
@login_required
def usersummery():
    user=User.query.get(session['user_id'])
    submissions=Submission.query.filter_by(user_id=user.id).all()
    subject_names = list(set(submission.quiz.chapter.subject.name for submission in submissions))
    submit_dates = list(set(submission.date.strftime('%B') for submission in submissions if submission.date))

    SW_no_of_quizzes = {subject_name: 0 for subject_name in subject_names}
    for submission in submissions:
        subject_name = submission.quiz.chapter.subject.name
        SW_no_of_quizzes[subject_name] += 1

    MW_no_of_quizzes = {month_name: 0 for month_name in submit_dates }
    for submission in submissions:
        month_name = submission.date.strftime('%B')
        MW_no_of_quizzes[month_name] += 1

    return render_template('usersummery.html',
                            SW_no_of_quizzes=SW_no_of_quizzes,
                            MW_no_of_quizzes=MW_no_of_quizzes,
                            submit_dates=submit_dates, 
                            subject_names=subject_names, 
                            user=user)


#____________ master summery ______

@app.route('/user/mastersummery')
@master_required
def mastersummery():
    user=User.query.get(session['user_id'])
    submissions=Submission.query.all()
    subject_names = list(set(submission.quiz.chapter.subject.name for submission in submissions))
    chapter_names = list(set(submission.quiz.chapter.name for submission in submissions))

    quiz_high = {chapter_name: 0 for chapter_name in chapter_names}
    for submission in submissions:
        chapter_name = submission.quiz.chapter.name
        if submission.score > quiz_high[chapter_name]:
            quiz_high[chapter_name] = submission.score

    no_of_users_sb = {subject_name: set() for subject_name in subject_names}
    for submission in submissions:
        subject_name = submission.quiz.chapter.subject.name
        no_of_users_sb[subject_name].add(submission.user_id)
    no_of_users_sb = {subject_name: len(user_ids) for subject_name, user_ids in no_of_users_sb.items()}

    no_of_users_ch = {chapter_name: set() for chapter_name in chapter_names}
    for submission in submissions:
        chapter_name = submission.quiz.chapter.name
        no_of_users_ch[chapter_name].add(submission.user_id)
    no_of_users_ch = {chapter_name: len(user_ids) for chapter_name, user_ids in no_of_users_ch.items()}


    return render_template('mastersummery.html',
                            subject_names=subject_names, 
                            chapter_names=chapter_names,
                            quiz_high=quiz_high, 
                            no_of_users_sb=no_of_users_sb,
                            no_of_users_ch=no_of_users_ch,
                            user=user)

#******************************************************************
#_____________SUBMISSIONS Routes_________###                      *
#******************************************************************

##----------Submissions for master_________
@app.route('/master/submissions')
@master_required
def submit():
    user=User.query.get(session['user_id'])
    submissions = Submission.query.all()

    parameter = request.args.get('parameter')
    query = request.args.get('query')
    parameters = {'username':'Username', 'fullname':'Fullname', 'qualification':'Qualification', 'subject':'Subject', 'chapter':'Chapter','score':'Score','user_id':'User_id'}

    if parameter and query:
        if parameter=="fullname":
            submissions = Submission.query.join(User).filter(User.fullname.like('%'+query+'%')).all()
            return render_template('submissions.html', user=user, submissions=submissions,parameters=parameters)
        if parameter=="qualification":
            submissions = Submission.query.join(User).filter(User.qualification.like('%'+query+'%')).all()
            return render_template('submissions.html', user=user, submissions=submissions,parameters=parameters)
        if parameter=="user_id":
            submissions = Submission.query.join(User).filter(User.id.like('%'+query+'%')).all()
            return render_template('submissions.html', user=user, submissions=submissions,parameters=parameters)
        if parameter=="username":
            submissions = Submission.query.join(User).filter(User.username.like('%'+query+'%')).all()
            return render_template('submissions.html', user=user, submissions=submissions,parameters=parameters)
        if parameter=="subject":
            submissions = Submission.query.join(Quiz).join(Chapter).join(Subject).filter(Subject.name.like('%'+query+'%')).all()
            return render_template('submissions.html', user=user, submissions=submissions,parameters=parameters)
        if parameter=="chapter":
            submissions = Submission.query.join(Quiz).join(Chapter).filter(Chapter.name.like('%'+query+'%')).all()
            return render_template('submissions.html', user=user, submissions=submissions,parameters=parameters)
        if parameter=="score":
            submissions = Submission.query.filter(Submission.score.like('%'+query+'%')).all()
            return render_template('submissions.html', user=user, submissions=submissions,parameters=parameters)

    return render_template('submissions.html' , submissions=submissions, user=user, parameters=parameters )