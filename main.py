from data import db_session
from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, RadioField
from wtforms import SelectField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data.posts import Post
from data.assessments import Assessment
from data.groups import Group
from data.teacher import Teacher
from data.vk_db import VkDb
from data.number_subject import numberSubject
from data.users import User
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import vk_api
import random
from PIL import Image
from io import BytesIO
import sqlite3
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# run_with_ngrok(app)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    patronymic = StringField('Patronymic', validators=[DataRequired()])
    position = RadioField('Label', coerce=int, choices=[(0, 'Студент'), (1, 'Преподаватель')])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    conn = sqlite3.connect("db/ptk.db")
    cursor = conn.cursor()
    s = [('0', 'all'), ('1', 'groups')]
    result = cursor.execute('''SELECT g."group" FROM groups as g''').fetchall()
    for i in result:
        s.append((i[0], i[0]))
    conn.close()
    position = SelectField('', choices=s)
    img = FileField('File')
    submit = SubmitField('Применить')


class AssessmentsForm(FlaskForm):
    id_user = StringField('Id пользователя', validators=[DataRequired()])
    assessment = SelectField('Оценка', choices=[('5', '5'), ('4', '4'), ('3', '3'),
                                                ('2', '2'), ('1', '1'), ('0', '0')])
    subject = StringField('Предмет', validators=[DataRequired()])
    submit = SubmitField('Применить')


def main():
    db_session.global_init("db/ptk.db")
    app.run()


@app.route("/")
def index():
    sub = []
    session = db_session.create_session()
    if current_user.is_authenticated and current_user.position == 0:
        s = []
        for i in session.query(User, Group).filter(User.group == Group.group,
                                                   current_user.id == User.id):
            s.append(i.Group.subject)
        s = list(map(int, s[0].split(',')))
        sub = session.query(numberSubject).filter(numberSubject.id.in_(s))
    elif current_user.is_authenticated and current_user.position == 1:
        s = []
        for i in session.query(Teacher).filter(current_user.id == Teacher.id_users):
            s.append(i.subjects)
        s = list(map(int, s[0].split(',')))
        sub = session.query(numberSubject).filter(numberSubject.id.in_(s))
    posts = session.query(Post).filter(Post.position == 0)
    return render_template("base.html", sub=sub, post=posts)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.patronymic.data,
            email=form.email.data,
            position=form.position.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/assessments')
def assessments():
    sub = []
    session = db_session.create_session()
    if current_user.is_authenticated and current_user.position == 0:
        slov = {}
        s1 = []
        s2 = []
        for i in session.query(User, Group).filter(current_user.id == User.id,
                                                   Group.group == User.group):
            s = i.Group.subject
        for i in session.query(numberSubject).filter(numberSubject.id.in_(s)):
            slov[i.subject] = []
        for i in session.query(Assessment, numberSubject).filter(
                current_user.id == Assessment.id_user,
                Assessment.subject == numberSubject.id):
            slov[i.numberSubject.subject].append(i.Assessment.assessment)
        print(slov)
        return render_template('assessments.html', sub=sub, slov=slov)


@app.route('/assessments_teacher', methods=['GET', 'POST'])
def assessments_teacher():
    if current_user.is_authenticated and current_user.position == 1:
        session = db_session.create_session()
        s = []
        for i in session.query(Teacher).filter(current_user.id == Teacher.id_users):
            s.append(i.subjects)
        s = list(map(int, s[0].split(',')))
        sub = session.query(numberSubject).filter(numberSubject.id.in_(s))
        form = AssessmentsForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            asm = Assessment()
            asm.assessment = form.assessment.data
            asm.id_teacher = current_user.id
            asm.id_user = form.id_user.data
            asm.subject = form.subject.data
            session.add(asm)
            session.merge(current_user)
            session.commit()
            return redirect('/assessments_teacher')
        return render_template('assessments_teacher.html', form=form, sub=sub)


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    if current_user.is_authenticated and current_user.position == 1:
        session = db_session.create_session()
        s = []
        for i in session.query(Teacher).filter(current_user.id == Teacher.id_users):
            s.append(i.subjects)
        s = list(map(int, s[0].split(',')))
        sub = session.query(numberSubject).filter(numberSubject.id.in_(s))
        form = PostForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            post = Post()
            post.headline = form.title.data
            post.text = form.content.data
            post.pathPict = form.img.data.filename
            post.id_user = current_user.id
            post.position = int(form.position.data)
            session.add(post)
            session.merge(current_user)
            session.commit()
            rez = Image.open(BytesIO(
                form.img.data.read()))
            rez.save(f'static/img/{form.img.data.filename}', 'PNG')
            vk_send(int(form.position.data), form.title.data, form.content.data)
            return redirect('/posts')
        return render_template('posts.html', form=form, sub=sub)


def vk_send(n, headline, text):
    if n != 0:
        session = db_session.create_session()
        if n == 1:
            result = session.query(VkDb)
        else:
            result = session.query(VkDb).filter(VkDb.group == n)
        TOKEN = 'cdbf3250db7404d91e4e88c7834ba2b587c9f60016bc02ff9ad7da18fbcf4008f1f7b9ff1ea6303195f29'
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        for item in result:
            vk.messages.send(user_id=item.id_dialog,
                             message=f"""{headline}
{text}""",
                             random_id=random.randint(0, 2 ** 64))


@app.route('/developments')
def developments():
    session = db_session.create_session()
    n_group = 1
    for i in session.query(Post, User, Group).filter(User.id == current_user.id,
                                                     User.group == Group.group,
                                                     Post.position == Group.group):
        n_group = int(i.Group.group)
    s = []
    for i in session.query(User, Group).filter(User.group == Group.group,
                                               current_user.id == User.id):
        s.append(i.Group.subject)
    s = list(map(int, s[0].split(',')))
    sub = session.query(numberSubject).filter(numberSubject.id.in_(s))
    s = session.query(Post).filter(Post.position.in_((1, n_group)))
    print(sub)
    return render_template('developments.html', s=s, sub=sub)


if __name__ == '__main__':
    main()
