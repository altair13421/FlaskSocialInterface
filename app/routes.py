from datetime import datetime
import os
from flask import Flask, redirect, render_template, request, url_for, flash
from app import db, app
from .forms import LoginForm, EntryForm, SignupForm, ProfileForm
from .models import Users, Posts
from .configs import image_dir, basedir
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import pyperclip as ppc
from markupsafe import escape
from hashlib import md5

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User': Users, 'Posts': Posts}

@app.route('/')
@app.route('/index')
def index():
    return render_template(
        'index.html', 
        title="Home", 
        homething="Blog",
        homelink=url_for('index'),
        heading="Home", 
        hrefdata = url_for('login'), 
        entry_1="Signup", 
        entry_1_link = url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('mainfeed'))
    form = SignupForm()
    if form.validate_on_submit():
        if Users.query.filter_by(username=form.username.data).first() != None:
            flash('User Exists, Please Login')
            return redirect('login')
        user = Users(username=f'{form.username.data}', email=f'{form.email.data}')
        user.set_password(f'{form.password.data}')
        db.session.add(user)
        db.session.commit()
        flash(f'User {form.username.data} Registered')
        return redirect('login')
    return render_template(
        'signup.html', 
        title="Sign Up - Blog", 
        homething="Blog",
        homelink=url_for('index'),
        form = form, 
        entry_1="Login", 
        entry_1_link = url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('mainfeed'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('mainfeed')
        return redirect(next_page)
    return render_template(
        'login.html', 
        title="Login - Blog", 
        homething="Blog",
        homelink=url_for('index'),
        form = form,  
        entry_1="Signup", 
        entry_1_link = url_for('signup'))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/mainfeed', methods=['GET', 'POST'])
@login_required
def mainfeed():
    posts = Posts.query.all()
    return render_template(
        'mainpage.html',
        title = "Home",
        homething = f'{current_user.username}',
        homelink=url_for('userprofile', username=current_user.username),
        entry_1="Write", 
        entry_1_link = url_for('writepost'),
        posts=posts,
    )

@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def userprofile(username):
    user = Users.query.filter_by(username=username).first()
    if username==current_user.username:
        return render_template(
            "userprofile.html",
            title=f'{username} Profile',
            homething='<',
            homelink=url_for('mainfeed'),
            entry_1='Update',
            entry_1_link=url_for('update_profile'),
            user=user,
        )
    return render_template(
        "userprofile.html",
        title=f'{username} Profile',
        homething='<',
        homelink=url_for('mainfeed'),
        entry_1='Posts',
        entry_1_link=url_for('userposts', username=username),
        user=user,
    )

@app.route('/profile/<username>/posts', methods=['GET', 'POST'])
@login_required
def userposts(username):
    user = Users.query.filter_by(username=username).first()
    posts = user.posts.all()
    return render_template(
        'mainpage.html',
        title=f'{escape(username)}\'s Posts',
        homething='<',
        homelink=url_for('userprofile', username=username),
        entry_1='Write',
        entry_1_link=url_for('writepost'),
        posts=posts,
    )

@app.route('/writepost', methods=['GET', 'POST'])
@login_required
def writepost():
    form = EntryForm()
    if form.validate_on_submit():
        post = Posts(
            post_title=form.title.data,
            post_body=form.body.data,
            author=current_user,
            timestamp=datetime.now(),
        )
        db.session.add(post)
        db.session.commit()
        flash(f'Post {form.title.data} added')
        return redirect('mainfeed')
    return render_template(
        'addentry.html',
        title="Write Post",
        homething="<",
        homelink=url_for('mainfeed'),
        form = form, 
        entry_1="Discard", 
        entry_1_link = url_for('mainfeed'),
    )

@app.route('/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    # user = Users.query.filter_by(username=current_user.username)
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        if request.method=='POST':
            file = request.files['avatar']
            filepath = f'{os.path.join(image_dir, secure_filename(file.filename))}'
            file_ext = filepath.split('.')[-1]
            filename = f'{current_user.username}_current.{file_ext}'
            if os.path.isfile(os.path.join(image_dir, filename)):
                hash_ = md5(filepath.encode('utf-8')).hexdigest()
                os.rename(os.path.join(image_dir, filename), os.path.join(image_dir, f'{current_user.username}_{hash_}.{file_ext}'))
            file.save(filepath)
            os.rename(filepath, os.path.join(image_dir, filename))
            current_user.avatar = f'/{os.path.join(image_dir, filename)}'[6:]
        db.session.commit()
        return redirect(url_for('userprofile', username=current_user.username))
    return render_template(
        'profileupdate.html',
        title=f'{current_user.username}\'s Profile',
        homething='<',
        homelink=url_for('userprofile', username=current_user.username),
        entry_1='Feed',
        entry_1_link=url_for('mainfeed'),
        user=current_user,
        form=form,
    )

@app.route('/view/<id>', methods=['GET', 'POST'])
@login_required
def view(id):
    post = Posts.query.get(id)
    return render_template(
        'viewpage.html', 
        title=f"{post.post_title} - Blog", 
        homething="<",
        homelink=url_for('mainfeed'),
        entry_1=f"{post.author.username}\'s Profile", 
        entry_1_link = url_for('userprofile', username=post.author.username), 
        post=post)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()