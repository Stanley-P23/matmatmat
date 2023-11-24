from datetime import date, timedelta, datetime
import flask
from flask import Flask, abort, render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar

from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

import math
from notifications import*
from forms import*
from db_classes import*


ckeditor = CKEditor(app)
Bootstrap5(app)



with app.app_context():
    db.create_all()

login_managero = LoginManager()
login_managero.init_app(app)
login_managero.login_view = 'login'


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)



@login_managero.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', error="Zaloguj się na swoje konto"))


@login_managero.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.id == 1:
                return f(*args, **kwargs)
        return redirect(url_for('login', error="Please log in as Admin first."))
    return decorated_function




@app.route("/")
def news():

    result = db.session.execute(db.select(Infos))
    information = result.scalars().all()
    information.reverse()

    page = request.args.get('page', default=1, type=int)
    series_per_page = 2
    start = (page - 1) * series_per_page
    end = start + series_per_page
    paginated_information = information[start:end]
    if_next = end < len(information)


    return render_template("index.html", all_posts=paginated_information, current_user=current_user, page=page,
                           if_next=if_next)

@app.route('/docs/<string:no>')
def get_pdf(no):

    prefixed = [filename for filename in os.listdir('static/assets/exercises/') if filename.startswith(no)]
    path = f"assets/exercises/{prefixed[0]}"
    return send_from_directory('static', path=path)

# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    register_form = RegisterForm()
    
    if register_form.validate_on_submit():
        email = register_form.email.data
        password = register_form.password.data
        confirm = register_form.confirm.data

        name = register_form.name.data

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user:
            error = "User with this e-mail address already exists. Log in instead"
            login_form = LoginForm()
            return redirect(url_for('login', form=login_form, error=error))

        elif password != confirm:
            error = "Given passwords do not match!"


        else:
            new_user = User(email=email,
                            password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8), name=name)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for('get_all_series'))

    
    return render_template("register.html", form=register_form, error=error)


# TODO: Retrieve a user from the database based on their email.
@app.route('/login', methods=['GET', 'POST'])
def login():

    error = request.args.get('error')

    login_form = LoginForm()
    if login_form.validate_on_submit():

        email = login_form.email.data
        password = login_form.password.data

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            error = "User with this e-mail address does not exist."

        else:

            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('get_all_series'))

            else:
                error = "Password does not match with this e-mail address."



    return render_template("login.html", form=login_form, error=error, logged_in=current_user.is_authenticated)





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('news'))


@app.route('/tests')
@login_required
def get_all_series():
    result = db.session.execute(db.select(Series))
    serieses = result.scalars().all()

    done = []
    expired = []
    score = []
    points = 0
    divide = 1
    for series in serieses:

        user_answers = db.session.query(Answer).filter(Answer.user_id == current_user.id,
                                                       Answer.series_id == series.id).all()



        points = 0
        for answer in user_answers:
            points += answer.point
        if len(user_answers) != 0:
            divide = len(user_answers)

            points = points/divide*100

        score.append(math.floor(points))

        finish_date = datetime.strptime(series.finish_date, "%Y-%m-%d").date()

        if finish_date >= date.today():
            expired.append(0)

        else:
            expired.append(1)

        if len(user_answers) != 0:
            done.append(1)
        else:
            done.append(0)

    serieses.reverse()
    done.reverse()
    expired.reverse()
    score.reverse()





    return render_template("tests.html", all_series=serieses, done=done, expired=expired, score=score)





@app.route("/series/<int:series_id>", methods=['GET', 'POST'])
@login_required
def show_series(series_id):

    error= None

    requested_series = db.get_or_404(Series, series_id)

    finish_date = datetime.strptime(requested_series.finish_date, "%Y-%m-%d").date()


    form = CreateAnswerForm()

    if flask.request.method == "POST":

        for count, exercise in enumerate(requested_series.exercises):
            new_answer = Answer(

                user=current_user,
                exercise_id=exercise.id,
                series_id=series_id,
                answer=form[f"answer{count+1}"].data,
                point=(form[f"answer{count+1}"].data == exercise.correct),


            )
            db.session.add(new_answer)
            db.session.commit()

        return redirect(url_for('show_answers', series_id=series_id, expired=0))




    return render_template("post.html", form=form, post=requested_series,  \
        logged_in=current_user.is_authenticated, series_id=series_id)

@app.route("/answers/<int:series_id>/<expired>")
@login_required
def show_answers(series_id, expired):

    requested_series = db.get_or_404(Series, series_id)

    user_answers = db.session.query(Answer).filter(Answer.series_id == series_id, Answer.user_id ==
                                                   current_user.id).all()


    score = 0
    for answer in user_answers:
        score += answer.point

    return render_template("answered-series.html", post=requested_series, series_id=series_id, user_answers=user_answers,
                           score=score, expired=expired)




@app.route("/students")
@admin_only
def students():

    series = db.session.execute(db.select(Series)).scalars().all()

    exercises = 0


    series_score = [0] * len(series)
    for index, ser in enumerate(series):

        exercises += len(ser.exercises)

        if len(ser.answers) != 0:
            points = 0
            for answer in ser.answers:
                points += answer.point
            points = math.floor(points/len(ser.answers)*100)
            
            series_score[index] = points


    pupils = db.session.execute(db.select(User)).scalars().all()

    pupil_score = [0] * len(pupils)
    pupil_series = [0] * len(pupils)
    for index, pup in enumerate(pupils):
        points = 0
        if len(pup.answers) != 0:


            for answer in pup.answers:
                points += answer.point


            points = math.floor(points / len(pup.answers) * 100)



        tests = 0
        for answer in pup.answers:

            tests += 1
        tests = math.floor(tests / exercises * 100)



        pupil_score[index] = points
        pupil_series[index] = tests

    series.reverse()
    series_score.reverse()

    return render_template("students.html", series=series, series_score=series_score,
                           pupils=pupils, pupil_score=pupil_score,
                           pupil_series=pupil_series)



