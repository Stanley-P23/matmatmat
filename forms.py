from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post

class CreateInfoForm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    body = CKEditorField("Treść", validators=[DataRequired()])
    submit = SubmitField("Wyślij")

class CreateExercisesSeriesForm(FlaskForm):

    session_no = StringField("Numer zajęć", validators=[DataRequired(), Length(1, 2)])
    title = StringField("Tytuł", validators=[DataRequired(), Length(5, 50)])
    submit = SubmitField("Stwórz serię zadań")



class CreateExerciseForm(FlaskForm):



    body = CKEditorField("Treść zadania", validators=[DataRequired()])
    value1 = StringField("Odpowiedź A", validators=[DataRequired(), Length(1, 100)])
    value2 = StringField("Odpowiedź B", validators=[DataRequired(), Length(1, 100)])
    value3 = StringField("Odpowiedź C", validators=[DataRequired(), Length(1, 100)])
    value4 = StringField("Odpowiedź D", validators=[DataRequired(), Length(1, 100)])
    correct = SelectField(u'Poprawna odpowiedź', choices=['A', 'B', 'C', 'D'])
    submit = SubmitField("Dodaj zadanie")



class CreateAnswerForm(FlaskForm):

                answer1 = SelectField('Odpowiedź', choices=['A', 'B', 'C', 'D'])
                answer2 = SelectField('Odpowiedź', choices=['A', 'B', 'C', 'D'])
                answer3 = SelectField('Odpowiedź', choices=['A', 'B', 'C', 'D'])
                answer4 = SelectField('Odpowiedź', choices=['A', 'B', 'C', 'D'])
                answer5 = SelectField('Odpowiedź', choices=['A', 'B', 'C', 'D'])
                answer6 = SelectField('Odpowiedź', choices=['A', 'B', 'C', 'D'])
                submit = SubmitField("Prześlij odpowiedzi")



# TODO: Create a RegisterForm to register new users


# TODO: Create a LoginForm to login existing users


# TODO: Create a CommentForm so users can leave comments below posts

class CreateCommentForm(FlaskForm):

    body = CKEditorField("Your comment:", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Add a comment")

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(8), ])

    submit = SubmitField(label="ZALOGUJ MNIE!")

class RegisterForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(8), ])
    confirm = PasswordField('Powtórz hasło', validators=[DataRequired(), Length(8), ])
    name = StringField('Imię', validators=[DataRequired()])
    submit = SubmitField(label="ZAREJESTRUJ MNIE!")