@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreateExercisesSeriesForm()
    if form.validate_on_submit():
        new_series = Series(

                    session_no=form.session_no.data,
                    title=form.title.data,
                    date=date.today(),
                    finish_date=date.today()+timedelta(days=7)
        )
        db.session.add(new_series)
        db.session.commit()
        return redirect(url_for("get_all_series"))
    return render_template("make-post.html", form=form)



@app.route("/new-info", methods=["GET", "POST"])
@admin_only
def add_new_info():
    form = CreateInfoForm()
    if form.validate_on_submit():
        new_info = Infos(


                    title=form.title.data,
                    body=form.body.data,
                    date=date.today(),

        )
        db.session.add(new_info)
        db.session.commit()
        return redirect(url_for("news"))
    return render_template("create-info.html", form=form)


@app.route("/add-exercise/<series_id>", methods=["GET", "POST"])
@admin_only
def add_exercise(series_id):

    add_form = CreateExerciseForm()

    if add_form.validate_on_submit():
        new_exercise = Exercise(

            body=add_form.body.data, value1=add_form.value1.data, value2=add_form.value2.data,
            value3=add_form.value3.data, value4=add_form.value4.data, correct=add_form.correct.data,
            series_id=series_id

        )
        db.session.add(new_exercise)
        db.session.commit()

        return redirect(url_for("show_series", series_id=series_id))

    return render_template("add-exercise.html", add_form=add_form, logged_in=current_user.is_authenticated,
                           series_id=series_id)






@app.route("/info-edit/<int:info_id>", methods=["GET", "POST"])
@admin_only
def edit_info(info_id):
    info = db.get_or_404(Infos, info_id)
    edit_form = CreateInfoForm(
        title=info.title,
        body=info.body
    )
    if edit_form.validate_on_submit():
        info.title = edit_form.title.data
        info.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("news"))
    return render_template("create-info.html", form=edit_form)

@app.route("/exercise-edit/<int:exercise_id>", methods=["GET", "POST"])
@admin_only
def edit_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    edit_form = CreateExerciseForm(


            body = exercise.body,
            value1 = exercise.value1,
            value2 = exercise.value2,
            value3 = exercise.value3,
            value4 = exercise.value4,
            correct = exercise.correct
        
        
                                    )
    
    
    
    if edit_form.validate_on_submit():

        exercise.body = edit_form.body.data
        exercise.value1 = edit_form.value1.data
        exercise.value2 = edit_form.value2.data
        exercise.value3 = edit_form.value3.data
        exercise.value4 = edit_form.value4.data
        exercise.correct = edit_form.correct.data
        

        db.session.commit()
        return redirect(url_for("get_all_series"))
    return render_template("edit-exercise.html", form=edit_form)


@app.route("/series-date-edit/<int:series_id>", methods=["GET", "POST"])
@admin_only
def series_date_edit(series_id):
    series = db.get_or_404(Series, series_id)
    edit_form = CreateDateForm(
        # date=series.finish_date,

    )
    if edit_form.validate_on_submit():
        series.finish_date = edit_form.date.data
        db.session.commit()
        return redirect(url_for("get_all_series"))
    return render_template("edit-date.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:series_id>/<int:exercise_id>")
@admin_only
def delete_exercise(series_id, exercise_id):

    exercise_to_delete = db.get_or_404(Exercise, exercise_id)
    answers_to_delete = db.session.query(Answer).filter(Answer.series_id == series_id).all()
    db.session.delete(exercise_to_delete)
    for item in answers_to_delete:
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for('show_series', series_id=series_id))

@app.route("/delete/<int:series_id>")
@admin_only
def delete_series(series_id):

    series_to_delete = db.get_or_404(Series, series_id)
    exercises_to_delete = db.session.query(Exercise).filter(Exercise.series_id == series_id).all()
    answers_to_delete = db.session.query(Answer).filter(Answer.series_id == series_id).all()

    db.session.delete(series_to_delete)

    for item in exercises_to_delete:
        db.session.delete(item)
    for item in answers_to_delete:
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for('get_all_series'))



@app.route("/delete-student/<int:student_id>")
@admin_only
def delete_student(student_id):

    student_to_delete = db.get_or_404(User, student_id)
    answers_to_delete = db.session.query(Answer).filter(Answer.user_id == student_id).all()

    db.session.delete(student_to_delete)


    for item in answers_to_delete:
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for('students'))


@app.route("/info/delete/<int:info_id>")
@admin_only
def delete_info(info_id):

    info_to_delete = db.get_or_404(Infos, info_id)
    db.session.delete(info_to_delete)
    db.session.commit()
    return redirect(url_for('news'))

@app.route("/send/<int:series_id>")
@admin_only
def send_notification(series_id):

    series = db.get_or_404(Series, series_id)
    addresses = []

    result = db.session.execute(db.select(User))
    users = result.scalars().all()
    for user in users:
        addresses.append(user.email)


    notification = NotificationManager(series, addresses)

    notification.send_mail()

    return redirect(url_for('get_all_series'))


@app.route("/base")
def base():
    return render_template("baza.html", logged_in=current_user.is_authenticated)

@app.route("/base/things")
def things():
    return render_template("things.html", logged_in=current_user.is_authenticated)

@app.route("/materials")
def materials():
    return render_template("materials-sessions.html", logged_in=current_user.is_authenticated)

@app.route('/download-repetytorium')
def download_repetytorium():
    return send_from_directory('static', path="assets/repetytorium.pdf")

@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in=current_user.is_authenticated)





if __name__ == "__main__":
    app.run(debug=False)
